import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

from ..services.segmentation_service import segment_image
from ..services.image_service import save_uploaded_image


@csrf_exempt
def segment_image_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED"}, status=405)

    file_obj = request.FILES.get("filePath") or request.FILES.get("file")
    if not file_obj:
        return JsonResponse({"error": "NO_FILE"}, status=400)

    saved_path, image_url = save_uploaded_image(file_obj)

    result = segment_image(saved_path)

    if "error" in result:
        return JsonResponse(result, status=500)

    return JsonResponse({
        "image_url": image_url,
        "detections": result["detections"],
    })


@csrf_exempt
def segment_existing_image_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "METHOD_NOT_ALLOWED"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "INVALID_JSON"}, status=400)

    image_path = data.get("image_path")
    if not image_path:
        return JsonResponse({"error": "image_path required"}, status=400)

    result = segment_image(image_path)

    if "error" in result:
        return JsonResponse(result, status=500)

    image_url = default_storage.url(image_path)

    return JsonResponse({
        "image_url": image_url,
        "detections": result["detections"],
    })
