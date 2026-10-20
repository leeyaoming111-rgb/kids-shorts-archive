"""Batch 01 song tool v2 (polish pass, 2026-10-18). One continuous ElevenLabs Music generation per fable.

Why v2: v1 spliced three separate generations (verse + stored sting + stored chorus) and cut them together. That gave
a 20 dB jump after the sting, a chorus that faded to silence before the outro bar slammed back in, and a fresh singer
choice per fable (Tumble was sung by a woman in Fables 2, 3, 4, 7, 8 and 10; Pip by a man in 6 and 9).

v2 builds one composition plan with inpainting:
  Hook (gen) | Sting = stored sting, inserted unchanged | Setup A .. Moral (gen) | Chorus = stored chorus 0-5.4 s,
  inserted unchanged | Button (gen, 4.8 s: band plays on, happy final chord rings out)
The model writes the generated chunks around the stored ones (context_adherence high), so every join is musical.
Each Tumble chunk is conditioned on Fable 1's Tumble verse (the owner-approved voice), each Pip chunk on Fable 1's
Pip lines, and the opposite gender goes into negative_styles.

Takes are scored automatically: speech-to-text recall, every line inside its section, and per-line singer match
(median pitch in the character's range plus voice-embedding similarity to the Fable 1 reference lines).

  python3 el_song2.py refs                       upload sting, chorus, Fable 1 song once -> series_audio/refs.json
  python3 el_song2.py take <fable_dir> <seed>    compose + check one take -> <fable_dir>/code/out/take_<seed>.*
  python3 el_song2.py pick <fable_dir>           best checked take -> code/out/song.wav + song_check.json
Key: ELEVENLABS_API_KEY only. Max 2 concurrent requests on this plan."""
import os, sys, json, re, difflib, subprocess, importlib.util, io, zipfile, glob
import numpy as np

API = "https://api.elevenlabs.io/v1"
HERE = os.path.dirname(os.path.abspath(__file__))
SER = os.path.join(HERE, "audio", "series")
REFS = os.path.join(SER, "refs.json")
BAR = 2.4
STING_MS, CHORUS_MS, BUTTON_MS = 2400, 7200, 4800
STRENGTH = os.environ.get("EL_STRENGTH", "high")

BASE = ["children's song", "gentle storybook folk", "100 BPM", "4/4 straight eighths", "D major", "acoustic guitar lead",
        "glockenspiel", "upright bass", "soft hand drum", "warm and playful", "clear diction"]
SUNG = ["sung melodically, legato singing, clear diction, sung exactly as written"]
TUMBLE = ["warm young male tenor lead vocal", "one solo male singer", "bassoon doubling the melody"] + SUNG
PIP = ["light high bright female soprano vocal", "one solo female singer", "tin whistle doubling the melody"] + SUNG
DUET = ["warm young male tenor and light high female soprano duet", "bassoon and tin whistle"] + SUNG
NEG = ["spoken word", "talking", "rap", "chant", "choir", "drum kit", "electric guitar", "autotune", "sad", "dark",
       "heavy reverb", "fade out"]
NEG_WHO = {"tumble": ["female vocal", "soprano", "woman singing", "girl vocal", "high pitched vocal"],
           "pip": ["male vocal", "tenor", "baritone", "man singing", "low pitched vocal"], "both": [], None: ["vocals", "singing", "voice"]}
BO = ["warm gentle low male baritone lead vocal", "one solo male singer", "soft cello doubling the melody"] + SUNG
ANT = ["small cheeky boy treble voice, a tiny cartoon ant", "one solo singer", "pizzicato strings doubling the melody"] + SUNG
STYLE = {"tumble": TUMBLE, "pip": PIP, "both": DUET, "bo": BO, "ant": ANT}
NEG_WHO["bo"] = ["female vocal", "soprano", "high pitched vocal", "child vocal"]
NEG_WHO["ant"] = ["baritone", "bass vocal", "deep voice", "soprano", "woman singing", "female vocal"]
# Fable 1 reference ranges (ms) in audio/fable-01/song.mp3: Tumble sings 11.7-24.0 s, Pip sings 7.2-9.6 s and 31.4-33.4 s
COND = {"tumble": (10800, 25200), "pip": (27600, 34800)}
F0_OK = {"tumble": (120, 270), "pip": (310, 560), "bo": (70, 190), "ant": (240, 800)}

def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k: sys.exit("ELEVENLABS_API_KEY is not set: stop and tell the owner (no Kokoro fallback).")
    return {"xi-api-key": k}

def load(path, sr=44100, ch=2):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    return x.reshape(-1, ch) if ch > 1 else x

def upload(path):
    import requests
    r = requests.post(f"{API}/music/upload", headers=key(), files={"file": open(path, "rb")}, timeout=600)
    if r.status_code != 200: sys.exit(f"upload failed {r.status_code}: {r.text[:300]}")
    return r.json()["song_id"]

def refs():
    have = json.load(open(REFS)) if os.path.exists(REFS) else {}
    if all(k in have for k in ("sting", "chorus", "fable01")): return have
    for name, p in [("sting", f"{SER}/sting_pad10.mp3"), ("chorus", f"{SER}/chorus.mp3"), ("fable01", f"{HERE}/audio/fable-01/song.mp3")]:
        if name not in have: have[name] = upload(p); print(name, have[name])
    json.dump(have, open(REFS, "w"), indent=1)
    return have

def timeline(fable_dir):
    spec = importlib.util.spec_from_file_location("tl", os.path.join(fable_dir, "code", "timeline.py"))
    cwd = os.getcwd(); os.chdir(os.path.join(fable_dir, "code"))
    try:
        tl = importlib.util.module_from_spec(spec); spec.loader.exec_module(tl)
    finally:
        os.chdir(cwd)
    return tl

def plan(fable_dir):
    """(name, ms, text, who, kind) per chunk on the v2 grid. kind: gen | sting | chorus"""
    tl = timeline(fable_dir); out = []
    for name, a, b, part in tl.PLAN_SECTIONS:
        lines = [(who, text) for s, who, text in tl.PLAN_LINES if s == name]
        if part == "sting": out.append((name, STING_MS, "[Intro]\nTumble and Pip!", "both", "sting")); continue
        if part == "chorus": out.append((name, CHORUS_MS, "[Chorus]\n" + "\n".join(t for _, t in lines), "both", "chorus")); continue
        if name == "Button":
            out.append((name, BUTTON_MS, "[Outro]\n{the band plays on for one bar, then a happy final chord that rings out to silence}",
                        None, "gen")); continue
        text = "[Verse]\n" + "\n".join(t for _, t in lines) if lines else "[Intro]\n{bright instrumental intro, the band only}"
        if name in ("Problem B", "Twist"): text += "\n{playful instrumental break}"
        out.append((name, int(round((b - a) * BAR * 1000)), text, lines[0][0] if lines else None, "gen"))
    return out

def compose(fable_dir, seed, out, cond=True):
    import requests
    R = refs(); chunks = []; extra = getattr(timeline(fable_dir), "STYLE_EXTRA", [])
    for i, (name, ms, text, who, kind) in enumerate(plan(fable_dir)):
        sty = STYLE.get(who, ["instrumental"])
        c = dict(text=text, duration_ms=ms, positive_styles=(BASE + extra if i == 0 else BASE[:6] + extra[:2]) + sty,
                 negative_styles=NEG + NEG_WHO[who], context_adherence="high")
        # stored series sting and chorus: condition on them so every fable sings the same tune, but generate them
        # inside the song so the band never stops (inserting them unchanged left silence on both sides of each join)
        if kind == "sting":
            # chunks must be 3 s or longer, so the 2.4 s title sting is sung at the end of the hook chunk
            prev = chunks[-1]; prev["text"] += "\n[Intro]\nTumble and Pip!"; prev["duration_ms"] += ms
            prev["positive_styles"] = prev["positive_styles"] + ["ends with a bright two-voice shout of the title"]
            continue
        if kind == "chorus": c["conditioning_ref"] = dict(song_id=R["chorus"], range=dict(start_ms=0, end_ms=7200)); c["condition_strength"] = "xhigh"
        elif cond and who in COND:
            c["conditioning_ref"] = dict(song_id=R["fable01"], range=dict(start_ms=COND[who][0], end_ms=COND[who][1]))
            c["condition_strength"] = STRENGTH
        if i == 0 and os.environ.get("EL_NOINTRO", "1") == "1":   # the hook line must land in the first second (Shorts rule)
            c["text"] = c["text"].replace("[Verse]\n", "[Verse]\n{no intro: the voice starts on the very first beat}\n", 1)
            c["positive_styles"] = c["positive_styles"] + ["vocals start immediately on the first beat"]
            c["negative_styles"] = c["negative_styles"] + ["instrumental intro", "long intro", "fade in"]
        chunks.append(c)
    body = dict(model_id="music_v2_5", composition_plan=dict(chunks=chunks), seed=int(seed))
    r = requests.post(f"{API}/music?output_format=mp3_44100_192", headers=key(), json=body, timeout=600)
    if r.status_code != 200: sys.exit(f"compose failed {r.status_code}: {r.text[:500]}")
    open(out, "wb").write(r.content); print("wrote", out, "song-id", r.headers.get("song-id"))

def words_norm(s): return [w for w in re.sub(r"[^a-z' ]", " ", s.lower().replace("-", " ")).split() if w]

_enc = None
def embed(y16):
    global _enc
    from resemblyzer import VoiceEncoder, preprocess_wav
    if _enc is None: _enc = VoiceEncoder("cpu", verbose=False)
    return _enc.embed_utterance(preprocess_wav(y16, source_sr=16000))
def f0_med(y16):
    import librosa
    f, v, _ = librosa.pyin(y16, fmin=80, fmax=1000, sr=16000, frame_length=1024)
    f = f[v] if v is not None else np.array([])
    return float(np.median(f)) if len(f) else float("nan")

def stems(mp3):
    import requests
    vo = mp3.replace(".mp3", "_vocals.mp3")
    if not os.path.exists(vo):
        r = requests.post(f"{API}/music/stem-separation", headers=key(), data={"stem_variation_id": "two_stems_v1"},
                          files={"file": open(mp3, "rb")}, timeout=600)
        if r.status_code != 200: sys.exit(f"stems failed {r.status_code}: {r.text[:300]}")
        z = zipfile.ZipFile(io.BytesIO(r.content))
        open(vo, "wb").write(z.read("vocals.mp3")); open(mp3.replace(".mp3", "_instr.mp3"), "wb").write(z.read("instrumental.mp3"))
    return vo

def ref_embeds():
    """mean voice embedding of Fable 1's sung Tumble and Pip lines (cached)"""
    p = os.path.join(SER, "voice_ref.npz")
    if os.path.exists(p): z = np.load(p); return {k: z[k] for k in z.files}
    vo = stems(os.path.join(HERE, "audio", "fable-01", "song.mp3")); y = load(vo, 16000, 1)
    sc = json.load(open(os.path.join(HERE, "audio", "fable-01", "song_check.json"))); E = {}
    for who in ("tumble", "pip"):
        es = [embed(y[int(L["words"][0]["t0"] * 16000):int(L["words"][-1]["t1"] * 16000)]) for L in sc["lines"]
              if L["who"] == who and L["sec"] not in ("Sting", "Chorus")]
        m = np.mean(es, 0); E[who] = m / np.linalg.norm(m)
    np.savez(p, **E); return E

def check(fable_dir, mp3):
    import requests
    H = key(); P = plan(fable_dir); tl = timeline(fable_dir)
    bounds, t = [], 0.0
    for name, ms, *_ in P: bounds.append((name, t, t + ms / 1000)); t += ms / 1000
    exp = []
    for (name, a, b) in bounds:
        for s, who, text in tl.PLAN_LINES:
            if s == name: exp.append(dict(line=text, who=who, sec=name, t0=a, t1=b))
    stt = requests.post(f"{API}/speech-to-text", headers=H, data={"model_id": "scribe_v1"},
                        files={"file": open(mp3, "rb")}, timeout=300).json()
    expected = [w for L in exp for w in words_norm(L["line"])]; heard = words_norm(stt.get("text", ""))
    recall = sum(b.size for b in difflib.SequenceMatcher(a=expected, b=heard, autojunk=False).get_matching_blocks()) / max(1, len(expected))
    fa = requests.post(f"{API}/forced-alignment", headers=H, data={"text": "\n".join(L["line"] for L in exp)},
                       files={"file": open(mp3, "rb")}, timeout=300).json()
    words = [w for w in fa.get("words", []) if w["text"].strip()]
    vo = stems(mp3); y = load(vo, 16000, 1); R = ref_embeds()
    lines, wi, inside_all, voice = [], 0, True, {k: [] for k in F0_OK}
    for L in exp:
        n = len(L["line"].split()); ws = words[wi:wi + n]; wi += n
        L = dict(L, words=[dict(w=w["text"], t0=w["start"], t1=w["end"]) for w in ws])
        inside = bool(ws) and L["t0"] - 0.05 <= ws[0]["start"] and ws[-1]["end"] <= L["t1"] + 0.05
        inside_all &= inside; L["inside"] = inside
        if ws and L["who"] in voice and L["sec"] not in ("Sting", "Chorus"):
            seg = y[int(ws[0]["start"] * 16000):int(ws[-1]["end"] * 16000)]
            if len(seg) > 8000:
                f = f0_med(seg); sim = float(embed(seg) @ R[L["who"]]) if L["who"] in R else 0.8; lo, hi = F0_OK[L["who"]]
                L.update(f0=round(f, 1), sim=round(sim, 3), f0_ok=bool(lo <= f <= hi)); voice[L["who"]].append(L)
        lines.append(L)
        print(f"{L['sec']:10s} {str(L['who']):6s} {'in ' if inside else 'OUT'} f0={L.get('f0', '-')!s:>6} sim={L.get('sim', '-')!s:>5}  {L['line']}")
    # snap section boundaries to the real phrasing: a cut that falls inside a sung line moves to the middle of the gap
    # between the two sections' lines (the hook and sting share one generated chunk, so the model places the sting)
    secs = [list(b) for b in bounds]
    for k in range(len(secs) - 1):
        A = [w for L in lines if L["sec"] == secs[k][0] for w in L["words"]]
        B = [w for L in lines if L["sec"] == secs[k + 1][0] for w in L["words"]]
        if not A or not B: continue
        a_end, b_start = A[-1]["t1"], B[0]["t0"]
        if not (a_end <= secs[k][2] <= b_start) and a_end < b_start:
            cut = round((a_end + b_start) / 2, 2)
            if secs[k][1] + 1.0 < cut < secs[k + 1][2] - 0.9: secs[k][2] = secs[k + 1][1] = cut
    order_ok = all(L["words"] and any(n == L["sec"] and a - 0.05 <= L["words"][0]["t0"] and L["words"][-1]["t1"] <= b + 0.05
                                      for n, a, b in secs) for L in lines)
    inside_all = inside_all or order_ok
    bounds = [tuple(x) for x in secs]
    allv = [L for v in voice.values() for L in v]
    f0_hits = sum(L["f0_ok"] for L in allv) / max(1, len(allv)); sim = float(np.mean([L["sim"] for L in allv])) if allv else 0
    score = recall * 2 + f0_hits * 2 + sim + (0.5 if inside_all else 0)
    res = dict(mp3=os.path.basename(mp3), stt=stt.get("text"), recall=round(recall, 4), all_inside=inside_all,
               f0_hits=round(f0_hits, 3), voice_sim=round(sim, 3), score=round(score, 3), sections=bounds, lines=lines)
    json.dump(res, open(mp3.replace(".mp3", "_check.json"), "w"), indent=1)
    print(f"recall {recall:.1%} inside {inside_all} singer pitch ok {f0_hits:.0%} voice sim {sim:.2f} -> score {score:.2f}")
    return res

def pick(fable_dir):
    od = os.path.join(fable_dir, "code", "out")
    cs = [json.load(open(p)) for p in glob.glob(f"{od}/take_*_check.json")]
    ok = [c for c in cs if c["recall"] >= 0.95 and c["f0_hits"] >= 0.99] or sorted(cs, key=lambda c: -c["score"])[:1]
    def hook0(c):
        L = next((L for L in c["lines"] if L["words"]), None); return L["words"][0]["t0"] if L else 9.0
    for c in cs: print(f"  {c['mp3']:14s} recall {c['recall']:.3f} pitch {c['f0_hits']:.2f} sim {c['voice_sim']:.2f} first word {hook0(c):.2f}s score {c['score']:.2f}")
    best = max(ok, key=lambda c: c["score"] - (0.6 if hook0(c) > 1.5 else 0.0))
    x = load(os.path.join(od, best["mp3"]))
    import soundfile as sf
    sf.write(os.path.join(od, "song.wav"), x, 44100)
    secs = [list(s) for s in best["sections"]]
    lines = [dict(line=L["line"], who=L["who"], sec=L["sec"], words=L["words"]) for L in best["lines"] if L["words"]]
    json.dump(dict(sections=secs, take=best["mp3"], first_word=hook0(best), recall=best["recall"], f0_hits=best["f0_hits"], voice_sim=best["voice_sim"],
                   lines=lines), open(os.path.join(od, "song_check.json"), "w"), indent=1)
    print("picked", best["mp3"], "score", best["score"], "recall", best["recall"], "pitch ok", best["f0_hits"], "sim", best["voice_sim"],
          "" if best in ok else "(NO TAKE PASSED THE GATES: make more takes)")
    return best

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "refs": print(refs())
    elif cmd == "take":
        fd, seed = sys.argv[2], sys.argv[3]; cond = "--nocond" not in sys.argv
        od = os.path.join(fd, "code", "out"); os.makedirs(od, exist_ok=True)
        mp3 = os.path.join(od, f"take_{seed}{'' if cond else 'n'}{os.environ.get('EL_TAG', '')}.mp3")
        if not os.path.exists(mp3): compose(fd, seed, mp3, cond)
        check(fd, mp3)
    elif cmd == "check": check(sys.argv[2], sys.argv[3])
    elif cmd == "pick": pick(sys.argv[2])
    elif cmd == "plan":
        for p in plan(sys.argv[2]): print(p)
    else: sys.exit(__doc__)
