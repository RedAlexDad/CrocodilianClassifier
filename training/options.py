"""
Константы и настройки для обучения моделей
"""
from scripts import train_mlp, train_cnn, train_resnet20


OPTIMIZERS = ['adam', 'adagrad', 'rmsprop', 'sgd']
OPTIMIZERS_MLP = ['adam', 'adagrad', 'rmsprop']
OPTIMIZERS_CNN = ['sgd', 'adam', 'rmsprop']
OPTIMIZERS_RESNET20 = ['adam', 'adagrad', 'rmsprop']


DEFAULT_OPTIMIZERS = {
    'mlp': 'adam',
    'cnn': 'sgd',
    'resnet20': 'adam',
}


MODELS = ['mlp', 'cnn', 'resnet20']


def get_model_trainer(model_type):
    """Получить функцию обучения для модели"""
    trainers = {
        'mlp': train_mlp,
        'cnn': train_cnn,
        'resnet20': train_resnet20,
    }
    return trainers.get(model_type)


def get_default_optimizer(model_type):
    """Получить оптимизатор по умолчанию для модели"""
    return DEFAULT_OPTIMIZERS.get(model_type, 'adam')


def get_available_optimizers(model_type):
    """Получить доступные оптимизаторы для модели"""
    optimizers = {
        'mlp': OPTIMIZERS_MLP,
        'cnn': OPTIMIZERS_CNN,
        'resnet20': OPTIMIZERS_RESNET20,
    }
    return optimizers.get(model_type, OPTIMIZERS)


def print_summary(results):
    """Вывод сводки по обучению"""
    print("\n" + "="*60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("="*60)
    
    for entry in results:
        print(f"  {entry['name']} ({entry['optimizer'].upper()}): {entry['acc']:.2f}%")
    
    print("="*60)
    
    if results:
        best = max(results, key=lambda x: x['acc'])
        print(f"\n🏆 Лучшая модель: {best['name']} ({best['optimizer'].upper()}) - {best['acc']:.2f}%")