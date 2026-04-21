"""
Обучение ResNet20 модели (transfer learning)
"""
import torch
import torch.nn as nn
from configs import ResNetConfig
from models import ResNet20Model
from utils import (
    load_data, create_dataloaders, Trainer,
    export_to_onnx, get_device, set_seed, validate,
    print_classification_report
)


def train_resnet20(optimizer_name='adam', seed=42, epochs=None, epochs_stage1=None, finetune_layers=None, lr=None, lr_finetune=None):
    """Обучение ResNet20 (transfer learning)"""
    print("\n" + "="*60)
    print("Обучение ResNet20 (Transfer Learning)")
    print("="*60)

    config = ResNetConfig()
    config.setup_dirs()
    device = get_device()
    set_seed(seed)

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

    train_X, train_y, test_X, test_y = load_data(
        config.DATA_DIR,
        config.CLASSES,
        image_size=config.IMAGE_SIZE
    )

    dataloader = create_dataloaders(
        train_X, train_y, test_X, test_y,
        config,
        model_type='resnet20'
    )

    model = ResNet20Model(
        num_classes=len(config.CLASSES),
        pretrained=config.PRETRAINED
    ).to(device)

    print(f"\nАрхитектура ResNet20:")
    print(model)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    from .train_mlp import get_optimizer
    optimizer = get_optimizer(
        optimizer_name,
        model.parameters(),
        config.LEARNING_RATE_STAGE1
    )

    # ЭТАП 1: Обучение только классификатора
    print("\nЭТАП 1: Обучение классификатора (база заморожена)")
    model.freeze_base()

    trainer = Trainer(model, criterion, optimizer, device)
    best_acc = trainer.train(
        dataloader,
        epochs=config.EPOCHS_STAGE1,
        model_name='ResNet20_stage1'
    )

    # ЭТАП 2: Fine-tuning
    print("\nЭТАП 2: Fine-tuning")
    model.unfreeze_last_n_layers(config.FINETUNE_LAYERS)

    optimizer_ft = get_optimizer(
        optimizer_name,
        model.parameters(),
        config.LEARNING_RATE_STAGE2
    )

    trainer = Trainer(model, criterion, optimizer_ft, device)
    best_acc = trainer.train(
        dataloader,
        epochs=config.EPOCHS_STAGE2,
        model_name='ResNet20_stage2'
    )

    _, _, y_true, y_pred = validate(model, dataloader['test'], criterion, device)
    print_classification_report(y_true, y_pred, config.CLASSES, 'Test')

    export_to_onnx(
        model, config.MODEL_NAME, config.ONNX_PATH,
        (3, config.IMAGE_SIZE, config.IMAGE_SIZE), device
    )

    print(f"\nИтоговая точность ResNet20 ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc