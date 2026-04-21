# CLAUDE_RU.md

Этот файл предоставляет руководство для Claude Code (claude.ai/code) при работе с кодом в этом репозитории.

## Обзор проекта

CrocodilianClassifier — это проект машинного обучения для классификации изображений крокодилов (крокодил, аллигатор, кайман) с использованием CNN. Проект включает:
- Пайплайн обучения с несколькими архитектурами моделей (MLP, CNN, ResNet20, MobileNetV2)
- Отслеживание экспериментов MLflow с хранением артефактов в S3
- Django REST бэкенд для инференса
- React + TypeScript фронтенд
- Оркестрация Docker Compose с MinIO S3 и MLflow

## Основные команды

### Обучение моделей
```bash
# Обучить конкретную модель (запускать из корня проекта)
make train MODEL=cnn OPTIMIZER=sgd EPOCHS=50 DEVICE=cuda

# Обучить все модели
make train-all

# Обучить с конкретными параметрами
cd training && python3 main.py --model resnet20 --optimizer adam --epochs 50 --device cuda

# Сравнить оптимизаторы для модели
cd training && python3 main.py --model cnn --compare-optimizers
```

### Docker сервисы
```bash
# Запустить все сервисы (Frontend, Django, MLflow, MinIO)
make full-up

# Остановить все сервисы
make full-down

# Пересобрать и перезапустить
make deploy

# Просмотр логов
make logs service=web
make mlflow-logs
make frontend-logs
```

### Управление MLflow
```bash
# Запустить MLflow сервер
make mlflow-up

# Список доступных запусков
make list-mlflow-runs

# Добавить модель из MLflow в репозиторий
make add-mlflow-model RUN_ID=<run_id>
```

### Django бэкенд
```bash
# Запустить Django локально (без Docker)
make run-django

# Выполнить миграции
make migrate

# Собрать статические файлы
make collectstatic
```

### Разработка фронтенда
```bash
# Запустить dev сервер фронтенда (без Docker)
make frontend-dev

# Собрать фронтенд
make frontend-build
```

### Управление датасетом
```bash
# Скачать изображения для всех классов
make download CLASSES='крокодил аллигатор кайман' IMAGES_PER_CLASS=100

# Показать статистику датасета
make dataset-stats
```

## Архитектура

### Пайплайн обучения (`training/`)

**Точка входа**: `training/main.py` - CLI для обучения моделей с настраиваемыми параметрами

**Ключевые компоненты**:
- `configs/config.py` - Конфигурации для каждой модели (MLPConfig, CNNConfig, ResNetConfig, MobileNetConfig)
- `models/` - Архитектуры моделей (mlp.py, cnn.py, resnet20.py, mobilenet.py)
- `scripts/train_model.py` - Функции обучения и фабрика оптимизаторов
- `utils/training.py` - Основной цикл обучения (train_epoch, validate, класс Trainer)
- `utils/data.py` - Загрузка датасета и аугментация
- `utils/export.py` - Функциональность экспорта в ONNX
- `utils/mlflow_utils.py` - Интеграция логирования MLflow

**Поток обучения**:
1. `main.py` парсит аргументы CLI и выбирает модель/оптимизатор
2. `options.py` предоставляет фабрику тренеров моделей
3. `train_model.py` организует обучение с отслеживанием MLflow
4. `utils/training.py` обрабатывает обучение/валидацию на уровне эпох
5. Модели сохраняются в `checkpoints/` и экспортируются в ONNX в `data/models/`

**Модели с Transfer Learning** (ResNet20, MobileNetV2):
- Двухэтапное обучение: Этап 1 (только классификатор), Этап 2 (fine-tuning)
- Настраиваемое количество размораживаемых слоёв
- Отдельные learning rate для каждого этапа

### Бэкенд (`backend/`)

**Django приложение** с ONNX инференсом:
- `core/views.py` - Основное представление для загрузки изображений и классификации
- `core/storage_backends.py` - S3 storage бэкенд для MinIO
- `core/settings.py` - Настройки Django с конфигурацией S3
- Использует `onnxruntime` для инференса модели
- Поддерживает загрузку моделей из MLflow S3 бакета

**Ключевые возможности**:
- Предобработка изображений (resize до 224x224, нормализация с ImageNet статистикой)
- ONNX инференс модели
- Интеграция S3 для хранения моделей и медиа
- Интеграция MLflow для версионирования моделей

### Фронтенд (`frontend/`)

**React + TypeScript + Vite** приложение:
- Архитектура Feature-Sliced Design (app/, entities/, features/, widgets/)
- Redux Toolkit для управления состоянием
- React Query для API вызовов
- Axios для HTTP запросов
- Взаимодействует с Django backend API

### Инфраструктура

**Docker Compose сервисы**:
- `frontend` - React dev сервер (порт 5173)
- `web` - Django приложение (порт 8000)
- `mlflow` - MLflow tracking сервер (порт 5000)
- `minio` - S3-совместимое хранилище (порты 9000, 9001)
- `minio-init` - Инициализирует S3 бакеты при запуске

**S3 бакеты**:
- `crocodilian` - Django медиа файлы (загруженные изображения, модели)
- `crocodilian-artifacts` - MLflow артефакты (модели, метрики, графики)

## Процесс обучения модели

1. **Подготовка данных**: Изображения организованы в `data/крокодил/`, `data/аллигатор/`, `data/кайман/`
2. **Обучение модели**: Используйте `make train MODEL=<model>` или `cd training && python3 main.py`
3. **Отслеживание экспериментов**: MLflow автоматически логирует метрики, параметры, артефакты
4. **Экспорт в ONNX**: Модели автоматически экспортируются после обучения
5. **Деплой**: Скопируйте ONNX модель в бэкенд или используйте MLflow model registry

## Интеграция MLflow

- Tracking URI: `http://localhost:5000`
- Артефакты хранятся в MinIO S3 (бакет `crocodilian-artifacts`)
- Логируемые артефакты: чекпоинты моделей, ONNX модели, матрицы ошибок, примеры предсказаний
- Используйте `make list-mlflow-runs` для просмотра доступных запусков
- Используйте `make add-mlflow-model RUN_ID=<id>` для добавления модели в репозиторий

## Важные заметки

- **Скрипты обучения должны запускаться из корня проекта** или директории `training/`
- **Выбор устройства**: Используйте `DEVICE=cuda` или `DEVICE=cpu` в make командах
- **Конфигурации моделей**: Каждая модель имеет специфичные оптимизаторы по умолчанию и гиперпараметры в `training/configs/config.py`
- **Обработка меток**: Утилиты обучения поддерживают как one-hot, так и скалярные метки
- **Предобработка изображений**: Обучение использует 32x32 для MLP/CNN, 224x224 для ResNet/MobileNet
- **S3 учетные данные**: Учетные данные MinIO по умолчанию `minioadmin/minioadmin`

## Процесс разработки

1. Запустить инфраструктуру: `make full-up`
2. Обучить модели: `make train MODEL=cnn` или использовать training CLI
3. Просмотреть эксперименты: Открыть MLflow UI на `http://localhost:5000`
4. Протестировать инференс: Загрузить изображения через фронтенд на `http://localhost:5173`
5. Просмотреть логи: `make logs service=<service_name>`

## Расположение файлов

- Чекпоинты обученных моделей: `checkpoints/*.pth`
- ONNX экспорты: `data/models/*.onnx`
- MLflow запуски: `mlruns/` (локально) или MinIO S3 (Docker)
- Датасет: `data/<class_name>/*.jpeg`
- Django медиа: `backend/media/` (локально) или MinIO S3 (Docker)
