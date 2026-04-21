"""
Загрузка данных и создание dataloader
"""

from PIL import Image
from glob import glob
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms as T
from pathlib import Path


def load_data(data_dir, classes, image_size, test_ratio=0.2):
    """
    Загрузка изображений из папок

    Args:
        data_dir: Путь к директории с данными
        classes: Список классов
        image_size: Размер изображения
        test_ratio: Доля тестовой выборки

    Returns:
        train_X, train_y, test_X, test_y
    """
    data_dir = Path(data_dir)
    images = []
    images_t = []
    classes_list = []
    classes_t = []

    print("=" * 60)
    print("Загрузка данных...")
    print("=" * 60)

    for class_idx, class_name in enumerate(classes):
        path_class = data_dir / class_name / "*.*"
        all_photos = list(glob(str(path_class)))
        print(f"Класс '{class_name}': найдено {len(all_photos)} изображений")

        for i, photo in enumerate(all_photos, 1):
            try:
                img = Image.open(photo).convert("RGB")
                img = img.resize((image_size, image_size), Image.LANCZOS)

                if i > int(len(all_photos) * (1 - test_ratio)):
                    images_t.append(np.asarray(img))
                    classes_t.append(class_idx)
                else:
                    images.append(np.asarray(img))
                    classes_list.append(class_idx)
            except Exception as e:
                print(f"  ⚠️ Ошибка {photo}: {e}")

    train_X = np.array(images)
    train_y = np.array(classes_list)
    test_X = np.array(images_t)
    test_y = np.array(classes_t)

    print(f"\n=== Статистика ===")
    print(f"Train: {len(train_X)} изображений")
    print(f"Test: {len(test_X)} изображений")

    if len(train_X) == 0:
        print("\n❌ Нет данных для обучения!")
        print(f"Проверьте папки: {data_dir}/")
        raise ValueError("Нет данных для обучения")

    return train_X, train_y, test_X, test_y


class AugmentedDataset(Dataset):
    """Dataset с аугментацией"""

    def __init__(self, images, labels, transform=None):
        self.images = images
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img = self.images[idx]
        label = self.labels[idx]

        if self.transform:
            img = self.transform(img)

        return (
            img,
            F.one_hot(
                torch.tensor(label, dtype=torch.int64),
                num_classes=len(self.labels.unique()) if hasattr(self.labels, "unique") else 3,
            ).float(),
        )


class SimpleDataset(Dataset):
    """Простой dataset без аугментации (для MLP)"""

    def __init__(self, images, labels, transform=None, flatten=True):
        self.images = images
        self.labels = labels
        self.transform = transform
        self.flatten = flatten

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img = self.images[idx]
        label = self.labels[idx]

        if self.transform:
            img = self.transform(img)

        if self.flatten:
            img = img.flatten()

        return img, label


def create_dataloaders(train_X, train_y, test_X, test_y, config, model_type="cnn"):
    """
    Создание dataloader для разных типов моделей

    Args:
        train_X, train_y, test_X, test_y: Данные
        config: Конфигурация
        model_type: Тип модели ('mlp', 'cnn', 'mobilenet')

    Returns:
        dataloader: dict с 'train' и 'test' DataLoader
    """
    batch_size = getattr(config, "BATCH_SIZE", 32)

    if model_type == "mlp":
        # MLP требует flatten изображения
        transform = T.Compose(
            [
                T.ToPILImage(),
                T.ToTensor(),
            ]
        )

        train_dataset = SimpleDataset(train_X, train_y, transform=transform, flatten=True)
        test_dataset = SimpleDataset(test_X, test_y, transform=transform, flatten=True)

    elif model_type == "cnn":
        # CNN с аугментацией
        train_transform = T.Compose(
            [
                T.ToPILImage(),
                T.RandomHorizontalFlip(p=0.5),
                T.RandomRotation(15),
                T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                T.ToTensor(),
            ]
        )

        test_transform = T.Compose(
            [
                T.ToPILImage(),
                T.ToTensor(),
            ]
        )

        train_dataset = AugmentedDataset(train_X, train_y, transform=train_transform)
        test_dataset = AugmentedDataset(test_X, test_y, transform=test_transform)

    elif model_type == "mobilenet":
        # MobileNet требует размер 224x224 и нормализацию ImageNet
        mean = getattr(config, "IMAGENET_MEAN", [0.485, 0.456, 0.406])
        std = getattr(config, "IMAGENET_STD", [0.229, 0.224, 0.225])
        image_size = getattr(config, "IMAGE_SIZE", 224)

        train_transform = T.Compose(
            [
                T.ToPILImage(),
                T.Resize((image_size, image_size)),
                T.RandomHorizontalFlip(p=0.5),
                T.RandomRotation(15),
                T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                T.ToTensor(),
                T.Normalize(mean=mean, std=std),
            ]
        )

        test_transform = T.Compose(
            [
                T.ToPILImage(),
                T.Resize((image_size, image_size)),
                T.ToTensor(),
                T.Normalize(mean=mean, std=std),
            ]
        )

        train_dataset = AugmentedDataset(train_X, train_y, transform=train_transform)
        test_dataset = AugmentedDataset(test_X, test_y, transform=test_transform)
    else:
        raise ValueError(f"Неизвестный тип модели: {model_type}")

    dataloader = {
        "train": DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=True
        ),
        "test": DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False, num_workers=0, drop_last=False
        ),
    }

    print(f"Train batches: {len(dataloader['train'])}")
    print(f"Test batches: {len(dataloader['test'])}")

    return dataloader
