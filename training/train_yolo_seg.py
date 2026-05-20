#!/usr/bin/env python3
"""
Обучение YOLOv8-segment с MLflow tracking.
Использование: python3 scripts/train_yolo_seg.py --model yolov8s-seg --optimizer sgd --epochs 100 --batch 8 --device cuda
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

import mlflow
from utils.mlflow_utils import setup_mlflow


MODEL_ALIASES = {
    "yolov8n-seg": "yolov8n-seg.pt",
    "yolov8s-seg": "yolov8s-seg.pt",
    "yolov8m-seg": "yolov8m-seg.pt",
}


def create_dataset_yaml(dst_dir):
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


def run_training(
    model_name="yolov8n-seg",
    optimizer="AdamW",
    lr=0.001,
    epochs=50,
    imgsz=640,
    batch=4,
    device="cuda",
    project="yolo8_segment",
):
    """Запустить обучение YOLOv8-segment."""
    base_dir = Path(__file__).parent.parent
    src_dir = base_dir / "data" / "yolo8_segment"
    yaml_path = create_dataset_yaml(src_dir)

    pt_name = MODEL_ALIASES.get(model_name, model_name)
    model = YOLO(pt_name)

    if device == "cpu" or not torch.cuda.is_available():
        device_str = "cpu"
    else:
        device_str = "0"

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

    run_name = f"{model_name}-e{epochs}-bs{batch}-{optimizer.lower()}"
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
            "train_samples": len(list((src_dir / "images" / "train").glob("*.jpeg"))),
            "val_samples": len(list((src_dir / "images" / "val").glob("*.jpeg"))),
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
        export_dir = base_dir / project / "train" / "weights"

        if best_model_path.exists():
            mlflow.log_artifact(str(best_model_path), "model")

            safe_name = model_name.replace("-", "_").replace(".", "_")
            onnx_path = export_dir / f"{safe_name}_best.onnx"
            model.export(format="onnx", imgsz=imgsz, simplify=True)
            exported = export_dir / f"{safe_name}_best.onnx"
            if exported.exists():
                mlflow.log_artifact(str(exported), "onnx_model")
                shutil.copy(exported, base_dir / "data" / "models" / f"{safe_name}_best.onnx")
                print(f"ONNX saved: {base_dir / 'data' / 'models' / f'{safe_name}_best.onnx'}")

        if last_model_path.exists():
            mlflow.log_artifact(str(last_model_path), "model_last")

        shutil.copy(export_dir / "best.pt", base_dir / "data" / "models" / f"{safe_name}_best.pt")

        results_plot = base_dir / project / "train" / "results.png"
        if results_plot.exists():
            mlflow.log_artifact(str(results_plot), "artifacts")

        confusion_matrix = base_dir / project / "train" / "confusion_matrix.png"
        if confusion_matrix.exists():
            mlflow.log_artifact(str(confusion_matrix), "artifacts")

        if hasattr(results, "results_dict"):
            metrics = results.results_dict
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    clean_key = key.replace("[", "_").replace("]", "_").replace("/", "_")
                    mlflow.log_metric(clean_key, value)

        print("\nTraining complete!")
        print(f"Best model: {best_model_path}")
        print(f"Results: {base_dir / project / 'train'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8-segment")
    parser.add_argument("--model", type=str, default="yolov8n-seg",
                        choices=list(MODEL_ALIASES.keys()),
                        help="Model size (yolov8n-seg, yolov8s-seg, yolov8m-seg)")
    parser.add_argument("--optimizer", type=str, default="AdamW",
                        choices=["AdamW", "SGD", "Adam"],
                        help="Optimizer type")
    parser.add_argument("--lr", type=float, default=0.001, help="Initial learning rate")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=4, help="Batch size")
    parser.add_argument("--device", type=str, default="cuda", help="Device (cuda/cpu)")
    args = parser.parse_args()

    run_training(
        model_name=args.model,
        optimizer=args.optimizer,
        lr=args.lr,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
    )