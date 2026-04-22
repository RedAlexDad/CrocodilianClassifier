"""
Сервис для инференса моделей
"""
import os
import tempfile
import shutil
import numpy as np
import onnxruntime
from PIL import Image
import onnx
from onnx.external_data_helper import load_external_data_for_model
from django.conf import settings
from django.core.files.storage import default_storage


# Классы по вашему варианту: крокодил, аллигатор, кайман
IMAGE_CLASS_LIST = {"0": "Крокодил", "1": "Аллигатор", "2": "Кайман"}


def predict_image(model_name, file_path):
    """
    Загрузка ONNX модели и предсказание класса изображения

    Args:
        model_name: Имя ONNX модели
        file_path: Путь к изображению в хранилище

    Returns:
        dict: {"predicted_class": int, "confidence": float} или {"error": str}
    """
    try:
        if not model_name:
            return {"error": "Ошибка: модель не выбрана"}

        # Загрузка модели из S3
        storage = default_storage
        model_base_name = model_name.replace(".onnx", "")

        # Создаём временную директорию для модели
        tmp_dir = tempfile.mkdtemp()

        try:
            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

            # Скачиваем основной файл модели и все связанные файлы (.data)
            for obj in bucket.objects.filter(Prefix=f"media/models/{model_base_name}"):
                file_name = obj.key.replace("media/models/", "")
                tmp_file_path = os.path.join(tmp_dir, file_name)

                with open(tmp_file_path, "wb") as f:
                    bucket.download_fileobj(obj.key, f)

            # Путь к основному файлу модели
            tmp_model_path = os.path.join(tmp_dir, model_name)
            if not os.path.isfile(tmp_model_path):
                return {"error": f"Ошибка: модель «{model_name}» не найдена в хранилище"}

            # Загружаем модель и определяем размер входа
            onnx_model = onnx.load(tmp_model_path, load_external_data=False)
            input_shape = [
                d.dim_value if d.dim_value != 0 else -1
                for d in onnx_model.graph.input[0].type.tensor_type.shape.dim
            ]

            # Определяем размер входа модели (height, width)
            img_size = _get_input_size(input_shape)

            # Загрузка и предобработка изображения с правильным размером
            img = Image.open(default_storage.open(file_path)).convert("RGB")
            img = img.resize((img_size, img_size), Image.LANCZOS)
            img = np.asarray(img, dtype=np.float32)

            # Подтягиваем внешние тензоры из tmp_dir в protobuf
            try:
                load_external_data_for_model(onnx_model, base_dir=tmp_dir)
                ort_bytes = onnx_model.SerializeToString()
                sess = onnxruntime.InferenceSession(
                    ort_bytes, providers=["CPUExecutionProvider"]
                )
            except Exception as ext_err:
                try:
                    sess = onnxruntime.InferenceSession(
                        tmp_model_path, providers=["CPUExecutionProvider"]
                    )
                except Exception:
                    return {
                        "error": f"Ошибка: не удалось загрузить веса модели «{model_name}» "
                        f"(внешние данные ONNX). Детали: {ext_err}"
                    }

            # Определение формата: NCHW или NHWC
            if len(input_shape) == 4 and input_shape[3] == 3:
                # NHWC формат - не транспонируем
                pass
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

            # Инференс
            input_name = sess.get_inputs()[0].name
            output = sess.run(None, {input_name: img})
            predicted_class = int(np.argmax(output[0]))

            # Вычисляем confidence
            probabilities = output[0][0]
            if len(probabilities.shape) > 0:
                confidence = float(np.max(probabilities))
            else:
                confidence = 1.0

            return {
                "predicted_class": predicted_class,
                "confidence": confidence,
            }

        finally:
            # Удаление временной директории со всеми файлами
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

    except Exception as e:
        return {"error": f"Ошибка: {str(e)}"}


def _get_input_size(input_shape):
    """Определить размер входа модели из shape"""
    if len(input_shape) == 4:
        if input_shape[1] == 3:  # NCHW: [batch, channels, height, width]
            img_size = input_shape[2] if input_shape[2] > 0 else 32
        elif input_shape[3] == 3:  # NHWC: [batch, height, width, channels]
            img_size = input_shape[1] if input_shape[1] > 0 else 32
        else:
            img_size = 32
    else:
        img_size = 32
    return img_size
