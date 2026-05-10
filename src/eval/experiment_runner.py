"""
Orchestrates end-to-end experiments: benchmark loading → STA → ChOA optimization → metrics.
"""
import time
import logging
import numpy as np
from pathlib import Path
from typing import Callable, Optional

from src.sta_engine.opensta_adapter import OpenSTAAdapter
from src.sta_engine.incremental_wrapper import IncrementalSTA
from src.swarm.chimp_optimizer import ChimpOptimizer
from src.swarm.population import Population
from src.objectives.timing_objectives import TimingObjectives
from src.objectives.aggregator import ObjectiveAggregator
from src.actions.eco_hooks import ECOHooks
from src.actions.candidate_ranker import CandidateRanker
from src.io.dataset_registry import DatasetRegistry

log = logging.getLogger(__name__)


class ExperimentRunner:
    def __init__(self, config: dict, adapter: OpenSTAAdapter):
        self.cfg = config
        self.adapter = adapter
        self.objectives = TimingObjectives(
            w_wns=config.get("w_wns", 1.0),
            w_tns=config.get("w_tns", 0.5),
            w_violations=config.get("w_violations", 0.3),
        )
        self.eco = ECOHooks(max_suggestions=config.get("max_eco_suggestions", 20))
        self.ranker = CandidateRanker()
        self.results: list = []

    def _make_fitness_fn(self, benchmark: dict) -> Callable:
        """Returns a closure that evaluates one ChOA candidate position."""
        sta = IncrementalSTA(self.adapter)
        sta.load_design(benchmark)
        obj = self.objectives

        def fitness(position: np.ndarray) -> float:
            params = Population.decode(Population, position)
            report = sta.reanalyze(
                slack_margin=params["slack_margin"],
                path_count=max(10, int(params["path_count_limit"])),
            )
            score = obj.compute(report, params)
            return score.composite

        return fitness

    def run_baseline(self, benchmark: dict) -> dict:
        """OpenSTA baseline — no optimization, default parameters."""
        t0 = time.perf_counter()
        report = self.adapter.run(
            liberty=benchmark["liberty"],
            verilog=benchmark["verilog"],
            sdc=benchmark["sdc"],
            top_module=benchmark["top_module"],
            sdf=benchmark.get("sdf"),
            spef=benchmark.get("spef"),
            run_id=f"{benchmark['name']}_baseline",
        )
        elapsed = time.perf_counter() - t0
        score = self.objectives.compute(report, {})
        return {
            "benchmark": benchmark["name"],
            "family": benchmark.get("family", "unknown"),
            "method": "baseline",
            "wns": report.wns,
            "tns": report.tns,
            "violations": report.violating_paths,
            "composite_score": score.composite,
            "runtime_s": round(elapsed, 3),
            "simulated": "[SIMULATED]" in report.raw_text,
        }

    def run_random_search(self, benchmark: dict, n_trials: int, seed: int) -> dict:
        """Random search baseline over the same parameter space as ChOA."""
        rng = np.random.default_rng(seed)
        best_fitness = float("inf")
        best_params = {}
        t0 = time.perf_counter()
        sta = IncrementalSTA(self.adapter)
        sta.load_design(benchmark)

        for _ in range(n_trials):
            pos = rng.uniform(Population.LOWER, Population.UPPER)
            params = Population.decode(Population, pos)
            report = sta.reanalyze(
                slack_margin=params["slack_margin"],
                path_count=max(10, int(params["path_count_limit"])),
            )
            score = self.objectives.compute(report, params)
            if score.composite < best_fitness:
                best_fitness = score.composite
                best_params = params
                best_report = report

        elapsed = time.perf_counter() - t0
        return {
            "benchmark": benchmark["name"],
            "family": benchmark.get("family", "unknown"),
            "method": "random_search",
            "wns": best_report.wns,
            "tns": best_report.tns,
            "violations": best_report.violating_paths,
            "composite_score": best_fitness,
            "runtime_s": round(elapsed, 3),
            "simulated": "[SIMULATED]" in best_report.raw_text,
        }

    def run_choa(self, benchmark: dict, use_memory: bool = False) -> dict:
        """ChOA optimization run."""
        pop_size  = self.cfg.get("pop_size", 20)
        max_iter  = self.cfg.get("max_iter", 50)
        seed      = self.cfg.get("seed", 42)

        fitness_fn = self._make_fitness_fn(benchmark)
        t0 = time.perf_counter()

        optimizer = ChimpOptimizer(
            fitness_fn=fitness_fn,
            pop_size=pop_size,
            max_iter=max_iter,
            seed=seed,
            use_memory=use_memory,
        )
        result = optimizer.optimize()
        elapsed = time.perf_counter() - t0

        # Final evaluation with best params
        best_params = result["best_params"]
        final_report = self.adapter.run(
            liberty=benchmark["liberty"],
            verilog=benchmark["verilog"],
            sdc=benchmark["sdc"],
            top_module=benchmark["top_module"],
            sdf=benchmark.get("sdf"),
            spef=benchmark.get("spef"),
            path_count=max(10, int(best_params.get("path_count_limit", 50))),
            slack_margin=best_params.get("slack_margin", 0.0),
            run_id=f"{benchmark['name']}_choa{'_mem' if use_memory else ''}",
        )

        eco_actions = self.eco.suggest(final_report, best_params)
        critical_eps = self.ranker.rank_endpoints(final_report, top_k=10)

        method = "choa_memory" if use_memory else "choa"
        return {
            "benchmark": benchmark["name"],
            "family": benchmark.get("family", "unknown"),
            "method": method,
            "wns": final_report.wns,
            "tns": final_report.tns,
            "violations": final_report.violating_paths,
            "composite_score": result["best_fitness"],
            "runtime_s": round(elapsed, 3),
            "convergence": result["convergence"],
            "best_params": best_params,
            "eco_suggestions": self.eco.to_table(eco_actions),
            "critical_endpoints": critical_eps,
            "simulated": "[SIMULATED]" in final_report.raw_text,
        }

    def run_benchmark(self, benchmark: dict) -> list:
        """Run all methods on a single benchmark, return list of result dicts."""
        log.info("=== Benchmark: %s ===", benchmark["name"])
        methods = self.cfg.get("methods", ["baseline", "random", "choa", "choa_memory"])
        results = []

        if "baseline" in methods:
            results.append(self.run_baseline(benchmark))

        if "random" in methods:
            n_trials = self.cfg.get("pop_size", 20) * self.cfg.get("max_iter", 50)
            results.append(self.run_random_search(benchmark, n_trials, self.cfg.get("seed", 42)))

        if "choa" in methods:
            results.append(self.run_choa(benchmark, use_memory=False))

        if "choa_memory" in methods:
            results.append(self.run_choa(benchmark, use_memory=True))

        return results

    def run_all(self, registry: DatasetRegistry) -> list:
        all_results = []
        for bm in registry.benchmarks:
            try:
                res = self.run_benchmark(bm)
                all_results.extend(res)
            except Exception as e:
                log.error("Benchmark %s failed: %s", bm["name"], e, exc_info=True)
        self.results = all_results
        return all_results
