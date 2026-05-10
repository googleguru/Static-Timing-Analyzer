"""Registry that loads benchmark manifests from YAML and tracks dataset metadata."""
import yaml
import logging
from pathlib import Path
from .benchmark_normalizer import BenchmarkNormalizer

log = logging.getLogger(__name__)


class DatasetRegistry:
    def __init__(self):
        self._benchmarks: list = []
        self._skipped: list = []
        self._normalizer = BenchmarkNormalizer()

    def load_manifest(self, manifest_path: str) -> None:
        p = Path(manifest_path)
        if not p.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        with open(p) as f:
            data = yaml.safe_load(f)
        entries = data.get("benchmarks", [])
        valid, skipped = self._normalizer.filter_valid(entries)
        self._benchmarks.extend(valid)
        self._skipped.extend(skipped)
        log.info("Manifest %s: %d valid, %d skipped", p.name, len(valid), len(skipped))
        for name, reason in skipped:
            log.warning("  SKIP benchmark '%s': %s", name, reason)

    def load_manifests(self, manifest_paths: list) -> None:
        for mp in manifest_paths:
            self.load_manifest(mp)

    @property
    def benchmarks(self) -> list:
        return list(self._benchmarks)

    @property
    def skipped(self) -> list:
        return list(self._skipped)

    def summary(self) -> dict:
        families = {}
        for bm in self._benchmarks:
            families.setdefault(bm["family"], 0)
            families[bm["family"]] += 1
        return {"total": len(self._benchmarks), "skipped": len(self._skipped), "families": families}

    def get_benchmark(self, name: str) -> dict | None:
        for bm in self._benchmarks:
            if bm["name"] == name:
                return bm
        return None
