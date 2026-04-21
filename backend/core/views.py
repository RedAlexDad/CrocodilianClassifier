from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import onnxruntime
import numpy as np
from PIL import Image
import os
import boto3

MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_BUCKET = "crocodilian-artifacts"

# Классы по вашему варианту: крокодил, аллигатор, кайман
imageClassList = {"0": "Крокодил", "1": "Аллигатор", "2": "Кайман"}


def get_mlflow_models():
    """Получить список моделей из MLflow S3"""
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )

        response = s3.list_objects_v2(Bucket=MLFLOW_BUCKET, Prefix="models/")

        if "Contents" not in response:
            return []

        models = []
        for obj in response["Contents"]:
            key = obj["Key"]
            if key.endswith(".onnx"):
                name = key.split("/")[-1]
                models.append(
                    {
                        "name": name,
                        "key": key,
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                    }
                )

        return models
    except Exception as e:
        print(f"Ошибка получения моделей из MLflow: {e}")
        return []


def get_mlflow_runs_api(request):
    """API: получить список RUN_ID из MLflow"""
    from botocore.client import Config

    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            config=Config(signature_version="s3v4"),
        )

        bucket = MLFLOW_BUCKET
        response = s3.list_objects_v2(Bucket=bucket, Prefix="")

        runs = {}
        for obj in response["Contents"]:
            key = obj["Key"]
            if "/artifacts/" in key:
                parts = key.split("/")
                if len(parts) >= 2:
                    exp_id = parts[0]
                    if exp_id not in runs:
                        runs[exp_id] = set()
                    if len(parts) >= 3:
                        runs[exp_id].add(parts[1])

        result = []
        for exp_id, run_ids in runs.items():
            for run_id in sorted(run_ids):
                result.append({"run_id": run_id, "experiment_id": exp_id})

        return JsonResponse({"runs": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_models_api(request):
    """API: получить список доступных моделей"""
    models = get_available_models()
    return JsonResponse({"models": models})


@csrf_exempt
def download_mlflow_model_api(request):
    """API: скачать модель из MLflow и сохранить в Django"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    run_id = request.POST.get("run_id")
    if not run_id:
        return JsonResponse({"error": "run_id required"}, status=400)

    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )

        bucket = MLFLOW_BUCKET
        # Ищем модель в разных возможных путях
        possible_prefixes = [
            f"{run_id}/artifacts/",
            f"1/{run_id}/artifacts/",
            f"0/{run_id}/artifacts/",
        ]

        onnx_key = None
        for prefix in possible_prefixes:
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            for obj in response.get("Contents", []):
                key = obj["Key"]
                if key.endswith(".onnx"):
                    onnx_key = key
                    break
            if onnx_key:
                break

        if not onnx_key:
            return JsonResponse({"error": "No ONNX model found"}, status=404)

        model_name = os.path.basename(onnx_key)
        local_path = f"/tmp/{model_name}"
        s3.download_file(bucket, onnx_key, local_path)

        storage = default_storage
        # Имя без префикса "media/": django-storages сам добавляет location ("media"),
        # иначе файл окажется в media/media/models/ и не попадёт в список моделей.
        model_key = f"models/{model_name}"
        with open(local_path, "rb") as f:
            storage.save(model_key, ContentFile(f.read()))

        os.remove(local_path)

        return JsonResponse({"success": True, "model": model_name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def download_model_from_mlflow(model_key, local_path):
    """Скачать модель из MLflow S3"""
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )

        s3.download_file(MLFLOW_BUCKET, model_key, local_path)
        return True
    except Exception as e:
        print(f"Ошибка скачивания модели: {e}")
        return False


def get_available_models():
    """Получение списка доступных ONNX моделей"""
    if settings.USE_S3:
        # S3 режим - получаем список из S3 через default_storage
        try:
            storage = default_storage
            # location уже установлен в 'media', поэтому ищем в 'models/'
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


def scoreImagePage(request):
    """Отображение страницы классификации"""
    context = {
        "available_models": get_available_models(),
        "current_model": request.POST.get("modelName", "cifar100.onnx"),
    }
    return render(request, "scorepage.html", context)


@csrf_exempt
def predictImage(request):
    """Обработка загруженного изображения и предсказание"""
    if request.method == "POST" and "filePath" in request.FILES:
        fileObj = request.FILES["filePath"]

        # Сохранение файла с использованием default_storage (S3 или локальное)
        # default_storage уже имеет location='media', поэтому сохраняем просто в 'images/'
        file_path = f"images/{fileObj.name}"
        saved_path = default_storage.save(file_path, fileObj)

        # Получаем URL через хранилище (для S3 будет http://localhost:19000/crocodilian/media/images/...)
        file_url = default_storage.url(saved_path)

        # Получение имени модели (если выбрано)
        modelName = request.POST.get("modelName", "cifar100.onnx")

        # Предсказание
        scorePrediction = predictImageData(modelName, saved_path)

        context = {
            "scorePrediction": scorePrediction,
            "image_url": file_url,
            "available_models": get_available_models(),
            "current_model": modelName,
        }
        if request.accepts("application/json"):
            return JsonResponse(
                {
                    "scorePrediction": scorePrediction,
                    "image_url": file_url,
                    "current_model": modelName,
                }
            )
        return render(request, "scorepage.html", context)

    if request.method == "POST" and request.accepts("application/json"):
        return JsonResponse({"error": "filePath required"}, status=400)

    return redirect("scoreImagePage")


def uploadModel(request):
    """Страница загрузки и управления моделями"""
    from django.contrib import messages

    # Удаление модели
    if request.method == "GET" and "delete_model" in request.GET:
        model_to_delete = request.GET.get("delete_model")
        try:
            storage = default_storage
            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
            full_key = f"media/models/{model_to_delete}"

            # Проверка существования и удаление
            objs = list(bucket.objects.filter(Prefix=full_key))
            if objs:
                bucket.delete_objects(Delete={"Objects": [{"Key": full_key}]})
                messages.success(request, f"Модель {model_to_delete} успешно удалена")
            else:
                messages.error(request, f"Модель {model_to_delete} не найдена")
        except Exception as e:
            messages.error(request, f"Ошибка при удалении: {str(e)}")

        return redirect("uploadModel")

    # Если выбрано использование модели
    if request.method == "GET" and "use_model" in request.GET:
        model_name = request.GET.get("use_model")
        messages.success(request, f"Модель {model_name} выбрана для классификации")
        return redirect("scoreImagePage")

    # Загрузка новой модели
    if request.method == "POST" and "modelFile" in request.FILES:
        model_file = request.FILES["modelFile"]

        # Проверка расширения
        if not model_file.name.endswith(".onnx"):
            messages.error(request, "Ошибка: Загрузите файл .onnx")
            return redirect("uploadModel")

        # Сохранение модели через boto3 напрямую
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

            messages.success(request, f"Модель {model_file.name} успешно загружена!")
        except Exception as e:
            messages.error(request, f"Ошибка при загрузке: {str(e)}")

        return redirect("uploadModel")

    context = {"available_models": get_available_models()}
    return render(request, "uploadmodel.html", context)


def uploadModelFromMLflow(request):
    """Загрузить модель из MLflow в Django"""
    from django.contrib import messages

    if request.method == "GET" and "model_key" in request.GET:
        model_key = request.GET.get("model_key")

        local_path = f"/tmp/{os.path.basename(model_key)}"
        if download_model_from_mlflow(model_key, local_path):
            try:
                s3 = boto3.client(
                    "s3",
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    aws_access_key_id="minioadmin",
                    aws_secret_access_key="minioadmin",
                )

                s3.upload_file(
                    local_path,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    f"media/models/{os.path.basename(model_key)}",
                )
                messages.success(request, f"Модель загружена из MLflow!")
            except Exception as e:
                messages.error(request, f"Ошибка: {str(e)}")
        else:
            messages.error(request, "Не удалось скачать модель из MLflow")

        return redirect("scoreImagePage")

    context = {"mlflow_models": get_mlflow_models()}
    return render(request, "mlflow_models.html", context)


def predictImageData(modelName, filePath):
    """Загрузка ONNX модели и предсказание класса изображения"""
    import tempfile
    import os
    import shutil
    import onnx

    try:
        # Загрузка и предобработка изображения
        img = Image.open(default_storage.open(filePath)).convert("RGB")
        img = img.resize((32, 32), Image.LANCZOS)
        img = np.asarray(img, dtype=np.float32)

        # Загрузка модели из S3
        storage = default_storage
        model_key = f"media/models/{modelName}"
        model_base_name = modelName.replace(".onnx", "")

        # Создаём временную директорию для модели
        tmp_dir = tempfile.mkdtemp()

        try:
            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

            # Скачиваем основной файл модели и все связанные файлы (.data)
            for obj in bucket.objects.filter(Prefix=f"media/models/{model_base_name}"):
                # Извлекаем имя файла из ключа
                file_name = obj.key.replace("media/models/", "")
                tmp_file_path = os.path.join(tmp_dir, file_name)

                # Скачиваем файл
                with open(tmp_file_path, "wb") as f:
                    bucket.download_fileobj(obj.key, f)

            # Путь к основному файлу модели
            tmp_model_path = os.path.join(tmp_dir, modelName)

            # Проверка формата входов модели
            onnx_model = onnx.load(tmp_model_path)
            input_shape = [
                d.dim_value if d.dim_value != 0 else -1
                for d in onnx_model.graph.input[0].type.tensor_type.shape.dim
            ]

            # Определение формата: NCHW или NHWC
            # NCHW: [batch, 3, 32, 32] - каналы на позиции 1
            # NHWC: [batch, 32, 32, 3] - каналы на позиции 3
            if len(input_shape) == 4 and input_shape[3] == 3:
                # NHWC формат - не транспонируем
                img = img  # уже в формате [32, 32, 3]
            elif len(input_shape) == 4 and input_shape[1] == 3:
                # NCHW формат - транспонируем
                img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
            else:
                # Плоский вектор или другой формат
                img = img.flatten()

            # Нормализация
            img = img / 255.0

            # Добавление размерности batch
            if len(img.shape) == 3:
                img = np.expand_dims(img, axis=0)
            elif len(img.shape) == 1:
                img = np.expand_dims(img, axis=0)

            # Запуск ONNX сессии
            sess = onnxruntime.InferenceSession(tmp_model_path)

            # Предсказание
            outputOfModel = sess.run(None, {"input": img})
            outputOfModel = np.argmax(outputOfModel[0])

            score = imageClassList[str(outputOfModel)]
            return score

        finally:
            # Удаление временной директории со всеми файлами
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

    except Exception as e:
        return f"Ошибка: {str(e)}"


@csrf_exempt
def model_upload_api(request):
    """API для загрузки модели через frontend"""
    from django.http import JsonResponse
    from django.contrib import messages

    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED"}, status=405)

    if "modelFile" not in request.FILES:
        return JsonResponse({"error": "NO_FILE"}, status=400)

    model_file = request.FILES["modelFile"]

    if not model_file.name.endswith(".onnx"):
        return JsonResponse({"error": "INVALID_FORMAT"}, status=400)

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

        return JsonResponse({"success": True, "model": model_file.name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def model_delete_api(request):
    """API для удаления модели"""
    from django.http import JsonResponse

    if request.method != "DELETE" and request.method != "GET":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED"}, status=405)

    model_name = request.GET.get("delete_model") or request.DELETE.get("delete_model")
    if not model_name:
        return JsonResponse({"error": "NO_MODEL_NAME"}, status=400)

    try:
        storage = default_storage
        s3 = storage.connection
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

        full_key = f"media/models/{model_name}"
        objs = list(bucket.objects.filter(Prefix=full_key))

        if not objs:
            return JsonResponse({"error": "MODEL_NOT_FOUND"}, status=404)

        bucket.delete_objects(Delete={"Objects": [{"Key": full_key}]})

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
