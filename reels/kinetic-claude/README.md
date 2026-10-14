# Kinetic Claude — рилс с кинетической типографикой

Вертикальный ролик 1080×1920, 30 fps, ~19 с. Голос ElevenLabs, синтезированные звуки переходов и фоновая музыка.
Готовый результат — `reel_final.mp4`.

## Как устроено

| Файл | Что делает |
|---|---|
| `index.html` | Все сцены и анимация (GSAP-таймлайн). `window.seek(t)` ставит кадр на время `t` |
| `timing.json` | Озвучка, fps и якоря `[время в ролике, время в анимации]`: подгоняют сцены под фразы |
| `render.js` | Покадровый рендер через Chromium (Playwright) → `silent.mp4`. `--snap 1,5,9` — проверочные кадры |
| `pauses.sh` | Делит озвучку на фразы по паузам — отсюда берутся тайминги для якорей |
| `sound.py` | Синтез SFX (удары, свисты, лазер, щелчки, райзеры) и музыки (120 BPM) → `sfx.wav`, `music.wav` |
| `mix.sh` | Сведение: голос + SFX + музыка (приглушается под голос), громкость −14 LUFS → `reel_final.mp4` |
| `fonts/` | Unbounded, Oswald, Playfair Display (SIL Open Font License, Google Fonts) |

## Пересборка

```bash
npm i                      # gsap
pip install numpy          # для sound.py
./pauses.sh voice.mp3      # фразы озвучки
node render.js --snap 1,5,9   # проверочные кадры
node render.js             # silent.mp4
PYTHON=python3 bash mix.sh # reel_final.mp4  (MUSIC_VOL / SFX_VOL — громкость)
```

Нужны Node 18+, Playwright с Chromium (`CHROMIUM=/путь` — свой бинарник), ffmpeg, Python 3 с numpy.
