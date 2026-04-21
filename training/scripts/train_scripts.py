"""
Скрипты обучения для разных моделей
"""
import torch
import torch.nn as nn
import torch.optim as optim

from configs import MLPConfig, CNNConfig, ResNetConfig
from models import MLPModel, CNNModel, ResNet20Model
from utils import (
    load_data, create_dataloaders, Trainer,
    export_to_onnx, get_device, set_seed, validate,
    print_classification_report
)


def get_optimizer(name, params, lr, weight_decay=1e-4, momentum=0.9):
    """
    Фабрика оптимизаторов
    
    Args:
        name: Название оптимизатора ('adam', 'adagrad', 'rmsprop', 'sgd')
        params: Параметры модели
        lr: Learning rate
        weight_decay: L2 регуляризация
        momentum: Моментум (для SGD, RMSprop)
    
    Returns:
        Optimizer
    """
    name = name.lower()
    
    if name == 'adam':
        return optim.Adam(params, lr=lr, weight_decay=weight_decay)
    elif name == 'adagrad':
        return optim.Adagrad(params, lr=lr, weight_decay=weight_decay)
    elif name == 'rmsprop':
        return optim.RMSprop(
            params, 
            lr=lr, 
            weight_decay=weight_decay,
            momentum=momentum,
            alpha=0.99
        )
    elif name == 'sgd':
        return optim.SGD(
            params, 
            lr=lr, 
            momentum=momentum, 
            weight_decay=weight_decay
        )
    else:
        raise ValueError(f"Неизвестный оптимизатор: {name}. Доступны: adam, adagrad, rmsprop, sgd")


def train_mlp(optimizer_name='adam', seed=42, epochs=None, lr=None):
    """
    Обучение MLP модели
    
    Args:
        optimizer_name: Название оптимизатора ('adam', 'adagrad', 'rmsprop')
        seed: Случайное зерно
        epochs: Количество эпох (None = из конфига)
        lr: Learning rate (None = из конфига)
    
    Returns:
        best_acc: Лучшая точность валидации
    """
    print("\n" + "="*60)
    print("Обучение MLP модели")
    print("="*60)
    
    config = MLPConfig()
    config.setup_dirs()
    device = get_device()
    set_seed(seed)
    
    # Переопределение параметров из аргументов
    if epochs is not None:
        config.EPOCHS = epochs
    if lr is not None:
        config.LEARNING_RATE = lr
    
    # Загрузка данных
    train_X, train_y, test_X, test_y = load_data(
        config.DATA_DIR,
        config.CLASSES,
        image_size=32
    )
    
    # Создание dataloader
    dataloader = create_dataloaders(
        train_X, train_y, test_X, test_y,
        config,
        model_type='mlp'
    )
    
    # Создание модели
    model = MLPModel(
        input_size=config.INPUT_SIZE,
        hidden_layers=config.HIDDEN_LAYERS,
        num_classes=len(config.CLASSES),
        dropout=config.DROPOUT
    ).to(device)
    
    print(f"\nАрхитектура MLP:")
    print(model)
    
    # Оптимизатор и функция потерь
    criterion = nn.CrossEntropyLoss()
    optimizer = get_optimizer(
        optimizer_name, 
        model.parameters(), 
        config.LEARNING_RATE,
        config.WEIGHT_DECAY
    )
    
    print(f"\nОптимизатор: {optimizer_name.upper()}")
    print(f"Learning rate: {config.LEARNING_RATE}")
    print(f"Эпох: {config.EPOCHS}")
    
    # Обучение
    trainer = Trainer(
        model, criterion, optimizer, device,
        checkpoint_path=config.CHECKPOINT
    )
    
    best_acc = trainer.train(
        dataloader,
        epochs=config.EPOCHS,
        model_name=config.MODEL_NAME,
        log_every=10
    )
    
    # Оценка качества
    print("\n" + "="*60)
    print("Оценка качества")
    print("="*60)
    
    _, _, y_true, y_pred = validate(model, dataloader['test'], criterion, device)
    print_classification_report(y_true, y_pred, config.CLASSES, 'Test')
    
    # Экспорт в ONNX
    export_to_onnx(
        model, config.MODEL_NAME, config.ONNX_PATH,
        (config.INPUT_SIZE,), device
    )
    
    print(f"\n📊 Итоговая точность MLP ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc


def train_cnn(optimizer_name='sgd', seed=42, epochs=None, lr=None):
    """
    Обучение CNN модели
    
    Args:
        optimizer_name: Название оптимизатора ('sgd', 'adam', 'rmsprop')
        seed: Случайное зерно
        epochs: Количество эпох (None = из конфига)
        lr: Learning rate (None = из конфига)
    
    Returns:
        best_acc: Лучшая точность валидации
    """
    print("\n" + "="*60)
    print("Обучение CNN модели")
    print("="*60)
    
    config = CNNConfig()
    config.setup_dirs()
    device = get_device()
    set_seed(seed)
    
    # Переопределение параметров из аргументов
    if epochs is not None:
        config.EPOCHS = epochs
    if lr is not None:
        config.LEARNING_RATE = lr
    
    # Загрузка данных
    train_X, train_y, test_X, test_y = load_data(
        config.DATA_DIR,
        config.CLASSES,
        image_size=config.IMAGE_SIZE
    )
    
    # Создание dataloader
    dataloader = create_dataloaders(
        train_X, train_y, test_X, test_y,
        config,
        model_type='cnn'
    )
    
    # Создание модели
    model = CNNModel(
        hidden_size=config.HIDDEN_SIZE,
        num_classes=len(config.CLASSES),
        dropout=config.DROPOUT
    ).to(device)
    
    print(f"\nАрхитектура CNN:")
    print(model)
    
    # Оптимизатор и функция потерь
    criterion = nn.CrossEntropyLoss(label_smoothing=config.LABEL_SMOOTHING)
    optimizer = get_optimizer(
        optimizer_name,
        model.parameters(),
        config.LEARNING_RATE,
        config.WEIGHT_DECAY
    )
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=240, gamma=0.5)
    
    print(f"\nОптимизатор: {optimizer_name.upper()}")
    print(f"Learning rate: {config.LEARNING_RATE}")
    print(f"Эпох: {config.EPOCHS}")
    
    # Обучение
    trainer = Trainer(
        model, criterion, optimizer, device,
        checkpoint_path=config.CHECKPOINT,
        scheduler=scheduler
    )
    
    best_acc = trainer.train(
        dataloader,
        epochs=config.EPOCHS,
        model_name=config.MODEL_NAME,
        log_every=50
    )
    
    # Оценка качества
    print("\n" + "="*60)
    print("Оценка качества")
    print("="*60)
    
    _, _, y_true, y_pred = validate(model, dataloader['test'], criterion, device)
    print_classification_report(y_true, y_pred, config.CLASSES, 'Test')
    
    # Экспорт в ONNX
    export_to_onnx(
        model, config.MODEL_NAME, config.ONNX_PATH,
        (3, config.IMAGE_SIZE, config.IMAGE_SIZE), device
    )
    
    print(f"\n📊 Итоговая точность CNN ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc


def train_resnet20(optimizer_name='adam', seed=42, epochs=None, epochs_stage1=None, finetune_layers=None, lr=None, lr_finetune=None):
    """
    Обучение ResNet20 (transfer learning)

    Args:
        optimizer_name: Название оптимизатора ('adam', 'adagrad', 'rmsprop')
        seed: Случайное зерно
        epochs: Количество эпох для этапа 2 (None = из конфига)
        epochs_stage1: Количество эпох для этапа 1 (None = из конфига)
        finetune_layers: Количество размораживаемых слоёв (None = из конфига)
        lr: Learning rate для этапа 1 (None = из конфига)
        lr_finetune: Learning rate для этапа 2 (None = из конфига)

    Returns:
        best_acc: Лучшая точность валидации
    """
    print("\n" + "="*60)
    print("Обучение ResNet20 (Transfer Learning)")
    print("="*60)

    config = ResNetConfig()
    config.setup_dirs()
    device = get_device()
    set_seed(seed)

    # Переопределение параметров из аргументов
    if epochs is not None:
        config.EPOCHS_STAGE2 = epochs
    if epochs_stage1 is not None:
        config.EPOCHS_STAGE1 = epochs_stage1
    if finetune_layers is not None:
        config.FINETUNE_LAYERS = finetune_layers
    if lr is not None:
        config.LEARNING_RATE_STAGE1 = lr
    if lr_finetune is not None:
        config.LEARNING_RATE_STAGE2 = lr_finetune

    # Загрузка данных
    train_X, train_y, test_X, test_y = load_data(
        config.DATA_DIR,
        config.CLASSES,
        image_size=config.IMAGE_SIZE
    )

    # Создание dataloader
    dataloader = create_dataloaders(
        train_X, train_y, test_X, test_y,
        config,
        model_type='resnet20'
    )

    # Создание модели
    model = ResNet20Model(
        num_classes=len(config.CLASSES),
        pretrained=config.PRETRAINED
    ).to(device)

    print(f"\nАрхитектура ResNet20:")
    print(model)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    # ============================================================
    # ЭТАП 1: Обучение только классификатора
    # ============================================================
    print("\n" + "="*60)
    print("ЭТАП 1: Обучение классификатора (база заморожена)")
    print("="*60)

    model.freeze_base()

    # Подсчёт параметров
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Обучаемых параметров: {trainable:,} из {total:,}")

    optimizer_stage1 = get_optimizer(
        optimizer_name,
        filter(lambda p: p.requires_grad, model.parameters()),
        config.LEARNING_RATE_STAGE1,
        config.WEIGHT_DECAY
    )

    print(f"\nОптимизатор (этап 1): {optimizer_name.upper()}")
    print(f"Learning rate: {config.LEARNING_RATE_STAGE1}")
    print(f"Эпох этап 1: {config.EPOCHS_STAGE1}")
    
    trainer = Trainer(
        model, criterion, optimizer_stage1, device,
        checkpoint_path=config.CHECKPOINT
    )
    
    best_acc = trainer.train(
        dataloader,
        epochs=config.EPOCHS_STAGE1,
        model_name=f"{config.MODEL_NAME} Этап 1",
        log_every=5
    )
    
    # ============================================================
    # ЭТАП 2: Fine-tuning
    # ============================================================
    print("\n" + "="*60)
    print("ЭТАП 2: Fine-tuning (разморозка последних слоёв)")
    print("="*60)

    frozen, unfrozen = model.unfreeze_last_n_layers(config.FINETUNE_LAYERS)
    print(f"Заморожено: {frozen}, Разморожено: {unfrozen}")
    print(f"Fine-tune слоёв: {config.FINETUNE_LAYERS}")

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Обучаемых параметров: {trainable:,} из {total:,}")
    
    # Для fine-tuning используем меньший learning rate
    lr_stage2 = config.LEARNING_RATE_STAGE2
    optimizer_stage2 = get_optimizer(
        optimizer_name,
        filter(lambda p: p.requires_grad, model.parameters()),
        lr_stage2,
        config.WEIGHT_DECAY
    )
    scheduler_stage2 = optim.lr_scheduler.StepLR(
        optimizer_stage2, step_size=30, gamma=0.5
    )
    
    print(f"\nОптимизатор (этап 2): {optimizer_name.upper()}")
    print(f"Learning rate: {lr_stage2}")
    print(f"Эпох этап 2: {config.EPOCHS_STAGE2}")

    # Обновление оптимизатора
    trainer.optimizer = optimizer_stage2
    trainer.scheduler = scheduler_stage2
    
    best_acc = trainer.train(
        dataloader,
        epochs=config.EPOCHS_STAGE2,
        model_name=f"{config.MODEL_NAME} Этап 2",
        log_every=10
    )
    
    # Оценка качества
    print("\n" + "="*60)
    print("Оценка качества")
    print("="*60)
    
    _, _, y_true, y_pred = validate(model, dataloader['test'], criterion, device)
    print_classification_report(y_true, y_pred, config.CLASSES, 'Test')
    
    # Экспорт в ONNX
    export_to_onnx(
        model, config.MODEL_NAME, config.ONNX_PATH,
        (3, config.IMAGE_SIZE, config.IMAGE_SIZE), device
    )
    
    print(f"\n📊 Итоговая точность ResNet20 ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc
