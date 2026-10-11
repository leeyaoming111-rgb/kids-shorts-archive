import json, os, subprocess, re
import numpy as np, soundfile as sf
from scipy import signal
from kokoro_onnx import Kokoro
import timeline as T
from sing import sing_phrase, midi_hz, hnr

SR = 44100
N = int(T.DURATION * SR) + SR
rng = np.random.default_rng(7)
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
vlog, words = [], []
raw_hnr = []
items = []
for i, p in enumerate(T.PHRASES):
    path = tts(p["text"], f"out/tts/p{i:02d}.wav")
    b0 = p["notes"][0][0]
    on = [(n[0] - b0) * T.BEAT for n in p["notes"]]
    du = [n[1] * T.BEAT for n in p["notes"]]
    y, lead = sing_phrase(path, on, du, [n[2] for n in p["notes"]])
    items.append([T.t(b0) - lead, y, p, i])
for idx, (s0, y, p, i) in enumerate(items):
    if idx + 1 < len(items):
        nb = T.t(items[idx + 1][2]["notes"][0][0])
        lim = min(nb - 0.13, items[idx + 1][0] - 0.04)
        cap = int((lim - s0) * SR)
        if len(y) > cap:
            y = y[:cap].copy(); f = int(0.05 * SR); y[-f:] *= np.linspace(1, 0, f)
    add(voice, y, s0)
    vlog.append(dict(tag=p["tag"], start=s0, length=len(y) / SR, beat=p["notes"][0][0]))
    k = 0
    for w in p["caption"].split():
        ns = len(w.split("-"))
        st = T.t(p["notes"][k][0]); en = T.t(p["notes"][k + ns - 1][0] + p["notes"][k + ns - 1][1])
        words.append(dict(w=w.replace("-", ""), t0=st, t1=en, line=i))
        k += ns
for j, s in enumerate(T.SPOKEN):
    path = tts(s["text"], f"out/tts/s{j:02d}.wav", s["speed"])
    x, sr = sf.read(path)
    x = signal.resample_poly(x, 147, 80)
    env = np.abs(x); idx = np.where(env > 0.02 * env.max())[0]; x = x[idx[0]:idx[-1] + int(0.05 * SR)]
    add(voice, x, s["t0"])
    vlog.append(dict(tag="spoken", start=s["t0"], length=len(x) / SR, beat=None))
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
    env = np.abs(x); out = np.zeros_like(env); g_a, g_r = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    e = 0.0
    # vectorised-ish envelope via lfilter on rectified signal (release dominated)
    e_r = signal.lfilter([1 - g_r], [1, -g_r], env)
    e_a = np.maximum(env, e_r)
    lvl = 20 * np.log10(e_a + 1e-9)
    over = np.maximum(lvl - thr_db, 0)
    gdb = -over * (1 - 1 / ratio)
    gdb = signal.lfilter([1 - g_a], [1, -g_a], gdb)
    return x * 10 ** (gdb / 20)

voice = filt(voice, "hp", 80)
voice = filt(voice, "ls", 240, 2.0)
voice = filt(voice, "hs", 7000, -3.0)
voice = filt(voice, "bp", 3000, 0) * 0.25 + voice          # presence lift for clarity
voice /= np.max(np.abs(voice)) + 1e-9
voice = compress(voice, -18, 2.5)
ir_n = int(0.9 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / (0.16 * SR))
ir = filt(ir, "lp", 4500); ir = np.concatenate([np.zeros(int(0.015 * SR)), ir]); ir /= np.sqrt(np.sum(ir ** 2))
wet = signal.fftconvolve(voice, ir)[:N]
voice = 0.86 * voice + 0.14 * wet * (np.std(voice) / (np.std(wet) + 1e-9))
voice /= np.max(np.abs(voice)) + 1e-9

# ---------------- band ----------------
band = np.zeros(N); drums = np.zeros(N); sfx = np.zeros(N)
def env_ad(n, a=0.003, d=0.3):
    tt = np.arange(n) / SR
    return np.minimum(tt / a, 1) * np.exp(-tt / d)
def pluck(f, dur=0.5, bright=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n)
    for h in range(1, 9):
        if f * h > 9000: break
        y += (0.9 ** h) / h * bright ** (h - 1) * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (3 + 2.2 * h))
    return y * np.minimum(tt / 0.002, 1)
def glock(f, dur=0.9):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3) + 0.25 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 9) \
        + 0.12 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 18)
    return y * np.minimum(tt / 0.001, 1)
def kick(g=1.0):
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 45 + 95 * np.exp(-tt / 0.035); ph = 2 * np.pi * np.cumsum(f) / SR
    return g * (np.sin(ph) * np.exp(-tt / 0.16) + 0.25 * filt(rng.standard_normal(n), "lp", 2500) * np.exp(-tt / 0.006))
def snare(g=1.0):
    n = int(0.25 * SR); tt = np.arange(n) / SR
    nz = filt(rng.standard_normal(n), "bp", 2200, q=0.6) * np.exp(-tt / 0.07)
    tone = np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / 0.05)
    clap = sum(filt(rng.standard_normal(n), "bp", 1300, q=1.0) * np.exp(-np.maximum(tt - d, 0) / 0.03) * (tt >= d) for d in (0, 0.011, 0.022))
    return g * (0.9 * nz + 0.5 * tone + 0.35 * clap)
def hat(g=1.0, open_=False):
    n = int((0.18 if open_ else 0.05) * SR); tt = np.arange(n) / SR
    return g * filt(rng.standard_normal(n), "hp", 7500) * np.exp(-tt / (0.06 if open_ else 0.012))
def tom(f, g=1.0):
    n = int(0.3 * SR); tt = np.arange(n) / SR
    ff = f * (1 + 0.5 * np.exp(-tt / 0.03)); ph = 2 * np.pi * np.cumsum(ff) / SR
    return g * np.sin(ph) * np.exp(-tt / 0.15)
def crash(g=1.0):
    n = int(1.8 * SR); tt = np.arange(n) / SR
    return g * filt(rng.standard_normal(n), "hp", 4000) * np.exp(-tt / 0.5) * np.minimum(tt / 0.002, 1)

TR = T.TRANSPOSE
def chord_notes(beat):
    r, q = T.chord_at(beat); r = r + TR
    third = 3 if q == "m" else 4
    return r, [r + 12, r + 12 + third, r + 19, r + 24]
def hz(m): return 440 * 2 ** ((m - 69) / 12)

def section(beat):
    if beat < 8: return "intro"
    if 68 <= beat < 74: return "countdown"
    if beat >= 80: return "outro"
    return "full"

for e in np.arange(0, 80, 0.5):            # eighth-note grid
    sec = section(e); tsec = T.t(e)
    r, ch = chord_notes(e)
    on_beat = abs(e - round(e)) < 1e-6
    bpos = e % 4
    # ukulele strum
    if sec != "countdown" or e in (68, 69, 70, 71, 72, 73):
        g = 0.20 if on_beat else 0.09
        if sec == "countdown": g = 0.12
        for j, m in enumerate(ch if on_beat else ch[1:]):
            add(band, pluck(hz(m), 0.6), tsec + j * 0.009, g)
    # bass: root on beat, octave bounce on the offbeat
    if sec in ("full",) or (sec == "intro" and e >= 4):
        if on_beat:
            add(band, pluck(hz(r), 0.45, 0.5) * 1.0, tsec, 0.55)
        else:
            add(band, pluck(hz(r + 12), 0.25, 0.5), tsec, 0.22)
    # drums
    if sec == "full":
        if bpos in (0, 1.5, 2): add(drums, kick(), tsec, 0.9)
        if bpos in (1, 3): add(drums, snare(), tsec, 0.42)
        add(drums, hat(open_=(not on_beat and bpos == 3.5)), tsec, 0.16 if not on_beat else 0.10)
    elif sec == "intro":
        if e < 6:
            add(drums, hat(), tsec, 0.10)
            if bpos == 0: add(drums, kick(), tsec, 0.6)
    elif sec == "countdown":
        if on_beat and e <= 72: add(drums, kick(), tsec, 1.0)
for b, f in zip(np.arange(6, 8, 0.25), [220, 220, 196, 196, 165, 165, 147, 130]):     # intro fill
    add(drums, tom(f), T.t(b), 0.45)
for b, f in zip(np.arange(73, 74, 0.25), [196, 165, 147, 130]):                       # pre-hooray fill
    add(drums, tom(f), T.t(b), 0.45)
for b in (8, 56, 74):
    add(drums, crash(), T.t(b), 0.18)
# final chord ring
r, ch = chord_notes(80)
for j, m in enumerate(ch): add(band, pluck(hz(m), 2.5), T.t(80) + j * 0.03, 0.2)
add(band, pluck(hz(r), 2.0, 0.5), T.t(80), 0.5)
add(drums, kick(), T.t(80), 0.8); add(drums, crash(), T.t(80), 0.16)
for p in T.PHRASES:                                # glockenspiel doubles the melody, one octave up
    for (b, d, m) in p["notes"]:
        add(band, glock(hz(m + TR + 12), 0.8), T.t(b), 0.13)

# ---------------- SFX ----------------
def stomp(g):
    """soft snow footstep: muffled thump plus a short band-passed crunch"""
    n = int(0.3 * SR); tt = np.arange(n) / SR
    f = 70 + 60 * np.exp(-tt / 0.03); ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-tt / 0.07)
    grains = rng.standard_normal(n) * (rng.random(n) < 0.25)
    crunch = filt(filt(grains, "bp", 2600, q=0.8), "lp", 6000) * np.exp(-tt / 0.06) * np.minimum(tt / 0.004, 1)
    return g * (0.6 * body + 1.1 * crunch)
def pop(f0=500, f1=1400):
    n = int(0.08 * SR); tt = np.arange(n) / SR
    f = f0 + (f1 - f0) * (tt / tt[-1]); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt / 0.03)
def boing(f=300):
    n = int(0.35 * SR); tt = np.arange(n) / SR
    ff = f * (1 + 0.6 * tt / 0.35) * (1 + 0.05 * np.sin(2 * np.pi * 18 * tt)); ph = 2 * np.pi * np.cumsum(ff) / SR
    return np.sin(ph) * np.exp(-tt / 0.15)
for (b, s, who) in T.STOMPS:
    add(sfx, stomp(s), T.t(b), 0.7)
for (b, d, m, fin) in T.POPS:
    add(sfx, pop(450 + 60 * (m + 1), 1200 + 120 * (m + 1)), T.t(b), 0.35)
    if True:
        for j, mm in enumerate([72, 76, 79, 84]):
            add(sfx, glock(hz(mm + TR + 12), 0.5), T.t(b) + 0.04 + j * 0.045, 0.06)
for b in (68, 69, 70, 71, 72):
    add(sfx, boing(260 + 30 * (72 - b)), T.t(b) + 0.02, 0.18)
for j in range(14):                              # hooray confetti sparkles
    add(sfx, glock(hz(rng.choice([84, 86, 88, 91, 93, 96]) + TR), 0.4), T.t(74) + j * 0.07, 0.05)
add(sfx, boing(240), T.t(74), 0.2)

def whoosh(dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = np.zeros(n); fc = 900 + 2200 * np.sin(np.pi * tt / dur)
    nz = rng.standard_normal(n)
    for k0 in range(0, n, 1024):
        seg = slice(k0, min(n, k0 + 1024)); y[seg] = filt(nz[seg], "bp", float(fc[k0]), q=1.2)
    return y * np.sin(np.pi * tt / dur) ** 2
for k in range(1, 6):
    add(sfx, whoosh(0.5), T.t(T.arrival_start(k) - 0.6), 0.25)

# ---------------- mix ----------------
music = band + drums * 1.0
venv = np.abs(signal.hilbert(voice)) if False else signal.lfilter([1 - np.exp(-1 / (0.05 * SR))], [1, -np.exp(-1 / (0.05 * SR))], np.abs(voice))
venv /= np.percentile(venv[venv > 1e-4], 95) + 1e-9
duck = 1 - 0.45 * np.clip(venv, 0, 1)
music_n = music / (np.max(np.abs(music)) + 1e-9)
sfx_n = sfx / (np.max(np.abs(sfx)) + 1e-9)
mix = 0.95 * voice + 0.55 * music_n * duck + 0.38 * sfx_n
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
