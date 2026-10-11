"""Sing a line in a cast voice: ElevenLabs TTS (multilingual v2) -> forced-align words -> per-word duration map onto the source
singer's word timings -> PSOLA pitch onto the source melody (octave-shifted into the character's range)."""
import json, numpy as np, parselmouth, subprocess, requests, sys
from parselmouth.praat import call
SCR = "/tmp/claude-0/-home-claude/6c643c4e-4a9a-54c7-b0b9-cac71cfb5471/scratchpad/"; KEY = open(SCR + "el_key").read().strip()
CAST = json.load(open("cast_voices.json")); HOME = {"tumble": 220.0, "pip": 520.0}
def wav(p, tag): subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", p, "-ac", "1", "-ar", "44100", SCR + tag + ".wav"]); return parselmouth.Sound(SCR + tag + ".wav")
def sing(name, who, text, src_wav, src_t0, words):
    """words: source words with absolute t0/t1; src_wav starts at absolute time src_t0."""
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{CAST[who]['voice_id']}?output_format=mp3_44100_128", headers={"xi-api-key": KEY},
                      json=dict(text=text, model_id="eleven_multilingual_v2", voice_settings=dict(stability=0.45, similarity_boost=0.85, style=0.35)), timeout=200)
    open(f"sts/tts_{name}.mp3", "wb").write(r.content)
    fa = requests.post("https://api.elevenlabs.io/v1/forced-alignment", headers={"xi-api-key": KEY}, data={"text": text},
                       files={"file": open(f"sts/tts_{name}.mp3", "rb")}, timeout=200).json()
    tw = [w for w in fa["words"] if w["text"].strip()]
    assert len(tw) == len(words), (len(tw), len(words))
    tts = wav(f"sts/tts_{name}.mp3", "t" + name)
    # piecewise map: TTS time -> output time (relative to src_t0); first word starts where the source word starts
    A = [(tw[0]["start"], words[0]["t0"] - src_t0)]
    for k, (a, s) in enumerate(zip(tw, words)):
        A.append((a["end"], s["t1"] - src_t0))
        if k + 1 < len(tw): A.append((tw[k + 1]["start"], words[k + 1]["t0"] - src_t0))
    A = [(max(x, 1e-3), max(y, 1e-3)) for x, y in A]
    # crop TTS to [first word start, last word end + tail]
    a0 = max(0.0, A[0][0] - 0.02); a1 = min(tts.duration, A[-1][0] + 0.15)
    tts = tts.extract_part(a0, a1, parselmouth.WindowShape.HANNING, 1.0, False) if False else call(tts, "Extract part", a0, a1, "rectangular", 1.0, "no")
    A = [(x - a0, y) for x, y in A]
    man = call(tts, "To Manipulation", 0.01, 75, 1000)
    dt = call("Create DurationTier", "d", 0, tts.duration)
    prev = (0.0, A[0][1] - 0.02 if A[0][1] > 0.02 else 0.0)
    for (x0, y0), (x1, y1) in zip(A, A[1:]):
        if x1 - x0 < 0.005: continue
        fct = max(0.25, min(4.0, (y1 - y0) / (x1 - x0)))
        call(dt, "Add point", x0 + 0.002, fct); call(dt, "Add point", x1 - 0.002, fct)
    call([dt, man], "Replace duration tier")
    # pitch: source melody, mapped back into TTS time
    src = wav(src_wav, "s" + name); ps = src.to_pitch(time_step=0.01, pitch_floor=70, pitch_ceiling=1100)
    t = ps.xs() + 0.0; f = ps.selected_array["frequency"]; v = f > 0
    k = min((-2, -1, 0, 1, 2), key=lambda k: abs(np.log2(np.median(f[v]) * 2.0 ** k / HOME[who])))
    ys = np.array([y for _, y in A]); xs = np.array([x for x, _ in A])
    srcoff = src_t0                                              # source wav time 0 == absolute src_t0 == output time 0
    pt = call("Create PitchTier", "p", 0, tts.duration)
    for tt, ff in zip(t[v], f[v]):
        if ys[0] <= tt <= ys[-1]: call(pt, "Add point", float(np.interp(tt, ys, xs)), float(ff * 2.0 ** k))
    call([pt, man], "Replace pitch tier")
    out = call(man, "Get resynthesis (overlap-add)")
    lead = A[0][1] - 0.02                                         # output time of the cropped start
    out.save(f"sts/sung_{name}.wav", "WAV")
    return dict(name=name, start=src_t0 + max(lead, 0.0), octave=k, dur=out.duration)
if __name__ == "__main__":
    C = json.load(open("take_f_check.json"))["lines"]; idx = json.load(open("sts/index.json")); res = []
    for i in (0, 1, 2, 3):
        res.append(sing(f"{i:02d}", idx[i]["who"], C[i]["line"], f"sts/src_{i:02d}.wav", idx[i]["start"], C[i]["words"])); print(res[-1], flush=True)
    X = json.load(open("sts/x.json")); xw = X["words"]; xw[0]["t1"] = 3.05; xw[1]["t0"] = 3.05
    res.append(sing("x", "tumble", "Big and small,", "sts/src_x.wav", X["start"], xw)); print(res[-1])
    json.dump(res, open("sts/sung_index.json", "w"), indent=1)
