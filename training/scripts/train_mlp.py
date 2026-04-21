"""
Обучение MLP модели
"""
import torch
import torch.nn as nn
import torch.optim as optim
from configs import MLPConfig
from models import MLPModel
from utils import (
    load_data, create_dataloaders, Trainer,
    export_to_onnx, get_device, set_seed, validate,
    print_classification_report
)


def train_mlp(optimizer_name='adam', seed=42, epochs=None, lr=None):
    """Обучение MLP модели"""
    print("\n" + "="*60)
    print("Обучение MLP")
    print("="*60)

    config = MLPConfig()
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
        image_size=32
    )

    dataloader = create_dataloaders(
        train_X, train_y, test_X, test_y, config, model_type='mlp'
    )

    model = MLPModel(
        num_classes=len(config.CLASSES),
        input_size=config.INPUT_SIZE,
        hidden_layers=config.HIDDEN_LAYERS,
        dropout=config.DROPOUT
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    
    optimizer_name = optimizer_name.lower()
    if optimizer_name == 'adam':
        optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    elif optimizer_name == 'adagrad':
        optimizer = optim.Adagrad(model.parameters(), lr=config.LEARNING_RATE)
    elif optimizer_name == 'rmsprop':
        optimizer = optim.RMSprop(model.parameters(), lr=config.LEARNING_RATE)
    else:
        raise ValueError(f"Неизвестный оптимизатор: {optimizer_name}")

    trainer = Trainer(model, dataloader, criterion, optimizer, device)
    best_acc = trainer.train(config.EPOCHS)

    _, _, y_true, y_pred = validate(model, dataloader['test'], criterion, device)
    print_classification_report(y_true, y_pred, config.CLASSES, 'Test')

    export_to_onnx(
        model, config.MODEL_NAME, config.ONNX_PATH,
        (3, 32, 32), device
    )

    print(f"\nИтоговая точность MLP ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc