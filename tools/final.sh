#!/usr/bin/env bash
# Gabung video asas + overlay telus + babak CTA/outro -> render/NKT-01-final.mp4
# Prasyarat: render/base.mp4 (edit/build_base.py)
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d render/ov ]  || node tools/render-motion.js motion/overlay.html   render/ov  30 --alpha
[ -d render/cta ] || node tools/render-motion.js motion/cta-outro.html render/cta 30
ffmpeg -v error -y -i render/base.mp4 -framerate 30 -i render/ov/f%05d.png \
  -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass:shortest=0,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -preset medium -crf 17 -c:a copy render/main.mp4
ffmpeg -v error -y -framerate 30 -i render/cta/f%05d.png -f lavfi -i anullsrc=r=48000:cl=stereo \
  -shortest -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k render/cta.mp4
# Cover video sebagai pembuka 0.6s (frame pertama = thumbnail automatik), zoom-in perlahan
ffmpeg -v error -y -loop 1 -framerate 30 -i cover/cover-video-01.png -f lavfi -i anullsrc=r=48000:cl=stereo \
  -vf "scale=1188:2112,zoompan=z='1+0.0015*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p" \
  -frames:v 18 -t 0.6 -c:v libx264 -preset medium -crf 15 -c:a aac -b:a 192k render/cover.mp4
ffmpeg -v error -y -i render/cover.mp4 -i render/main.mp4 -i render/cta.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart \
  render/NKT-01-final.mp4
ffprobe -v error -show_entries format=duration,size -of compact render/NKT-01-final.mp4
