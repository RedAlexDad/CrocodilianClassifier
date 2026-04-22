# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CrocodilianClassifier is a machine learning project for classifying images of crocodilians (крокодил, аллигатор, кайман) using CNNs. The project includes:
- Training pipeline with multiple model architectures (MLP, CNN, ResNet20, MobileNetV2)
- MLflow experiment tracking with S3 artifact storage
- Django REST backend for inference
- React + TypeScript frontend with hot reload
- Docker Compose orchestration with MinIO S3 and MLflow
- Image gallery for viewing uploaded images
- Model management with metrics display

## Common Commands

### Docker Services
```bash
# Start all services (Frontend, Django, MLflow, MinIO)
make full-up

# Stop all services
make full-down

# Rebuild and restart everything
make deploy

# Fast restart (no rebuild)
make backend-restart   # Restart Django only
make frontend-restart  # Restart React only
make web-restart       # Restart both backend + frontend

# View logs
make backend-logs
make frontend-logs
make web-logs          # Both backend + frontend
make mlflow-logs
```

### Training Models
```bash
# Train specific model (run from project root)
make train MODEL=cnn OPTIMIZER=sgd EPOCHS=50 DEVICE=cuda

# Quick shortcuts
make train-cnn         # Train CNN with SGD
make train-mlp         # Train MLP
make train-resnet20    # Train ResNet20

# Train all models
make train-all

# Train with custom parameters
cd training && python3 main.py --model resnet20 --optimizer adam --epochs 50 --device cuda
```

### MLflow Management
```bash
# Start MLflow server
make mlflow-up

# List available runs with metadata
make list-mlflow-runs

# Add model from MLflow to repository
make add-mlflow-model RUN_ID=<run_id>
```

### MinIO Management
```bash
# Start MinIO
make minio-up

# Open MinIO Console
make minio-console

# Clear all buckets (removes all data)
make minio-clear
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

# Build frontend for production
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

### Frontend (`frontend/`)

**Tech Stack**: React + TypeScript + Vite + Redux + React Router

**Key Features**:
- Hot reload in dev mode (no rebuild needed)
- Feature-Sliced Design architecture
- Three main pages:
  - `/` - Image classification with file upload
  - `/gallery` - View and classify uploaded images
  - `/models` - Model management (upload, delete, load from MLflow)

**Structure**:
```
frontend/src/
├── app/           # Redux store configuration
├── widgets/       # Page-level components
│   ├── Classifier/          # Main classification page
│   ├── Gallery/             # Image gallery page
│   └── ModelManagement/     # Model management page
├── entities/      # Business entities
└── features/      # Feature components
```

**Important Files**:
- `vite.config.ts` - Proxy configuration for Django backend
- `App.tsx` - Main routing and navigation
- `ClassifierWidget.tsx` - Image upload and classification
- `GalleryWidget.tsx` - Gallery with click-to-classify
- `ModelManagementWidget.tsx` - Model upload/delete/MLflow integration

### Backend (`backend/`)

**Tech Stack**: Django + ONNX Runtime + boto3 + MinIO

**Key Endpoints**:
- `POST /predictImage` - Classify uploaded image
- `GET /api/models` - List available models
- `GET /api/images` - List uploaded images
- `POST /api/predict-existing` - Classify existing image from gallery
- `GET /api/mlflow-runs` - List MLflow runs with metrics
- `POST /api/mlflow-download` - Download model from MLflow
- `POST /api/model-upload` - Upload ONNX model
- `DELETE /api/model-delete` - Delete model

**Important Files**:
- `core/views.py` - All API endpoints and inference logic
- `core/urls.py` - URL routing
- `core/settings.py` - Django configuration with S3 storage

**Storage Structure**:
- MinIO bucket `crocodilian`:
  - `media/models/` - ONNX models for inference
  - `media/images/` - Uploaded images
  - `mlflow-artifacts/` - MLflow experiment artifacts

### Training Pipeline (`training/`)

**Entry Point**: `training/main.py` - CLI for training models with configurable parameters

**Key Components**:
- `configs/config.py` - Model-specific configurations
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
5. Models saved to `checkpoints/` and exported to ONNX
6. Artifacts logged to MLflow (metrics, plots, reports, ONNX model)

**Transfer Learning Models** (ResNet20, MobileNetV2):
- Two-stage training: Stage 1 (classifier only), Stage 2 (fine-tuning)
- Configurable number of layers to unfreeze
- Separate learning rates for each stage

### MLflow Integration

**Tracking Server**: Runs on port 5000 with SQLite backend

**Logged Artifacts**:
- ONNX model (`onnx/*.onnx`)
- Training plots (loss/accuracy curves)
- Confusion matrices (normalized and raw)
- Classification report (precision, recall, F1)
- Model checkpoint (.pth)

**Metrics Tracked**:
- Training: loss, accuracy per epoch
- Validation: loss, accuracy per epoch
- Test: final accuracy, precision, recall, F1
- System: CPU, memory, GPU usage

**Storage**:
- Metadata: SQLite database in Docker volume `mlflow_data`
- Artifacts: MinIO S3 bucket `crocodilian/mlflow-artifacts/`

### Docker Services

**Services**:
1. **frontend** - React app with Vite (port 5173)
   - Dev mode with hot reload
   - Proxies API requests to backend
   - Volume mounted for live code updates

2. **backend** - Django app (port 8000)
   - ONNX Runtime for inference
   - S3 storage via django-storages
   - Volume mounted for live code updates

3. **mlflow** - MLflow tracking server (port 5000)
   - SQLite backend with persistent volume
   - S3 artifact storage in MinIO

4. **minio** - S3-compatible storage (ports 9000, 9001)
   - API: port 9000
   - Console: port 9001
   - Persistent volume for data

5. **minio-init** - One-time bucket initialization
   - Creates `crocodilian` bucket
   - Sets public read access

**Volumes**:
- `minio_data` - MinIO storage
- `mlflow_data` - MLflow database (persistent runs history)

## Development Workflow

### Adding New Features

1. **Frontend changes**: Edit files in `frontend/src/`, changes apply automatically (hot reload)
2. **Backend changes**: Edit files in `backend/`, run `make backend-restart` for quick reload
3. **Training changes**: Edit files in `training/`, run training commands directly

### Training New Models

```bash
# 1. Train model with MLflow tracking
make train-cnn

# 2. Check MLflow UI for run metrics
open http://localhost:5000

# 3. Load model from MLflow in web UI
# Go to http://localhost:5173/models → "Загрузить из MLflow"

# 4. Test classification
# Go to http://localhost:5173/ and upload an image
```

### Debugging

**Backend logs**:
```bash
make backend-logs
```

**Frontend logs**:
```bash
make frontend-logs
```

**Check MinIO contents**:
```bash
# Open MinIO Console
make minio-console
# Login: minioadmin / minioadmin
```

**Clear all data**:
```bash
make minio-clear  # Clears all S3 buckets
```

## Important Notes

### CSRF Protection
- API endpoints use `@csrf_exempt` decorator for frontend access
- Production should use proper CSRF tokens

### S3 Storage
- All media files stored in MinIO S3
- Public read access for images
- Models stored in `media/models/`
- Images stored in `media/images/`

### Model Format
- Models must be in ONNX format (.onnx)
- Input shape: [batch, channels, height, width] or [batch, height, width, channels]
- Automatic format detection (NCHW vs NHWC)
- Image preprocessing: resize to 32x32, normalize to [0, 1]

### MLflow Runs
- Each training run creates unique run_id
- Artifacts stored in `mlflow-artifacts/{experiment_id}/{run_id}/artifacts/`
- Metrics parsed from `classification_report.txt`
- Only runs with ONNX models shown in UI

## Troubleshooting

**Frontend not updating**: 
- Check if dev mode is running: `docker compose logs frontend`
- Restart: `make frontend-restart`

**Backend 502 error**:
- Check backend logs: `make backend-logs`
- Restart: `make backend-restart`

**No models in MLflow**:
- Train a model first: `make train-cnn`
- Check MLflow UI: http://localhost:5000
- Verify S3 bucket: `make minio-console`

**Images not displaying**:
- Check MinIO is running: `docker compose ps`
- Verify bucket access: http://localhost:9001

**Database reset**:
```bash
# Stop services
make full-down

# Remove volumes
docker volume rm crocodilianclassifier_mlflow_data
docker volume rm crocodilianclassifier_minio_data

# Restart
make full-up
```

## URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- MLflow UI: http://localhost:5000
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
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
