FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование Django проекта
COPY . ./

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV USE_S3=1

# Порт Django
EXPOSE 8000

# Запуск миграций и сервера
WORKDIR /app/core
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]