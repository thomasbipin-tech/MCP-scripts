#!/usr/bin/env bash
cd "$(dirname "$0")"
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
export NODE_PATH=$(npm root -g)
port=8600
while read -r SLUG N <&3; do
  [ -f "netforge-${SLUG}.mp4" ] && { echo "skip ${SLUG} (done)"; continue; }
  port=$((port+1))
  echo "=== ${SLUG} (${N} frames) ==="
  TL_PATH="timeline_${SLUG}.json" VO_PATH="vo_${SLUG}.wav" MUSIC_OUT="music_${SLUG}.wav" python3 music.py >/dev/null </dev/null
  $FF -y -hide_banner -loglevel error -i "vo_${SLUG}.wav" -i "music_${SLUG}.wav" \
    -filter_complex "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=0.92[v];[1:a]aresample=48000[m];[v][m]amix=inputs=2:normalize=0:duration=longest[mx];[mx]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
    -map "[a]" -ar 48000 -ac 2 -c:a pcm_s16le "audio_${SLUG}.wav"
  TL="timeline_${SLUG}.json" FRAMES="frames_${SLUG}" PORT="$port" RESUME=1 \
    nohup node capture.js all >> "render_${SLUG}.log" 2>&1 </dev/null &
  sleep 15
  ./watch_build.sh "$SLUG" "$port" "$N" </dev/null
done 3< episodes.txt
echo "=== ALL EPISODES DONE ==="
