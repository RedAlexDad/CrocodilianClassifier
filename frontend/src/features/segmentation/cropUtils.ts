import type { Detection } from "./segmentUtils";

export function cropDetection(
  image: HTMLImageElement,
  detection: Detection,
): HTMLCanvasElement {
  const [x1, y1, x2, y2] = detection.bbox;
  const cropW = x2 - x1;
  const cropH = y2 - y1;

  const canvas = document.createElement("canvas");
  const bboxCanvas = document.createElement("canvas");
  bboxCanvas.width = cropW;
  bboxCanvas.height = cropH;
  const bboxCtx = bboxCanvas.getContext("2d")!;
  bboxCtx.drawImage(image, x1, y1, cropW, cropH, 0, 0, cropW, cropH);

  const mask = new Uint8Array(cropW * cropH);
  const { rle, width: maskW, height: maskH } = detection.mask;
  let idx = 0;
  for (let i = 0; i < rle.length; i++) {
    const val = i % 2;
    for (let j = 0; j < rle[i]; j++) {
      mask[idx++] = val;
    }
  }

  const scaleX = cropW / maskW;
  const scaleY = cropH / maskH;

  canvas.width = cropW;
  canvas.height = cropH;
  const ctx = canvas.getContext("2d")!;

  const imageData = bboxCtx.getImageData(0, 0, cropW, cropH);
  for (let y = 0; y < cropH; y++) {
    for (let x = 0; x < cropW; x++) {
      const maskX = Math.min(Math.floor(x / scaleX), maskW - 1);
      const maskY = Math.min(Math.floor(y / scaleY), maskH - 1);
      const pixelIdx = (y * cropW + x) * 4 + 3;
      if (!mask[maskY * maskW + maskX]) {
        imageData.data[pixelIdx] = 0;
      }
    }
  }
  ctx.putImageData(imageData, 0, 0);

  return canvas;
}

export function canvasToDataUrl(canvas: HTMLCanvasElement): string {
  return canvas.toDataURL("image/png");
}
