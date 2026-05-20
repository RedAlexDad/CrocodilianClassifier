import base64
import io
import json
from PIL import Image

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.services.clip_service import search_similar_cards


@csrf_exempt
@require_POST
def card_search_api(request):
    try:
        body = json.loads(request.body)
        image_data = body.get("image_data")
        top_k = body.get("top_k", 5)
        class_id = body.get("class_id")

        if not image_data:
            return JsonResponse({"error": "image_data is required"}, status=400)

        if "," in image_data:
            image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        results = search_similar_cards(image, top_k=top_k, class_id=class_id)

        return JsonResponse({
            "results": results,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
