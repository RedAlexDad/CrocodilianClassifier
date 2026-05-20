import { useCallback, useState, useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';
import { CLASS_COLORS, drawMasksOnCanvas, type Detection } from '@/features/segmentation/segmentUtils';
import { cropDetection, canvasToDataUrl } from '@/features/segmentation/cropUtils';
import { useCardSearch } from '@/hooks/useCardSearch';
import type { CardMatch } from '@/hooks/useCardSearch';
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

const CLASS_NAMES_RU = ['Аллигатор', 'Кайман', 'Крокодил'];

function CardsSection({ results, detClassId }: { results: CardMatch[]; detClassId: number }) {
  return (
    <div className="cards-section">
      <h3>Похожие карточки для: {CLASS_NAMES_RU[detClassId]}</h3>
      <div className="cards-grid">
        {results.map((card) => {
          const cardClassId = Math.floor((card.card_id - 1) / 12);
          const color = CLASS_COLORS[cardClassId] || { r: 128, g: 128, b: 128 };
          return (
            <div key={card.card_id} className="card-item">
              <div className="card-header">
                <div
                  className="card-number"
                  style={{ backgroundColor: `rgb(${color.r},${color.g},${color.b})` }}
                >
                  {card.card_id}
                </div>
                <span className="card-similarity">
                  {(card.similarity * 100).toFixed(1)}%
                </span>
              </div>
              <div className="card-title">{card.title}</div>
              <div className="card-desc">{card.description}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
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
  const [segDetections, setSegDetections] = useState<Detection[]>([]);
  const [isSegmenting, setIsSegmenting] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const segImageRef = useRef<HTMLImageElement>(null);
  const [searchingIdx, setSearchingIdx] = useState<number | null>(null);
  const { results: cardResults, isLoading: cardsLoading, searchCards } = useCardSearch();
  const [searchedDetIdx, setSearchedDetIdx] = useState<number | null>(null);

  const loadImages = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/images');
      if (!response.ok) {
        throw new Error(`Ошибка ${response.status}`);
      }
      const data = await response.json();
      setImages(data.images || []);
    } catch (err) {
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
    setSegDetections([]);
    setIsPredicting(true);

    try {
      const response = await fetch('/api/predict-existing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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

  const handleSegment = useCallback(async () => {
    if (!selectedImage) return;
    setIsSegmenting(true);
    setSegDetections([]);

    try {
      const response = await fetch('/api/segment-existing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_path: `images/${selectedImage.filename}`,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || `Ошибка ${response.status}`);
      }

      const data = await response.json();
      setSegDetections(data.detections || []);
    } catch (err) {
      setError((err as Error).message || 'Ошибка сегментации');
    } finally {
      setIsSegmenting(false);
    }
  }, [selectedImage]);

  const drawSegCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const img = segImageRef.current;
    if (!canvas || !img || segDetections.length === 0) return;
    drawMasksOnCanvas(canvas, img, segDetections);
  }, [segDetections]);

  const handleFindCards = useCallback(async (detection: Detection, idx: number) => {
    const img = segImageRef.current;
    if (!img) return;
    setSearchingIdx(idx);
    setSearchedDetIdx(null);
    try {
      const cropCanvas = cropDetection(img, detection);
      const dataUrl = canvasToDataUrl(cropCanvas);
      await searchCards(dataUrl);
      setSearchedDetIdx(idx);
    } finally {
      setSearchingIdx(null);
    }
  }, [searchCards]);

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

        {error && (
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
            <div className="segment-action">
              <button
                className="btn btn-segment"
                onClick={handleSegment}
                disabled={isSegmenting}
              >
                {isSegmenting ? 'Сегментация...' : 'Сегментировать'}
              </button>
            </div>
          </div>
        )}

        {isSegmenting && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Сегментация...</p>
          </div>
        )}

        {segDetections.length > 0 && selectedImage && (
          <div className="result seg-result">
            <h3>Результат сегментации:</h3>
            <div className="canvas-container">
              <canvas ref={canvasRef} className="segment-canvas" />
              <img
                ref={segImageRef}
                src={selectedImage.url}
                alt={selectedImage.filename}
                className="hidden-img"
                onLoad={drawSegCanvas}
                crossOrigin="anonymous"
              />
            </div>
            <div className="seg-detections">
              {segDetections.map((det, idx) => {
                const color = CLASS_COLORS[det.class_id] || { r: 128, g: 128, b: 128 };
                return (
                  <div key={idx} className="seg-item">
                    <span className="color-badge" style={{ backgroundColor: `rgb(${color.r},${color.g},${color.b})` }} />
                    <span className="class-name">{det.class_name}</span>
                    <span className="confidence">{(det.confidence * 100).toFixed(1)}%</span>
                    <button
                      className="btn btn-small btn-card-search"
                      onClick={() => handleFindCards(det, idx)}
                      disabled={searchingIdx === idx}
                    >
                      {searchingIdx === idx ? 'Поиск...' : 'Найти карточки'}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {cardsLoading && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Поиск похожих карточек через CLIP...</p>
          </div>
        )}

        {cardResults.length > 0 && searchedDetIdx !== null && segDetections[searchedDetIdx] && (
          <CardsSection
            results={cardResults}
            detClassId={segDetections[searchedDetIdx].class_id}
          />
        )}
      </div>
    </div>
  );
}
