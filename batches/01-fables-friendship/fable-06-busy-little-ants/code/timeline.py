"""Timeline for 'Tumble & Pip Fables 6: Busy Little Ants' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable06"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Busy Little ", 96, "white"), ("Ants", 112, "ant")]
SOURCE = "Based on Aesop's fable The Ant and the Grasshopper"
WORD_STYLE = {"ants": (1.2, "ant"), "ant": (1.2, "ant"), "snowflake": (1.2, "tiny"), "share": (1.2, "gold"), "help": (1.2, "big")}

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
    ("Hook",      "tumble", "Little ants, where do you go?"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "tumble", "Crunchy leaves! Come and play!"),
    ("Setup B",   "pip",    "Work first, play later, okay?"),
    ("Problem A", "tumble", "Look at me, I'm an ant!"),
    ("Problem B", "tumble", "Brr, a snowflake! My tummy rumbles..."),
    ("Twist",     "pip",    "Knock, knock! The ants share their snack!"),
    ("Moral",     "tumble", "Help a little every day!"),
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
SB_SPLIT = _sb[0] + 1.25 * BAR               # Pip sings with the ants, then carries a seed along the line
PB_SPLIT = _pb[0] + 1.5 * BAR                # the first snowflake close-up, then the chilly wide
TW_SPLIT1 = _tw[0] + 1.25 * BAR              # knock-knock and the door, then the shared snack
TW_SPLIT2 = _tw[0] + 2.15 * BAR              # next morning: Tumble carries the biggest seed
SHOTS = [(0.0, _h[1], "hook_ants"), (_s[0], _s[1], "title_wide"), (_sa[0], _sa[1], "leaf_play"),
         (_sb[0], SB_SPLIT, "pip_work"), (SB_SPLIT, _sb[1], "pip_carry"), (_pa[0], _pa[1], "ant_hat"),
         (_pb[0], PB_SPLIT, "snowflake"), (PB_SPLIT, _pb[1], "chilly"), (_tw[0], TW_SPLIT1, "knock"),
         (TW_SPLIT1, TW_SPLIT2, "snack"), (TW_SPLIT2, _tw[1], "next_day"),
         (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

# story events from word times
LEAF_HOPS = (word_times("leaves", "Setup A") + word_times("play", "Setup A"))[:2]
SEED_ON = (word_times("ant", "Problem A") or [_pa[0] + 1.8])[0]          # the seed settles on his head on "ant"
SEED_LIFT = SEED_ON - 1.35                                              # he lifts it, dips (anticipation)...
TOSS = SEED_ON - 0.55                                                   # ...and tosses it up onto his head
TIP_OFF = _pa[1] - 0.8                                                  # after the wobble it tips off into the leaves
FLAKE_LAND = (word_times("snowflake", "Problem B") or [_pb[0] + 0.6])[0] + 0.25
RUMBLE = (word_times("rumbles", "Problem B") or [_pb[0] + 2.4])[0]
SNEEZE = PB_SPLIT + 0.7                                                 # "Ah-choo!" pops the flake off his nose
KNOCKS = word_times("knock", "Twist")[:2] or [_tw[0] + 0.2, _tw[0] + 0.6]
DOOR_OPEN = KNOCKS[-1] + 0.45
NIBBLE = TW_SPLIT1 + 1.0
SET_DOWN = _tw[1] - 0.6                                                 # the biggest seed set down at the door
HIGH_FIVE = _c[1] - 0.9
_wob = line("Problem A")["t1"] + 0.35
SPOKEN = [dict(file="s00_tumble", who="tumble", t0=_wob, caption="Wibble-wobble!", tags="[giggling] [playful]"),
          dict(file="s01_tumble", who="tumble", t0=SNEEZE - 0.35, caption="Ah... CHOO!", tags="[sneezing] [cute]"),
          dict(file="s02_tumble", who="tumble", t0=NIBBLE, caption="Mmm, crunchy!", tags="[delighted]"),
          dict(file="s03_both", who="both", t0=_bt[0] + 0.7, caption="Bye-bye!", tags="[cheerful]")]
