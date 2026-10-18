"""Timeline for 'Tumble & Pip Fables 8: Pip Who Cried Help' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable08"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Pip Who Cried ", 92, "white"), ("Help!", 108, "gold")]
SOURCE = "Based on Aesop's fable The Boy Who Cried Wolf"
WORD_STYLE = {"help": (1.2, "gold"), "truth": (1.3, "big"), "really": (1.15, "tiny")}

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
    ("Hook",      "pip",    "Help! Oh, help me! Come quick!"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "tumble", "I'm coming, Pip! I'm on my way!"),
    ("Setup B",   "pip",    "Just joking! It was just a game!"),
    ("Problem A", "pip",    "Help me, Tumble! Hurry, hurry!"),
    ("Problem B", "tumble", "Oh, Pip! Not another joke!"),
    ("Twist",     "pip",    "Help! It's really true this time!"),
    ("Moral",     "pip",    "Tell the truth, so friends know!"),
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
_la = line("Setup A")
TRIP = max(_la["t1"] + 0.25, _sa[0] + 3.0)    # his foot catches the puddle's edge just after he sings
SA_SPLIT = TRIP - 0.35                         # the run, then the ground-level splash
FLOP = TRIP + 0.4                              # belly lands in the puddle
SB_SPLIT = _sb[0] + 1.0 * BAR                  # Pip giggles, then Tumble drips and walks back
_lpa = line("Problem A")
RUN2 = (word_times("tumble", "Problem A") or [_pa[0] + 0.9])[0]          # sets off when Pip calls his name
LEAP2 = (word_times("hurry", "Problem A") or [_pa[0] + 2.0])[0] + 0.2    # jumps the puddle on the first "hurry"
SPIN = LEAP2 + 1.0                             # skids past the flower and spins
PB_SPLIT = max(line("Problem B")["t1"] + 0.4, _pb[0] + 2.6)               # dizzy line, then the basket
P_FLY = PB_SPLIT + 0.1                         # Pip flutters to the basket rim
P_RIM = P_FLY + 1.2
P_IN = P_RIM + 0.5                             # hops in
LID_FLOP = P_IN + 0.45                         # the lid tips forward ...
LID_SHUT = LID_FLOP + 0.45                     # ... and flops shut
TW_SPLIT1 = _tw[0] + 2.3                       # basket wobble, then Tumble wonders
JOKE = max(TW_SPLIT1 + 0.35, line("Twist")["t1"] + 0.2)                # "Is it a joke?"
TW_SPLIT2 = JOKE + 1.0      # then the rescue
STEP = TW_SPLIT2                               # steps up to the basket
LIFT = STEP + 0.35                              # lifts the lid front
POP = LIFT + 0.35                              # Pip pops out
SORRY = POP + 0.4                              # "Sorry, Tumble!"
LOWER = SORRY + 0.15                           # lid goes back down gently
CUDDLE = SORRY + 0.45                           # Pip hops onto his paws for the hug
HIGH_FIVE = _c[1] - 0.9
SHOTS = [(0.0, _h[1], "hook_flower"), (_s[0], _s[1], "title_wide"), (_sa[0], SA_SPLIT, "rush"),
         (SA_SPLIT, FLOP + 0.6, "splash"), (FLOP + 0.6, SB_SPLIT, "giggle"), (SB_SPLIT, _sb[1], "drip"),
         (_pa[0], _pa[1], "rush2"), (_pb[0], PB_SPLIT, "not_again"), (PB_SPLIT, LID_SHUT + 0.3, "basket"),
         (LID_SHUT + 0.3, TW_SPLIT1, "muffled"), (TW_SPLIT1, TW_SPLIT2, "is_it_a_joke"), (TW_SPLIT2, _tw[1], "rescue"),
         (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

SPOKEN = [dict(file="s00_tumble", who="tumble", t0=TRIP - 0.05, caption="Whoa!", tags="[surprised] [falling]"),
          dict(file="s01_tumble", who="tumble", t0=JOKE, caption="Is it a joke?", tags="[curious] [thoughtful]"),
          dict(file="s02_pip", who="pip", t0=SORRY, caption="Sorry, Tumble!", tags="[sheepish] [sincere]"),
          dict(file="s03_both", who="both", t0=_bt[0] + 0.7, caption="Bye-bye!", tags="[cheerful]")]
