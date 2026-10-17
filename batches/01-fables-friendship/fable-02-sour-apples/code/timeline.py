"""Timeline for 'Tumble & Pip Fables 2: Sour Apples?' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable02"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Sour ", 110, "sour"), ("Apples?", 100, "white")]
SOURCE = "Based on Aesop's fable The Fox and the Grapes"
WORD_STYLE = {"sour": (1.25, "sour"), "sweet": (1.3, "sweet"), "friend": (1.15, "gold")}

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
    ("Hook",      "tumble", "One red apple, way up high!"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "tumble", "Jump, jump, jump! I'll reach it, I'll try!"),
    ("Setup B",   "tumble", "One more big jump... whoa!"),
    ("Problem A", "tumble", "Those apples are sour anyway!"),
    ("Problem B", "pip",    "Let's try together, you and me!"),
    ("Twist",     "pip",    "Tug, tug, tug... here it comes!"),
    ("Moral",     "pip",    "Don't say sour, ask a friend!"),
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
LEAP = (word_times("jump", "Setup B") or [_sb[0] + 1.2])[0]
BIG_SPLIT = LEAP + 0.5                       # run-up and the leap up to its peak, then the leaf-pile close-up as he comes down
PB_SPLIT = _pb[0] + 1.5 * BAR                # Pip's idea, then the climb onto the stump
_tug_w = word_times("tug", "Twist")
TUGS = _tug_w if _tug_w else [_tw[0] + 1.3, _tw[0] + 1.9, _tw[0] + 2.5]
_comes = (word_times("comes", "Twist") or [_tw[0] + 5.0])[0]
RELEASE = _comes - 0.2                       # the apple comes free as "here it comes" lands
TW_SPLIT = RELEASE - 0.1                     # tug close-up, then the catch (the fall happens in the catch shot)
READY_SPLIT = TUGS[0] - 1.2                  # Tumble waits on the stump while Pip flies up, then the tug close-up
SHOTS = [(0.0, _h[1], "hook_reach"), (_s[0], _s[1], "title_wide"), (_sa[0], _sa[1], "jumps"),
         (_sb[0], BIG_SPLIT, "big_jump"), (BIG_SPLIT, _sb[1], "leaf_pile"), (_pa[0], _pa[1], "sour_face"),
         (_pb[0], PB_SPLIT, "pip_idea"), (PB_SPLIT, _tw[0], "climb"), (_tw[0], READY_SPLIT, "ready"), (READY_SPLIT, TW_SPLIT, "tug"),
         (TW_SPLIT, _tw[1], "catch"), (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

# story events from word times
JUMPS = word_times("jump", "Setup A")[:3]
LAND = BIG_SPLIT + 0.2                        # lands head-first in the leaf pile just after the cut
POP_OUT = _pa[0] + 0.2
CATCH = RELEASE + 0.55
GAG_SWEET = _c[1] - 1.6                       # after the chorus lyric ends: the first crunchy bite ("Mmm, SWEET!")
HIGH_FIVE = (line("Chorus") and [L for L in LINES if L["section"] == "Chorus"][-1]["t1"] - 0.25) or (_c[1] - 0.9)
SPOKEN = [dict(file="s00_tumble", who="tumble", t0=LAND + 0.15, caption="Oof!", tags="[muffled] [surprised]"),
          dict(file="s01_tumble", who="tumble", t0=GAG_SWEET, caption="Mmm, SWEET!", tags="[delighted]"),
          dict(file="s02_both", who="both", t0=_bt[0] + 0.7, caption="Bye-bye!", tags="[cheerful]")]
