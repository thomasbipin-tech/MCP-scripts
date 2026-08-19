#!/usr/bin/env bash
# Drive a cut to completion regardless of container restarts.
#   - progress is judged by frames on disk (never pgrep: it self-matches)
#   - if the frame count stops moving, the renderer is restarted with RESUME=1
#   - when all frames exist, it encodes
cd "$(dirname "$0")"
SLUG="$1"; PORT="${2:-8500}"; N="$3"; RPID="${4:-}"   # RPID = renderer we own, if any
# ffmpeg: the system build if present, else the wheel-bundled one. The container is
# rebuilt between sessions and only one of the two survives.
FF=$(command -v ffmpeg || echo /usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2)
export NODE_PATH=$(npm root -g)
stall=0; last=-1
while :; do
  have=$(ls "frames_${SLUG}" 2>/dev/null | wc -l)
  if [ "$have" -ge "$N" ]; then break; fi
  if [ "$have" -eq "$last" ]; then stall=$((stall+1)); else stall=0; fi
  last=$have
  if [ "$stall" -ge 4 ]; then
    echo "$(date +%H:%M:%S) stalled at ${have}/${N} — restarting renderer"
    # Kill ONLY the renderer this script owns. A blanket `pkill -9 -x node` also kills
    # unrelated renders running in parallel -- same class of bug as `pkill -f capture.js`
    # matching this script's own command line.
    [ -n "$RPID" ] && kill -9 "$RPID" 2>/dev/null
    sleep 3
    TL="timeline_${SLUG}.json" FRAMES="frames_${SLUG}" PORT="$PORT" RESUME=1 \
      nohup node capture.js all >> "render_${SLUG}.log" 2>&1 &
    RPID=$!
    stall=0; sleep 20
  fi
  sleep 30
done
echo "$(date +%H:%M:%S) frames complete (${N}) — encoding"
$FF -y -hide_banner -loglevel error -framerate 30 -i "frames_${SLUG}/%05d.png" \
  -i "audio_${SLUG}.wav" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p \
  -profile:v high -level 4.2 -c:a aac -b:a 192k -movflags +faststart -shortest \
  "netforge-${SLUG}.mp4"
rm -rf "frames_${SLUG}"
echo "DONE $(ls -lh netforge-${SLUG}.mp4 | awk '{print $9"  "$5}')"
