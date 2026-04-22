# CLAUDE_RU.md

Этот файл предоставляет руководство для Claude Code (claude.ai/code) при работе с кодом в этом репозитории.

## Обзор проекта

CrocodilianClassifier — это проект машинного обучения для классификации изображений крокодилов (крокодил, аллигатор, кайман) с использованием CNN. Проект включает:
- Пайплайн обучения с несколькими архитектурами моделей (MLP, CNN, ResNet20, MobileNetV2)
- Отслеживание экспериментов MLflow с хранением артефактов в S3
- Django REST бэкенд для инференса
- React + TypeScript фронтенд с hot reload
- Оркестрация Docker Compose с MinIO S3 и MLflow
- Галерея изображений для просмотра загруженных файлов
- Управление моделями с отображением метрик

## Основные команды

### Docker сервисы
```bash
# Запустить все сервисы (Frontend, Django, MLflow, MinIO)
make full-up

# Остановить все сервисы
make full-down

# Пересобрать и перезапустить всё
make deploy

# Быстрый перезапуск (без пересборки)
make backend-restart   # Перезапустить только Django
make frontend-restart  # Перезапустить только React
make web-restart       # Перезапустить backend + frontend

# Просмотр логов
make backend-logs
make frontend-logs
make web-logs          # Логи backend + frontend
make mlflow-logs
```

### Обучение моделей
```bash
# Обучить конкретную модель (запускать из корня проекта)
make train MODEL=cnn OPTIMIZER=sgd EPOCHS=50 DEVICE=cuda

# Быстрые команды
make train-cnn         # Обучить CNN с SGD
make train-mlp         # Обучить MLP
make train-resnet20    # Обучить ResNet20

# Обучить все модели
make train-all

# Обучить с кастомными параметрами
cd training && python3 main.py --model resnet20 --optimizer adam --epochs 50 --device cuda
```

### Управление MLflow
```bash
# Запустить MLflow сервер
make mlflow-up

# Список доступных запусков с метаданными
make list-mlflow-runs

# Добавить модель из MLflow в репозиторий
make add-mlflow-model RUN_ID=<run_id>
```

### Управление MinIO
```bash
# Запустить MinIO
make minio-up

# Открыть MinIO Console
make minio-console

# Очистить все бакеты (удаляет все данные)
make minio-clear
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

# Собрать фронтенд для production
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

### Фронтенд (`frontend/`)

**Стек технологий**: React + TypeScript + Vite + Redux + React Router

**Ключевые возможности**:
- Hot reload в dev режиме (не требует пересборки)
- Архитектура Feature-Sliced Design
- Три основные страницы:
  - `/` - Классификация изображений с загрузкой файлов
  - `/gallery` - Просмотр и классификация загруженных изображений
  - `/models` - Управление моделями (загрузка, удаление, загрузка из MLflow)

**Структура**:
```
frontend/src/
├── app/           # Конфигурация Redux store
├── widgets/       # Компоненты уровня страниц
│   ├── Classifier/          # Главная страница классификации
│   ├── Gallery/             # Страница галереи
│   └── ModelManagement/     # Страница управления моделями
├── entities/      # Бизнес-сущности
└── features/      # Компоненты функций
```

**Важные файлы**:
- `vite.config.ts` - Конфигурация прокси для Django бэкенда
- `App.tsx` - Основная маршрутизация и навигация
- `ClassifierWidget.tsx` - Загрузка и классификация изображений
- `GalleryWidget.tsx` - Галерея с классификацией по клику
- `ModelManagementWidget.tsx` - Загрузка/удаление/интеграция с MLflow

### Бэкенд (`backend/`)

**Стек технологий**: Django + ONNX Runtime + boto3 + MinIO

**Ключевые эндпоинты**:
- `POST /predictImage` - Классифицировать загруженное изображение
- `GET /api/models` - Список доступных моделей
- `GET /api/images` - Список загруженных изображений
- `POST /api/predict-existing` - Классифицировать существующее изображение из галереи
- `GET /api/mlflow-runs` - Список запусков MLflow с метриками
- `POST /api/mlflow-download` - Скачать модель из MLflow
- `POST /api/model-upload` - Загрузить ONNX модель
- `DELETE /api/model-delete` - Удалить модель

**Важные файлы**:
- `core/views.py` - Все API эндпоинты и логика инференса
- `core/urls.py` - Маршрутизация URL
- `core/settings.py` - Конфигурация Django с S3 хранилищем

**Структура хранилища**:
- MinIO бакет `crocodilian`:
  - `media/models/` - ONNX модели для инференса
  - `media/images/` - Загруженные изображения
  - `mlflow-artifacts/` - Артефакты экспериментов MLflow

### Пайплайн обучения (`training/`)

**Точка входа**: `training/main.py` - CLI для обучения моделей с настраиваемыми параметрами

**Ключевые компоненты**:
- `configs/config.py` - Конфигурации для каждой модели
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
- `utils/data.py` - Загрузка датасета и аугментация
- `utils/export.py` - Функциональность экспорта в ONNX
- `utils/mlflow_utils.py` - Интеграция логирования MLflow

**Процесс обучения**:
1. `main.py` парсит аргументы CLI и выбирает модель/оптимизатор
2. `options.py` предоставляет фабрику тренеров моделей
3. `train_model.py` оркестрирует обучение с отслеживанием MLflow
4. `utils/training.py` обрабатывает обучение/валидацию на уровне эпох
5. Модели сохраняются в `checkpoints/` и экспортируются в ONNX
6. Артефакты логируются в MLflow (метрики, графики, отчеты, ONNX модель)

**Модели с Transfer Learning** (ResNet20, MobileNetV2):
- Двухэтапное обучение: Этап 1 (только классификатор), Этап 2 (fine-tuning)
- Настраиваемое количество размораживаемых слоев
- Отдельные learning rates для каждого этапа

### Интеграция MLflow

**Tracking Server**: Работает на порту 5000 с SQLite бэкендом

**Логируемые артефакты**:
- ONNX модель (`onnx/*.onnx`)
- Графики обучения (кривые loss/accuracy)
- Матрицы ошибок (нормализованные и сырые)
- Отчет классификации (precision, recall, F1)
- Чекпоинт модели (.pth)

**Отслеживаемые метрики**:
- Обучение: loss, accuracy на эпоху
- Валидация: loss, accuracy на эпоху
- Тест: финальные accuracy, precision, recall, F1
- Система: CPU, память, использование GPU

**Хранилище**:
- Метаданные: SQLite база данных в Docker volume `mlflow_data`
- Артефакты: MinIO S3 бакет `crocodilian/mlflow-artifacts/`

### Docker сервисы

**Сервисы**:
1. **frontend** - React приложение с Vite (порт 5173)
   - Dev режим с hot reload
   - Проксирует API запросы к бэкенду
   - Volume смонтирован для live обновлений кода

2. **backend** - Django приложение (порт 8000)
   - ONNX Runtime для инференса
   - S3 хранилище через django-storages
   - Volume смонтирован для live обновлений кода

3. **mlflow** - MLflow tracking сервер (порт 5000)
   - SQLite бэкенд с persistent volume
   - S3 хранилище артефактов в MinIO

4. **minio** - S3-совместимое хранилище (порты 9000, 9001)
   - API: порт 9000
   - Console: порт 9001
   - Persistent volume для данных

5. **minio-init** - Одноразовая инициализация бакетов
   - Создает бакет `crocodilian`
   - Устанавливает публичный read доступ

**Volumes**:
- `minio_data` - Хранилище MinIO
- `mlflow_data` - База данных MLflow (персистентная история запусков)

## Рабочий процесс разработки

### Добавление новых функций

1. **Изменения фронтенда**: Редактируйте файлы в `frontend/src/`, изменения применяются автоматически (hot reload)
2. **Изменения бэкенда**: Редактируйте файлы в `backend/`, запустите `make backend-restart` для быстрой перезагрузки
3. **Изменения обучения**: Редактируйте файлы в `training/`, запускайте команды обучения напрямую

### Обучение новых моделей

```bash
# 1. Обучить модель с отслеживанием MLflow
make train-cnn

# 2. Проверить MLflow UI для метрик запуска
open http://localhost:5000

# 3. Загрузить модель из MLflow в web UI
# Перейти на http://localhost:5173/models → "Загрузить из MLflow"

# 4. Протестировать классификацию
# Перейти на http://localhost:5173/ и загрузить изображение
```

### Отладка

**Логи бэкенда**:
```bash
make backend-logs
```

**Логи фронтенда**:
```bash
make frontend-logs
```

**Проверить содержимое MinIO**:
```bash
# Открыть MinIO Console
make minio-console
# Логин: minioadmin / minioadmin
```

**Очистить все данные**:
```bash
make minio-clear  # Очищает все S3 бакеты
```

## Важные замечания

### CSRF защита
- API эндпоинты используют декоратор `@csrf_exempt` для доступа с фронтенда
- В production следует использовать правильные CSRF токены

### S3 хранилище
- Все медиа файлы хранятся в MinIO S3
- Публичный read доступ для изображений
- Модели хранятся в `media/models/`
- Изображения хранятся в `media/images/`

### Формат моделей
- Модели должны быть в формате ONNX (.onnx)
- Форма входа: [batch, channels, height, width] или [batch, height, width, channels]
- Автоматическое определение формата (NCHW vs NHWC)
- Предобработка изображений: resize до 32x32, нормализация в [0, 1]

### MLflow запуски
- Каждый запуск обучения создает уникальный run_id
- Артефакты хранятся в `mlflow-artifacts/{experiment_id}/{run_id}/artifacts/`
- Метрики парсятся из `classification_report.txt`
- В UI показываются только запуски с ONNX моделями

## Решение проблем

**Фронтенд не обновляется**: 
- Проверьте, работает ли dev режим: `docker compose logs frontend`
- Перезапустите: `make frontend-restart`

**Ошибка 502 на бэкенде**:
- Проверьте логи бэкенда: `make backend-logs`
- Перезапустите: `make backend-restart`

**Нет моделей в MLflow**:
- Сначала обучите модель: `make train-cnn`
- Проверьте MLflow UI: http://localhost:5000
- Проверьте S3 бакет: `make minio-console`

**Изображения не отображаются**:
- Проверьте, что MinIO запущен: `docker compose ps`
- Проверьте доступ к бакету: http://localhost:9001

**Сброс базы данных**:
```bash
# Остановить сервисы
make full-down

# Удалить volumes
docker volume rm crocodilianclassifier_mlflow_data
docker volume rm crocodilianclassifier_minio_data

# Перезапустить
make full-up
```

## URL-адреса

- Фронтенд: http://localhost:5173
- Backend API: http://localhost:8000
- MLflow UI: http://localhost:5000
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
