import os
import tempfile
import shutil
import numpy as np
import onnxruntime
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage


SEG_MODEL_NAME = "yolov8_seg.onnx"
IMGSZ = 640
NUM_CLASSES = 3
NUM_MASK_COEFFS = 32
CLASSES = ["Аллигатор", "Кайман", "Крокодил"]

_model_path = None


def segment_image(image_path):
    try:
        model_path = _get_model_path()
        if model_path is None:
            return {"error": "Модель сегментации не найдена"}

        img_file = default_storage.open(image_path)
        img = Image.open(img_file).convert("RGB")
        orig_w, orig_h = img.size

        img_array, pad_info = _preprocess(img, IMGSZ)

        sess = onnxruntime.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        input_name = sess.get_inputs()[0].name
        outputs = sess.run(None, {input_name: img_array})

        detections = _postprocess(outputs[0], outputs[1], (orig_h, orig_w), pad_info)

        return {"detections": detections}

    except Exception as e:
        return {"error": str(e)}


def segment_image_file(image_path, model_path):
    try:
        if not os.path.isfile(model_path):
            return {"error": "Модель не найдена"}

        img = Image.open(image_path).convert("RGB")
        orig_w, orig_h = img.size

        img_array, pad_info = _preprocess(img, IMGSZ)

        sess = onnxruntime.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        input_name = sess.get_inputs()[0].name
        outputs = sess.run(None, {input_name: img_array})

        detections = _postprocess(outputs[0], outputs[1], (orig_h, orig_w), pad_info)

        return {"detections": detections}

    except Exception as e:
        return {"error": str(e)}


def _get_model_path():
    global _model_path
    if _model_path is not None and os.path.isfile(_model_path):
        return _model_path

    local_path = os.path.join(settings.BASE_DIR, "media", "models", SEG_MODEL_NAME)
    if os.path.isfile(local_path):
        _model_path = local_path
        return local_path

    if getattr(settings, "USE_S3", False):
        try:
            storage = default_storage
            s3 = storage.connection
            bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

            s3_key = f"media/models/{SEG_MODEL_NAME}"
            tmp_dir = tempfile.mkdtemp()
            tmp_path = os.path.join(tmp_dir, SEG_MODEL_NAME)

            with open(tmp_path, "wb") as f:
                bucket.download_fileobj(s3_key, f)

            _model_path = tmp_path
            return _model_path
        except Exception:
            return None

    return None


def _preprocess(img, target_size=640):
    orig_w, orig_h = img.size
    scale = min(target_size / orig_w, target_size / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

    padded = Image.new("RGB", (target_size, target_size), (114, 114, 114))
    x_off = (target_size - new_w) // 2
    y_off = (target_size - new_h) // 2
    padded.paste(img_resized, (x_off, y_off))

    img_array = np.asarray(padded, dtype=np.float32) / 255.0
    img_array = np.transpose(img_array, (2, 0, 1))
    img_array = np.expand_dims(img_array, axis=0)

    pad_info = {"x_off": x_off, "y_off": y_off, "scale": scale}
    return img_array, pad_info


def _postprocess(output0, output1, orig_shape, pad_info):
    conf_thres = 0.25
    iou_thres = 0.45

    pred = output0[0].T

    boxes = pred[:, :4]
    scores = pred[:, 4:4 + NUM_CLASSES]
    masks_coeff = pred[:, 4 + NUM_CLASSES:]

    class_ids = np.argmax(scores, axis=1)
    confs = np.max(scores, axis=1)

    keep = confs > conf_thres
    if not np.any(keep):
        return []

    boxes = boxes[keep]
    class_ids = class_ids[keep]
    confs = confs[keep]
    masks_coeff = masks_coeff[keep]

    x1 = boxes[:, 0] - boxes[:, 2] / 2
    y1 = boxes[:, 1] - boxes[:, 3] / 2
    x2 = boxes[:, 0] + boxes[:, 2] / 2
    y2 = boxes[:, 1] + boxes[:, 3] / 2
    bboxes = np.stack([x1, y1, x2, y2], axis=1)

    keep_idx = _nms(bboxes, confs, iou_thres)
    if len(keep_idx) == 0:
        return []

    bboxes = bboxes[keep_idx]
    class_ids = class_ids[keep_idx]
    confs = confs[keep_idx]
    masks_coeff = masks_coeff[keep_idx]

    prototypes = output1[0].reshape(NUM_MASK_COEFFS, -1)
    orig_h, orig_w = orig_shape
    scale_ratio = 160.0 / IMGSZ

    detections = []
    for i in range(len(bboxes)):
        mask = masks_coeff[i] @ prototypes
        mask = 1.0 / (1.0 + np.exp(-mask))
        mask = mask.reshape(160, 160)

        x1_i, y1_i, x2_i, y2_i = bboxes[i]

        orig_x1 = max(0, (x1_i - pad_info["x_off"]) / pad_info["scale"])
        orig_y1 = max(0, (y1_i - pad_info["y_off"]) / pad_info["scale"])
        orig_x2 = min(orig_w, (x2_i - pad_info["x_off"]) / pad_info["scale"])
        orig_y2 = min(orig_h, (y2_i - pad_info["y_off"]) / pad_info["scale"])

        bw = max(1, int(orig_x2 - orig_x1))
        bh = max(1, int(orig_y2 - orig_y1))

        mx1 = max(0, int(x1_i * scale_ratio))
        my1 = max(0, int(y1_i * scale_ratio))
        mx2 = min(160, int(x2_i * scale_ratio))
        my2 = min(160, int(y2_i * scale_ratio))

        if mx2 <= mx1 or my2 <= my1:
            continue

        mask_crop = mask[my1:my2, mx1:mx2]

        mask_img = Image.fromarray((mask_crop * 255).astype(np.uint8))
        mask_img = mask_img.resize((bw, bh), Image.LANCZOS)
        mask_resized = np.asarray(mask_img, dtype=np.float32) / 255.0
        mask_binary = (mask_resized > 0.5).astype(np.uint8)

        rle = _mask_to_rle(mask_binary)

        detections.append({
            "class_id": int(class_ids[i]),
            "class_name": CLASSES[int(class_ids[i])],
            "confidence": float(confs[i]),
            "bbox": [int(orig_x1), int(orig_y1), int(orig_x2), int(orig_y2)],
            "mask": {
                "rle": rle,
                "height": bh,
                "width": bw,
            }
        })

    return detections


def _nms(bboxes, scores, iou_threshold):
    x1 = bboxes[:, 0]
    y1 = bboxes[:, 1]
    x2 = bboxes[:, 2]
    y2 = bboxes[:, 3]

    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(i)

        if len(order) == 1:
            break

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        intersection = w * h

        iou = intersection / (areas[i] + areas[order[1:]] - intersection + 1e-10)
        order = order[1:][iou <= iou_threshold]

    return np.array(keep)


def _mask_to_rle(mask):
    flat = mask.flatten()
    if len(flat) == 0:
        return []
    runs = []
    current_val = int(flat[0])
    run_length = 0
    for val in flat:
        if int(val) == current_val:
            run_length += 1
        else:
            runs.append(run_length)
            current_val = int(val)
            run_length = 1
    runs.append(run_length)
    if int(flat[0]) == 1:
        runs.insert(0, 0)
    return runs
