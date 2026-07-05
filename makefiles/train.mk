.PHONY: train train-all train-mlp train-cnn train-resnet20 train-mobilenet
.PHONY: train-yolo-seg train-yolo-n train-yolo-s train-yolo-m train-yolo-l train-yolo-xl train-compared

include makefiles/_vars.mk

train: ## Обучение: make train MODEL=cnn OPTIMIZER=adam EPOCHS=50 LR=0.001 DEVICE=cpu
	@echo "$(GREEN)Обучение: MODEL=$(MODEL), OPTIMIZER=$(OPTIMIZER), EPOCHS=$(EPOCHS), DEVICE=$(DEVICE)$(NC)"
	cd $(TRAINING_DIR) && $(PYTHON) main.py \
		--model $(MODEL) \
		--optimizer $(OPTIMIZER) \
		--epochs $(EPOCHS) \
		--epochs-stage1 $(EPOCHS_STAGE1) \
		--finetune-layers $(FINETUNE_LAYERS) \
		--lr $(LR) \
		--lr-finetune $(LR_FINETUNE) \
		--batch-size $(BATCH_SIZE) \
		--weight-decay $(WEIGHT_DECAY) \
		--seed $(SEED) \
		--device $(DEVICE)

train-all: ## Обучить все модели
	@echo "$(GREEN)Обучение всех моделей...$(NC)"
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model all

train-mlp: ## make train-mlp
	$(MAKE) train MODEL=mlp

train-cnn: ## make train-cnn
	$(MAKE) train MODEL=cnn OPTIMIZER=sgd

train-resnet20: ## make train-resnet20
	$(MAKE) train MODEL=resnet20

train-mobilenet: ## make train-mobilenet
	$(MAKE) train MODEL=mobilenet

train-yolo-seg: EPOCHS = 50
train-yolo-seg: BATCH_SIZE = 8
train-yolo-seg: OPTIMIZER = Adam
train-yolo-seg: LR = 0.001
train-yolo-seg: ## YOLOv8-segment: yolov8n (50ep, batch=8, Adam, lr=0.001)
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg --optimizer $(OPTIMIZER) --lr $(LR) --epochs $(EPOCHS) --batch-size $(BATCH_SIZE) --device $(DEVICE)

train-yolo-n: EPOCHS = 50
train-yolo-n: BATCH_SIZE = 8
train-yolo-n: OPTIMIZER = AdamW
train-yolo-n: LR = 0.0005
train-yolo-n: ## yolov8n-seg (50ep, AdamW, lr=0.0005, batch=8)
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg --optimizer $(OPTIMIZER) --lr $(LR) --epochs $(EPOCHS) --batch-size $(BATCH_SIZE) --device $(DEVICE)

train-yolo-s: EPOCHS = 50
train-yolo-s: BATCH_SIZE = 8
train-yolo-s: OPTIMIZER = AdamW
train-yolo-s: LR = 0.0005
train-yolo-s: ## yolov8s-seg (50ep, AdamW, lr=0.0005, batch=8)
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8s-seg --optimizer $(OPTIMIZER) --lr $(LR) --epochs $(EPOCHS) --batch-size $(BATCH_SIZE) --device $(DEVICE)

train-yolo-m: EPOCHS = 50
train-yolo-m: BATCH_SIZE = 8
train-yolo-m: OPTIMIZER = AdamW
train-yolo-m: LR = 0.0005
train-yolo-m: ## yolov8m-seg (50ep, AdamW, lr=0.0005, batch=8)
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8m-seg --optimizer $(OPTIMIZER) --lr $(LR) --epochs $(EPOCHS) --batch-size $(BATCH_SIZE) --device $(DEVICE)

train-yolo-l: EPOCHS = 50
train-yolo-l: BATCH_SIZE = 8
train-yolo-l: OPTIMIZER = AdamW
train-yolo-l: LR = 0.0005
train-yolo-l: ## yolov8l-seg (50ep, AdamW, lr=0.0005, batch=8)
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8l-seg --optimizer $(OPTIMIZER) --lr $(LR) --epochs $(EPOCHS) --batch-size $(BATCH_SIZE) --device $(DEVICE)

train-yolo-xl: EPOCHS = 50
train-yolo-xl: BATCH_SIZE = 8
train-yolo-xl: OPTIMIZER = AdamW
train-yolo-xl: LR = 0.0005
train-yolo-xl: ## yolov8x-seg (50ep, AdamW, lr=0.0005, batch=8)
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8x-seg --optimizer $(OPTIMIZER) --lr $(LR) --epochs $(EPOCHS) --batch-size $(BATCH_SIZE) --device $(DEVICE)

train-yolo-coco: EPOCHS = 50
train-yolo-coco: BATCH_SIZE = 8
train-yolo-coco: OPTIMIZER = AdamW
train-yolo-coco: LR = 0.0005
train-yolo-coco: ## YOLOv8-seg COCO RLE датасет (50ep, AdamW, lr=0.0005, batch=8)
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg-coco-adamw --optimizer $(OPTIMIZER) --lr $(LR) --epochs $(EPOCHS) --batch-size $(BATCH_SIZE) --device $(DEVICE)

train-compared: ## Сравнить все оптимизаторы
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model all --compare-optimizers