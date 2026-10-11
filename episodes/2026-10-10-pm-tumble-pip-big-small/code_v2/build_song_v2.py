"""v2 song: ElevenLabs take_f instrumental stems + vocals converted to the fixed cast voices (speech-to-speech) and PSOLA-retuned
back onto the sung melody. Writes out/song.wav and out/song_check.json (line/word timings for captions, lip sync and shots)."""
import json, numpy as np, soundfile as sf, subprocess
V = "/home/claude/job4/v2/"; SR = 44100
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i",p,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout,np.float32).astype(np.float64)
inst = sum(load(V + f"stems_f/{s}.mp3") for s in ("bass", "drums", "guitar", "other", "piano"))
C = json.load(open(V + "take_f_check.json")); idx = json.load(open(V + "sts/index.json"))
BAR = 1.37; SHIFT = {10: -BAR}                  # "Small feet hop!" moved back one bar (instrumental chroma match 0.92)
vox = np.zeros(len(inst) + SR); lines = []
def place(path, a):
    y, _ = sf.read(path); s = int(a * SR); vox[s:s + len(y)] += y
SUNG = {d["name"]: d for d in json.load(open(V + "sts/sung_index.json"))}   # lines 0-3 + x: cast-voice TTS sung onto the melody (STS garbled them)
for j in idx:
    i = j["i"]; sh = SHIFT.get(i, 0.0)
    if f"{i:02d}" in SUNG: place(V + f"sts/sung_{i:02d}.wav", SUNG[f"{i:02d}"]["start"])
    else: place(V + f"sts/tuned_{i:02d}.wav", j["start"] + sh)
    L = dict(C["lines"][i]); L["words"] = [dict(w, t0=w["t0"] + sh, t1=w["t1"] + sh) for w in L["words"]]; lines.append(L)
X = json.load(open(V + "sts/x.json")); place(V + "sts/sung_x.wav", SUNG["x"]["start"])       # the singer's extra "big and small" in the intro
xw = X["words"]; xw[0]["t1"] = 3.05; xw[1]["t0"] = 3.05
lines[0]["line"] = "Big and small, big and small, big and small,"
lines[0]["words"] += [dict(w=w["w"], t0=w["t0"], t1=w["t1"]) for w in xw]
rng = np.random.default_rng(3); n = int(0.5 * SR)
ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (0.09 * SR)); ir /= np.abs(ir).sum() / 6
vox = (vox + 0.18 * np.convolve(vox, ir)[:len(vox)])[:len(inst)]
vox /= np.max(np.abs(vox)) + 1e-9; inst /= np.max(np.abs(inst)) + 1e-9
song = 0.62 * inst + 0.85 * vox
sf.write("out/song.wav", song / np.max(np.abs(song)) * 0.95, SR)
sf.write("out/el_v2/vox.wav", vox, SR); sf.write("out/el_v2/inst.wav", inst, SR)
json.dump(dict(C, lines=lines, note="v2: take_f; vocals converted to cast voices and retuned; line 10 shifted -1 bar"), open("out/song_check.json", "w"), indent=1)
print("ok", len(lines))
