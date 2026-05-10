.PHONY: build docker-build run eval ablation report clean install lint

PYTHON     := python3
DOCKER     := docker
IMAGE_NAME := sta-choa
CONTAINER  := sta-choa-run
OUT_DIR    := outputs

build:
	pip install -r requirements.txt
	$(PYTHON) setup.py develop

docker-build:
	$(DOCKER) build -t $(IMAGE_NAME) -f docker/Dockerfile .

docker-run:
	$(DOCKER) compose -f docker/docker-compose.yml up --build

run:
	$(PYTHON) main.py run --config configs/default.yaml

eval:
	$(PYTHON) main.py eval --config configs/default.yaml

ablation:
	$(PYTHON) main.py ablation --config configs/ablation.yaml

report:
	$(PYTHON) main.py report

bench-prep:
	bash scripts/run_benchmarks.sh

opensta-build:
	bash scripts/build_opensta.sh

update-readme:
	bash scripts/update_readme.sh

clean:
	rm -rf $(OUT_DIR)/figures/* $(OUT_DIR)/tables/* $(OUT_DIR)/logs/* $(OUT_DIR)/reports/*
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

lint:
	$(PYTHON) -m py_compile src/**/*.py && echo "Syntax OK"

help:
	@echo "Targets: build docker-build docker-run run eval ablation report bench-prep opensta-build update-readme clean lint"
