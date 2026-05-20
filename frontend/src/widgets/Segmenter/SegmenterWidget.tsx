import type { AppDispatch, RootState } from "@/app/store/store";
import { Loader2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { CLASS_COLORS, drawMasksOnCanvas } from "@/features/segmentation/segmentUtils";
import { cropDetection, canvasToDataUrl } from "@/features/segmentation/cropUtils";
import { useCardSearch } from "@/hooks/useCardSearch";
import type { Detection } from "@/features/segmentation/segmentUtils";
import "./SegmenterWidget.css";

export function SegmenterWidget() {
  const dispatch = useDispatch<AppDispatch>();
  const { imageUrl, detections, isLoading, error } = useSelector(
    (state: RootState) => state.segmenter,
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [showMask, setShowMask] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const [searchingIdx, setSearchingIdx] = useState<number | null>(null);
  const { results: cardResults, isLoading: cardsLoading, searchCards } = useCardSearch();
  const [searchedDetIdx, setSearchedDetIdx] = useState<number | null>(null);

  const drawDetections = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    if (!canvas || !img || detections.length === 0) return;
    if (!showMask) {
      const ctx = canvas.getContext("2d")!;
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      ctx.drawImage(img, 0, 0);
      return;
    }
    drawMasksOnCanvas(canvas, img, detections);
  }, [detections, showMask]);

  useEffect(() => {
    if (imageUrl && detections.length > 0) {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => {
        imageRef.current = img;
        drawDetections();
      };
      img.src = imageUrl;
    }
  }, [imageUrl, detections, drawDetections]);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith("image/")) return;
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      dispatch({ type: "segmenter/setSegImage", payload: { url } });
    },
    [dispatch],
  );

  const handleSubmit = useCallback(async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("filePath", selectedFile);

    dispatch({ type: "segmenter/segment/pending" });

    try {
      const response = await fetch("/api/segment", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        dispatch({
          type: "segmenter/segment/rejected",
          payload: { message: data.error || `Ошибка ${response.status}` },
        });
        return;
      }

      const data = await response.json();
      dispatch({
        type: "segmenter/segment/fulfilled",
        payload: data,
      });
    } catch (err) {
      dispatch({
        type: "segmenter/segment/rejected",
        payload: { message: (err as Error).message || "Ошибка сегментации" },
      });
    }
  }, [dispatch, selectedFile]);

  const handleClear = useCallback(() => {
    setSelectedFile(null);
    dispatch({ type: "segmenter/clearSegmentation" });
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext("2d");
      if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }, [dispatch]);

  const handleFindCards = useCallback(async (detection: Detection, idx: number) => {
    const img = imageRef.current;
    if (!img) return;
    setSearchingIdx(idx);
    setSearchedDetIdx(null);
    try {
      const cropCanvas = cropDetection(img, detection);
      const dataUrl = canvasToDataUrl(cropCanvas);
      await searchCards(dataUrl, detection.class_id);
      setSearchedDetIdx(idx);
    } finally {
      setSearchingIdx(null);
    }
  }, [searchCards]);

  const CLASS_NAMES_RU = ["Аллигатор", "Кайман", "Крокодил"];

  return (
    <div className="segmenter-widget">
      <div className="content">
        <div className="upload-form">
          <h2>Сегментация изображений</h2>
          <label className="form-label">
            Загрузите изображение для сегментации:
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            ref={fileInputRef}
            style={{ display: "none" }}
          />
          <div className="custom-file-upload">
            <button
              type="button"
              className="custom-file-button"
              onClick={() => fileInputRef.current?.click()}
            >
              Выбрать файл
            </button>
            <span className="file-name">
              {selectedFile ? selectedFile.name : "Файл не выбран"}
            </span>
          </div>

          <div className="segment-actions">
            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={!selectedFile || isLoading}
            >
              {isLoading ? "Сегментация..." : "Сегментировать"}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={!imageUrl}
            >
              Очистить
            </button>
          </div>

          {detections.length > 0 && (
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={showMask}
                onChange={(e) => setShowMask(e.target.checked)}
              />
              Показать маски
            </label>
          )}
        </div>

        {isLoading && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Идет сегментация...</p>
          </div>
        )}

        {error && <div className="message error">{error}</div>}

        {imageUrl && (
          <div className="canvas-container">
            <canvas ref={canvasRef} className="segment-canvas" />
            <img
              ref={imageRef}
              src={imageUrl}
              alt="Original"
              className="hidden-img"
              onLoad={drawDetections}
              crossOrigin="anonymous"
            />
          </div>
        )}

        {detections.length > 0 && (
          <div className="results-list">
            <h3>Обнаруженные объекты:</h3>
            {detections.map((det, idx) => {
              const color = CLASS_COLORS[det.class_id] || { r: 128, g: 128, b: 128 };
              return (
                <div key={idx} className="result-item">
                  <span
                    className="color-badge"
                    style={{ backgroundColor: `rgb(${color.r},${color.g},${color.b})` }}
                  />
                  <span className="class-name">{det.class_name}</span>
                  <span className="confidence">
                    {(det.confidence * 100).toFixed(1)}%
                  </span>
                  <button
                    className="btn btn-small btn-card-search"
                    onClick={() => handleFindCards(det, idx)}
                    disabled={searchingIdx === idx}
                  >
                    {searchingIdx === idx ? "Поиск..." : "Найти карточки"}
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {cardsLoading && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Поиск похожих карточек через CLIP...</p>
          </div>
        )}

        {cardResults.length > 0 && searchedDetIdx !== null && detections[searchedDetIdx] && (
          <div className="cards-section">
            <h3>
              Похожие карточки для: {CLASS_NAMES_RU[detections[searchedDetIdx].class_id]}
            </h3>
            <div className="cards-grid">
              {cardResults.map((card) => {
                const cardClassId = Math.floor((card.card_id - 1) / 12);
                const color = CLASS_COLORS[cardClassId] || { r: 128, g: 128, b: 128 };
                return (
                  <div key={card.card_id} className="card-item">
                    <div className="card-header">
                      <div className="card-number" style={{ backgroundColor: `rgb(${color.r},${color.g},${color.b})` }}>
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
        )}
      </div>
    </div>
  );
}
