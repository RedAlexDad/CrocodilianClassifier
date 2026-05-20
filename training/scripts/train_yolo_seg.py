#!/usr/bin/env python3
"""
Обучение YOLOv8-segment с MLflow tracking.

Использование:
    python3 main.py --task segment --model yolov8n-seg --optimizer SGD --epochs 50 --batch 4
    python3 main.py --task segment --model yolov8s-seg --optimizer SGD --lr 0.01 --epochs 100 --batch 8
"""

import argparse
import os
import shutil
import urllib.request
from pathlib import Path

import torch
from ultralytics.utils import SETTINGS
SETTINGS["mlflow"] = False
from ultralytics import YOLO

import mlflow
from utils.mlflow_utils import setup_mlflow
from utils.yolo_data import prepare_dataset
from configs.config import BASE_DIR as ROOT_DIR


MODEL_ALIASES = {
    "yolov8n-seg":            "yolov8n-seg.pt",
    "yolov8n-seg-sgd":       "yolov8n-seg.pt",
    "yolov8n-seg-adamw":     "yolov8n-seg.pt",
    "yolov8n-seg-long":       "yolov8n-seg.pt",
    "yolov8n-seg-long-sgd":  "yolov8n-seg.pt",
    "yolov8n-seg-long-adamw":"yolov8n-seg.pt",
}

YOLO_MODELS = list(MODEL_ALIASES.keys())

SEGMENT_CONFIGS = {
    "yolov8n-seg": {"default_optimizer": "AdamW", "default_epochs": 50,  "default_batch": 4,  "default_lr": 0.001},
    "yolov8s-seg": {"default_optimizer": "SGD",   "default_epochs": 100,  "default_batch": 8,  "default_lr": 0.01},
    "yolov8m-seg": {"default_optimizer": "Adam",  "default_epochs": 100,  "default_batch": 8,  "default_lr": 0.001},
}


def create_dataset_yaml(dst_dir: Path) -> Path:
    """Создать YAML конфигурацию датасета для YOLO."""
    yaml_content = f"""path: {dst_dir}
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


def train_yolo_segment(
    model_name: str = "yolov8n-seg",
    optimizer: str = "AdamW",
    lr: float = 0.001,
    epochs: int = 50,
    imgsz: int = 640,
    batch: int = 4,
    device: str = "cuda",
    prepare: bool = True,
) -> dict:
    """Запустить обучение YOLOv8-segment. Returns dict with final metrics."""
    dataset_dir = ROOT_DIR / "data" / "yolo8_segment"

    if prepare:
        print("  Preparing dataset (bbox -> polygon)...")
        prepare_dataset()

    yaml_path = create_dataset_yaml(dataset_dir)

    pt_name = MODEL_ALIASES.get(model_name, model_name)
    model = YOLO(pt_name)

    device_str = "cpu" if device == "cpu" or not torch.cuda.is_available() else "0"

    try:
        urllib.request.urlopen("http://localhost:5000", timeout=2)
        mlflow_tracking_uri = "http://localhost:5000"
    except Exception:
        mlflow_tracking_uri = str(ROOT_DIR / "mlruns")
        print(f"  MLflow: using local {mlflow_tracking_uri}")

    mlflow = setup_mlflow(
        experiment_name="yolo8-segment",
        tracking_uri=mlflow_tracking_uri,
    )

    run_name = f"{model_name}-e{epochs}-bs{batch}-{optimizer.lower()}"
    project_dir = ROOT_DIR / "yolo8_segment" / run_name

    with mlflow.start_run(run_name=run_name):
        mlflow.log_params({
            "model": model_name,
            "optimizer": optimizer,
            "learning_rate": lr,
            "epochs": epochs,
            "imgsz": imgsz,
            "batch": batch,
            "device": device_str,
            "dataset": "crocodilian_segmentation",
            "num_classes": 3,
            "classes": "alligator, cayman, crocodile",
            "train_samples": len(list((dataset_dir / "images" / "train").glob("*.jpeg"))),
            "val_samples": len(list((dataset_dir / "images" / "val").glob("*.jpeg"))),
        })

        results = model.train(
            data=str(yaml_path),
            epochs=epochs,
            imgsz=imgsz,
            device=device_str,
            batch=batch,
            optimizer=optimizer,
            lr0=lr,
            lrf=0.01,
            project=str(ROOT_DIR / "yolo8_segment"),
            name=run_name,
            exist_ok=False,
            verbose=True,
            amp=True,
            plots=True,
            save=True,
            save_period=10,
        )

        best_model_path = project_dir / "weights" / "best.pt"
        last_model_path = project_dir / "weights" / "last.pt"
        export_dir = project_dir / "weights"

        safe_name = model_name.replace("-", "_").replace(".", "_")

        if best_model_path.exists():
            mlflow.log_artifact(str(best_model_path), "model")

            onnx_file = export_dir / "best.onnx"
            if onnx_file.exists():
                mlflow.log_artifact(str(onnx_file), "onnx_model")
                shutil.copy(onnx_file, ROOT_DIR / "data" / "models" / f"{safe_name}_best.onnx")

        if last_model_path.exists():
            mlflow.log_artifact(str(last_model_path), "model_last")

        if (export_dir / "best.pt").exists():
            shutil.copy(export_dir / "best.pt", ROOT_DIR / "data" / "models" / f"{safe_name}_best.pt")

        results_plot = project_dir / "results.png"
        if results_plot.exists():
            mlflow.log_artifact(str(results_plot), "artifacts")

        confusion_matrix = project_dir / "confusion_matrix.png"
        if confusion_matrix.exists():
            mlflow.log_artifact(str(confusion_matrix), "artifacts")

        metrics = {}
        if hasattr(results, "results_dict"):
            for key, value in results.results_dict.items():
                if isinstance(value, (int, float)):
                    clean_key = key.replace("[", "_").replace("]", "_").replace("(", "_").replace(")", "_").replace("/", "_")
                    mlflow.log_metric(clean_key, value)
                    metrics[clean_key] = value

        print(f"\n  Training complete!")
        print(f"  Best model: {best_model_path}")

        return metrics


def run_segment_from_args(args) -> dict:
    """Запустить обучение сегментации из аргументов командной строки."""
    model_name = args.model
    optimizer = args.optimizer or SEGMENT_CONFIGS[model_name]["default_optimizer"]
    lr = args.lr or SEGMENT_CONFIGS[model_name]["default_lr"]
    epochs = args.epochs or SEGMENT_CONFIGS[model_name]["default_epochs"]
    batch = args.batch or SEGMENT_CONFIGS[model_name]["default_batch"]
    imgsz = args.imgsz or 640
    device = args.device or "cuda"

    return train_yolo_segment(
        model_name=model_name,
        optimizer=optimizer,
        lr=lr,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        prepare=args.prepare,
    )