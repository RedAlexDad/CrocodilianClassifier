# Структурированный проект обучения моделей

## Структура проекта

```
training/
├── main.py              # Главный скрипт с CLI
├── configs/
│   ├── __init__.py
│   └── config.py        # Конфигурации для каждой модели
├── models/
│   ├── __init__.py
│   ├── mlp.py           # MLP модель
│   ├── cnn.py           # CNN модель (самописная)
│   └── mobilenet.py     # MobileNetV2 (transfer learning)
├── scripts/
│   ├── __init__.py
│   └── train_scripts.py # Скрипты обучения + фабрика оптимизаторов
├── utils/
│   ├── __init__.py
│   ├── data.py          # Загрузка данных и dataloader
│   ├── training.py      # Функции обучения (Trainer класс)
│   ├── export.py        # Экспорт в ONNX
│   └── utils.py         # Вспомогательные функции (device, seed)
└── data/                # Данные (крокодил, аллигатор, кайман)
```

## Использование

**Важно:** Запускайте скрипт из папки `homework/`:

```bash
cd ~/GitHub/BMSTU/2\ семестр/РНС/homework
```

### Обучение всех моделей (оптимизаторы по умолчанию)
```bash
python3 training/main.py
```

### Обучение конкретной модели
```bash
# MLP (по умолчанию: adam)
python3 training/main.py --model mlp

# CNN (по умолчанию: sgd)
python3 training/main.py --model cnn

# MobileNetV2 (по умолчанию: adam)
python3 training/main.py --model mobilenet
```

### Выбор оптимизатора
```bash
# MLP с разными оптимизаторами
python3 training/main.py --model mlp --optimizer adam
python3 training/main.py --model mlp --optimizer adagrad
python3 training/main.py --model mlp --optimizer rmsprop

# CNN с разными оптимизаторами
python3 training/main.py --model cnn --optimizer sgd
python3 training/main.py --model cnn --optimizer adam
python3 training/main.py --model cnn --optimizer rmsprop

# MobileNetV2 с разными оптимизаторами
python3 training/main.py --model mobilenet --optimizer adam
python3 training/main.py --model mobilenet --optimizer adagrad
python3 training/main.py --model mobilenet --optimizer rmsprop
```

### Выбор количества эпох и learning rate
```bash
# MLP с 50 эпохами и LR=0.0005
python3 training/main.py --model mlp --epochs 50 --lr 0.0005

# CNN с 100 эпохами и LR=0.001
python3 training/main.py --model cnn --epochs 100 --lr 0.001

# MobileNetV2 с 50 эпохами fine-tuning и LR=0.0001
python3 training/main.py --model mobilenet --epochs 50 --lr 0.001 --lr-finetune 0.0001
```

### Сравнение всех оптимизаторов
```bash
# Сравнить все оптимизаторы для MLP
python3 training/main.py --model mlp --compare-optimizers

# Сравнить все оптимизаторы для MobileNetV2
python3 training/main.py --model mobilenet --compare-optimizers

# Сравнить все оптимизаторы для всех моделей
python3 training/main.py --model all --compare-optimizers
```

### С выбором случайного зерна
```bash
python3 training/main.py --model mobilenet --optimizer adam --seed 42
```

## Описание моделей

### MLP (Multilayer Perceptron)
- **Вход**: 32×32×3 = 3072 признаков
- **Слои**: 512 → 256 → 128 → 3 класса
- **Нормализация**: BatchNorm + Dropout
- **Оптимизаторы**: adam, adagrad, rmsprop
- **Ожидаемая точность**: ~75-85%

### CNN (Convolutional Neural Network)
- **Вход**: 32×32×3
- **Архитектура**: 2 свёрточных блока + pooling
- **Параметров**: ~50K
- **Оптимизаторы**: sgd, adam, rmsprop
- **Ожидаемая точность**: ~70-80%

### MobileNetV2 (Transfer Learning)
- **Вход**: 224×224×3
- **Backbone**: MobileNetV2 (ImageNet weights)
- **Обучение**: 2 этапа (классификатор + fine-tuning)
- **Параметров**: ~3.5M
- **Оптимизаторы**: adam, adagrad, rmsprop
- **Ожидаемая точность**: ~85-95%

## Описание оптимизаторов

### Adam (Adaptive Moment Estimation)
- **Плюсы**: Быстрая сходимость, работает из коробки
- **Минусы**: Может переобучаться
- **Рекомендация**: По умолчанию для MLP и MobileNet

### Adagrad (Adaptive Gradient)
- **Плюсы**: Адаптирует LR для каждого параметра
- **Минусы**: LR может стать слишком маленькой
- **Рекомендация**: Для разреженных данных

### RMSprop (Root Mean Square Propagation)
- **Плюсы**: Хорошо работает для RNN, решает проблему затухания LR
- **Минусы**: Требует подбора гиперпараметров
- **Рекомендация**: Для CNN и нестабильного обучения

### SGD (Stochastic Gradient Descent)
- **Плюсы**: Простой, хорошо обобщает
- **Минусы**: Медленная сходимость, требует подбора LR
- **Рекомендация**: По умолчанию для CNN

## Конфигурация

Все настройки находятся в `configs/config.py`:

```python
# MLP
MLPConfig:
    HIDDEN_LAYERS = [512, 256, 128]
    EPOCHS = 100
    LEARNING_RATE = 0.001
    AVAILABLE_OPTIMIZERS = ['adam', 'adagrad', 'rmsprop']

# CNN
CNNConfig:
    HIDDEN_SIZE = 32
    EPOCHS = 500
    LEARNING_RATE = 0.005
    AVAILABLE_OPTIMIZERS = ['sgd', 'adam', 'rmsprop']

# MobileNetV2
MobileNetConfig:
    IMAGE_SIZE = 224
    EPOCHS_STAGE1 = 30   # Только классификатор
    EPOCHS_STAGE2 = 100  # Fine-tuning
    LEARNING_RATE_STAGE1 = 0.001
    LEARNING_RATE_STAGE2 = 0.0001
    FINETUNE_LAYERS = 20
    AVAILABLE_OPTIMIZERS = ['adam', 'adagrad', 'rmsprop']
```

## Сохранённые файлы

После обучения создаются:
- `checkpoints/*.pth` - веса моделей
- `data/models/*.onnx` - ONNX модели для продакшена

## Требования

```
torch>=1.9.0
torchvision>=0.10.0
onnx>=1.10.0
onnxruntime>=1.9.0
scikit-learn>=0.24.0
tqdm>=4.62.0
pillow>=8.0.0
```

## Примеры запуска

### 1. Обучение MobileNetV2 с Adam
```bash
$ python main.py --model mobilenet --optimizer adam

============================================================
Классификация: крокодил, аллигатор, кайман
============================================================
PyTorch: 1.13.1, CUDA: True
Модель: mobilenet
Оптимизатор: ADAM
============================================================
...
📊 Итоговая точность MobileNetV2 (ADAM): 92.50%
```

### 2. Сравнение оптимизаторов для MLP
```bash
$ python main.py --model mlp --compare-optimizers

============================================================
Сравнение оптимизаторов для MLP
============================================================
...
📊 Итоговая точность MLP (ADAM): 82.50%
...
📊 Итоговая точность MLP (ADAGRAD): 79.30%
...
📊 Итоговая точность MLP (RMSPROP): 80.10%

🏆 Лучшая модель: MLP (ADAM) - 82.50%
```

## Добавление нового оптимизатора

1. Откройте `scripts/train_scripts.py`
2. Добавьте новый оптимизатор в функцию `get_optimizer`:

```python
def get_optimizer(name, params, lr, weight_decay=1e-4, momentum=0.9):
    ...
    elif name == 'adamw':
        return optim.AdamW(params, lr=lr, weight_decay=weight_decay)
    ...
```

3. Обновите `AVAILABLE_OPTIMIZERS` в конфигурации модели

## Добавление новой модели

1. Создайте файл модели в `models/новая_модель.py`
2. Добавьте функцию обучения в `scripts/train_scripts.py`
3. Обновите `main.py` для поддержки новой модели
