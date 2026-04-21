"""
Константы и настройки для обучения моделей
"""

from scripts import train_mlp, train_cnn, train_resnet20, train_mobilenet

OPTIMIZERS = ["adam", "adagrad", "rmsprop", "sgd"]
OPTIMIZERS_MLP = ["adam", "adagrad", "rmsprop"]
OPTIMIZERS_CNN = ["sgd", "adam", "rmsprop"]
OPTIMIZERS_TL = ["adam", "adagrad", "rmsprop"]  # Transfer learning: ResNet20, MobileNet


MODEL_CONFIGS = {
    "mlp": {
        "trainer": train_mlp,
        "default_optimizer": "adam",
        "available_optimizers": OPTIMIZERS_MLP,
        "description": "MLP (многослойный перцептрон)",
    },
    "cnn": {
        "trainer": train_cnn,
        "default_optimizer": "sgd",
        "available_optimizers": OPTIMIZERS_CNN,
        "description": "CNN (свёрточная нейросеть)",
    },
    "resnet20": {
        "trainer": train_resnet20,
        "default_optimizer": "adam",
        "available_optimizers": OPTIMIZERS_TL,
        "description": "ResNet20 (transfer learning)",
    },
    "mobilenet": {
        "trainer": train_mobilenet,
        "default_optimizer": "adam",
        "available_optimizers": OPTIMIZERS_TL,
        "description": "MobileNetV2 (transfer learning)",
    },
}


MODELS = list(MODEL_CONFIGS.keys())

DEFAULT_OPTIMIZER = "adam"
DEFAULT_MODEL = "all"


def get_model_config(model_type: str) -> dict | None:
    """Получить конфигурацию модели"""
    return MODEL_CONFIGS.get(model_type)


def get_default_optimizer(model_type: str) -> str:
    """Получить оптимизатор по умолчанию для модели"""
    config = get_model_config(model_type)
    if config is None:
        return DEFAULT_OPTIMIZER
    return config["default_optimizer"]


def get_available_optimizers(model_type: str) -> list:
    """Получить доступные оптимизаторы для модели"""
    config = get_model_config(model_type)
    if config is None:
        return OPTIMIZERS
    return config["available_optimizers"]


def get_model_description(model_type: str) -> str:
    """Получить описание модели"""
    config = get_model_config(model_type)
    if config is None:
        return ""
    return config["description"]


def print_summary(results):
    """Вывод сводки по обучению"""
    print("\n" + "=" * 60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)

    for entry in results:
        print(f"  {entry['name']} ({entry['optimizer'].upper()}): {entry['acc']:.2f}%")

    print("=" * 60)

    if results:
        best = max(results, key=lambda x: x["acc"])
        print(
            f"\n🏆 Лучшая модель: {best['name']} ({best['optimizer'].upper()}) - {best['acc']:.2f}%"
        )
