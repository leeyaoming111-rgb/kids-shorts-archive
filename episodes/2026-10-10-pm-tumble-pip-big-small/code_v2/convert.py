"""Convert each sung line of the vocal stem to the character's fixed ElevenLabs voice (speech-to-speech keeps melody and timing)."""
import json, subprocess, requests, numpy as np, soundfile as sf, io, concurrent.futures as cf, sys
KEY = open("/tmp/claude-0/-home-claude/6c643c4e-4a9a-54c7-b0b9-cac71cfb5471/scratchpad/el_key").read().strip()
CAST = json.load(open("cast_voices.json")); SR = 44100
C = json.load(open("take_f_check.json"))
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i",p,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout,np.float32).astype(np.float64)
voc = load("stems_f/vocals.mp3")
import os; os.makedirs("sts", exist_ok=True)
jobs = []
for i, L in enumerate(C["lines"]):
    a = max(0.0, L["words"][0]["t0"] - 0.12); b = min(len(voc) / SR, L["words"][-1]["t1"] + 0.45)
    seg = voc[int(a * SR):int(b * SR)].copy(); n = len(seg); f = int(0.03 * SR)
    seg[:f] *= np.linspace(0, 1, f); seg[-int(0.12 * SR):] *= np.linspace(1, 0, int(0.12 * SR))
    fn = f"sts/src_{i:02d}.wav"; sf.write(fn, seg, SR); jobs.append((i, L["who"], fn, a))
def run(j):
    i, who, fn, a = j
    r = requests.post(f"https://api.elevenlabs.io/v1/speech-to-speech/{CAST[who]['voice_id']}?output_format=mp3_44100_128",
                      headers={"xi-api-key": KEY}, files={"audio": open(fn, "rb")},
                      data={"model_id": "eleven_multilingual_sts_v2", "remove_background_noise": "false",
                            "voice_settings": json.dumps({"stability": 0.35, "similarity_boost": 0.9, "style": 0.3, "use_speaker_boost": True})}, timeout=300)
    if r.status_code != 200: return i, f"ERR {r.status_code} {r.text[:200]}"
    open(f"sts/out_{i:02d}.mp3", "wb").write(r.content); return i, "ok"
with cf.ThreadPoolExecutor(2) as ex:
    for i, s in ex.map(run, jobs): print(i, s, flush=True)
json.dump([dict(i=i, who=w, src=fn, start=a) for i, w, fn, a in jobs], open("sts/index.json", "w"), indent=1)
