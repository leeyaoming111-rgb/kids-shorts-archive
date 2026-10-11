"""Timeline for 'Tumble & Pip, Episode 2: Big and Small'. The song comes from the ElevenLabs Music API
(out/song.mp3, take 33); every time below is derived from its composition plan sections and forced-alignment word times
(out/song_check.json). Audio and video both import this."""
import json, re
FPS = 30
W, H = 1080, 1920
DURATION = 44.9
TITLE = "Tumble & Pip"
SUBTITLE = "Big and Small!"
EPISODE = "Episode 2"

_C = json.load(open("out/song_check.json"))
SECTIONS = [(n, a, b) for n, a, b in _C["sections"]]          # (name, t0, t1) from the composition plan
def sec(name):
    for n, a, b in SECTIONS:
        if n == name: return a, b
    raise KeyError(name)

LINES = []                                                       # sung lines with aligned word times
for i, L in enumerate(_C["lines"]):
    LINES.append(dict(i=i, who=L["who"], text=L["line"], section=L["sec"],
                      words=[dict(w=w["w"], t0=w["t0"], t1=w["t1"]) for w in L["words"]],
                      t0=L["words"][0]["t0"], t1=L["words"][-1]["t1"]))
def line(section, who=None):
    for L in LINES:
        if L["section"] == section and (who is None or L["who"] == who): return L
def word_time(section, word, nth=0):
    hits = [w for L in LINES if L["section"] == section for w in L["words"] if re.sub(r"[^a-z]", "", w["w"].lower()) == word]
    return hits[nth]["t0"] if len(hits) > nth else None

def gag_window(k):
    """instrumental break after Pip's sung line in round k (0-based)."""
    a, b = sec(f"Round {k + 1} small")
    L = line(f"Round {k + 1} small")
    return L["t1"] + 0.15, b

# gag exclamations: ElevenLabs v3 expressive TTS in the cast voices (cast_voices.json); everything else is sung
SPOKEN = [dict(file="wheee", who="pip", t0=gag_window(0)[0] + 0.15, caption="Wheee!"),
          dict(file="whoa", who="pip", t0=gag_window(1)[0] + 0.08, caption="Whoa!"),
          dict(file="oops", who="tumble", t0=gag_window(2)[0] + 0.75, caption="Oops!"),
          dict(file="boing", who="tumble", t0=gag_window(3)[0] + 0.5, caption="Boing!")]

# shot table (t0, t1, name): one shot per composition section, gags split off at the end of Pip's line
SHOTS = [(0.0, sec("Intro")[1], "flyover"), (sec("Chorus")[0], sec("Chorus")[1], "overhead")]
for k in range(4):
    a, b = sec(f"Round {k + 1} big"); SHOTS.append((a, b, f"big{k}"))
    a, b = sec(f"Round {k + 1} small"); g0, g1 = gag_window(k)
    SHOTS.append((a, g0, f"small{k}")); SHOTS.append((g0, b, f"gag{k}"))
SHOTS += [(sec("Finale A")[0], sec("Finale A")[1], "split"), (sec("Finale B")[0], line("Finale B", "tumble")["t0"] - 0.2, "together"),
          (line("Finale B", "tumble")["t0"] - 0.2, DURATION + 0.1, "crane_out")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

# story events from the aligned words
WHOOSH = word_time("Round 2 big", "whoosh")
STOMPS = [word_time("Round 4 big", "stomp", 0), word_time("Round 4 big", "stomp", 1)]
PIP_HOP = word_time("Round 4 small", "hop")
TINY_STOMP = gag_window(3)[0] + 0.15
BIG_HOP = gag_window(3)[0] + 0.55
SQUASH = gag_window(2)[0] + 0.35
BLOWN = gag_window(1)[0]                # the big leaf's gust starts the gag
ROLL = gag_window(0)[0]
