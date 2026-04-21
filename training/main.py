#!/usr/bin/env python3
"""
Главный скрипт для обучения моделей классификации

Использование:
    python main.py --model mlp|cnn|resnet20|mobilenet|all [--optimizer adam|sgd|...]
"""

import argparse
import torch
from options import (
    MODELS,
    get_model_trainer,
    get_default_optimizer,
    get_available_optimizers,
    print_summary,
)


def main():
    parser = argparse.ArgumentParser(
        description="Обучение моделей классификации",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Доступные модели: mlp, cnn, resnet20, mobilenet, all
Доступные оптимизаторы: adam, adagrad, rmsprop, sgd

Примеры:
  python main.py --model cnn                              CNN модель
  python main.py --model resnet20 --optimizer adam        ResNet20
  python main.py --model all --epochs 50                Все модели, 50 эпох
  python main.py --model cnn --lr 0.01 --epochs 100   CNN с LR=0.01
  python main.py --model all --compare-optimizers       Сравнить оптимизаторы
        """,
    )
    parser.add_argument(
        "--model", type=str, choices=MODELS + ["all"], default="all", help="Модель для обучения"
    )
    parser.add_argument(
        "--optimizer", type=str, default=None, help="Оптимизатор (adam, adagrad, rmsprop, sgd)"
    )
    parser.add_argument("--epochs", type=int, default=None, help="Количество эпох")
    parser.add_argument(
        "--epochs-stage1", type=int, default=None, help="Эпох этап 1 (только для TL)"
    )
    parser.add_argument("--finetune-layers", type=int, default=None, help="Слоёв для fine-tuning")
    parser.add_argument("--lr", type=float, default=None, help="Learning rate")
    parser.add_argument("--lr-finetune", type=float, default=None, help="LR для fine-tuning")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--compare-optimizers", action="store_true", help="Сравнить все оптимизаторы"
    )
    parser.add_argument("--batch-size", type=int, default=None, help="Batch size")
    parser.add_argument(
        "--weight-decay", type=float, default=1e-4, help="Weight decay (L2 regularization)"
    )
    parser.add_argument(
        "--device", type=str, default="cuda", choices=["cuda", "cpu"], help="Устройство (cuda/cpu)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("Классификация: крокодил, аллигатор, кайман")
    print("=" * 60)
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
                    kwargs.update(
                        {
                            "epochs_stage1": args.epochs_stage1,
                            "finetune_layers": args.finetune_layers,
                            "lr": args.lr,
                            "lr_finetune": args.lr_finetune,
                        }
                    )
                acc = trainer(**kwargs)
                results.append({"name": model_type.upper(), "optimizer": opt, "acc": acc})
        else:
            optimizer = args.optimizer or get_default_optimizer(model_type)
            kwargs = {"model_name": model_type, "optimizer_name": optimizer, "seed": args.seed, "epochs": args.epochs, "device": args.device}

            if model_type in ("resnet20", "mobilenet"):
                kwargs.update(
                    {
                        "epochs_stage1": args.epochs_stage1,
                        "finetune_layers": args.finetune_layers,
                        "lr": args.lr,
                        "lr_finetune": args.lr_finetune,
                    }
                )

            acc = trainer(**kwargs)
            results.append({"name": model_type.upper(), "optimizer": optimizer, "acc": acc})

    print_summary(results)


if __name__ == "__main__":
    main()
