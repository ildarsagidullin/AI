"""Ужимает паузы в озвучке и слегка ускоряет её.
python3 tighten.py voice_raw.mp3 voice.mp3 [пауза=0.1] [темп=1.08]
Пишет segments.json — начало/конец каждой фразы в НОВОМ аудио (для cues в timing.json)."""
import json, re, subprocess, sys, wave
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
GAP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
TEMPO = float(sys.argv[4]) if len(sys.argv) > 4 else 1.08
SR = 48000

log = subprocess.run(['ffmpeg', '-i', src, '-af', 'silencedetect=n=-35dB:d=0.12', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                     capture_output=True).stdout
x = np.frombuffer(raw, np.float32)
dur = len(x) / SR
# фразы = промежутки между тишинами; по краям оставляем 30 мс, чтобы не резать атаки
segs, s = [], 0.0
for a, b in zip(starts, ends + [dur]):
    if a - s > 0.05: segs.append((s, a))
    s = b
if dur - s > 0.05: segs.append((s, dur))
PAD = 0.03
out, new, t = [], [], 0.0
for i, (a, b) in enumerate(segs):
    a2, b2 = max(0, a - PAD), min(dur, b + PAD)
    piece = x[int(a2 * SR):int(b2 * SR)].copy()
    f = min(len(piece), int(0.008 * SR)); piece[:f] *= np.linspace(0, 1, f); piece[-f:] *= np.linspace(1, 0, f)
    new.append((t + (a - a2), t + (a - a2) + (b - a)))
    out.append(piece); t += len(piece) / SR
    if i < len(segs) - 1:
        out.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
y = np.concatenate(out)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                '-af', f'atempo={TEMPO}', '-c:a', 'libmp3lame', '-b:a', '192k', dst], input=y.tobytes(), check=True)
segs_new = [[round(a / TEMPO, 3), round(b / TEMPO, 3)] for a, b in new]
json.dump({'segments': segs_new, 'duration': round(t / TEMPO, 3)}, open('segments.json', 'w'), indent=1)
for i, (a, b) in enumerate(segs_new, 1): print(f'{i:2d}  {a:6.2f} – {b:6.2f}')
print(f'длина: {dur:.2f} → {t / TEMPO:.2f} c')
