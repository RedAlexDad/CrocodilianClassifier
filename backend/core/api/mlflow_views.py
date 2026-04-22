"""
API endpoints для работы с MLflow
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os

from ..services.mlflow_service import (
    get_mlflow_runs,
    download_mlflow_model
)


def get_mlflow_runs_api(request):
    """API: получить список RUN_ID из MLflow с метаданными"""
    try:
        runs = get_mlflow_runs()
        return JsonResponse({"runs": runs})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def download_mlflow_model_api(request):
    """API: скачать модель из MLflow и сохранить в Django"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    run_id = request.POST.get("run_id")
    if not run_id:
        return JsonResponse({"error": "run_id required"}, status=400)

    try:
        local_path, model_name = download_mlflow_model(run_id)
        
        if not local_path:
            return JsonResponse({"error": model_name}, status=404)

        storage = default_storage
        model_key = f"models/{model_name}"
        with open(local_path, "rb") as f:
            storage.save(model_key, ContentFile(f.read()))

        os.remove(local_path)

        return JsonResponse({"success": True, "model": model_name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
