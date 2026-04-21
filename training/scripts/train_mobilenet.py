"""
Обучение MobileNetV2 модели (transfer learning)
"""

import torch
import torch.nn as nn
from configs import MobileNetConfig
from models import MobileNetModel
from utils import (
    setup_mlflow, log_params,
    load_data, create_dataloaders, Trainer,
    export_to_onnx, get_device, set_seed, validate,
    print_classification_report
)


def train_mobilenet(
    optimizer_name="adam",
    seed=42,
    epochs=None,
    epochs_stage1=None,
    finetune_layers=None,
    lr=None,
    lr_finetune=None,
):
    """Обучение MobileNetV2 (transfer learning)"""
    print("\n" + "=" * 60)
    print("Обучение MobileNetV2 (Transfer Learning)")
    print("=" * 60)

    config = MobileNetConfig()
    config.setup_dirs()
    device = get_device()
    set_seed(seed)

    # MLflow
    mlflow = setup_mlflow()
    log_params({
        "model": "MobileNetV2",
        "optimizer": optimizer_name,
        "seed": seed,
        "epochs_stage1": epochs_stage1 or config.EPOCHS_STAGE1,
        "epochs_stage2": epochs or config.EPOCHS_STAGE2,
        "lr_stage1": lr or config.LEARNING_RATE_STAGE1,
        "lr_stage2": lr_finetune or config.LEARNING_RATE_STAGE2,
        "finetune_layers": finetune_layers or config.FINETUNE_LAYERS,
    })

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
        config.DATA_DIR, config.CLASSES, image_size=config.IMAGE_SIZE
    )

    dataloader = create_dataloaders(
        train_X, train_y, test_X, test_y, config, model_type="mobilenet"
    )

    model = MobileNetModel(num_classes=len(config.CLASSES), pretrained=config.PRETRAINED).to(device)

    print(f"\nАрхитектура MobileNetV2:")
    print(model)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    from .train_mlp import get_optimizer

    optimizer = get_optimizer(optimizer_name, model.parameters(), config.LEARNING_RATE_STAGE1)

    # ЭТАП 1: Обучение только классификатора
    print("\nЭТАП 1: Обучение классификатора (база заморожена)")
    model.freeze_base()

    def mlflow_callback(epoch, loss, acc):
        import mlflow
        mlflow.log_metric("val_loss", loss, step=epoch)
        mlflow.log_metric("val_acc", acc, step=epoch)

    trainer = Trainer(model, criterion, optimizer, device, mlflow_callback=mlflow_callback)
    best_acc = trainer.train(
        dataloader, epochs=config.EPOCHS_STAGE1, model_name="MobileNetV2_stage1"
    )

    # ЭТАП 2: Fine-tuning
    print("\nЭТАП 2: Fine-tuning")
    model.unfreeze_last_n_layers(config.FINETUNE_LAYERS)

    optimizer_ft = get_optimizer(optimizer_name, model.parameters(), config.LEARNING_RATE_STAGE2)

    trainer = Trainer(model, criterion, optimizer_ft, device)
    best_acc = trainer.train(
        dataloader, epochs=config.EPOCHS_STAGE2, model_name="MobileNetV2_stage2"
    )

    _, _, y_true, y_pred = validate(model, dataloader["test"], criterion, device)
    print_classification_report(y_true, y_pred, config.CLASSES, "Test")

    export_to_onnx(
        model,
        config.MODEL_NAME,
        config.ONNX_PATH,
        (3, config.IMAGE_SIZE, config.IMAGE_SIZE),
        device,
    )

    trainer.log_final_artifacts(
        dataloader, criterion, device,
        class_names=config.CLASSES,
        checkpoint_path=config.CHECKPOINT,
        onnx_path=config.ONNX_PATH
    )

    print(f"\nИтоговая точность MobileNetV2 ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc
