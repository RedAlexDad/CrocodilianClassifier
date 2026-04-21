import { useCallback, useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Loader2 } from 'lucide-react';
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
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const modelSelectRef = useRef<HTMLSelectElement>(null);

  const loadModels = useCallback(() => {
    fetch('/api/models')
      .then(res => res.json())
      .then(data => {
        if (data.models && data.models.length > 0) {
          const names = data.models.map((m: string | {name: string}) =>
            typeof m === 'string' ? m : m.name
          );
          setAvailableModels(names);
        } else {
          setAvailableModels([]);
        }
      })
      .catch(() => {
        setAvailableModels([]);
      });
  }, []);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

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
    formData.append('filePath', selectedFile);
    const modelName =
      modelSelectRef.current?.value ||
      availableModels[0] ||
      '';
    if (modelName) {
      formData.append('modelName', modelName);
    }

    dispatch({ type: 'classifier/classify/pending' });

    try {
      const response = await fetch('/predictImage', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
        },
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        dispatch({
          type: 'classifier/classify/rejected',
          payload: { message: data.error || `Ошибка ${response.status}` },
        });
        return;
      }
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
  }, [dispatch, selectedFile, availableModels]);

  const handleClear = useCallback(() => {
    setSelectedFile(null);
    dispatch({ type: 'classifier/clearPrediction' });
  }, [dispatch]);

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
          {availableModels.length === 0 ? (
            <div className="no-models-warning">
              <p>⚠️ Нет доступных моделей. Загрузите модель через <a href="/models">Управление моделями</a></p>
            </div>
          ) : (
            <select ref={modelSelectRef} name="modelName">
              {availableModels.map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          )}

          <input
            type="submit"
            value={isLoading ? 'Классификация...' : 'Классифицировать'}
            onClick={handleSubmit}
            disabled={!selectedFile || isLoading || availableModels.length === 0}
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