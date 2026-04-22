from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services.model_service import get_available_models, pick_model_for_request
from .services.inference_service import predict_image

# Классы по вашему варианту: крокодил, аллигатор, кайман
imageClassList = {"0": "Крокодил", "1": "Аллигатор", "2": "Кайман"}


def scoreImagePage(request):
    """Отображение страницы классификации"""
    available = get_available_models()
    posted = (request.POST.get("modelName") or "").strip()
    
    # Автовыбор модели
    if posted and posted in available:
        current = posted
    else:
        current = available[0] if available else ""
    
    context = {
        "available_models": available,
        "current_model": current,
    }
    return render(request, "scorepage.html", context)


@csrf_exempt
def predictImage(request):
    """Обработка загруженного изображения и предсказание"""
    if request.method != "POST":
        return redirect("scoreImagePage")

    # HTML-форма использует filePath; SPA может слать file — принимаем оба ключа.
    fileObj = request.FILES.get("filePath") or request.FILES.get("file")
    if fileObj:
        # Сохранение файла с использованием default_storage (S3 или локальное)
        file_path = f"images/{fileObj.name}"
        saved_path = default_storage.save(file_path, fileObj)

        # Получаем URL через хранилище
        image_url = default_storage.url(saved_path)

        # Выбор модели
        model_name = pick_model_for_request(request)
        if not model_name:
            return JsonResponse(
                {"error": "No models available"}, 
                status=500
            )

        # Предсказание через сервис
        result = predict_image(model_name, saved_path)
        
        if "error" in result:
            return JsonResponse(result, status=500)

        predicted_class = result["predicted_class"]
        confidence = result["confidence"]
        class_name = imageClassList.get(str(predicted_class), "Unknown")

        return JsonResponse({
            "predictedLabel": class_name,
            "confidence": f"{confidence:.2%}",
            "imageUrl": image_url,
        })

    return JsonResponse({"error": "No file uploaded"}, status=400)


@csrf_exempt
def uploadModel(request):
    """Загрузка ONNX модели (legacy endpoint для HTML формы)"""
    if request.method != "POST":
        return redirect("scoreImagePage")

    model_file = request.FILES.get("modelFile")
    if not model_file:
        return JsonResponse({"error": "No model file provided"}, status=400)

    if not model_file.name.endswith(".onnx"):
        return JsonResponse({"error": "Only .onnx files are supported"}, status=400)

    try:
        # Сохраняем модель
        model_path = f"models/{model_file.name}"
        default_storage.save(model_path, model_file)

        return JsonResponse({
            "success": True,
            "message": f"Model {model_file.name} uploaded successfully"
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def uploadModelFromMLflow(request):
    """Загрузка модели из MLflow (legacy endpoint для HTML формы)"""
    if request.method != "POST":
        return redirect("scoreImagePage")

    run_id = request.POST.get("run_id")
    if not run_id:
        return JsonResponse({"error": "run_id required"}, status=400)

    # Используем API endpoint для загрузки
    from .api.mlflow_views import download_mlflow_model_api
    return download_mlflow_model_api(request)
