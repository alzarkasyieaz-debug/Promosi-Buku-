"""Bina video asas daripada NKT.mov mengikut edit/edl.json.

- Potong & susun segmen (cold-open + jump cut)
- Zoom per segmen (punch-in / slow push-in) dengan eval per-frame
- Color grade sinematik hangat (selaras palet buku)
- Audio: high-pass, denoise ringan, loudnorm -14 LUFS (standard media sosial)

Guna: python3 edit/build_base.py <NKT.mov> <out.mp4>
"""
import json, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
src, out = sys.argv[1], sys.argv[2]
segs = json.load(open(ROOT / "edit/edl.json"))["segments"]

GRADE = ("eq=contrast=1.07:saturation=0.88:gamma=0.97,"
         "colorbalance=rs=0.02:bs=-0.04:rm=0.04:gm=0.01:bm=-0.04:rh=0.03:bh=-0.03,"
         "vignette=PI/5")
FACE_Y = 0.34  # titik tumpu zoom menegak (0=atas, 1=bawah) — wajah penceramah

import tempfile, os
tmp = pathlib.Path(tempfile.mkdtemp(prefix="nkt_"))
lst = []
for i, s in enumerate(segs):
    a, b = s["src_in"], s["src_out"]; d = b - a
    z0, z1 = s["zoom"]
    z = f"({z0}+({z1}-{z0})*t/{d:.3f})"
    vf = (f"scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame,"
          f"crop=1080:1920:'(iw-1080)/2':'(ih-1920)*{FACE_Y}',setsar=1,fps=30,{GRADE},format=yuv420p")
    n = round(d * 30)
    af = f"afade=t=in:d=0.015,afade=t=out:st={n/30-0.015:.4f}:d=0.015,apad,atrim=0:{n/30:.4f}"
    seg = tmp / f"s{i:02d}.mkv"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{d:.3f}", "-i", src,
                    "-vf", vf, "-af", af, "-frames:v", str(n), "-c:v", "libx264", "-preset", "fast", "-crf", "14",
                    "-c:a", "pcm_s16le", "-ar", "48000", str(seg)], check=True)
    lst.append(f"file '{seg}'")
(tmp / "list.txt").write_text("\n".join(lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                "-af", "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=2.5:attack=10:release=200,"
                       "loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000",
                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print("OK", out)
