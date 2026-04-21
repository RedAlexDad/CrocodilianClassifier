import { useCallback, useState } from 'react';
import { useAppDispatch, useAppSelector } from '@/app/store/hooks';
import { setSelectedFile, classifyImage, clearPrediction } from '@/features/classifier/classifierSlice';
import { Upload, Loader2, X } from 'lucide-react';
import './ClassifierWidget.css';

export function ClassifierWidget() {
  const dispatch = useAppDispatch();
  const { imageUrl, prediction, isLoading, error } = useAppSelector(
    (state) => state.classifier
  );
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      if (!file.type.startsWith('image/')) return;
      const url = URL.createObjectURL(file);
      setSelectedFile(file);
      dispatch(setSelectedFile({ url }));
    },
    [dispatch]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleSubmit = useCallback(async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    dispatch(classifyImage(formData));
  }, [dispatch, selectedFile]);

  return (
    <div className="classifier-widget">
      <div className="content">
        <div
          className={`drop-zone ${dragActive ? 'active' : ''}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-input"
            accept="image/*"
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
          <label htmlFor="file-input">
            {imageUrl ? (
              <img src={imageUrl} alt="Preview" />
            ) : (
              <>
                <Upload size={48} />
                <p>Перетащите изображение или нажмите для выбора</p>
              </>
            )}
          </label>
          {imageUrl && (
            <button className="clear-btn" onClick={() => dispatch(clearPrediction())}>
              <X size={20} />
            </button>
          )}
        </div>

        <div className="upload-form">
          <input
            type="submit"
            value={isLoading ? 'Классификация...' : 'Классифицировать'}
            onClick={handleSubmit}
            disabled={!imageUrl || isLoading}
          />
        </div>

        {isLoading && (
          <div className="loading">
            <Loader2 className="spin" />
            <p>Идет классификация...</p>
          </div>
        )}

        {prediction && (
          <div className="result">
            <h3>Результат классификации:</h3>
            <p className="prediction-text">{prediction.scorePrediction}</p>
            {prediction.image_url && (
              <img src={prediction.image_url} alt="Result" className="result-image" />
            )}
          </div>
        )}

        {error && (
          <div className="message error">
            <p>Ошибка: {error}</p>
          </div>
        )}
      </div>
    </div>
  );
}