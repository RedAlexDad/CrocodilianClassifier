"""
Обучение MLP модели
"""

import torch
import torch.nn as nn
import torch.optim as optim
from configs import MLPConfig
from models import MLPModel
from utils import (
    setup_mlflow,
    log_params,
    load_data,
    create_dataloaders,
    Trainer,
    export_to_onnx,
    get_device,
    set_seed,
    validate,
    print_classification_report,
)


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


def train_mlp(optimizer_name="adam", seed=42, epochs=None, lr=None):
    """Обучение MLP модели"""
    print("\n" + "=" * 60)
    print("Обучение MLP")
    print("=" * 60)

    config = MLPConfig()
    config.setup_dirs()
    device = get_device()
    set_seed(seed)

    # MLflow with single experiment for all models
    import mlflow
    setup_mlflow(experiment_name="crocodilian_classifier")
    run_name = f"mlp_{optimizer_name}_e{epochs or config.EPOCHS}_s{seed}"

    with mlflow.start_run(run_name=run_name):
        log_params({
            "model": "MLP",
            "optimizer": optimizer_name,
            "seed": seed,
            "epochs": epochs or config.EPOCHS,
            "lr": lr or config.LEARNING_RATE,
            "input_size": config.INPUT_SIZE,
            "hidden_layers": config.HIDDEN_LAYERS,
        })

        if epochs is not None:
            config.EPOCHS = epochs
        if lr is not None:
            config.LEARNING_RATE = lr

        train_X, train_y, test_X, test_y = load_data(config.DATA_DIR, config.CLASSES, image_size=32)

        dataloader = create_dataloaders(train_X, train_y, test_X, test_y, config, model_type="mlp")

        model = MLPModel(
            num_classes=len(config.CLASSES),
            input_size=config.INPUT_SIZE,
            hidden_layers=config.HIDDEN_LAYERS,
            dropout=config.DROPOUT,
        ).to(device)

        criterion = nn.CrossEntropyLoss()

        optimizer_name = optimizer_name.lower()
        if optimizer_name == "adam":
            optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
        elif optimizer_name == "adagrad":
            optimizer = optim.Adagrad(model.parameters(), lr=config.LEARNING_RATE)
        elif optimizer_name == "rmsprop":
            optimizer = optim.RMSprop(model.parameters(), lr=config.LEARNING_RATE)
        else:
            raise ValueError(f"Неизвестный оптимизатор: {optimizer_name}")

        def mlflow_log_callback(epoch, loss, acc):
            import mlflow
            mlflow.log_metric("val_loss", loss, step=epoch)
            mlflow.log_metric("val_acc", acc, step=epoch)

        trainer = Trainer(
            model, criterion, optimizer, device,
            checkpoint_path=config.CHECKPOINT,
            mlflow_callback=mlflow_log_callback
        )
        best_acc = trainer.train(dataloader, epochs=config.EPOCHS, model_name=config.MODEL_NAME, log_every=1)

        _, _, y_true, y_pred = validate(model, dataloader["test"], criterion, device)
        print_classification_report(y_true, y_pred, config.CLASSES, "Test")

        export_to_onnx(model, config.MODEL_NAME, config.ONNX_PATH, (3, 32, 32), device)

        trainer.log_final_artifacts(
            dataloader, criterion, device,
            class_names=config.CLASSES,
            checkpoint_path=config.CHECKPOINT,
            onnx_path=config.ONNX_PATH
        )

        print(f"\nИтоговая точность MLP ({optimizer_name.upper()}): {best_acc:.2f}%")
