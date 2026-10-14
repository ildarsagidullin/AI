#!/usr/bin/env bash
# Синтез звуков (sound.py) и сведение: голос + SFX + музыка с приглушением под голос -> reel_final.mp4
set -euo pipefail
cd "$(dirname "$0")"
VOICE=$(python3 -c "import json;print(json.load(open('timing.json'))['voice'])")
DUR=$(python3 -c "import json;print(json.load(open('timing.json'))['anchors'][-1][0])")
"${PYTHON:-python3}" -I sound.py   # нужен numpy
ffmpeg -v error -y -i silent.mp4 -i "$VOICE" -i sfx.wav -i music.wav -filter_complex "
[1:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[v1][vsc];
[3:a]volume=${MUSIC_VOL:-0.19}[m];
[m][vsc]sidechaincompress=threshold=0.03:ratio=5:attack=15:release=300[md];
[2:a]volume=${SFX_VOL:-0.27}[s];
[v1][s][md]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95,loudnorm=I=-14:TP=-1:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t "$DUR" reel_final.mp4
echo "reel_final.mp4 готов"
