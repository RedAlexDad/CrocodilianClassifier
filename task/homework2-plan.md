# План выполнения ДЗ2 — Сегментация крокодиловых (YOLOv8-seg + CLIP)

**Ветка:** `homework2-segmentation`

---

## Этап 1. Разметка данных в CVAT ✅

### 1.1 Подготовка датасета для разметки ✅
- [x] Загрузить изображения (298 на 3 класса) в CVAT
- [x] Создать 1 проект с 3 лейблами: alligator, cayman, crocodile
- [x] Разметить bbox (прямоугольники)

### 1.2 Экспорт и подготовка датасета ✅
- [x] Распаковать `data/dataset/` (YOLO darknet format)
- [x] Датасет: 298 изображений, bbox-разметка, 3 класса
- [x] Ремэппинг: alligator→0, caiman→1, crocodile→2 (родной порядок)

**Статус датасета:**
```
data/dataset/obj_train_data/
  alligator: 74 images
  caiman:    136 images
  crocodile: 88 images
  Всего: 298 изображений, bbox-формат (class x_center y_center width height)
```

---

## Этап 2. Обучение YOLOv8-segment (6 запусков)

### 2.1 Создание окружения
- [x] Создать `data/yolo8_segment/` — папка с датасетом в формате YOLO
- [x] Скрипт конвертации `scripts/convert_to_yolo_seg.py` (bbox → polygon)
- [x] MLflow трекинг интегрирован (`training/utils/mlflow_utils.py`)
- [x] Скрипт обучения `scripts/train_yolo_seg.py`

### 2.2 Запуск 6 тренировок с разными параметрами

| # | Модель | epochs | batch | Optimizer | LR | Статус |
|---|--------|--------|-------|-----------|----|--------|
| 1 | yolov8n-seg | 20 | 8 | Adam | 0.001 | ✅ mAP50=0.803 |
| 2 | yolov8n-seg | 20 | 8 | SGD | 0.01 | ✅ mAP50=0.877 |
| 3 | yolov8n-seg | 20 | 8 | AdamW | 0.001 | ✅ mAP50=0.749 |
| 4 | yolov8n-seg | 50 | 16 | Adam | 0.001 | ⏳ |
| 5 | yolov8n-seg | 50 | 16 | SGD | 0.01 | ⏳ |
| 6 | yolov8n-seg | 50 | 16 | AdamW | 0.001 | ⏳ |

**Запуск 1 (Adam, 20 эпох, batch=8) — Результаты:**

| Класс | Precision | Recall | Box mAP50 | Box mAP50-95 | Mask mAP50 | Mask mAP50-95 |
|-------|-----------|--------|-----------|--------------|------------|---------------|
| alligator | 0.802 | 0.813 | 0.811 | 0.709 | 0.811 | 0.692 |
| cayman | 0.871 | 1.000 | 0.963 | 0.829 | 0.963 | 0.793 |
| crocodile | 0.656 | 0.500 | 0.634 | 0.544 | 0.634 | 0.531 |
| **all** | **0.777** | **0.771** | **0.803** | **0.694** | **0.803** | **0.672** |

**MLflow:** http://localhost:5000/#/experiments/2/runs/64b063dc25f341cb96cb4676ab78e7a4  
**Модель:** `yolo8_segment/yolov8n-seg-e20-bs8-adam/weights/best.pt`  
**Время обучения:** 0.060 часов (20 эпох, GTX 1650 Ti)

**Запуск 2 (SGD, 20 эпох, batch=8) — Результаты:**

| Класс | Precision | Recall | Box mAP50 | Box mAP50-95 | Mask mAP50 | Mask mAP50-95 |
|-------|-----------|--------|-----------|--------------|------------|---------------|
| alligator | 0.887 | 0.788 | 0.926 | 0.817 | 0.926 | 0.791 |
| cayman | 0.609 | 1.000 | 0.995 | 0.898 | 0.995 | 0.911 |
| crocodile | 0.458 | 0.625 | 0.708 | 0.595 | 0.708 | 0.607 |
| **all** | **0.651** | **0.804** | **0.877** | **0.770** | **0.877** | **0.770** |

**MLflow:** http://localhost:5000/#/experiments/2/runs/ba4d83e982294fb6959e0d4fffe0477e  
**Модель:** `yolo8_segment/yolov8n-seg-sgd-e20-bs8-sgd/weights/best.pt`  
**Время обучения:** 0.059 часов (20 эпох, GTX 1650 Ti)

**Запуск 3 (AdamW, 20 эпох, batch=8) — Результаты:**

| Класс | Precision | Recall | Box mAP50 | Box mAP50-95 | Mask mAP50 | Mask mAP50-95 |
|-------|-----------|--------|-----------|--------------|------------|---------------|
| alligator | 0.670 | 0.815 | 0.752 | 0.651 | 0.752 | 0.649 |
| cayman | 0.464 | 1.000 | 0.915 | 0.804 | 0.915 | 0.797 |
| crocodile | 0.295 | 0.625 | 0.579 | 0.505 | 0.579 | 0.502 |
| **all** | **0.476** | **0.813** | **0.749** | **0.653** | **0.749** | **0.649** |

**MLflow:** http://localhost:5000/#/experiments/2/runs/aff0bd6a12c84e668a02224ad8a0ae0f  
**Модель:** `yolo8_segment/yolov8n-seg-adamw-e20-bs8-adamw/weights/best.pt`  
**Время обучения:** 0.060 часов (20 эпох, GTX 1650 Ti)

**Сводка 20-эпохных запусков (mAP50):**
| Оптимизатор | Box mAP50 | Mask mAP50 |
|-------------|-----------|------------|
| SGD | **0.877** | **0.877** |
| Adam | 0.803 | 0.803 |
| AdamW | 0.749 | 0.749 |

- [ ] Запустить оставшиеся 3 тренировки (50 эпох: Adam, SGD, AdamW)
- [ ] Сравнить метрики: mAP@0.5, mAP@0.5:0.95, precision, recall
- [ ] Выбрать лучшую модель по mAP

### 2.3 Экспорт в ONNX
- [ ] Конвертировать лучшую YOLO-модель в ONNX: `model.export(format='onnx')`
- [ ] Проверить инференс ONNX-модели через `onnxruntime`
- [ ] Сохранить ONNX в `data/models/yolov8_seg.onnx`
- [ ] Загрузить ONNX в MinIO S3

---

## Этап 3. Интеграция YOLO-модели в backend

### 3.1 Backend: сервис инференса сегментации
- [ ] Создать `core/services/segmentation_service.py`
- [ ] Реализовать YOLO-постпроцессинг: decode boxes → NMS → decode masks
- [ ] Возвращать: класс, confidence, bbox, маска

### 3.2 Backend: API-эндпоинты
- [ ] `POST /api/segment` — загрузить изображение, вернуть сегментацию
- [ ] `POST /api/segment-existing` — сегментировать существующее изображение из галереи
- [ ] Зарегистрировать в `core/api/segmentation_views.py` и `core/urls.py`

### 3.3 Обновить модель данных
- [ ] Обновить `core/settings.py` для поддержки новой модели
- [ ] Убедиться, что `onnxruntime` установлен (уже есть)

---

## Этап 4. Обновление frontend (React SPA)

### 4.1 Новая страница сегментации
- [ ] Создать `frontend/src/widgets/Segmenter/SegmenterWidget.tsx`
- [ ] Загрузка изображения, отображение результата с наложением маски
- [ ] Canvas для отрисовки масок (разные цвета для классов)
- [ ] Подписи классов: красный → Крокодил, синий → Аллигатор, зеленый → Кайман

### 4.2 Обновить роутинг
- [ ] Добавить `/segment` маршрут в `App.tsx`
- [ ] Добавить навигационную ссылку в меню

### 4.3 Обновить существующие страницы
- [ ] Классификатор: добавить кнопку "Перейти к сегментации"
- [ ] Галерея: добавить кнопку "Сегментировать" для каждого изображения

---

## Этап 5. Дополнительное задание: CLIP-поиск карточек (бонус)

### 5.1 Создать набор карточек
- [ ] Собрать 10+ карточек на каждый класс (30+ всего)
- [ ] У каждой карточки: название и описание на английском
- [ ] Сохранить карточки в `frontend/src/assets/cards/`

### 5.2 Интегрировать CLIP/SigLIP на фронтенде
- [ ] Установить `@huggingface/transformers`
- [ ] Создать Web Worker `frontend/src/workers/search.worker.ts`
- [ ] Загружать SigLIP модель при старте (Singleton)
- [ ] При загрузке изображения:
  1. Вырезать сегментированные объекты по маске
  2. Подать в CLIP Vision Encoder
  3. Сравнить с текстовыми эмбеддингами через cosine similarity
  4. Отобразить top-K похожих карточек

### 5.3 UI для карточек
- [ ] Добавить секцию "Похожие карточки" под результатом сегментации
- [ ] Отображать сетку карточек с названием и процентом сходства

---

## Этап 6. Интеграционное тестирование и деплой

### 6.1 Проверка Docker
- [ ] Собрать и запустить через `make full-up`

### 6.2 Тестирование
- [ ] Загрузить изображение → проверить сегментацию
- [ ] Проверить overlay масок на canvas
- [ ] Проверить CLIP-поиск (бонус)
- [ ] Проверить галерею и классификацию (регрессия)

---

## Схема зависимостей

```
Этап 1 (CVAT разметка) ✅
    │
    ▼
Этап 2 (обучение YOLO x1/4 ✅, осталось 3 тренировки → экспорт ONNX)
    │
    ├──────────────────┐
    ▼                   ▼
Этап 3 (backend API)   Этап 5 (CLIP cards) ←─┐
    │                   │                     │
    ▼                   ▼                     │
Этап 4 (frontend SPA) ──┼─────────────────────┘
    │                   │
    ▼                   ▼
Этап 6 (тестирование в Docker)
```

## Технические заметки

- **CVAT workaround:** Traefik несовместим с Docker 29.x → заменён на nginx-proxy в `~/cvat/docker-compose.override.yml`
- **Формат меток:** bbox (class x_center y_center width height) — YOLOv8-seg обучается на bbox + masks
- **Конвертация:** `scripts/convert_to_yolo_seg.py` — bbox → polygon (8 точек), split 90/10 train/val
- **Датасет:** `data/yolo8_segment/` — 268 train / 30 val изображений
- **YOLO ONNX на backend:** Модель содержит 3 выхода (boxes, scores, masks). Потребуется постпроцессинг (NMS, decode masks) на Python с `onnxruntime`.
- **Цвета классов:** Крокодил → `#FF4444`, Аллигатор → `#4444FF`, Кайман → `#44FF44`
- **CLIP на фронтенде:** Работает в браузере через Web Worker (`@huggingface/transformers`), модель SigLIP base (~400MB) загружается один раз.
- **Совместимость:** Все изменения обратно совместимы с ДЗ1 (классификация продолжает работать).
- **Train/Val split:** `scripts/convert_to_yolo_seg.py` разбивает на train/val перед обучением
- **Torch версия:** Обновлено torch 2.6.0 + torchvision 0.21.0 (cu124) для совместимости с ultralytics

---

## Структура файлов

```
data/dataset/                          ← ✅ аннотация CVAT (bbox)
  obj.names                            ← классы (alligator, cayman, crocodile)
  obj.data                             ← конфиг для darknet
  obj_train_data/*.jpeg, *.txt        ← изображения + bbox-разметка

data/yolo8_segment/                   ← ✅ подготовленный YOLO-датасет
  dataset.yaml                         ← конфиг для YOLO
  images/train/*.jpeg                  ← 268 изображений
  images/val/*.jpeg                    ← 30 изображений
  labels/train/*.txt                  ← polygon-разметка
  labels/val/*.txt

yolo8_segment/train/                   ← результаты обучения
  weights/best.pt                      ← лучшая модель
  weights/last.pt
  results.png

scripts/
  convert_to_yolo_seg.py              ← ✅ конвертация bbox → polygon
  train_yolo_seg.py                   ← ✅ обучение с MLflow

backend/core/
  services/segmentation_service.py   ← создать
  api/segmentation_views.py           ← создать

frontend/src/
  widgets/Segmenter/                 ← создать
  workers/search.worker.ts          ← создать (CLIP)
  hooks/useFurnitureSearch.ts         ← создать (CLIP)
  modules/card_mock.ts, math.ts      ← создать (CLIP)
  assets/cards/                     ← создать (CLIP)
```