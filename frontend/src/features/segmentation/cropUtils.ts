import type { Detection } from "./segmentUtils";

const MAX_CROP_SIZE = 640;

export function cropDetection(
  image: HTMLImageElement,
  detection: Detection,
): HTMLCanvasElement {
  const [x1, y1, x2, y2] = detection.bbox;
  const cropW = x2 - x1;
  const cropH = y2 - y1;

  const scale = Math.min(MAX_CROP_SIZE / cropW, MAX_CROP_SIZE / cropH, 1);
  const outW = Math.round(cropW * scale);
  const outH = Math.round(cropH * scale);

  const { rle, width: maskW, height: maskH } = detection.mask;

  const bboxCanvas = document.createElement("canvas");
  bboxCanvas.width = cropW;
  bboxCanvas.height = cropH;
  const bboxCtx = bboxCanvas.getContext("2d")!;
  bboxCtx.drawImage(image, x1, y1, cropW, cropH, 0, 0, cropW, cropH);

  const mask = new Uint8Array(maskW * maskH);
  let idx = 0;
  for (let i = 0; i < rle.length; i++) {
    const val = i % 2;
    for (let j = 0; j < rle[i]; j++) {
      mask[idx++] = val;
    }
  }

  const scaleX = cropW / maskW;
  const scaleY = cropH / maskH;

  const bboxData = bboxCtx.getImageData(0, 0, cropW, cropH);
  for (let y = 0; y < cropH; y++) {
    for (let x = 0; x < cropW; x++) {
      const maskX = Math.min(Math.floor(x / scaleX), maskW - 1);
      const maskY = Math.min(Math.floor(y / scaleY), maskH - 1);
      const pixelIdx = (y * cropW + x) * 4 + 3;
      if (!mask[maskY * maskW + maskX]) {
        bboxData.data[pixelIdx] = 0;
      }
    }
  }

  const tempCanvas = document.createElement("canvas");
  tempCanvas.width = cropW;
  tempCanvas.height = cropH;
  tempCanvas.getContext("2d")!.putImageData(bboxData, 0, 0);

  const outCanvas = document.createElement("canvas");
  outCanvas.width = outW;
  outCanvas.height = outH;
  outCanvas.getContext("2d")!.drawImage(tempCanvas, 0, 0, outW, outH);

  return outCanvas;
}

export function canvasToDataUrl(canvas: HTMLCanvasElement): string {
  return canvas.toDataURL("image/jpeg", 0.85);
}
