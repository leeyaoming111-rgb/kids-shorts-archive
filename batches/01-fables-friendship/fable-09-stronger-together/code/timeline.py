"""Timeline for 'Tumble & Pip Fables 9: Stronger Together' (Batch 01, Fables About Friendship).

Same skeleton and 100 BPM grid as every fable in the batch (one bar = 2.4 s): verse take + stored sting + stored
moral chorus. Until out/song_check.json exists the planned grid and estimated word times are used; nothing else
changes when the real song arrives. ASPECT=short (1080x1920) or wide (1920x1080)."""
import json, os, re

FPS = 30
JOB = "fable09"
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Stronger ", 100, "white"), ("Together!", 104, "gold")]
SOURCE = "Based on Aesop's fable The Bundle of Sticks"
WORD_STYLE = {"snap": (1.2, "sweet"), "snap!": (1.2, "sweet"), "strong": (1.3, "big"), "together": (1.2, "gold"), "bridge": (1.15, "tiny")}

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
    ("Hook",      "tumble", "One little twig? Snap! So easy!"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "pip",    "Can you snap the whole big bundle?"),
    ("Setup B",   "tumble", "Easy peasy! Watch me go!"),
    ("Problem A", "tumble", "Pull and push... it will not snap!"),
    ("Problem B", "tumble", "I'll sit on it, as hard as I can!"),
    ("Twist",     "pip",    "One stick snaps, but lots stay strong!"),
    ("Twist",     "pip",    "Make a bridge and hop along!"),
    ("Moral",     "pip",    "Together we're strong!"),
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
# story events from word times
SNAP = (word_times("snap", "Hook") or [_h[0] + 1.3])[0]
PULL = (word_times("pull", "Problem A") or [_pa[0] + 0.3])[0]
PUSH = (word_times("push", "Problem A") or [_pa[0] + 1.0])[0]
_lpb = line("Problem B")
SAT = _pb[0] + 0.85                          # hops up and sits on the middle of the bundle
STRAIN = _lpb["t1"] - 0.3                    # sits down HARD: the bundle bows under him...
LAUNCH = max(STRAIN + 0.75, _pb[0] + 3.0)    # ...and springs back: BOING, up he goes
PB_SPLIT = min(LAUNCH + 0.55, _pb[1] - 1.4)  # cut while he is high in the air; he falls into the next shot
LANDED = PB_SPLIT + 0.75
_ltw = [L for L in LINES if L["section"] == "Twist"]
TW_SPLIT = max(_ltw[1]["t0"] - 0.15, _tw[0] + 1.4) if len(_ltw) > 1 else _tw[0] + 1.5 * BAR
TIP = TW_SPLIT + 0.35                        # he tips the bundle over the stream...
THUMP = TIP + 0.8                            # ...it lands on the far bank
CROSS0, CROSS1 = THUMP + 0.3, _tw[1] - 0.2   # and he walks across it
SETUPB_SPLIT = _sb[0]
SHOTS = [(0.0, _h[1], "hook_snap"), (_s[0], _s[1], "title_wide"), (_sa[0], _sa[1], "pip_ask"),
         (_sb[0], _sb[1], "watch_me"), (_pa[0], _pa[1], "pull_push"), (_pb[0], PB_SPLIT, "sit_boing"),
         (PB_SPLIT, _pb[1], "land"), (_tw[0], TW_SPLIT, "pip_idea"), (TW_SPLIT, _tw[1], "bridge"),
         (_m[0], _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

HIGH_FIVE = _c[1] - 0.9
SPOKEN = [dict(file="s00_tumble", who="tumble", t0=LAUNCH + 0.1, caption="Whoa-oa!", tags="[surprised] [whoosh]"),
          dict(file="s01_tumble", who="tumble", t0=LANDED + 0.35, caption="It went BOING!", tags="[dizzy] [amazed]"),
          dict(file="s02_both", who="both", t0=_bt[0] + 0.9, caption="Bye-bye!", tags="[cheerful]")]
