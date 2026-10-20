"""Episode v2 assembly.

  python3 assemble.py audio      -> out/episode_audio.m4a + out/manifest.json (cloud: voices, beds, fable mixes)
  python3 assemble.py macjob     -> out/macjob/ (render.py for the Mac queue: concatenates the rendered segments with
                                    a soft dip to cream between them and muxes the master audio)
Segment videos are rendered on the Mac: scenes as ep2_<scene>.mp4, fables as fable-NN_wide.mp4 (no audio needed)."""
import os, sys, json, subprocess
import numpy as np, soundfile as sf, pyloudnorm as pyln
HERE = os.path.dirname(os.path.abspath(__file__)); BATCH = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import script as S
SR, FPS, DIP = 44100, 30, 0.3
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)

def load(p, ch=2):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", p, "-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()
def fable_dir(n): return next(os.path.join(BATCH, d) for d in sorted(os.listdir(BATCH)) if d.startswith(f"fable-{n:02d}-"))
def fable_len(n):
    tl = os.path.join(fable_dir(n), "code", "out", "song_check.json")
    secs = json.load(open(tl))["sections"]; return secs[-1][2]
def seg_frames(it):
    d = fable_len(it) if isinstance(it, int) else json.load(open(os.path.join(HERE, "audio", f"{it}.json")))["duration"]
    return int(d * FPS)
def norm(x, lufs):
    m = pyln.Meter(SR); l = m.integrated_loudness(x)
    return x if not np.isfinite(l) else pyln.normalize.loudness(x, l, lufs).astype(np.float32)

def scene_audio(name, dusk):
    C = json.load(open(os.path.join(HERE, "audio", f"{name}.json")))
    n = int(C["duration"] * FPS) * SR // FPS
    d = sf.read(os.path.join(HERE, "audio", f"{name}_dialogue.wav"), always_2d=True)[0].astype(np.float32)
    d = np.pad(d, ((0, max(0, n - len(d))), (0, 0)))[:n]
    songs = [(a["t0"], a["t1"]) for a in C["acts"] if a["name"] in ("dance", "recap_song")]
    d = norm(d, -15.0 if not songs else -14.5)
    bed = load(os.path.join(HERE, "songs", f"bed_{'night' if dusk > 0.55 else 'day'}.mp3"))
    bed = norm(bed, -31.0)
    off = (abs(hash(name)) % 40) * SR                                  # a different place in the bed for each scene
    reps = np.concatenate([bed] * 6)[off:off + n]
    g = np.ones(n, np.float32)
    env = np.abs(d).mean(1); k = int(0.25 * SR); env = np.convolve(env, np.ones(k) / k, mode="same")
    g *= np.where(env > 0.01, 10 ** (-5 / 20), 1.0).astype(np.float32)   # the bed dips under speech
    for a, b in songs: g[int(a * SR):int(b * SR)] = 0.0                  # no bed under the songs
    g = np.convolve(g, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode="same").astype(np.float32)
    return d + reps * g[:, None]

def audio():
    import importlib.util
    spec = importlib.util.spec_from_file_location("tl_any", os.path.join(HERE, "code", "timeline.py"))
    total = sum(seg_frames(it) for it in S.ORDER) / FPS
    parts, t, man = [], 0.0, []
    for it in S.ORDER:
        fr = seg_frames(it); n = fr * SR // FPS
        if isinstance(it, int):
            x = sf.read(os.path.join(fable_dir(it), "code", "out", "audio.wav"), always_2d=True)[0].astype(np.float32)
            x = np.pad(x, ((0, max(0, n - len(x))), (0, 0)))[:n]; vid = f"fable-{it:02d}_wide.mp4"
        else:
            u = t / total; dusk = 0.33 * u / 0.5 if u < 0.5 else 0.33 + 0.27 * (u - 0.5) / 0.3 if u < 0.8 else 0.6 + (u - 0.8) * 2
            x = scene_audio(it, dusk); vid = f"ep2_{it}.mp4"
        f = int(DIP * SR); x[:f] *= np.linspace(0, 1, f)[:, None]; x[-f:] *= np.linspace(1, 0, f)[:, None]
        parts.append(x); man.append(dict(item=str(it), video=vid, frames=fr, start=round(t, 3))); t += fr / FPS
    a = np.concatenate(parts)
    a = norm(a, -14.0); a = np.clip(a, -0.98, 0.98)
    wav = os.path.join(OUT, "episode_audio.wav"); sf.write(wav, a, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "aac", "-b:a", "192k", os.path.join(OUT, "episode_audio.m4a")], check=True)
    json.dump(dict(fps=FPS, dip=DIP, duration=round(t, 3), segments=man), open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print(f"episode {t / 60:.1f} min, {len(man)} segments")

MAC = r'''# Mac queue job: join the episode segments (soft dip to cream between them) and mux the master audio.
import json, os, subprocess, sys
M = json.load(open("manifest.json")); V = os.path.expanduser("~/Movies/kids-shorts/videos/episode2")
ins, fl = [], []
for i, s in enumerate(M["segments"]):
    p = os.path.join(V, s["video"]); ins += ["-i", p]; d = s["frames"] / M["fps"]
    fl.append(f"[{i}:v]fps={M['fps']},scale=1920:1080,setsar=1,format=yuv420p,trim=end_frame={s['frames']},setpts=PTS-STARTPTS,"
              f"fade=t=in:st=0:d={M['dip']}:color=0xFFF8EC,fade=t=out:st={d - M['dip']:.3f}:d={M['dip']}:color=0xFFF8EC[v{i}]")
n = len(M["segments"])
graph = ";".join(fl) + ";" + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
os.makedirs("out", exist_ok=True)
cmd = ["ffmpeg", "-y", "-loglevel", "error"] + ins + ["-i", "episode_audio.m4a", "-filter_complex", graph, "-map", "[v]", "-map", f"{n}:a",
       "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", "out/video.mp4"]
print(" ".join(cmd[:8]), "...", flush=True)
subprocess.run(cmd, check=True)
'''
def macjob():
    d = os.path.join(OUT, "macjob"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "render.py"), "w").write(MAC)
    for f in ("manifest.json", "episode_audio.m4a"): subprocess.run(["cp", os.path.join(OUT, f), d], check=True)
    json.dump(dict(title="Tumble & Pip: Fables About Friendship (long-form v2)"), open(os.path.join(d, "job.json"), "w"))
    print("wrote", d)

if __name__ == "__main__":
    {"audio": audio, "macjob": macjob}[sys.argv[1]]()
