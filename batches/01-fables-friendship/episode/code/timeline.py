"""Timeline for the Episode 01 Story Stump scenes (intro, link01..link09, break, recap, outro), one scene per run.

SCENE (env, set by render.py --scene <name>) picks the scene; ASPECT defaults to wide (the episode is 16:9 only).
Planned lines come from ../episode.py. Until audio/episode-01/<scene>.json exists (written by el_episode.py mix) the
planned times and estimated word times are used; with it, the real TTS and song word times drive captions, mouths,
cuts and events, and nothing else changes. The stored sting and chorus already have real word times."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import episode as EP

FPS = 30
SCENE = os.environ.get("SCENE", "intro")
if SCENE not in EP.SCENE_LEN: sys.exit(f"unknown scene {SCENE}: one of {sorted(EP.SCENE_LEN)}")
JOB = f"ep01_{SCENE}"
ASPECT = os.environ.get("ASPECT", "wide")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = EP.BPM
BAR = EP.BAR
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Fables About ", 92, "white"), ("Friendship", 92, "gold")]
WORD_STYLE = {"tiny": (0.8, "tiny"), "small": (0.8, "tiny"), "big": (1.3, "big"), "helpers": (1.3, "big"),
              "sour": (1.2, "sour"), "sweet": (1.2, "sweet"), "friend": (1.12, "gold"), "friends": (1.12, "gold"),
              "friendship": (1.0, "gold"), "strong": (1.2, "big"), "kind": (1.12, "gold"), "share": (1.12, "gold"),
              "goodnight": (1.12, "gold")}
SPOKEN = []                              # every line (spoken or sung) is in LINES, so long lines keep their caption

_check = os.path.join(EP.AUDIO, f"{SCENE}.json")
ALIGNED = os.path.exists(_check)
SEC = {"sting": "Sting", "tts": "Talk", "chorus": "Chorus", "recap": "Moral", "lullaby": "Lullaby"}

def _syllables(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1: n -= 1
    return max(1, n)
def _estimate(text, t, rate):
    words = []
    for w in text.split():
        d = _syllables(w) / rate
        words.append(dict(w=w, t0=round(t, 3), t1=round(t + d * 0.9, 3)))
        t += d + (0.22 if w.endswith((",", "!", "?", "...", ".")) else 0.0)
    return words
def _stored(name):
    return json.load(open(os.path.join(EP.BATCH, "audio", "series", f"{name}_check.json")))["lines"]

if ALIGNED:
    _C = json.load(open(_check))
    DURATION = _C["duration"]
    LINES = [dict(i=i, who=L["who"], text=L["line"], section=L["sec"], kind=L.get("kind", ""),
                  words=[dict(w=w["w"], t0=w["t0"], t1=w["t1"]) for w in L["words"]]) for i, L in enumerate(_C["lines"])]
else:
    DURATION = EP.SCENE_LEN[SCENE]
    LINES, used = [], set()
    for (t, who, text, kind, tags) in EP.LINES[SCENE]:
        if kind in ("sting", "chorus"):                     # stored takes: real word times, shifted to where they play
            src = next(L for L in _stored(kind) if L["line"] == text)
            words = [dict(w=w["w"], t0=round(w["t0"] + t, 3), t1=round(w["t1"] + t, 3)) for w in src["words"]]
        else:
            words = _estimate(text, t + (0.2 if kind == "recap" else 0.0), 2.4 if kind in ("recap", "lullaby") else 4.2)
        LINES.append(dict(i=len(LINES), who=who, text=text, section=SEC[kind], kind=kind, words=words))
for L in LINES:
    L["t0"], L["t1"] = L["words"][0]["t0"], L["words"][-1]["t1"]
LINES.sort(key=lambda L: L["t0"])
TALK = [L for L in LINES if L["kind"] == "tts" or L["section"] == "Talk"]

def word_times(word, lines=None):
    k = word.lower()
    return [w["t0"] for L in (lines or LINES) for w in L["words"] if re.sub(r"[^a-z]", "", w["w"].lower()) == k]
def line(section, who=None):
    for L in LINES:
        if L["section"] == section and (who is None or L["who"] == who): return L

# ---------------- shots and events per scene ----------------
HIGH_FIVES = []
TURNS = []                     # page turns: (t0, page index after the turn)
OPEN = CLOSE = None            # front cover opens / book closes
FADE_OUT = None
LINK = SCENE.startswith("link")
if SCENE == "intro":
    L1, L2, L3, L4, L5, L6, L7 = TALK
    OPEN = L4["t1"] + 0.35
    SHOTS = [(0.0, 2.9, "title_wide"), (2.9, L2["t0"] - 0.2, "arrive"), (L2["t0"] - 0.2, L3["t0"] - 0.25, "show_cover"),
             (L3["t0"] - 0.25, L4["t0"] - 0.2, "cover_close"), (L4["t0"] - 0.2, L5["t0"] - 0.25, "open_book"),
             (L5["t0"] - 0.25, L7["t0"] - 0.3, "spread_close"), (L7["t0"] - 0.3, DURATION + 0.1, "thats_me")]
    PIP_LAND = 3.0
elif LINK:
    A, B = TALK[0], TALK[1]
    TURN = min(max(A["t1"] + 0.3, 2.6), B["t0"] - 0.7)
    TURNS = [(TURN, 1)]
    k = int(SCENE[4:])
    SHOTS = [(0.0, TURN - 0.25, f"a_{k:02d}"), (TURN - 0.25, DURATION + 0.1, f"b_{k:02d}")]
elif SCENE == "break":
    CH = [L for L in LINES if L["section"] == "Chorus"]
    C0 = EP.CHORUS_AT["break"][0]; C1 = EP.CHORUS_AT["break"][1] + 3 * BAR
    if ALIGNED: C0, C1 = _C["cues"]["chorus"]
    HIGH_FIVES = [C0 + 3 * BAR - 0.9, C1 - 0.9]
    SHOTS = [(0.0, C0, "call"), (C0, C1, "chorus"), (C1, DURATION + 0.1, "well_done")]
elif SCENE == "recap":
    M = [L for L in LINES if L["section"] == "Moral"]
    TURNS = [(L["t0"] - 0.95, k) for k, L in enumerate(M) if k > 0]
    cuts = [0.0] + [a - 0.25 for a, _ in TURNS] + [M[-1]["t1"] + 0.6, DURATION + 0.1]
    names = [f"r{k + 1:02d}" for k in range(len(M))] + ["recap_end"]
    SHOTS = [(cuts[i], cuts[i + 1], names[i]) for i in range(len(names))]
elif SCENE == "outro":
    G = TALK[0]
    CLOSE = 2.2
    FADE_OUT = (DURATION - 2.4, DURATION)
    SHOTS = [(0.0, 4.0, "lullaby_a"), (4.0, G["t0"] - 0.3, "lullaby_b"), (G["t0"] - 0.3, G["t0"] + 2.1, "goodnight"),
             (G["t0"] + 2.1, DURATION + 0.1, "sky")]
HIGH_FIVE = HIGH_FIVES[-1] if HIGH_FIVES else -10.0
if TITLE_SHOT not in [n for _, _, n in SHOTS]: SHOTS.append((-2.0, -1.0, TITLE_SHOT))   # no title card in this scene
SHOTS.sort(key=lambda s: s[0])

def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

# where this scene sits in the episode (for the sunset-to-night light)
EP_START = EP.starts()[0][SCENE]
def dusk(t): return EP.dusk(EP_START + t)
