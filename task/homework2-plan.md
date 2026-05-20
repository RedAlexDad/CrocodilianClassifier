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

## Этап 2. Обучение YOLOv8-segment (6 запусков) ✅

### 2.1 Создание окружения ✅
- [x] `data/yolo8_segment/` — датасет в формате YOLO
- [x] `scripts/convert_to_yolo_seg.py` — bbox → polygon
- [x] MLflow трекинг интегрирован
- [x] `scripts/train_yolo_seg.py` — скрипт обучения

### 2.2 Запуск 6 тренировок ✅

| # | Модель | epochs | batch | Оптимизатор | LR | Box mAP50 |
|---|--------|--------|-------|-------------|----|-----------|
| 1 | yolov8n-seg | 20 | 8 | Adam | 0.001 | 0.803 |
| 2 | yolov8n-seg | 20 | 8 | SGD | 0.01 | 0.877 |
| 3 | yolov8n-seg | 20 | 8 | AdamW | 0.001 | 0.749 |
| 4 | yolov8n-seg | 50 | 8 | Adam | 0.0005 | **0.900** |
| 5 | yolov8n-seg | 50 | 8 | SGD | 0.0005 | 0.685 |
| 6 | yolov8n-seg | 50 | 8 | AdamW | 0.0005 | **0.905** 🏆 |

- [x] Запустить Run #6 (AdamW, 50ep) — mAP50=0.905
- [x] Сравнить метрики: все 6 запусков в таблице
- [x] Выбрать лучшую: **AdamW 50ep (0.905)** — установлена как основная

### 2.3 Экспорт в ONNX ✅
- [x] Конвертировать `best.pt` → `yolov8_seg.onnx` (12.6 MB)
- [x] Проверить инференс: выходы `output0 [1,39,8400]` + `output1 [1,32,160,160]`
- [x] Сохранить в `data/models/yolov8_seg.onnx`
- [x] Загрузить в MinIO S3 через `POST /api/model-upload`

---

## Этап 3. Интеграция YOLO-модели в backend ✅

### 3.1 Backend: сервис инференса сегментации ✅
- [x] `core/services/segmentation_service.py`
- [x] YOLO-постпроцессинг: letterbox → decode boxes → NMS (IoU 0.45, conf 0.25) → маски (prototypes × coeffs → sigmoid → RLE)
- [x] Возврат: class_name, confidence, bbox (xyxy), mask (RLE)

### 3.2 Backend: API-эндпоинты ✅
- [x] `POST /api/segment` — загрузить + сегментировать
- [x] `POST /api/segment-existing` — сегментировать из галереи
- [x] `core/api/segmentation_views.py` + `core/urls.py`

### 3.3 Настройки ✅
- [x] ONNXRuntime установлен
- [x] Модель загружается сначала локально, fallback на S3

---

## Этап 4. Обновление frontend (React SPA) ✅

### 4.1 Новая страница сегментации ✅
- [x] `SegmenterWidget.tsx` — загрузка + masked canvas
- [x] Canvas с полупрозрачными масками (RGB per class)
- [x] Цвета: красный (аллигатор), зелёный (кайман), синий (крокодил)
- [x] Вывод: class + confidence, toggle show/hide масок

### 4.2 Роутинг ✅
- [x] `/segment` маршрут в `App.tsx`
- [x] Навигационная ссылка в меню

### 4.3 Shared utils ✅
- [x] `features/segmentation/segmentationSlice.ts` — Redux state
- [x] `features/segmentation/segmentUtils.ts` — `decodeRle`, `drawMasksOnCanvas`, `CLASS_COLORS`

### 4.4 Галерея ✅
- [x] Кнопка "Сегментировать" после классификации изображения
- [x] Canvas overlay с масками на выбранном изображении
- [x] Список обнаруженных объектов
- [x] Проверено: классификация + сегментация в галерее

---

## Этап 5. Дополнительное задание: CLIP-поиск карточек (бонус) ✅

### 5.1 Набор карточек ✅
- [x] 36 карточек (12 на класс) с названиями и описаниями на русском
- [x] `frontend/src/features/cards/cardsData.ts` — Card[] с id, classId, title, description

### 5.2 Backend: CLIP сервис ✅
- [x] `openai/clip-vit-base-patch32` через `transformers` (Python, на backend)
- [x] `core/services/clip_service.py` — кэширование модели + текстовых эмбеддингов
- [x] `encode_image()` → 512d вектор, `encode_texts()` → матрица N×512
- [x] Cosine similarity между image embedding и всеми text embeddings → top-K
- [x] `POST /api/card-search` — принимает обрезанный объект (base64), возвращает карточки

### 5.3 Frontend: crop + поиск ✅
- [x] `features/segmentation/cropUtils.ts` — `cropDetection()` вырезает объект по маске (RLE decode → alpha channel)
- [x] `hooks/useCardSearch.ts` — хук для вызова `/api/card-search`
- [x] Кнопка "Найти карточки" в результатах сегментации (SegmenterWidget + GalleryWidget)
- [x] Секция "Похожие карточки" с сеткой карточек (номер, название, описание, % сходства)
- [x] Проверено: сегментация → обрезка по маске → CLIP → 5 похожих карточек

---

## Этап 6. Интеграционное тестирование и деплой ✅

### 6.1 Проверка развёртывания ✅
- [x] `make full-up` — все сервисы запускаются
- [x] Backend отвечает на `/api/segment`, `/api/segment-existing`, `/api/card-search`

### 6.2 Тестирование функциональности ✅
- [x] Загрузить изображение → классификация → сегментация
- [x] Overlay масок на canvas (разные цвета)
- [x] Галерея: просмотр → классификация → сегментация
- [x] CLIP-поиск: сегментация → обрезка → API → карточки
- [x] Навигация между страницами (регрессия)

---

## Схема зависимостей

```
Этап 1 (CVAT разметка) ✅
    │
    ▼
Этап 2 (обучение YOLO 6/6 ✅ → ONNX экспорт ✅)
    │
    ├──────────────────────┐
    ▼                       ▼
Этап 3 (backend API ✅)   Этап 5 (CLIP cards ✅)
    │                       │
    ▼                       ▼
Этап 4 (frontend SPA ✅) ──┘
    │
    ▼
Этап 6 (тестирование ✅)
```

## Технические заметки

- **CVAT workaround:** Traefik несовместим с Docker 29.x → заменён на nginx-proxy в `~/cvat/docker-compose.override.yml`
- **Формат меток:** bbox (class x_center y_center width height) → YOLOv8-seg
- **Конвертация:** `scripts/convert_to_yolo_seg.py` — bbox → polygon (8 точек), split 90/10 train/val
- **Датасет:** `data/yolo8_segment/` — 268 train / 30 val
- **ONNX:** input `[1,3,640,640]`, outputs `output0 [1,39,8400]` + `output1 [1,32,160,160]`
- **Постпроцессинг:** sigmoid → NMS 0.45 → masks (prototypes × coeffs → resize → RLE)
- **Цвета классов (frontend):** красный → аллигатор, зелёный → кайман, синий → крокодил
- **Лучшая модель:** AdamW 50ep (mAP50=0.905), крокодил стабильно слабее (0.816)
- **Torch версия:** 2.6.0 + torchvision 0.21.0 (cu124)
- **CLIP модель:** `openai/clip-vit-base-patch32` (512d эмбеддинги), работает на backend через `transformers`
- **CLIP поиск:** изображение обрезается по маске (RLE → alpha channel) → base64 → POST /api/card-search → cosine similarity с текстовыми эмбеддингами 36 карточек → top-5
- **Карточки:** 36 шт (12 на класс), статический файл `frontend/src/features/cards/cardsData.ts`

---

## Структура файлов (текущая)

```
data/dataset/                          ← CVAT аннотация (bbox)
data/yolo8_segment/                   ← YOLO-датасет (polygon)
data/models/yolov8_seg.onnx           ← ONNX экспорт лучшей модели

TRAINING_RESULTS.md                   ← Анализ результатов обучения

yolo8_segment/
  yolov8n-seg-e20-bs8-adam/
  yolov8n-seg-sgd-e20-bs8-sgd/
  yolov8n-seg-adamw-e20-bs8-adamw/
  yolov8n-seg-long-e50-bs8-adam/      ← Run #4
  yolov8n-seg-long-sgd-e50-bs8-sgd/   ← Run #5
  yolov8n-seg-long-adamw-e50-bs8-adamw/ ← Run #6 🏆

scripts/
  convert_to_yolo_seg.py              ← конвертация bbox → polygon
  train_yolo_seg.py                   ← обучение с MLflow

backend/core/
  services/segmentation_service.py    ← YOLO inference + postprocessing
  services/clip_service.py            ← CLIP модель + токенизация + encode
  api/segmentation_views.py           ← /api/segment, /api/segment-existing
  api/card_views.py                   ← /api/card-search
  urls.py                             ← все маршруты

frontend/src/
  features/cards/
    cardsData.ts                      ← 36 карточек (12 на класс)
  features/segmentation/
    segmentationSlice.ts              ← Redux state
    segmentUtils.ts                   ← decodeRle, drawMasksOnCanvas, CLASS_COLORS
    cropUtils.ts                      ← cropDetection по маске, canvasToDataUrl
  hooks/
    useCardSearch.ts                  ← хук для поиска карточек
  widgets/Segmenter/
    SegmenterWidget.tsx               ← страница сегментации + карточки
    SegmenterWidget.css               ← стили для карточек
  widgets/Gallery/
    GalleryWidget.tsx                 ← сегментация + карточки в галерее
    GalleryWidget.css                 ← стили
```
