#!/bin/bash
# Make the grammar MP4s on a CPU pod and put the two zips on Dropbox (see README, "Grammar videos").
#   bash tools/video/pod_run.sh <commit>      (run from the pod's /workspace; logs to /workspace/video.log)
set -euo pipefail
COMMIT=${1:-main}
cd /workspace
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq ffmpeg zip git > /dev/null
[ -d basic1000 ] || git clone -q https://github.com/johnlqdev/basic1000.git
cd basic1000 && git fetch -q origin && git checkout -q "$COMMIT"
OUT=/workspace/out
python3 tools/video/render.py --out "$OUT" --workers "${WORKERS:-12}" --preset medium --crf 20
for L in desktop phone; do
  n=$(ls "$OUT/$L"/*.mp4 | wc -l)
  [ "$n" -eq 46 ] || { echo "only $n $L films"; exit 1; }
  (cd "$OUT/$L" && rm -f "/workspace/grammar_46_$L.zip" && zip -q -0 "/workspace/grammar_46_$L.zip" *.mp4)
done
ls -la /workspace/*.zip
python3 tools/video/upload.py /basic1000-backup/grammar-videos /workspace/grammar_46_phone.zip /workspace/grammar_46_desktop.zip
echo ALL DONE
