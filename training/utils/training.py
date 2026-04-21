"""
Функции для обучения моделей
"""

import torch
import torch.nn as nn
import numpy as np
from tqdm.auto import tqdm
from sklearn.metrics import classification_report


def train_epoch(model, dataloader, criterion, optimizer, device, scheduler=None):
    """
    Обучение за одну эпоху

    Returns:
        avg_loss, avg_acc
    """
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)

        # Обработка меток: one-hot или скаляры
        if labels.dim() == 2 and labels.size(1) > 1:
            # One-hot encoded
            loss = criterion(outputs, labels)
            _, label_class = labels.max(1)
        else:
            # Scalar labels
            loss = criterion(outputs, labels.long())
            label_class = labels.long()

        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(label_class).sum().item()

    if scheduler is not None:
        scheduler.step()

    avg_loss = total_loss / len(dataloader)
    avg_acc = 100.0 * correct / total

    return avg_loss, avg_acc


def validate(model, dataloader, criterion, device):
    """
    Валидация модели

    Returns:
        avg_loss, avg_acc, y_true, y_pred
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    y_pred = []
    y_true = []

    with torch.no_grad():
        for inputs, labels in dataloader:
            if inputs.size(0) <= 1:
                continue

            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)

            # Обработка меток: one-hot или скаляры
            if labels.dim() == 2 and labels.size(1) > 1:
                # One-hot encoded
                loss = criterion(outputs, labels)
                _, label_class = labels.max(1)
            else:
                # Scalar labels
                loss = criterion(outputs, labels.long())
                label_class = labels.long()

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(label_class).sum().item()

            y_pred.append(outputs.cpu().numpy())
            # Сохраняем как one-hot для classification_report
            if labels.dim() == 1 or labels.size(1) == 1:
                y_true.append(
                    torch.nn.functional.one_hot(labels.long(), num_classes=3).cpu().numpy()
                )
            else:
                y_true.append(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    avg_acc = 100.0 * correct / total

    y_true = np.concatenate(y_true) if y_true else np.array([])
    y_pred = np.concatenate(y_pred) if y_pred else np.array([])

    return avg_loss, avg_acc, y_true, y_pred


class Trainer:
    """
    Класс для обучения модели с поддержкой:
        - Сохранения лучшей модели
        - Логирования метрик
        - MLflow integration в реальном времени
        - Двухэтапного обучения (для transfer learning)
    """

    def __init__(self, model, criterion, optimizer, device, checkpoint_path=None, scheduler=None,
                 mlflow_callback=None):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.checkpoint_path = checkpoint_path
        self.best_acc = 0.0
        self.best_state = None
        self.history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
        self.mlflow_callback = mlflow_callback

    def train(self, dataloader, epochs, model_name="Model", log_every=10):
        """
        Обучение модели

        Args:
            dataloader: dict с 'train' и 'test' DataLoader
            epochs: Количество эпох
            model_name: Название модели для логов
            log_every: Частота логирования
        """
        # Попытка импортировать MLflow
        mlflow_available = False
        try:
            import mlflow
            mlflow_available = True
        except ImportError:
            pass

        pbar = tqdm(total=epochs, desc=f"Обучение {model_name}")

        for epoch in range(epochs):
            # Training
            train_loss, train_acc = train_epoch(
                self.model,
                dataloader["train"],
                self.criterion,
                self.optimizer,
                self.device,
                self.scheduler,
            )

            # Validation
            val_loss, val_acc, _, _ = validate(
                self.model, dataloader["test"], self.criterion, self.device
            )

            # Сохранение истории
            self.history["train_loss"].append(train_loss)
            self.history["train_acc"].append(train_acc)
            self.history["val_loss"].append(val_loss)
            self.history["val_acc"].append(val_acc)

            # Сохранение лучшей модели
            if val_acc > self.best_acc:
                self.best_acc = val_acc
                self.best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                if self.checkpoint_path:
                    torch.save(self.best_state, self.checkpoint_path)

            pbar.update(1)

            # MLflow логирование в реальном времени
            if mlflow_available and (epoch + 1) % log_every == 0 or epoch == 0:
                try:
                    import mlflow
                    import psutil
                    import torch

                    # Метрики обучения
                    mlflow.log_metric("train_loss", train_loss, step=epoch)
                    mlflow.log_metric("train_acc", train_acc, step=epoch)
                    mlflow.log_metric("val_loss", val_loss, step=epoch)
                    mlflow.log_metric("val_acc", val_acc, step=epoch)
                    mlflow.log_metric("best_acc", self.best_acc, step=epoch)

                    # System metrics
                    mlflow.log_metric("system_cpu_percent", psutil.cpu_percent(), step=epoch)
                    mlflow.log_metric("system_memory_percent", psutil.virtual_memory().percent, step=epoch)
                    mlflow.log_metric("system_disk_percent", psutil.disk_usage('/').percent, step=epoch)

                    # GPU metrics
                    if torch.cuda.is_available():
                        mlflow.log_metric("gpu_memory_allocated_mb", torch.cuda.memory_allocated() / 1024**2, step=epoch)
                        mlflow.log_metric("gpu_memory_reserved_mb", torch.cuda.memory_reserved() / 1024**2, step=epoch)
                        for i in range(torch.cuda.device_count()):
                            mlflow.log_metric(f"gpu_{i}_utilization", torch.cuda.utilization(i), step=epoch)
                except Exception:
                    pass

            # CustomMLflow callback
            if self.mlflow_callback is not None:
                try:
                    self.mlflow_callback(epoch + 1, val_loss, val_acc)
                except Exception:
                    pass

            if (epoch + 1) % log_every == 0 or epoch == 0:
                print(f"\n{model_name} | Epoch {epoch+1}/{epochs}")
                print(f"  Train: Loss={train_loss:.4f}, Acc={train_acc:.2f}%")
                print(f"  Val:   Loss={val_loss:.4f}, Acc={val_acc:.2f}%")
                print(f"  Best:  {self.best_acc:.2f}%")

        pbar.close()

        # Загрузка лучшей модели
        if self.best_state is not None:
            self.model.load_state_dict(self.best_state)

        # Сохранить артефакты после обучения
        if mlflow_available:
            try:
                import mlflow
                import matplotlib.pyplot as plt

                # График обучения
                fig, axes = plt.subplots(1, 2, figsize=(12, 4))

                axes[0].plot(self.history["train_loss"], label="Train")
                axes[0].plot(self.history["val_loss"], label="Val")
                axes[0].set_title(f"{model_name} - Loss")
                axes[0].set_xlabel("Epoch")
                axes[0].set_ylabel("Loss")
                axes[0].legend()

                axes[1].plot(self.history["train_acc"], label="Train")
                axes[1].plot(self.history["val_acc"], label="Val")
                axes[1].set_title(f"{model_name} - Accuracy")
                axes[1].set_xlabel("Epoch")
                axes[1].set_ylabel("Accuracy")
                axes[1].legend()

                plt.tight_layout()
                plt.savefig("/tmp/training_plot.png", dpi=100)
                plt.close()
                mlflow.log_artifact("/tmp/training_plot.png", "plots")
            except Exception:
                pass

        print(f"\n✓ {model_name} завершено! Лучшая точность: {self.best_acc:.2f}%")

        return self.best_acc

    def train_two_stage(
        self,
        dataloader,
        model_name="Model",
        epochs_stage1=30,
        epochs_stage2=100,
        optimizer_stage2=None,
        scheduler_stage2=None,
        log_every=5,
    ):
        """
        Двухэтапное обучение (для transfer learning)

        Этап 1: Обучение только классификатора (база заморожена)
        Этап 2: Fine-tuning с разморозкой части слоёв
        """
        print(f"\n{'='*60}")
        print(f"ЭТАП 1: Обучение классификатора ({epochs_stage1} эпох)")
        print(f"{'='*60}")

        # Этап 1
        self.train(
            dataloader, epochs_stage1, model_name=f"{model_name} Этап 1", log_every=log_every
        )

        print(f"\n{'='*60}")
        print(f"ЭТАП 2: Fine-tuning ({epochs_stage2} эпох)")
        print(f"{'='*60}")

        # Обновление оптимизатора для этапа 2
        if optimizer_stage2 is not None:
            self.optimizer = optimizer_stage2
        if scheduler_stage2 is not None:
            self.scheduler = scheduler_stage2

        # Этап 2
        self.train(
            dataloader, epochs_stage2, model_name=f"{model_name} Этап 2", log_every=log_every
        )

        return self.best_acc


def print_classification_report(y_true, y_pred, class_names, part_name=""):
    """Вывод отчёта о классификации"""
    if len(y_true) == 0 or len(y_pred) == 0:
        print(f"{part_name}: Нет данных для отчёта")
        return

    print(f"\n{part_name.upper()}")
    print(
        classification_report(
            y_true.argmax(axis=-1), y_pred.argmax(axis=-1), digits=4, target_names=class_names
        )
    )
