#!/usr/bin/env python3
"""
Обучение любой модели (CNN, MLP, ResNet20, MobileNetV2)
"""
import argparse
from typing import Optional

import torch
import torch.nn as nn
import torch.optim as optim
from configs import CNNConfig, MLPConfig, MobileNetConfig, ResNetConfig
from models import CNNModel, MLPModel, MobileNetModel, ResNet20Model
from utils import (Trainer, create_dataloaders, export_to_onnx, get_device,
                   load_data, log_params, print_classification_report,
                   set_seed, setup_mlflow, validate)


def get_optimizer(name: str, params, lr: float, weight_decay: float = 1e-4, momentum: float = 0.9):
    """Создать оптимизатор"""
    name = name.lower()
    if name == "adam":
        return optim.Adam(params, lr=lr, weight_decay=weight_decay)
    elif name == "adagrad":
        return optim.Adagrad(params, lr=lr, weight_decay=weight_decay)
    elif name == "rmsprop":
        return optim.RMSprop(params, lr=lr, weight_decay=weight_decay, momentum=momentum)
    elif name == "sgd":
        return optim.SGD(params, lr=lr, momentum=momentum, weight_decay=weight_decay)
    else:
        raise ValueError(f"Неизвестный оптимизатор: {name}")


MODEL_CONFIGS = {
    "cnn": {"class": CNNModel, "config": CNNConfig, "image_size": 32},
    "mlp": {"class": MLPModel, "config": MLPConfig, "image_size": 32},
    "resnet20": {"class": ResNet20Model, "config": ResNetConfig, "image_size": 224},
    "mobilenet": {"class": MobileNetModel, "config": MobileNetConfig, "image_size": 224},
}


def train_model(
    model_name: str = "cnn",
    optimizer_name: str = "sgd",
    seed: int = 42,
    epochs: Optional[int] = None,
    lr: Optional[float] = None,
    epochs_stage1: Optional[int] = None,
    finetune_layers: Optional[int] = None,
    lr_finetune: Optional[float] = None,
    device: str = "cuda",
) -> float:
    """Обучение модели"""
    model_name = model_name.lower()
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Неизвестная модель: {model_name}. Доступные: {list(MODEL_CONFIGS.keys())}")

    print("\n" + "=" * 60)
    print(f"Обучение {model_name.upper()} модели")
    print("=" * 60)

    model_cfg = MODEL_CONFIGS[model_name]
    config = model_cfg["config"]()
    config.setup_dirs()
    device = torch.device(device)
    print(f"Устройство: {device}")
    set_seed(seed)

    import mlflow
    setup_mlflow(experiment_name="crocodilian_classifier")
    run_name = f"{model_name}_{optimizer_name}_e{epochs or config.EPOCHS}_s{seed}"

    with mlflow.start_run(run_name=run_name):
        log_params({
            "model": model_name.upper(),
            "optimizer": optimizer_name,
            "seed": seed,
            "epochs": epochs or config.EPOCHS,
            "lr": lr or config.LEARNING_RATE,
            "image_size": model_cfg["image_size"],
            "device": device.type,
        })

        if epochs is not None:
            config.EPOCHS = epochs
        if lr is not None:
            config.LEARNING_RATE = lr

        train_X, train_y, test_X, test_y = load_data(
            config.DATA_DIR, config.CLASSES, image_size=model_cfg["image_size"]
        )

        dataloader = create_dataloaders(
            train_X, train_y, test_X, test_y, config, model_type=model_name
        )

        model_class = model_cfg["class"]
        if model_name == "cnn":
            model = model_class(
                hidden_size=config.HIDDEN_SIZE,
                num_classes=len(config.CLASSES),
                dropout=config.DROPOUT
            ).to(device)
        elif model_name == "mlp":
            model = model_class(
                num_classes=len(config.CLASSES),
                input_size=config.INPUT_SIZE,
                hidden_layers=config.HIDDEN_LAYERS,
                dropout=config.DROPOUT,
            ).to(device)
        elif model_name == "resnet20":
            model = model_class(num_classes=len(config.CLASSES), pretrained=config.PRETRAINED).to(device)
        elif model_name == "mobilenet":
            model = model_class(num_classes=len(config.CLASSES), pretrained=config.PRETRAINED).to(device)

        print(f"\nАрхитектура {model_name.upper()}:")
        print(model)

        criterion = nn.CrossEntropyLoss(
            label_smoothing=getattr(config, "LABEL_SMOOTHING", 0.0)
        )

        optimizer = get_optimizer(
            optimizer_name, model.parameters(), config.LEARNING_RATE
        )
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=240, gamma=0.5)

        print(f"\nОптимизатор: {optimizer_name.upper()}")
        print(f"Learning rate: {config.LEARNING_RATE}")
        print(f"Эпох: {config.EPOCHS}")

        def mlflow_callback(epoch, loss, acc):
            import mlflow
            mlflow.log_metric("val_loss", loss, step=epoch)
            mlflow.log_metric("val_acc", acc, step=epoch)

        trainer = Trainer(
            model, criterion, optimizer, device,
            checkpoint_path=config.CHECKPOINT,
            scheduler=scheduler if hasattr(config, "SCHEDULER_STEP") else None,
            mlflow_callback=mlflow_callback
        )

        best_acc = trainer.train(
            dataloader, epochs=config.EPOCHS, model_name=config.MODEL_NAME, log_every=1
        )

        _, _, y_true, y_pred = validate(model, dataloader["test"], criterion, device)
        print_classification_report(y_true, y_pred, config.CLASSES, "Test")

        export_to_onnx(
            model,
            config.MODEL_NAME,
            config.ONNX_PATH,
            (3, model_cfg["image_size"], model_cfg["image_size"]),
            device,
        )

        trainer.log_final_artifacts(
            dataloader, criterion, device,
            class_names=config.CLASSES,
            checkpoint_path=config.CHECKPOINT,
            onnx_path=config.ONNX_PATH
        )

        print(f"\nИтоговая точность {model_name.upper()} ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc


def main():
    parser = argparse.ArgumentParser(description="Обучение модели")
    parser.add_argument("--model", default="cnn", choices=["cnn", "mlp", "resnet20", "mobilenet"],
                        help="Модель для обучения")
    parser.add_argument("--optimizer", default="sgd", choices=["sgd", "adam", "adagrad", "rmsprop"],
                        help="Оптимизатор")
    parser.add_argument("--seed", type=int, default=42, help="Seed для воспроизводимости")
    parser.add_argument("--epochs", type=int, help="Количество эпох")
    parser.add_argument("--lr", type=float, help="Learning rate")
    args = parser.parse_args()

    train_model(
        model_name=args.model,
        optimizer_name=args.optimizer,
        seed=args.seed,
        epochs=args.epochs,
        lr=args.lr,
    )


if __name__ == "__main__":
    main()