"""Auto-updates README.md with results tables, figure embeds, and reproduction commands."""
import logging
import re
from pathlib import Path
from typing import List, Optional

import pandas as pd

log = logging.getLogger(__name__)

_SECTION_RE = re.compile(r"(<!-- STA:(\w+):BEGIN -->)(.*?)(<!-- STA:\2:END -->)", re.DOTALL)


class READMEUpdater:
    MARKER_BEGIN = "<!-- STA:{section}:BEGIN -->"
    MARKER_END   = "<!-- STA:{section}:END -->"

    def __init__(self, readme_path: str = "README.md"):
        self.path = Path(readme_path)

    def _wrap(self, section: str, content: str) -> str:
        b = self.MARKER_BEGIN.format(section=section)
        e = self.MARKER_END.format(section=section)
        return f"{b}\n{content}\n{e}"

    def _inject(self, text: str, section: str, content: str) -> str:
        marker_b = re.escape(self.MARKER_BEGIN.format(section=section))
        marker_e = re.escape(self.MARKER_END.format(section=section))
        pattern  = rf"{marker_b}.*?{marker_e}"
        new_block = self._wrap(section, content)
        if re.search(pattern, text, re.DOTALL):
            return re.sub(pattern, new_block, text, flags=re.DOTALL)
        return text + "\n\n" + new_block + "\n"

    def update_section(self, section: str, content: str) -> None:
        text = self.path.read_text() if self.path.exists() else ""
        text = self._inject(text, section, content)
        self.path.write_text(text)
        log.info("README section '%s' updated", section)

    def update_results_table(self, results: List[dict]) -> None:
        flat = [{k: v for k, v in r.items() if not isinstance(v, (list, dict))} for r in results]
        df = pd.DataFrame(flat)
        if df.empty:
            return
        cols = ["benchmark", "method", "wns", "tns", "violations", "composite_score", "runtime_s", "simulated"]
        cols = [c for c in cols if c in df.columns]
        md = df[cols].to_markdown(index=False)
        self.update_section("RESULTS", md)

    def update_figures(self, figure_paths: List[Path], figure_dir: str = "outputs/figures") -> None:
        lines = []
        for p in figure_paths:
            rel = Path(figure_dir) / p.name
            lines.append(f"![{p.stem}]({rel})")
        self.update_section("FIGURES", "\n\n".join(lines))

    def update_summary(self, skipped: List[tuple], simulated: bool) -> None:
        lines = []
        if simulated:
            lines.append("> **Note:** OpenSTA not detected — results are SIMULATED (synthetic model). "
                         "Install OpenSTA and set `OPENSTA_BIN` to run real timing analysis.")
        if skipped:
            lines.append("\n**Skipped benchmarks:**")
            for name, reason in skipped:
                lines.append(f"- `{name}`: {reason}")
        self.update_section("NOTES", "\n".join(lines))

    def update_commands(self) -> None:
        md = """\
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run with synthetic benchmarks (no OpenSTA required)
python main.py run --config configs/default.yaml

# 3. Full evaluation (all methods)
python main.py eval --config configs/default.yaml

# 4. Ablation study
python main.py ablation --config configs/ablation.yaml

# 5. Generate report + update README
python main.py report

# 6. Docker (full OpenSTA build)
make docker-build
make docker-run
```"""
        self.update_section("COMMANDS", md)
