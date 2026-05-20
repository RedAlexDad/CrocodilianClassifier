.PHONY: mlflow-up list-mlflow-runs add-mlflow-model minio-up minio-console minio-clear

include makefiles/_vars.mk

mlflow-up: ## Запустить MLflow сервер
	@echo "$(GREEN)Запуск MLflow...$(NC)"
	$(DOCKER_COMPOSE) up -d mlflow minio minio-init
	@echo "$(YELLOW)MLflow: http://localhost:5000$(NC)"

list-mlflow-runs: ## Показать все запуски MLflow
	@echo "$(GREEN)Запуски MLflow:${NC}"
	@python3 scripts/list_mlflow_runs.py

add-mlflow-model: ## Добавить модель из MLflow (RUN_ID=<id>)
ifndef RUN_ID
	@echo "$(RED)Ошибка: необходим RUN_ID${NC}"
	@echo "Использование: $(GREEN)make add-mlflow-model RUN_ID=<run_id>${NC}"
	@$(MAKE) list-mlflow-runs
	@exit 1
endif
	@echo "$(GREEN)Добавление модели $(RUN_ID) в репозиторий...${NC}"
	@mkdir -p $(MLRUNS_DIR)/$(RUN_ID)/artifacts
	@python3 scripts/download_mlflow_artifacts.py "1" "$(RUN_ID)" "$(MLRUNS_DIR)/$(RUN_ID)/artifacts"
	@echo ""
	@echo "$(GREEN)✓ Модель добавлена!${NC}"

minio-up: ## Запустить MinIO
	@echo "$(GREEN)Запуск MinIO...$(NC)"
	$(DOCKER_COMPOSE) up -d minio minio-init
	@echo "$(YELLOW)MinIO API:   http://localhost:9000$(NC)"
	@echo "$(YELLOW)MinIO Console: http://localhost:9001$(NC)"

minio-console: ## MinIO Console
	@echo "$(BLUE)Открытие MinIO Console...$(NC)"
	@xdg-open http://localhost:9001 || echo "Откройте http://localhost:9001"

minio-clear: ## Очистить все бакеты MinIO
	@echo "$(YELLOW)Очистка всех бакетов MinIO...$(NC)"
	@$(DOCKER_COMPOSE) exec backend python -c "\
import boto3; \
from django.conf import settings; \
import os; \
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); \
import django; \
django.setup(); \
s3 = boto3.client('s3', endpoint_url=settings.AWS_S3_ENDPOINT_URL, aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin'); \
buckets = ['crocodilian', 'crocodilian-artifacts', 'dz1-media', 'mlflow-artifacts']; \
[print(f'Очистка {b}...') or [s3.delete_objects(Bucket=b, Delete={'Objects': [{'Key': obj['Key']} for obj in s3.list_objects_v2(Bucket=b).get('Contents', [])[i:i+1000]]}) for i in range(0, len(s3.list_objects_v2(Bucket=b).get('Contents', [])), 1000)] or print(f'✓ {b} очищен') for b in buckets if s3.list_objects_v2(Bucket=b).get('Contents')]; \
print('$(GREEN)Все бакеты очищены!$(NC)'); \
"
	@echo "$(GREEN)✓ MinIO полностью очищен$(NC)"