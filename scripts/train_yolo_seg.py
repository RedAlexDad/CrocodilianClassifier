#!/usr/bin/env python3
"""
Обучение YOLOv8-segment с MLflow tracking.
Использование: python3 scripts/train_yolo_seg.py [--epochs 50] [--device cuda]
"""

import argparse
import os
import sys
import shutil
import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import mlflow
from training.utils.mlflow_utils import setup_mlflow


def create_dataset_yaml(dst_dir):
    """Создать YAML конфигурацию датасета для YOLO."""
    yaml_content = f"""
path: {dst_dir}
train: images/train
val: images/val

nc: 3
names:
  0: alligator
  1: cayman
  2: crocodile
"""
    yaml_path = dst_dir / "dataset.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content.strip())
    return yaml_path


def run_training(epochs=50, imgsz=640, device="cuda", project="yolo8_segment"):
    """Запустить обучение YOLOv8-segment."""
    base_dir = Path(__file__).parent.parent
    src_dir = base_dir / "data" / "yolo8_segment"
    yaml_path = create_dataset_yaml(src_dir)

    model = YOLO("yolov8n-seg.pt")

    if device == "cpu" or not torch.cuda.is_available():
        device_str = "cpu"
    else:
        device_str = "0"  # YOLO uses "0" for first GPU

    experiment_name = "yolo8-segment"

    try:
        urllib.request.urlopen("http://localhost:5000", timeout=2)
        mlflow_tracking_uri = "http://localhost:5000"
    except Exception:
        mlflow_tracking_uri = str(base_dir / "mlruns")
        print(f"MLflow server unavailable, using local: {mlflow_tracking_uri}")

    mlflow = setup_mlflow(
        experiment_name=experiment_name,
        tracking_uri=mlflow_tracking_uri,
    )

    with mlflow.start_run(run_name=f"yolo8n-seg-e{epochs}"):
        mlflow.log_params({
            "model": "YOLOv8n-segment",
            "epochs": epochs,
            "imgsz": imgsz,
            "device": device_str,
            "dataset": "crocodilian_segmentation",
            "num_classes": 3,
            "classes": "alligator, cayman, crocodile",
            "train_samples": len(list((src_dir / "images" / "train").glob("*.jpeg"))),
            "val_samples": len(list((src_dir / "images" / "val").glob("*.jpeg"))),
        })

        results = model.train(
            data=str(yaml_path),
            epochs=epochs,
            imgsz=imgsz,
            device=device_str,
            batch=4,
            project=str(base_dir / project),
            name="train",
            exist_ok=True,
            verbose=True,
            amp=True,
            plots=True,
            save=True,
            save_period=10,
        )

        best_model_path = base_dir / project / "train" / "weights" / "best.pt"
        last_model_path = base_dir / project / "train" / "weights" / "last.pt"

        if best_model_path.exists():
            mlflow.log_artifact(str(best_model_path), "model")
        if last_model_path.exists():
            mlflow.log_artifact(str(last_model_path), "model_last")

        export_dir = base_dir / project / "train" / "weights"
        if (export_dir / "best.pt").exists():
            shutil.copy(export_dir / "best.pt", base_dir / "data" / "models" / "yolo8n_seg_best.pt")

        results_plot = base_dir / project / "train" / "results.png"
        if results_plot.exists():
            mlflow.log_artifact(str(results_plot), "artifacts")

        if hasattr(results, "results_dict"):
            metrics = results.results_dict
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value)

        print("\nTraining complete!")
        print(f"Best model: {best_model_path}")
        print(f"Results: {base_dir / project / 'train'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8-segment")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    run_training(epochs=args.epochs, imgsz=args.imgsz, device=args.device)