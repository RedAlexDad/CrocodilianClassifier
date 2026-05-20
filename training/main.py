#!/usr/bin/env python3
"""
Главный скрипт для обучения моделей классификации и сегментации

Использование:
    # Классификация
    python main.py --model mlp|cnn|resnet20|mobilenet [--optimizer adam|sgd] [--epochs 50]

    # Сегментация
    python main.py --task segment --model yolov8n-seg|yolov8s-seg [--optimizer sgd] [--epochs 50] [--batch 8]
"""

import argparse
import torch
from options import (
    MODELS,
    get_model_trainer,
    get_default_optimizer,
    get_available_optimizers,
    print_summary,
    YOLO_MODELS,
    MODEL_ALIASES,
    SEGMENT_CONFIGS,
)
from scripts.train_yolo_seg import run_segment_from_args


def main():
    parser = argparse.ArgumentParser(
        description="Обучение моделей классификации и сегментации",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Классификация:
  python main.py --model cnn
  python main.py --model resnet20 --optimizer adam --epochs 50
  python main.py --model all --epochs 50

Сегментация:
  python main.py --task segment --model yolov8n-seg --epochs 50 --batch 4
  python main.py --task segment --model yolov8s-seg --optimizer SGD --lr 0.01 --epochs 100 --batch 8
  python main.py --task segment --model yolov8m-seg --epochs 100 --batch 8
  python main.py --task segment --model yolov8l-seg --optimizer SGD --lr 0.01 --epochs 100 --batch 4
        """,
    )
    parser.add_argument(
        "--task", type=str, default="classify",
        choices=["classify", "segment"],
        help="Тип задачи: classify (по умолчанию) или segment"
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help=f"Модель: {MODELS + ['all']} (класс.) или {YOLO_MODELS} (сегм.)"
    )
    parser.add_argument(
        "--optimizer", type=str, default=None, help="Оптимизатор (adam, sgd, rmsprop, adagrad)"
    )
    parser.add_argument("--lr", type=float, default=None, help="Learning rate")
    parser.add_argument("--epochs", type=int, default=None, help="Количество эпох")
    parser.add_argument(
        "--epochs-stage1", type=int, default=None, help="Эпох этап 1 (только для transfer learning)"
    )
    parser.add_argument("--finetune-layers", type=int, default=None, help="Слоёв для fine-tuning")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--compare-optimizers", action="store_true", help="Сравнить все оптимизаторы"
    )
    parser.add_argument("--batch-size", type=int, default=None, help="Batch size")
    parser.add_argument(
        "--weight-decay", type=float, default=1e-4, help="Weight decay (L2 regularization)"
    )
    parser.add_argument(
        "--device", type=str, default="cuda", choices=["cuda", "cpu"], help="Устройство"
    )
    parser.add_argument(
        "--imgsz", type=int, default=640, help="Размер изображения (сегментация)"
    )
    parser.add_argument(
        "--no-prepare", action="store_true", help="Не пересоздавать датасет (сегментация)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("Крокодиловые: классификация и сегментация")
    print("=" * 60)
    print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    print(f"Устройство: {args.device}")
    print(f"Задача: {args.task}")

    if args.task == "segment":
        model_name = args.model or "yolov8n-seg"
        if model_name not in YOLO_MODELS:
            raise ValueError(f"Модель сегментации: {YOLO_MODELS}")

        print(f"Модель: {model_name}")

        cfg = SEGMENT_CONFIGS[model_name]
        seg_args = argparse.Namespace(
            model=model_name,
            optimizer=args.optimizer or cfg["default_optimizer"],
            lr=args.lr or cfg["default_lr"],
            epochs=args.epochs or cfg["default_epochs"],
            imgsz=args.imgsz or 640,
            batch=args.batch or cfg["default_batch"],
            device=args.device,
            prepare=not args.no_prepare,
        )
        metrics = run_segment_from_args(seg_args)

        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ СЕГМЕНТАЦИИ")
        print("=" * 60)
        if metrics:
            for k, v in sorted(metrics.items()):
                if "mAP" in k or "precision" in k or "recall" in k:
                    print(f"  {k}: {v:.4f}")
        print("=" * 60)
        return

    # === Классификация ===
    if args.model and args.model not in MODELS + ["all"]:
        raise ValueError(f"Модель классификации должна быть одна из: {MODELS + ['all']}")

    print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    print(f"Устройство: {args.device}")
    print(f"Модель: {args.model}")
    print("=" * 60)

    models_to_train = MODELS if args.model == "all" else [args.model]
    results = []

    for model_type in models_to_train:
        trainer = get_model_trainer(model_type)
        if trainer is None:
            raise ValueError(f"Неизвестная модель: {model_type}")

        if args.compare_optimizers:
            optimizers = get_available_optimizers(model_type)
            print(f"\n=== Сравнение оптимизаторов для {model_type.upper()} ===")

            for opt in optimizers:
                kwargs = {"model_name": model_type, "optimizer_name": opt, "seed": args.seed, "epochs": args.epochs, "device": args.device}
                if model_type in ("resnet20", "mobilenet"):
                    kwargs.update({
                        "epochs_stage1": args.epochs_stage1,
                        "finetune_layers": args.finetune_layers,
                        "lr": args.lr,
                        "lr_finetune": args.lr_finetune,
                    })
                acc = trainer(**kwargs)
                results.append({"name": model_type.upper(), "optimizer": opt, "acc": acc})
        else:
            optimizer = args.optimizer or get_default_optimizer(model_type)
            kwargs = {"model_name": model_type, "optimizer_name": optimizer, "seed": args.seed, "epochs": args.epochs, "device": args.device}

            if model_type in ("resnet20", "mobilenet"):
                kwargs.update({
                    "epochs_stage1": args.epochs_stage1,
                    "finetune_layers": args.finetune_layers,
                    "lr": args.lr,
                    "lr_finetune": args.lr_finetune,
                })

            acc = trainer(**kwargs)
            results.append({"name": model_type.upper(), "optimizer": optimizer, "acc": acc})

    print_summary(results)


if __name__ == "__main__":
    main()