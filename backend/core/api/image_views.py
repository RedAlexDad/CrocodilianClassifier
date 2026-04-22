"""
API endpoints для работы с изображениями
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from ..services.image_service import get_uploaded_images, save_uploaded_image
from ..services.inference_service import predict_image
from ..services.model_service import pick_model_for_request


def get_uploaded_images_api(request):
    """API: получить список всех загруженных изображений из MinIO"""
    try:
        images = get_uploaded_images()
        return JsonResponse({"images": images})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def predict_existing_image_api(request):
    """API: классифицировать уже загруженное изображение по URL"""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    image_path = data.get("image_path")
    model_name = data.get("model_name")

    if not image_path:
        return JsonResponse({"error": "image_path required"}, status=400)

    if not model_name:
        model_name = pick_model_for_request(request)

    if not model_name:
        return JsonResponse({
            "error": "Нет доступных моделей"
        }, status=400)

    try:
        from django.core.files.storage import default_storage

        result = predict_image(model_name, image_path)

        if "error" in result:
            return JsonResponse(result, status=500)

        # Преобразуем predicted_class в название класса
        imageClassList = {"0": "Крокодил", "1": "Аллигатор", "2": "Кайман"}
        predicted_class = result["predicted_class"]
        confidence = result["confidence"]
        class_name = imageClassList.get(str(predicted_class), "Unknown")

        image_url = default_storage.url(image_path)

        return JsonResponse({
            "scorePrediction": class_name,
            "confidence": f"{confidence:.2%}",
            "image_url": image_url,
            "current_model": model_name
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
