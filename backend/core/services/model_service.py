"""
Сервис для работы с моделями
"""
import os
import boto3
from django.conf import settings
from django.core.files.storage import default_storage


DEPRIORITIZED_AUTO_MODELS = frozenset({"cifar100.onnx"})


def get_available_models():
    """Получение списка доступных ONNX моделей"""
    if settings.USE_S3:
        try:
            storage = default_storage
            prefix = f"{storage.location}/models/"

            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

            models = []
            for obj in bucket.objects.filter(Prefix=prefix):
                key = obj.key.replace(prefix, "")
                if key.endswith(".onnx") and "/" not in key:
                    models.append(key)

            return models
        except Exception as e:
            print(f"Ошибка получения списка моделей: {e}")
            return []
    else:
        # Локальный режим
        models_dir = os.path.join(settings.BASE_DIR, "media", "models")
        if not os.path.exists(models_dir):
            return []

        models = [f for f in os.listdir(models_dir) if f.endswith(".onnx")]
        return models


def pick_model_for_request(request):
    """Имя .onnx из POST, если файл есть в хранилище; иначе первая подходящая модель."""
    posted = (request.POST.get("modelName") or "").strip()
    available = get_available_models()
    if posted in available:
        return posted
    return _autopick_model_name(available)


def _autopick_model_name(available):
    """Автовыбор: не брать устаревший cifar100, если в бакете есть другие модели."""
    if not available:
        return ""
    preferred = [m for m in available if m not in DEPRIORITIZED_AUTO_MODELS]
    pool = preferred if preferred else list(available)
    return sorted(pool)[0]


def upload_model_to_storage(model_file):
    """Загрузить модель в S3 хранилище"""
    try:
        storage = default_storage
        s3 = storage.connection
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        model_key = f"media/models/{model_file.name}"
        bucket.upload_fileobj(
            model_file.file,
            model_key,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": model_file.content_type or "application/octet-stream",
            },
        )
        return True, None
    except Exception as e:
        return False, str(e)


def delete_model_from_storage(model_name):
    """Удалить модель из S3 хранилища"""
    try:
        storage = default_storage
        s3 = storage.connection
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        full_key = f"media/models/{model_name}"
        objs = list(bucket.objects.filter(Prefix=full_key))

        if not objs:
            return False, "MODEL_NOT_FOUND"

        bucket.delete_objects(Delete={"Objects": [{"Key": full_key}]})
        return True, None
    except Exception as e:
        return False, str(e)
