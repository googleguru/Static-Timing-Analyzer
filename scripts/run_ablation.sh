#!/usr/bin/env bash
# Run ablation study across all four method variants.
# Copyright (c) 2024 sta-choa project (MIT License)
set -euo pipefail

CONFIG="${CONFIG:-configs/ablation.yaml}"
OUT_DIR="${OUT_DIR:-outputs}"
PYTHON="${PYTHON:-python3}"

echo "[run_ablation] Config  : ${CONFIG}"
echo "[run_ablation] Out dir : ${OUT_DIR}"

mkdir -p "${OUT_DIR}/figures" "${OUT_DIR}/tables" "${OUT_DIR}/logs" "${OUT_DIR}/sta_work"

${PYTHON} main.py ablation --config "${CONFIG}" --out-dir "${OUT_DIR}" \
    2>&1 | tee "${OUT_DIR}/logs/ablation_$(date +%Y%m%d_%H%M%S).log"

echo "[run_ablation] Done. Results in ${OUT_DIR}/tables/ablation_results.csv"
