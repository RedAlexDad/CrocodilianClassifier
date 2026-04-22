#!/usr/bin/env python3
"""
Скрипт для поиска и удаления дубликатов изображений в датасете.
Использует perceptual hashing для определения похожих изображений.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import imagehash
from collections import defaultdict
import argparse


def find_duplicates(data_dir, threshold=5, dry_run=False):
    """
    Найти и удалить дубликаты изображений.
    
    Args:
        data_dir: Путь к директории с данными
        threshold: Порог различия хэшей (0 = идентичные, 5 = очень похожие)
        dry_run: Если True, только показать дубликаты без удаления
    """
    print(f"🔍 Поиск дубликатов в {data_dir} (порог: {threshold})")
    
    # Словарь: хэш -> список файлов
    hashes = defaultdict(list)
    
    # Проходим по всем изображениям
    for root, dirs, files in os.walk(data_dir):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(root, filename)
                try:
                    # Вычисляем perceptual hash
                    img = Image.open(filepath)
                    img_hash = imagehash.average_hash(img)
                    hashes[img_hash].append(filepath)
                except Exception as e:
                    print(f"⚠️  Ошибка обработки {filepath}: {e}")
    
    # Ищем похожие изображения
    all_hashes = list(hashes.keys())
    duplicates = []
    
    for i, hash1 in enumerate(all_hashes):
        for hash2 in all_hashes[i+1:]:
            # Вычисляем разницу между хэшами
            diff = hash1 - hash2
            if diff <= threshold:
                # Нашли дубликаты
                files1 = hashes[hash1]
                files2 = hashes[hash2]
                duplicates.append((diff, files1, files2))
    
    if not duplicates:
        print("✅ Дубликаты не найдены!")
        return 0
    
    # Группируем дубликаты
    print(f"\n📊 Найдено групп дубликатов: {len(duplicates)}")
    
    removed_count = 0
    for diff, files1, files2 in duplicates:
        print(f"\n🔗 Похожесть: {100 - (diff / 64 * 100):.1f}% (diff={diff})")
        
        # Объединяем все файлы в одну группу
        all_files = files1 + files2
        
        # Оставляем первый файл, остальные удаляем
        keep_file = all_files[0]
        remove_files = all_files[1:]
        
        print(f"  ✓ Оставить: {keep_file}")
        for remove_file in remove_files:
            print(f"  ✗ Удалить:  {remove_file}")
            
            if not dry_run:
                try:
                    os.remove(remove_file)
                    removed_count += 1
                except Exception as e:
                    print(f"    ⚠️  Ошибка удаления: {e}")
    
    if dry_run:
        print(f"\n🔍 Режим проверки: найдено {len(duplicates)} групп дубликатов")
        print("   Запустите без --dry-run для удаления")
    else:
        print(f"\n✅ Удалено файлов: {removed_count}")
    
    return removed_count


def main():
    parser = argparse.ArgumentParser(
        description='Поиск и удаление дубликатов изображений в датасете'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Путь к директории с данными (по умолчанию: data)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=5,
        help='Порог различия хэшей (0-64, меньше = строже, по умолчанию: 5)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Только показать дубликаты без удаления'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data_dir):
        print(f"❌ Директория {args.data_dir} не найдена!")
        sys.exit(1)
    
    removed = find_duplicates(args.data_dir, args.threshold, args.dry_run)
    
    return 0 if args.dry_run else removed


if __name__ == '__main__':
    sys.exit(main())
