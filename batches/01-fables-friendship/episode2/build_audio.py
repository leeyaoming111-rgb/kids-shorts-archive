"""Episode v2 scene audio: TTS every line in the cast voices, align the words, lay the scene out in time.

  python3 build_audio.py <scene> [<scene> ...] | all
Writes audio/<scene>.json (the timeline the renderer reads) and audio/<scene>_dialogue.wav (voices only; the music
bed is added in assemble.py). Clips are cached in audio/clips/ by a hash of who + tags + text, so re-running after a
script edit only re-voices the lines that changed. Key: ELEVENLABS_API_KEY only (max 2 concurrent requests)."""
import os, sys, json, re, hashlib, time
import numpy as np, soundfile as sf, requests
HERE = os.path.dirname(os.path.abspath(__file__)); BATCH = os.path.dirname(HERE)
sys.path.insert(0, BATCH); sys.path.insert(0, HERE)
import el_voice2 as V
import script as S
SR = 44100
AUD = os.path.join(HERE, "audio"); CLIPS = os.path.join(AUD, "clips"); os.makedirs(CLIPS, exist_ok=True)
SONGS = {"dance": os.path.join(HERE, "songs", "dance", "code", "out"), "recap_song": os.path.join(HERE, "songs", "recap", "code", "out")}
WHO = {"T": "tumble", "P": "pip", "B": "both"}

def plain(text): return re.sub(r"\s+", " ", text).strip()
def clip(who, text, tags):
    h = hashlib.sha1(f"{who}|{tags}|{text}|v2".encode()).hexdigest()[:12]
    mp3 = os.path.join(CLIPS, f"{who}_{h}.mp3"); meta = mp3[:-4] + ".json"
    if not os.path.exists(meta):
        info = V.say(who, f"{tags} {text}".strip(), mp3)
        info["words"] = align(mp3, text)
        json.dump(info, open(meta, "w"))
    return mp3, json.load(open(meta))
def align(mp3, text):
    for attempt in range(5):
        r = requests.post(f"{V.API}/forced-alignment", headers=V.key(), data={"text": plain(text)},
                          files={"file": open(mp3, "rb")}, timeout=300)
        if r.status_code == 200:
            return [dict(w=w["text"], t0=round(w["start"], 3), t1=round(w["end"], 3)) for w in r.json().get("words", []) if w["text"].strip()]
        if r.status_code == 429: time.sleep(5 + 5 * attempt); continue
        sys.exit(f"alignment failed {r.status_code}: {r.text[:300]}")
    sys.exit("alignment: rate limited")

def song_part(name):
    """(audio, lines with word times, sections, duration) of a picked episode song"""
    od = SONGS[name]; sc = json.load(open(os.path.join(od, "song_check.json")))
    x = sf.read(os.path.join(od, "song.wav"), always_2d=True)[0].astype(np.float32)
    return x, sc["lines"], sc["sections"], len(x) / SR

def build(name):
    sc = S.SCENES[name]; t = 0.6; prev = None
    lines, pauses, acts, pages, audio = [], [], [], [], []
    page_open = None
    for b in sc["beats"]:
        kind = b[0]
        if kind in ("T", "P", "B"):
            who, text, tags, tg, pg, look = b
            w = WHO[who]
            mp3, info = clip(w, text, tags)
            if prev is not None: t += 0.32 if prev == w else 0.5
            if page_open is not None and page_open[0] is None: page_open[0] = t - 0.35
            x = V.load(mp3); d = len(x) / SR
            words = [dict(w=q["w"], t0=round(t + q["t0"], 3), t1=round(t + q["t1"], 3)) for q in info["words"]] or \
                    [dict(w=text, t0=round(t, 3), t1=round(t + d, 3))]
            lines.append(dict(who=w, line=text, sec="Talk", kind="tts", words=words, t0=round(t, 3), t1=round(t + d, 3),
                              tg=tg, pg=pg, look=look, clip=os.path.basename(mp3)))
            audio.append((t, x)); t += d; prev = w
            if text.rstrip().endswith("?"): t += 0.25
        elif kind == "pause":
            _, s, tg, pg = b; t += 0.25
            pauses.append(dict(t0=round(t, 3), t1=round(t + s, 3), tg=tg, pg=pg, who=lines[-1]["who"] if lines else "tumble"))
            t += s; prev = None
        elif kind == "act":
            _, an, s = b
            if an in SONGS:
                x, sl, secs, d = song_part(an); t += 0.3
                for L in sl:
                    lines.append(dict(who=L["who"], line=L["line"], sec="Song", kind="song", t0=round(t + L["words"][0]["t0"], 3),
                                      t1=round(t + L["words"][-1]["t1"], 3), look="cam", tg=None, pg=None,
                                      words=[dict(w=q["w"], t0=round(t + q["t0"], 3), t1=round(t + q["t1"], 3)) for q in L["words"]]))
                acts.append(dict(name=an, t0=round(t, 3), t1=round(t + d, 3), sections=[(n, round(t + a, 3), round(t + c, 3)) for n, a, c in secs]))
                audio.append((t, x)); t += d + 0.2; prev = None
            else:
                t += 0.25; acts.append(dict(name=an, t0=round(t, 3), t1=round(t + s, 3))); t += s; prev = None
        elif kind == "page":
            _, n, at, s = b; page_open = [None, n, at]
        elif kind == "endpage":
            if page_open: pages.append(dict(t0=round(page_open[0], 3), t1=round(t + 0.45, 3), fable=page_open[1], still=page_open[2]))
            page_open = None
    dur = round(t + (1.2 if sc["mode"] == "talk" else 0.9), 3)
    n = int(dur * SR) + SR; mix = np.zeros((n, 2), np.float32)
    for (a, x) in audio:
        i = int(a * SR); mix[i:i + len(x)] += x[:n - i]
    mix = mix[:int(dur * SR)]
    sf.write(os.path.join(AUD, f"{name}_dialogue.wav"), mix, SR)
    out = dict(scene=name, mode=sc["mode"], fable=sc.get("fable"), page_from=sc.get("page_from"), page_to=sc.get("page_to"),
               closed_book=sc.get("closed_book", False), night=sc.get("night", False), duration=dur,
               lines=lines, pauses=pauses, acts=acts, pages=pages)
    json.dump(out, open(os.path.join(AUD, f"{name}.json"), "w"), indent=1)
    print(f"{name}: {dur:.1f} s, {len(lines)} lines, {len(pauses)} pauses, {len(pages)} pictures", flush=True)
    return out

if __name__ == "__main__":
    names = [s for s in S.ORDER if isinstance(s, str)] if sys.argv[1:] == ["all"] else sys.argv[1:]
    for nm in names: build(nm)
