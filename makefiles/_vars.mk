PYTHON ?= python3
PIP ?= pip3
DOCKER := docker
DOCKER_COMPOSE := $(DOCKER) compose -f docker-compose.yml

TRAINING_DIR := training
DATA_DIR := data
DJANGO_DIR := backend

CLASSES ?= крокодил аллигатор кайман
IMAGES_PER_CLASS ?= 100

S3_BUCKET ?= dz1-media
S3_ENDPOINT ?= http://localhost:9000
MLFLOW_URI ?= http://localhost:5000

BOLD   := $(shell printf '\033[1m' 2>/dev/null || echo "")
GREEN  := $(shell printf '\033[32;1m' 2>/dev/null || echo "")
YELLOW := $(shell printf '\033[33;1m' 2>/dev/null || echo "")
BLUE   := $(shell printf '\033[34;1m' 2>/dev/null || echo "")
CYAN   := $(shell printf '\033[36;1m' 2>/dev/null || echo "")
RED    := $(shell printf '\033[31;1m' 2>/dev/null || echo "")
NC     := $(shell printf '\033[0m' 2>/dev/null || echo "")

MODEL ?= cnn
OPTIMIZER ?= adam
EPOCHS ?= 50
EPOCHS_STAGE1 ?= 50
FINETUNE_LAYERS ?= 20
LR ?= 0.001
LR_FINETUNE ?= 0.0001
BATCH_SIZE ?= 32
WEIGHT_DECAY ?= 0.0001
SEED ?= 42
DEVICE ?= cuda

MLRUNS_DIR := mlruns