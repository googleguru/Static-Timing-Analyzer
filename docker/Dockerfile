# ─────────────────────────────────────────────────────────────────────────────
# sta-choa Dockerfile
# Builds OpenSTA from source (https://github.com/The-OpenROAD-Project/OpenSTA)
# then installs the Python analysis layer.
#
# Copyright notice for OpenSTA:
#   Copyright (c) 2019, Parallax Software, Inc.
#   Licensed under the GNU General Public License v3.
#   https://github.com/The-OpenROAD-Project/OpenSTA/blob/master/LICENSE
#   This Dockerfile does NOT modify or redistribute OpenSTA source or binaries;
#   it builds them from the upstream public repository at runtime.
#
# sta-choa wrapper: Copyright (c) 2024 sta-choa project (MIT License)
# ─────────────────────────────────────────────────────────────────────────────

FROM ubuntu:22.04 AS opensta-builder

ARG OPENSTA_TAG=v2.6.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git cmake build-essential \
    tcl-dev tcllib \
    libeigen3-dev \
    libspdlog-dev \
    libboost-all-dev \
    swig \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN git clone --depth 1 --branch ${OPENSTA_TAG} \
    https://github.com/The-OpenROAD-Project/OpenSTA.git opensta

WORKDIR /build/opensta/build
RUN cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/opt/opensta \
    && make -j$(nproc) \
    && make install

# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV OPENSTA_BIN=/opt/opensta/bin/sta
ENV PATH="/opt/opensta/bin:${PATH}"

# OpenSTA runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    tcl \
    libgomp1 \
    libspdlog1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=opensta-builder /opt/opensta /opt/opensta

# Python deps
WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy framework source
COPY . /workspace

# Create output directories
RUN mkdir -p outputs/figures outputs/tables outputs/logs outputs/reports outputs/sta_work

ENTRYPOINT ["bash", "docker/entrypoint.sh"]
CMD ["eval"]
