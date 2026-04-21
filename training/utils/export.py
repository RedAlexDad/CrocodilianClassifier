"""
Экспорт моделей в ONNX
"""
import torch
import onnx
import onnxruntime as ort
from pathlib import Path


def export_to_onnx(model, model_name, onnx_path, input_shape, device):
    """
    Экспорт модели в ONNX формат с проверкой
    
    Args:
        model: Обученная модель
        model_name: Название модели для логов
        onnx_path: Путь для сохранения
        input_shape: Форма входа (C, H, W) или (H, W, C)
        device: Устройство
    """
    print(f"\n{'='*60}")
    print(f"Экспорт {model_name} в ONNX: {onnx_path}")
    print(f"{'='*60}")
    
    model.eval()
    onnx_path = Path(onnx_path)
    
    # Создаем фиктивный вход
    if len(input_shape) == 3:
        if input_shape[0] == 3:  # CHW
            dummy_input = torch.randn(1, *input_shape).to(device)
        else:  # HWC
            dummy_input = torch.randn(1, *input_shape).to(device)
    else:
        dummy_input = torch.randn(1, *input_shape).to(device)
    
    # Временный файл для экспорта
    temp_path = str(onnx_path) + '.tmp'
    
    # Экспорт модели
    torch.onnx.export(
        model,
        dummy_input,
        temp_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    # Если создан файл с данными (.data), объединяем в один файл
    data_path = temp_path + '.data'
    if Path(data_path).exists():
        print("  Объединение весов в один файл...")
        onnx_model = onnx.load(temp_path)
        onnx.save_model(onnx_model, str(onnx_path), save_as_external_data=False)
        Path(temp_path).unlink(missing_ok=True)
        Path(data_path).unlink(missing_ok=True)
    else:
        Path(temp_path).replace(str(onnx_path))
    
    # Проверка модели
    try:
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        print(f"✓ ONNX модель валидна")
        
        # Тестовый запуск
        sess = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        input_name = sess.get_inputs()[0].name
        output_name = sess.get_outputs()[0].name
        
        dummy_cpu = dummy_input.cpu().numpy()
        ort_inputs = {input_name: dummy_cpu}
        ort_outs = sess.run([output_name], ort_inputs)
        
        print(f"✓ ONNX модель успешно протестирована")
        print(f"  Размер файла: {onnx_path.stat().st_size / 1024 / 1024:.2f} MB")
        
    except Exception as e:
        print(f"⚠ Предупреждение при проверке ONNX: {e}")
    
    print(f"{'='*60}\n")
    return onnx_path
