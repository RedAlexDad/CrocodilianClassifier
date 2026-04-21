# Makefile для домашнего задания №1
# РНС | МГТУ им. Баумана
# Классификация: крокодил, аллигатор, кайман

# ==============================================================================
# Переменные
# ==============================================================================
PYTHON ?= python3
PIP ?= pip3
DOCKER := docker
DOCKER_COMPOSE := $(DOCKER) compose -f docker-compose.yml

# Директории
TRAINING_DIR := training
DATA_DIR := data
DJANGO_DIR := django-webapp

# Классы датасета
CLASSES ?= крокодил аллигатор кайман
IMAGES_PER_CLASS ?= 100

# S3
S3_BUCKET ?= dz1-media
S3_ENDPOINT ?= http://localhost:9000

# MLflow
MLFLOW_URI ?= http://localhost:5000

# Цвета
GREEN  := $(shell tput setaf 2 2>/dev/null || echo "")
YELLOW := $(shell tput setaf 3 2>/dev/null || echo "")
BLUE   := $(shell tput setaf 4 2>/dev/null || echo "")
RED    := $(shell tput setaf 1 2>/dev/null || echo "")
NC     := $(shell tput sgr0 2>/dev/null || echo "")

.PHONY: help

# ==============================================================================
# Параметры обучения (можно переопределить через переменные)
# ==============================================================================
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

# ==============================================================================
# Основное
# ==============================================================================

help: ## Показать справку
	@echo ""
	@echo "$(BLUE)Крокодилы - Классификатор ДЗ1$(NC)"
	@echo ""
	@echo "$(GREEN)Обучение (просто):$(NC)"
	@echo "  $(MAKE) train-cnn           Обучить CNN"
	@echo "  $(MAKE) train-mlp           Обучить MLP"
	@echo "  $(MAKE) train-resnet20      Обучить ResNet20"
	@echo "  $(MAKE) train-all          Обучить все модели"
	@echo ""
	@echo "$(GREEN)Обучение с параметрами:$(NC)"
	@echo "  $(MAKE) train MODEL=cnn OPTIMIZER=sgd EPOCHS=100 LR=0.01"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  $(MAKE) full-up             Запустить все сервисы"
	@echo "  $(MAKE) build               Собрать Docker"
	@echo "  $(MAKE) logs service=mlflow Логи сервиса"
	@echo ""
	@echo "$(GREEN)MLflow:$(NC)"
	@echo "  $(MAKE) mlflow-up          Запустить MLflow"
	@echo "  $(MAKE) mlflow-logs         Логи MLflow"
	@echo ""
	@echo "$(GREEN)MinIO:$(NC)"
	@echo "  $(MAKE) minio-up           Запустить MinIO"
	@echo "  $(MAKE) minio-console       MinIO Console"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  $(MAKE) full-up                       Запустить все сервисы"
	@echo "  $(MAKE) full-down                     Остановить все сервисы"
	@echo "  $(MAKE) build                        Собрать Docker образ"
	@echo "  $(MAKE) logs [service=web|mlflow|minio]  Логи сервиса"
	@echo "  $(MAKE) clean                        Очистить контейнеры"
	@echo ""
	@echo "$(GREEN)MLflow:$(NC)"
	@echo "  $(MAKE) mlflow-up                     Запустить MLflow"
	@echo "  $(MAKE) mlflow-logs                  Логи MLflow"
	@echo ""
	@echo "$(GREEN)MinIO:$(NC)"
	@echo "  $(MAKE) minio-up                     Запустить MinIO"
	@echo "  $(MAKE) minio-console                Открыть MinIO Console"
	@echo ""
	@echo "$(GREEN)Django:$(NC)"
	@echo "  $(MAKE) run-django                  Запустить Django локально"
	@echo "  $(MAKE) collectstatic               Собрать static файлы"
	@echo ""
	@echo "$(GREEN)Датасет:$(NC)"
	@echo "  $(MAKE) download CLASSES='крокодил аллигатор кайман'  Скачать изображения"
	@echo "  $(MAKE) dataset-stats                Показать статистику"

# ==============================================================================
# Обучение моделей
# ==============================================================================

train: ## Обучить: make train MODEL=cnn OPTIMIZER=adam EPOCHS=50 LR=0.001
	@echo "$(GREEN)Обучение: MODEL=$(MODEL), OPTIMIZER=$(OPTIMIZER), EPOCHS=$(EPOCHS)$(NC)"
	cd $(TRAINING_DIR) && $(PYTHON) main.py \
		--model $(MODEL) \
		--optimizer $(OPTIMIZER) \
		--epochs $(EPOCHS) \
		--epochs-stage1 $(EPOCHS_STAGE1) \
		--finetune-layers $(FINETUNE_LAYERS) \
		--lr $(LR) \
		--lr-finetune $(LR_FINETUNE) \
		--batch-size $(BATCH_SIZE) \
		--weight-decay $(WEIGHT_DECAY) \
		--seed $(SEED)

train-all: ## Обучить все модели
	@echo "$(GREEN)Обучение всех моделей...$(NC)"
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model all

train-compared: ## Сравнить все оптимизаторы
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model all --compare-optimizers

# ==============================================================================
# Shortcut команды для обучения (используют переменные above)
# ==============================================================================

train-mlp: ## make train-mlp
	$(MAKE) train MODEL=mlp

train-cnn: ## make train-cnn
	$(MAKE) train MODEL=cnn OPTIMIZER=sgd

train-resnet20: ## make train-resnet20
	$(MAKE) train MODEL=resnet20

train-mobilenet: ## make train-mobilenet
	$(MAKE) train MODEL=mobilenet
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model all

train-compared: ## Сравнить все оптимизаторы
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model all --compare-optimizers

# ==============================================================================
# Docker Compose
# ==============================================================================

full-up: ## Запустить все сервисы (Django + MinIO + MLflow)
	@echo "$(GREEN)Запуск всех сервисов...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@sleep 10
	@echo ""
	@echo "$(GREEN)Сервисы запущены:$(NC)"
	@echo "$(YELLOW)Django:      http://localhost:8000$(NC)"
	@echo "$(YELLOW)MinIO API:   http://localhost:9000$(NC)"
	@echo "$(YELLOW)MinIO Console: http://localhost:9001$(NC)"
	@echo "$(YELLOW)MLflow:      http://localhost:5000$(NC)"

full-down: ## Остановить все сервисы
	@echo "$(GREEN)Остановка сервисов...$(NC)"
	$(DOCKER_COMPOSE) down

full-restart: ## Перезапустить все сервисы
	$(MAKE) full-down
	$(MAKE) full-up

build: ## Собрать Docker образ
	@echo "$(GREEN)Сборка Docker образа...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache

logs: ## Логи сервиса (service=web|mlflow|minio)
	$(DOCKER_COMPOSE) logs -f $(service)

clean: ## Очистить Docker ресурсы
	@echo "$(YELLOW)Очистка...$(NC)"
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f

# ==============================================================================
# MLflow
# ==============================================================================

mlflow-up: ## Запустить MLflow сервер
	@echo "$(GREEN)Запуск MLflow...$(NC)"
	$(DOCKER_COMPOSE) up -d mlflow minio minio-init
	@echo "$(YELLOW)MLflow: http://localhost:5000$(NC)"

mlflow-logs: ## Логи MLflow
	$(DOCKER_COMPOSE) logs -f mlflow

# ==============================================================================
# MinIO
# ==============================================================================

minio-up: ## Запустить MinIO
	@echo "$(GREEN)Запуск MinIO...$(NC)"
	$(DOCKER_COMPOSE) up -d minio minio-init
	@echo "$(YELLOW)MinIO API:   http://localhost:9000$(NC)"
	@echo "$(YELLOW)MinIO Console: http://localhost:9001$(NC)"

minio-console: ## MinIO Console
	@echo "$(BLUE)Открытие MinIO Console...$(NC)"
	@xdg-open http://localhost:9001 || echo "Откройте http://localhost:9001"

# ==============================================================================
# Django
# ==============================================================================

run-django: ## Запустить Django локально
	@echo "$(GREEN)Запуск Django...$(NC)"
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py runserver

collectstatic: ## Собрать static файлы
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py collectstatic --noinput

migrate: ## Миграции БД
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py migrate

shell: ## Django shell
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py shell

# ==============================================================================
# Датасет
# ==============================================================================

download: ## Скачать изображения (CLASSES='крокодил аллигатор кайман')
	@echo "$(GREEN)Скачивание изображений...$(NC)"
	$(PYTHON) download_images.py --classes $(CLASSES) --limit $(IMAGES_PER_CLASS)

dataset-stats: ## Статистика датасета
	@echo "$(GREEN)Статистика датасета:$(NC)"
	@for class in $(CLASSES); do \
		count=$$(ls $(DATA_DIR)/$$class/*.jpeg 2>/dev/null | wc -l); \
		echo "  $$class: $$count изображений"; \
	done

# ==============================================================================
# Установка
# ==============================================================================

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r $(DJANGO_DIR)/requirements.txt
	$(PIP) install torch torchvision mlflow

install-dev: ## Зависимости для разработки
	$(MAKE) install
	$(PIP) install black flake8 mypy

# ==============================================================================
# Тестирование
# ==============================================================================

test: ## Запустить тесты
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py test

lint: ## Проверка кода
	@command -v flake8 >/dev/null 2>&1 && cd . && flake8 . --ignore=E501,W503 || echo "flake8 не установлен"

format: ## Форматировать код
	@command -v black >/dev/null 2>&1 && black . || echo "black не установлен"

# ==============================================================================
# По умолчанию
# ==============================================================================

default: help