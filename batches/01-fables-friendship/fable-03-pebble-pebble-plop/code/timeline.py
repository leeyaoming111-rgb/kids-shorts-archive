"""Timeline for 'Tumble & Pip Fables 3: Pebble, Pebble, Plop!' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable03"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Pebble, Pebble, ", 92, "white"), ("Plop!", 104, "water")]
SOURCE = "Based on Aesop's fable The Crow and the Pitcher"
WORD_STYLE = {"plop": (1.3, "water"), "pop": (1.35, "big"), "stuck": (1.2, "big"), "think": (1.15, "gold"),
              "one": (1.2, "water"), "two": (1.2, "water"), "three": (1.2, "water"), "four": (1.2, "water"), "five": (1.3, "water")}

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
    ("Hook",      "pip",    "The water's way down there!"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "tumble", "Hot, hot sun! We need a drink!"),
    ("Setup B",   "pip",    "My beak can't reach... let me think!"),
    ("Problem A", "tumble", "In goes my paw... uh-oh, it's stuck!"),
    ("Problem B", "tumble", "Pull, pull, pull... and POP!"),
    ("Twist",     "pip",    "Pebbles in! One, two, three, four, five!"),
    ("Moral",     "pip",    "Think it through, try something new!"),
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
def _clip(x, a, b): return min(max(x, a), b)

_h, _s, _sa, _sb = sec("Hook"), sec("Sting"), sec("Setup A"), sec("Setup B")
_pa, _pb, _tw, _m, _c, _bt = sec("Problem A"), sec("Problem B"), sec("Twist"), sec("Moral"), sec("Chorus"), sec("Button")

# story events from word times
PAW_IN = (word_times("in", "Problem A") or [_pa[0] + 0.6])[0]          # pushes his paw into the neck
STUCK = (word_times("stuck", "Problem A") or [_pa[0] + 2.5])[0]
PULLS = word_times("pull", "Problem B")[:3] or [_pb[0] + 0.3 + 0.45 * k for k in range(3)]
POP = (word_times("pop", "Problem B") or [PULLS[-1] + 0.9])[0]
COUNT = [(word_times(w, "Twist") or [_tw[0] + 1.2 + 0.6 * k])[0] for k, w in enumerate(("one", "two", "three", "four", "five"))]
HOOK_SPLIT = _clip(_h[0] + 1.9, 1.4, _h[1] - 1.4)                     # Pip peering in, then the look down the neck
PB_SPLIT = _clip(POP + 0.35, _pb[0] + 1.4, _pb[1] - 3.0)              # the pull and the pop, then the backward roll
TW_SPLIT = _clip(COUNT[-1] + 0.9, _tw[0] + 2.5, _tw[1] - 1.6)          # the counting drops, then the drink
SHOTS = [(0.0, HOOK_SPLIT, "hook_peer"), (HOOK_SPLIT, _h[1], "hook_pov"), (_s[0], _s[1], "title_wide"),
         (_sa[0], _sa[1], "hot_walk"), (_sb[0], _sb[1], "pip_try"), (_pa[0], _pa[1], "paw_in"),
         (_pb[0], PB_SPLIT, "pull"), (PB_SPLIT, _pb[1], "roll_back"), (_tw[0], TW_SPLIT, "count"),
         (TW_SPLIT, _tw[1], "drink"), (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

ROLL_END = POP + 1.25                         # backward somersault, lands on his feet by the pebble pile
IDEA = max(ROLL_END + 0.3, _pb[1] - 2.0)      # Pip lands by the pebbles and points
SCOOP = IDEA + 0.75                           # Tumble scoops five pebbles into his paws
FULL = COUNT[-1] + 0.45                       # the water reaches the top
SIP = TW_SPLIT + 0.25                         # Pip sips from the brim
LAP = TW_SPLIT + 0.9                          # Tumble's tongue reaches it too
SPLASH = _bt[0] + 0.75                        # button: Pip's wing-splash lands on Tumble's nose
HIGH_FIVE = _c[1] - 0.9
SPOKEN = [dict(file="s00_tumble", who="tumble", t0=POP + 0.35, caption="Whoa-oh!", tags="[surprised] [laughing]"),
          dict(file="s01_both", who="both", t0=LAP + 0.35, caption="Ahh!", tags="[relieved] [happy sigh]"),
          dict(file="s02_both", who="both", t0=_bt[0] + 1.2, caption="Bye-bye!", tags="[cheerful] [giggles]")]
