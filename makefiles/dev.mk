.PHONY: run-django collectstatic migrate shell download dataset-stats
.PHONY: dataset-check-duplicates dataset-remove-duplicates install install-dev
.PHONY: test lint format

include makefiles/_vars.mk

run-django: ## Запустить Django локально
	@echo "$(GREEN)Запуск Django...$(NC)"
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py runserver

collectstatic: ## Собрать static файлы
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py collectstatic --noinput

migrate: ## Миграции БД
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py migrate

shell: ## Django shell
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py shell

download: ## Скачать изображения: make download CLASSES='крокодил аллигатор кайман'
	@echo "$(GREEN)Скачивание изображений...$(NC)"
	$(PYTHON) download_images.py --classes $(CLASSES) --limit $(IMAGES_PER_CLASS)

dataset-stats: ## Статистика датасета
	@echo "$(GREEN)Статистика датасета:$(NC)"
	@for class in $(CLASSES); do \
		count=$$(ls $(DATA_DIR)/$$class/*.jpeg 2>/dev/null | wc -l); \
		echo "  $$class: $$count изображений"; \
	done

dataset-check-duplicates: ## Проверить дубликаты (без удаления)
	$(PYTHON) scripts/remove_duplicates.py --data-dir $(DATA_DIR) --dry-run

dataset-remove-duplicates: ## Удалить дубликаты
	@echo "$(YELLOW)Удаление дубликатов...$(NC)"
	$(PYTHON) scripts/remove_duplicates.py --data-dir $(DATA_DIR)
	@echo "$(GREEN)✓ Дубликаты удалены$(NC)"

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r $(DJANGO_DIR)/requirements.txt
	$(PIP) install torch torchvision mlflow

install-dev: install
	$(PIP) install black flake8 mypy

test: ## Запустить тесты
	cd $(DJANGO_DIR)/web-site-dl && $(PYTHON) manage.py test

lint: ## Проверка кода
	@command -v flake8 >/dev/null 2>&1 && flake8 . --ignore=E501,W503 || echo "flake8 не установлен"

format: ## Форматировать код
	@command -v black >/dev/null 2>&1 && black . || echo "black не установлен"