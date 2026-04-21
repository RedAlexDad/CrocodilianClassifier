import { useCallback, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Upload, Loader2, X } from 'lucide-react';
import type { RootState } from '@/app/store/store';
import type { AppDispatch } from '@/app/store/store';
import './ClassifierWidget.css';

interface PredictionResult {
  scorePrediction: string;
  image_url: string;
}

export function ClassifierWidget() {
  const dispatch = useDispatch<AppDispatch>();
  const { imageUrl, prediction, isLoading, error } = useSelector(
    (state: RootState) => state.classifier
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith('image/')) return;
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      dispatch({ type: 'classifier/setSelectedFile', payload: { url } });
    },
    [dispatch]
  );

  const handleSubmit = useCallback(async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    dispatch({ type: 'classifier/classify/pending' });

    try {
      const response = await fetch('/predictImage', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      dispatch({
        type: 'classifier/classify/fulfilled',
        payload: data,
      });
    } catch (err) {
      dispatch({
        type: 'classifier/classify/rejected',
        payload: { message: (err as Error).message || 'Ошибка классификации' },
      });
    }
  }, [dispatch, selectedFile]);

  const handleClear = useCallback(() => {
    setSelectedFile(null);
    dispatch({ type: 'classifier/clearPrediction' });
  }, [dispatch]);

  const classLabels = ['Крокодил', 'Аллигатор', 'Кайман'];

  return (
    <div className="classifier-widget">
      <div className="content">
        <div className="upload-form">
          <label className="form-label">
            Загрузите изображение для классификации:
          </label>
          <input
            type="file"
            name="filePath"
            accept="image/*"
            onChange={handleFileChange}
          />

          <label className="form-label" style={{ marginTop: '15px' }}>
            Выберите модель:
          </label>
          <select name="modelName">
            <option value="cnn">CNN Model</option>
            <option value="mlp">MLP Model</option>
            <option value="resnet20">ResNet20</option>
          </select>

          <a href="http://localhost:8000/uploadModel" className="manage-models-link">
            Управление моделями →
          </a>

          <input
            type="submit"
            value={isLoading ? 'Классификация...' : 'Классифицировать'}
            onClick={handleSubmit}
            disabled={!selectedFile || isLoading}
          />
        </div>

        {isLoading && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Идет классификация...</p>
          </div>
        )}

        {error && (
          <div className="message error">{error}</div>
        )}

        {prediction && (
          <div className="result">
            {imageUrl && (
              <img
                src={imageUrl}
                alt="Загруженное изображение"
                className="result-image"
              />
            )}
            <h3>Результат классификации:</h3>
            <div className="prediction">{prediction.scorePrediction}</div>
          </div>
        )}

        <div className="classes-info">
          <h4>О наборе данных</h4>
          <p>Данная модель обучена классифицировать изображения трёх классов:</p>
          <ul>
            <li><strong>Крокодил</strong> (класс 0)</li>
            <li><strong>Аллигатор</strong> (класс 1)</li>
            <li><strong>Кайман</strong> (класс 2)</li>
          </ul>
          <p><strong>Требования к изображению:</strong></p>
          <ul>
            <li>Формат: JPG, PNG</li>
            <li>Изображение будет автоматически масштабировано до 32x32 пикселей</li>
          </ul>
        </div>
      </div>
    </div>
  );
}