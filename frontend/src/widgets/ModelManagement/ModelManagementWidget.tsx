import { useCallback, useState, useEffect } from 'react';
import { Upload, Trash2, Download, Loader2, Database, Check, X } from 'lucide-react';
import './ModelManagementWidget.css';

interface ModelInfo {
  name: string;
  url: string;
}

interface MlflowRun {
  run_id: string;
  experiment_id: string;
}

export function ModelManagementWidget() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showMlflowModal, setShowMlflowModal] = useState(false);
  const [mlflowRuns, setMlflowRuns] = useState<MlflowRun[]>([]);
  const [loadingRuns, setLoadingRuns] = useState(false);
  const [downloadingRun, setDownloadingRun] = useState<string | null>(null);

  const loadModels = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/models');
      const data = await res.json();
      if (data.models) {
        const modelList: ModelInfo[] = data.models.map((m: string | {name: string, url?: string}) => {
          const name = typeof m === 'string' ? m : m.name;
          return { name, url: `/media/models/${name}` };
        });
        setModels(modelList);
      }
    } catch (err) {
      console.error('Failed to load models:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  const handleUpload = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const fileInput = form.elements.namedItem('modelFile') as HTMLInputElement;
    const file = fileInput?.files?.[0];
    
    if (!file) {
      setError('Выберите файл модели');
      return;
    }

    if (!file.name.endsWith('.onnx')) {
      setError('Загрузите файл .onnx');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    const formData = new FormData();
    formData.append('modelFile', file);

    try {
      const res = await fetch('/api/model-upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      
      if (data.success) {
        setSuccess(`Модель ${file.name} успешно загружена!`);
        fileInput.value = '';
        loadModels();
      } else {
        setError(data.error || 'Ошибка загрузки');
      }
    } catch (err) {
      setError('Ошибка загрузки');
    } finally {
      setUploading(false);
    }
  }, [loadModels]);

  const handleDelete = useCallback(async (modelName: string) => {
    if (!confirm(`Удалить модель ${modelName}?`)) return;

    setError(null);
    setSuccess(null);

    try {
      const res = await fetch(`/api/model-delete?delete_model=${encodeURIComponent(modelName)}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      
      if (data.success) {
        setSuccess(`Модель ${modelName} удалена`);
        loadModels();
      } else {
        setError(data.error || 'Ошибка удаления');
      }
    } catch (err) {
      setError('Ошибка удаления');
    }
  }, [loadModels]);

  const openMlflowModal = useCallback(async () => {
    setShowMlflowModal(true);
    setLoadingRuns(true);
    try {
      const res = await fetch('/api/mlflow-runs');
      const data = await res.json();
      setMlflowRuns(data.runs || []);
    } catch (err) {
      console.error('Failed to load MLflow runs:', err);
    } finally {
      setLoadingRuns(false);
    }
  }, []);

  const downloadFromMlflow = useCallback(async (runId: string) => {
    setDownloadingRun(runId);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('run_id', runId);
      const res = await fetch('/api/mlflow-download', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      
      if (data.success) {
        setSuccess(`Модель загружена из MLflow`);
        loadModels();
      } else {
        setError(data.error || 'Ошибка загрузки из MLflow');
      }
    } catch (err) {
      setError('Ошибка загрузки из MLflow');
    } finally {
      setDownloadingRun(null);
    }
  }, [loadModels]);

  return (
    <div className="model-management">
      <h2>Управление моделями</h2>

      {error && (
        <div className="message error">
          <X size={16} />
          {error}
        </div>
      )}

      {success && (
        <div className="message success">
          <Check size={16} />
          {success}
        </div>
      )}

      <div className="section">
        <h3>Загрузить модель</h3>
        <form onSubmit={handleUpload}>
          <input type="file" name="modelFile" accept=".onnx" />
          <button type="submit" disabled={uploading}>
            {uploading ? (
              <>
                <Loader2 className="spin" size={16} />
                Загрузка...
              </>
            ) : (
              <>
                <Upload size={16} />
                Загрузить
              </>
            )}
          </button>
        </form>
      </div>

      <div className="section">
        <h3>Доступные модели</h3>
        <button className="mlflow-btn" onClick={openMlflowModal}>
          <Database size={16} />
          Загрузить из MLflow
        </button>

        {loading ? (
          <div className="loading">
            <Loader2 className="spin" />
            Загрузка...
          </div>
        ) : models.length === 0 ? (
          <p>Нет доступных моделей</p>
        ) : (
          <table className="models-table">
            <thead>
              <tr>
                <th>Модель</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {models.map(model => (
                <tr key={model.name}>
                  <td>{model.name}</td>
                  <td>
                    <button
                      className="delete-btn"
                      onClick={() => handleDelete(model.name)}
                      title="Удалить"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showMlflowModal && (
        <div className="modal-overlay" onClick={() => setShowMlflowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>MLflow модели</h3>
              <button className="modal-close" onClick={() => setShowMlflowModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              {loadingRuns ? (
                <div className="loading">
                  <Loader2 className="spin" />
                  <p>Загрузка...</p>
                </div>
              ) : mlflowRuns.length === 0 ? (
                <p>Нет моделей в MLflow</p>
              ) : (
                <div className="runs-list">
                  {mlflowRuns.map(run => (
                    <div key={run.run_id} className="run-item">
                      <span className="run-id">{run.run_id}</span>
                      <button
                        className="download-btn"
                        onClick={() => downloadFromMlflow(run.run_id)}
                        disabled={downloadingRun === run.run_id}
                      >
                        {downloadingRun === run.run_id ? (
                          <Loader2 className="spin" size={16} />
                        ) : (
                          <Download size={16} />
                        )}
                        Загрузить
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}