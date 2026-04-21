"""
Обучение CNN модели
"""

import torch
import torch.nn as nn
from configs import CNNConfig
from models import CNNModel
from utils import (
    setup_mlflow,
    log_params,
    log_metrics,
    log_sample_images,
    load_data,
    create_dataloaders,
    Trainer,
    export_to_onnx,
    get_device,
    set_seed,
    validate,
    print_classification_report,
)


def train_cnn(optimizer_name="sgd", seed=42, epochs=None, lr=None):
    """Обучение CNN модели"""
    print("\n" + "=" * 60)
    print("Обучение CNN модели")
    print("=" * 60)

    config = CNNConfig()
    config.setup_dirs()
    device = get_device()
    set_seed(seed)

    # MLflow setup with single experiment for all models
    import mlflow
    setup_mlflow(experiment_name="crocodilian_classifier")
    run_name = f"cnn_{optimizer_name}_e{epochs or config.EPOCHS}_s{seed}"

    with mlflow.start_run(run_name=run_name):
        log_params({
            "model": "CNN",
            "optimizer": optimizer_name,
            "seed": seed,
            "epochs": epochs or config.EPOCHS,
            "lr": lr or config.LEARNING_RATE,
            "batch_size": config.BATCH_SIZE,
            "dropout": config.DROPOUT,
            "image_size": config.IMAGE_SIZE,
        })

        if epochs is not None:
            config.EPOCHS = epochs
        if lr is not None:
            config.LEARNING_RATE = lr

        train_X, train_y, test_X, test_y = load_data(
            config.DATA_DIR, config.CLASSES, image_size=config.IMAGE_SIZE
        )

        dataloader = create_dataloaders(train_X, train_y, test_X, test_y, config, model_type="cnn")

        model = CNNModel(
            hidden_size=config.HIDDEN_SIZE, num_classes=len(config.CLASSES), dropout=config.DROPOUT
        ).to(device)

        print(f"\nАрхитектура CNN:")
        print(model)

        criterion = nn.CrossEntropyLoss(label_smoothing=config.LABEL_SMOOTHING)

        from .train_mlp import get_optimizer

        optimizer = get_optimizer(
            optimizer_name, model.parameters(), config.LEARNING_RATE, config.WEIGHT_DECAY
        )
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=240, gamma=0.5)

        print(f"\nОптимизатор: {optimizer_name.upper()}")
        print(f"Learning rate: {config.LEARNING_RATE}")
        print(f"Эпох: {config.EPOCHS}")

        def mlflow_log_callback(epoch, loss, acc):
            """Callback для MLflow логирования"""
            import mlflow
            mlflow.log_metric("val_loss", loss, step=epoch)
            mlflow.log_metric("val_acc", acc, step=epoch)

        trainer = Trainer(
            model, criterion, optimizer, device,
            checkpoint_path=config.CHECKPOINT, scheduler=scheduler,
            mlflow_callback=mlflow_log_callback
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
            (3, config.IMAGE_SIZE, config.IMAGE_SIZE),
            device,
        )

        trainer.log_final_artifacts(
            dataloader, criterion, device,
            class_names=config.CLASSES,
            checkpoint_path=config.CHECKPOINT,
            onnx_path=config.ONNX_PATH
        )

        print(f"\nИтоговая точность CNN ({optimizer_name.upper()}): {best_acc:.2f}%")
    return best_acc
