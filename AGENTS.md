# AGENTS.md

## Структура проекта

```
CrocodilianClassifier/
├── data/               # Датасет: крокодил/, аллигатор/, кайман/
├── checkpoints/        # .pth чекпоинты моделей
├── data/models/        # .onnx модели
├── training/           # Модули обучения: MLP, CNN, MobileNetV2
│   ├── configs/        # Конфигурации (config.py)
│   ├── models/        # Архитектуры моделей (mlp.py, cnn.py, mobilenet.py)
│   ├── scripts/      # Скрипты обучения
│   └── utils/        # Утилиты: data.py, training.py, export.py, utils.py
├── django-webapp/      # Django web-приложение
├── task/              # Инструкции к домашнему заданию
└── report/            # Отчеты (PDF, DOCX)
```

## Классы датасета

- `крокодил` - крокодилы
- `аллигатор` - аллигаторы  
- `кайман` - кайманы

Требование: не менее 100 изображений на класс.

## Ключевые команды

```bash
# Обучение моделей
python training/main.py --model mlp           # MLP модель
python training/main.py --model cnn           # CNN модель
python training/main.py --model mobilenet     # MobileNetV2 (transfer learning)
python training/main.py --model all         # Все модели

# С оптимизатором
python training/main.py --model cnn --optimizer sgd
python training/main.py --model mobilenet --optimizer adam

# Запуск Django
cd django-webapp && python manage.py runserver
```

## Конфигурации моделей

### MLP
- INPUT_SIZE: 32x32x3 = 3072
- Скрытые слои: [512, 256, 128]
- Dropout: 0.3
- Оптимизаторы: adam, adagrad, rmsprop
- Эпохи: 100

### CNN (своя)
- IMAGE_SIZE: 32
- HIDDEN_SIZE: 32
- Dropout: 0.3
- Эпохи: 500
- LR: 0.005
- Аугментация: включена
- Оптимизаторы: sgd, adam, rmsprop

### MobileNetV2 (transfer learning)
- IMAGE_SIZE: 224 (ImageNet стандарт)
- Предобученная: True
- Этап 1: только классификатор (50 эпох, LR=0.001)
- Этап 2: fine-tuning (30 эпох, LR=0.0001)
- Размораживаемых слоёв: 20

## Правила коммитов

Только на русском языке, формат:
- `type: описание` (type: chore, docs, feat, fix, refactor, style, test)
- до 50 символов, повелительное наклонение, без точки

## Важные ограничения

- Модели (.pth, .onnx) в gitignored, не отслеживаются
- Изображения датасета отслеживаются (в data/)
- Для рефакторинга кода использовать тип refactor
- Jupyter notebooks в .gitignored

## Зависимости

См. `django-webapp/requirements.txt`:
- Django>=4.2
- Pillow>=10.0.0
- onnx, onnxruntime
- torch, torchvision
- numpy, pandas
- scikit-learn
- boto3 (S3)

## Домашнее задание

см. `task/homework1.md`

Требования:
1. Датасет 3 класса, 100+ изображений на класс
2. Аугментация данных
3. Регуляризация (dropout, weight decay)
4. Перенос обучения (transfer learning)
5. Экспорт в ONNX
6. Django web-приложение для классификации