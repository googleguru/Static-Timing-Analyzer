"""Incremental STA wrapper — re-runs timing analysis after ECO without reloading design."""
import logging
from typing import Optional

from .opensta_adapter import OpenSTAAdapter
from .report_parser import STAReport

log = logging.getLogger(__name__)


class IncrementalSTA:
    """
    Wraps OpenSTAAdapter to support incremental re-analysis.
    Maintains state between runs (loaded design context).
    In the current Tcl-subprocess model, each call fully reloads;
    true incremental mode requires a persistent Tcl session (future extension).
    """

    def __init__(self, adapter: OpenSTAAdapter):
        self.adapter = adapter
        self._last_manifest: Optional[dict] = None
        self._call_count = 0

    def load_design(self, benchmark: dict) -> None:
        self._last_manifest = benchmark
        self._call_count = 0
        log.debug("IncrementalSTA: design loaded — %s", benchmark.get("name"))

    def reanalyze(
        self,
        slack_margin: float = 0.0,
        path_count: int = 50,
        extra_label: str = "",
    ) -> STAReport:
        if self._last_manifest is None:
            raise RuntimeError("Call load_design() before reanalyze()")
        bm = self._last_manifest
        self._call_count += 1
        run_id = f"{bm['name']}_incr_{self._call_count}{extra_label}"
        report = self.adapter.run(
            liberty=bm["liberty"],
            verilog=bm["verilog"],
            sdc=bm["sdc"],
            top_module=bm["top_module"],
            sdf=bm.get("sdf"),
            spef=bm.get("spef"),
            path_count=path_count,
            slack_margin=slack_margin,
            run_id=run_id,
        )
        log.debug("IncrementalSTA reanalyze #%d: WNS=%.4f TNS=%.4f", self._call_count, report.wns, report.tns)
        return report

    @property
    def call_count(self) -> int:
        return self._call_count
