"""Timeline for 'Tumble & Pip Fables 1: Tiny Pip, Big Help!' (Batch 01, Fables About Friendship).

Single source of truth for audio and video. The song is built on a 100 BPM grid (one bar = 2.4 s) from three parts:
the stored theme sting, this fable's verse take (ElevenLabs Music) and the stored moral chorus.

When out/song_check.json exists (written after the ElevenLabs take is chosen and force-aligned), every section and
word time comes from it. Until then the planned grid below is used with estimated word times, which is enough for
staging, stills and an animatic. Nothing else in the code changes when the real song arrives.

ASPECT=short (default) renders the 1080x1920 Short; ASPECT=wide renders the 1920x1080 episode framing."""
import json, math, os, re

FPS = 30
ASPECT = os.environ.get("ASPECT", "short")
W, H = (1080, 1920) if ASPECT == "short" else (1920, 1080)
BPM = 100.0
BAR = 4 * 60.0 / BPM                       # 2.4 s
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
SUBTITLE = "Tiny Pip, Big Help!"
SOURCE = "Based on Aesop's fable The Lion and the Mouse"

# (section, start bar, end bar, part) -- part: sting / verse / chorus are the three audio sources
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
# sung lines: (section, who, text). 'both' = duet.
PLAN_LINES = [
    ("Hook",      "tumble", "Up, up, up goes my big kite!"),
    ("Sting",     "both",   "Tumble and Pip!"),
    ("Setup A",   "pip",    "Can I help? I'm good at things!"),
    ("Setup B",   "tumble", "This kite's too big for tiny wings!"),
    ("Problem A", "tumble", "Whoosh! The wind goes round and round,"),
    ("Problem B", "tumble", "now Tumble's tangled on the ground!"),
    ("Twist",     "pip",    "I can help! Peck, peck, peck!"),
    ("Moral",     "tumble", "Tiny friends can be BIG helpers!"),
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
    # Breathing space between the moral line and the chorus: the final mix has GAP seconds of ring-out inserted at
    # GAP_AT (the end of the Moral), so everything from there on is later by GAP. The Moral section runs on over it.
    GAP_AT, GAP = 38.4, 1.5
    def _sh(t, strict=False): return t + GAP if t > GAP_AT - 1e-6 else t
    SECTIONS = [(n, a if a < GAP_AT - 1e-6 else a + GAP, b + GAP if b > GAP_AT - 1e-6 else b) for n, a, b in _C["sections"]]
    LINES = [dict(i=i, who=L["who"], text=L["line"], section=L["sec"],
                  words=[dict(w=w["w"], t0=_sh(w["t0"]), t1=_sh(w["t1"])) for w in L["words"]]) for i, L in enumerate(_C["lines"])]
else:
    SECTIONS = [(n, a * BAR, b * BAR) for n, a, b, _ in PLAN_SECTIONS]
    LINES = []
    sec_pos = {}
    for i, (sname, who, text) in enumerate(PLAN_LINES):
        a, b = next((x, y) for n, x, y in SECTIONS if n == sname)
        t = sec_pos.get(sname, a + 0.2)                  # a line starts on the section's first beat (small pickup)
        words = []
        for w in text.split():
            d = _syllables(w) / 3.0                      # 3 sung syllables per second (budget: 3.5 max)
            words.append(dict(w=w, t0=round(t, 3), t1=round(t + d * 0.9, 3)))
            t += d + (0.25 if w.endswith((",", "!", "?")) else 0.0)
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

# spoken gag lines in the fixed cast voices (eleven_v3, audio tags, stability 0.0)
_pb, _tw = sec("Problem B"), sec("Twist")
GAG_UHOH = line("Problem B")["t1"] + 0.9
GAG_WHEE = _tw[0] + 4.3
SPOKEN = [dict(file="s00_tumble", who="tumble", t0=GAG_UHOH, caption="Uh-oh! Help!", tags="[surprised] [wobbly]"),
          dict(file="s01_tumble", who="tumble", t0=GAG_WHEE, caption="Wheee!", tags="[delighted] [spinning]"),
          dict(file="s02_both", who="both", t0=sec("Button")[0] + 0.7, caption="Bye-bye!", tags="[cheerful]")]

# shots: (t0, t1, name). Cuts sit on section boundaries or on bar lines inside a section.
_h, _s, _sa, _sb = sec("Hook"), sec("Sting"), sec("Setup A"), sec("Setup B")
_pa, _m, _c, _bt = sec("Problem A"), sec("Moral"), sec("Chorus"), sec("Button")
PB_SPLIT = _pb[0] + 1.5 * BAR              # topple seen from the side, then overhead once he's down
# peck close-up, then the wide spin-out. The cut is the first half-bar line at least 0.5 s after the last sung "peck"
# (room for the knot to pop). The real take sings the pecks late in the Twist (after its instrumental break), so the
# spin-out runs on over the Moral's first bars and the moral shot starts on the last half-bar line at or just before
# the sung "Tiny", at least 1.9 s after the spin-out starts and a bar before the Moral ends.
HALF = BAR / 2
_pk = word_times("peck", "Twist")
TW_SPLIT = _tw[0] + 1.5 * BAR if not _pk else _tw[0] + math.ceil((_pk[-1] + 0.5 - _tw[0]) / HALF - 1e-6) * HALF
_tiny = line("Moral")["t0"]
MORAL_CUT = math.floor((_tiny + 0.1) / HALF + 1e-6) * HALF
MORAL_CUT = min(max(MORAL_CUT, _m[0], TW_SPLIT + 1.9), _m[1] - BAR)
SHOTS = [(0.0, _h[1], "hook_track"), (_s[0], _s[1], "title_wide"), (_sa[0], _sa[1], "pip_ask"),
         (_sb[0], _sb[1], "tumble_no"), (_pa[0], _pa[1], "gust"), (_pb[0], PB_SPLIT, "topple"),
         (PB_SPLIT, _pb[1], "overhead_tangled"), (_tw[0], TW_SPLIT, "peck"), (TW_SPLIT, MORAL_CUT, "spin_out"),
         (MORAL_CUT, _m[1], "moral"), (_c[0], _c[1], "chorus"), (_bt[0], DURATION + 0.1, "button_crane")]
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]

# story events, all from word times so they follow the real alignment
PECKS = word_times("peck", "Twist")
WHOOSH = (word_times("whoosh", "Problem A") or [_pa[0] + 0.2])[0]
KNOT_POP = min((PECKS[-1] if PECKS else _tw[0] + 2.5) + 0.45, TW_SPLIT - 0.35)   # pop and puff seen before the cut
GUST0, GUST1 = WHOOSH - 0.2, _pa[1] - 0.3             # kite swoops and circles Tumble
TOPPLE = (word_times("tangled", "Problem B") or [_pb[0] + 1.4])[0]   # he tips over on "tangled", lands by "ground"
SPIN0 = TW_SPLIT + 0.45                                     # Pip hops clear first, then Tumble rises and spins
SPIN1 = min(TW_SPLIT + 2.2, MORAL_CUT - 0.5)                # and is dizzy for at least half a second before the cut
GAG_WHEE = TW_SPLIT + 0.7; SPOKEN[1]["t0"] = GAG_WHEE      # "Wheee!" as he starts to spin (mix v2: spliced from the song-only audio)
HIGH_FIVE = _c[1] - 0.9
