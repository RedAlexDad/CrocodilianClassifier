"""
MobileNetV2 модель для классификации изображений
Transfer Learning с предобученными весами ImageNet
"""

import torch
import torch.nn as nn
from torchvision import models


class MobileNetModel(nn.Module):
    """
    MobileNetV2 с Transfer Learning

    Архитектура:
        MobileNetV2 Backbone (ImageNet weights) ->
        Dropout -> Linear (num_classes)
    """

    def __init__(self, num_classes=3, pretrained=True, dropout=0.3):
        super(MobileNetModel, self).__init__()

        # Загрузка предобученной модели
        weights = models.MobileNet_V2_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.mobilenet_v2(weights=weights)

        # Замена классификатора
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        # Приведение к NCHW формату если нужно
        if x.dim() == 4 and x.shape[3] == 3:
            x = x.permute(0, 3, 1, 2)
        return self.backbone(x)

    def freeze_base(self):
        """Заморозить базовую модель (обучать только классификатор)"""
        for param in self.backbone.features.parameters():
            param.requires_grad = False
        # Классификатор оставляем размороженным
        for param in self.backbone.classifier.parameters():
            param.requires_grad = True

    def freeze_all(self):
        """Заморозить все параметры"""
        for param in self.parameters():
            param.requires_grad = False

    def unfreeze_all(self):
        """Разморозить все параметры"""
        for param in self.parameters():
            param.requires_grad = True

    def unfreeze_last_n_layers(self, n=20):
        """
        Разморозить последние N слоёв для fine-tuning

        Args:
            n: Количество размораживаемых слоёв (с конца)
        """
        self.freeze_all()

        # Получаем все параметры
        params = list(self.named_parameters())
        total = len(params)

        # Размораживаем последние N
        for i, (name, param) in enumerate(params):
            if i >= total - n:
                param.requires_grad = True

        return total - n, n  # frozen_count, unfrozen_count


def create_mobilenet(config, num_classes):
    """Фабричная функция для создания MobileNetV2"""
    return MobileNetModel(num_classes=num_classes, pretrained=config.PRETRAINED, dropout=0.3)
