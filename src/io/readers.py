"""File readers for Liberty, Verilog, SDC, SPEF, SDF formats."""
import re
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class LibertyMeta:
    path: Path
    library_name: str = ""
    cells: list = field(default_factory=list)
    time_unit: str = "1ns"


@dataclass
class VerilogMeta:
    path: Path
    top_module: str = ""
    modules: list = field(default_factory=list)
    port_count: int = 0


@dataclass
class SDCMeta:
    path: Path
    clocks: list = field(default_factory=list)
    period_ns: float = 0.0


@dataclass
class SPEFMeta:
    path: Path
    net_count: int = 0


@dataclass
class SDFMeta:
    path: Path
    cell_count: int = 0


class LibertyReader:
    def read(self, path: str) -> LibertyMeta:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Liberty file not found: {path}")
        meta = LibertyMeta(path=p)
        text = p.read_text(errors="replace")
        m = re.search(r'library\s*\(\s*(\S+)\s*\)', text)
        if m:
            meta.library_name = m.group(1).strip('"')
        meta.cells = re.findall(r'\bcell\s*\(\s*["\']?(\w+)["\']?\s*\)', text)
        tu = re.search(r'time_unit\s*:\s*"([^"]+)"', text)
        if tu:
            meta.time_unit = tu.group(1)
        log.debug("Liberty: lib=%s cells=%d", meta.library_name, len(meta.cells))
        return meta


class VerilogReader:
    def read(self, path: str) -> VerilogMeta:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Verilog file not found: {path}")
        meta = VerilogMeta(path=p)
        text = p.read_text(errors="replace")
        modules = re.findall(r'\bmodule\s+(\w+)', text)
        meta.modules = modules
        meta.top_module = modules[0] if modules else ""
        ports = re.findall(r'\b(?:input|output|inout)\s+(?:\[[\d:]+\]\s+)?(\w+)', text)
        meta.port_count = len(ports)
        log.debug("Verilog: top=%s modules=%d", meta.top_module, len(meta.modules))
        return meta


class SDCReader:
    def read(self, path: str) -> SDCMeta:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"SDC file not found: {path}")
        meta = SDCMeta(path=p)
        text = p.read_text(errors="replace")
        clk_lines = re.findall(r'create_clock[^\n]+', text)
        meta.clocks = clk_lines
        periods = re.findall(r'-period\s+([\d.]+)', text)
        if periods:
            meta.period_ns = float(periods[0])
        log.debug("SDC: clocks=%d period=%.2f", len(meta.clocks), meta.period_ns)
        return meta


class SPEFReader:
    def read(self, path: str) -> SPEFMeta:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"SPEF file not found: {path}")
        meta = SPEFMeta(path=p)
        text = p.read_text(errors="replace")
        meta.net_count = text.count("*D_NET")
        log.debug("SPEF: nets=%d", meta.net_count)
        return meta


class SDFReader:
    def read(self, path: str) -> SDFMeta:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"SDF file not found: {path}")
        meta = SDFMeta(path=p)
        text = p.read_text(errors="replace")
        meta.cell_count = text.count("(CELL")
        log.debug("SDF: cells=%d", meta.cell_count)
        return meta
