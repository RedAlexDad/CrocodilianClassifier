#!/usr/bin/env python3
"""
Главный скрипт для обучения моделей классификации:
- MLP (многослойный перцептрон)
- CNN (свёрточная нейросеть)
- MobileNetV2 (transfer learning)

Использование:
    # Обучение всех моделей
    python main.py
    
    # Обучение конкретной модели с оптимизатором по умолчанию
    python main.py --model mlp
    python main.py --model cnn
    python main.py --model mobilenet
    
    # Обучение с выбором оптимизатора
    python main.py --model mlp --optimizer adam
    python main.py --model cnn --optimizer rmsprop
    python main.py --model mobilenet --optimizer adagrad
    
    # Обучение всех моделей с разными оптимизаторами для сравнения
    python main.py --model all --optimizer adam
    python main.py --model all --optimizer rmsprop
"""

import argparse
import torch

from scripts import train_mlp, train_cnn, train_mobilenet


OPTIMIZERS = ['adam', 'adagrad', 'rmsprop', 'sgd']
OPTIMIZERS_MLP = ['adam', 'adagrad', 'rmsprop']
OPTIMIZERS_CNN = ['sgd', 'adam', 'rmsprop']
OPTIMIZERS_MOBILENET = ['adam', 'adagrad', 'rmsprop']


def print_summary(results):
    """Вывод сводки по обучению"""
    print("\n" + "="*60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("="*60)
    
    for entry in results:
        model_name = entry['name']
        optimizer = entry['optimizer']
        acc = entry['acc']
        print(f"  {model_name} ({optimizer.upper()}): {acc:.2f}%")
    
    print("="*60)
    
    if results:
        best_entry = max(results, key=lambda x: x['acc'])
        print(f"\n🏆 Лучшая модель: {best_entry['name']} ({best_entry['optimizer'].upper()}) - {best_entry['acc']:.2f}%")


def main():
    parser = argparse.ArgumentParser(
        description='Обучение моделей классификации изображений'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=['mlp', 'cnn', 'mobilenet', 'all'],
        default='all',
        help='Модель для обучения (по умолчанию: all)'
    )
    parser.add_argument(
        '--optimizer',
        type=str,
        choices=OPTIMIZERS,
        default=None,
        help=f'Оптимизатор (по умолчанию: adam для MLP/MobileNet, sgd для CNN)'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=None,
        help='Количество эпох для этапа 2 (fine-tuning), по умолчанию: 30'
    )
    parser.add_argument(
        '--epochs-stage1',
        type=int,
        default=None,
        help='Количество эпох для этапа 1 (классификатор), по умолчанию: 50'
    )
    parser.add_argument(
        '--finetune-layers',
        type=int,
        default=None,
        help='Количество размораживаемых слоёв для fine-tuning (по умолчанию: 20)'
    )
    parser.add_argument(
        '--lr', '--learning-rate',
        type=float,
        default=None,
        dest='lr',
        help='Learning rate для этапа 1 (по умолчанию: из конфига)'
    )
    parser.add_argument(
        '--lr-finetune',
        type=float,
        default=None,
        help='Learning rate для fine-tuning этапа 2 (по умолчанию: 0.0001)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Случайное зерно (по умолчанию: 42)'
    )
    parser.add_argument(
        '--compare-optimizers',
        action='store_true',
        help='Сравнить все оптимизаторы для выбранной модели'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("Классификация: крокодил, аллигатор, кайман")
    print("="*60)
    print(f"PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    print(f"Модель: {args.model}")
    if args.optimizer:
        print(f"Оптимизатор: {args.optimizer.upper()}")
    if args.epochs:
        print(f"Эпох этап 2: {args.epochs}")
    if args.epochs_stage1:
        print(f"Эпох этап 1: {args.epochs_stage1}")
    if args.finetune_layers:
        print(f"Fine-tune слоёв: {args.finetune_layers}")
    if args.lr:
        print(f"Learning rate: {args.lr}")
    if args.compare_optimizers:
        print("Режим: Сравнение оптимизаторов")
    print("="*60)
    
    results = []
    
    # Определение моделей для обучения
    if args.model == 'mlp':
        models_to_train = ['mlp']
    elif args.model == 'cnn':
        models_to_train = ['cnn']
    elif args.model == 'mobilenet':
        models_to_train = ['mobilenet']
    else:  # all
        models_to_train = ['mlp', 'cnn', 'mobilenet']
    
    # Обучение с сравнением оптимизаторов или с одним оптимизатором
    for model_type in models_to_train:
        if args.compare_optimizers:
            # Выбор доступных оптимизаторов для модели
            if model_type == 'mlp':
                optimizers = OPTIMIZERS_MLP
            elif model_type == 'cnn':
                optimizers = OPTIMIZERS_CNN
            else:
                optimizers = OPTIMIZERS_MOBILENET
            
            print(f"\n{'='*60}")
            print(f"Сравнение оптимизаторов для {model_type.upper()}")
            print(f"{'='*60}")
            
            for opt in optimizers:
                acc = train_model(
                    model_type, opt, args.seed,
                    epochs=args.epochs, epochs_stage1=args.epochs_stage1,
                    finetune_layers=args.finetune_layers,
                    lr=args.lr, lr_finetune=args.lr_finetune
                )
                results.append({
                    'name': model_type.upper(),
                    'optimizer': opt,
                    'acc': acc
                })
        else:
            # Обучение с одним оптимизатором
            optimizer = args.optimizer
            if optimizer is None:
                # Оптимизатор по умолчанию
                if model_type == 'mlp':
                    optimizer = 'adam'
                elif model_type == 'cnn':
                    optimizer = 'sgd'
                else:
                    optimizer = 'adam'
            
            acc = train_model(
                model_type, optimizer, args.seed,
                epochs=args.epochs, epochs_stage1=args.epochs_stage1,
                finetune_layers=args.finetune_layers,
                lr=args.lr, lr_finetune=args.lr_finetune
            )
            results.append({
                'name': model_type.upper(),
                'optimizer': optimizer,
                'acc': acc
            })
    
    print_summary(results)


def train_model(model_type, optimizer, seed, epochs=None, epochs_stage1=None, finetune_layers=None, lr=None, lr_finetune=None):
    """Обучение конкретной модели"""
    if model_type == 'mlp':
        return train_mlp(optimizer_name=optimizer, seed=seed, epochs=epochs, lr=lr)
    elif model_type == 'cnn':
        return train_cnn(optimizer_name=optimizer, seed=seed, epochs=epochs, lr=lr)
    elif model_type == 'mobilenet':
        return train_mobilenet(
            optimizer_name=optimizer, 
            seed=seed, 
            epochs=epochs, 
            epochs_stage1=epochs_stage1,
            finetune_layers=finetune_layers,
            lr=lr,
            lr_finetune=lr_finetune
        )
    else:
        raise ValueError(f"Неизвестная модель: {model_type}")


if __name__ == '__main__':
    main()
