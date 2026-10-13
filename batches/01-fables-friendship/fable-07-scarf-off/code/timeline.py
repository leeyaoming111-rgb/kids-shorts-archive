"""Timeline for 'Tumble & Pip Fables 7: Scarf Off!' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable07"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Scarf ", 110, "scarf"), ("Off!", 110, "sunny")]
SOURCE = "Based on Aesop's fable The North Wind and the Sun"
WORD_STYLE = {"wind": (1.2, "windy"), "huff": (1.15, "windy"), "puff": (1.15, "windy"), "sun": (1.25, "sunny"), "suns": (1.25, "sunny"),
              "scarf": (1.15, "scarf"), "gentle": (1.2, "gold"), "kind": (1.2, "gold")}

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
    ("Hook",      "pip",    "Who can get the scarf off?"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "pip",    "Wind and Sun, a friendly game!"),
    ("Setup B",   "tumble", "My stripy scarf is snug and warm!"),
    ("Problem A", "tumble", "Huff and puff! I'll hold on tight!"),
    ("Problem B", "tumble", "Round and round... it won't come off!"),
    ("Twist",     "pip",    "Sun's turn! Shine so soft and kind..."),
    ("Moral",     "pip",    "Gentle and kind works best!"),
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
SA_SPLIT = _sa[0] + 1.08 * BAR              # Wind and Sun greet each other, then Pip blows the whistle
PA_SPLIT = _pa[0] + 0.75 * BAR              # Wind puffs up, then Tumble hugs his scarf in the wind
PB_SPLIT1 = _pb[0] + 1.25 * BAR             # the weathervane spin, then Pip on the flower
PB_SPLIT2 = _pb[0] + 2.0 * BAR              # Pip on the flower, then Wind runs out of puff
TW_SPLIT1 = _tw[0] + 1.0 * BAR              # the Sun shines, then the scarf comes off
TW_SPLIT2 = _tw[0] + 2.08 * BAR             # the scarf falls, he lies down in the sun
SHOTS = [(0.0, _h[1], "hook_sky"), (_s[0], _s[1], "title_wide"), (_sa[0], SA_SPLIT, "sky_faces"), (SA_SPLIT, _sa[1], "whistle"),
         (_sb[0], _sb[1], "snug"), (_pa[0], PA_SPLIT, "wind_puff"), (PA_SPLIT, _pa[1], "hold_tight"),
         (_pb[0], PB_SPLIT1, "spin"), (PB_SPLIT1, PB_SPLIT2, "pip_cling"), (PB_SPLIT2, _pb[1], "wind_tired"),
         (_tw[0], TW_SPLIT1, "sun_shine"), (TW_SPLIT1, TW_SPLIT2, "scarf_off"), (TW_SPLIT2, _tw[1], "sunbathe"),
         (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

# story events from word times
_hl = line("Hook")
WHISTLE_HOOK = min(_hl["t1"] + 0.25, _h[1] - 0.5)          # a peep after the question
_sa_l = line("Setup A")
WHISTLE_GO = max(_sa_l["t1"] + 0.2, SA_SPLIT + 0.7)       # "go!" whistle in the macro shot
WHISTLE_GO = min(WHISTLE_GO, _sa[1] - 0.6)
BLOW0 = (word_times("huff", "Problem A") or [_pa[0] + 0.3])[0] - 0.1   # Wind starts blowing
_tight = word_times("tight", "Problem A")
BLOWN = min((_tight[0] if _tight else _pa[0] + 2.6) + 0.35, _pa[1] - 0.75)  # Pip blown off the post
CLING = BLOWN + 0.6
SPIN0 = (word_times("round", "Problem B") or [_pb[0] + 0.2])[0]
SPIN1 = min(SPIN0 + 1.7, PB_SPLIT1 - 0.6)
BLOW1 = PB_SPLIT2 + 0.5                                   # Wind runs out of puff
SUN0 = _tw[0] + 0.35                                      # the sky warms from here (ramp 1.6 s)
GRAB = TW_SPLIT1 + 0.55
FREE = TW_SPLIT2 - 0.55                                   # the scarf leaves his neck
DROP = TW_SPLIT2 + 0.15
LIE0, LIE1 = TW_SPLIT2 + 0.6, TW_SPLIT2 + 1.3
WHISTLE_WIN = _tw[1] - 0.75
HIGH_FIVE = _c[1] - 0.9
SPOKEN = [dict(file="s00_pip", who="pip", t0=PB_SPLIT1 + 0.35, caption="Whoa-whoa!", tags="[surprised] [giggling]"),
          dict(file="s01_tumble", who="tumble", t0=FREE - 0.25, caption="Ahh... scarf off!", tags="[relieved] [happy sigh]"),
          dict(file="s02_both", who="both", t0=_bt[0] + 0.7, caption="Bye-bye!", tags="[cheerful]")]
