"""Potong subjek (penceramah) daripada frame -> PNG beralfa.
Model: onnx-community/mediapipe_selfie_segmentation (Apache-2.0).
Guna: python3 tools/cutout.py model.onnx input.jpg output.png"""
import sys, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
model, src, out = sys.argv[1:4]
im = Image.open(src).convert("RGB")
s = ort.InferenceSession(model)
# jalankan pada beberapa jubin bertindih untuk resolusi lebih baik pada imej potret
x = np.asarray(im.resize((256, 256), Image.BILINEAR), np.float32).transpose(2, 0, 1)[None] / 255.0
a = s.run(None, {"pixel_values": x})[0][0, 0]
m = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize(im.size, Image.BICUBIC)
m = m.filter(ImageFilter.GaussianBlur(2)).point(lambda v: 0 if v < 90 else (255 if v > 170 else int((v - 90) * 255 / 80)))
im.putalpha(m); im.save(out)
