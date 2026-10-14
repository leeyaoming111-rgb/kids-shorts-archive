"""Episode 01 audio tool (ElevenLabs): the Story Stump scenes (intro, link01..09, break, recap, outro).

usage (ELEVENLABS_API_KEY from the environment only; never printed or written):
  python3 el_episode.py music bed|recap|outro <seed> ...   music_v2_5 takes -> audio/episode-01/<name>_<seed>.mp3 (+ _check.json for sung ones)
  python3 el_episode.py keep  bed|recap|outro <seed>       copy that take to audio/episode-01/<name>.mp3 (+ _check.json)
  python3 el_episode.py voice [scene ...]                  eleven_v3 TTS in the cast voices, 2 takes, widest pitch range wins,
                                                           forced-aligned -> audio/episode-01/tts/<scene>_<i>.mp3 + tts.json
  python3 el_episode.py mix [scene ...]                    per-scene mix at -14 LUFS -> audio/episode-01/<scene>.mp3 and
                                                           <scene>.json (duration, lines with word times, cues), recall by speech-to-text

Scenes: intro = the stored sting, then the bed; links = a bar-aligned 8 s window of the bed, ducked under the voices;
break = the stored chorus twice (3 bars apart) plus Tumble's call; recap and outro = their own music takes plus voices.
Models after el_batch.py / el_voice.py / el_mix.py (same fingerprint, singers, voices, TTS settings)."""
import os, sys, json, shutil, difflib, subprocess
import numpy as np, requests, soundfile as sf, pyloudnorm as pyln
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "episode"))
import el_batch as E
import el_voice as V
import episode as EP

SR = 44100
AD = EP.AUDIO
SERIES = os.path.join(HERE, "audio", "series")
os.makedirs(os.path.join(AD, "tts"), exist_ok=True)
SCENES = ["intro"] + [f"link{k:02d}" for k in range(1, 10)] + ["break", "recap", "outro"]

# ------------------------------------------------------------------ music takes
BASE_LULLABY = ["children's lullaby", "gentle storybook folk", "100 BPM", "half-time feel", "D major", "music box glockenspiel",
                "soft acoustic guitar", "upright bass", "hushed and warm", "clear diction"]
BASE_RECAP = [b if b != "warm and playful" else "warm and gentle" for b in E.BASE]
TAKES = {"bed": (EP.BED_SECTIONS, E.BASE, []), "recap": (EP.RECAP_SECTIONS, BASE_RECAP + ["softer and slower in feel"], []),
         "outro": (EP.OUTRO_SECTIONS, BASE_LULLABY, ["drums", "percussion", "soft hand drum", "loud"])}

def compose(name, seed):
    secs, base, neg_extra = TAKES[name]
    chunks = []
    for i, (sec, ms, text, who) in enumerate(secs):
        sty = E.VOICE.get(who, ["instrumental"])
        pos = (base + sty) if i == 0 else (base[:6] + sty)
        neg = E.NEG + neg_extra + (["vocals", "singing", "voice"] if who is None else [])
        chunks.append(dict(text=text, duration_ms=ms, positive_styles=pos, negative_styles=neg))
    r = requests.post(f"{E.API}/music?output_format=mp3_44100_128", headers=E.key(), timeout=300,
                      json=dict(model_id="music_v2_5", composition_plan=dict(chunks=chunks), seed=int(seed)))
    if r.status_code != 200: sys.exit(f"compose failed {r.status_code}: {r.text[:300]}")
    out = os.path.join(AD, f"{name}_{seed}.mp3"); open(out, "wb").write(r.content)
    if name == "bed":                                                   # instrumental: STT should hear no words
        stt = requests.post(f"{E.API}/speech-to-text", headers=E.key(), data={"model_id": "scribe_v1"},
                            files={"file": open(out, "rb")}, timeout=300).json()
        print(name, seed, "words heard:", len(E.words_norm(stt.get("text", ""))))
    else:
        E.check(out, secs)
    print("wrote", out)

def keep(name, seed):
    shutil.copy(os.path.join(AD, f"{name}_{seed}.mp3"), os.path.join(AD, f"{name}.mp3"))
    c = os.path.join(AD, f"{name}_{seed}_check.json")
    if os.path.exists(c): shutil.copy(c, os.path.join(AD, f"{name}_check.json"))

# ------------------------------------------------------------------ voices
def voice():
    only = [a for a in sys.argv[2:]] or SCENES
    tj = os.path.join(AD, "tts", "tts.json"); rep = json.load(open(tj)) if os.path.exists(tj) else {}
    for sc in only:
        for i, (t, who, text, kind, tags) in enumerate(EP.LINES[sc]):
            if kind != "tts": continue
            key = f"{sc}_{i}"; out = os.path.join(AD, "tts", f"{key}.mp3")
            if key in rep and os.path.exists(out) and rep[key]["text"] == text and rep[key]["tags"] == tags: continue
            takes = []
            for k, seed in enumerate(V.SEEDS):
                p = os.path.join(AD, "tts", f"{key}_take{k + 1}.mp3"); V.tts(V.VOICES[who]["voice_id"], f"{tags} {text}", seed, p)
                takes.append(dict(path=p, seed=seed, range_st=round(V.pitch_range(p), 2)))
            best = max(takes, key=lambda x: x["range_st"])
            shutil.copy(best["path"], out)
            for x in takes: os.remove(x["path"])
            fa = requests.post(f"{E.API}/forced-alignment", headers=E.key(), data={"text": text},
                               files={"file": open(out, "rb")}, timeout=300).json()
            words = [dict(w=w["text"], t0=w["start"], t1=w["end"]) for w in fa.get("words", []) if w["text"].strip()]
            n = len(text.split())
            if len(words) != n: words = (words + [words[-1]] * n)[:n] if words else []
            rep[key] = dict(scene=sc, who=who, text=text, tags=tags, seed=best["seed"], takes=[dict(seed=x["seed"], range_st=x["range_st"]) for x in takes],
                            dur=round(len(E.load(out)) / SR, 3), words=words, align_loss=fa.get("loss"))
            print(key, who, rep[key]["dur"], "s", [x["range_st"] for x in takes], flush=True)
            json.dump(rep, open(tj, "w"), indent=1)

# ------------------------------------------------------------------ mix
def fade(x, a=0.0, b=0.0):
    x = x.copy()
    if a: n = min(len(x), int(a * SR)); x[:n] *= np.linspace(0, 1, n)[:, None]
    if b: n = min(len(x), int(b * SR)); x[-n:] *= np.linspace(1, 0, n)[:, None]
    return x
def put(m, x, t):
    i = int(round(t * SR)); seg = x[:max(0, len(m) - i)]
    if i >= 0: m[i:i + len(seg)] += seg
def envelope(voice, win=0.08, up=0.12, down=0.5):
    """smooth 0..1 'someone is talking' envelope from the voice track (attack and release in seconds)"""
    r = np.sqrt(np.convolve((voice.mean(1)) ** 2, np.ones(int(win * SR)) / int(win * SR), "same"))
    on = (r > 0.01).astype(float)[::441]
    e = np.zeros(len(on)); v = 0.0
    for i, o in enumerate(on):
        c = 1 / (up * 100) if o > v else 1 / (down * 100)
        v += (o - v) * min(1.0, c * 3); e[i] = v
    return np.interp(np.arange(len(voice)), np.arange(len(e)) * 441, e)
def stored_lines(name, t, text=None):
    out = []
    for L in json.load(open(os.path.join(SERIES, f"{name}_check.json")))["lines"]:
        out.append(dict(who=L["who"], line=L["line"], sec="Sting" if name == "sting" else "Chorus", kind=name,
                        words=[dict(w=w["w"], t0=round(w["t0"] + t, 3), t1=round(w["t1"] + t, 3)) for w in L["words"]]))
    return out

def place_voice(sc):
    """TTS lines at their planned time, or 0.3 s after the previous voice line; returns (lines, [(t, audio)])"""
    rep = json.load(open(os.path.join(AD, "tts", "tts.json"))); lines, clips, prev_end = [], [], -9.0
    for i, (t, who, text, kind, tags) in enumerate(EP.LINES[sc]):
        if kind != "tts": continue
        r = rep[f"{sc}_{i}"]; x = E.load(os.path.join(AD, "tts", f"{sc}_{i}.mp3"))
        t0 = max(t, prev_end + 0.3); prev_end = t0 + len(x) / SR
        clips.append((t0, x))
        lines.append(dict(who=who, line=text, sec="Talk", kind="tts", words=[dict(w=w["w"], t0=round(w["t0"] + t0, 3), t1=round(w["t1"] + t0, 3)) for w in r["words"]]))
    return lines, clips

def mix_scene(sc):
    planned = EP.SCENE_LEN[sc]; lines, clips = [], []; cues = {}
    if sc in EP.LINES and any(k == "tts" for _, _, _, k, _ in EP.LINES[sc]): lines, clips = place_voice(sc)
    end_voice = max([c[0] + len(c[1]) / SR for c in clips], default=0)
    dur = planned if end_voice + 0.5 <= planned else round(end_voice + 0.6, 1)
    n = int(dur * SR); music = np.zeros((n, 2), np.float32); voice = np.zeros((n, 2), np.float32)
    for t0, x in clips: put(voice, x, t0)
    if sc == "intro":
        sting = E.load(os.path.join(SERIES, "sting.mp3")); bed = E.load(os.path.join(AD, "bed.mp3"))
        put(music, fade(sting, 0, 0.25), 0.0)
        put(music, fade(bed[:int((dur - EP.BAR) * SR)], 1.0, 2.0) * 0.5, EP.BAR)
        lines = stored_lines("sting", 0.0) + lines
    elif sc.startswith("link"):
        bed = E.load(os.path.join(AD, "bed.mp3")); o = int(EP.BED_AT[sc] * EP.BAR * SR)
        music += fade(bed[o:o + n], 0.4, 0.7) * 0.5
    elif sc == "break":
        ch = E.load(os.path.join(SERIES, "chorus.mp3")); a, b = EP.CHORUS_AT["break"]
        put(music, fade(ch[:int(7.2 * SR) + int(0.3 * SR)], 0, 0.3), a)                 # first: 3 bars and a short tail under the second
        put(music, ch, b)
        lines += stored_lines("chorus", a) + stored_lines("chorus", b); cues["chorus"] = [a, round(b + 3 * EP.BAR, 3)]
    else:                                                                              # recap, outro: their own sung takes
        take = E.load(os.path.join(AD, f"{sc}.mp3")); chk = json.load(open(os.path.join(AD, f"{sc}_check.json")))
        music[:min(n, len(take))] = take[:n]
        music = fade(music, 0.0, 1.2 if sc == "outro" else 0.0) if sc == "outro" else music
        for L in chk["lines"]:
            lines.append(dict(who="both", line=L["line"], sec="Moral" if sc == "recap" else "Lullaby", kind="recap" if sc == "recap" else "lullaby", words=L["words"]))
    if sc.startswith("link") or sc == "intro":                                         # duck the bed under the voices
        duck = envelope(voice)
        music = music * (1.0 - 0.55 * duck)[:, None]
    elif sc == "outro" and len(clips):
        music = music * (1.0 - 0.4 * envelope(voice))[:, None]
    elif sc == "break":
        music = music * (1.0 - 0.35 * envelope(voice))[:, None]
    m = music + voice * 1.1
    meter = pyln.Meter(SR)
    m = pyln.normalize.loudness(m, meter.integrated_loudness(m), -14.0)
    pk = float(np.abs(m).max())
    if pk > 0.97: m *= 0.97 / pk
    wav = os.path.join(AD, f"{sc}.wav"); sf.write(wav, m, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-b:a", "160k", os.path.join(AD, f"{sc}.mp3")], check=True); os.remove(wav)
    lufs = meter.integrated_loudness(E.load(os.path.join(AD, f"{sc}.mp3")))
    exp = [w for L in lines for w in E.words_norm(L["line"])]
    stt = requests.post(f"{E.API}/speech-to-text", headers=E.key(), data={"model_id": "scribe_v1"},
                        files={"file": open(os.path.join(AD, f"{sc}.mp3"), "rb")}, timeout=300).json()
    heard = E.words_norm(stt.get("text", ""))
    recall = sum(b.size for b in difflib.SequenceMatcher(a=exp, b=heard, autojunk=False).get_matching_blocks()) / max(1, len(exp))
    lines.sort(key=lambda L: L["words"][0]["t0"])
    json.dump(dict(scene=sc, duration=dur, lines=lines, cues=cues,
                   mix=dict(lufs=round(lufs, 2), target_lufs=-14, peak=round(float(np.abs(m).max()), 3), lyric_recall=round(recall, 4), stt=stt.get("text"))),
              open(os.path.join(AD, f"{sc}.json"), "w"), indent=1)
    print(f"{sc:7s} {dur:5.1f}s  LUFS {lufs:6.2f}  recall {recall:.0%} {'ok' if recall >= 0.9 and abs(lufs + 14) <= 1 else 'CHECK'}", flush=True)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    c = sys.argv[1]
    if c == "music":
        for s in sys.argv[3:]: compose(sys.argv[2], s)
    elif c == "keep": keep(sys.argv[2], sys.argv[3])
    elif c == "voice": voice()
    elif c == "mix":
        for sc in (sys.argv[2:] or SCENES): mix_scene(sc)
    else: sys.exit(__doc__)
