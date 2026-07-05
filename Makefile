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
	@echo "$(BLUE)╔══════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║     CrocodilianClassifier                     ║$(NC)"
	@echo "$(BLUE)╚══════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BOLD)Классификация:$(NC)"
	@echo "  $(GREEN)make train-cnn$(NC)          	— CNN"
	@echo "  $(GREEN)make train-mlp$(NC)          	— MLP"
	@echo "  $(GREEN)make train-resnet20$(NC)     	— ResNet20"
	@echo "  $(GREEN)make train-mobilenet$(NC)    	— MobileNetV2"
	@echo "  $(GREEN)make train-all$(NC)          	— Все модели"
	@echo ""
	@echo "$(BOLD)Сегментация (YOLOv8):$(NC)"
	@echo "  $(GREEN)make train-yolo-n$(NC)       	— yolov8n-seg, nano (50ep, AdamW, lr=0.0005, batch=8)"
	@echo "  $(GREEN)make train-yolo-s$(NC)       	— yolov8s-seg, small (50ep, AdamW, lr=0.0005, batch=8)"
	@echo "  $(GREEN)make train-yolo-m$(NC)       	— yolov8m-seg, medium (50ep, AdamW, lr=0.0005, batch=8)"
	@echo "  $(GREEN)make train-yolo-l$(NC)       	— yolov8l-seg, large (50ep, AdamW, lr=0.0005, batch=8)"
	@echo "  $(GREEN)make train-yolo-xl$(NC)      	— yolov8x-seg, xlarge (50ep, AdamW, lr=0.0005, batch=8)"
	@echo "  $(CYAN)  MODEL=yolov8n-seg$(NC)     	— модель сегментации"
	@echo "  $(CYAN)  EPOCHS=100$(NC)            	— количество эпох"
	@echo "  $(CYAN)  OPTIMIZER=SGD$(NC)         	— оптимизатор (Adam, AdamW, SGD)"
	@echo "  $(CYAN)  LR=0.001$(NC)              	— learning rate"
	@echo "  $(CYAN)  BATCH_SIZE=16$(NC)         	— размер батча"
	@echo "  $(CYAN)  DEVICE=cpu$(NC)            	— устройство (cuda, cpu)"
	@echo ""
	@echo "$(BOLD)Docker:$(NC)"
	@echo "  $(GREEN)make full-up$(NC)           	— Все сервисы"
	@echo "  $(GREEN)make full-down$(NC)         	— Остановить"
	@echo "  $(GREEN)make deploy$(NC)            	— Пересобрать и запустить"
	@echo "  $(GREEN)make backend-restart$(NC)   	— Перезапустить Django"
	@echo "  $(GREEN)make frontend-restart$(NC)  	— Перезапустить React"
	@echo "  $(CYAN)  service=backend$(NC)       	— сервис для логов"
	@echo ""
	@echo "$(BOLD)MLflow / MinIO:$(NC)"
	@echo "  $(GREEN)make mlflow-up$(NC)         	— MLflow сервер"
	@echo "  $(GREEN)make list-mlflow-runs$(NC)  	— Список запусков"
	@echo "  $(GREEN)make minio-up$(NC)          	— MinIO"
	@echo "  $(GREEN)make minio-console$(NC)     	— MinIO Console"
	@echo ""
	@echo "$(BOLD)Django / Frontend:$(NC)"
	@echo "  $(GREEN)make run-django$(NC)        	— Django локально"
	@echo "  $(GREEN)make migrate$(NC)           	— Миграции БД"
	@echo "  $(GREEN)make frontend-dev$(NC)      	— React dev сервер"
	@echo ""
	@echo "$(BOLD)Датасет:$(NC)"
	@echo "  $(GREEN)make download$(NC)          	— Скачать изображения"
	@echo "  $(GREEN)make dataset-stats$(NC)     	— Статистика"
	@echo ""
	@echo "$(BOLD)Git:$(NC)"
	@echo "  $(GREEN)make git-template$(NC)      	— Подключить шаблон коммита"

git-template: ## Подключить шаблон сообщения коммита (.gitmessage)
	@git config commit.template "$(CURDIR)/.gitmessage"
	@echo "$(GREEN)commit.template -> $(CURDIR)/.gitmessage$(NC)"

.PHONY: help git-template
