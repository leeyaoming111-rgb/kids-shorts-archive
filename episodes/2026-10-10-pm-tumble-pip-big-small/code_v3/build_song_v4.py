"""v4 song (owner's pick, plan A): the ElevenLabs Music take's OWN singers, no voice conversion.
Instrumental + vocal stems re-summed; only "Small feet hop!" is moved back one bar (vocal stem segment) to leave room for the gag."""
import json, numpy as np, soundfile as sf, subprocess
V = "/home/claude/job4/v2/"; SR = 44100
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i",p,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout,np.float32).astype(np.float64)
inst = sum(load(V + f"stems_f/{s}.mp3") for s in ("bass", "drums", "guitar", "other", "piano")); voc = load(V + "stems_f/vocals.mp3")[:len(inst)]
C = json.load(open(V + "take_f_check.json")); BAR = 1.37
L = C["lines"][10]; a = L["words"][0]["t0"] - 0.12; b = L["words"][-1]["t1"] + 0.45
i0, i1, d = int(a * SR), int(b * SR), int(BAR * SR)
seg = voc[i0:i1].copy(); f = int(0.03 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-int(0.12 * SR):] *= np.linspace(1, 0, int(0.12 * SR))
voc[i0:i1] = 0.0; voc[i0 - d:i1 - d] += seg
lines = []
for k, L in enumerate(C["lines"]):
    sh = -BAR if k == 10 else 0.0
    L = dict(L); L["words"] = [dict(w, t0=w["t0"] + sh, t1=w["t1"] + sh) for w in L["words"]]; lines.append(L)
lines[0]["line"] = "Big and small, big and small, big and small,"            # the singer's extra repeat (2.7-4.5 s)
X = json.load(open(V + "sts/x.json")); xw = X["words"]; xw[0]["t1"] = 3.05; xw[1]["t0"] = 3.05
lines[0]["words"] += [dict(w=w["w"], t0=w["t0"], t1=w["t1"]) for w in xw]
song = inst + voc
sf.write("out/song.wav", song / np.max(np.abs(song)) * 0.95, SR)
json.dump(dict(C, lines=lines, note="v4: take_f native singers (no conversion); line 10 vocal moved -1 bar"), open("out/song_check.json", "w"), indent=1)
print("ok")
