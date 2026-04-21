# Домашнее задание №1
## Классификация изображений: Крокодилы, Аллигаторы, Кайманы

---

##  Описание

Проект для выполнения домашнего задания №1 по курсу "Распознавание природных сигналов".

**Задача:** Создать веб-приложение для классификации изображений трёх классов:
-  Крокодил
-  Аллигатор
-  Кайман

---

##  Структура проекта

```
homework/
├── dz1/                      # Django проект
│   ├── __init__.py
│   ├── settings.py           # Настройки Django
│   ├── urls.py               # URL маршруты
│   ├── views.py              # Обработчики запросов
│   ├── wsgi.py
│   └── templates/
│       └── scorepage.html    # HTML шаблон
├── media/                    # Медиа файлы
│   ├── images/               # Загруженные изображения
│   └── models/               # ONNX модели
├── data/                     # Датасет (создаётся при скачивании)
│   ├── крокодил/
│   ├── аллигатор/
│   └── кайман/
├── colab_notebook.ipynb      # Ноутбук для Google Colab
├── download_images.py        # Скрипт для скачивания изображений
├── requirements.txt          # Зависимости
├── Dockerfile               # Docker образ
├── docker-compose.yml       # Docker Compose
└── README.md                # Этот файл
```

---

##  Быстрый старт

### Вариант 1: Локальный запуск с полным пайплайном

```bash
# 1. Перейдите в папку проекта
cd homework

# 2. Запустите полный пайплайн (скачать → загрузить в S3 → запустить)
make full-pipeline
```

**Что делает `make full-pipeline`:**
1. Устанавливает все зависимости
2. Запускает MinIO S3
3. Скачивает изображения по классам (крокодил, аллигатор, кайман)
4. Загружает данные в S3 хранилище
5. Запускает Django приложение

**Сервисы после запуска:**
-  Django: `http://localhost:8000`
-  MinIO API: `http://localhost:9000`
-  MinIO Console: `http://localhost:9001` (minioadmin/minioadmin)

---

### Вариант 2: Пошаговая установка

#### Шаг 1: Установка зависимостей
```bash
cd homework
make install
```

#### Шаг 2: Скачивание изображений
```bash
# Скачать все классы (по 100 изображений)
make download-all

# Скачать конкретный класс
make download-class CLASS=крокодил COUNT=100

# Скачать по отдельности
make download-crocodile
make download-alligator
make download-caiman
```

#### Шаг 3: Запуск MinIO S3
```bash
make minio-up
```

#### Шаг 4: Загрузка данных в S3
```bash
# Загрузить все изображения и модели в S3
make upload-all

# Загрузить конкретный класс
make upload-class-s3 CLASS=крокодил

# Загрузить модель
make upload-model MODEL=cifar100.onnx
```

#### Шаг 5: Запуск Django
```bash
make migrate
make run
```

---

### Вариант 3: Docker с MinIO S3

```bash
# 1. Перейдите в папку проекта
cd homework

# 2. Запустите через Docker Compose (включая MinIO)
make docker-up

# 3. Остановите
make docker-down
```

**Сервисы:**
-  Django: `http://localhost:8000`
-  MinIO API: `http://localhost:9000`
-  MinIO Console: `http://localhost:9001` (minioadmin/minioadmin)

---

### Вариант 4: Docker без S3 (локальное хранилище)

```bash
# Создайте .env файл
echo "USE_S3=0" > .env

# Запустите только веб-приложение
docker-compose up web --build
```

---

##  Часть 1: Обучение модели в Google Colab

###  Важно: Скачивание изображений

Автоматическое скачивание изображений заблокировано (Яндекс/Google блокируют ботов).

**Рекомендуемый способ: Скачать вручную**

См. подробную инструкцию: **[DATA_DOWNLOAD.md](DATA_DOWNLOAD.md)**

Кратко:
1. Установите расширение [Image downloader - Imageye](https://chrome.google.com/webstore/detail/image-downloader-imageye/agionbommeaifngbhincahgmoflcikhm)
2. Найдите изображения по классам: `крокодил`, `аллигатор`, `кайман`
3. Скачайте ≥100 изображений на каждый класс
4. Разложите по папкам: `data/крокодил/`, `data/аллигатор/`, `data/кайман/`

**Альтернатива: Тестовые заглушки**

Для демонстрации работы приложения создайте тестовые изображения:
```bash
make download-placeholders
```

### Шаг 1: Подготовка данных

**Способ A: Автоматически (скрипт)**
```bash
python download_images.py
```

**Способ B: Вручную через браузер**
1. Установите расширение Chrome: [Image downloader - Imageye](https://chrome.google.com/webstore/detail/image-downloader-imageye/agionbommeaifngbhincahgmoflcikhm)
2. Найдите изображения в поисковике
3. Скачайте через расширение в 3 папки: `крокодил`, `аллигатор`, `кайман`

**Способ C: Через yandex-images-download**
```bash
pip install yandex-images-download
yandex-images-download Chrome --keywords "крокодил, аллигатор, кайман" --limit 100
```

### Шаг 2: Загрузка в Google Colab

1. Откройте [проект в Colab](https://colab.research.google.com/)
2. Загрузите `colab_notebook.ipynb`
3. В файловой системе создайте папки в `/content/`:
   - `/content/крокодил/`
   - `/content/аллигатор/`
   - `/content/кайман/`
4. Загрузите изображения в соответствующие папки

### Шаг 3: Обучение модели

1. Запустите все ячейки ноутбука
2. Модель использует:
   -  **Transfer Learning** (ResNet18)
   -  **Аугментацию** (flip, rotation, color jitter)
   -  **Регуляризацию** (Dropout, L2 weight decay)
3. Дождитесь завершения обучения (50 эпох)

### Шаг 4: Скачивание модели

После обучения модель автоматически скачается:
- `cifar100.onnx` - для веб-приложения
- `model_weights.pth` - веса PyTorch

---

##  Часть 2: Веб-приложение

### Шаг 1: Подготовка модели

1. Скопируйте `cifar100.onnx` в папку `media/models/`
   ```bash
   cp /path/to/cifar100.onnx media/models/
   ```

### Шаг 2: Запуск приложения

```bash
python manage.py runserver
```

### Шаг 3: Использование

1. Откройте `http://127.0.0.1:8000/`
2. Загрузите изображение
3. Нажмите "Классифицировать"
4. Получите результат

---

##  Конфигурация

### Изменение классов

В файле `dz1/views.py`:
```python
imageClassList = {
    '0': 'Крокодил',
    '1': 'Аллигатор',
    '2': 'Кайман'
}
```

### Изменение пути к модели

В файле `dz1/views.py`:
```python
modelPath = 'media/models/ваша_модель.onnx'
```

---

##  Контрольные вопросы

### 1. Структура набора данных, аугментация данных

**Структура:**
- 3 класса (крокодил, аллигатор, кайман)
- ≥100 изображений на класс
- Разделение: 80% train, 20% test

**Аугментация:**
- RandomHorizontalFlip (p=0.5)
- RandomRotation (15°)
- ColorJitter (brightness, contrast, saturation)

### 2. Перенос обучения, дообучение

**Transfer Learning:**
- Используется предобученная ResNet18 (ImageNet)
- Заморожены ранние слои
- Дообучаются последние слои
- Заменён финальный FC слой на 3 класса

**Регуляризация:**
- Dropout (0.3, 0.2)
- L2 регуляризация (weight_decay=1e-4)
- Learning Rate Scheduler

### 3. Архитектура сверточной нейронной сети

```
ResNet18 Backbone:
├── Conv2d(3, 64, 7x7, stride=2)
├── BatchNorm2d
├── ReLU
├── MaxPool2d(3x3, stride=2)
├── Residual Blocks (x8)
└── AdaptiveAvgPool2d(1x1)

Classifier Head:
├── Dropout(0.3)
├── Linear(512, 256)
├── ReLU
├── Dropout(0.2)
└── Linear(256, 3)
```

---

##  Технологии

- **Backend:** Django 4.2+
- **ML:** PyTorch 2.0+, ONNX, ONNX Runtime
- **Data:** Pillow, NumPy, Pandas
- **Storage:** MinIO S3, boto3, django-storages
- **Deployment:** Docker, Docker Compose

---

##  MinIO S3 хранилище

Проект включает поддержку **MinIO** — S3-совместимого объектного хранилища.

### Запуск MinIO

```bash
# Запустить MinIO
make minio-up

# Остановить MinIO
make minio-down

# Открыть консоль
make minio-console
```

### Загрузка файлов в S3

```bash
# Загрузить файл
python s3_upload.py model.onnx

# Загрузить модель
make s3-upload-model

# Загрузить директорию с изображениями
python s3_upload.py --dir data/крокодил media/images/крокодил/

# Список файлов
python s3_upload.py --list media/models/

# Скачать файл
python s3_upload.py --download media/models/model.onnx ./model.onnx
```

### Переменные окружения для S3

```bash
# Включить S3
USE_S3=1

# Настройки подключения
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_STORAGE_BUCKET_NAME=dz1-media
AWS_S3_ENDPOINT_URL=http://localhost:9000
AWS_S3_REGION_NAME=us-east-1
AWS_QUERYSTRING_AUTH=0
```

---

##  Отчёт

Отчёт должен содержать:
1. Титульный лист
2. Задание с вариантом
3. Скриншоты:
   - Процесс скачивания изображений
   - Обучение в Colab (графики loss/accuracy)
   - Работа веб-приложения
4. Результаты classification_report
5. Выводы

---

##  Полезные ссылки

- [Google Colab](https://colab.research.google.com/)
- [Django Documentation](https://docs.djangoproject.com/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [ONNX Documentation](https://onnx.ai/onnx/)

---

## ‍ Автор

Студент МГТУ им. Баумана, ИУ5-21М
Папин
