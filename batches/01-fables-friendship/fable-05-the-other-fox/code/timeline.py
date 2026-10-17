"""Timeline for 'Tumble & Pip Fables 5: The Other Fox' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable05"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("The ", 100, "white"), ("Other ", 110, "gold"), ("Fox", 110, "white")]
SOURCE = "Based on Aesop's fable The Dog and His Reflection"
WORD_STYLE = {"bigger": (1.35, "big"), "splash": (1.3, "tiny"), "half": (1.2, "gold"), "share": (1.25, "gold")}

PLAN_SECTIONS = [
    ("Hook",      0.0,  1.5, "verse"),
    ("Sting",     1.5,  2.5, "sting"),
    ("Setup A",   2.5,  4.5, "verse"),
    ("Setup B",   4.5,  6.5, "verse"),
    ("Problem A", 6.5,  8.5, "verse"),
    ("Problem B", 8.5, 11.5, "verse"),
    ("Twist",    11.5, 14.5, "verse"),
    ("Moral",    14.5, 16.0, "verse"),
    ("Chorus",   16.0, 19.0, "chorus"),
    ("Button",   19.0, 20.0, "verse"),
]
PLAN_LINES = [
    ("Hook",      "tumble", "Hey! Who's that fox down there?"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "tumble", "My shiny apple, red and round!"),
    ("Setup B",   "tumble", "That fox has a BIGGER one!"),
    ("Problem A", "tumble", "Silly face! He copies me!"),
    ("Problem B", "tumble", "I want THAT one! Oh no, SPLASH!"),
    ("Twist",     "pip",    "Here's my berry, half for you!"),
    ("Moral",     "pip",    "Love what you've got, and share it!"),
    ("Chorus",    "both",   "Big or small, short or tall,"),
    ("Chorus",    "both",   "friends help friends, that's best of all!"),
]
_check = "out/song_check.json"
ALIGNED = os.path.exists(_check)

def _syllables(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1: n -= 1
    return max(1, n)

if ALIGNED:
    _C = json.load(open(_check))
    SECTIONS = [(n, a, b) for n, a, b in _C["sections"]]
    LINES = [dict(i=i, who=L["who"], text=L["line"], section=L["sec"],
                  words=[dict(w=w["w"], t0=w["t0"], t1=w["t1"]) for w in L["words"]]) for i, L in enumerate(_C["lines"])]
else:
    SECTIONS = [(n, a * BAR, b * BAR) for n, a, b, _ in PLAN_SECTIONS]
    LINES = []; sec_pos = {}
    for i, (sname, who, text) in enumerate(PLAN_LINES):
        a, b = next((x, y) for n, x, y in SECTIONS if n == sname)
        t = sec_pos.get(sname, a + 0.2); words = []
        for w in text.split():
            d = _syllables(w) / 3.0
            words.append(dict(w=w, t0=round(t, 3), t1=round(t + d * 0.9, 3)))
            t += d + (0.25 if w.endswith((",", "!", "?", "...")) else 0.0)
        sec_pos[sname] = t + 0.35
        LINES.append(dict(i=i, who=who, text=text, section=sname, words=words))
for L in LINES:
    L["t0"], L["t1"] = L["words"][0]["t0"], L["words"][-1]["t1"]
DURATION = SECTIONS[-1][2]

def sec(name):
    for n, a, b in SECTIONS:
        if n == name: return a, b
    raise KeyError(name)
def line(section, who=None):
    for L in LINES:
        if L["section"] == section and (who is None or L["who"] == who): return L
def word_times(word, section=None):
    k = word.lower()
    return [w["t0"] for L in LINES if section is None or L["section"] == section
            for w in L["words"] if re.sub(r"[^a-z]", "", w["w"].lower()) == k]

_h, _s, _sa, _sb = sec("Hook"), sec("Sting"), sec("Setup A"), sec("Setup B")
_pa, _pb, _tw, _m, _c, _bt = sec("Problem A"), sec("Problem B"), sec("Twist"), sec("Moral"), sec("Chorus"), sec("Button")
def _first(word, section, default):
    w = word_times(word, section)
    return w[0] if w else default
COPY = _first("he", "Problem A", _pa[0] + 1.6)               # "He copies me!": the cut to both foxes at once
PA_SPLIT = max(_pa[0] + 1.4, min(COPY - 0.1, _pa[1] - 1.4))
SLIP = _first("no", "Problem B", _pb[0] + 1.8)                # "Oh no": the apple slips out of his paws
SPLASH = max(_first("splash", "Problem B", _pb[0] + 2.4), SLIP + 0.45)
PB_SPLIT = max(_pb[0] + 1.4, SPLASH + 0.55)                   # the splash, then the wobble shot
BERRY_W = _first("berry", "Twist", _tw[0] + 0.8)
HALF = _first("half", "Twist", _tw[0] + 1.4)                  # Pip pecks the berry in two
TW_SPLIT = max(_tw[0] + 1.4, min(_tw[0] + 1.5 * BAR, _tw[1] - 1.4))
SHOTS = [(0.0, _h[1], "hook_mirror"), (_s[0], _s[1], "title_wide"), (_sa[0], _sa[1], "proud"),
         (_sb[0], _sb[1], "bigger"), (_pa[0], PA_SPLIT, "silly_face"), (PA_SPLIT, _pa[1], "copycat"),
         (_pb[0], PB_SPLIT, "reach"), (PB_SPLIT, _pb[1], "wobble"), (_tw[0], TW_SPLIT, "berry"),
         (TW_SPLIT, _tw[1], "share"), (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

# story events from word times
HEY = _first("hey", "Hook", 0.3)
SHINY = word_times("shiny", "Setup A") + word_times("red", "Setup A") + word_times("round", "Setup A")
BIGGER = _first("bigger", "Setup B", _sb[0] + 1.3)
_pal = line("Problem A")
FACE = max(_pa[0] + 0.15, _pal["t0"] - 0.2)                  # pulls the face as he starts the line
BLEH = max(_pal["t1"] + 0.35, PA_SPLIT + 0.6)
REACH = line("Problem B")["t0"]
_pbl = line("Problem B")
WOBBLY = max(_pbl["t1"] + 0.5, PB_SPLIT + 0.7)
_twl = line("Twist")
BITE = max(_twl["t1"] + 0.4, TW_SPLIT + 0.35)
BEST = BITE + 0.55
HIGH_FIVE = _c[1] - 0.9
SPOKEN = [dict(file="s00_tumble", who="tumble", t0=BLEH, caption="Blehhh!", tags="[silly] [playful]"),
          dict(file="s01_tumble", who="tumble", t0=WOBBLY, caption="Whoa, wobbly!", tags="[surprised] [giggles]"),
          dict(file="s02_tumble", who="tumble", t0=BEST, caption="Your berry is the best!", tags="[happy] [laughing]"),
          dict(file="s03_both", who="both", t0=_bt[0] + 0.7, caption="Bye-bye!", tags="[cheerful]")]
