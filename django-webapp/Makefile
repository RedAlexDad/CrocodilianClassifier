# Makefile для домашнего задания №1
# РНС | МГТУ им. Баумана
# С поддержкой скачивания изображений и загрузки в S3

# Переменные
PYTHON ?= python3
PIP ?= pip3
MANAGE := python web-site-dl/manage.py
DOCKER_COMPOSE := docker compose
DOCKER := docker

# Классы для скачивания (ваш вариант)
CLASSES ?= крокодил аллигатор кайман
IMAGES_PER_CLASS ?= 100
DATA_DIR := data

# S3 настройки
S3_BUCKET ?= dz1-media
S3_PREFIX ?= media/images

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help install run download-images download-class upload-to-s3 upload-class upload-all s3-list

# ==============================================================================
# Основная информация
# ==============================================================================

help: ## Показать справку по всем командам
	@echo ""
	@echo "Домашнее задание №1 - Makefile Справка"
	@echo ""
	@echo "Установка:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'install|venv' | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Скачивание изображений:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'download' | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Загрузка в S3:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E 'upload|s3-' | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Django и Docker:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^run|^docker|^minio' | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Тестирование:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^test|^lint|^format' | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Примеры использования:"
	@echo "  make download-all              # Скачать все классы (100 изображений каждый)"
	@echo "  make download-class CLASS=тигр # Скачать один класс"
	@echo "  make upload-all                # Загрузить всё в S3"
	@echo "  make docker-up                 # Запустить Docker с MinIO"
	@echo ""

# ==============================================================================
# Установка
# ==============================================================================

install: ##  Установить все зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Зависимости установлены!$(NC)"

install-dev: ##  Установить зависимости для разработки
	@echo "$(GREEN)Установка зависимостей для разработки...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install black flake8 pylint
	@echo "$(GREEN)Зависимости установлены!$(NC)"

venv: ##  Создать виртуальное окружение
	@echo "$(GREEN)Создание виртуального окружения...$(NC)"
	$(PYTHON) -m venv venv
	@echo "$(GREEN)Виртуальное окружение создано!$(NC)"
	@echo "$(YELLOW)Для активации:$(NC)"
	@echo "  source venv/bin/activate  # Linux/Mac"
	@echo "  venv\Scripts\activate     # Windows"

# ==============================================================================
# Скачивание изображений
# ==============================================================================

download-all: ##  Скачать все изображения по классам (CLASSES, IMAGES_PER_CLASS)
	@echo "$(GREEN) Скачивание изображений для всех классов...$(NC)"
	@echo "Классы: $(CLASSES)"
	@echo "Изображений на класс: $(IMAGES_PER_CLASS)"
	@mkdir -p $(DATA_DIR)
	@echo "$(YELLOW)Проверка зависимостей...$(NC)"
	@$(PYTHON) -m pip install requests --quiet --break-system-packages 2>/dev/null || true
	@for class in $(CLASSES); do \
		echo ""; \
		echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"; \
		echo "$(GREEN)Класс: $$class$(NC)"; \
		echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"; \
		mkdir -p $(DATA_DIR)/$$class; \
		$(PYTHON) download_simple.py "$$class" $(IMAGES_PER_CLASS) $(DATA_DIR)/$$class || \
		echo "$(RED) Ошибка при скачивании $$class$(NC)"; \
	done
	@echo ""
	@echo "$(GREEN)Скачивание завершено!$(NC)"
	@echo "$(YELLOW)Путь к данным: $(DATA_DIR)/$(NC)"
	@echo ""
	@echo "$(YELLOW)Следующий шаг: make upload-all$(NC)"

download-class: ##  Скачать один класс (CLASS=тигр, COUNT=100)
	@echo "$(GREEN) Скачивание изображений для класса: $(CLASS)$(NC)"
	@echo "$(YELLOW)Проверка зависимостей...$(NC)"
	@$(PYTHON) -m pip install requests --quiet --break-system-packages 2>/dev/null || true
	@mkdir -p $(DATA_DIR)/$(CLASS)
	$(PYTHON) download_simple.py "$(CLASS)" "$(COUNT)" "$(DATA_DIR)/$(CLASS)"
	@echo "$(GREEN)Скачивание завершено!$(NC)"

download-crocodile: ##  Скачать крокодилов
	@$(MAKE) download-class CLASS=крокодил COUNT=$(IMAGES_PER_CLASS)

download-alligator: ##  Скачать аллигаторов
	@$(MAKE) download-class CLASS=аллигатор COUNT=$(IMAGES_PER_CLASS)

download-caiman: ##  Скачать кайманов
	@$(MAKE) download-class CLASS=кайман COUNT=$(IMAGES_PER_CLASS)

download-placeholders: ##  Создать тестовые изображения-заглушки
	@echo "$(GREEN)Создание тестовых изображений-заглушек...$(NC)"
	@echo "$(YELLOW)Проверка зависимостей...$(NC)"
	@$(PYTHON) -m pip install pillow --quiet --break-system-packages 2>/dev/null || true
	$(PYTHON) create_placeholders.py
	@echo "$(GREEN)Готово!$(NC)"
	@echo "$(YELLOW) Это заглушки! Для обучения скачайте реальные изображения$(NC)"

extract-archive: ##  Распаковать архив и переименовать (ARCHIVE=файл.zip FOLDER=папка PREFIX=префикс)
	@echo "$(GREEN)Распаковка архива и переименование...$(NC)"
	@echo "$(YELLOW)Проверка зависимостей...$(NC)"
	@$(PYTHON) -m pip install rarfile --quiet --break-system-packages 2>/dev/null || true
	$(PYTHON) extract_and_rename.py "$(ARCHIVE)" "$(FOLDER)" "$(PREFIX)"

# ==============================================================================
# Загрузка в S3 / MinIO
# ==============================================================================

upload-all: ##  Загрузить все изображения и модели в S3
	@echo "$(GREEN)Загрузка всех данных в S3...$(NC)"
	@echo "Bucket: $(S3_BUCKET)"
	@echo ""
	@# Загрузка изображений по классам
	@for class in $(CLASSES); do \
		echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"; \
		echo "$(GREEN)Загрузка класса: $$class$(NC)"; \
		echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"; \
		if [ -d "$(DATA_DIR)/$$class" ]; then \
			$(PYTHON) s3_upload.py --dir "$(DATA_DIR)/$$class" "$(S3_PREFIX)/$$class/"; \
		else \
			echo "$(YELLOW) Папка $(DATA_DIR)/$$class не найдена$(NC)"; \
		fi; \
		echo ""; \
	done
	@# Загрузка моделей если есть
	@if [ -d "media/models" ] && [ "$$(ls -A media/models 2>/dev/null)" ]; then \
		echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"; \
		echo "$(GREEN)Загрузка моделей$(NC)"; \
		echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"; \
		$(PYTHON) s3_upload.py --dir "media/models" "media/models/"; \
	fi
	@echo ""
	@echo "$(GREEN)Загрузка в S3 завершена!$(NC)"
	@echo "$(YELLOW)Bucket: $(S3_BUCKET)$(NC)"
	@$(MAKE) s3-list

upload-class-s3: ##  Загрузить конкретный класс в S3 (CLASS=тигр)
	@echo "$(GREEN)Загрузка класса $(CLASS) в S3...$(NC)"
	$(PYTHON) s3_upload.py --dir "$(DATA_DIR)/$(CLASS)" "$(S3_PREFIX)/$(CLASS)/"
	@echo "$(GREEN)Завершено!$(NC)"

upload-model: ##  Загрузить модель в S3 (MODEL=model.onnx)
	@echo "$(GREEN)Загрузка модели $(MODEL) в S3...$(NC)"
	$(PYTHON) s3_upload.py "$(MODEL)" "media/models/$(MODEL)"
	@echo "$(GREEN)Завершено!$(NC)"

upload-models: ##  Загрузить все модели в S3
	@echo "$(GREEN)Загрузка всех моделей в S3...$(NC)"
	$(PYTHON) s3_upload.py --dir "media/models" "media/models/"
	@echo "$(GREEN)Завершено!$(NC)"

s3-list: ##  Показать список файлов в S3
	@echo "$(GREEN)Файлы в S3 ($(S3_BUCKET)):$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	$(PYTHON) s3_upload.py --list ""

s3-list-images: ##  Показать список изображений в S3
	@echo "$(GREEN)Изображения в S3:$(NC)"
	$(PYTHON) s3_upload.py --list "$(S3_PREFIX)/"

s3-list-models: ##  Показать список моделей в S3
	@echo "$(GREEN)Модели в S3:$(NC)"
	$(PYTHON) s3_upload.py --list "media/models/"

s3-download: ##  Скачать файл из S3 (KEY=путь, OUT=локальный_путь)
	@echo "$(GREEN)Скачивание из S3...$(NC)"
	$(PYTHON) s3_upload.py --download "$(KEY)" "$(OUT)"

s3-delete: ##  Удалить файл из S3 (KEY=путь)
	@echo "$(RED)Удаление из S3: $(KEY)$(NC)"
	$(PYTHON) s3_delete.py "$(KEY)"
	@echo "$(GREEN)Удалено!$(NC)"

s3-create-bucket: ##  Создать S3 бакет
	@echo "$(GREEN)Создание бакета $(S3_BUCKET)...$(NC)"
	$(PYTHON) s3_upload.py --list > /dev/null 2>&1
	@echo "$(GREEN)Бакет создан/проверен!$(NC)"

# ==============================================================================
# Полный пайплайн
# ==============================================================================

full-pipeline: ##  Полный пайплайн: скачать → загрузить в S3 → запустить
	@echo "$(BLUE)$(NC)"
	@echo "$(BLUE)          ЗАПУСК ПОЛНОГО ПАЙПЛАЙНА                      $(NC)"
	@echo "$(BLUE)$(NC)"
	@echo ""
	@echo "$(YELLOW)Шаг 1/4: Установка зависимостей...$(NC)"
	@$(MAKE) install
	@echo ""
	@echo "$(YELLOW)Шаг 2/4: Запуск MinIO...$(NC)"
	@$(MAKE) minio-up
	@sleep 5
	@echo ""
	@echo "$(YELLOW)Шаг 3/4: Скачивание изображений...$(NC)"
	@$(MAKE) download-all
	@echo ""
	@echo "$(YELLOW)Шаг 4/4: Загрузка в S3...$(NC)"
	@$(MAKE) upload-all
	@echo ""
	@echo "$(GREEN)$(NC)"
	@echo "$(GREEN)             ПАЙПЛАЙН ЗАВЕРШЁН!                          $(NC)"
	@echo "$(GREEN)$(NC)"
	@echo ""
	@echo "$(YELLOW)Приложение: http://localhost:8000$(NC)"
	@echo "$(YELLOW)MinIO API: http://localhost:9000$(NC)"
	@echo "$(YELLOW) MinIO Console: http://localhost:9001$(NC)"
	@echo ""

# ==============================================================================
# Django команды
# ==============================================================================

run: ##  Запустить Django сервер
	@echo "$(GREEN)Запуск Django сервера...$(NC)"
	$(MANAGE) runserver

run-0: ##  Запустить Django сервер на 0.0.0.0:8000
	@echo "$(GREEN)Запуск Django сервера на 0.0.0.0:8000...$(NC)"
	$(MANAGE) runserver 0.0.0.0:8000

migrate: ##  Применить миграции
	@echo "$(GREEN)Применение миграций...$(NC)"
	$(MANAGE) migrate
	@echo "$(GREEN)Миграции применены!$(NC)"

migrate-make: ##  Создать миграции
	@echo "$(GREEN)Создание миграций...$(NC)"
	$(MANAGE) makemigrations
	@echo "$(GREEN)Миграции созданы!$(NC)"

collectstatic: ##  Собрать статику
	@echo "$(GREEN)Сбор статических файлов...$(NC)"
	$(MANAGE) collectstatic --noinput
	@echo "$(GREEN)Статика собрана!$(NC)"

createsuperuser: ##  Создать суперпользователя
	@echo "$(GREEN)Создание суперпользователя...$(NC)"
	$(MANAGE) createsuperuser

shell: ##  Django shell
	$(MANAGE) shell

check: ##  Проверить проект
	@echo "$(GREEN)Проверка Django проекта...$(NC)"
	$(MANAGE) check

# ==============================================================================
# Docker команды
# ==============================================================================

docker-build: ##  Собрать Docker образ
	@echo "$(GREEN)Сборка Docker образа...$(NC)"
	$(DOCKER) build -t dz1-homework .
	@echo "$(GREEN)Образ собран!$(NC)"

docker-up: ##  Запустить Docker Compose
	@echo "$(GREEN)Запуск Docker Compose...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Контейнеры запущены!$(NC)"
	@echo "$(YELLOW)Django: http://localhost:8000$(NC)"
	@echo "$(YELLOW)MinIO API: http://localhost:9000$(NC)"
	@echo "$(YELLOW) MinIO Console: http://localhost:9001 (minioadmin/minioadmin)$(NC)"

docker-down: ##  Остановить Docker
	@echo "$(GREEN)Остановка Docker...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Остановлено!$(NC)"

docker-restart: ##  Перезапустить Docker
	@echo "$(GREEN)Перезапуск Docker...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)Перезапущено!$(NC)"

docker-rebuild: ##  Пересобрать и запустить Docker
	@echo "$(GREEN)Пересборка Docker...$(NC)"
	$(DOCKER_COMPOSE) up -d --build
	@echo "$(GREEN)Готово!$(NC)"

docker-logs: ##  Показать логи Docker
	@echo "$(GREEN)Логи Docker:$(NC)"
	$(DOCKER_COMPOSE) logs -f

docker-shell: ##  Войти в Docker контейнер
	@echo "$(GREEN)Вход в Docker контейнер...$(NC)"
	$(DOCKER_COMPOSE) exec web /bin/bash

docker-clean: ##  Очистить Docker ресурсы
	@echo "$(YELLOW)Очистка Docker ресурсов...$(NC)"
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f
	@echo "$(GREEN)Очистка завершена!$(NC)"

# ==============================================================================
# MinIO команды
# ==============================================================================

minio-up: ##  Запустить MinIO S3
	@echo "$(GREEN)Запуск MinIO S3...$(NC)"
	$(DOCKER_COMPOSE) up -d minio minio-init
	@sleep 3
	@echo "$(GREEN)MinIO запущен!$(NC)"
	@echo "$(YELLOW)API: http://localhost:9000$(NC)"
	@echo "$(YELLOW) Console: http://localhost:9001 (minioadmin/minioadmin)$(NC)"

minio-down: ##  Остановить MinIO
	@echo "$(GREEN)Остановка MinIO...$(NC)"
	$(DOCKER_COMPOSE) stop minio minio-init
	@echo "$(GREEN)MinIO остановлен!$(NC)"

minio-console: ##  Показать доступ к MinIO Console
	@echo ""
	@echo "$(BLUE)$(NC)"
	@echo "$(BLUE)             MinIO Console                               $(NC)"
	@echo "$(BLUE)$(NC)"
	@echo ""
	@echo "$(YELLOW)URL: http://localhost:9001$(NC)"
	@echo "$(YELLOW)Login: minioadmin$(NC)"
	@echo "$(YELLOW)Password: minioadmin$(NC)"
	@echo ""

# ==============================================================================
# Тестирование
# ==============================================================================

test: ##  Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	$(MANAGE) test

lint: ##  Проверка кода
	@echo "$(GREEN)Проверка кода...$(NC)"
	@command -v flake8 >/dev/null 2>&1 || { echo "Установите flake8"; exit 1; }
	flake8 dz1/ --count --select=E9,F63,F7,F82 --show-source --statistics

format: ##  Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	@command -v black >/dev/null 2>&1 || { echo "Установите black"; exit 1; }
	black dz1/

# ==============================================================================
# По умолчанию
# ==============================================================================

default: help
