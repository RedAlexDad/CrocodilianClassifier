"""
MLflow интеграция для отслеживания обучения
Хранение артефактов в MinIO (S3)
"""

import io
import os

import mlflow
import numpy as np
import torch
from mlflow.tracking import MlflowClient

MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = "crocodilian-classifier"

S3_BUCKET = os.environ.get("AWS_S3_MLWFL_ARTIFACTS", "crocodilian")
S3_ENDPOINT = os.environ.get("MLFLOW_S3_ENDPOINT_URL", "http://localhost:9000")


def setup_mlflow(experiment_name=None, tracking_uri=None):
    """Настроить MLflow с S3 артефактами"""
    import urllib.request

    uri = tracking_uri or MLFLOW_TRACKING_URI
    experiment = experiment_name or MLFLOW_EXPERIMENT_NAME

    # Check if tracking server is available, fallback to local
    try:
        urllib.request.urlopen(uri, timeout=2)
    except Exception:
        # Fallback to local storage
        local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mlruns")
        uri = local_path
        print(f"MLflow tracking server unavailable, using local storage: {local_path}")

    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(experiment)

    os.environ["AWS_S3_ENDPOINT_URL"] = S3_ENDPOINT
    os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"

    # Enable autolog with traces
    try:
        mlflow.autolog(
            log_models=False,
            silent=True,
            log_traces=True,
        )
    except Exception as e:
        print(f"MLflow autolog: {e}")

    # Enable system metrics logging
    try:
        from mlflow.system_metrics import enable_system_metrics_logging
        enable_system_metrics_logging()
    except Exception as e:
        print(f"System metrics: {e}")

    # Enable tracing
    try:
        mlflow.tracing.enable()
    except Exception as e:
        print(f"Tracing: {e}")

    return mlflow


def log_metrics(epoch, loss, accuracy, phase="train"):
    """Логировать метрики"""
    mlflow.log_metric({f"{phase}_loss": loss, f"{phase}_accuracy": accuracy}, step=epoch)


def log_params(params):
    """Логировать параметры"""
    mlflow.log_params(params)


def log_model_summary(model, model_name):
    """Логировать архитектуру модели"""
    summary = str(model)
    mlflow.log_param(f"{model_name}_architecture", summary[:500])


def log_sample_images(images, labels, class_names, num_samples=5, predictions=None, probabilities=None):
    """Логировать образцы изображений как артефакты с предсказаниями

    Args:
        images: изображения (N, C, H, W) или (N, flattened) для MLP
        labels: истинные метки
        class_names: названия классов
        num_samples: количество образцов на класс
        predictions: предсказанные метки (опционально)
        probabilities: вероятности предсказаний (опционально)
    """
    import matplotlib.pyplot as plt

    images = np.array(images)

    if images.ndim == 2:
        size = images.shape[1]
        if size % 3 == 0:
            channels = 3
            flat_size = size // channels
            side = int(np.sqrt(flat_size))
            if side * side == flat_size:
                images = images.reshape(-1, channels, side, side)

    if images.ndim != 4 or images.shape[1] not in (1, 3):
        print(f"  log_sample_images: invalid image shape {images.shape}")
        return

    unique_labels = sorted(list(set(labels)))
    num_classes = len(unique_labels)

    samples_per_class = {label: [] for label in unique_labels}
    for idx, label in enumerate(labels):
        if len(samples_per_class[label]) < num_samples:
            samples_per_class[label].append(idx)

    if not any(samples_per_class.values()):
        return

    fig, axes = plt.subplots(
        num_classes, num_samples, figsize=(3 * num_samples, 3 * num_classes)
    )
    if num_classes == 1:
        axes = [axes]
    if num_samples == 1:
        axes = [[ax] for ax in axes]

    for row, label in enumerate(unique_labels):
        indices = samples_per_class[label][:num_samples]
        for col, idx in enumerate(indices):
            if num_classes > 1:
                ax = axes[row][col]
            else:
                ax = axes[col]
            img = images[idx].copy()

            if img.shape[0] == 3:
                img = img.transpose(1, 2, 0)

            img = img.clip(0, 1)

            ax.imshow(img)

            true_name = class_names[label]
            title = true_name

            if predictions is not None:
                pred = predictions[idx]
                pred_name = class_names[pred]
                is_correct = pred == label

                if probabilities is not None:
                    conf = probabilities[idx][pred] * 100
                    title = f"True: {true_name}\nPred: {pred_name}\nConf: {conf:.1f}%"
                    color = "green" if is_correct else "red"
                else:
                    title = f"True: {true_name}\nPred: {pred_name}\n{'OK' if is_correct else 'X'}"
                    color = "green" if is_correct else "red"

                ax.set_title(title, color=color, fontsize=8)
            else:
                ax.set_title(title, fontsize=8)

            ax.axis("off")

    plt.tight_layout()

    temp_path = "/tmp/sample_images.png"
    plt.savefig(temp_path, format="png", dpi=100)
    plt.close()

    mlflow.log_artifact(temp_path)


def log_confusion_matrix(y_true, y_pred, class_names):
    """Логировать матрицу ошибок"""
    from sklearn.metrics import confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns

    cm = confusion_matrix(y_true, y_pred)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()

    mlflow.log_artifact(buf.getvalue(), "confusion_matrix.png")


def log_training_plot(history, model_name):
    """Логировать график обучения"""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history["train_loss"], label="Train")
    axes[0].plot(history["val_loss"], label="Val")
    axes[0].set_title(f"{model_name} - Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()

    axes[1].plot(history["train_acc"], label="Train")
    axes[1].plot(history["val_acc"], label="Val")
    axes[1].set_title(f"{model_name} - Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].legend()

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()

    mlflow.log_artifact(buf.getvalue(), "training_plot.png")


def save_model_for_mlflow(model, model_path, model_name):
    """Сохранить модель для MLflow"""
    from utils import export_to_onnx

    torch.save(model.state_dict(), model_path)
    mlflow.log_artifact(model_path, "model.pth")


def download_latest_model(model_name, output_path, experiment_name=None):
    """Скачать последнюю модель из MLflow"""
    client = MlflowClient()

    exp_name = experiment_name or MLFLOW_EXPERIMENT_NAME
    exp = mlflow.get_experiment_by_name(exp_name)

    if not exp:
        raise ValueError(f"Experiment {exp_name} not found")

    runs = client.search_runs(exp.experiment_id, "metrics.val_accuracy DESC", max_results=1)

    if not runs:
        raise ValueError("No runs found")

    best_run = runs[0]

    for artifact in client.list_artifacts(best_run.info.run_id, "model"):
        if artifact.path.endswith(".pth"):
            client.download_artifacts(best_run.info.run_id, artifact.path, dst_path=output_path)
            return output_path

    return None
