"""Mix v2 (polish pass 2026-10-20): python3 el_mix2.py <fable_dir> [--nostt]

Song (code/out/song.wav from el_song2.py pick) + spoken lines (el_voice2.py) at timeline.SPOKEN t0, with:
- the song ducked 5 dB under each spoken line (60 ms attack, 250 ms release) so gags never fight the band,
- no clip truncated: a line that would run past the end is reported as an error (move its t0 in timeline.py),
- a check that no spoken line lands on a sung word (reported, so the timeline can move it),
- 15 ms fade-in, 0.5 s fade-out matching the picture fade, -14 LUFS, soft peak limit,
- out/spoken_env.json: each clip's 30 fps loudness envelope, so the mouths follow the real speech.
Writes code/out/audio.wav, audio/<fable-NN>/mix.mp3 and report.json (mix section)."""
import os, sys, json, difflib, subprocess
import numpy as np, soundfile as sf, pyloudnorm as pyln, requests
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from el_voice2 import load, timeline, audio_dir, key, API
from el_song2 import words_norm
SR, FPS = 44100, 30

def envelope(x):
    m = np.abs(x).mean(1) if x.ndim > 1 else np.abs(x); hop = SR // FPS; n = len(m) // hop + 1
    e = np.array([np.sqrt(np.mean(m[k * hop:(k + 1) * hop] ** 2)) if k * hop < len(m) else 0 for k in range(n)])
    return (e / (e.max() + 1e-9)).round(3).tolist()

def mix(fable_dir, stt=True):
    out, dest = os.path.join(fable_dir, "code", "out"), audio_dir(fable_dir)
    tl = timeline(fable_dir); dur = float(tl.DURATION); n = int(round(dur * SR))
    song = sf.read(os.path.join(out, "song.wav"), always_2d=True)[0].astype(np.float32)
    sc = json.load(open(os.path.join(out, "song_check.json")))
    m = np.zeros((n, 2), np.float32); m[:min(n, len(song))] = song[:n]
    duck = np.ones(n, np.float32); voice = np.zeros((n, 2), np.float32)
    env, placed, problems = {}, [], []
    sung = [(w["t0"], w["t1"], L["line"]) for L in sc["lines"] for w in L["words"]]
    for s in tl.SPOKEN:
        x = load(os.path.join(dest, f"{s['file']}.mp3")); i = int(s["t0"] * SR); d = len(x) / SR
        if s["t0"] + d > dur - 0.25: problems.append(f"{s['file']} ends at {s['t0'] + d:.2f}, past the end fade ({dur - 0.25:.2f}): move t0")
        for a, b, line in sung:
            if a < s["t0"] + d - 0.15 and b > s["t0"] + 0.1:
                problems.append(f"{s['file']} ({s['caption']}) {s['t0']:.2f}-{s['t0'] + d:.2f} overlaps sung '{line}' at {a:.2f}"); break
        seg = x[:max(0, n - i)]; voice[i:i + len(seg)] += seg
        a0, a1 = max(0, i - int(0.06 * SR)), min(n, i + len(seg) + int(0.25 * SR)); duck[a0:a1] = 10 ** (-5 / 20)
        env[s["file"]] = envelope(x); placed.append((s["file"], round(s["t0"], 3), round(d, 2)))
    # smooth the duck gain (60 ms attack / 250 ms release equivalent)
    k = int(0.08 * SR); g = np.convolve(duck, np.ones(k) / k, mode="same").astype(np.float32)
    m = m * g[:, None] + voice
    m[:int(0.015 * SR)] *= np.linspace(0, 1, int(0.015 * SR))[:, None]
    f = int(0.5 * SR); m[-f:] *= np.linspace(1, 0, f)[:, None] ** 1.5
    meter = pyln.Meter(SR); m = pyln.normalize.loudness(m, meter.integrated_loudness(m), -14.0)
    m = np.where(np.abs(m) > 0.9, np.sign(m) * (0.9 + 0.09 * np.tanh((np.abs(m) - 0.9) / 0.09)), m).astype(np.float32)
    sf.write(os.path.join(out, "audio.wav"), m, SR)
    json.dump(env, open(os.path.join(out, "spoken_env.json"), "w"))
    mp3 = os.path.join(dest, "mix.mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(out, "audio.wav"), "-b:a", "192k", mp3], check=True)
    for nm in ("song.mp3",):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(out, "song.wav"), "-b:a", "192k", os.path.join(dest, nm)], check=True)
    import shutil; shutil.copy(os.path.join(out, "song_check.json"), os.path.join(dest, "song_check.json"))
    shutil.copy(os.path.join(out, "spoken_env.json"), os.path.join(dest, "spoken_env.json"))
    lufs = meter.integrated_loudness(m); recall, text = None, None
    if stt:
        import time
        for attempt in range(6):
            rr = requests.post(f"{API}/speech-to-text", headers=key(), data={"model_id": "scribe_v1"}, files={"file": open(mp3, "rb")}, timeout=300)
            if rr.status_code != 429: break
            time.sleep(6 + 6 * attempt)
        r = rr.json() if rr.status_code == 200 else {}
        text = r.get("text", ""); exp = [w for L in sc["lines"] for w in words_norm(L["line"])]; heard = words_norm(text)
        recall = sum(b.size for b in difflib.SequenceMatcher(a=exp, b=heard, autojunk=False).get_matching_blocks()) / max(1, len(exp))
    rp = os.path.join(dest, "report.json"); rep = json.load(open(rp)) if os.path.exists(rp) else {}
    rep["v2"] = dict(song_take=sc.get("take"), song_recall=sc.get("recall"), singer_pitch_ok=sc.get("f0_hits"),
                     singer_voice_sim=sc.get("voice_sim"), duration=dur, spoken=placed, problems=problems,
                     mix=dict(lufs=round(lufs, 2), peak=round(float(np.abs(m).max()), 3), lyric_recall=recall, stt=text))
    json.dump(rep, open(rp, "w"), indent=1)
    print(f"mix {dur:.2f}s  LUFS {lufs:.2f}  recall {recall}  problems: {len(problems)}")
    for p in problems: print("  PROBLEM", p)
    return problems

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    mix(sys.argv[1], "--nostt" not in sys.argv)
