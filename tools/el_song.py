"""Generate the Episode 2 song with the ElevenLabs Music API (composition plan, music_v2_5), then check it:
speech-to-text vs lyrics, forced-alignment word timings, duet pitch split, words inside their sections.
Key comes from the ELEVENLABS_API_KEY environment variable; it is never written to disk."""
import os, sys, json, re, subprocess, requests, numpy as np
KEY = os.environ["ELEVENLABS_API_KEY"]
H = {"xi-api-key": KEY}
API = "https://api.elevenlabs.io/v1"

BASE = ["children's song", "bouncy 6/8 jig", "88 BPM", "G major", "tuba oom-pah bass", "tin whistle", "toy piano",
        "pizzicato strings", "playful cartoon", "clear diction", "male and female duet vocals"]
NEG = ["drum kit", "electric guitar", "autotune", "sad", "dark", "rap", "heavy reverb", "choir"]
TUMBLE = ["bright friendly young male lead vocal", "clear diction", "sung exactly as written"]
BIGV = ["deep slow booming male vocal", "big heavy tuba", "clear diction", "sung exactly as written"]
PIPV = ["high quick light female vocal", "cute", "tin whistle", "clear diction", "sung exactly as written"]
ROUNDS = [("A big red apple!", "Tiny berry!"), ("A big leaf fan, whoosh!", "Tiny leaf fan!"),
          ("A big tree stump seat!", "Tiny mushroom!"), ("Big feet go stomp, stomp!", "Small feet go hop!")]
SECTIONS = [("Intro", 4090, "[Intro]", [], ["instrumental"]),
            ("Chorus", 5450, "[Chorus]\nBig and small, big and small!\nLet's go find them all!", ["tumble", "tumble"], TUMBLE)]
for k, (big, small) in enumerate(ROUNDS):
    SECTIONS.append((f"Round {k + 1} big", 3410, f"[Verse]\n{big}", ["tumble"], BIGV))
    SECTIONS.append((f"Round {k + 1} small", 3410, f"[Verse]\n{small}\n{{instrumental break}}", ["pip"], PIPV + ["playful instrumental break after the line"]))
SECTIONS += [("Finale A", 3410, "[Outro]\nBig and small, big and small!", ["tumble"], TUMBLE),
             ("Finale B", 4770, "[Outro]\nBest friends, big and small!\nBye-bye, friends!", ["pip", "tumble"], ["male and female duet vocals", "clear diction", "sung exactly as written", "warm ending"])]

def lyrics_of(text):
    return [l for l in text.split("\n") if l and not l.startswith("[") and not l.startswith("{")]

def compose(seed=None):
    chunks = []
    for i, (name, ms, text, _, sty) in enumerate(SECTIONS):
        pos = (BASE + sty) if i == 0 else (BASE[:5] + sty)
        c = dict(text=text, duration_ms=ms, positive_styles=pos, negative_styles=NEG + (["vocals", "singing", "voice"] if name == "Intro" else []))
        chunks.append(c)
    body = dict(model_id="music_v2_5", composition_plan=dict(chunks=chunks))
    if seed is not None: body["seed"] = seed
    r = requests.post(f"{API}/music?output_format=mp3_44100_192", headers=H, json=body, timeout=300)
    if r.status_code != 200: sys.exit(f"compose failed {r.status_code}: {r.text[:400]}")
    open(OUT, "wb").write(r.content)
    return r.headers.get("song-id")

def words_norm(s): return [w for w in re.sub(r"[^a-z' ]", " ", s.lower().replace("-", " ")).split() if w]

def check():
    exp_lines = []; t0 = 0.0; bounds = []
    for (name, ms, text, who, _) in SECTIONS:
        for li, line in enumerate(lyrics_of(text)): exp_lines.append(dict(line=line, who=who[li], sec=name, t0=t0, t1=t0 + ms / 1000))
        bounds.append((name, t0, t0 + ms / 1000)); t0 += ms / 1000
    r = requests.post(f"{API}/speech-to-text", headers=H, data={"model_id": "scribe_v1"}, files={"file": open(OUT, "rb")}, timeout=300)
    stt = r.json(); heard = words_norm(stt.get("text", ""))
    expected = [w for l in exp_lines for w in words_norm(l["line"])]
    # word recall via LCS
    import difflib
    sm = difflib.SequenceMatcher(a=expected, b=heard, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    full_text = "\n".join(l["line"] for l in exp_lines)
    r = requests.post(f"{API}/forced-alignment", headers=H, data={"text": full_text}, files={"file": open(OUT, "rb")}, timeout=300)
    fa = r.json()
    words = [w for w in fa["words"] if w["text"].strip()]
    # map aligned words back to lines
    out, wi = [], 0
    for L in exp_lines:
        n = len(L["line"].split())
        ws = words[wi:wi + n]; wi += n
        out.append(dict(L, words=[dict(w=w["text"], t0=w["start"], t1=w["end"], loss=w.get("loss")) for w in ws]))
    json.dump(dict(stt=stt.get("text"), recall=matched / len(expected), lines=out, sections=bounds, align_loss=fa.get("loss")),
              open(OUT.replace(".mp3", "_check.json"), "w"), indent=1)
    print("STT:", stt.get("text"))
    print(f"lyric word recall {matched}/{len(expected)} = {matched / len(expected):.0%}; alignment loss {fa.get('loss'):.3f}")
    for L in out:
        a, b = L["words"][0]["t0"], L["words"][-1]["t1"]
        inside = L["t0"] - 0.05 <= a and b <= L["t1"] + 0.05
        print(f"{L['sec']:8s} {L['who']:6s} {a:6.2f}-{b:6.2f} {'in section' if inside else 'OUTSIDE ' + str((round(L['t0'],2), round(L['t1'],2)))}  {L['line']}")

OUT = sys.argv[2] if len(sys.argv) > 2 else "song.mp3"
if __name__ == "__main__":
    if sys.argv[1] == "compose":
        print("song-id", compose(int(sys.argv[3]) if len(sys.argv) > 3 else None))
    check()
