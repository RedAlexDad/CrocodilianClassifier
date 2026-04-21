"""
Кастомное S3 хранилище для MinIO с правильным формированием URL
"""

import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class MinioMediaStorage(S3Boto3Storage):
    """S3 хранилище для медиа файлов с правильным URL для MinIO"""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("bucket_name", getattr(settings, "AWS_STORAGE_BUCKET_NAME", "dz1-media"))
        kwargs.setdefault("location", "media")
        kwargs.setdefault("default_acl", "public-read")
        kwargs.setdefault("querystring_auth", False)
        kwargs.setdefault("signature_version", "s3v4")
        kwargs.setdefault("addressing_style", "path")

        # Endpoint URL из настроек Django
        kwargs.setdefault(
            "endpoint_url", getattr(settings, "AWS_S3_ENDPOINT_URL", "http://minio:9000")
        )
        kwargs.setdefault("access_key", getattr(settings, "AWS_ACCESS_KEY_ID", "minioadmin"))
        kwargs.setdefault("secret_key", getattr(settings, "AWS_SECRET_ACCESS_KEY", "minioadmin"))

        super().__init__(*args, **kwargs)

        # Базовый URL для доступа к файлам (для браузера)
        self.custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", "localhost:9000")
        self.bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "dz1-media")
        self.location = getattr(settings, "AWS_LOCATION", "media")

    def url(self, name, parameters=None, expire=None, http_method=None):
        """Возвращает URL для доступа к файлу через браузер"""
        # Удаляем префикс location, если он уже есть в имени файла
        clean_name = name
        if clean_name.startswith(self.location + "/"):
            clean_name = clean_name[len(self.location) + 1 :]

        # Формируем URL вручную для правильного доступа через браузер
        return f"http://{self.custom_domain}/{self.bucket_name}/{self.location}/{clean_name}"

    def get_available_models(self):
        """Получение списка .onnx моделей из S3"""
        try:
            bucket = self.connection.Bucket(self.bucket_name)
            prefix = f"{self.location}/models/"

            models = []
            for obj in bucket.objects.filter(Prefix=prefix):
                key = obj.key.replace(prefix, "")
                if key.endswith(".onnx") and "/" not in key:
                    models.append(key)

            return models if models else ["cifar100.onnx"]
        except Exception:
            return ["cifar100.onnx"]
