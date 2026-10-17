"""Batch 01 song tool (ElevenLabs Music, music_v2_5). Untested against the live API: written in a session without
ELEVENLABS_API_KEY or network access to api.elevenlabs.io. It follows tools/el_song.py (Episode 2), which did work.

The key comes from ELEVENLABS_API_KEY only. Never print it or write it to disk.

One sound for the batch, from three parts (see plan.md, "Song plan"):
  python3 el_batch.py sting  <seed>          -> series_audio/sting_<seed>.mp3     (once per batch; owner picks one)
  python3 el_batch.py chorus <seed>          -> series_audio/chorus_<seed>.mp3    (once per batch; owner picks one)
  python3 el_batch.py verse  <fable_dir> <seed>  -> <fable_dir>/code/out/verse_<seed>.mp3 + verse_<seed>_check.json
  python3 el_batch.py check  <mp3> <part> [<fable_dir>]  -> re-run speech-to-text and forced alignment on a take
  python3 el_batch.py assemble <fable_dir> <verse.mp3> <sting.mp3> <chorus.mp3>
        -> <fable_dir>/code/out/song.wav and out/song_check.json (the timeline format render.py reads)

Takes: make 3 per part with different seeds, 2 requests at a time. Keep a take with speech-to-text recall of 95% or
more and every line inside its section. Joins are cut on bar lines; a join is accepted only when the instrumental
chroma on both sides matches at 0.9 or more (ENGINE.md rule), otherwise regenerate the verse take."""
import os, sys, json, re, difflib, subprocess, importlib.util
import numpy as np

API = "https://api.elevenlabs.io/v1"
HERE = os.path.dirname(os.path.abspath(__file__))
SERIES = os.path.join(HERE, "series_audio")

# ---- series sound (same words every fable) ----
BASE = ["children's song", "gentle storybook folk", "100 BPM", "4/4 straight eighths", "D major", "acoustic guitar lead",
        "glockenspiel", "upright bass", "soft hand drum", "warm and playful", "clear diction"]
TUMBLE = ["warm young male tenor lead vocal", "one solo singer", "bassoon doubling the melody",
          "sung melodically, legato singing, clear diction, sung exactly as written"]
PIP = ["light high female soprano vocal", "one solo singer", "tin whistle doubling the melody",
       "sung melodically, legato singing, clear diction, sung exactly as written"]
DUET = ["warm young male tenor and light high female soprano duet", "bassoon and tin whistle",
        "sung melodically, legato singing, clear diction, sung exactly as written"]
NEG = ["spoken word", "talking", "rap", "chant", "choir", "drum kit", "electric guitar", "autotune", "sad", "dark", "heavy reverb"]
VOICE = {"tumble": TUMBLE, "pip": PIP, "both": DUET}

STING = [("Sting", 3000, "[Intro]\nTumble and Pip!", "both")]                     # the first 2.4 s bar is kept
CHORUS = [("Chorus", 7200, "[Chorus]\nBig or small, short or tall,\nfriends help friends, that's best of all!", "both"),
          ("Ring-out", 3000, "[Outro]\n{instrumental ending}", None)]

def fable_sections(fable_dir):
    """verse plan from the fable's timeline.py: every section except the stored sting; the chorus stays in the plan
    (with its lyrics) so the verse take leads into it naturally and the join can be matched."""
    spec = importlib.util.spec_from_file_location("tl", os.path.join(fable_dir, "code", "timeline.py"))
    cwd = os.getcwd(); os.chdir(os.path.join(fable_dir, "code"))
    try:
        tl = importlib.util.module_from_spec(spec); spec.loader.exec_module(tl)
    finally:
        os.chdir(cwd)
    out = []
    for name, a, b, part in tl.PLAN_SECTIONS:
        if part == "sting": continue
        ms = int(round((b - a) * tl.BAR * 1000))
        lines = [(who, text) for s, who, text in tl.PLAN_LINES if s == name]
        text = f"[{'Chorus' if part == 'chorus' else 'Verse'}]\n" + "\n".join(t for _, t in lines)
        who = lines[0][0] if lines else None
        if name in ("Problem B", "Twist"): text += "\n{playful instrumental break}"
        if name == "Button": text = "[Outro]\n{instrumental ending, happy final chord}"; who = None
        out.append((name, max(ms, 3000), text, who))
    return out, tl

def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    if not k: sys.exit("ELEVENLABS_API_KEY is not set: stop, queue nothing, tell the owner (no Kokoro fallback).")
    return {"xi-api-key": k}

def compose(sections, out, seed):
    import requests
    chunks = []
    for i, (name, ms, text, who) in enumerate(sections):
        sty = VOICE.get(who, ["instrumental"])
        pos = (BASE + sty) if i == 0 else (BASE[:6] + sty)
        neg = NEG + (["vocals", "singing", "voice"] if who is None else [])
        chunks.append(dict(text=text, duration_ms=ms, positive_styles=pos, negative_styles=neg))
    body = dict(model_id="music_v2_5", composition_plan=dict(chunks=chunks), seed=int(seed))
    r = requests.post(f"{API}/music?output_format=mp3_44100_128", headers=key(), json=body, timeout=300)
    if r.status_code != 200: sys.exit(f"compose failed {r.status_code}: {r.text[:400]}")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "wb").write(r.content)
    print("wrote", out, "song-id", r.headers.get("song-id"))

def words_norm(s): return [w for w in re.sub(r"[^a-z' ]", " ", s.lower().replace("-", " ")).split() if w]
def lyric_lines(text): return [l for l in text.split("\n") if l and not l.startswith(("[", "{"))]

def check(mp3, sections):
    import requests
    H = key()
    exp, t0, bounds = [], 0.0, []
    for (name, ms, text, who) in sections:
        for line in lyric_lines(text): exp.append(dict(line=line, who=who, sec=name, t0=t0, t1=t0 + ms / 1000))
        bounds.append((name, t0, t0 + ms / 1000)); t0 += ms / 1000
    stt = requests.post(f"{API}/speech-to-text", headers=H, data={"model_id": "scribe_v1", "diarize": "true"},
                        files={"file": open(mp3, "rb")}, timeout=300).json()
    heard = words_norm(stt.get("text", ""))
    expected = [w for l in exp for w in words_norm(l["line"])]
    sm = difflib.SequenceMatcher(a=expected, b=heard, autojunk=False)
    recall = sum(b.size for b in sm.get_matching_blocks()) / max(1, len(expected))
    fa = requests.post(f"{API}/forced-alignment", headers=H, data={"text": "\n".join(l["line"] for l in exp)},
                       files={"file": open(mp3, "rb")}, timeout=300).json()
    words = [w for w in fa.get("words", []) if w["text"].strip()]
    lines, wi, ok = [], 0, True
    for L in exp:
        n = len(L["line"].split()); ws = words[wi:wi + n]; wi += n
        L = dict(L, words=[dict(w=w["text"], t0=w["start"], t1=w["end"]) for w in ws]); lines.append(L)
        inside = ws and L["t0"] - 0.05 <= ws[0]["start"] and ws[-1]["end"] <= L["t1"] + 0.05
        ok &= bool(inside)
        print(f"{L['sec']:10s} {str(L['who']):6s} {'in section' if inside else 'OUTSIDE'}  {L['line']}")
    speakers = sorted({w.get("speaker_id") for w in stt.get("words", []) if w.get("speaker_id")})
    res = dict(stt=stt.get("text"), recall=recall, speakers=speakers, lines=lines, sections=bounds,
               align_loss=fa.get("loss"), all_inside=ok)
    json.dump(res, open(mp3.replace(".mp3", "_check.json"), "w"), indent=1)
    print(f"recall {recall:.1%}  speakers {speakers}  all lines inside: {ok}  -> {'KEEP' if recall >= 0.95 and ok else 'REJECT'}")
    return res

# ---- assembly ----
def load(path, sr=44100):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def chroma_sim(a, b, sr=44100):
    """cosine similarity of 12-bin chroma (simple FFT fold) of two short instrumental windows"""
    def chroma(x):
        x = x.mean(1); X = np.abs(np.fft.rfft(x * np.hanning(len(x)))); f = np.fft.rfftfreq(len(x), 1 / sr)
        m = (f > 60) & (f < 4000); pc = np.round(12 * np.log2(f[m] / 440.0)).astype(int) % 12
        c = np.bincount(pc, weights=X[m], minlength=12); return c / (np.linalg.norm(c) + 1e-9)
    return float(chroma(a) @ chroma(b))
def instrumental(mp3):
    """instrumental stem of a take (/v1/music/stem-separation, two_stems_v1), cached next to it as *_instr.mp3"""
    out = mp3.replace(".mp3", "_instr.mp3")
    if not os.path.exists(out):
        import requests, zipfile, io
        r = requests.post(f"{API}/music/stem-separation", headers=key(), data={"stem_variation_id": "two_stems_v1"},
                          files={"file": open(mp3, "rb")}, timeout=300)
        if r.status_code != 200: sys.exit(f"stem separation failed {r.status_code}: {r.text[:400]}")
        open(out, "wb").write(zipfile.ZipFile(io.BytesIO(r.content)).read("instrumental.mp3"))
    return load(out)
def join_sim(A, ea, B, sb, sr=44100, w=0.6):
    """instrumental chroma 'under both spots': B's head vs what A itself plays after the cut, and A's tail vs what
    precedes B's head in its own take. Uninterrupted audio scores 1.0; returns the lower of the two that exist."""
    if sb < 0: ea, sb = ea - sb, 0.0                     # B delayed: compare from B's first sample
    i, j, n = int(ea * sr), int(sb * sr), int(w * sr)
    sims = []
    if i + n <= len(A) and j + n <= len(B): sims.append(chroma_sim(A[i:i + n], B[j:j + n]))
    if i >= n and j >= n: sims.append(chroma_sim(A[i - n:i], B[j - n:j]))
    return min(sims)
def beat_offset(own, stored, sr=44100, hop=441, max_ms=150):
    """seconds to skip into `stored` so its onsets line up with `own` (negative: delay it)"""
    def env(x):
        x = x.mean(1); n = len(x) // hop; fr = x[:n * hop].reshape(n, hop)
        S = np.abs(np.fft.rfft(fr * np.hanning(hop), axis=1)); f = np.maximum(np.diff(np.log1p(S), axis=0), 0).sum(1)
        return f - f.mean()
    a, b = env(own), env(stored); L = min(len(a), len(b)); m = int(max_ms / 1000 * sr / hop)
    cc = {l: np.dot(a[max(0, l):L + min(0, l)], b[max(0, -l):L - max(0, l)]) for l in range(-m, m + 1)}
    return -max(cc, key=cc.get) * hop / sr
def assemble(fable_dir, verse_mp3, sting_mp3, chorus_mp3, sr=44100):
    secs, tl = fable_sections(fable_dir)
    bar = tl.BAR; xf = int(0.03 * sr)
    v, s, c = load(verse_mp3), load(sting_mp3), load(chorus_mp3)
    vi, si, ci = instrumental(verse_mp3), instrumental(sting_mp3), instrumental(chorus_mp3)
    vchk = json.load(open(verse_mp3.replace(".mp3", "_check.json")))
    schk = json.load(open(sting_mp3.replace(".mp3", "_check.json")))
    cchk = json.load(open(chorus_mp3.replace(".mp3", "_check.json")))
    # verse take timeline: Hook | Setup..Moral | Chorus(lyric, replaced) | Button
    vb = {n: (a, b) for n, a, b in vchk["sections"]}
    cut1 = vb["Hook"][1]; cut2 = vb["Chorus"][0]; cut3 = vb["Button"][0]
    # the stored chorus lands up to ~80 ms off the verse's beat: line it up with the verse take's own chorus
    c0 = beat_offset(v[int(cut2 * sr): int((cut2 + 3 * bar) * sr)], c[: int(3 * bar * sr)], sr)
    i0 = int(round(c0 * sr)); pad = max(0, -i0)
    cp = np.concatenate([np.zeros((pad, 2), np.float32), c[max(0, i0): max(0, i0) + int(3 * bar * sr) - pad]])
    # half-beat equal-power crossfade from the verse's own chorus into the stored one (in time with each other)
    nx = pad + int(0.3 * sr); g = np.zeros(nx); g[pad:] = np.linspace(0, np.pi / 2, nx - pad)
    cp[:nx] = v[int(cut2 * sr): int(cut2 * sr) + nx] * np.cos(g)[:, None] + cp[:nx] * np.sin(g)[:, None]
    print(f"chorus aligned to the verse beat: offset {c0 * 1000:+.0f} ms, crossfade 0.3 s")
    pieces = [("verse", v[: int(cut1 * sr)]), ("sting", s[: int(bar * sr)]), ("verse", v[int(cut1 * sr): int(cut2 * sr)]),
              ("chorus", cp), ("verse", v[int(cut3 * sr): int((cut3 + bar) * sr)])]
    # (instrumental, start, end) of each piece in its own take, for the join check
    spans = [(vi, 0, cut1), (si, 0, bar), (vi, cut1, cut2), (ci, c0, c0 + 3 * bar), (vi, cut3, cut3 + bar)]
    joins = []
    for (na, _), (nb, _), (A, _, ea), (B, sb, _) in zip(pieces[:-1], pieces[1:], spans[:-1], spans[1:]):
        sim = join_sim(A, ea, B, sb, sr)
        joins.append(dict(join=f"{na}->{nb}", chroma=round(sim, 3), ok=sim >= 0.9))
        print(f"join {na} -> {nb}: chroma similarity {sim:.2f} {'ok' if sim >= 0.9 else 'TOO LOW: regenerate the verse take'}")
    out = pieces[0][1]
    for name, p in pieces[1:]:
        if name == "chorus": out = np.concatenate([out, p]); continue      # already crossfaded above
        ramp = np.linspace(0, 1, xf)[:, None]
        out = np.concatenate([out[:-xf], out[-xf:] * (1 - ramp) + p[:xf] * ramp, p[xf:]])
    od = os.path.join(fable_dir, "code", "out"); os.makedirs(od, exist_ok=True)
    import soundfile as sf
    sf.write(os.path.join(od, "song.wav"), out, sr)
    # word times on the final timeline
    sh_sting, sh_chorus = bar, 3 * bar
    def shift(t, part):
        if part == "verse":
            if t < cut1: return t
            if t < cut2: return t + sh_sting
            return t - cut3 + (cut2 + sh_sting + sh_chorus)
        if part == "sting": return t + cut1
        return t - c0 + cut2 + sh_sting
    lines = []
    for L in vchk["lines"]:
        if L["sec"] == "Chorus": continue
        lines.append(dict(L, words=[dict(w, t0=shift(w["t0"], "verse"), t1=shift(w["t1"], "verse")) for w in L["words"]]))
    for L in schk["lines"]: lines.append(dict(L, sec="Sting", words=[dict(w, t0=shift(w["t0"], "sting"), t1=shift(w["t1"], "sting")) for w in L["words"]]))
    for L in cchk["lines"]:
        if L["sec"] == "Chorus": lines.append(dict(L, words=[dict(w, t0=shift(w["t0"], "chorus"), t1=shift(w["t1"], "chorus")) for w in L["words"]]))
    lines.sort(key=lambda L: L["words"][0]["t0"])
    sections = [(n, a * bar, b * bar) for n, a, b, _ in tl.PLAN_SECTIONS]
    json.dump(dict(sections=sections, joins=joins, lines=[dict(line=L["line"], who=L["who"], sec=L["sec"], words=L["words"]) for L in lines]),
              open(os.path.join(od, "song_check.json"), "w"), indent=1)
    print("wrote song.wav and song_check.json; next: TTS gag lines (eleven_v3, cast voices), SFX, mix at -14 LUFS, full-mix recall")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sting": compose(STING, os.path.join(SERIES, f"sting_{sys.argv[2]}.mp3"), sys.argv[2]); check(os.path.join(SERIES, f"sting_{sys.argv[2]}.mp3"), STING)
    elif cmd == "chorus": compose(CHORUS, os.path.join(SERIES, f"chorus_{sys.argv[2]}.mp3"), sys.argv[2]); check(os.path.join(SERIES, f"chorus_{sys.argv[2]}.mp3"), CHORUS)
    elif cmd == "verse":
        secs, _ = fable_sections(sys.argv[2]); out = os.path.join(sys.argv[2], "code", "out", f"verse_{sys.argv[3]}.mp3")
        compose(secs, out, sys.argv[3]); check(out, secs)
    elif cmd == "check":
        part = sys.argv[3]
        secs = STING if part == "sting" else CHORUS if part == "chorus" else fable_sections(sys.argv[4])[0]
        check(sys.argv[2], secs)
    elif cmd == "assemble": assemble(*sys.argv[2:6])
    elif cmd == "plan":                                                      # print a fable's verse plan (no API call)
        for s in fable_sections(sys.argv[2])[0]: print(s)
    else: sys.exit(__doc__)
