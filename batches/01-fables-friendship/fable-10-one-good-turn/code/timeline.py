"""Timeline for 'Tumble & Pip Fables 10: One Good Turn' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable10"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("One ", 104, "white"), ("Good ", 112, "gold"), ("Turn", 104, "white")]
SOURCE = "Based on Aesop's fable The Dove and the Ant"
WORD_STYLE = {"honey's": (1.2, "gold"), "sticky": (1.2, "gold"), "pop": (1.4, "big"), "friend": (1.15, "gold"),
              "helps": (1.15, "gold"), "ant": (0.85, "big")}

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
PLAN_LINES = [                                 # "ant": sung by the music model in the ant's own voice (code/el_verse.py)
    ("Hook",      "pip",    "Oh no, little ant!"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "pip",    "Here's a leaf! Hop on, hop on!"),
    ("Setup B",   "ant",    "Thank you, Pip! I won't forget!"),
    ("Problem A", "tumble", "Careful, Pip! The honey's sticky!"),
    ("Problem B", "pip",    "Oh no! My feet are stuck!"),
    ("Twist",     "ant",    "Heave, ho! Heave, ho! One more... POP!"),
    ("Moral",     "ant",    "Help a friend, and a friend helps you!"),
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
def _w(word, section, k=0, default=None):
    ts = word_times(word, section)
    return ts[k] if len(ts) > k else default

# story events from word times
HOPS = word_times("hop", "Setup A")
DROP = max((HOPS[0] if HOPS else _sa[0] + 2.0) - 0.4, _sa[0] + 1.8)   # the leaf leaves Pip's beak and lands on the first "hop"
ANT_HOP = (HOPS[1] if len(HOPS) > 1 else DROP + 1.2)  # the ant hops from the twig onto the leaf on the second "hop"
SA_SPLIT = min(max(DROP - 1.0, _sa[0] + 1.4), _sa[1] - 2.2)   # carry the leaf out, then the overhead drop
ASHORE = _sb[0] + 0.5                                # the leaf touches the bank, the ant hops off
GRAB = _s[1] - 0.45                                  # Pip takes the leaf stem in his beak (end of the title shot)
PA_SPLIT = _pa[0] + 1.0 * BAR                        # Pip flies off, then the landing close-up
SPLAT = PA_SPLIT + 0.55                              # Pip lands in the honey
STUCK = word_times("stuck", "Problem B")
PB_SPLIT = (line("Problem B")["t1"] if line("Problem B") else _pb[0] + 2.3) + 0.6   # the stuck close-up, then the wide
WHISTLE = PB_SPLIT + 1.0                             # the ant whistles for its friends
MARCH = WHISTLE + 0.35                               # the ant line sets off
TUGS = word_times("heave", "Twist")[:2] + word_times("more", "Twist")[:1]
POP = _w("pop", "Twist", 0, _tw[0] + 3.0)
TW_SPLIT = POP - 0.25                                # cut to the wide just before the pop
LANDING = POP + 1.25                                 # Pip lands on Tumble's nose
HIGH_FIVE = _c[1] - 0.9
SPOKEN = [dict(file="s00_tumble", who="tumble", t0=PB_SPLIT + 0.25, caption="Uh-oh!", tags="[worried]"),
          dict(file="s01_pip", who="pip", t0=POP + 0.2, caption="Wheee!", tags="[excited] [laughing]"),
          dict(file="s02_both", who="both", t0=_bt[0] + 0.7, caption="Bye-bye!", tags="[cheerful]")]
SHOTS = [(0.0, _h[1], "hook_water"), (_s[0], _s[1], "title_wide"), (_sa[0], SA_SPLIT, "leaf_pickup"),
         (SA_SPLIT, _sa[1], "leaf_drop"), (_sb[0], _sb[1], "thank_you"), (_pa[0], PA_SPLIT, "fly_off"),
         (PA_SPLIT, _pa[1], "splat"), (_pb[0], PB_SPLIT, "stuck"), (PB_SPLIT, _pb[1], "ants_march"),
         (_tw[0], TW_SPLIT, "tug"), (TW_SPLIT, _tw[1], "pop"), (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"),
         (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]
