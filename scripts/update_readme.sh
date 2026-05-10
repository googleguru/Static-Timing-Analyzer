#!/usr/bin/env bash
# Regenerate README.md sections from saved CSV results and figures.
# Copyright (c) 2024 sta-choa project (MIT License)
set -euo pipefail

PYTHON="${PYTHON:-python3}"

echo "[update_readme] Regenerating README.md from saved results..."

${PYTHON} main.py report \
    --results-csv outputs/tables/all_results.csv \
    --figures-dir outputs/figures

echo "[update_readme] README.md updated."
