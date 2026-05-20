export const CLASS_COLORS = [
  { r: 239, g: 68, b: 68 },
  { r: 34, g: 197, b: 94 },
  { r: 59, g: 130, b: 246 },
];

export const CLASS_NAMES = ["Аллигатор", "Кайман", "Крокодил"];

export interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number];
  mask: {
    rle: number[];
    height: number;
    width: number;
  };
}

export function decodeRle(
  rle: number[],
  height: number,
  width: number,
): Uint8Array {
  const mask = new Uint8Array(height * width);
  let idx = 0;
  for (let i = 0; i < rle.length; i++) {
    const val = i % 2;
    for (let j = 0; j < rle[i]; j++) {
      mask[idx++] = val;
    }
  }
  return mask;
}

export function drawMasksOnCanvas(
  canvas: HTMLCanvasElement,
  image: HTMLImageElement,
  detections: Detection[],
): void {
  const ctx = canvas.getContext("2d")!;
  canvas.width = image.naturalWidth;
  canvas.height = image.naturalHeight;

  ctx.drawImage(image, 0, 0);

  for (const det of detections) {
    const color = CLASS_COLORS[det.class_id] || { r: 128, g: 128, b: 128 };
    const [x1, y1, x2, y2] = det.bbox;
    const { rle, height, width } = det.mask;

    const mask = decodeRle(rle, height, width);

    const imageData = ctx.getImageData(x1, y1, width, height);
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const maskIdx = y * width + x;
        if (mask[maskIdx]) {
          const pixelIdx = (y * width + x) * 4;
          imageData.data[pixelIdx + 0] =
            imageData.data[pixelIdx + 0] * 0.5 + color.r * 0.5;
          imageData.data[pixelIdx + 1] =
            imageData.data[pixelIdx + 1] * 0.5 + color.g * 0.5;
          imageData.data[pixelIdx + 2] =
            imageData.data[pixelIdx + 2] * 0.5 + color.b * 0.5;
        }
      }
    }
    ctx.putImageData(imageData, x1, y1);

    ctx.strokeStyle = `rgb(${color.r},${color.g},${color.b})`;
    ctx.lineWidth = 3;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

    const label = `${det.class_name} (${(det.confidence * 100).toFixed(1)}%)`;
    ctx.font = "bold 16px sans-serif";
    const textMetrics = ctx.measureText(label);
    const labelH = 24;
    const labelY = y1 > labelH + 4 ? y1 - labelH - 2 : y1;

    ctx.fillStyle = `rgb(${color.r},${color.g},${color.b})`;
    ctx.fillRect(x1, labelY, textMetrics.width + 8, labelH);
    ctx.fillStyle = "#fff";
    ctx.fillText(label, x1 + 4, labelY + 17);
  }
}
