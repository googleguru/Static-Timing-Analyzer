"""OpenSTA subprocess adapter — executes Tcl scripts and returns parsed STAReport."""
import os
import shutil
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional

from .tcl_generator import TCLGenerator
from .report_parser import ReportParser, STAReport

log = logging.getLogger(__name__)

OPENSTA_BINARY = os.environ.get("OPENSTA_BIN", "sta")


class OpenSTAAdapter:
    """
    Runs OpenSTA as a subprocess via Tcl script generation.
    Falls back to a simulated/mock mode when OpenSTA is not installed,
    clearly marking results as SIMULATED.
    """

    def __init__(
        self,
        binary: str = OPENSTA_BINARY,
        workdir: Optional[str] = None,
        timeout: int = 300,
    ):
        self.binary = binary
        self.workdir = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix="sta_choa_"))
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.tcl_gen = TCLGenerator()
        self.parser = ReportParser()
        self._sta_available = shutil.which(binary) is not None
        if not self._sta_available:
            log.warning(
                "OpenSTA binary '%s' not found on PATH. "
                "Simulation mode active — results are SYNTHETIC, not real STA.",
                binary,
            )

    @property
    def sta_available(self) -> bool:
        return self._sta_available

    def run(
        self,
        liberty: str,
        verilog: str,
        sdc: str,
        top_module: str,
        sdf: Optional[str] = None,
        spef: Optional[str] = None,
        path_count: int = 50,
        slack_margin: float = 0.0,
        run_id: str = "run",
    ) -> STAReport:
        report_path = str(self.workdir / f"{run_id}_report.txt")
        tcl_path    = str(self.workdir / f"{run_id}.tcl")

        tcl_content = self.tcl_gen.generate(
            liberty=liberty,
            verilog=verilog,
            sdc=sdc,
            top_module=top_module,
            sdf=sdf,
            spef=spef,
            path_count=path_count,
            report_path=report_path,
            slack_margin=slack_margin,
        )
        self.tcl_gen.write(tcl_content, tcl_path)

        if self._sta_available:
            return self._run_opensta(tcl_path, report_path, run_id)
        else:
            return self._simulate(liberty, verilog, sdc, top_module, slack_margin, path_count, run_id)

    def _run_opensta(self, tcl_path: str, report_path: str, run_id: str) -> STAReport:
        cmd = [self.binary, "-exit", tcl_path]
        log.info("Running OpenSTA: %s", " ".join(cmd))
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            stdout = result.stdout + result.stderr
            log.debug("OpenSTA stdout:\n%s", stdout[:2000])

            if result.returncode != 0:
                log.error("OpenSTA exited with code %d", result.returncode)
                # Still try to parse whatever was written
        except subprocess.TimeoutExpired:
            log.error("OpenSTA timed out after %ds for run_id=%s", self.timeout, run_id)
            return STAReport(parse_ok=False)
        except Exception as e:
            log.error("OpenSTA execution failed: %s", e)
            return STAReport(parse_ok=False)

        report = self.parser.parse_file(report_path)
        report.raw_text = report.raw_text or stdout
        return report

    def _simulate(
        self,
        liberty: str,
        verilog: str,
        sdc: str,
        top_module: str,
        slack_margin: float,
        path_count: int,
        run_id: str,
    ) -> STAReport:
        """
        Deterministic synthetic timing model used when OpenSTA is unavailable.
        Results are clearly marked SIMULATED and must not be presented as real STA.
        Values are derived from design file heuristics + noise for realism.
        """
        import hashlib
        import math
        import numpy as np

        seed_str = f"{liberty}{verilog}{sdc}{top_module}{run_id}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**31)
        rng = np.random.default_rng(seed)

        # Heuristic: read netlist size as proxy for complexity
        try:
            vlines = Path(verilog).read_text(errors="replace").count('\n')
        except Exception:
            vlines = 200

        complexity = math.log1p(vlines) / math.log1p(1000)

        # Simulate base WNS worsening with complexity, improved by slack_margin
        base_wns = -(complexity * 2.0 + rng.uniform(0, 0.5)) + slack_margin
        base_tns = base_wns * rng.uniform(3.0, 8.0) * complexity
        n_viol   = max(0, int(-base_tns / 0.3 + rng.integers(0, 5)))
        n_paths  = min(path_count, max(n_viol + rng.integers(2, 10), 10))

        from .report_parser import TimingPath
        paths = []
        for i in range(int(n_paths)):
            slack = base_wns + rng.uniform(0, abs(base_wns) * 1.5)
            p = TimingPath(
                startpoint=f"ff_{i}/Q",
                endpoint=f"ff_{i+1}/D",
                path_group="clk",
                path_type="max",
                slack=round(float(slack), 4),
                is_violated=slack < 0.0,
            )
            paths.append(p)

        report = STAReport(
            wns=round(float(base_wns), 4),
            tns=round(float(sum(p.slack for p in paths if p.is_violated)), 4),
            violating_paths=sum(1 for p in paths if p.is_violated),
            total_paths=len(paths),
            paths=paths,
            parse_ok=True,
            raw_text="[SIMULATED — OpenSTA not available]",
        )
        log.warning("SIMULATED STA result for %s: WNS=%.4f TNS=%.4f", run_id, report.wns, report.tns)
        return report

    def get_version(self) -> str:
        if not self._sta_available:
            return "not-installed (simulation mode)"
        try:
            r = subprocess.run([self.binary, "-version"], capture_output=True, text=True, timeout=10)
            return r.stdout.strip() or r.stderr.strip()
        except Exception:
            return "unknown"
