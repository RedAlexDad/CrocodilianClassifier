import {
  Check,
  Database,
  Download,
  Loader2,
  Trash2,
  Upload,
  X,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import "./ModelManagementWidget.css";

interface ModelInfo {
  name: string;
  url: string;
}

interface MlflowRun {
  run_id: string;
  experiment_id: string;
  model_name?: string;
  optimizer?: string;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  date?: string;
  status?: string;
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
  const [sortBy, setSortBy] = useState<"date" | "accuracy" | "name">("date");
  const [groupByModel, setGroupByModel] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadModels = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/models");
      const data = await res.json();
      if (data.models) {
        const modelList: ModelInfo[] = data.models.map(
          (m: string | { name: string; url?: string }) => {
            const name = typeof m === "string" ? m : m.name;
            return { name, url: `/media/models/${name}` };
          },
        );
        setModels(modelList);
      }
    } catch (err) {
      console.error("Failed to load models:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFileName(file.name);
    } else {
      setSelectedFileName("");
    }
  };

  const handleCustomButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      const form = e.currentTarget;
      const fileInput = form.elements.namedItem(
        "modelFile",
      ) as HTMLInputElement;
      const file = fileInput?.files?.[0];

      if (!file) {
        setError("Выберите файл модели");
        return;
      }

      if (!file.name.endsWith(".onnx")) {
        setError("Загрузите файл .onnx");
        return;
      }

      setUploading(true);
      setError(null);
      setSuccess(null);

      const formData = new FormData();
      formData.append("modelFile", file);

      try {
        const res = await fetch("/api/model-upload", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();

        if (data.success) {
          setSuccess(`Модель ${file.name} успешно загружена!`);
          fileInput.value = "";
          setSelectedFileName("");
          loadModels();
        } else {
          setError(data.error || "Ошибка загрузки");
        }
      } catch (err) {
        setError("Ошибка загрузки");
      } finally {
        setUploading(false);
      }
    },
    [loadModels],
  );

  const handleDelete = useCallback(
    async (modelName: string) => {
      if (!confirm(`Удалить модель ${modelName}?`)) return;

      setError(null);
      setSuccess(null);

      try {
        const res = await fetch(
          `/api/model-delete?delete_model=${encodeURIComponent(modelName)}`,
          {
            method: "DELETE",
          },
        );
        const data = await res.json();

        if (data.success) {
          setSuccess(`Модель ${modelName} удалена`);
          loadModels();
        } else {
          setError(data.error || "Ошибка удаления");
        }
      } catch (err) {
        setError("Ошибка удаления");
      }
    },
    [loadModels],
  );

  const openMlflowModal = useCallback(async () => {
    setShowMlflowModal(true);
    setLoadingRuns(true);
    try {
      const res = await fetch("/api/mlflow-runs");
      const data = await res.json();
      setMlflowRuns(data.runs || []);
    } catch (err) {
      console.error("Failed to load MLflow runs:", err);
    } finally {
      setLoadingRuns(false);
    }
  }, []);

  const downloadFromMlflow = useCallback(
    async (runId: string) => {
      setDownloadingRun(runId);
      setError(null);
      setSuccess(null);

      try {
        const formData = new FormData();
        formData.append("run_id", runId);
        const res = await fetch("/api/mlflow-download", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();

        if (data.success) {
          setSuccess(`Модель загружена из MLflow`);
          loadModels();
        } else {
          setError(data.error || "Ошибка загрузки из MLflow");
        }
      } catch (err) {
        setError("Ошибка загрузки из MLflow");
      } finally {
        setDownloadingRun(null);
      }
    },
    [loadModels],
  );

  const getSortedAndGroupedRuns = useCallback(() => {
    let sorted = [...mlflowRuns];

    // Сортировка
    switch (sortBy) {
      case "accuracy":
        sorted.sort((a, b) => (b.accuracy || 0) - (a.accuracy || 0));
        break;
      case "name":
        sorted.sort((a, b) =>
          (a.model_name || "").localeCompare(b.model_name || ""),
        );
        break;
      case "date":
      default:
        sorted.sort((a, b) => (b.date || "").localeCompare(a.date || ""));
        break;
    }

    // Группировка
    if (groupByModel) {
      const grouped: { [key: string]: MlflowRun[] } = {};
      sorted.forEach((run) => {
        const model = run.model_name || "Unknown";
        if (!grouped[model]) {
          grouped[model] = [];
        }
        grouped[model].push(run);
      });
      return grouped;
    }

    return sorted;
  }, [mlflowRuns, sortBy, groupByModel]);

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
          <input
            type="file"
            name="modelFile"
            accept=".onnx"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          <div className="custom-file-upload">
            <button
              type="button"
              className="custom-file-button"
              onClick={handleCustomButtonClick}
            >
              Выбрать файл .onnx
            </button>
            <span className="file-name">
              {selectedFileName || "Файл не выбран"}
            </span>
          </div>
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
              {models.map((model) => (
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
        <div
          className="modal-overlay"
          onClick={() => setShowMlflowModal(false)}
        >
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>MLflow модели</h3>
              <button
                className="modal-close"
                onClick={() => setShowMlflowModal(false)}
              >
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
                <>
                  <div className="filter-controls">
                    <div className="filter-group">
                      <label>Сортировка:</label>
                      <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as any)}
                      >
                        <option value="date">По дате</option>
                        <option value="accuracy">По точности</option>
                        <option value="name">По названию</option>
                      </select>
                    </div>
                    <div className="filter-group">
                      <label>
                        <input
                          type="checkbox"
                          checked={groupByModel}
                          onChange={(e) => setGroupByModel(e.target.checked)}
                        />
                        Группировать по модели
                      </label>
                    </div>
                  </div>

                  <div className="runs-list">
                    {groupByModel
                      ? Object.entries(
                          getSortedAndGroupedRuns() as {
                            [key: string]: MlflowRun[];
                          },
                        ).map(([modelName, runs]) => (
                          <div key={modelName} className="model-group">
                            <h4 className="group-title">
                              {modelName} ({runs.length})
                            </h4>
                            {runs.map((run) => (
                              <div key={run.run_id} className="run-item">
                                <div className="run-info">
                                  <div className="run-metrics">
                                    {run.accuracy !== null &&
                                      run.accuracy !== undefined && (
                                        <span className="metric">
                                          Accuracy:{" "}
                                          {(run.accuracy * 100).toFixed(2)}%
                                        </span>
                                      )}
                                    {run.precision !== null &&
                                      run.precision !== undefined && (
                                        <span className="metric">
                                          Precision:{" "}
                                          {(run.precision * 100).toFixed(2)}%
                                        </span>
                                      )}
                                    {run.recall !== null &&
                                      run.recall !== undefined && (
                                        <span className="metric">
                                          Recall:{" "}
                                          {(run.recall * 100).toFixed(2)}%
                                        </span>
                                      )}
                                    {run.f1_score !== null &&
                                      run.f1_score !== undefined && (
                                        <span className="metric">
                                          F1: {(run.f1_score * 100).toFixed(2)}%
                                        </span>
                                      )}
                                  </div>
                                  <div className="run-meta">
                                    <span className="run-date">
                                      {run.date || "N/A"}
                                    </span>
                                    <span className="run-id-short">
                                      {run.run_id.substring(0, 8)}...
                                    </span>
                                  </div>
                                </div>
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
                        ))
                      : (getSortedAndGroupedRuns() as MlflowRun[]).map(
                          (run) => (
                            <div key={run.run_id} className="run-item">
                              <div className="run-info">
                                <div className="run-header">
                                  <span className="model-name">
                                    {run.model_name || "Unknown"}
                                  </span>
                                  {run.optimizer && (
                                    <span className="optimizer">
                                      {run.optimizer}
                                    </span>
                                  )}
                                </div>
                                <div className="run-metrics">
                                  {run.accuracy !== null &&
                                    run.accuracy !== undefined && (
                                      <span className="metric">
                                        Accuracy:{" "}
                                        {(run.accuracy * 100).toFixed(2)}%
                                      </span>
                                    )}
                                  {run.precision !== null &&
                                    run.precision !== undefined && (
                                      <span className="metric">
                                        Precision:{" "}
                                        {(run.precision * 100).toFixed(2)}%
                                      </span>
                                    )}
                                  {run.recall !== null &&
                                    run.recall !== undefined && (
                                      <span className="metric">
                                        Recall: {(run.recall * 100).toFixed(2)}%
                                      </span>
                                    )}
                                  {run.f1_score !== null &&
                                    run.f1_score !== undefined && (
                                      <span className="metric">
                                        F1: {(run.f1_score * 100).toFixed(2)}%
                                      </span>
                                    )}
                                </div>
                                <div className="run-meta">
                                  <span className="run-date">
                                    {run.date || "N/A"}
                                  </span>
                                  <span className="run-id-short">
                                    {run.run_id.substring(0, 8)}...
                                  </span>
                                </div>
                              </div>
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
                          ),
                        )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
