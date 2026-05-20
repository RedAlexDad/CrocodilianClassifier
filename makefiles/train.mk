.PHONY: train train-all train-mlp train-cnn train-resnet20 train-mobilenet
.PHONY: train-yolo-seg train-yolo-n train-yolo-s train-yolo-m train-yolo-l train-yolo-xl train-yolo-xxl train-compared

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

train-yolo-seg: ## YOLOv8-segment: yolov8n 50ep batch=8 Adam lr=0.001 (run #1)
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg --optimizer Adam --lr 0.001 --epochs 50 --batch 8 --device $(DEVICE)

train-yolo-n: ## Run #1: yolov8n-seg 20ep Adam lr=0.001 batch=8
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg --optimizer Adam --lr 0.001 --epochs 20 --batch 8 --device $(DEVICE)

train-yolo-s: ## Run #2: yolov8n-seg 20ep SGD lr=0.01 batch=8
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg-sgd --optimizer SGD --lr 0.001 --epochs 20 --batch 8 --device $(DEVICE)

train-yolo-m: ## Run #3: yolov8n-seg 20ep AdamW lr=0.001 batch=8
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg-adamw --optimizer AdamW --lr 0.001 --epochs 20 --batch 8 --device $(DEVICE)

train-yolo-l: ## Run #4: yolov8n-seg 50ep Adam lr=0.0005 batch=8
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg-long --optimizer Adam --lr 0.0005 --epochs 50 --batch 8 --device $(DEVICE)

train-yolo-xl: ## Run #5: yolov8n-seg 50ep SGD lr=0.0005 batch=8
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg-long-sgd --optimizer SGD --lr 0.0005 --epochs 50 --batch 8 --device $(DEVICE)

train-yolo-xxl: ## Run #6: yolov8n-seg 50ep AdamW lr=0.0005 batch=8
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg-long-adamw --optimizer AdamW --lr 0.0005 --epochs 50 --batch 8 --device $(DEVICE)

train-yolo-coco: ## YOLOv8-seg COCO RLE датасет: yolov8n 50ep AdamW lr=0.0005 batch=8
	cd $(TRAINING_DIR) && $(PYTHON) main.py --task segment --model yolov8n-seg-coco-adamw --optimizer AdamW --lr 0.0005 --epochs 50 --batch 8 --device $(DEVICE)

train-compared: ## Сравнить все оптимизаторы
	cd $(TRAINING_DIR) && $(PYTHON) main.py --model all --compare-optimizers