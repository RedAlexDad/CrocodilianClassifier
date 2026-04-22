# Crocodilian Classifier

Классификация изображений крокодилов, аллигаторов и кайманов с помощью нейронных сетей.

## Возможности

- 🧠 Обучение моделей: CNN, MLP, ResNet20
- 📊 Интеграция с MLflow для отслеживания экспериментов
- 🗄️ Хранение артефактов в MinIO (S3-совместимое хранилище)
- 🌐 Web-интерфейс на React + Django
- 📸 Галерея загруженных изображений
- 📈 Метрики моделей (accuracy, precision, recall, F1)
- 🔄 Сортировка и группировка моделей
- 🚀 Hot reload для frontend разработки

## Быстрый старт

```bash
# Запустить все сервисы
make full-up

# Обучить модель
make train-cnn

# Открыть приложение
# Frontend: http://localhost:5173
# MLflow: http://localhost:5000
# MinIO Console: http://localhost:9001
```

## Структура проекта

```
├── frontend/          # React приложение (Vite + TypeScript)
├── backend/           # Django backend
├── training/          # Скрипты обучения моделей
├── data/             # Датасет изображений
├── docker-compose.yml # Конфигурация сервисов
└── Makefile          # Команды для управления проектом
```

## Основные команды

### Docker

```bash
make full-up          # Запустить все сервисы
make full-down        # Остановить все сервисы
make deploy           # Пересобрать и запустить
make backend-restart  # Перезапустить Django (быстро)
make frontend-restart # Перезапустить React (быстро)
make web-restart      # Перезапустить backend + frontend
```

### Обучение

```bash
make train-cnn        # Обучить CNN
make train-mlp        # Обучить MLP
make train-resnet20   # Обучить ResNet20
make train-all        # Обучить все модели
```

### MLflow

```bash
make mlflow-up        # Запустить MLflow
make list-mlflow-runs # Список запусков
```

### MinIO

```bash
make minio-up         # Запустить MinIO
make minio-console    # Открыть консоль
make minio-clear      # Очистить все бакеты
```

## Архитектура

### Frontend (React + TypeScript)

- **Vite** - сборщик с hot reload
- **React Router** - маршрутизация
- **Redux** - управление состоянием
- **Feature-Sliced Design** - архитектура

Страницы:

- `/` - Классификация изображений
- `/gallery` - Галерея загруженных изображений
- `/models` - Управление моделями

### Backend (Django)

- REST API для классификации
- Интеграция с MLflow
- Хранение в MinIO S3
- ONNX Runtime для инференса

### MLflow

- Отслеживание экспериментов
- Хранение метрик и параметров
- Версионирование моделей
- Артефакты в S3

### MinIO

- S3-совместимое хранилище
- Бакет `crocodilian`:
  - `media/models/` - ONNX модели
  - `media/images/` - загруженные изображения
  - `mlflow-artifacts/` - артефакты MLflow

## Датасет

Три класса:

- Крокодил (класс 0)
- Аллигатор (класс 1)
- Кайман (класс 2)

Требования к изображениям:

- Формат: JPG, PNG
- Автоматическое масштабирование до 32x32

## Разработка

### Frontend

```bash
cd frontend
npm install
npm run dev  # Запуск dev сервера
```

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

## Технологии

- **Frontend**: React, TypeScript, Vite, Redux, React Router
- **Backend**: Django, ONNX Runtime, boto3
- **ML**: PyTorch, MLflow, ONNX
- **Storage**: MinIO (S3)
- **Containerization**: Docker, Docker Compose

## Автор

МГТУ им. Баумана | РНС | 2026
