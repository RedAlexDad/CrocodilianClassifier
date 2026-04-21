# Makefile для домашнего задания №1
# РНС | МГТУ им. Баумана
# Классификация: крокодил, аллигатор, кайман
# С поддержкой MLflow, Minio, Django

# Переменные
PYTHON ?= python3
PIP ?= pip3
MANAGE := django-webapp/web-site-dl/manage.py
DOCKER_COMPOSE := docker compose -f $(DJANGO_DIR)/docker-compose.yml
DOCKER := docker

# Директории
TRAINING_DIR := training
DATA_DIR := data
DJANGO_DIR := django-webapp

# Классы датасета
CLASSES ?= крокодил аллигатор кайман

# MLflow
MLFLOW_URI ?= http://localhost:5000

# Цвета
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m

.PHONY: help install train test run-full run-django download-images

# ==============================================================================
# Основное
# ==============================================================================

help: ## Показать справку
	@echo ""
	@echo "Крокодилы - Makefile Справка"
	@echo ""
	@echo "Обучение:"
	@echo "  make train model=cnn         Обучить модель (mlp|cnn|resnet20|mobilenet)"
	@echo "  make train model=all          Обучить все модели"
	@echo ""
	@echo "Запуск:"
	@echo "  make full-up                Запустить все сервисы"
	@echo "  make run-django            Запустить Django"
	@echo ""
	@echo "MLflow:"
	@echo "  make mlflow-up              Запустить MLflow"
	@echo "  make mlflow-logs            Логи MLflow"
	@echo ""
	@echo "MinIO:"
	@echo "  make minio-up              Запустить MinIO"
	@echo ""

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	cd $(DJANGO_DIR) && $(PIP) install -r requirements.txt
	cd $(TRAINING_DIR) && $(PIP) install torch torchvision mlflow

# ==============================================================================
# Обучение моделей
# ==============================================================================

train: ## Обучить модель
	@echo "$(GREEN)Обучение модели: $(model)$(NC)"
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model $(model)

train-mlp: ## Обучить MLP
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model mlp

train-cnn: ## Обучить CNN
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model cnn

train-resnet20: ## Обучить ResNet20
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model resnet20

train-mobilenet: ## Обучить MobileNetV2
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model mobilenet

train-all: ## Обучить все модели
	@echo "$(GREEN)Обучение всех моделей...$(NC)"
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model all

# ==============================================================================
# Docker и сервисы
# ==============================================================================

full-up: ## Запустить все сервисы (Django + MinIO + MLflow)
	@echo "$(GREEN)Запуск всех сервисов...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@sleep 5
	@echo "$(GREEN)Сервисы запущены!$(NC)"
	@echo "$(YELLOW)Django: http://localhost:8000$(NC)"
	@echo "$(YELLOW)MinIO API: http://localhost:9000$(NC)"
	@echo "$(YELLOW)MinIO Console: http://localhost:9001$(NC)"
	@echo "$(YELLOW)MLflow: http://localhost:5000$(NC)"

full-down: ## Остановить все сервисы
	@echo "$(GREEN)Остановка сервисов...$(NC)"
	$(DOCKER_COMPOSE) down

mlflow-up: ## Запустить MLflow
	@echo "$(GREEN)Запуск MLflow...$(NC)"
	$(DOCKER_COMPOSE) up -d mlflow
	@echo "$(YELLOW)MLflow: http://localhost:5000$(NC)"

mlflow-logs: ## Логи MLflow
	$(DOCKER_COMPOSE) logs -f mlflow

minio-up: ## Запустить MinIO
	@echo "$(GREEN)Запуск MinIO...$(NC)"
	$(DOCKER_COMPOSE) up -d minio minio-init
	@echo "$(YELLOW)MinIO API: http://localhost:9000$(NC)"
	@echo "$(YELLOW)MinIO Console: http://localhost:9001$(NC)"

run-django: ## Запустить Django
	@echo "$(GREEN)Запуск Django...$(NC)"
	cd $(DJANGO_DIR) && $(MANAGE) runserver

docker-build: ## Собрать Docker образ
	$(DOCKER_COMPOSE) build

docker-rebuild: ## Пересобрать и запустить
	$(DOCKER_COMPOSE) up -d --build

docker-logs: ## Логи
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Очистить
	$(DOCKER_COMPOSE) down -v

# ==============================================================================
# Датасет
# ==============================================================================

download-images: ## Скачать изображения
	@echo "$(GREEN)Скачивание изображений...$(NC)"
	$(PYTHON) download_images.py --classes "$(CLASSES)"

dataset-stats: ## Показать статистику датасета
	@echo "$(GREEN)Статистика датасета:$(NC)"
	@for class in $(CLASSES); do \
		count=$$(ls $(DATA_DIR)/$$class/*.jpeg 2>/dev/null | wc -l); \
		echo "  $$class: $$count изображений"; \
	done

# ==============================================================================
# По умолчанию
# ==============================================================================

default: help