#!/usr/bin/env bash
# Run full benchmark evaluation.
# Copyright (c) 2024 sta-choa project (MIT License)
set -euo pipefail

CONFIG="${CONFIG:-configs/default.yaml}"
OUT_DIR="${OUT_DIR:-outputs}"
PYTHON="${PYTHON:-python3}"

echo "[run_benchmarks] Config  : ${CONFIG}"
echo "[run_benchmarks] Out dir : ${OUT_DIR}"

# Generate synthetic benchmarks if not present
if [ ! -f "benchmarks/synthetic/synth_small.v" ]; then
    echo "[run_benchmarks] Generating synthetic benchmarks..."
    ${PYTHON} benchmarks/synthetic/gen_synthetic.py --out-dir benchmarks/synthetic
fi

# Create output directories
mkdir -p "${OUT_DIR}/figures" "${OUT_DIR}/tables" "${OUT_DIR}/logs" "${OUT_DIR}/reports" "${OUT_DIR}/sta_work"

# Run evaluation
echo "[run_benchmarks] Starting evaluation..."
${PYTHON} main.py eval --config "${CONFIG}" --out-dir "${OUT_DIR}" \
    2>&1 | tee "${OUT_DIR}/logs/eval_$(date +%Y%m%d_%H%M%S).log"

echo "[run_benchmarks] Done. Results in ${OUT_DIR}/"
