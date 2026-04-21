"""
Обучение CNN модели
"""
import torch
import torch.nn as nn
from configs import CNNConfig
from models import CNNModel
from utils import (
    load_data, create_dataloaders, Trainer,
    export_to_onnx, get_device, set_seed, validate,
    print_classification_report
)


def train_cnn(optimizer_name='sgd', seed=42, epochs=None, lr=None):
    """Обучение CNN модели"""
    print("\n" + "="*60)
    print("Обучение CNN модели")
    print("="*60)

    config = CNNConfig()
    config.setup_dirs()
    device = get_device()
    set_seed(seed)

    if epochs is not None:
        config.EPOCHS = epochs
    if lr is not None:
        config.LEARNING_RATE = lr

    train_X, train_y, test_X, test_y = load_data(
        config.DATA_DIR,
        config.CLASSES,
        image_size=config.IMAGE_SIZE
    )

    dataloader = create_dataloaders(
        train_X, train_y, test_X, test_y,
        config,
        model_type='cnn'
    )

    model = CNNModel(
        hidden_size=config.HIDDEN_SIZE,
        num_classes=len(config.CLASSES),
        dropout=config.DROPOUT
    ).to(device)

    print(f"\nАрхитектура CNN:")
    print(model)

    criterion = nn.CrossEntropyLoss(label_smoothing=config.LABEL_SMOOTHING)

    from .train_mlp import get_optimizer
    optimizer = get_optimizer(
        optimizer_name,
        model.parameters(),
        config.LEARNING_RATE,
        config.WEIGHT_DECAY
    )
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=240, gamma=0.5)

    print(f"\nОптимизатор: {optimizer_name.upper()}")
    print(f"Learning rate: {config.LEARNING_RATE}")
    print(f"Эпох: {config.EPOCHS}")

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

    _, _, y_true, y_pred = validate(model, dataloader['test'], criterion, device)
    print_classification_report(y_true, y_pred, config.CLASSES, 'Test')

    export_to_onnx(
        model, config.MODEL_NAME, config.ONNX_PATH,
        (3, config.IMAGE_SIZE, config.IMAGE_SIZE), device
    )

    print(f"\nИтоговая точность CNN ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc