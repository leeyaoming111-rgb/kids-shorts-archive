"""usage: python3 el_mix.py <fable_dir>  -> audio/<fable-NN>/mix.mp3 + report.json, and <fable_dir>/code/out/audio.wav + song_check.json

Mixes the assembled song (code/out/song.wav from `el_batch.py assemble`, else the committed audio/<fable-NN>/song.mp3)
with the spoken lines from `el_voice.py` at their timeline t0, normalises to -14 LUFS (peak kept under -0.2 dBFS), then
runs speech-to-text on the full mix for lyric recall (target 90%+). report.json keeps any fields already in it (verse
take, seeds) and updates joins, spoken lines and mix numbers. The key comes from ELEVENLABS_API_KEY only."""
import os, sys, json, shutil, difflib, subprocess
import numpy as np, requests, soundfile as sf, pyloudnorm as pyln
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import el_batch as E
from el_voice import timeline, audio_dir

SR = 44100

def mix(fable_dir):
    out, dest = os.path.join(fable_dir, "code", "out"), audio_dir(fable_dir)
    os.makedirs(out, exist_ok=True)
    # song + song_check: fresh from assemble if present, else the committed copies (and keep both places in step)
    if os.path.exists(os.path.join(out, "song.wav")):
        song = sf.read(os.path.join(out, "song.wav"), always_2d=True)[0].astype(np.float32)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(out, "song.wav"), "-b:a", "128k",
                        os.path.join(dest, "song.mp3")], check=True)
        shutil.copy(os.path.join(out, "song_check.json"), os.path.join(dest, "song_check.json"))
    else:
        song = E.load(os.path.join(dest, "song.mp3"))
        shutil.copy(os.path.join(dest, "song_check.json"), os.path.join(out, "song_check.json"))
    tl = timeline(fable_dir)                                   # reads out/song_check.json for the real word times
    spoken = json.load(open(os.path.join(dest, "spoken.json"))) if os.path.exists(os.path.join(dest, "spoken.json")) else {}
    n = max(len(song), int(tl.DURATION * SR)); m = np.zeros((n, 2), np.float32); m[:len(song)] += song
    placed = []
    for s in tl.SPOKEN:
        x = E.load(os.path.join(dest, f"{s['file']}.mp3")); i = int(s["t0"] * SR); seg = x[:max(0, n - i)]
        m[i:i + len(seg)] += seg; placed.append((s["file"], round(s["t0"], 3)))
    meter = pyln.Meter(SR)
    m = pyln.normalize.loudness(m, meter.integrated_loudness(m), -14.0)
    pk = float(np.abs(m).max())
    if pk > 0.98: m *= 0.98 / pk
    sf.write(os.path.join(out, "audio.wav"), m, SR)                       # render.py muxes this
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(out, "audio.wav"), "-b:a", "128k",
                    os.path.join(dest, "mix.mp3")], check=True)
    lufs = meter.integrated_loudness(E.load(os.path.join(dest, "mix.mp3")))
    sc = json.load(open(os.path.join(out, "song_check.json")))
    stt = requests.post(f"{E.API}/speech-to-text", headers=E.key(), data={"model_id": "scribe_v1"},
                        files={"file": open(os.path.join(dest, "mix.mp3"), "rb")}, timeout=300).json()
    exp = [w for L in sc["lines"] for w in E.words_norm(L["line"])]; heard = E.words_norm(stt.get("text", ""))
    recall = sum(b.size for b in difflib.SequenceMatcher(a=exp, b=heard, autojunk=False).get_matching_blocks()) / max(1, len(exp))
    rp = os.path.join(dest, "report.json")
    rep = json.load(open(rp)) if os.path.exists(rp) else dict(fable=os.path.basename(os.path.normpath(fable_dir)))
    if "joins" in sc: rep.update(joins=sc["joins"], joins_all_ok=all(j["ok"] for j in sc["joins"]))
    if spoken:
        by_file = {r["file"]: r for r in spoken["spoken"]}
        rep["spoken"] = [dict(by_file.get(f"{f}.mp3", dict(file=f"{f}.mp3")), t0=t0) for f, t0 in placed]
        rep["tts"] = {k: spoken[k] for k in ("model", "stability", "takes", "pick")}
    rep["mix"] = dict(rep.get("mix", {}), lufs=round(lufs, 2), target_lufs=-14, peak=round(float(np.abs(m).max()), 3),
                      lyric_recall=round(recall, 4), stt=stt.get("text"))
    json.dump(rep, open(rp, "w"), indent=1)
    print(f"mix LUFS {lufs:.2f}  full-mix lyric recall {recall:.1%} {'ok' if recall >= 0.9 and abs(lufs + 14) <= 1 else 'CHECK'}")

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    mix(sys.argv[1])
