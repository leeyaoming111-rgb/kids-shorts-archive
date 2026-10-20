"""Spoken lines v2 (polish pass 2026-10-20): the cast voices stay on-model from line to line and episode to episode.

v1 used eleven_v3 at stability 0.0 and kept the take with the WIDEST pitch range, which picked the least stable takes
(Tumble's lines spanned up to 26 semitones). v2 uses stability 0.5 ("natural", still expressive with audio tags),
makes 3 takes, and keeps the take whose voice embedding sits closest to that character's anchor clip (one fixed
sentence per voice at stability 1.0, made once and stored in audio/series/anchor_<who>.mp3), with a small bonus for
pitch movement so gags stay lively.

  python3 el_voice2.py <fable_dir>                  every line in timeline.SPOKEN -> audio/<fable-NN>/<file>.mp3 + spoken.json
  python3 el_voice2.py say <who> "<tags> text" out.mp3   one line (used by the long-form dialogue scenes)
Key: ELEVENLABS_API_KEY only."""
import os, re, sys, json, subprocess, importlib.util
import numpy as np, requests, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
API = "https://api.elevenlabs.io/v1"
SR = 44100
VOICES = json.load(open(os.path.join(HERE, "..", "..", "tools", "cast_voices.json")))
SER = os.path.join(HERE, "audio", "series")
SEEDS = (11, 22, 33)
STABILITY = 0.5
ANCHOR_TEXT = {"tumble": "Hello, friends! I'm Tumble, and this is my best friend Pip. Shall we play?",
               "pip": "Hi hi! I'm Pip! I'm small, but I'm super quick. Let's go, Tumble!",
               "bo": "Hello there, little friends. I'm Bo. I like to go slow and steady."}

def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k: sys.exit("ELEVENLABS_API_KEY is not set: stop and tell the owner.")
    return {"xi-api-key": k}

def load(path, sr=SR, ch=2):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    return x.reshape(-1, ch) if ch > 1 else x

def tts(voice_id, text, seed, out, stability=STABILITY):
    for attempt in range(4):
        r = requests.post(f"{API}/text-to-speech/{voice_id}?output_format=mp3_44100_128", headers=key(), timeout=180,
                          json=dict(text=text, model_id="eleven_v3", seed=seed, voice_settings=dict(stability=stability)))
        if r.status_code == 200: open(out, "wb").write(r.content); return
        if r.status_code == 429: import time; time.sleep(5 + 5 * attempt); continue
        sys.exit(f"tts failed {r.status_code}: {r.text[:300]}")
    sys.exit("tts: rate limited 4 times")

_enc = None
def embed(path):
    global _enc
    from resemblyzer import VoiceEncoder, preprocess_wav
    if _enc is None: _enc = VoiceEncoder("cpu", verbose=False)
    e = _enc.embed_utterance(preprocess_wav(load(path, 16000, 1), source_sr=16000)); return e / np.linalg.norm(e)

def pitch_range(path):
    import librosa
    y = load(path, 16000, 1)
    f, v, _ = librosa.pyin(y, fmin=80, fmax=1000, sr=16000, frame_length=1024)
    f = f[v] if v is not None else np.array([])
    if len(f) < 5: return 0.0
    st = 12 * np.log2(f / 440.0); return float(np.percentile(st, 95) - np.percentile(st, 5))

def anchor(who):
    p = os.path.join(SER, f"anchor_{who}.mp3")
    if not os.path.exists(p): tts(VOICES[who]["voice_id"], ANCHOR_TEXT[who], 7, p, stability=1.0)
    return embed(p)

def best_take(who, text, out):
    """3 takes; keep the one closest to the character's anchor voice (plus a little credit for pitch movement)"""
    A = anchor(who); takes = []
    for k, seed in enumerate(SEEDS):
        p = out.replace(".mp3", f"_take{k + 1}.mp3"); tts(VOICES[who]["voice_id"], text, seed, p)
        sim = float(embed(p) @ A) if load(p, 16000, 1).size > 8000 else 0.0
        rng = pitch_range(p); takes.append(dict(path=p, seed=seed, sim=round(sim, 3), range_st=round(rng, 2),
                                                score=sim + 0.006 * min(rng, 14)))
    best = max(takes, key=lambda t: t["score"])
    os.replace(best["path"], out)
    for t in takes:
        if os.path.exists(t["path"]): os.remove(t["path"])
    return best, takes

def trim(x, thr_db=-45):
    """drop leading and trailing near-silence (keeps 40 ms), so a clip's t0 is where the voice starts"""
    e = np.abs(x).max(1); thr = 10 ** (thr_db / 20) * max(e.max(), 1e-6)
    idx = np.where(e > thr)[0]
    if not len(idx): return x
    a, b = max(0, idx[0] - int(0.04 * SR)), min(len(x), idx[-1] + int(0.08 * SR))
    return x[a:b]

def say(who, text, out):
    """one line -> out (trimmed); returns its info"""
    whos = ["tumble", "pip"] if who == "both" else [who]
    parts, info = [], []
    for w in whos:
        tmp = out.replace(".mp3", f"_{w}.mp3"); best, takes = best_take(w, text, tmp)
        parts.append(trim(load(tmp))); os.remove(tmp)
        info.append(dict(voice=w, voice_id=VOICES[w]["voice_id"], seed=best["seed"], sim=best["sim"],
                         takes=[{k: t[k] for k in ("seed", "sim", "range_st")} for t in takes]))
    L = max(len(p) for p in parts); line = np.zeros((L, 2), np.float32)
    for p in parts: line[:len(p)] += p / len(parts) ** 0.5
    wav = out[:-4] + ".wav"; sf.write(wav, line, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "160k", out], check=True); os.remove(wav)
    return dict(dur=round(L / SR, 2), voices=info)

def timeline(fable_dir):
    spec = importlib.util.spec_from_file_location("tl", os.path.join(fable_dir, "code", "timeline.py"))
    cwd = os.getcwd(); os.chdir(os.path.join(fable_dir, "code"))
    try:
        tl = importlib.util.module_from_spec(spec); spec.loader.exec_module(tl)
    finally:
        os.chdir(cwd)
    return tl

def audio_dir(fable_dir):
    d = os.path.join(HERE, "audio", re.match(r"fable-\d+", os.path.basename(os.path.normpath(fable_dir))).group(0))
    os.makedirs(d, exist_ok=True); return d

def voice(fable_dir):
    tl, dest = timeline(fable_dir), audio_dir(fable_dir); rep = []
    for s in tl.SPOKEN:
        out = os.path.join(dest, f"{s['file']}.mp3")
        r = say(s["who"], f"{s['tags']} {s['caption']}", out)
        rep.append(dict(file=f"{s['file']}.mp3", who=s["who"], t0=round(s["t0"], 3), caption=s["caption"], tags=s["tags"], **r))
        print(s["file"], r["dur"], [(v["voice"], v["sim"]) for v in r["voices"]])
    json.dump(dict(model="eleven_v3", stability=STABILITY, takes=len(SEEDS), pick="closest to the character's anchor voice",
                   spoken=rep), open(os.path.join(dest, "spoken.json"), "w"), indent=1)

if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "say": print(say(sys.argv[2], sys.argv[3], sys.argv[4]))
    elif len(sys.argv) == 2: voice(sys.argv[1])
    else: sys.exit(__doc__)
