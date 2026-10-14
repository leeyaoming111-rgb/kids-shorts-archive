"""Assemble Episode 01 (16:9) from the Story Stump scene renders and the fable renders.

usage: python3 assemble.py [--out renders/episode-01_wide.mp4] [--crf 21] [--work <dir>] [--keep]

Inputs (episode.py has the running order, the cut grid, XF and HANDLE):
  renders/episode-01/<scene>_wide.mp4     intro, link01..09, break, recap, outro (from `code/render.py`, audio muxed)
  renders/fable-NN_wide.mp4               the ten fables (1920x1080, 30 fps, with audio)
A segment that does not exist yet becomes a placeholder card of the right length (silent), so the assembly can be tested
at any time. Each fable drops the series sting (3.6-6.0 s): a hard cut on the bar line in the picture, a 0.1 s equal-power
crossfade in the sound; it also stops at the cut grid's chorus or button point plus HANDLE. Segments join with 0.5 s
video dissolves (ffmpeg xfade) and equal-power audio crossfades. The result is normalised to -14 LUFS (peak under -0.2 dBFS)."""
import os, sys, json, subprocess, argparse, shutil
import numpy as np, soundfile as sf, pyloudnorm as pyln
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import episode as EP

SR, FPS, W, H = 44100, 30, 1920, 1080
XF = EP.XF
FONT = os.path.join(HERE, "code", "assets", "Fredoka.ttf")

def run(*a):
    r = subprocess.run(list(map(str, a)), capture_output=True)
    if r.returncode: sys.exit(f"{a[0]} failed: {r.stderr.decode()[-1500:]}")
    return r
def probe(p):
    return float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p).stdout)
def load_audio(p):
    raw = run("ffmpeg", "-loglevel", "error", "-i", p, "-f", "f32le", "-ac", "2", "-ar", SR, "-").stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def sec(x, a, b):
    """audio between a and b seconds, zero-padded if the file is short"""
    i, j = int(round(a * SR)), int(round(b * SR)); seg = x[i:j]
    if len(seg) < j - i: seg = np.concatenate([seg, np.zeros((j - i - len(seg), 2), np.float32)])
    return seg
def xfade_audio(a, b, n):
    """equal-power crossfade of a's last n samples into b's first n; length len(a)+len(b)-n"""
    g = np.linspace(0, np.pi / 2, n)[:, None]
    return np.concatenate([a[:-n], a[-n:] * np.cos(g) + b[:n] * np.sin(g), b[n:]])

def card(path, secs, big, small):
    """placeholder segment: a plain card with text, silent"""
    txt = lambda s: s.replace(":", r"\:").replace("'", "")
    vf = (f"drawtext=fontfile={FONT}:text='{txt(big)}':fontcolor=white:fontsize=96:x=(w-text_w)/2:y=(h-text_h)/2-40,"
          f"drawtext=fontfile={FONT}:text='{txt(small)}':fontcolor=0xffd650:fontsize=54:x=(w-text_w)/2:y=(h/2)+70")
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c=0x28305c:s={W}x{H}:r={FPS}:d={secs}",
        "-vf", vf, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", path)

def segment(item, work):
    """-> (video path, audio array, is_placeholder). Video is exactly seg_len(item) long at 30 fps."""
    n = EP.seg_len(item)
    if isinstance(item, int):
        src = os.path.join(EP.RENDERS, f"fable-{item:02d}_wide.mp4"); name = f"fable{item:02d}"
        title = f"{item}. {EP.FABLES[item]['title']}"
    else:
        src = os.path.join(EP.SCENE_RENDERS, f"{item}_wide.mp4"); name = item; title = item
    vid = os.path.join(work, f"{name}.mp4")
    if not os.path.exists(src):
        print(f"  placeholder for {name} ({n:.2f} s)")
        card(vid, n, title, "placeholder card (render not landed yet)")
        return vid, np.zeros((int(round(n * SR)), 2), np.float32), True
    if isinstance(item, int):
        a, b = EP.HOOK_END, EP.STING_END; out = EP.fable_out(item)
        # picture: hook, hard cut over the dropped sting, then on to the cut point plus HANDLE
        fc = (f"[0:v]trim=0:{a},setpts=PTS-STARTPTS[p];[0:v]trim={b}:{out},setpts=PTS-STARTPTS[q];[p][q]concat=n=2:v=1:a=0,"
              f"fps={FPS},scale={W}:{H},format=yuv420p[v]")
        run("ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-crf", "16", vid)
        x = load_audio(src); h = 0.05
        p = sec(x, 0, a + h); q = sec(x, b - h, out)
        au = xfade_audio(p, q, int(2 * h * SR))                       # crossfade centred on the cut: q[b] lands at a
    else:
        run("ffmpeg", "-y", "-loglevel", "error", "-i", src, "-an", "-vf", f"fps={FPS},scale={W}:{H},format=yuv420p",
            "-c:v", "libx264", "-crf", "16", vid)
        au = sec(load_audio(src), 0, n)
    nn = int(round(n * SR)); au = au[:nn] if len(au) >= nn else np.concatenate([au, np.zeros((nn - len(au), 2), np.float32)])
    return vid, au, False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(EP.RENDERS, "episode-01_wide.mp4"))
    ap.add_argument("--crf", type=int, default=21)
    ap.add_argument("--work", default=os.path.join(HERE, "code", "out", "assemble"))
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True); os.makedirs(os.path.dirname(a.out), exist_ok=True)
    segs = []
    for item in EP.ORDER:
        print("segment", item, flush=True); segs.append((item,) + segment(item, a.work))
    starts, total = EP.starts()
    # ---- picture: chained xfade dissolves ----
    ins = []
    for _, vid, _, _ in segs: ins += ["-i", vid]
    chain, label, acc = "", "[0:v]", EP.seg_len(segs[0][0])
    for k in range(1, len(segs)):
        out = f"[x{k}]"; off = acc - XF
        chain += f"{label}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.4f}{out};"; label = out
        acc = off + EP.seg_len(segs[k][0])
    chain = chain.rstrip(";") + f";{label}format=yuv420p[v]"
    silent = os.path.join(a.work, "picture.mp4")
    run("ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", chain, "-map", "[v]", "-c:v", "libx264", "-preset", "medium",
        "-crf", a.crf, "-r", FPS, silent)
    # ---- sound: equal-power crossfades at the same offsets, then -14 LUFS ----
    n = int(round(total * SR)) + SR; mix = np.zeros((n, 2), np.float32); xn = int(XF * SR)
    for (item, _, au, _), t0 in zip(segs, [starts[i] for i in EP.ORDER]):
        au = au.copy(); i = int(round(t0 * SR)); g = np.linspace(0, np.pi / 2, xn)[:, None]
        if item != EP.ORDER[0]: au[:xn] *= np.sin(g)
        if item != EP.ORDER[-1]: au[-xn:] *= np.cos(g)
        mix[i:i + len(au)] += au
    mix = mix[:int(round(total * SR))]
    meter = pyln.Meter(SR); lu = meter.integrated_loudness(mix)
    if lu > -70:
        mix = pyln.normalize.loudness(mix, lu, -14.0)
        pk = float(np.abs(mix).max())
        if pk > 0.977: mix *= 0.977 / pk
    wav = os.path.join(a.work, "episode.wav"); sf.write(wav, mix, SR)
    run("ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", a.out)
    final = load_audio(a.out)
    rep = dict(out=os.path.relpath(a.out, EP.BATCH), duration=round(probe(a.out), 2), planned=round(total, 2),
               lufs=round(meter.integrated_loudness(final), 2), peak_dbfs=round(20 * np.log10(np.abs(final).max() + 1e-9), 2),
               placeholders=[str(s[0]) for s in segs if s[3]], size_mb=round(os.path.getsize(a.out) / 1e6, 1),
               segments={str(i): round(starts[i], 2) for i in EP.ORDER})
    json.dump(rep, open(os.path.join(a.work, "report.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "segments"}, indent=1))
    if not a.keep:
        for f in os.listdir(a.work):
            if f.endswith(".mp4") and f != os.path.basename(a.out): os.remove(os.path.join(a.work, f))
        wavp = os.path.join(a.work, "episode.wav")
        if os.path.exists(wavp): os.remove(wavp)

if __name__ == "__main__":
    main()
