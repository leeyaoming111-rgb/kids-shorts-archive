"""Timeline for 'Tumble & Pip Fables 4: Slow and Steady Bo' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable04"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Slow ", 100, "slow"), ("and Steady ", 84, "white"), ("Bo", 110, "bo")]
SOURCE = "Based on Aesop's fable The Tortoise and the Hare"
WORD_STYLE = {"slow": (1.2, "slow"), "steady": (1.2, "slow"), "zoom": (1.25, "big"), "fastest": (1.2, "big")}

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
    ("Hook",      "pip",    "Ready, steady... go, go, go!"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "tumble", "Zoom, zoom! I'm the fastest fox!"),
    ("Setup B",   "bo",     "Step by step, I'm slow but sure."),
    ("Problem A", "tumble", "Too easy! Time for a tiny rest!"),
    ("Problem B", "pip",    "Shh! Tumble's snoozing... Bo keeps going!"),
    ("Twist",     "pip",    "Wake up, Tumble! Look at Bo!"),
    ("Moral",     "bo",     "Slow and steady gets there too!"),
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
LIE_SPLIT = _pa[0] + 1.0 * BAR               # the show-off, then lying down in the mushroom shade
SNORE_SPLIT = _pb[0] + 1.0 * BAR             # close on the snore, then Bo plodding past
_lt = line("Twist")
NEAR_SPLIT = max(_tw[0] + 1.4, (word_times("tumble", "Twist") or [_tw[0] + 1.2])[0] + 0.45)   # Pip calls from the finish...
WAKE = max(_lt["t1"] + 0.15, NEAR_SPLIT + 0.5)   # ...cut to Tumble, who hears it and sits up with a jolt
WAKE_SPLIT = WAKE + 1.15                       # legs spin, he zooms off; cut to the finish
SHOTS = [(0.0, _h[1], "start_line"), (_s[0], _s[1], "title_wide"), (_sa[0], _sa[1], "zoom"), (_sb[0], _sb[1], "bo_steps"),
         (_pa[0], LIE_SPLIT, "show_off"), (LIE_SPLIT, _pa[1], "lie_down"), (_pb[0], SNORE_SPLIT, "snore"),
         (SNORE_SPLIT, _pb[1], "bo_passes"), (_tw[0], NEAR_SPLIT, "bo_near"), (NEAR_SPLIT, WAKE_SPLIT, "wake"),
         (WAKE_SPLIT, _tw[1], "finish"), (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

# story events from word times
GO = (word_times("go", "Hook") or [_h[0] + 2.6])[0]           # Pip drops the flag, the race starts
ZOOMS = word_times("zoom", "Setup A")
RUN_END = _sa[0] + 1.25 * BAR                  # Tumble skids to a stop past the mushrooms
EASY = (word_times("easy", "Problem A") or [_pa[0] + 0.6])[0]
LIE = LIE_SPLIT + 1.0                          # lies down in the shade, eyes shut
_lb = line("Problem B")
SNORES = [_lb["t1"] + 0.35 + k * 1.15 for k in range(3) if _lb["t1"] + 0.35 + k * 1.15 < _pb[1] - 0.6]
SPIN = (WAKE + 0.3, WAKE + 0.85)               # legs spin in the air before he takes off
BO_TOUCH = WAKE_SPLIT + 0.4                    # Bo's nose touches the stump
FOX_ARRIVE = WAKE_SPLIT + 0.85                 # Tumble zooms in a moment later and skids to a stop
CHEER = FOX_ARRIVE + 0.35
HIGH_FIVE = _c[1] - 0.9
SPOKEN = [dict(file="s00_tumble", who="tumble", t0=SNORES[0] if SNORES else _pb[1] - 2.0, caption="Zzz... snore...", tags="[snoring] [sleepy]"),
          dict(file="s01_tumble", who="tumble", t0=WAKE, caption="Huh? Whoa!", tags="[startled]"),
          dict(file="s02_tumble", who="tumble", t0=CHEER, caption="Well done, Bo!", tags="[cheerful] [warm]"),
          dict(file="s03_both", who="both", t0=_bt[0] + 0.35, caption="Bye-bye!", tags="[cheerful]"),
          dict(file="s04_bo", who="bo", t0=_bt[0] + 1.3, caption="Bye... bye!", tags="[slowly] [warm]")]
