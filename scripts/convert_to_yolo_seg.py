#!/usr/bin/env python3
"""Convert YOLO detection dataset to YOLOv8 segmentation format.

Current format: class_id x_center y_center width height (normalized)
Target format: class_id polygon_points (normalized, space-separated)
"""

import os
import shutil
import random
from pathlib import Path

SRC_DIR = Path("data/dataset/obj_train_data")
DST_DIR = Path("data/yolo8_segment")
SPLIT = 0.9  # 90% train, 10% val

def convert_bbox_to_polygon(x_c, y_c, w, h):
    """Convert bounding box to polygon (rectangle with 4 corners)."""
    x1 = x_c - w / 2
    y1 = y_c - h / 2
    x2 = x_c + w / 2
    y2 = y_c + h / 2
    return f"{x1:.6f} {y1:.6f} {x2:.6f} {y1:.6f} {x2:.6f} {y2:.6f} {x1:.6f} {y2:.6f}"

def convert_dataset():
    images = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.jpeg')])
    random.seed(42)
    random.shuffle(images)

    split_idx = int(len(images) * SPLIT)
    train_images = images[:split_idx]
    val_images = images[split_idx:]

    for split_name, split_images in [("train", train_images), ("val", val_images)]:
        print(f"Processing {split_name}: {len(split_images)} images")

        for img_name in split_images:
            label_name = img_name.replace('.jpeg', '.txt')
            src_img = SRC_DIR / img_name
            src_label = SRC_DIR / label_name

            dst_img = DST_DIR / "images" / split_name / img_name
            dst_label = DST_DIR / "labels" / split_name / label_name

            shutil.copy(src_img, dst_img)

            if src_label.exists():
                with open(src_label) as f:
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
                open(dst_label, 'w').close()

    print(f"\nTotal images: {len(images)}")
    print(f"Train: {len(train_images)}, Val: {len(val_images)}")

if __name__ == "__main__":
    convert_dataset()