"""Синтез SFX и фоновой музыки под ролик. Пишет sfx.wav и music.wav (48 кГц, стерео)."""
import numpy as np, wave

SR = 48000
DUR = __import__('json').load(open('timing.json'))['end'] + 0.3
rng = np.random.default_rng(7)
N = int(SR * DUR)


def t_(d):
    return np.arange(int(SR * d)) / SR


def lp(x, a):  # однополюсный ФНЧ, a in (0,1): меньше = темнее
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x):
        s += a * (v - s); y[i] = s
    return y


def lp_sweep(x, a0, a1):
    a = np.linspace(a0, a1, len(x)); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x):
        s += a[i] * (v - s); y[i] = s
    return y


def env(n, att, rel_pow=1.0):
    e = np.ones(n); k = max(1, int(att * SR)); e[:k] = np.linspace(0, 1, k)
    e[k:] = np.linspace(1, 0, n - k) ** rel_pow
    return e


# ---------- звуки ----------
def whoosh(d=0.35, up=True, amp=0.5):
    n = int(SR * d); x = rng.standard_normal(n)
    y = lp_sweep(x, 0.02, 0.35) if up else lp_sweep(x, 0.35, 0.02)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return y * e * amp * 2.5


def impact(amp=1.0, f0=110, f1=38, d=0.7):
    t = t_(d)
    f = f1 + (f0 - f1) * np.exp(-t * 25)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    click = lp(rng.standard_normal(len(t)), 0.5) * np.exp(-t * 60) * 0.6
    tail = lp(rng.standard_normal(len(t)), 0.05) * np.exp(-t * 4) * 0.5
    return np.tanh((body + click + tail) * 1.8) * amp


def tick(amp=0.35):
    t = t_(0.05)
    return (np.sin(2 * np.pi * 2400 * t) + rng.standard_normal(len(t)) * 0.3) * np.exp(-t * 120) * amp


def laser(d=0.45, amp=0.3):
    t = t_(d); f = 2600 * np.exp(-t * 4) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.01, 1.5) * amp


def riser(d=0.6, amp=0.4):
    t = t_(d); f = 200 + 1800 * (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    nz = lp_sweep(rng.standard_normal(len(t)), 0.01, 0.4)
    return (tone + nz * 1.5) * (t / d) ** 2 * amp


def blip(f=880, amp=0.25):
    t = t_(0.12)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 30) * amp


def clatter(d=0.6, amp=0.3):
    out = np.zeros(int(SR * d))
    for _ in range(18):
        s = tick(amp * rng.uniform(.3, 1)); p = rng.integers(0, len(out) - len(s))
        out[p:p + len(s)] += s
    return out


def zip_(d=0.3, amp=0.3):
    t = t_(d); f = 400 + 3000 * t / d
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * lp(np.ones(len(t)), 1) * env(len(t), .02) * amp * 0.4


sfx = np.zeros((N, 2))


def put(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR); j = min(N, i + len(sig)); s = sig[:j - i] * gain
    sfx[i:j, 0] += s * (1 - max(0, pan)); sfx[i:j, 1] += s * (1 + min(0, pan))


# таймкоды берутся из timing.json: cues — старты сцен
import json
CFG = json.load(open('timing.json'))
C = CFG['cues']
L = [b - a for a, b in zip(C, C[1:] + [CFG['end']])]
# тип входа сцены: i — удар, w — свист, h — мягкий удар
ENTRY = 'iwwiiiwwiiwiwiihiwwwi'
for k, t in enumerate(C):
    e = ENTRY[k]
    if e == 'i': put(impact(.9), t + 0.08)
    elif e == 'h': put(impact(1.1, 120), t)
    else: put(whoosh(.35, True, .5), t - 0.05, (k % 2) * .6 - .3)
    if k: put(whoosh(.25, False, .45), t - 0.22, .3 - (k % 2) * .6)   # вылет прошлой сцены
# особые моменты внутри сцен (смещения как в index.html)
put(impact(.6, 150, 50, .4), C[0] + .24); put(impact(.7, 100), C[0] + .52)
put(laser(.5, .2), C[1] + .2)
put(impact(.6, 140), C[2] + L[2] * .62)                               # CLAUDE
put(impact(.6, 150), C[3] + L[3] * .2); put(impact(1.0), C[3] + L[3] * .65)  # ПО AI
put(impact(.9, 120), C[4] + .12)                                      # 13
for k in range(7): put(tick(.3), C[5] + .1 + L[5] * .5 * ((k + 1) / 7) ** .5)  # счётчик
put(impact(1.0, 130), C[5] + .1 + L[5] * .5)                          # 20
put(zip_(), C[6] + L[6] * .5); put(impact(.5, 180, 60, .4), C[6] + L[6] * .5 + .3)
put(impact(.7, 140), C[7] + L[7] * .62)
for k in range(3): put(whoosh(.2, True, .35), C[8] + L[8] * .45 + k * .1)
for k in range(7): put(tick(.25), C[9] + .25 + k * .04)
put(whoosh(.3, True, .4), C[10] + .1); put(whoosh(.3, True, .4), C[10] + .1 + L[10] * .5)
put(impact(.8), C[11] + .25)
for k in range(6): put(tick(.3), C[11] + L[11] * .55 + k * .07)
for k in range(3): put(whoosh(.25, True, .4), C[12] + .25 + k * L[12] * .28)
put(impact(.6, 140), C[13] + L[13] * .5)
put(riser(.6, .35), C[15] + L[15] - .6)
put(impact(1.1, 90, 30, 1.2), C[16] + .3)                             # 0 ₽
for k in range(12): put(tick(.22), C[17] + .55 + k * L[17] * .5 / 12)
for k in range(22): put(tick(.22), C[18] + .6 + k * L[18] * .45 / 22)
put(whoosh(.4, True, .4), C[19] + L[19] * .62); put(impact(.7, 140), C[19] + L[19] * .72)
put(impact(1.0, 80, 30, 2.5), C[20] + .45)

# ---------- музыка: 120 BPM, тёмный бит ----------
BPM = 120; beat = 60 / BPM
mus = np.zeros((N, 2))


def mput(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N: return
    j = min(N, i + len(sig)); s = sig[:j - i] * gain
    mus[i:j, 0] += s * (1 - max(0, pan)); mus[i:j, 1] += s * (1 + min(0, pan))


def kick():
    t = t_(0.4); f = 45 + 110 * np.exp(-t * 30)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 2.2) * 0.8


def hat(open_=False):
    t = t_(0.2 if open_ else 0.05); x = rng.standard_normal(len(t))
    x = x - lp(x, 0.3)
    return x * np.exp(-t * (18 if open_ else 90)) * 0.18


def snare():
    t = t_(0.25)
    return (lp(rng.standard_normal(len(t)), 0.4) * np.exp(-t * 18) * 0.5 +
            np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.3)


# тональность: ре минор, бас ре-ре-сиb-до
roots = [36.71, 36.71, 29.14, 32.70]
silent = (C[16] - 0.55, C[16])  # провал перед «Всё бесплатно»
END = C[20] + 2.0
b = 0
while b * beat < END:
    at = b * beat
    if not (silent[0] <= at < silent[1]):
        bar = b // 4
        if at >= 0.0:
            mput(kick(), at)
        if b % 4 in (1, 3) and at >= 3.75:
            mput(snare(), at, 0, .8)
        for h in (0, 0.5):
            mput(hat(h == 0.5 and b % 2), at + h * beat, .35 if h else -.35)
        # пульсирующий бас восьмыми
        f = roots[bar % 4] * 2
        for e in (0, .5):
            t = t_(beat / 2)
            saw = 2 * ((f * t) % 1) - 1
            bs = lp(saw, 0.04) * np.exp(-t * 6) * 0.55
            mput(bs, at + e * beat)
    b += 1

# пэд-дрон по всей длине
t = np.arange(N) / SR
pad = np.zeros(N)
for f, g in ((73.42, .5), (110.0, .35), (146.83, .25), (174.61, .2)):
    pad += np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * .2 * t) * 2) * g
pad = lp(pad, 0.05) * 0.18
padenv = np.clip(t / 1.0, 0, 1) * np.clip((DUR - t) / 2.0, 0, 1)
pad *= padenv
mute = (t >= silent[0]) & (t < silent[1])
pad[mute] *= 0.4
mus[:, 0] += pad; mus[:, 1] += pad * 0.95
# финальный хвост: затухание после логотипа
fade = np.clip((DUR - t) / 3.0, 0, 1)
mus *= fade[:, None]


def save(name, x, peak=0.89):
    x = x / max(1e-9, np.abs(x).max()) * peak
    with wave.open(name, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())


save('sfx.wav', sfx)
save('music.wav', mus)
print('ok')
