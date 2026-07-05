# Makefile для CrocodilianClassifier
# Классификация: крокодил, аллигатор, кайман (ДЗ1)
# Сегментация: YOLOv8-segment (ДЗ2)

include makefiles/_vars.mk
include makefiles/train.mk
include makefiles/docker.mk
include makefiles/infra.mk
include makefiles/dev.mk

.DEFAULT_GOAL := help

.PHONY: help
help: ## Показать справку
	@echo ""
	@echo "$(BLUE)Крокодилы — Классификатор / Сегментатор$(NC)"
	@echo ""
	@echo "$(GREEN)Обучение классификация:$(NC)"
	@echo "  $(MAKE) train-cnn                   CNN"
	@echo "  $(MAKE) train-mlp                   MLP"
	@echo "  $(MAKE) train-resnet20              ResNet20"
	@echo "  $(MAKE) train-mobilenet             MobileNetV2"
	@echo "  $(MAKE) train-all                   Все модели"
	@echo ""
	@echo "$(GREEN)Обучение сегментация (YOLOv8):$(NC)"
	@echo "  $(MAKE) train-yolo-n                $(YELLOW)yolov8n$(NC)-seg 50ep $(BLUE)AdamW$(NC) lr=0.0005 batch=8"
	@echo "  $(MAKE) train-yolo-s                $(YELLOW)yolov8s$(NC)-seg 50ep $(BLUE)AdamW$(NC) lr=0.0005 batch=8"
	@echo "  $(MAKE) train-yolo-m                $(YELLOW)yolov8m$(NC)-seg 50ep $(BLUE)AdamW$(NC) lr=0.0005 batch=8"
	@echo "  $(MAKE) train-yolo-l                $(YELLOW)yolov8l$(NC)-seg 50ep $(BLUE)AdamW$(NC) lr=0.0005 batch=8"
	@echo "  $(MAKE) train-yolo-xl               $(YELLOW)yolov8x$(NC)-seg 50ep $(BLUE)AdamW$(NC) lr=0.0005 batch=8"
	@echo "  $(MAKE) train $(RED)MODEL=$(YELLOW)yolov8n-seg$(NC) $(RED)EPOCHS=$(GREEN)100$(NC) $(RED)BATCH_SIZE=$(GREEN)16$(NC)  Произвольные аргументы"
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
	@echo "  $(MAKE) list-mlflow-runs            Список запусков"
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

.PHONY: help git-template
