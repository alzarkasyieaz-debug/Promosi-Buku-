#!/usr/bin/env bash
# Barisan render: untuk setiap "vid:face_x:src", bina base+mask (jika belum) dan render video akhir.
# Guna: SEG_MODEL=... bash tools/queue.sh v03:0.5:/path/a.mov v04:0.5:/path/b.mov
set -uo pipefail
cd "$(dirname "$0")/.."
for item in "$@"; do
  IFS=: read -r vid fx src <<< "$item"; n=${vid#v}; RD=render/$vid; mkdir -p $RD
  echo "[$vid] mula $(date +%T)"
  # tunggu jika base sedang dibina oleh proses lain
  while pgrep -f "build_base.py .* $RD/base.mp4" >/dev/null || pgrep -f "mask_video.py .* $RD/mask.mkv" >/dev/null; do sleep 10; done
  if [ ! -f $RD/mask.mkv ]; then
    python3 edit/build_base.py "$src" $RD/base.mp4 edit/$vid/edl.json "$fx" 0.34 && \
    python3 -I tools/mask_video.py "$SEG_MODEL" $RD/base.mp4 $RD/mask.mkv || { echo "[$vid] GAGAL base"; continue; }
  fi
  RD=$RD DATA=overlay-data-$vid.js CTAV=$vid COVER=cover/cover-video-$n.png OUT=NKT-$n-final.mp4 bash tools/final.sh \
    && echo "[$vid] SIAP $(date +%T)" || echo "[$vid] GAGAL final"
done
