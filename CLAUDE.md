# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CrocodilianClassifier is a machine learning project for classifying images of crocodilians (крокодил, аллигатор, кайман) using CNNs. The project includes:
- Training pipeline with multiple model architectures (MLP, CNN, ResNet20, MobileNetV2)
- MLflow experiment tracking with S3 artifact storage
- Django REST backend for inference
- React + TypeScript frontend
- Docker Compose orchestration with MinIO S3 and MLflow

## Common Commands

### Training Models
```bash
# Train specific model (run from project root)
make train MODEL=cnn OPTIMIZER=sgd EPOCHS=50 DEVICE=cuda

# Train all models
make train-all

# Train with specific parameters
cd training && python3 main.py --model resnet20 --optimizer adam --epochs 50 --device cuda

# Compare optimizers for a model
cd training && python3 main.py --model cnn --compare-optimizers
```

### Docker Services
```bash
# Start all services (Frontend, Django, MLflow, MinIO)
make full-up

# Stop all services
make full-down

# Rebuild and restart
make deploy

# View logs
make logs service=web
make mlflow-logs
make frontend-logs
```

### MLflow Management
```bash
# Start MLflow server
make mlflow-up

# List available runs
make list-mlflow-runs

# Add model from MLflow to repository
make add-mlflow-model RUN_ID=<run_id>
```

### Django Backend
```bash
# Run Django locally (without Docker)
make run-django

# Run migrations
make migrate

# Collect static files
make collectstatic
```

### Frontend Development
```bash
# Run frontend dev server (without Docker)
make frontend-dev

# Build frontend
make frontend-build
```

### Dataset Management
```bash
# Download images for all classes
make download CLASSES='крокодил аллигатор кайман' IMAGES_PER_CLASS=100

# Show dataset statistics
make dataset-stats
```

## Architecture

### Training Pipeline (`training/`)

**Entry Point**: `training/main.py` - CLI for training models with configurable parameters

**Key Components**:
- `configs/config.py` - Model-specific configurations (MLPConfig, CNNConfig, ResNetConfig, MobileNetConfig)
- `models/` - Model architectures (mlp.py, cnn.py, resnet20.py, mobilenet.py)
- `scripts/train_model.py` - Training functions and optimizer factory
- `utils/training.py` - Core training loop (train_epoch, validate, Trainer class)
- `utils/data.py` - Dataset loading and augmentation
- `utils/export.py` - ONNX export functionality
- `utils/mlflow_utils.py` - MLflow logging integration

**Training Flow**:
1. `main.py` parses CLI args and selects model/optimizer
2. `options.py` provides model trainer factory
3. `train_model.py` orchestrates training with MLflow tracking
4. `utils/training.py` handles epoch-level training/validation
5. Models saved to `checkpoints/` and exported to ONNX in `data/models/`

**Transfer Learning Models** (ResNet20, MobileNetV2):
- Two-stage training: Stage 1 (classifier only), Stage 2 (fine-tuning)
- Configurable number of layers to unfreeze
- Separate learning rates for each stage

### Backend (`backend/`)

**Django Application** with ONNX inference:
- `core/views.py` - Main view handling image upload and classification
- `core/storage_backends.py` - S3 storage backend for MinIO
- `core/settings.py` - Django settings with S3 configuration
- Uses `onnxruntime` for model inference
- Supports loading models from MLflow S3 bucket

**Key Features**:
- Image preprocessing (resize to 224x224, normalize with ImageNet stats)
- ONNX model inference
- S3 integration for model and media storage
- MLflow integration for model versioning

### Frontend (`frontend/`)

**React + TypeScript + Vite** application:
- Feature-Sliced Design architecture (app/, entities/, features/, widgets/)
- Redux Toolkit for state management
- React Query for API calls
- Axios for HTTP requests
- Communicates with Django backend API

### Infrastructure

**Docker Compose Services**:
- `frontend` - React dev server (port 5173)
- `web` - Django application (port 8000)
- `mlflow` - MLflow tracking server (port 5000)
- `minio` - S3-compatible storage (ports 9000, 9001)
- `minio-init` - Initializes S3 buckets on startup

**S3 Buckets**:
- `crocodilian` - Django media files (uploaded images, models)
- `crocodilian-artifacts` - MLflow artifacts (models, metrics, plots)

## Model Training Workflow

1. **Prepare data**: Images organized in `data/крокодил/`, `data/аллигатор/`, `data/кайман/`
2. **Train model**: Use `make train MODEL=<model>` or `cd training && python3 main.py`
3. **Track experiments**: MLflow automatically logs metrics, parameters, artifacts
4. **Export to ONNX**: Models automatically exported after training
5. **Deploy**: Copy ONNX model to backend or use MLflow model registry

## MLflow Integration

- Tracking URI: `http://localhost:5000`
- Artifacts stored in MinIO S3 (`crocodilian-artifacts` bucket)
- Logged artifacts: model checkpoints, ONNX models, confusion matrices, sample predictions
- Use `make list-mlflow-runs` to see available runs
- Use `make add-mlflow-model RUN_ID=<id>` to add model to repository

## Important Notes

- **Training scripts must be run from project root** or `training/` directory
- **Device selection**: Use `DEVICE=cuda` or `DEVICE=cpu` in make commands
- **Model configs**: Each model has specific default optimizers and hyperparameters in `training/configs/config.py`
- **Label handling**: Training utils support both one-hot and scalar labels
- **Image preprocessing**: Training uses 32x32 for MLP/CNN, 224x224 for ResNet/MobileNet
- **S3 credentials**: Default MinIO credentials are `minioadmin/minioadmin`

## Development Workflow

1. Start infrastructure: `make full-up`
2. Train models: `make train MODEL=cnn` or use training CLI
3. View experiments: Open MLflow UI at `http://localhost:5000`
4. Test inference: Upload images via frontend at `http://localhost:5173`
5. View logs: `make logs service=<service_name>`

## Git: сообщения коммитов

Правила на русском для Cursor: `.cursor/rules/format-commit.mdc`.

Шаблон для редактора при `git commit`: файл `.gitmessage` в корне репозитория. Подключить один раз в клоне:

```bash
make git-template
```

или `git config commit.template /абсолютный/путь/к/репозиторию/.gitmessage`.

## File Locations

- Trained model checkpoints: `checkpoints/*.pth`
- ONNX exports: `data/models/*.onnx`
- MLflow runs: `mlruns/` (local) or MinIO S3 (Docker)
- Dataset: `data/<class_name>/*.jpeg`
- Django media: `backend/media/` (local) or MinIO S3 (Docker)
