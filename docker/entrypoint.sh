#!/usr/bin/env bash
# sta-choa Docker entrypoint
# Copyright (c) 2024 sta-choa project (MIT License)
set -euo pipefail

CMD="${1:-eval}"

echo "============================================"
echo "  sta-choa: ChOA + OpenSTA Framework"
echo "  Command : ${CMD}"
echo "  OpenSTA : ${OPENSTA_BIN:-not set}"
echo "============================================"

# Verify OpenSTA
if command -v "${OPENSTA_BIN:-sta}" &>/dev/null; then
    echo "[INFO] OpenSTA found: $(${OPENSTA_BIN:-sta} -version 2>&1 | head -1)"
else
    echo "[WARN] OpenSTA not found — simulation mode will be used"
fi

# Ensure output directories exist
mkdir -p outputs/figures outputs/tables outputs/logs outputs/reports outputs/sta_work

case "${CMD}" in
    run)
        python3 main.py run --config configs/default.yaml
        ;;
    eval)
        python3 main.py eval --config configs/default.yaml
        ;;
    ablation)
        python3 main.py ablation --config configs/ablation.yaml
        ;;
    report)
        python3 main.py report
        ;;
    shell)
        exec bash
        ;;
    *)
        echo "[ERROR] Unknown command: ${CMD}"
        echo "Usage: docker run sta-choa [run|eval|ablation|report|shell]"
        exit 1
        ;;
esac

echo "[INFO] Done. Outputs in /workspace/outputs/"
