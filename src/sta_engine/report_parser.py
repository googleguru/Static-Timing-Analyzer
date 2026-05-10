"""Parses OpenSTA text report outputs into structured dicts."""
import re
import logging
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class TimingPath:
    startpoint: str = ""
    endpoint: str = ""
    path_group: str = ""
    path_type: str = "max"
    slack: float = 0.0
    data_arrival: float = 0.0
    data_required: float = 0.0
    is_violated: bool = False


@dataclass
class STAReport:
    wns: float = 0.0
    tns: float = 0.0
    violating_paths: int = 0
    total_paths: int = 0
    paths: list = field(default_factory=list)
    clock_skew_ns: float = 0.0
    raw_text: str = ""
    parse_ok: bool = False


class ReportParser:
    # Regex patterns for OpenSTA report_checks output
    _RE_SLACK   = re.compile(r'slack\s+\(?(MET|VIOLATED)?\)?\s+([-\d.]+)', re.I)
    _RE_START   = re.compile(r'Startpoint:\s+(.+)')
    _RE_END     = re.compile(r'Endpoint:\s+(.+)')
    _RE_GROUP   = re.compile(r'Path Group:\s+(.+)')
    _RE_TYPE    = re.compile(r'Path Type:\s+(\w+)')
    _RE_ARRIVAL = re.compile(r'data arrival time\s+([-\d.]+)')
    _RE_REQD    = re.compile(r'data required time\s+([-\d.]+)')
    _RE_WNS     = re.compile(r'wns\s+([-\d.]+)', re.I)
    _RE_TNS     = re.compile(r'tns\s+([-\d.]+)', re.I)
    _RE_SKEW    = re.compile(r'Clock skew[^\n]*\n\s+([-\d.]+)', re.I)
    _RE_PATH_SEP = re.compile(r'-{40,}')

    def parse_file(self, report_path: str) -> STAReport:
        try:
            with open(report_path, errors="replace") as f:
                text = f.read()
            return self.parse_text(text)
        except FileNotFoundError:
            log.error("Report file not found: %s", report_path)
            return STAReport(parse_ok=False)

    def parse_text(self, text: str) -> STAReport:
        report = STAReport(raw_text=text)

        # WNS / TNS from summary lines
        wns_m = self._RE_WNS.search(text)
        tns_m = self._RE_TNS.search(text)
        if wns_m:
            report.wns = float(wns_m.group(1))
        if tns_m:
            report.tns = float(tns_m.group(1))

        # Clock skew
        sk_m = self._RE_SKEW.search(text)
        if sk_m:
            report.clock_skew_ns = float(sk_m.group(1))

        # Parse individual paths
        paths = self._parse_paths(text)
        report.paths = paths
        report.total_paths = len(paths)
        report.violating_paths = sum(1 for p in paths if p.is_violated)

        # Derive WNS/TNS from paths if report_wns not present
        if not wns_m and paths:
            slacks = [p.slack for p in paths]
            report.wns = min(slacks)
            report.tns = sum(s for s in slacks if s < 0.0)

        report.parse_ok = True
        log.debug("Parsed: WNS=%.4f TNS=%.4f violations=%d", report.wns, report.tns, report.violating_paths)
        return report

    def _parse_paths(self, text: str) -> list:
        paths = []
        # Split on OpenSTA path separator lines
        blocks = self._RE_PATH_SEP.split(text)
        for block in blocks:
            if 'Startpoint' not in block:
                continue
            p = TimingPath()
            m = self._RE_START.search(block)
            if m:
                p.startpoint = m.group(1).strip()
            m = self._RE_END.search(block)
            if m:
                p.endpoint = m.group(1).strip()
            m = self._RE_GROUP.search(block)
            if m:
                p.path_group = m.group(1).strip()
            m = self._RE_TYPE.search(block)
            if m:
                p.path_type = m.group(1).strip()
            m = self._RE_ARRIVAL.search(block)
            if m:
                p.data_arrival = float(m.group(1))
            m = self._RE_REQD.search(block)
            if m:
                p.data_required = float(m.group(1))
            m = self._RE_SLACK.search(block)
            if m:
                p.slack = float(m.group(2))
                p.is_violated = p.slack < 0.0
            elif p.data_arrival and p.data_required:
                p.slack = p.data_required - p.data_arrival
                p.is_violated = p.slack < 0.0
            paths.append(p)
        return paths

    def extract_endpoint_slacks(self, report: STAReport) -> dict:
        """Return {endpoint: slack} mapping from parsed paths."""
        return {p.endpoint: p.slack for p in report.paths if p.endpoint}
