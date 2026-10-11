import json, glob, numpy as np, soundfile as sf, parselmouth, subprocess, re
import timeline as T
from sing import hnr
v, sr = sf.read("out/voice.wav")
log = json.load(open("out/vocal_log.json"))
sung = [e for e in log if e["tag"] != "spoken"]
seg = np.concatenate([v[int(e["start"] * sr):int((e["start"] + e["length"]) * sr)] for e in sung])
p = parselmouth.Sound(seg, sr).to_pitch_ac(0.01, 60, 500).selected_array["frequency"]; p = p[p > 0]
m = 69 + 12 * np.log2(p / 440); cents = 100 * np.abs(m - np.round(m))
print(f"tuning: median {np.median(cents):.1f} cents, within30 {np.mean(cents < 30) * 100:.0f}%")
raw = [hnr(*sf.read(f)) for f in sorted(glob.glob("out/tts/p*.wav"))]
print(f"HNR raw TTS {np.mean(raw):.1f} dB, tuned sung voice {hnr(seg, sr):.1f} dB")
S = np.abs(np.fft.rfft(seg)) ** 2; f = np.fft.rfftfreq(len(seg), 1 / sr)
print(f"energy >12k: {S[f > 12000].sum() / S.sum() * 100:.2f}%")
cuts = [(e["tag"], e["cut"]) for e in log]
print("max cut", max(c for _, c in cuts), "phrases cut >0.03:", [c for c in cuts if c[1] > 0.03])
srt = sorted(log, key=lambda e: e["start"])
gaps = [b["start"] - (a["start"] + a["length"]) for a, b in zip(srt, srt[1:])]
print("min gap between voice lines", round(min(gaps), 3))
r = subprocess.run(["ffmpeg", "-nostats", "-i", "out/audio.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
print("loudness", re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1], "LUFS")
