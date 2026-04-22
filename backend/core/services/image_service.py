"""
Сервис для работы с изображениями
"""
import boto3
from django.conf import settings
from django.core.files.storage import default_storage


def get_uploaded_images():
    """Получить список всех загруженных изображений из MinIO"""
    try:
        storage = default_storage
        prefix = f"{storage.location}/images/"

        s3 = storage.connection
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        images = []
        for obj in bucket.objects.filter(Prefix=prefix):
            key = obj.key
            # Пропускаем директории
            if key.endswith('/'):
                continue

            # Получаем имя файла без префикса
            filename = key.replace(prefix, "")
            if filename:
                # Генерируем URL для изображения
                image_url = default_storage.url(key.replace(f"{storage.location}/", ""))
                images.append({
                    "filename": filename,
                    "url": image_url,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat()
                })

        return images
    except Exception as e:
        print(f"Ошибка получения изображений: {e}")
        return []


def save_uploaded_image(file_obj):
    """
    Сохранить загруженное изображение в хранилище
    
    Args:
        file_obj: Объект загруженного файла
        
    Returns:
        tuple: (saved_path, file_url)
    """
    file_path = f"images/{file_obj.name}"
    saved_path = default_storage.save(file_path, file_obj)
    file_url = default_storage.url(saved_path)
    return saved_path, file_url
