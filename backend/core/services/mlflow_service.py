"""
Сервис для работы с MLflow
"""
import os
import boto3
from django.conf import settings


MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_BUCKET = "crocodilian"
MLFLOW_PREFIX = "mlflow-artifacts/"


def get_mlflow_models():
    """Получить список моделей из MLflow S3"""
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )

        response = s3.list_objects_v2(Bucket=MLFLOW_BUCKET, Prefix="models/")

        if "Contents" not in response:
            return []

        models = []
        for obj in response["Contents"]:
            key = obj["Key"]
            if key.endswith(".onnx"):
                name = key.split("/")[-1]
                models.append(
                    {
                        "name": name,
                        "key": key,
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                    }
                )

        return models
    except Exception as e:
        print(f"Ошибка получения моделей из MLflow: {e}")
        return []


def get_mlflow_runs():
    """Получить список запусков MLflow с метаданными"""
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )

        bucket = MLFLOW_BUCKET
        response = s3.list_objects_v2(Bucket=bucket, Prefix=MLFLOW_PREFIX)

        runs_dict = {}
        for obj in response.get("Contents", []):
            key = obj["Key"]
            relative_key = key.replace(MLFLOW_PREFIX, "")

            if "/artifacts/" in relative_key:
                parts = relative_key.split("/")
                if len(parts) >= 3:
                    exp_id = parts[0]
                    run_id = parts[1]

                    if run_id not in runs_dict:
                        runs_dict[run_id] = {
                            "run_id": run_id,
                            "experiment_id": exp_id,
                            "model_name": "Unknown",
                            "date": obj["LastModified"].strftime("%Y-%m-%d %H:%M"),
                            "has_onnx": False,
                            "accuracy": None,
                            "precision": None,
                            "recall": None,
                            "f1_score": None,
                        }

                    # Определяем тип модели по имени файла .onnx
                    if key.endswith(".onnx"):
                        model_file = key.split("/")[-1].replace(".onnx", "")
                        runs_dict[run_id]["model_name"] = model_file.upper()
                        runs_dict[run_id]["has_onnx"] = True

                    # Читаем метрики из classification_report.txt
                    if key.endswith("classification_report.txt"):
                        try:
                            obj_data = s3.get_object(Bucket=bucket, Key=key)
                            report = obj_data["Body"].read().decode("utf-8")

                            for line in report.split("\n"):
                                if "accuracy" in line.lower():
                                    parts = line.split()
                                    if len(parts) >= 2:
                                        try:
                                            runs_dict[run_id]["accuracy"] = float(parts[1])
                                        except (ValueError, IndexError):
                                            pass

                                if "weighted avg" in line.lower():
                                    parts = line.split()
                                    try:
                                        runs_dict[run_id]["precision"] = float(parts[2])
                                        runs_dict[run_id]["recall"] = float(parts[3])
                                        runs_dict[run_id]["f1_score"] = float(parts[4])
                                    except (ValueError, IndexError):
                                        pass
                        except Exception as e:
                            print(f"Ошибка чтения classification_report для {run_id}: {e}")

        # Фильтруем только runs с ONNX моделями
        result = [run for run in runs_dict.values() if run["has_onnx"]]
        result.sort(key=lambda x: x["date"], reverse=True)

        return result
    except Exception as e:
        print(f"Ошибка получения runs: {e}")
        return []


def download_mlflow_model(run_id):
    """Скачать модель из MLflow и вернуть путь к ONNX файлу"""
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
        )

        bucket = MLFLOW_BUCKET
        possible_prefixes = [
            f"{MLFLOW_PREFIX}{run_id}/artifacts/",
            f"{MLFLOW_PREFIX}1/{run_id}/artifacts/",
            f"{MLFLOW_PREFIX}0/{run_id}/artifacts/",
        ]

        onnx_key = None
        for prefix in possible_prefixes:
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            for obj in response.get("Contents", []):
                key = obj["Key"]
                if key.endswith(".onnx"):
                    onnx_key = key
                    break
            if onnx_key:
                break

        if not onnx_key:
            return None, "No ONNX model found"

        model_name = os.path.basename(onnx_key)
        local_path = f"/tmp/{model_name}"
        s3.download_file(bucket, onnx_key, local_path)

        return local_path, model_name
    except Exception as e:
        return None, str(e)
