"""Timeline for one Story Stump scene of the long-form episode v2 (16:9). SCENE (env) picks the scene.

Reads ../audio/<SCENE>.json (written by ../build_audio.py: real TTS word times, pauses, actions, picture inserts) and
plans the shots from it: who speaks, whether they talk to the audience, picture-quiz inserts, book actions, the dance.
The renderer (render.py) and the kit (fablekit.py) read everything from here."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); EP2 = os.path.dirname(HERE)
sys.path.insert(0, EP2)
import script as S

FPS = 30
SCENE = os.environ.get("SCENE", "intro")
JOB = f"ep2_{SCENE}"
ASPECT = "wide"
W, H = 1920, 1080
BPM = 100.0
BAR = 2.4
TITLE = "Tumble & Pip"
SERIES_TAG = "Fables"
TITLE_SHOT = "title_wide"
TITLE_PARTS = [("Fables About ", 92, "white"), ("Friendship", 92, "gold")]
WORD_STYLE = {"tiny": (0.85, "tiny"), "small": (0.85, "tiny"), "big": (1.25, "big"), "helpers": (1.25, "big"),
              "sour": (1.15, "sour"), "sweet": (1.15, "sweet"), "friend": (1.1, "gold"), "friends": (1.1, "gold"),
              "strong": (1.2, "big"), "kind": (1.1, "gold"), "share": (1.1, "gold"), "goodnight": (1.1, "gold")}
SPOKEN = []
SMALL_CAPTIONS = True
END_FADE = False                    # scenes dissolve into each other in assemble.py
ALIGNED = True
_C = json.load(open(os.path.join(EP2, "audio", f"{SCENE}.json")))
MODE = _C["mode"]; DURATION = float(_C["duration"]); FABLE = _C.get("fable")
PAGE_FROM, PAGE_TO = _C.get("page_from"), _C.get("page_to")
CLOSED_BOOK = _C.get("closed_book", False); NIGHT = _C.get("night", False)
PAUSES, ACTS, PAGES = _C["pauses"], _C["acts"], _C["pages"]

def _norm(s): return re.sub(r"[^a-z ]", "", s.lower()).strip()
LINES = []
for i, L in enumerate(_C["lines"]):
    sec = L["sec"]
    frag = _norm(L["line"].replace("...", " "))
    for n, m in S.MORALS.items():                       # call-and-response halves of a moral get the yellow moral card
        if len(frag) > 8 and frag in _norm(m) and L["kind"] == "tts": sec = "Moral"
    LINES.append(dict(i=i, who=L["who"], text=L["line"], section=sec, kind=L["kind"], words=L["words"],
                      t0=L["words"][0]["t0"], t1=L["words"][-1]["t1"], tg=L.get("tg"), pg=L.get("pg"), look=L.get("look", "other")))
LINES.sort(key=lambda L: L["t0"])
TALK = [L for L in LINES if L["kind"] == "tts"]
def act(name):
    return next((a for a in ACTS if a["name"] == name), None)
def line(section, who=None):
    for L in LINES:
        if L["section"] == section and (who is None or L["who"] == who): return L
def word_times(word, lines=None):
    k = word.lower()
    return [w["t0"] for L in (lines or LINES) for w in L["words"] if re.sub(r"[^a-z]", "", w["w"].lower()) == k]

# ---------------- dance: the two chorus high-fives ----------------
DANCE = act("dance")
HIGH_FIVES = []
if DANCE:
    for (n, a, b) in DANCE["sections"]:
        if n.startswith("Chorus"):
            CL = [L for L in LINES if L["kind"] == "song" and a - 0.1 <= L["t0"] < b]
            HIGH_FIVES.append((CL[-1]["t1"] - 0.25) if CL else b - 0.9)
HIGH_FIVE = HIGH_FIVES[-1] if HIGH_FIVES else -10.0
RECAP = act("recap_song")

# ---------------- book events ----------------
OPEN = act("open_book")["t0"] if act("open_book") else None
CLOSE = act("close_book")["t0"] if act("close_book") else None
TURNS = []
if act("turn_page"): TURNS.append((act("turn_page")["t0"], 1))
if RECAP:
    RL = [L for L in LINES if L["kind"] == "song" and RECAP["t0"] <= L["t0"] < RECAP["t1"] and L["who"] != "both"]
    for k, L in enumerate(RL): TURNS.append((max(L["t0"] - 0.95, RECAP["t0"] + 0.2 if k == 0 else 0), k + 1))
    TURNS.append((RL[-1]["t1"] + 1.2 if RL else RECAP["t0"] + 1, len(RL) + 1))

# ---------------- shot plan ----------------
def _spk(who): return {"tumble": "t", "pip": "p"}.get(who, "both")
def _plan():
    ev = []                                   # (t0, t1, kind)
    in_page = lambda t: any(p["t0"] - 0.05 <= t < p["t1"] for p in PAGES)
    last = None; alt = 0
    for n_, L in enumerate(TALK):
        s = _spk(L["who"])
        if in_page(L["t0"]):                      # quiz: questions on the picture, answers on the character
            k = "page" if L["look"] == "cam" else ("cu_" + s if s != "both" else "two")
            ev.append((L["t0"] - 0.12, L["t1"], k)); last = k; continue
        if n_ == 0 and MODE != "read" and not DANCE: k = "wide"
        elif MODE == "read":
            if L["look"] == "book": k = "r_spread"
            elif L["look"] == "cam": k = "r_aud" if s != "p" else "r_cu_p"
            elif s == "both": k = "r_two"
            else: k = ("r_med", "r_two", "r_cu_p" if s == "p" else "r_med")[alt % 3]; alt += 1
        else:
            if L["look"] == "cam": k = "aud_" + s if s != "both" else "two"
            elif s == "both": k = "two"
            else:
                k = "cu_" + s if last == "two" else "two"
        ev.append((L["t0"] - 0.12, L["t1"], k)); last = k
    for P in PAUSES:
        ev.append((P["t0"], P["t1"], "page" if in_page(P["t0"]) else None))   # a pause holds the previous shot
    for A in ACTS:
        if A["name"] in ("open_book", "turn_page"): ev.append((A["t0"] - 0.3, A["t1"] + 0.2, "r_spread"))
        elif A["name"] == "close_book": ev.append((A["t0"] - 0.3, A["t1"] + 0.2, "r_two"))
        elif A["name"] == "pip_arrive": ev.append((0.0, A["t1"] + 0.3, "title_wide"))
        elif A["name"] == "dance":
            for (n, a, b) in A["sections"]:
                k = "chorus" if n.startswith("Chorus") else ("d_wide" if n in ("Intro", "Button") else "d_med")
                ev.append((a, b, k))
        elif A["name"] == "recap_song":
            for (n, a, b) in A["sections"]:
                k = "r_spread" if n.startswith("Moral") and int(n.split()[1]) % 2 == 0 else ("r_med" if n.startswith("Moral") else "r_two")
                ev.append((a, b, k))
    ev.sort(key=lambda e: e[0])
    shots = []; cur = "wide" if MODE != "read" else "r_two"
    if CLOSED_BOOK: cur = "title_wide"
    t = 0.0
    for (a, b, k) in ev:
        if k is None: continue
        a = max(a, t)
        if not shots: shots.append([0.0, a, cur])
        if k != shots[-1][2]:
            if a - shots[-1][0] < 1.4 and len(shots) > 1 and k != "page" and shots[-1][2] != "page":
                shots[-1][2] = k if shots[-1][2] not in ("title_wide", "chorus") else shots[-1][2]   # too short: merge
                if shots[-1][2] == k: continue
            shots[-1][1] = a; shots.append([a, b, k])
        t = a
    shots[-1][1] = DURATION + 0.1
    for i in range(len(shots) - 1): shots[i][1] = shots[i + 1][0]
    shots = [s for s in shots if s[1] - s[0] > 0.05]
    out = []
    for i, (a, b, k) in enumerate(shots):
        nm = k if k in ("title_wide", "chorus") else f"{k}:{i}"
        out.append((round(a, 3), round(b, 3), nm))
    return out
SHOTS = _plan()
if TITLE_SHOT not in [n for _, _, n in SHOTS]: SHOTS.append((-2.0, -1.0, TITLE_SHOT))
SHOTS.sort(key=lambda s: s[0])
def shot_at(t):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= t < b: return i, n, (t - a) / max(b - a, 1e-6), t - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, t - SHOTS[-1][0]
def kind_at(t): return shot_at(t)[1].split(":")[0]

# ---------------- where this scene sits in the episode: golden afternoon -> starry night ----------------
def _lengths():
    out = []
    for it in S.ORDER:
        if isinstance(it, int): out.append((it, 50.4))
        else:
            p = os.path.join(EP2, "audio", f"{it}.json")
            out.append((it, json.load(open(p))["duration"] if os.path.exists(p) else 60.0))
    return out
_L = _lengths(); _TOT = sum(d for _, d in _L)
EP_START = sum(d for it, d in _L[:[it for it, _ in _L].index(SCENE)])
def dusk(t):
    u = (EP_START + t) / _TOT
    pts = [(0.0, 0.0), (0.5, 0.33), (0.8, 0.6), (0.93, 0.8), (1.0, 1.0)]
    for (a, va), (b, vb) in zip(pts[:-1], pts[1:]):
        if u <= b: return va + (vb - va) * (u - a) / (b - a)
    return 1.0
