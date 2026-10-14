# Anthropic Academy — рилс про бесплатную академию Anthropic

Вертикальный ролик 1080×1920, 30 fps, ~51 с, 21 сцена. Голос ElevenLabs (Jack John), синтезированные
звуки переходов и музыка. Результат — `reel_final.mp4`.

Устроен как шаблон для длинных роликов: каждая сцена — функция `B[i](t, L)` в `index.html`,
старты сцен `cues` в `timing.json` взяты из пауз озвучки (`./pauses.sh voice.mp3`).

```bash
npm i
node render.js --snap 1,5,10      # проверочные кадры
node render.js                    # silent.mp4
PYTHON=python3 bash mix.sh        # нужен numpy -> reel_final.mp4
```
