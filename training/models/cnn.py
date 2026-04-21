"""
CNN модель для классификации изображений
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class Normalize(nn.Module):
    """Слой нормализации"""

    def __init__(self, mean, std):
        super().__init__()
        self.register_buffer("mean", torch.tensor(mean).view(1, -1, 1, 1))
        self.register_buffer("std", torch.tensor(std).view(1, -1, 1, 1))

    def forward(self, x):
        return (x - self.mean) / self.std


class GlobalMaxPool2d(nn.Module):
    """Глобальный max pooling"""

    def __init__(self):
        super().__init__()

    def forward(self, x):
        return F.adaptive_max_pool2d(x, output_size=1).flatten(1)


class CNNModel(nn.Module):
    """
    Самописная CNN для классификации изображений 32x32

    Архитектура:
        Normalize -> Conv2d -> ReLU -> Dropout2d ->
        Conv2d -> ReLU -> AvgPool2d -> Dropout2d ->
        Flatten -> Linear -> Output
    """

    def __init__(self, hidden_size=32, num_classes=3, dropout=0.3):
        super(CNNModel, self).__init__()

        # Нормализация (статистики CIFAR-100)
        self.normalize = Normalize(mean=[0.5074, 0.4867, 0.4411], std=[0.2011, 0.1987, 0.2025])

        self.seq = nn.Sequential(
            # Первый блок: уменьшение размерности через stride
            nn.Conv2d(3, hidden_size, 3, stride=4),
            nn.ReLU(),
            nn.Dropout2d(p=dropout),
            # Второй блок: conv + pooling
            nn.Conv2d(hidden_size, hidden_size * 2, 3, stride=1, padding=1),
            nn.ReLU(),
            nn.AvgPool2d(4),
            nn.Dropout2d(p=dropout),
            # Классификатор
            nn.Flatten(),
            nn.Linear(hidden_size * 8, num_classes),
        )

    def forward(self, x):
        # Приведение к NCHW формату
        if x.dim() == 4 and x.shape[3] == 3:
            x = x.permute(0, 3, 1, 2)
        return self.seq(self.normalize(x))


def create_cnn(config, num_classes):
    """Фабричная функция для создания CNN"""
    return CNNModel(hidden_size=config.HIDDEN_SIZE, num_classes=num_classes, dropout=config.DROPOUT)
