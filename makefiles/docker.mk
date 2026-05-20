.PHONY: full-up full-down full-restart build build-no-cache rebuild deploy
.PHONY: frontend-build frontend-dev frontend-rebuild frontend-restart
.PHONY: backend-rebuild backend-restart web-restart restart web-rebuild
.PHONY: logs frontend-logs backend-logs web-logs mlflow-logs minio-logs clean

include makefiles/_vars.mk

full-up: ## Запустить все сервисы
	@echo "$(GREEN)Запуск всех сервисов...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@sleep 5
	@echo "$(GREEN)Сервисы запущены!$(NC)"
	@echo "$(YELLOW)Frontend:   http://localhost:5173$(NC)"
	@echo "$(YELLOW)Django:      http://localhost:8000$(NC)"
	@echo "$(YELLOW)MinIO API:   http://localhost:9000$(NC)"
	@echo "$(YELLOW)MinIO Console: http://localhost:9001$(NC)"
	@echo "$(YELLOW)MLflow:      http://localhost:5000$(NC)"

full-down: ## Остановить все сервисы
	@echo "$(GREEN)Остановка сервисов...$(NC)"
	$(DOCKER_COMPOSE) down

full-restart:
	$(MAKE) full-down && $(MAKE) full-up

build: ## Собрать Docker образ
	@echo "$(GREEN)Сборка Docker образа...$(NC)"
	$(DOCKER_COMPOSE) build

build-no-cache: ## Без кэша
	@echo "$(GREEN)Сборка без кэша...$(NC)"
	$(DOCKER_COMPOSE) build --no-cache

rebuild: ## Пересобрать и запустить
	@echo "$(GREEN)Пересборка...$(NC)"
	$(DOCKER_COMPOSE) down --remove-orphans
	$(DOCKER_COMPOSE) build && $(DOCKER_COMPOSE) up -d

deploy: ## Пересобрать и запустить все
	@echo "$(GREEN)Деплой...$(NC)"
	$(DOCKER_COMPOSE) down --remove-orphans
	$(DOCKER_COMPOSE) build && $(DOCKER_COMPOSE) up -d
	@sleep 5
	@echo "$(GREEN)Деплой завершен!$(NC)"
	@echo "$(YELLOW)Frontend:   http://localhost:5173$(NC)"
	@echo "$(YELLOW)Django:      http://localhost:8000$(NC)"

frontend-build: ## Собрать Frontend
	@echo "$(GREEN)Сборка Frontend...$(NC)"
	cd frontend && node /home/redalexdad/.npm-global/node_modules/vite/bin/vite.js build

frontend-dev: ## Dev сервер
	@echo "$(GREEN)Запуск Frontend...$(NC)"
	cd frontend && node /home/redalexdad/.npm-global/node_modules/vite/bin/vite.js

frontend-rebuild: ## Пересобрать Frontend
	$(DOCKER_COMPOSE) build frontend
	$(DOCKER_COMPOSE) up -d --no-deps --force-recreate frontend

frontend-restart: ## Перезапустить Frontend
	$(DOCKER_COMPOSE) restart frontend

backend-rebuild: ## Пересобрать Django
	$(DOCKER_COMPOSE) build backend
	$(DOCKER_COMPOSE) up -d --no-deps --force-recreate backend

backend-restart: ## Перезапустить Django
	$(DOCKER_COMPOSE) restart backend

web-restart: ## backend + frontend
	$(DOCKER_COMPOSE) restart backend frontend

restart: web-restart
web-rebuild: backend-rebuild

logs: ## make logs service=backend|mlflow|minio|frontend
	$(DOCKER_COMPOSE) logs -f $(service)

frontend-logs:
	$(DOCKER_COMPOSE) logs -f frontend

backend-logs:
	$(DOCKER_COMPOSE) logs -f backend

web-logs:
	$(DOCKER_COMPOSE) logs -f backend frontend

mlflow-logs:
	$(DOCKER_COMPOSE) logs -f mlflow

minio-logs:
	$(DOCKER_COMPOSE) logs -f minio

clean: ## Очистить Docker ресурсы
	@echo "$(YELLOW)Очистка...$(NC)"
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f