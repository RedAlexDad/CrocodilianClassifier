#!/usr/bin/env python3
"""List MLflow runs from MinIO."""
import boto3
from botocore.client import Config


def main():
    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        config=Config(signature_version="s3v4"),
    )

    bucket = "crocodilian"
    response = s3.list_objects_v2(Bucket=bucket, Prefix="")

    if "Contents" not in response:
        print("Нет запусков")
        return

    runs = {}
    for obj in response["Contents"]:
        key = obj["Key"]
        if "/artifacts/" in key:
            parts = key.split("/")
            if len(parts) >= 2:
                exp_id = parts[0]
                if exp_id not in runs:
                    runs[exp_id] = set()
                if len(parts) >= 3:
                    runs[exp_id].add(parts[1])

    if not runs:
        print("Нет запусков")
        return

    for exp_id, run_ids in runs.items():
        print(f"Experiment {exp_id}:")
        for run_id in sorted(run_ids):
            print(f"  {run_id}")

    print("")
    print("Для добавления модели:")
    print("  make add-mlflow-model RUN_ID=<run_id>")


if __name__ == "__main__":
    main()