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

  const handleFile = useCallback(
    (file: File) => {
      if (!file.type.startsWith('image/')) return;
      const url = URL.createObjectURL(file);
      dispatch(setSelectedFile({ file, url }));
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
    const { selectedFile } = useAppSelector.getState();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('filePath', selectedFile);

    dispatch(classifyImage(formData));
  }, [dispatch]);

  return (
    <div className="classifier-widget">
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

      <button
        className="submit-btn"
        onClick={handleSubmit}
        disabled={!imageUrl || isLoading}
      >
        {isLoading ? <Loader2 className="spin" /> : 'Классифицировать'}
      </button>

      {prediction && (
        <div className="result">
          <h3>Результат:</h3>
          <p className="prediction-text">{prediction.scorePrediction}</p>
          {prediction.image_url && (
            <img src={prediction.image_url} alt="Result" className="result-image" />
          )}
        </div>
      )}

      {error && <p className="error">{error}</p>}
    </div>
  );
}