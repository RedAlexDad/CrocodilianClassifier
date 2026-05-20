#!/usr/bin/env python3
"""
Конвертация датасетов в формат YOLOv8-segment.

1. bbox → polygon (rectangle, 8 points)
2. COCO RLE → polygon (реальные маски из Roboflow)
"""

import json
import os
import shutil
import random
import zipfile
from pathlib import Path
from typing import Tuple, List

import cv2
import numpy as np
from pycocotools import mask as maskUtils

from configs.config import BASE_DIR as ROOT_DIR


CLASS_NAME_TO_ID = {
    "alligator": 0,
    "cayman": 1,
    "crocodile": 2,
}


def convert_bbox_to_polygon(x_c: float, y_c: float, w: float, h: float) -> str:
    """Convert bounding box to polygon (rectangle with 4 corners, 8 points)."""
    x1 = x_c - w / 2
    y1 = y_c - h / 2
    x2 = x_c + w / 2
    y2 = y_c + h / 2
    return f"{x1:.6f} {y1:.6f} {x2:.6f} {y1:.6f} {x2:.6f} {y2:.6f} {x1:.6f} {y2:.6f}"


def rle_to_yolo_polygon(rle: dict, img_w: int, img_h: int) -> str:
    """Convert COCO RLE annotation to YOLO polygon string (normalized)."""
    binary_mask = maskUtils.decode(rle)
    contours, _ = cv2.findContours(
        binary_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return ""

    total_fg = int(binary_mask.sum())
    min_area = max(total_fg * 0.005, 1)

    poly_mask = np.zeros((img_h, img_w), dtype=np.uint8)
    points = []

    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        perim = cv2.arcLength(c, True)
        epsilon = max(0.001 * perim, 0.5)
        approx = cv2.approxPolyDP(c, epsilon=epsilon, closed=True)
        pts = approx.reshape(-1, 2).astype(np.int32)
        cv2.fillPoly(poly_mask, [pts.reshape(-1, 1, 2)], 1)
        points.append(pts)

    if not points:
        return ""

    all_pts = np.concatenate(points, axis=0)
    all_pts = all_pts.astype(float)
    all_pts[:, 0] /= img_w
    all_pts[:, 1] /= img_h
    all_pts = np.clip(all_pts, 0.0, 1.0)

    return " ".join(f"{x:.6f} {y:.6f}" for x, y in all_pts)


def prepare_coco_dataset(
    dst_dir: str = "data/yolo_seg_v2",
    split: float = 0.9,
    seed: int = 42,
) -> Tuple[int, int]:
    """Read Segment1_*.zip (COCO RLE), convert to YOLO polygon.

    Returns (train_count, val_count).
    """
    dst = ROOT_DIR / dst_dir
    zip_patterns = {
        "data/Segment1_0.zip": "cayman",
        "data/Segment1_1.zip": "crocodile",
        "data/Segment1_2.zip": "alligator",
    }

    all_records = []

    for zip_rel, class_name in zip_patterns.items():
        zip_path = ROOT_DIR / zip_rel
        with zipfile.ZipFile(zip_path) as z:
            with z.open("train/_annotations.coco.json") as f:
                coco = json.load(f)

        cat_name_to_id = {c["name"]: c["id"] for c in coco["categories"]}
        target_cat_id = cat_name_to_id[class_name]
        yolo_class_id = CLASS_NAME_TO_ID[class_name]

        img_index = {i["id"]: i for i in coco["images"]}
        anns_by_img: dict = {}
        for ann in coco["annotations"]:
            if ann["category_id"] != target_cat_id:
                continue
            img_id = ann["image_id"]
            if img_id not in anns_by_img:
                anns_by_img[img_id] = []
            anns_by_img[img_id].append(ann)

        img_ids = sorted(img_index.keys())
        random.seed(seed)
        random.shuffle(img_ids)

        for img_id in img_ids:
            img_info = img_index[img_id]
            anns = anns_by_img.get(img_id, [])
            if not anns:
                continue
            all_records.append((zip_path, img_info, anns, yolo_class_id))

    random.seed(seed)
    random.shuffle(all_records)

    split_idx = int(len(all_records) * split)
    splits = [("train", all_records[:split_idx]), ("val", all_records[split_idx:])]

    for split_name, records in splits:
        print(f"  {split_name}: {len(records)} images")
        for zip_path, img_info, anns, yolo_class_id in records:
            img_name = img_info["file_name"]
            label_name = img_name.rsplit(".", 1)[0] + ".txt"
            img_w = img_info["width"]
            img_h = img_info["height"]

            dst_img = dst / "images" / split_name / img_name
            dst_label = dst / "labels" / split_name / label_name
            dst_img.parent.mkdir(parents=True, exist_ok=True)
            dst_label.parent.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path) as z:
                img_path_in_zip = f"train/{img_name}"
                try:
                    with z.open(img_path_in_zip) as src_f:
                        with open(dst_img, "wb") as dst_f:
                            dst_f.write(src_f.read())
                except KeyError:
                    continue

            polygon_lines = []
            for ann in anns:
                poly_str = rle_to_yolo_polygon(
                    ann["segmentation"], img_w, img_h
                )
                if poly_str:
                    polygon_lines.append(f"{yolo_class_id} {poly_str}")

            with open(dst_label, "w") as f:
                f.write("\n".join(polygon_lines))

    total = len(all_records)
    train_c = split_idx
    val_c = total - split_idx
    print(f"  Total: {total}, Train: {train_c}, Val: {val_c}")
    return train_c, val_c


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