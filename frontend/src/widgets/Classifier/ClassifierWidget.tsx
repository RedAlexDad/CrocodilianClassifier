import type { AppDispatch, RootState } from "@/app/store/store";
import { Loader2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import "./ClassifierWidget.css";

interface PredictionResult {
  scorePrediction: string;
  image_url: string;
}

export function ClassifierWidget() {
  const dispatch = useDispatch<AppDispatch>();
  const { imageUrl, prediction, isLoading, error } = useSelector(
    (state: RootState) => state.classifier,
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadModels = useCallback(() => {
    fetch("/api/models")
      .then((res) => res.json())
      .then((data) => {
        if (data.models && data.models.length > 0) {
          const names = data.models.map((m: string | { name: string }) =>
            typeof m === "string" ? m : m.name,
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

  useEffect(() => {
    if (availableModels.length === 0) {
      setSelectedModel("");
      return;
    }
    setSelectedModel((prev) =>
      prev && availableModels.includes(prev) ? prev : availableModels[0],
    );
  }, [availableModels]);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!file.type.startsWith("image/")) return;
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      dispatch({ type: "classifier/setSelectedFile", payload: { url } });
    },
    [dispatch],
  );

  const handleSubmit = useCallback(async () => {
    if (!selectedFile) return;

    const modelToSend = selectedModel || availableModels[0] || "";
    if (!modelToSend) {
      dispatch({
        type: "classifier/classify/rejected",
        payload: { message: "Нет доступных моделей" },
      });
      return;
    }

    const formData = new FormData();
    formData.append("filePath", selectedFile);
    formData.append("modelName", modelToSend);

    dispatch({ type: "classifier/classify/pending" });

    try {
      const response = await fetch("/predictImage", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        dispatch({
          type: "classifier/classify/rejected",
          payload: { message: data.error || `Ошибка ${response.status}` },
        });
        return;
      }

      const data = await response.json();
      dispatch({
        type: "classifier/classify/fulfilled",
        payload: data,
      });
    } catch (err) {
      dispatch({
        type: "classifier/classify/rejected",
        payload: { message: (err as Error).message || "Ошибка классификации" },
      });
    }
  }, [dispatch, selectedFile, availableModels, selectedModel]);

  const handleClear = useCallback(() => {
    setSelectedFile(null);
    dispatch({ type: "classifier/clearPrediction" });
  }, [dispatch]);

  const handleCustomButtonClick = () => {
    fileInputRef.current?.click();
  };

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
            ref={fileInputRef}
            style={{ display: "none" }}
          />
          <div className="custom-file-upload">
            <button
              type="button"
              className="custom-file-button"
              onClick={handleCustomButtonClick}
            >
              Выбрать файл
            </button>
            <span className="file-name">
              {selectedFile ? selectedFile.name : "Файл не выбран"}
            </span>
          </div>

          {selectedFile && imageUrl && (
            <div className="image-preview">
              <img src={imageUrl} alt="Выбранное изображение" />
            </div>
          )}

          <label className="form-label" style={{ marginTop: "15px" }}>
            Выберите модель:
          </label>
          {availableModels.length === 0 ? (
            <div className="no-models-warning">
              <p>
                ⚠️ Нет доступных моделей. Загрузите модель через{" "}
                <a href="/models">Управление моделями</a>
              </p>
            </div>
          ) : (
            <select
              name="modelName"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              {availableModels.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          )}

          <input
            type="submit"
            value={isLoading ? "Классификация..." : "Классифицировать"}
            onClick={handleSubmit}
            disabled={
              !selectedFile || isLoading || availableModels.length === 0
            }
          />
        </div>

        {isLoading && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Идет классификация...</p>
          </div>
        )}

        {error && <div className="message error">{error}</div>}

        {prediction && (
          <div className="result">
            {prediction.image_url && (
              <img
                src={prediction.image_url}
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
          <p>
            Данная модель обучена классифицировать изображения трёх классов:
          </p>
          <ul>
            <li>
              <strong>Крокодил</strong> (класс 0)
            </li>
            <li>
              <strong>Аллигатор</strong> (класс 1)
            </li>
            <li>
              <strong>Кайман</strong> (класс 2)
            </li>
          </ul>
          <p>
            <strong>Требования к изображению:</strong>
          </p>
          <ul>
            <li>Формат: JPG, PNG</li>
            <li>
              Изображение будет автоматически масштабировано до 32x32 пикселей
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
