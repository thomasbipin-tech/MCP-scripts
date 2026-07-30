#!/usr/bin/env bash
# Build a single cut by slug: build_one.sh <slug> [port]
set -euo pipefail
cd "$(dirname "$0")"
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
export NODE_PATH=$(npm root -g)
SLUG="$1"; PORT="${2:-8500}"
TL_PATH="timeline_${SLUG}.json" VO_PATH="vo_${SLUG}.wav" MUSIC_OUT="music_${SLUG}.wav" python3 music.py
$FF -y -hide_banner -loglevel error -i "vo_${SLUG}.wav" -i "music_${SLUG}.wav" \
  -filter_complex "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=0.92[v];[1:a]aresample=48000[m];[v][m]amix=inputs=2:normalize=0:duration=longest[mx];[mx]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
  -map "[a]" -ar 48000 -ac 2 -c:a pcm_s16le "audio_${SLUG}.wav"
TL="timeline_${SLUG}.json" FRAMES="frames_${SLUG}" PORT="$PORT" node capture.js all > "render_${SLUG}.log" 2>&1
$FF -y -hide_banner -loglevel error -framerate 30 -i "frames_${SLUG}/%05d.png" -i "audio_${SLUG}.wav" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -level 4.2 \
  -c:a aac -b:a 192k -movflags +faststart -shortest "netforge-${SLUG}.mp4"
rm -rf "frames_${SLUG}"
ls -lh "netforge-${SLUG}.mp4" | awk '{print "    -> "$9"  "$5}'
