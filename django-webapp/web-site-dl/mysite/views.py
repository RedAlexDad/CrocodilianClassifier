from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import onnxruntime
import numpy as np
from PIL import Image
import os

# Классы по вашему варианту: крокодил, аллигатор, кайман
imageClassList = {
    '0': 'Крокодил',
    '1': 'Аллигатор',
    '2': 'Кайман'
}

def get_available_models():
    """Получение списка доступных ONNX моделей"""
    if settings.USE_S3:
        # S3 режим - получаем список из S3 через default_storage
        try:
            storage = default_storage
            # location уже установлен в 'media', поэтому ищем в 'models/'
            prefix = f'{storage.location}/models/'
            
            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
            
            models = []
            for obj in bucket.objects.filter(Prefix=prefix):
                key = obj.key.replace(prefix, '')
                if key.endswith('.onnx') and '/' not in key:
                    models.append(key)
            
            return models if models else ['cifar100.onnx']
        except Exception as e:
            print(f'Ошибка получения списка моделей: {e}')
            return ['cifar100.onnx']
    else:
        # Локальный режим
        models_dir = os.path.join(settings.BASE_DIR, 'media', 'models')
        if not os.path.exists(models_dir):
            return ['cifar100.onnx']
        
        models = [f for f in os.listdir(models_dir) if f.endswith('.onnx')]
        return models if models else ['cifar100.onnx']

def scoreImagePage(request):
    """Отображение страницы классификации"""
    context = {
        'available_models': get_available_models(),
        'current_model': request.POST.get('modelName', 'cifar100.onnx')
    }
    return render(request, 'scorepage.html', context)

def predictImage(request):
    """Обработка загруженного изображения и предсказание"""
    if request.method == 'POST' and 'filePath' in request.FILES:
        fileObj = request.FILES['filePath']

        # Сохранение файла с использованием default_storage (S3 или локальное)
        # default_storage уже имеет location='media', поэтому сохраняем просто в 'images/'
        file_path = f'images/{fileObj.name}'
        saved_path = default_storage.save(file_path, fileObj)
        
        # Получаем URL через хранилище (для S3 будет http://localhost:19000/dz1-media/media/images/...)
        file_url = default_storage.url(saved_path)

        # Получение имени модели (если выбрано)
        modelName = request.POST.get('modelName', 'cifar100.onnx')

        # Предсказание
        scorePrediction = predictImageData(modelName, saved_path)

        context = {
            'scorePrediction': scorePrediction,
            'image_url': file_url,
            'available_models': get_available_models(),
            'current_model': modelName
        }
        return render(request, 'scorepage.html', context)

    return redirect('scoreImagePage')

def uploadModel(request):
    """Страница загрузки и управления моделями"""
    from django.contrib import messages
    
    # Удаление модели
    if request.method == 'GET' and 'delete_model' in request.GET:
        model_to_delete = request.GET.get('delete_model')
        try:
            storage = default_storage
            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
            full_key = f'media/models/{model_to_delete}'
            
            # Проверка существования и удаление
            objs = list(bucket.objects.filter(Prefix=full_key))
            if objs:
                bucket.delete_objects(Delete={'Objects': [{'Key': full_key}]})
                messages.success(request, f'Модель {model_to_delete} успешно удалена')
            else:
                messages.error(request, f'Модель {model_to_delete} не найдена')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')
        
        return redirect('uploadModel')
    
    # Если выбрано использование модели
    if request.method == 'GET' and 'use_model' in request.GET:
        model_name = request.GET.get('use_model')
        messages.success(request, f'Модель {model_name} выбрана для классификации')
        return redirect('scoreImagePage')
    
    # Загрузка новой модели
    if request.method == 'POST' and 'modelFile' in request.FILES:
        model_file = request.FILES['modelFile']
        
        # Проверка расширения
        if not model_file.name.endswith('.onnx'):
            messages.error(request, 'Ошибка: Загрузите файл .onnx')
            return redirect('uploadModel')
        
        # Сохранение модели через boto3 напрямую
        try:
            storage = default_storage
            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
            
            model_key = f'media/models/{model_file.name}'
            bucket.upload_fileobj(
                model_file.file,
                model_key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': model_file.content_type or 'application/octet-stream'
                }
            )
            
            messages.success(request, f'Модель {model_file.name} успешно загружена!')
        except Exception as e:
            messages.error(request, f'Ошибка при загрузке: {str(e)}')
        
        return redirect('uploadModel')
    
    context = {
        'available_models': get_available_models()
    }
    return render(request, 'uploadmodel.html', context)

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
        model_key = f'media/models/{modelName}'
        model_base_name = modelName.replace('.onnx', '')
        
        # Создаём временную директорию для модели
        tmp_dir = tempfile.mkdtemp()
        
        try:
            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
            
            # Скачиваем основной файл модели и все связанные файлы (.data)
            for obj in bucket.objects.filter(Prefix=f'media/models/{model_base_name}'):
                # Извлекаем имя файла из ключа
                file_name = obj.key.replace('media/models/', '')
                tmp_file_path = os.path.join(tmp_dir, file_name)
                
                # Скачиваем файл
                with open(tmp_file_path, 'wb') as f:
                    bucket.download_fileobj(obj.key, f)
            
            # Путь к основному файлу модели
            tmp_model_path = os.path.join(tmp_dir, modelName)
            
            # Проверка формата входов модели
            onnx_model = onnx.load(tmp_model_path)
            input_shape = [d.dim_value if d.dim_value != 0 else -1 
                          for d in onnx_model.graph.input[0].type.tensor_type.shape.dim]
            
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
            outputOfModel = sess.run(None, {'input': img})
            outputOfModel = np.argmax(outputOfModel[0])
            
            score = imageClassList[str(outputOfModel)]
            return score
            
        finally:
            # Удаление временной директории со всеми файлами
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
                
    except Exception as e:
        return f"Ошибка: {str(e)}"
