"""Audio for 'Tumble & Pip, Episode 1'. 3/4 waltz band (marimba, plucked bass, music box, pad, shaker, triangle),
sung TTS tuned by phrase, weather SFX. Writes out/audio.wav, out/voice.wav, out/word_times.json, out/vocal_log.json,
out/mouth.json (per-frame mouth opening for lip sync)."""
import json, os, subprocess, re
import numpy as np, soundfile as sf
from scipy import signal
from kokoro_onnx import Kokoro
import timeline as T
from sing import sing_phrase

SR = 44100
N = int(T.DURATION * SR) + SR
rng = np.random.default_rng(21)
os.makedirs("out/tts", exist_ok=True)

def at(sec): return int(round(sec * SR))
def add(buf, x, sec, gain=1.0):
    i = at(sec)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += gain * x[:n]

# ---------------- voice ----------------
kok = Kokoro("assets/kokoro-v1.0.onnx", "assets/voices-v1.0.bin")
def tts(text, path, speed=0.95):
    if not os.path.exists(path):
        x, sr = kok.create(text, voice=T.VOICE, speed=speed)
        sf.write(path, x, sr)
    return path

voice = np.zeros(N)
vlog, words, items = [], [], []
for i, p in enumerate(T.PHRASES):
    path = tts(p["text"], f"out/tts/p{i:02d}.wav")
    b0 = p["notes"][0][0]
    on = [(n[0] - b0) * T.BEAT for n in p["notes"]]
    du = [n[1] * T.BEAT for n in p["notes"]]
    y, lead = sing_phrase(path, on, du, [n[2] for n in p["notes"]])
    items.append([T.t(b0) - lead, y, p, i])
for idx, (s0, y, p, i) in enumerate(items):
    cut = 0.0
    if idx + 1 < len(items):
        nb = T.t(items[idx + 1][2]["notes"][0][0])
        lim = min(nb - 0.13, items[idx + 1][0] - 0.04)
        cap = int((lim - s0) * SR)
        if len(y) > cap:
            cut = (len(y) - cap) / SR
            y = y[:cap].copy(); f = int(0.05 * SR); y[-f:] *= np.linspace(1, 0, f)
    add(voice, y, s0)
    vlog.append(dict(tag=p["tag"], start=s0, length=len(y) / SR, beat=p["notes"][0][0], cut=round(cut, 4)))
    k = 0
    for w in p["caption"].split():
        ns = len(re.split("[-~]", w))
        st = T.t(p["notes"][k][0]); en = T.t(p["notes"][k + ns - 1][0] + p["notes"][k + ns - 1][1])
        words.append(dict(w=w.replace("-", "").replace("~", "-"), t0=st, t1=en, line=i))
        k += ns
for j, s in enumerate(T.SPOKEN):
    path = tts(s["text"], f"out/tts/s{j:02d}.wav", s["speed"])
    x, sr = sf.read(path)
    x = signal.resample_poly(x, 147, 80)
    env = np.abs(x); idx = np.where(env > 0.02 * env.max())[0]; x = x[idx[0]:idx[-1] + int(0.05 * SR)]
    add(voice, x, s["t0"])
    vlog.append(dict(tag="spoken", start=s["t0"], length=len(x) / SR, beat=None, cut=0.0))
    ws = s["caption"].split(); L = len(x) / SR
    wl = np.array([len(w) + 2 for w in ws], float); cs = np.concatenate([[0], np.cumsum(wl)]) / wl.sum() * L
    for wi, w in enumerate(ws):
        words.append(dict(w=w, t0=s["t0"] + cs[wi], t1=s["t0"] + cs[wi + 1], line=100 + j))

def biquad(kind, f0, gain_db=0, q=0.707):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f0 / SR; c, s_ = np.cos(w), np.sin(w); al = s_ / (2 * q)
    if kind == "hp":
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == "lp":
        b = [(1 - c) / 2, 1 - c, (1 - c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == "ls":
        sq = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * c + sq), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sq)]
        a = [(A + 1) + (A - 1) * c + sq, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sq]
    elif kind == "hs":
        sq = 2 * np.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * c + sq), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sq)]
        a = [(A + 1) - (A - 1) * c + sq, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sq]
    elif kind == "bp":
        b = [al, 0, -al]; a = [1 + al, -2 * c, 1 - al]
    return np.array(b) / a[0], np.array(a) / a[0]
def filt(x, *args, **kw):
    b, a = biquad(*args, **kw); return signal.lfilter(b, a, x)
def compress(x, thr_db=-20, ratio=2.5, att=0.005, rel=0.12):
    env = np.abs(x); g_a, g_r = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    e_r = signal.lfilter([1 - g_r], [1, -g_r], env)
    lvl = 20 * np.log10(np.maximum(env, e_r) + 1e-9)
    gdb = -np.maximum(lvl - thr_db, 0) * (1 - 1 / ratio)
    gdb = signal.lfilter([1 - g_a], [1, -g_a], gdb)
    return x * 10 ** (gdb / 20)

# mouth envelope for lip sync (before reverb)
fr_n = int(T.DURATION * T.FPS); hop = SR // T.FPS
rms = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(fr_n)])
rms = rms / (np.percentile(rms[rms > 1e-4], 90) + 1e-9)
rms = np.clip((rms - 0.12) / 0.88, 0, 1)
rms = np.convolve(rms, [0.25, 0.5, 0.25], mode="same")
json.dump([round(float(v), 3) for v in rms], open("out/mouth.json", "w"))

voice = filt(voice, "hp", 75)
voice = filt(voice, "ls", 260, 2.5)
voice = filt(voice, "hs", 7000, -3.5)
voice /= np.max(np.abs(voice)) + 1e-9
voice = compress(voice, -18, 2.5)
ir_n = int(0.9 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / (0.15 * SR))
ir = filt(ir, "lp", 4500); ir = np.concatenate([np.zeros(int(0.015 * SR)), ir]); ir /= np.sqrt(np.sum(ir ** 2))
wet = signal.fftconvolve(voice, ir)[:N]
voice = 0.84 * voice + 0.16 * wet * (np.std(voice) / (np.std(wet) + 1e-9))
voice /= np.max(np.abs(voice)) + 1e-9

# ---------------- instruments ----------------
TR = T.TRANSPOSE
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def marimba(f, dur=0.7, bright=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 5.5) + 0.35 * bright * np.sin(2 * np.pi * f * 3.93 * tt) * np.exp(-tt * 22) \
        + 0.12 * bright * np.sin(2 * np.pi * f * 9.2 * tt) * np.exp(-tt * 45)
    return y * np.minimum(tt / 0.0015, 1)
def musicbox(f, dur=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.6) + 0.3 * np.sin(2 * np.pi * f * 3.0 * tt) * np.exp(-tt * 8) \
        + 0.08 * np.sin(2 * np.pi * f * 5.04 * tt) * np.exp(-tt * 16)
    return y * np.minimum(tt / 0.0008, 1)
def pbass(f, dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 8) + 0.1 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 14)
    return y * np.exp(-tt * 4.0) * np.minimum(tt / 0.004, 1)
def pad(freqs, dur):
    n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for f in freqs:
        for d in (-0.15, 0.15):
            y += np.sin(2 * np.pi * f * (1 + d / 100) * tt + rng.uniform(0, 6))
    env = np.minimum(tt / 0.35, 1) * np.minimum((dur - tt) / 0.4, 1)
    return filt(y, "lp", 1800) * np.clip(env, 0, 1) / len(freqs)
def shaker(g=1.0):
    n = int(0.09 * SR); tt = np.arange(n) / SR
    return g * filt(rng.standard_normal(n), "hp", 6000) * np.exp(-tt / 0.025) * np.minimum(tt / 0.01, 1)
def triangle(g=1.0):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) for f, a, d in ((2850, 1, 2.2), (4310, 0.6, 3), (6020, 0.4, 4)))
    return g * y * np.minimum(tt / 0.001, 1)
def chord_notes(beat):
    r, q = T.chord_at(beat); r = r + TR
    third = 3 if q == "m" else 4
    return r, [r + 12, r + 12 + third, r + 19]

band = np.zeros(N); perc = np.zeros(N); sfx = np.zeros(N)
in_pause = lambda b: any(T.t(b) >= a - 0.01 and T.t(b) < z for a, z in T.QUESTION_PAUSE)
for b in range(0, 93):
    tsec = T.t(b); pos = b % 3
    r, ch = chord_notes(b)
    if in_pause(b):
        continue
    quiet = b < 6
    if pos == 0:
        add(band, pbass(hz(r), 0.9), tsec, 0.55 if not quiet else 0.3)
    else:
        for j, m in enumerate(ch):
            add(band, marimba(hz(m), 0.5), tsec + j * 0.006, 0.14 if not quiet else 0.09)
    if b >= 6:
        add(perc, shaker(), tsec, 0.10 if pos == 0 else 0.06)
        add(perc, shaker(), tsec + T.BEAT / 2, 0.04)
    if pos == 0 and (12 <= b < 24 or b >= 84) and b % 6 == 0:
        add(perc, triangle(), tsec, 0.05)
# guessing pause: soft pad + three rising music-box "thinking" notes
for k, (a, z) in enumerate(T.QUESTION_PAUSE):
    r, ch = chord_notes(T.seg_start(k) + 3)
    add(band, pad([hz(m) for m in ch], z - a + 0.3), a - 0.05, 0.22)
    for j, m in enumerate([72, 74, 76]):
        add(band, musicbox(hz(m + TR + 12), 0.9), a + 0.25 + j * 0.42, 0.10)
# final ring
r, ch = chord_notes(93)
for j, m in enumerate(ch + [ch[0] + 12]): add(band, marimba(hz(m), 2.0), T.t(93) + j * 0.05, 0.16)
add(band, pbass(hz(r), 2.0), T.t(93), 0.5); add(perc, triangle(), T.t(93), 0.08)
# music box doubles the melody an octave up
for p in T.PHRASES:
    for (b, d, m) in p["notes"]:
        add(band, musicbox(hz(m + TR + 12), 0.9), T.t(b), 0.11)

# ---------------- SFX ----------------
def chirp(f0=2600, f1=3800, dur=0.09):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = f0 + (f1 - f0) * np.sin(np.pi * tt / dur); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.sin(np.pi * tt / dur) ** 2
def tweet(sec, g=0.12):
    for j in range(3):
        add(sfx, chirp(2400 + 300 * j, 3600 + 200 * j), sec + j * 0.11, g)
def shimmer(dur=1.4):
    y = np.zeros(int(dur * SR))
    for j, m in enumerate([84, 88, 91, 96, 100]):
        x = musicbox(hz(m + TR), 0.8); i = int(j * 0.12 * SR); y[i:i + len(x)] += x[:len(y) - i] * 0.5
    return y
def noise_sweep(dur, f0, f1, q=0.9):
    n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n); nz = rng.standard_normal(n)
    fc = f0 + (f1 - f0) * tt / dur
    for k0 in range(0, n, 1024):
        sl = slice(k0, min(n, k0 + 1024)); y[sl] = filt(nz[sl], "bp", float(fc[k0]), q=q)
    return y * np.sin(np.pi * tt / dur) ** 1.5
def wind(dur):
    n = int(dur * SR); tt = np.arange(n) / SR; nz = rng.standard_normal(n); y = np.zeros(n)
    fc = 500 + 350 * np.sin(2 * np.pi * tt / 1.7) + 150 * np.sin(2 * np.pi * tt / 0.6)
    for k0 in range(0, n, 1024):
        sl = slice(k0, min(n, k0 + 1024)); y[sl] = filt(nz[sl], "bp", float(fc[k0]), q=2.5)
    return y * np.minimum(tt / 0.6, 1) * np.minimum((dur - tt) / 0.8, 1)
def rain(dur, dens=180):
    n = int(dur * SR); y = filt(rng.standard_normal(n), "lp", 5000) * 0.05
    for _ in range(int(dens * dur)):
        i = rng.integers(0, n - 800); m = 400; tt = np.arange(m) / SR
        y[i:i + m] += np.sin(2 * np.pi * rng.uniform(2500, 5000) * tt) * np.exp(-tt / 0.004) * rng.uniform(0.2, 0.6)
    tt = np.arange(n) / SR
    return y * np.minimum(tt / 0.8, 1) * np.minimum((dur - tt) / 0.8, 1)
def splash():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    return filt(rng.standard_normal(n), "bp", 1800, q=0.6) * np.exp(-tt / 0.08) + 0.4 * np.sin(2 * np.pi * (300 - 400 * tt) * tt) * np.exp(-tt / 0.05)
def pop(f0=400, f1=1500):
    n = int(0.08 * SR); tt = np.arange(n) / SR
    f = f0 + (f1 - f0) * tt / tt[-1]; ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt / 0.03)
def harp_gliss(start_m=60, n=12, step=0.06):
    y = np.zeros(int((n * step + 1.5) * SR)); sc = [0, 2, 4, 7, 9]
    for j in range(n):
        m = start_m + 12 * (j // 5) + sc[j % 5]; x = marimba(hz(m + TR + 12), 1.2, 0.6)
        i = int(j * step * SR); y[i:i + len(x)] += x
    return y

add(sfx, noise_sweep(1.0, 3000, 600, 0.7), 2.0, 0.28)          # slide-in skid
tweet(7.0); tweet(9.6, 0.1)
for k in range(5):
    a = T.t(T.seg_start(k) + 2.4)
    if k == 0: add(sfx, shimmer(), a + 0.6, 0.2)
    if k == 1: add(sfx, noise_sweep(1.6, 400, 900, 1.5), a + 0.2, 0.12)
    if k == 2: add(sfx, wind(5.0), a, 0.22)
    if k == 3: add(sfx, rain(5.6), a + 0.4, 0.22)
    if k == 4: add(sfx, harp_gliss(), a + 0.5, 0.22)
add(sfx, pop(300, 900), T.t(T.HAT_DROP) + 0.25, 0.25)                 # hat lands
add(sfx, pop(250, 1600), T.t(T.UMBRELLA_POP), 0.3)                    # umbrella pops open
for hb in T.HOPS_RAIN:
    add(sfx, splash(), T.t(hb) + 0.08, 0.3)
tweet(T.t(T.seg_start(0) + 9), 0.09); tweet(T.t(T.seg_start(4) + 9), 0.1); tweet(T.t(90), 0.1)

# ---------------- mix ----------------
music = band + perc
venv = signal.lfilter([1 - np.exp(-1 / (0.05 * SR))], [1, -np.exp(-1 / (0.05 * SR))], np.abs(voice))
venv /= np.percentile(venv[venv > 1e-4], 95) + 1e-9
duck = 1 - 0.45 * np.clip(venv, 0, 1)
music_n = music / (np.max(np.abs(music)) + 1e-9)
sfx_n = sfx / (np.max(np.abs(sfx)) + 1e-9)
mix = 0.95 * voice + 0.55 * music_n * duck + 0.32 * sfx_n
mix = mix[:int(T.DURATION * SR)]
fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo) ** 2

def lufs(x):
    sf.write("out/_tmp.wav", x, SR)
    r = subprocess.run(["ffmpeg", "-nostats", "-i", "out/_tmp.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
for _ in range(3):
    L = lufs(mix)
    mix = mix * 10 ** ((-14 - L) / 20)
    mix = 0.95 * np.tanh(mix / 0.95)
print("LUFS", round(lufs(mix), 2), "peak", round(float(np.max(np.abs(mix))), 3))
sf.write("out/audio.wav", mix, SR)
sf.write("out/voice.wav", voice[:len(mix)], SR)
json.dump(words, open("out/word_times.json", "w"), indent=1)
json.dump(vlog, open("out/vocal_log.json", "w"), indent=1)
