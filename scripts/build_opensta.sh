#!/usr/bin/env bash
# Build OpenSTA from source (native, outside Docker).
# Copyright (c) 2024 sta-choa project (MIT License)
#
# OpenSTA copyright: Copyright (c) 2019, Parallax Software, Inc. (GPL v3)
# Source: https://github.com/The-OpenROAD-Project/OpenSTA
set -euo pipefail

OPENSTA_TAG="${OPENSTA_TAG:-v2.6.0}"
INSTALL_PREFIX="${INSTALL_PREFIX:-/opt/opensta}"
BUILD_DIR="${BUILD_DIR:-/tmp/opensta_build}"

echo "[build_opensta] Tag    : ${OPENSTA_TAG}"
echo "[build_opensta] Install: ${INSTALL_PREFIX}"
echo "[build_opensta] Build  : ${BUILD_DIR}"

# ── Dependency check ──────────────────────────────────────────────────────────
check_dep() {
    command -v "$1" &>/dev/null || { echo "[ERROR] Missing: $1 — install it first."; exit 1; }
}
for dep in git cmake g++ make tcl tclsh; do
    check_dep "$dep"
done

# ── Clone ─────────────────────────────────────────────────────────────────────
mkdir -p "${BUILD_DIR}"
if [ ! -d "${BUILD_DIR}/OpenSTA" ]; then
    git clone --depth 1 --branch "${OPENSTA_TAG}" \
        https://github.com/The-OpenROAD-Project/OpenSTA.git \
        "${BUILD_DIR}/OpenSTA"
fi

# ── Configure & Build ─────────────────────────────────────────────────────────
mkdir -p "${BUILD_DIR}/OpenSTA/build"
cd "${BUILD_DIR}/OpenSTA/build"

cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="${INSTALL_PREFIX}"

make -j"$(nproc)"
make install

echo ""
echo "[build_opensta] OpenSTA installed to: ${INSTALL_PREFIX}/bin/sta"
echo "[build_opensta] Add to PATH: export PATH=\"${INSTALL_PREFIX}/bin:\$PATH\""
echo "[build_opensta] Set env var: export OPENSTA_BIN=${INSTALL_PREFIX}/bin/sta"
