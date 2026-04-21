import { useCallback, useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import './GalleryWidget.css';

interface ImageItem {
  filename: string;
  url: string;
  size: number;
  last_modified: string;
}

interface PredictionResult {
  scorePrediction: string;
  image_url: string;
  current_model: string;
}

export function GalleryWidget() {
  const [images, setImages] = useState<ImageItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<ImageItem | null>(null);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState('');

  const loadImages = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log('Загрузка изображений из /api/images...');
      const response = await fetch('/api/images');
      console.log('Ответ от /api/images:', response.status);
      if (!response.ok) {
        throw new Error(`Ошибка ${response.status}`);
      }
      const data = await response.json();
      console.log('Получено изображений:', data.images?.length || 0);
      setImages(data.images || []);
    } catch (err) {
      console.error('Ошибка загрузки изображений:', err);
      setError((err as Error).message || 'Ошибка загрузки изображений');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadModels = useCallback(async () => {
    try {
      const response = await fetch('/api/models');
      const data = await response.json();
      if (data.models && data.models.length > 0) {
        const names = data.models.map((m: string | {name: string}) =>
          typeof m === 'string' ? m : m.name
        );
        setAvailableModels(names);
        setSelectedModel(names[0]);
      }
    } catch (err) {
      console.error('Ошибка загрузки моделей:', err);
    }
  }, []);

  useEffect(() => {
    loadImages();
    loadModels();
  }, [loadImages, loadModels]);

  const handleImageClick = useCallback(async (image: ImageItem) => {
    setSelectedImage(image);
    setPrediction(null);
    setIsPredicting(true);

    try {
      const response = await fetch('/api/predict-existing', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_path: `images/${image.filename}`,
          model_name: selectedModel,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || `Ошибка ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError((err as Error).message || 'Ошибка классификации');
    } finally {
      setIsPredicting(false);
    }
  }, [selectedModel]);

  return (
    <div className="gallery-widget">
      <div className="content">
        <h2>Галерея загруженных изображений</h2>

        {availableModels.length > 0 && (
          <div className="model-selector">
            <label className="form-label">Модель для классификации:</label>
            <select
              value={selectedModel}
              onChange={e => setSelectedModel(e.target.value)}
            >
              {availableModels.map(name => (
                <option key={name} value={name}>{name}</option>
              ))}
            </select>
          </div>
        )}

        {isLoading && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Загрузка изображений...</p>
          </div>
        )}

        {error && !isPredicting && (
          <div className="message error">{error}</div>
        )}

        {!isLoading && images.length === 0 && (
          <div className="no-images">
            <p>Нет загруженных изображений. Загрузите изображение на странице <a href="/">Классификация</a></p>
          </div>
        )}

        {images.length > 0 && (
          <div className="images-grid">
            {images.map((image) => (
              <div
                key={image.filename}
                className={`image-card ${selectedImage?.filename === image.filename ? 'selected' : ''}`}
                onClick={() => handleImageClick(image)}
              >
                <img src={image.url} alt={image.filename} />
                <div className="image-info">
                  <p className="filename">{image.filename}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {isPredicting && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Классификация...</p>
          </div>
        )}

        {prediction && selectedImage && (
          <div className="result">
            <h3>Результат классификации:</h3>
            <div className="result-content">
              <img
                src={selectedImage.url}
                alt={selectedImage.filename}
                className="result-image"
              />
              <div className="prediction-info">
                <div className="prediction">{prediction.scorePrediction}</div>
                <p className="model-used">Модель: {prediction.current_model}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
