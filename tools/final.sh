#!/usr/bin/env bash
# Gabung video asas + overlay telus + babak CTA/outro -> "$RD/$OUT"
# Prasyarat: $RD/base.mp4 (edit/build_base.py)
set -euo pipefail
cd "$(dirname "$0")/.."
# Tetapan per video (lalai = video 01). Contoh video 02:
#   RD=render/v02 DATA=overlay-data-v02.js CTAV=v02 COVER=cover/cover-video-02.png OUT=NKT-02-final.mp4 bash tools/final.sh
RD=${RD:-render}; DATA=${DATA:-overlay-data.js}; CTAV=${CTAV:-v01}
COVER=${COVER:-cover/cover-video-01.png}; OUT=${OUT:-NKT-01-final.mp4}
# Mask penceramah untuk text-behind-subject (model: onnx-community/mediapipe_selfie_segmentation)
[ -f $RD/mask.mkv ] || python3 -I tools/mask_video.py "${SEG_MODEL:?set SEG_MODEL=path/model.onnx}" $RD/base.mp4 $RD/mask.mkv
[ -d $RD/ovb ] || node tools/render-motion.js "motion/overlay.html?layer=behind&data=$DATA" $RD/ovb 30 --alpha
[ -d $RD/ov ]  || node tools/render-motion.js "motion/overlay.html?layer=front&data=$DATA"  $RD/ov  30 --alpha
[ -d $RD/cta ] || node tools/render-motion.js "motion/cta-outro.html?v=$CTAV" $RD/cta 30
# Komposit: video -> kata belakang -> penceramah (mask) -> lapisan hadapan
ffmpeg -v error -y -i $RD/base.mp4 -i $RD/mask.mkv -framerate 30 -i $RD/ovb/f%05d.png -framerate 30 -i $RD/ov/f%05d.png \
  -filter_complex "[0:v]split[a][b];[a][2:v]overlay[bg];[b][1:v]alphamerge[p];[bg][p]overlay[x];[x][3:v]overlay,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -preset medium -crf 17 -c:a copy $RD/main.mp4
ffmpeg -v error -y -framerate 30 -i $RD/cta/f%05d.png -f lavfi -i anullsrc=r=48000:cl=stereo \
  -shortest -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k $RD/cta.mp4
# Cover video sebagai pembuka 0.6s (frame pertama = thumbnail automatik), zoom-in perlahan
ffmpeg -v error -y -loop 1 -framerate 30 -i "$COVER" -f lavfi -i anullsrc=r=48000:cl=stereo \
  -vf "scale=1188:2112,zoompan=z='1+0.0015*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p" \
  -frames:v 18 -t 0.6 -c:v libx264 -preset medium -crf 15 -c:a aac -b:a 192k $RD/cover.mp4
ffmpeg -v error -y -i $RD/cover.mp4 -i $RD/main.mp4 -i $RD/cta.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart \
  "$RD/$OUT"
ffprobe -v error -show_entries format=duration,size -of compact "$RD/$OUT"
