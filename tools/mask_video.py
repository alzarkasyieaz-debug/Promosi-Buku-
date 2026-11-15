"""Jana mask subjek (penceramah) untuk setiap frame video -> video mask kelabu (ffv1).
Digunakan untuk kesan text-behind-subject.
Guna: python3 -I tools/mask_video.py model.onnx render/base.mp4 render/mask.mkv"""
import sys, subprocess, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
model, src, out = sys.argv[1:4]
W, H, w, h = 1080, 1920, 270, 480
sess = ort.InferenceSession(model)
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30",
                        "-i", "-", "-c:v", "ffv1", out], stdin=subprocess.PIPE)
prev, n = None, 0
while True:
    buf = dec.stdout.read(w * h * 3)
    if len(buf) < w * h * 3: break
    im = Image.frombuffer("RGB", (w, h), buf)
    x = np.asarray(im.resize((256, 256), Image.BILINEAR), np.float32).transpose(2, 0, 1)[None] / 255.0
    a = sess.run(None, {"pixel_values": x})[0][0, 0]
    a = np.clip((a - .35) / .3, 0, 1)                      # tajamkan tepi
    prev = a if prev is None else .55 * a + .45 * prev     # licin temporal (kurang kelip)
    m = Image.fromarray((prev * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
    enc.stdin.write(m.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n)
