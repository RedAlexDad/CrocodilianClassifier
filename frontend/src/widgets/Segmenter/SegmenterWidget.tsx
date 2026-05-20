import type { AppDispatch, RootState } from "@/app/store/store";
import { Loader2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import "./SegmenterWidget.css";

const CLASS_COLORS = [
  { r: 239, g: 68, b: 68, name: "red" },
  { r: 34, g: 197, b: 94, name: "green" },
  { r: 59, g: 130, b: 246, name: "blue" },
];

function decodeRle(rle: number[], height: number, width: number): Uint8Array {
  const mask = new Uint8Array(height * width);
  let idx = 0;
  for (let i = 0; i < rle.length; i++) {
    const val = i % 2;
    for (let j = 0; j < rle[i]; j++) {
      mask[idx++] = val;
    }
  }
  return mask;
}

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

  const drawDetections = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    if (!canvas || !img || detections.length === 0) return;

    const ctx = canvas.getContext("2d")!;
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;

    ctx.drawImage(img, 0, 0);

    if (!showMask) return;

    for (const det of detections) {
      const color = CLASS_COLORS[det.class_id] || { r: 128, g: 128, b: 128 };
      const [x1, y1, x2, y2] = det.bbox;
      const { rle, height, width } = det.mask;

      const mask = decodeRle(rle, height, width);

      const imageData = ctx.getImageData(x1, y1, width, height);

      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          const maskIdx = y * width + x;
          if (mask[maskIdx]) {
            const pixelIdx = (y * width + x) * 4;
            imageData.data[pixelIdx + 0] =
              imageData.data[pixelIdx + 0] * 0.5 + color.r * 0.5;
            imageData.data[pixelIdx + 1] =
              imageData.data[pixelIdx + 1] * 0.5 + color.g * 0.5;
            imageData.data[pixelIdx + 2] =
              imageData.data[pixelIdx + 2] * 0.5 + color.b * 0.5;
          }
        }
      }

      ctx.putImageData(imageData, x1, y1);

      ctx.strokeStyle = `rgb(${color.r},${color.g},${color.b})`;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      const label = `${det.class_name} (${(det.confidence * 100).toFixed(1)}%)`;
      ctx.font = "bold 16px sans-serif";
      const textMetrics = ctx.measureText(label);
      const labelH = 24;
      const labelY = y1 > labelH + 4 ? y1 - labelH - 2 : y1;

      ctx.fillStyle = `rgb(${color.r},${color.g},${color.b})`;
      ctx.fillRect(x1, labelY, textMetrics.width + 8, labelH);

      ctx.fillStyle = "#fff";
      ctx.fillText(label, x1 + 4, labelY + 17);
    }
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
              const color = CLASS_COLORS[det.class_id] || {
                r: 128,
                g: 128,
                b: 128,
              };
              return (
                <div key={idx} className="result-item">
                  <span
                    className="color-badge"
                    style={{
                      backgroundColor: `rgb(${color.r},${color.g},${color.b})`,
                    }}
                  />
                  <span className="class-name">{det.class_name}</span>
                  <span className="confidence">
                    {(det.confidence * 100).toFixed(1)}%
                  </span>
                  <span className="bbox-info">
                    bbox: [{det.bbox.join(", ")}]
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
