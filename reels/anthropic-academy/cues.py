"""Пересчитывает cues в timing.json из segments.json (после tighten.py).
scene_segments[i] — номер фразы (с 1), на которой стартует сцена i."""
import json
T = json.load(open('timing.json')); S = json.load(open('segments.json'))['segments']
T['cues'] = [0.0 if i == 0 else round(S[n - 1][0] - T.get('lead', 0.06), 2) for i, n in enumerate(T['scene_segments'])]
T['end'] = round(S[-1][1] + T.get('tail', 1.6), 2)
json.dump(T, open('timing.json', 'w'), ensure_ascii=False, indent=1)
print(T['cues'], T['end'])
