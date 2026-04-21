"""
Конфигурация обучения
"""

from pathlib import Path

# Определяем базовую директорию проекта (на два уровня выше configs/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Config:
    """Базовая конфигурация"""

    # Данные
    CLASSES = ["крокодил", "аллигатор", "кайман"]
    DATA_DIR = BASE_DIR / "data"

    # Обучение
    BATCH_SIZE = 32
    EPOCHS = 100
    LEARNING_RATE = 0.001
    WEIGHT_DECAY = 1e-4

    # Оптимизатор по умолчанию
    DEFAULT_OPTIMIZER = "adam"

    # Чекпоинты и ONNX (сохраняем в директорию запуска скрипта)
    CHECKPOINT_DIR = Path("checkpoints")
    ONNX_DIR = Path("data/models")

    @classmethod
    def setup_dirs(cls):
        cls.CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        cls.ONNX_DIR.mkdir(parents=True, exist_ok=True)


class MLPConfig(Config):
    """Конфигурация для MLP"""

    MODEL_NAME = "MLP"
    CHECKPOINT = "checkpoints/mlp_checkpoint.pth"
    ONNX_PATH = "data/models/mlp.onnx"

    # Архитектура
    INPUT_SIZE = 32 * 32 * 3
    HIDDEN_LAYERS = [512, 256, 128]
    DROPOUT = 0.3

    # Обучение
    EPOCHS = 100
    LEARNING_RATE = 0.001

    # Доступные оптимизаторы
    AVAILABLE_OPTIMIZERS = ["adam", "adagrad", "rmsprop"]


class CNNConfig(Config):
    """Конфигурация для CNN (самописная)"""

    MODEL_NAME = "CNN"
    CHECKPOINT = "checkpoints/cnn_checkpoint.pth"
    ONNX_PATH = "data/models/cnn.onnx"

    # Архитектура
    IMAGE_SIZE = 32
    HIDDEN_SIZE = 32
    DROPOUT = 0.3

    # Обучение
    EPOCHS = 500
    LEARNING_RATE = 0.005
    LABEL_SMOOTHING = 0.1

    # Аугментация
    USE_AUGMENTATION = True

    # Доступные оптимизаторы
    AVAILABLE_OPTIMIZERS = ["sgd", "adam", "rmsprop"]
    DEFAULT_OPTIMIZER = "sgd"


class ResNetConfig(Config):
    """Конфигурация для ResNet20"""

    MODEL_NAME = "ResNet20"
    CHECKPOINT = "checkpoints/resnet20_checkpoint.pth"
    ONNX_PATH = "data/models/resnet20.onnx"

    # Архитектура
    IMAGE_SIZE = 224  # Стандарт для ImageNet
    PRETRAINED = True

    # Обучение (два этапа)
    EPOCHS_STAGE1 = 50  # Только классификатор
    EPOCHS_STAGE2 = 30  # Fine-tuning
    LEARNING_RATE_STAGE1 = 0.001
    LEARNING_RATE_STAGE2 = 0.0001
    FINETUNE_LAYERS = 20  # Количество размораживаемых слоёв

    # Нормализация ImageNet
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]

    # Доступные оптимизаторы
    AVAILABLE_OPTIMIZERS = ["adam", "adagrad", "rmsprop"]


class MobileNetConfig(Config):
    """Конфигурация для MobileNetV2"""

    MODEL_NAME = "MobileNetV2"
    CHECKPOINT = "checkpoints/mobilenet_checkpoint.pth"
    ONNX_PATH = "data/models/mobilenet.onnx"

    # Архитектура
    IMAGE_SIZE = 224
    PRETRAINED = True

    # Обучение (два этапа)
    EPOCHS_STAGE1 = 50
    EPOCHS_STAGE2 = 30
    LEARNING_RATE_STAGE1 = 0.001
    LEARNING_RATE_STAGE2 = 0.0001
    FINETUNE_LAYERS = 20

    # Нормализация ImageNet
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]

    # Доступные оптимизаторы
    AVAILABLE_OPTIMIZERS = ["adam", "adagrad", "rmsprop"]
