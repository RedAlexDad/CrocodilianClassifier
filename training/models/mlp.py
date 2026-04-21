"""
MLP модель для классификации изображений
"""

import torch
import torch.nn as nn


class MLPModel(nn.Module):
    """
    Многослойный перцептрон для классификации изображений

    Архитектура:
        Input -> [Linear -> BatchNorm -> ReLU -> Dropout] x N -> Linear -> Output
    """

    def __init__(
        self, input_size=32 * 32 * 3, hidden_layers=[512, 256, 128], num_classes=3, dropout=0.3
    ):
        super(MLPModel, self).__init__()

        layers = []
        prev_size = input_size

        for hidden_size in hidden_layers:
            layers.extend(
                [
                    nn.Linear(prev_size, hidden_size),
                    # nn.BatchNorm1d(hidden_size),
                    nn.ReLU(),
                    # nn.Dropout(dropout),
                ]
            )
            prev_size = hidden_size

        layers.append(nn.Linear(prev_size, num_classes))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        # Flatten: (N, H, W, C) -> (N, H*W*C)
        if x.dim() == 4:
            if x.shape[3] == 3:  # NHWC
                x = x.permute(0, 3, 1, 2)  # NCHW
            x = x.flatten(1)
        elif x.dim() == 3:  # NCHW
            x = x.flatten(1)
        return self.network(x)


def create_mlp(config, num_classes):
    """Фабричная функция для создания MLP"""
    return MLPModel(
        input_size=config.INPUT_SIZE,
        hidden_layers=config.HIDDEN_LAYERS,
        num_classes=num_classes,
        dropout=config.DROPOUT,
    )
