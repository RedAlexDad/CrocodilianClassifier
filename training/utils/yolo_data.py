#!/usr/bin/env python3
"""
Конвертация bbox-датасета в формат YOLOv8-segment.

Current format: class_id x_center y_center width height (normalized)
Target format: class_id polygon_points (normalized, 8 points = rectangle)
"""

import os
import shutil
import random
from pathlib import Path
from typing import Tuple, List

from configs.config import BASE_DIR as ROOT_DIR


def convert_bbox_to_polygon(x_c: float, y_c: float, w: float, h: float) -> str:
    """Convert bounding box to polygon (rectangle with 4 corners, 8 points)."""
    x1 = x_c - w / 2
    y1 = y_c - h / 2
    x2 = x_c + w / 2
    y2 = y_c + h / 2
    return f"{x1:.6f} {y1:.6f} {x2:.6f} {y1:.6f} {x2:.6f} {y2:.6f} {x1:.6f} {y2:.6f}"


def prepare_dataset(
    src_dir: str = "data/dataset/obj_train_data",
    dst_dir: str = "data/yolo8_segment",
    split: float = 0.9,
    seed: int = 42,
) -> Tuple[int, int]:
    """Convert dataset and return (train_count, val_count)."""
    src = ROOT_DIR / src_dir
    dst = ROOT_DIR / dst_dir

    images = sorted([f for f in os.listdir(src) if f.endswith('.jpeg')])
    random.seed(seed)
    random.shuffle(images)

    split_idx = int(len(images) * split)
    train_images = images[:split_idx]
    val_images = images[split_idx:]

    for split_name, split_imgs in [("train", train_images), ("val", val_images)]:
        print(f"  {split_name}: {len(split_imgs)} images")
        for img_name in split_imgs:
            label_name = img_name.replace('.jpeg', '.txt')
            dst_img = dst / "images" / split_name / img_name
            dst_label = dst / "labels" / split_name / label_name

            dst_img.parent.mkdir(parents=True, exist_ok=True)
            dst_label.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy(src / img_name, dst_img)

            if (src / label_name).exists():
                with open(src / label_name) as f:
                    lines = f.read().strip().split('\n')
                new_lines = []
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls = parts[0]
                        x_c, y_c, w, h = map(float, parts[1:5])
                        polygon = convert_bbox_to_polygon(x_c, y_c, w, h)
                        new_lines.append(f"{cls} {polygon}")
                with open(dst_label, 'w') as f:
                    f.write('\n'.join(new_lines))
            else:
                dst_label.touch()

    print(f"  Total: {len(images)}, Train: {len(train_images)}, Val: {len(val_images)}")
    return len(train_images), len(val_images)