"""usage: python3 el_voice.py <fable_dir>  -> audio/<fable-NN>/sNN_*.mp3 + spoken.json, from that fable's timeline.SPOKEN

Spoken gag lines: eleven_v3 TTS in the fixed cast voices (tools/cast_voices.json), the line's audio tags, stability 0.0.
Two takes per voice (seeds 11 and 22); the take with the widest pitch range (5th to 95th percentile, semitones) wins.
who="both" makes the Tumble and Pip lines separately and overlays them. The key comes from ELEVENLABS_API_KEY only."""
import os, re, sys, json, subprocess, importlib.util
import numpy as np, requests, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import el_batch as E

SR = 44100
VOICES = json.load(open(os.path.join(HERE, "..", "..", "tools", "cast_voices.json")))
SEEDS = (11, 22)

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

def tts(voice_id, text, seed, out):
    r = requests.post(f"{E.API}/text-to-speech/{voice_id}?output_format=mp3_44100_128", headers=E.key(), timeout=120,
                      json=dict(text=text, model_id="eleven_v3", seed=seed, voice_settings=dict(stability=0.0)))
    if r.status_code != 200: sys.exit(f"tts failed {r.status_code}: {r.text[:300]}")
    open(out, "wb").write(r.content)

def pitch_range(path, fmin=70, fmax=1100):
    """5-95 percentile spread of an autocorrelation f0 track, in semitones"""
    x = E.load(path).mean(1); win, hop = 2048, 441; f0 = []
    for i in range(0, len(x) - win, hop):
        fr = x[i:i + win] * np.hanning(win)
        if np.sqrt((fr ** 2).mean()) < 0.01: continue
        ac = np.fft.irfft(np.abs(np.fft.rfft(fr, 2 * win)) ** 2)[:win]; ac /= ac[0] + 1e-12
        lo, hi = int(SR / fmax), int(SR / fmin); k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.5: f0.append(SR / k)
    if len(f0) < 5: return 0.0
    st = 12 * np.log2(np.array(f0) / 440.0); return float(np.percentile(st, 95) - np.percentile(st, 5))

def voice(fable_dir):
    tl, dest = timeline(fable_dir), audio_dir(fable_dir)
    rep = []
    for s in tl.SPOKEN:
        text = f"{s['tags']} {s['caption']}"
        whos = ["tumble", "pip"] if s["who"] == "both" else [s["who"]]
        parts, info = [], []
        for w in whos:
            takes = []
            for k, seed in enumerate(SEEDS):
                p = os.path.join(dest, f"{s['file']}_{w}_take{k + 1}.mp3"); tts(VOICES[w]["voice_id"], text, seed, p)
                takes.append(dict(path=p, seed=seed, range_st=round(pitch_range(p), 2)))
            best = max(takes, key=lambda t: t["range_st"])
            parts.append(E.load(best["path"]))
            info.append(dict(voice=w, voice_id=VOICES[w]["voice_id"], seed=best["seed"],
                             takes=[dict(seed=t["seed"], range_st=t["range_st"]) for t in takes]))
            for t in takes: os.remove(t["path"])
        L = max(len(p) for p in parts); line = np.zeros((L, 2), np.float32)
        for p in parts: line[:len(p)] += p / len(parts) ** 0.5           # equal-power sum for the overlaid duet
        out = os.path.join(dest, f"{s['file']}.mp3"); wav = out[:-4] + ".wav"
        sf.write(wav, line, SR); subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "128k", out], check=True)
        os.remove(wav)
        rep.append(dict(file=f"{s['file']}.mp3", who=s["who"], t0=round(s["t0"], 3), caption=s["caption"], tags=s["tags"],
                        dur=round(L / SR, 2), voices=info))
        print(s["file"], [(v["voice"], v["takes"]) for v in info])
    json.dump(dict(model="eleven_v3", stability=0.0, takes=len(SEEDS), pick="widest 5-95% pitch range (semitones)", spoken=rep),
              open(os.path.join(dest, "spoken.json"), "w"), indent=1)
    print("wrote", dest)

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    voice(sys.argv[1])
