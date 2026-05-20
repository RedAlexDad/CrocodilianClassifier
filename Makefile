# Makefile для CrocodilianClassifier
# Классификация: крокодил, аллигатор, кайман (ДЗ1)
# Сегментация: YOLOv8-segment (ДЗ2)

include makefiles/_vars.mk
include makefiles/train.mk
include makefiles/docker.mk
include makefiles/infra.mk
include makefiles/dev.mk

# ==============================================================================
# Help
# ==============================================================================

help: ## Показать справку
	@echo ""
	@echo "$(BLUE)Крокодилы — Классификатор / Сегментатор$(NC)"
	@echo ""
	@echo "$(GREEN)Обучение классификация:$(NC)"
	@echo "  $(MAKE) train-cnn                   CNN"
	@echo "  $(MAKE) train-mlp                   MLP"
	@echo "  $(MAKE) train-resnet20              ResNet20"
	@echo "  $(MAKE) train-mobilenet            MobileNetV2"
	@echo "  $(MAKE) train-all                  Все модели"
	@echo ""
	@echo "$(GREEN)Обучение сегментация (YOLOv8, light):$(NC)"
	@echo "  $(MAKE) train-yolo-n               Run #1: yolov8n-seg 50ep AdamW lr=0.001"
	@echo "  $(MAKE) train-yolo-s               Run #2: yolov8n-seg 50ep SGD lr=0.01"
	@echo "  $(MAKE) train-yolo-m               Run #3: yolov8n-seg 50ep Adam lr=0.001"
	@echo "  $(MAKE) train-yolo-l               Run #4: yolov8n-seg 100ep AdamW lr=0.0001"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  $(MAKE) full-up                     Все сервисы"
	@echo "  $(MAKE) full-down                   Остановить"
	@echo "  $(MAKE) deploy                      Пересобрать и запустить"
	@echo "  $(MAKE) backend-restart             Перезапустить Django"
	@echo "  $(MAKE) frontend-restart            Перезапустить React"
	@echo "  $(MAKE) logs service=backend        Логи"
	@echo ""
	@echo "$(GREEN)MLflow / MinIO:$(NC)"
	@echo "  $(MAKE) mlflow-up                   MLflow сервер"
	@echo "  $(MAKE) list-mlflow-runs             Список запусков"
	@echo "  $(MAKE) minio-up                    MinIO"
	@echo "  $(MAKE) minio-console               MinIO Console"
	@echo ""
	@echo "$(GREEN)Django / Frontend:$(NC)"
	@echo "  $(MAKE) run-django                  Django локально"
	@echo "  $(MAKE) migrate                     Миграции БД"
	@echo "  $(MAKE) frontend-dev                React dev сервер"
	@echo ""
	@echo "$(GREEN)Датасет:$(NC)"
	@echo "  $(MAKE) download                    Скачать изображения"
	@echo "  $(MAKE) dataset-stats               Статистика"
	@echo ""
	@echo "$(GREEN)Git:$(NC)"
	@echo "  $(MAKE) git-template                Подключить шаблон коммита"

git-template: ## Подключить шаблон сообщения коммита (.gitmessage)
	@git config commit.template "$(CURDIR)/.gitmessage"
	@echo "$(GREEN)commit.template -> $(CURDIR)/.gitmessage$(NC)"

default: help

.PHONY: help git-template default