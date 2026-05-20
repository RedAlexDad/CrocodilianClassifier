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

## Этап 2. Обучение YOLOv8-segment (не менее 4 запусков)

### 2.1 Создание окружения
- [x] Создать `data/yolo8_segment/` — папка с датасетом в формате YOLO
- [x] Скрипт конвертации `scripts/convert_to_yolo_seg.py` (bbox → polygon)
- [x] MLflow трекинг интегрирован (`training/utils/mlflow_utils.py`)
- [x] Скрипт обучения `scripts/train_yolo_seg.py`

### 2.2 Запуск 4+ тренировок с разными параметрами

| # | Модель | imgsz | epochs | batch | Optimizer | LR | Статус |
|---|--------|-------|--------|-------|-----------|----|--------|
| 1 | yolov8n-seg | 640 | 50 | 4 | AdamW(auto) | 0.00143 | ✅ Завершено |
| 2 | yolov8s-seg | 640 | 100 | 8 | SGD | 0.01 | ⏳ |
| 3 | yolov8n-seg | 640 | 50 | 8 | SGD | 0.01 | ⏳ |
| 4 | yolov8s-seg | 640 | 100 | 8 | Adam | 0.001 | ⏳ |

**Запуск 1 — результаты (best.pt):**

| Класс | Precision | Recall | mAP50 | mAP50-95 |
|-------|-----------|--------|-------|----------|
| alligator | 0.864 | 0.900 | 0.932 | 0.844 |
| cayman | 0.953 | 1.000 | 0.995 | 0.882 |
| crocodile | 0.841 | 0.666 | 0.810 | 0.711 |
| **all** | **0.886** | **0.855** | **0.912** | **0.831** |

**MLflow:** http://localhost:5000/#/experiments/2/runs/4811636994f74b53ae88e54e54106d45
**Модель:** `yolo8_segment/train/weights/best.pt`

- [ ] Запустить оставшиеся 3 тренировки (yolov8s, SGD, и т.д.)
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