"""
API endpoints для работы с моделями
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..services.model_service import (
    get_available_models,
    upload_model_to_storage,
    delete_model_from_storage
)


def get_models_api(request):
    """API: получить список доступных моделей"""
    models = get_available_models()
    return JsonResponse({"models": models})


@csrf_exempt
def model_upload_api(request):
    """API для загрузки модели через frontend"""
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED"}, status=405)

    if "modelFile" not in request.FILES:
        return JsonResponse({"error": "NO_FILE"}, status=400)

    model_file = request.FILES["modelFile"]

    if not model_file.name.endswith(".onnx"):
        return JsonResponse({"error": "INVALID_FORMAT"}, status=400)

    success, error = upload_model_to_storage(model_file)
    
    if success:
        return JsonResponse({"success": True, "model": model_file.name})
    else:
        return JsonResponse({"error": error}, status=500)


@csrf_exempt
def model_delete_api(request):
    """API для удаления модели"""
    if request.method != "DELETE" and request.method != "GET":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED"}, status=405)

    model_name = request.GET.get("delete_model") or request.DELETE.get("delete_model")
    if not model_name:
        return JsonResponse({"error": "NO_MODEL_NAME"}, status=400)

    success, error = delete_model_from_storage(model_name)
    
    if success:
        return JsonResponse({"success": True})
    elif error == "MODEL_NOT_FOUND":
        return JsonResponse({"error": error}, status=404)
    else:
        return JsonResponse({"error": error}, status=500)
