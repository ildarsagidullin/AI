#!/usr/bin/env bash
# Делит озвучку на фразы по паузам: печатает "N  начало–конец" для каждой фразы.
# ./pauses.sh voice.mp3 [порог_dB=-35] [мин_пауза_сек=0.12]
set -euo pipefail
F=${1:-voice.mp3}; DB=${2:--35}; D=${3:-0.12}
LEN=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F")
ffmpeg -v info -i "$F" -af "silencedetect=n=${DB}dB:d=${D}" -f null - 2>&1 \
 | grep -o "silence_\(start\|end\): [0-9.]*" | awk -v len="$LEN" '
  BEGIN{s=0;n=0}
  /silence_start/{ if($2-s>0.05) printf "%2d  %6.2f – %6.2f\n", ++n, s, $2 }
  /silence_end/{ s=$2 }
  END{ if(len-s>0.05) printf "%2d  %6.2f – %6.2f\n", ++n, s, len; printf "длина: %.2f c\n", len }'
