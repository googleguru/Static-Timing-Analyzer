"""Normalizes benchmark collateral paths into a canonical manifest dict."""
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

REQUIRED_FIELDS = {"liberty", "verilog", "sdc", "top_module"}


class BenchmarkNormalizer:
    def normalize(self, raw: dict) -> dict:
        """Validate and normalize a raw YAML benchmark entry."""
        missing = REQUIRED_FIELDS - set(raw.keys())
        if missing:
            raise ValueError(f"Benchmark '{raw.get('name','?')}' missing fields: {missing}")

        norm = dict(raw)
        for key in ("liberty", "verilog", "sdc", "sdf", "spef"):
            if key in norm and norm[key]:
                p = Path(norm[key])
                if not p.exists():
                    log.warning("File missing for field '%s': %s — will be skipped", key, p)
                    norm[key] = None
                else:
                    norm[key] = str(p.resolve())
            else:
                norm.setdefault(key, None)

        norm.setdefault("family", "unknown")
        norm.setdefault("enabled", True)
        norm.setdefault("clock_period_ns", 10.0)
        return norm

    def filter_valid(self, benchmarks: list) -> tuple:
        """Return (valid_list, skipped_list)."""
        valid, skipped = [], []
        for bm in benchmarks:
            try:
                n = self.normalize(bm)
                if not n["enabled"]:
                    skipped.append((bm.get("name", "?"), "disabled"))
                    continue
                # Check required files exist after normalization
                if not n["liberty"] or not n["verilog"] or not n["sdc"]:
                    skipped.append((n["name"], "required file missing"))
                    continue
                valid.append(n)
            except ValueError as e:
                skipped.append((bm.get("name", "?"), str(e)))
        return valid, skipped
