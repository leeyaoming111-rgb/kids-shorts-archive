import numpy as np, soundfile as sf, parselmouth, glob
from parselmouth.praat import call
import timeline as T
from sing import hnr
v, sr = sf.read("out/voice.wav")
seg = v[int(3.6*sr):int(40*sr)]
p = parselmouth.Sound(seg, sr).to_pitch_ac(0.01, 60, 500).selected_array["frequency"]; p = p[p > 0]
m = 69 + 12*np.log2(p/440); cents = 100*np.abs(m - np.round(m))
print(f"tuning: median {np.median(cents):.1f} cents, within30 {np.mean(cents<30)*100:.0f}%")
raw = [hnr(*sf.read(f)) for f in sorted(glob.glob("out/tts/p*.wav"))]
print(f"HNR raw TTS {np.mean(raw):.1f} dB, tuned voice bus {hnr(seg, sr):.1f} dB")
S = np.abs(np.fft.rfft(seg))**2; f = np.fft.rfftfreq(len(seg), 1/sr)
print(f"energy >12k: {S[f>12000].sum()/S.sum()*100:.2f}%")
