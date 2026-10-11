"""PSOLA-retune each converted line onto the source melody (octave-shifted to suit the character), keeping the new voice."""
import json, numpy as np, parselmouth, subprocess
from parselmouth.praat import call
SCR = "/tmp/claude-0/-home-claude/6c643c4e-4a9a-54c7-b0b9-cac71cfb5471/scratchpad/"
idx = json.load(open("sts/index.json")); HOME = {"tumble": 270.0, "pip": 520.0}
def snd(path):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", path, "-ac", "1", "-ar", "44100", SCR + "r.wav"]); return parselmouth.Sound(SCR + "r.wav")
rep = []
for j in idx:
    src = snd(j["src"]); out = snd(f"sts/out_{j['i']:02d}.mp3")
    ps = src.to_pitch(time_step=0.01, pitch_floor=70, pitch_ceiling=1100)
    t = ps.xs(); f = ps.selected_array["frequency"]
    v = f > 0
    k = min((-2, -1, 0, 1, 2), key=lambda k: abs(np.log2(np.median(f[v]) * 2.0 ** k / HOME[j["who"]])))
    tgt = f * 2.0 ** k
    scale = out.duration / src.duration
    man = call(out, "To Manipulation", 0.01, 75, 1000)
    tier = call("Create PitchTier", "t", 0, out.duration)
    for tt, ff in zip(t[v], tgt[v]): call(tier, "Add point", tt * scale, float(ff))
    call([tier, man], "Replace pitch tier")
    res = call(man, "Get resynthesis (overlap-add)")
    res.save(f"sts/tuned_{j['i']:02d}.wav", "WAV")
    po = res.to_pitch(time_step=0.01, pitch_floor=70, pitch_ceiling=1100).selected_array["frequency"]
    n = min(len(po), len(tgt)); m = (po[:n] > 0) & (tgt[:n] > 0)
    err = np.abs(12 * np.log2(po[:n][m] / tgt[:n][m]))
    rep.append(dict(i=j["i"], who=j["who"], octave=k, median_hz=round(float(np.median(po[po > 0])), 1), within_50c=round(float(np.mean(err < 0.5)), 2)))
    print(rep[-1], flush=True)
json.dump(rep, open("sts/retune_report.json", "w"), indent=1)
