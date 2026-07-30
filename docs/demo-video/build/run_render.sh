#!/usr/bin/env bash
# Render one cut, resumable. Progress is judged by frames on disk, never by pgrep -- a
# pattern like "capture.js" matches this script's own command line and reports false alive.
cd "$(dirname "$0")"
SLUG="$1"; PORT="${2:-8500}"
export NODE_PATH=$(npm root -g)
for attempt in 1 2 3 4 5 6 7 8; do
  TL="timeline_${SLUG}.json" FRAMES="frames_${SLUG}" PORT="$PORT" RESUME=1 \
    node capture.js all >> "render_${SLUG}.log" 2>&1 && break
  echo "attempt $attempt ended early, resuming in 10s" >> "render_${SLUG}.log"
  sleep 10
done
