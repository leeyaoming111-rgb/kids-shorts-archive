"""Mix for Episode 2: ElevenLabs song (out/song.mp3) + ElevenLabs TTS spoken lines + synthesized gag SFX.
Writes out/audio.wav, out/word_times.json, out/mouth_tumble.json, out/mouth_pip.json, out/vocal_log.json."""
import json, subprocess, re
import numpy as np, soundfile as sf
from scipy import signal
import timeline as T

SR = 44100
N = int(T.DURATION * SR)
rng = np.random.default_rng(44)
def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)
def at(s): return int(round(s * SR))
def add(buf, x, s, g=1.0):
    i = at(s)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += g * x[:n]
def biquad(kind, f0, q=0.707):
    w = 2 * np.pi * f0 / SR; c, s_ = np.cos(w), np.sin(w); al = s_ / (2 * q)
    if kind == "lp": b = [(1 - c) / 2, 1 - c, (1 - c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == "hp": b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a = [1 + al, -2 * c, 1 - al]
    else: b = [al, 0, -al]; a = [1 + al, -2 * c, 1 - al]
    return np.array(b) / a[0], np.array(a) / a[0]
def filt(x, kind, f0, q=0.707): b, a = biquad(kind, f0, q); return signal.lfilter(b, a, x)

song = load("out/song.wav")[:N]
song = np.pad(song, (0, max(0, N - len(song))))
speech = np.zeros(N); sfx = np.zeros(N)
words, vlog = [], []
mouth = {"tumble": np.zeros(int(T.DURATION * T.FPS)), "pip": np.zeros(int(T.DURATION * T.FPS))}

def syll_count(w):
    return max(1, len(re.findall(r"[aeiouy]+", w.lower().replace("e!", "!").rstrip("e"))))
def mouth_word(who, t0, t1, w, amp=1.0):
    n = syll_count(w); f0, f1 = int(t0 * T.FPS), int(t1 * T.FPS) + 1
    for f in range(f0, min(f1, len(mouth[who]))):
        u = (f / T.FPS - t0) / max(t1 - t0, 1e-3)
        mouth[who][f] = max(mouth[who][f], amp * (0.25 + 0.75 * abs(np.sin(np.pi * n * min(max(u, 0), 1)))))

# sung words (forced alignment)
for L in T.LINES:
    for w in L["words"]:
        cap = w["w"]
        if re.sub(r"[^a-z]", "", cap.lower()) == "big": cap = cap.replace("big", "BIG").replace("Big", "BIG")
        words.append(dict(w=cap, t0=w["t0"], t1=w["t1"], line=L["i"], who=L["who"]))
        mouth_word(L["who"], w["t0"], w["t1"], w["w"])
    vlog.append(dict(tag=L["section"], who=L["who"], start=L["t0"], length=L["t1"] - L["t0"], cut=0.0))

# spoken lines (ElevenLabs TTS with character timestamps)
for j, s in enumerate(T.SPOKEN):
    x = load(f"out/el_v2/{s['file']}.wav")
    add(speech, x, s["t0"])
    e = np.convolve(np.abs(x), np.ones(441) / 441, "same"); on = np.where(e > 0.08 * e.max())[0]
    spans = [(s["caption"], on[0] / SR, on[-1] / SR)]          # one-word exclamation: caption spans the voiced part
    caps = s["caption"].split()
    for k, (wtxt, a, b) in enumerate(spans):
        words.append(dict(w=caps[k] if k < len(caps) else wtxt, t0=s["t0"] + a, t1=s["t0"] + b, line=100 + j, who=s["who"]))
        mouth_word(s["who"], s["t0"] + a, s["t0"] + b, wtxt)
    vlog.append(dict(tag="spoken", who=s["who"], start=s["t0"], length=len(x) / SR, cut=0.0))

for who in mouth:
    m = np.convolve(mouth[who], [0.25, 0.5, 0.25], mode="same")
    json.dump([round(float(v), 3) for v in m], open(f"out/mouth_{who}.json", "w"))

# ---------------- gag SFX ----------------
def env(n, a=0.01, r=0.08):
    tt = np.arange(n) / SR; L = n / SR
    return np.clip(tt / a, 0, 1) * np.clip((L - tt) / r, 0, 1)
def slide_whistle(dur, f0, f1):
    n = int(dur * SR); tt = np.arange(n) / SR; f = f0 * (f1 / f0) ** (tt / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.03, 0.08)
def boing(f=220, dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    ff = f * (1 + 0.8 * tt / dur) * (1 + 0.06 * np.sin(2 * np.pi * 16 * tt))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-tt / 0.22)
def thump(g=1.0):
    n = int(0.45 * SR); tt = np.arange(n) / SR; f = 40 + 70 * np.exp(-tt / 0.05)
    return g * (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.16) + 0.4 * filt(rng.standard_normal(n), "lp", 500) * np.exp(-tt / 0.05))
def tap():
    n = int(0.05 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt / 0.008)
def squash():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    return filt(rng.standard_normal(n), "bp", 500, 1.5) * np.exp(-tt / 0.1) + 0.6 * np.sin(2 * np.pi * (180 - 200 * tt) * tt) * np.exp(-tt / 0.1)
def roll(dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    return filt(rng.standard_normal(n), "lp", 300) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * tt)) * env(n, 0.1, 0.3)
def whoosh(dur=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR; y = np.zeros(n); nz = rng.standard_normal(n)
    fc = 600 + 2400 * np.sin(np.pi * tt / dur)
    for k0 in range(0, n, 1024):
        sl = slice(k0, min(n, k0 + 1024)); y[sl] = filt(nz[sl], "bp", float(fc[k0]), 1.2)
    return y * np.sin(np.pi * tt / dur) ** 2
def chirp(f0, f1, dur=0.09):
    n = int(dur * SR); tt = np.arange(n) / SR; f = f0 + (f1 - f0) * np.sin(np.pi * tt / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / dur) ** 2
def tweet(s, g=0.1):
    for j in range(3): add(sfx, chirp(2400 + 300 * j, 3600 + 200 * j), s + j * 0.11, g)

tweet(3.75)
add(sfx, thump(0.5), T.sec("Chorus")[0] + 0.9, 0.35)                       # basket plops on the blanket
add(sfx, roll(1.8), T.ROLL, 0.35); add(sfx, slide_whistle(0.6, 500, 1400), T.ROLL + 0.15, 0.12)
add(sfx, whoosh(0.7), T.WHOOSH - 0.1, 0.35); add(sfx, whoosh(0.9), T.BLOWN, 0.45)
add(sfx, slide_whistle(0.8, 1600, 500), T.BLOWN + 0.2, 0.12); add(sfx, thump(0.4), T.BLOWN + 0.9, 0.3)
add(sfx, thump(0.6), T.sec("Round 3 big")[0] + 0.6, 0.35)                 # sits on the stump
add(sfx, squash(), T.SQUASH, 0.45); add(sfx, boing(180, 0.8), T.SQUASH + 0.35, 0.4)
for s_ in T.STOMPS: add(sfx, thump(1.0), s_, 0.55)
add(sfx, boing(900, 0.25), T.PIP_HOP, 0.15)
add(sfx, tap(), T.TINY_STOMP, 0.3)
add(sfx, boing(140, 1.0), T.BIG_HOP, 0.5); add(sfx, thump(1.2), T.BIG_HOP + 0.95, 0.55)
tweet(T.sec("Finale B")[0] - 0.3, 0.08)

# ---------------- mix ----------------
senv = signal.lfilter([1 - np.exp(-1 / (0.06 * SR))], [1, -np.exp(-1 / (0.06 * SR))], np.abs(speech))
senv /= np.percentile(senv[senv > 1e-4], 95) + 1e-9
duck = 1 - 0.4 * np.clip(senv, 0, 1)                      # song dips under the spoken lines
song_n = song / (np.max(np.abs(song)) + 1e-9)
speech_n = speech / (np.max(np.abs(speech)) + 1e-9)
sfx_n = sfx / (np.max(np.abs(sfx)) + 1e-9)
mix = 0.9 * song_n * duck + 0.75 * speech_n + 0.3 * sfx_n
fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo) ** 2
def lufs(x):
    sf.write("out/_tmp.wav", x, SR)
    r = subprocess.run(["ffmpeg", "-nostats", "-i", "out/_tmp.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
for _ in range(3):
    mix = mix * 10 ** ((-14 - lufs(mix)) / 20); mix = 0.95 * np.tanh(mix / 0.95)
print("LUFS", round(lufs(mix), 2), "peak", round(float(np.max(np.abs(mix))), 3))
sf.write("out/audio.wav", mix, SR)
json.dump(sorted(words, key=lambda w: w["t0"]), open("out/word_times.json", "w"), indent=1)
json.dump(vlog, open("out/vocal_log.json", "w"), indent=1)
srt = sorted(vlog, key=lambda e: e["start"])
print("min gap between voice lines", round(min(b["start"] - (a["start"] + a["length"]) for a, b in zip(srt, srt[1:])), 3))
