#!/usr/bin/env python3
"""
Главный скрипт для обучения моделей классификации

Использование:
    python main.py --model mlp|cnn|resnet20|mobilenet|all [--optimizer adam|sgd|...]
"""
import argparse
import torch
from options import (
    MODELS, get_model_trainer, get_default_optimizer, 
    get_available_optimizers, print_summary
)


def main():
    parser = argparse.ArgumentParser(description='Обучение моделей классификации')
    parser.add_argument('--model', type=str, choices=MODELS + ['all'], default='all')
    parser.add_argument('--optimizer', type=str, default=None)
    parser.add_argument('--epochs', type=int, default=None)
    parser.add_argument('--epochs-stage1', type=int, default=None)
    parser.add_argument('--finetune-layers', type=int, default=None)
    parser.add_argument('--lr', type=float, default=None)
    parser.add_argument('--lr-finetune', type=float, default=None)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--compare-optimizers', action='store_true')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("Классификация: крокодил, аллигатор, кайман")
    print("="*60)
    print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    print(f"Модель: {args.model}")
    print("="*60)

    models_to_train = MODELS if args.model == 'all' else [args.model]
    results = []

    for model_type in models_to_train:
        trainer = get_model_trainer(model_type)

        if args.compare_optimizers:
            optimizers = get_available_optimizers(model_type)
            print(f"\n=== Сравнение оптимизаторов для {model_type.upper()} ===")

            for opt in optimizers:
                kwargs = {'optimizer_name': opt, 'seed': args.seed, 'epochs': args.epochs}
                if model_type in ('resnet20', 'mobilenet'):
                    kwargs.update({
                        'epochs_stage1': args.epochs_stage1,
                        'finetune_layers': args.finetune_layers,
                        'lr': args.lr,
                        'lr_finetune': args.lr_finetune
                    })
                acc = trainer(**kwargs)
                results.append({'name': model_type.upper(), 'optimizer': opt, 'acc': acc})
        else:
            optimizer = args.optimizer or get_default_optimizer(model_type)
            kwargs = {'optimizer_name': optimizer, 'seed': args.seed, 'epochs': args.epochs}
            
            if model_type in ('resnet20', 'mobilenet'):
                kwargs.update({
                    'epochs_stage1': args.epochs_stage1,
                    'finetune_layers': args.finetune_layers,
                    'lr': args.lr,
                    'lr_finetune': args.lr_finetune
                })

            acc = trainer(**kwargs)
            results.append({'name': model_type.upper(), 'optimizer': optimizer, 'acc': acc})

    print_summary(results)


if __name__ == '__main__':
    main()