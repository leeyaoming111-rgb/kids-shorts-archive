"""Tumble & Pip Fables 1: Tiny Pip, Big Help!  Shot-based 3D claymation renderer (Batch 01).

python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | seg f0 f1 out.mp4 | sheet | qa

--wide     1920x1080 episode framing (same scene, same timing, cameras re-fitted for 16:9)
--preview  half resolution, 2x MSAA, for fast CPU stills and animatics

Every shot frames a world-space box (fit_w, fit_h half sizes around its target). The camera distance is solved per
aspect so the box fits: width decides in 9:16, height decides in 16:9. A shot can still override anything per aspect."""
import os, sys
if "--wide" in sys.argv: os.environ["ASPECT"] = "wide"; sys.argv.remove("--wide")
PREVIEW = "--preview" in sys.argv
if PREVIEW: sys.argv.remove("--preview")
import timeline as T
if PREVIEW:
    T.W, T.H = T.W // 2, T.H // 2
from render_base import *
import re
WIDE = T.ASPECT == "wide"
K = min(W, H) / 1080.0                      # overlay scale (1.0 at full size, 0.5 in preview)

def lerp(a, b, u): return np.asarray(a, float) * (1 - u) + np.asarray(b, float) * u
def clampu(t, a, b): return min(max((t - a) / max(b - a, 1e-6), 0.0), 1.0)
def apply(M, p): return (M @ np.array([p[0], p[1], p[2], 1.0]))[:3]
SH = {n: (a, b) for a, b, n in T.SHOTS}
BEAT = 60.0 / T.BPM

FOXP = {k: Mesh(p["mesh"]) for k, p in D["fox"]["parts"].items() if "mesh" in p}
FOXD = D["fox"]["parts"]
PIPP = {k: Mesh(p["mesh"]) for k, p in D["pip"]["parts"].items() if "mesh" in p}
PIPD = D["pip"]["parts"]
PR = {k: Mesh(m) for k, m in D["props"].items()}
SC = {k: Mesh(m) for k, m in D["scene"].items()}
E2 = {k: Mesh(m) for k, m in D["ep2"].items()}
EYE_W, EYE_P = Mesh(D["eye_w"]), Mesh(D["eye_p"])

# ---------------- world layout (Picnic Meadow, a new corner by the stump) ----------------
STUMP = (2.7, -1.0); STUMP_TOP = 0.55 - 0.02
TPOS = (1.2, -0.35)                         # Tumble's kite-flying spot
APPLE_TREE = (-3.6, -3.4)
COTTAGE_FAR = (7.5, -17.0)
MUSH = [(3.5, -0.2, 0.2), (3.2, 0.25, 0.14), (0.2, -1.6, 0.18)]
KITE_SKY = np.array([TPOS[0] + 1.5, 4.7, TPOS[1] - 2.6])      # on his paw side, so the string never crosses his face
KITE_REST = (TPOS[0] - 1.3, TPOS[1] + 1.6)          # in front of his head side, clear of the body when he falls
STRING_FREE = (TPOS[0] + 0.95 * math.cos(0.9), TPOS[1] + 0.95 * math.sin(0.9))            # the loose end of the string on the grass after the spin-out (spiral start)
GRAB = 0.9                                          # button: Pip picks the string up at this time into the shot
GRAB_PT = np.array([KITE_REST[0] + 0.85, ground_h(KITE_REST[0] + 0.85, KITE_REST[1] - 0.35) + 0.0, KITE_REST[1] - 0.35])   # on the string, beside the resting kite
rng = np.random.default_rng(21)
FLOWERS = []
pastel = [(1.0, .72, .82), (1.0, .85, .6), (.78, .72, 1.0), (.7, .86, 1.0), (1.0, 1.0, 1.0), (1.0, .78, .7)]
while len(FLOWERS) < 80:
    x, z = rng.uniform(-8, 8), rng.uniform(-9, 3.5)
    if (x - TPOS[0]) ** 2 + (z - TPOS[1]) ** 2 < 2.6: continue
    if (x - STUMP[0]) ** 2 + (z - STUMP[1]) ** 2 < 1.4: continue
    if (x - KITE_REST[0]) ** 2 + (z - KITE_REST[1]) ** 2 < 1.0: continue
    if (x - APPLE_TREE[0]) ** 2 + (z - APPLE_TREE[1]) ** 2 < 1.4: continue
    if -6.6 < z < -4.4: continue
    if 0.2 < z < 1.4 and -3.0 < x < 1.2: continue          # the hook's running lane
    FLOWERS.append((x, z, rng.uniform(0, 6.28), pastel[len(FLOWERS) % 6], rng.uniform(0.9, 1.4)))
SKY = ((0.46, 0.72, 0.97), (0.70, 0.86, 1.0), (1.0, 0.93, 0.86))
def surf(x, z): return ground_h(x, z)
def gust_amt(t):
    return clampu(t, T.GUST0 - 0.3, T.GUST0 + 0.4) * (1 - clampu(t, T.GUST1 - 0.2, T.GUST1 + 0.8))

# ---------------- mouths from word times (sung lines + spoken gags) ----------------
def mouth_track(who):
    n = int(T.DURATION * FPS) + 2; m = np.zeros(n)
    for L in T.LINES:
        if L["who"] not in (who, "both"): continue
        for w in L["words"]:
            a, b = int(w["t0"] * FPS), int(max(w["t1"], w["t0"] + 0.18) * FPS)
            for f in range(a, min(b + 1, n)):
                m[f] = max(m[f], math.sin(math.pi * (f - a + 0.5) / (b - a + 1)) * 0.95)
    for s in T.SPOKEN:
        if s["who"] not in (who, "both"): continue
        a, b = int(s["t0"] * FPS), int((s["t0"] + 0.75) * FPS)
        for f in range(a, min(b + 1, n)): m[f] = max(m[f], 0.6 + 0.35 * math.sin((f - a) * 0.9))
    return m
MOUTH = {}
for w_ in ("tumble", "pip"):
    p_ = f"out/mouth_{w_}.json"
    MOUTH[w_] = json.load(open(p_)) if (T.ALIGNED and os.path.exists(p_)) else mouth_track(w_).tolist()

# ---------------- Tumble ----------------
COIL_TURNS = 4.6
def wrap_amt(t):
    """how much string is coiled round Tumble (0..1)"""
    if t < T.GUST0 + 0.9: return 0.0
    if t < T.GUST1: return ease(clampu(t, T.GUST0 + 0.9, T.GUST1 - 0.4))
    if t < T.SPIN0: return 1.0
    return 1.0 - ease(clampu(t, T.SPIN0, T.SPIN1 - 0.2))
def lying_amt(t):
    if t < T.TOPPLE: return 0.0
    if t < T.SPIN0: return clampu(t, T.TOPPLE, T.TOPPLE + 0.55) ** 2       # falls with gravity
    return 1.0 - ease(clampu(t, T.SPIN0, T.SPIN0 + 0.4))

def tumble(t):
    st = dict(x=TPOS[0], z=TPOS[1], yaw=-0.25, y=0.0, sq=0.015 * math.sin(t * 3.7), roll=0.0, lie=0.0,
              head=[0.0, 0.05 * math.sin(t * 1.3), 0.0], arms=[[0.35, 1.0], [0.15, 0.0]], legs=[0.0, 0.0],
              tail=0.25 * math.sin(t * 2.6), hold=True)
    n = T.shot_at(t)[1]
    w = wrap_amt(t)
    if n == "hook_track":
        u = clampu(t, 0.15, 3.0); p0, p1 = (-2.6, 0.85), TPOS
        st["x"], st["z"] = lerp(p0, p1, ease(u))
        if u < 1:
            ph = t * 2 * math.pi * 2.3
            st["y"] += 0.06 * abs(math.sin(ph)); st["legs"] = [0.1 * max(0, math.sin(ph)), 0.1 * max(0, -math.sin(ph))]
            st["yaw"] = math.atan2(p1[0] - p0[0], p1[1] - p0[1]) * (1 - ease(clampu(t, 2.5, 3.0))) - 0.25 * ease(clampu(t, 2.5, 3.0))
        k_ = (T.word_times("kite", "Hook") or [2.65])[0]
        lift = clampu(t, k_ - 0.1, k_ + 0.8)                                # the kite tugs him up on the sung "kite!"
        if 0 < lift < 1:
            st["y"] += 0.62 * math.sin(math.pi * lift); st["legs"] = [0.12, 0.05]; st["sq"] += 0.06 * math.sin(math.pi * lift)
        st["arms"][0] = [0.45, 1.35 + 0.15 * lift]
        st["head"][0] = -0.2
    elif n == "title_wide":
        a, b = SH[n]
        st["arms"][1] = [2.3 + 0.35 * math.sin((t - a) * 9), 0.25]           # waves hello
        st["head"][0] = -0.05
    elif n == "pip_ask":
        st["head"][0] = -0.25; st["yaw"] = 0.6                              # turned towards the kite, tail swung away from Pip
        st["arms"][0] = [0.4, 1.25 + 0.08 * math.sin(t * 2)]
    elif n == "tumble_no":
        a, b = SH[n]
        u = ease(clampu(t, a, a + 0.6))
        st["yaw"] = lerp(0.6, math.atan2(STUMP_PIP[0] - TPOS[0], STUMP_PIP[2] - TPOS[1]) - 0.35, u)   # turns to Pip on the stump
        L = T.line("Setup B")
        if L["t0"] - 0.2 < t < L["t1"] + 0.6:                                # kind, wrong: chuckles and shakes his head
            k = (t - L["t0"])
            st["head"][1] = 0.22 * math.sin(k * 7.5) * clampu(t, L["t0"] - 0.2, L["t0"] + 0.2)
            st["y"] += 0.03 * abs(math.sin(k * 9)); st["arms"][1] = [0.7, 1.15]
        st["arms"][0] = [0.45, 1.3]
    elif n == "gust":
        a, b = SH[n]
        g = gust_amt(t)
        st["roll"] = 0.07 * g * math.sin(t * 11); st["head"][0] = -0.15
        ang = kite_orbit_angle(t)
        if ang is not None:                                                 # he turns as the kite circles him
            st["yaw"] = 0.15 + 0.3 * math.sin(ang) * (1 - w)                # turns away from the stump side
        low = ease(clampu(t, T.GUST0 - 0.1, T.GUST0 + 0.35))                # clutches the string low at his waist as the wind hits
        st["arms"][0] = lerp(lerp([0.45, 1.3], [0.35, 0.5], low), [0.06, 0.05], ease(clampu(w, 0.0, 0.5)))
        st["arms"][1] = lerp([0.15, 0.0], [0.06, 0.05], ease(clampu(w, 0.0, 0.5)))
        st["legs"] = [0.04 * g * max(0, math.sin(t * 13)), 0.04 * g * max(0, -math.sin(t * 13))]
        st["hold"] = w < 0.05
    elif n in ("topple", "overhead_tangled", "peck"):
        st["arms"] = [[0.06, 0.05], [0.06, 0.05]]; st["hold"] = False
        if t < T.TOPPLE:                                                    # tiny wrapped hops, wobbling
            hp = (t - SH["topple"][0]) * 2 * math.pi * 1.6
            st["y"] += 0.09 * abs(math.sin(hp)); st["roll"] = 0.12 * math.sin(hp * 0.5); st["yaw"] = -0.25
        else:
            st["lie"] = lying_amt(t); st["yaw"] = -0.25
            d = t - (T.TOPPLE + 0.55)
            if 0 <= d < 0.5: st["sq"] -= 0.12 * math.exp(-d * 8) * math.cos(d * 22)          # bump on landing
            if d > 0.5:                                                     # rocks like a log, feet kicking
                st["roll"] = 0.1 * math.sin(d * 4.2) * math.exp(-max(0.0, t - T.KNOT_POP) * 3)
                kick = math.sin(d * 14) if t < SH["peck"][0] else 0.3 * math.sin(d * 6)
                st["legs"] = [0.08 * max(0, kick), 0.08 * max(0, -kick)]
        st["head"][0] = -0.1
    elif n == "spin_out":
        a, b = SH[n]
        st["arms"] = [[0.06 + 1.6 * ease(clampu(t, T.SPIN1 - 0.3, T.SPIN1 + 0.2)), 0.3], [0.06 + 1.6 * ease(clampu(t, T.SPIN1 - 0.3, T.SPIN1 + 0.2)), 0.3]]
        st["hold"] = False; st["lie"] = lying_amt(t)
        u = clampu(t, T.SPIN0 + 0.4, T.SPIN1)                              # stands up first, then spins
        st["yaw"] = -0.25 + 2 * math.pi * 3 * (1 - (1 - u) ** 2)              # unwinds like a top, slowing down
        st["y"] += 0.35 * math.sin(math.pi * clampu(t, T.SPIN0 + 0.3, T.SPIN1))
        d = t - T.SPIN1
        if d > 0:                                                           # dizzy, then a happy laugh
            st["roll"] = 0.16 * math.sin(d * 7) * math.exp(-d * 1.4)
            st["head"][2] = 0.2 * math.sin(d * 7 + 1) * math.exp(-d * 1.4)
            st["y"] += 0.03 * abs(math.sin(d * 10)) * clampu(d, 0.8, 1.0)
    elif n == "moral":
        a, b = SH[n]
        st["yaw"] = -0.05; st["hold"] = False
        st["arms"] = [[1.3, 0.35], [0.15, 0.0]]                           # Pip sits on his raised paw, clear of his face
        st["head"][0] = -0.05; st["head"][2] = 0.08          # paw out at shoulder height, head tipped away (pose solved for clearance)
        L = T.line("Moral")
        if L and L["t0"] < t < L["t1"] + 0.3: st["y"] += 0.025 * abs(math.sin((t - L["t0"]) * 8))
    elif n == "chorus":
        a, b = SH[n]
        st["yaw"] = -0.05; st["hold"] = False
        sway = math.sin(2 * math.pi * (t - a) / (2 * BEAT))                   # sway on every second beat, Pip riding his paw
        st["roll"] = 0.06 * sway; st["head"][2] = 0.1                                  # tips away from Pip (positive roll moves the crown to -x)
        st["arms"] = [[1.3, 0.35], [0.6 - 0.3 * sway, 0.3]]
        hc = hf_curves(t)
        if hc: st["arms"][0] = [paw_side_for_rise(hc[1]), 0.35]                # paw comes up to meet Pip's wing
    elif n == "button_crane":
        a, b = SH[n]
        st["yaw"] = -0.05; st["hold"] = False
        ph = (t - a) * 2 * math.pi * 1.5
        up_ = ease(clampu(t, a + 0.45, a + 0.8))                           # the paw Pip leaves from rises only once he is clear
        st["arms"] = [[lerp(1.3, 2.4 + 0.25 * math.sin(ph), up_), lerp(0.35, 0.2, up_)], [2.4 + 0.25 * math.sin(ph + 1), 0.2]]   # cheers
        st["y"] += 0.08 * abs(math.sin(ph * 0.5)); st["head"][0] = -0.3 * up_; st["head"][2] = 0.1 * (1 - up_)   # keeps the chorus tilt until Pip is clear
    if n in ("chorus", "button_crane", "moral"): st["x"], st["z"] = TPOS
    return st

FOX_SIDE_LIFT = 0.6                     # lying on his side: lowest point of the rotated model sits at the ground
def fox_mats(st):
    gy = surf(st["x"], st["z"])
    sq = st["sq"]; lie = st["lie"]
    tip = lie * math.pi / 2                                                # tips onto his left side, away from the stump
    lift = FOX_SIDE_LIFT * abs(math.sin(tip)) + 0.22 * abs(math.sin(st["roll"]))
    R = trans(st["x"], gy - 0.01 + st["y"] + lift, st["z"]) @ roty(st["yaw"]) @ rotz(tip + st["roll"]) @ scale(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5)
    hp = FOXD["head"]["pivot"]; hd = st["head"]
    Mh = R @ trans(*hp) @ rotx(hd[0]) @ roty(hd[1]) @ rotz(hd[2]) @ trans(*(-np.array(hp)))
    arms = []
    for ai in range(2):
        pv = FOXD[f"arm{ai}"]["pivot"]; sgn = 1 if ai == 0 else -1
        side, fwd = st["arms"][ai]
        arms.append(R @ trans(*pv) @ rotz(sgn * side) @ rotx(-fwd) @ trans(*(-np.array(pv))))
    legs = []
    for li in range(2):
        pv = FOXD[f"leg{li}"]["pivot"]
        legs.append(R @ trans(0, st["legs"][li], 0) @ trans(*pv) @ trans(*(-np.array(pv))))
    return R, Mh, arms, legs

# ---------------- kite ----------------
ORBIT_A, ORBIT_B = T.GUST0 + 0.5, T.GUST1 - 0.5
def kite_orbit_angle(t):
    if not (ORBIT_A <= t <= ORBIT_B): return None
    return 1.0 + 2 * math.pi * 2.34 * ease(clampu(t, ORBIT_A, ORBIT_B))   # starts on his paw side; 2.34 loops end behind him
def kite_state(t, st):
    """kite position and rotation; the kite is a diamond in its local xy plane"""
    bob = np.array([0.25 * math.sin(t * 1.1), 0.18 * math.sin(t * 1.7), 0.0])
    if t < SH["hook_track"][1]:
        u = ease(clampu(t, 0.0, 3.2))
        p = lerp(np.array([st["x"] - 1.4, 1.2, st["z"] - 1.0]), KITE_SKY, u) + bob
        return p, roty(0.35) @ rotz(0.25 * math.sin(t * 2.2)) @ rotx(-0.35)
    if t < ORBIT_A:
        p = KITE_SKY + bob
        u = clampu(t, T.GUST0, ORBIT_A)                                     # swoop down towards Tumble
        p = lerp(p, orbit_pos(ORBIT_A), ease(u))
        return p, roty(0.35) @ rotz(0.25 * math.sin(t * 2.2) + 1.2 * u) @ rotx(-0.35)
    if t <= ORBIT_B:
        return orbit_pos(t), roty(kite_orbit_angle(t) + math.pi / 2) @ rotz(0.4 * math.sin(t * 7)) @ rotx(-0.3)
    rest = np.array([KITE_REST[0], surf(*KITE_REST) + 0.06, KITE_REST[1]])
    Mrest = roty(0.6) @ rotx(-math.pi / 2)                                   # lying face up in the grass
    if t < SH["button_crane"][0] + GRAB + 0.3:
        u = clampu(t, ORBIT_B, ORBIT_B + 0.9)
        if u < 1:                                                           # flutters down round behind him, never across his face
            p0, p2 = orbit_pos(ORBIT_B), rest
            via = np.array([TPOS[0] - 1.9, 3.4, TPOS[1] - 2.1])
            e = ease(u)
            p = (1 - e) ** 2 * p0 + 2 * (1 - e) * e * via + e ** 2 * p2
            return p, roty(0.6) @ rotx(-math.pi / 2 * e - 0.3 * (1 - e))
        return rest, Mrest
    u = ease(clampu(t, SH["button_crane"][0] + GRAB + 0.1, SH["button_crane"][1]))     # Pip pulls it up into the sky again, on his left
    p = lerp(rest, np.array([TPOS[0] - 2.2, 4.3, TPOS[1] + 0.1]), u) + bob * u
    p[1] = lerp(rest[1], 4.2, u ** 0.45)                                      # lifts straight up first, clear of his head
    return p, roty(0.6 * (1 - u) + 0.2 * u) @ rotx(-math.pi / 2 * (1 - u) - 0.35 * u)
def orbit_pos(t):
    ang = kite_orbit_angle(min(max(t, ORBIT_A), ORBIT_B))
    u = clampu(t, ORBIT_A, ORBIT_B)
    r = lerp(2.5, 1.75, u); hgt = lerp(2.0, 1.25, u)                     # circles low, so the string from his waist stays below his face
    return np.array([TPOS[0] + r * math.sin(ang), hgt + 0.15 * math.sin(t * 5), TPOS[1] + r * math.cos(ang)])

# ---------------- string ----------------
COIL_RX, COIL_RZ, COIL_Y0, COIL_Y1 = 0.62, 0.47, 1.0, 0.42
def coil_points(R, w, loosen=0.0):
    """points of the coiled part (local helix on Tumble's body), from the top end (start) down"""
    if w <= 0.002: return []
    nseg = max(2, int(70 * w))
    th = np.linspace(0, 2 * math.pi * COIL_TURNS * w, nseg)
    yy = COIL_Y0 + (COIL_Y1 - COIL_Y0) * th / (2 * math.pi * COIL_TURNS)
    k = 1.0 + loosen
    return [apply(R, (COIL_RX * k * math.sin(a), y, COIL_RZ * k * math.cos(a))) for a, y in zip(th, yy)]
def sag_line(a, b, sag, n=24, ground=True):
    pts = []
    for s in np.linspace(0, 1, n):
        p = lerp(a, b, s); p[1] -= sag * 4 * s * (1 - s)
        if ground: p[1] = max(p[1], surf(p[0], p[2]) + 0.015)
        pts.append(p)
    return pts
PILE_A0 = 0.9                                  # the loose string's spiral starts front-right of Tumble, clear of the stump
def ground_spiral(c, r0, r1, turns, n=40):
    return [np.array([c[0] + r * math.cos(a), surf(c[0] + r * math.cos(a), c[1] + r * math.sin(a)) + 0.015, c[1] + r * math.sin(a)])
            for a, r in zip(PILE_A0 + np.linspace(0, 2 * math.pi * turns, n), np.linspace(r0, r1, n))]
def string_path(t, st, mats, kite_p, pip_beak):
    R, Mh, arms, legs = mats
    hand = apply(arms[0], FOXD["arm0"]["hand"])
    w = wrap_amt(t)
    kite_low = kite_p + np.array([0, -0.55, 0])                            # bridle point under the diamond
    if t >= SH["button_crane"][0] + GRAB and pip_beak is not None:          # Pip reels the loose string up off the grass
        pile = ground_spiral((TPOS[0], TPOS[1]), 0.95, 1.25, 1.2)           # the slack stays on the grass round his feet
        return pile + sag_line(pile[-1], pip_beak, 2.0, 30)[1:] + sag_line(pip_beak, kite_low, 0.15, 16)[1:]
    if st["hold"] and w < 0.05:
        return sag_line(hand, kite_low, 0.35 if t < T.GUST0 else 0.1, 30)
    if t < T.SPIN0:
        loosen = 0.06 * clampu(t, T.KNOT_POP, T.KNOT_POP + 0.2)
        cp = coil_points(R, w, loosen)
        start = hand if w < 0.25 else cp[0]
        tail_pts = sag_line(cp[-1], kite_low, 0.2 if t < T.GUST1 else 0.0, 30)
        return [start] + cp + tail_pts[1:]
    if w > 0.002:                                                          # unwinding: what comes off lies on the grass
        cp = coil_points(R, w, 0.06)
        pile = ground_spiral((st["x"], st["z"]), 0.95, 1.25, 1.2 * (1 - w))
        return cp + pile + sag_line(pile[-1], kite_low, 0.0, 20)[1:]
    pile = ground_spiral((st["x"], st["z"]), 0.95, 1.25, 1.2)
    return pile + sag_line(pile[-1], kite_low, 0.0, 20)[1:]

# ---------------- Pip ----------------
PIP_FOOT = 0.060
UP = np.array([0, PIP_FOOT, 0])
PAW_TOP = 0.072
HF_H = 0.42                                    # Pip's high-five hop height
def _paw_table():
    """local hand height for arm0 side angles (fwd 0.35), to solve the paw raise that meets Pip"""
    pv = np.array(FOXD["arm0"]["pivot"]); hd = np.array(FOXD["arm0"]["hand"]); out = []
    for sd in np.linspace(1.3, 1.9, 61):
        M = trans(*pv) @ rotz(sd) @ rotx(-0.35) @ trans(*(-pv)); out.append((sd, apply(M, hd)[1]))
    return np.array(out)
PAW_TAB = _paw_table()
def paw_side_for_rise(r):
    y = PAW_TAB[:, 1] - PAW_TAB[0, 1]
    i = np.argmax(y)
    return float(np.interp(r, y[:i + 1], PAW_TAB[:i + 1, 0]))
HF_RISE = 0.11                                 # the paw can rise this far before Pip would touch Tumble's head (solved)
def hf_curves(t):
    """Pip hops up and lands back on the paw just as it bumps up to meet him: contact at T.HIGH_FIVE"""
    a0 = T.HIGH_FIVE - 0.42; u = clampu(t, a0, a0 + 0.7)
    if not (0 < u < 1): return None
    r = HF_RISE * math.sin(math.pi * u) ** 2
    g = 0.34 * math.sin(math.pi * min(u / 0.6, 1.0))
    return g + r, r                                                         # (Pip height, paw rise) above the rest pose                              # paw sphere radius 0.1, minus a little so the feet rest on the clay
STUMP_PIP = np.array([STUMP[0] - 0.4, surf(*STUMP) + STUMP_TOP, STUMP[1] + 0.12]) + UP
KNOT_L = (-0.22, 0.7, COIL_RZ + 0.1)       # on the coil, low on his chest once he lies on his side (beak height)
def knot_ground(R):
    """Pip's spot in front of the knot, and the knot itself"""
    kc = apply(R, KNOT_L); f = apply(R, (KNOT_L[0], KNOT_L[1], KNOT_L[2] + 0.24))
    return np.array([f[0], surf(f[0], f[2]), f[2]]) + UP, kc
def pip_state(t, st, mats):
    """returns pos, yaw, flying, pitch, perch flag, extra dict"""
    R, Mh, arms, legs = mats
    n = T.shot_at(t)[1]
    def on_ground(x, z): return np.array([x, surf(x, z), z]) + UP
    yaw_to_tumble = math.atan2(st["x"] - STUMP_PIP[0], st["z"] - STUMP_PIP[2])
    if n == "hook_track":
        p = np.array([st["x"] - 0.6, 1.65 + 0.2 * math.sin(t * 5), st["z"] + 1.0])   # same depth as Tumble, beside him on screen
        return p, 1.3, True, 0.0, False, {}
    if n == "title_wide":
        a, b = SH[n]; u = clampu(t, a, a + 1.4)
        p0 = np.array([TPOS[0] - 0.6, 1.65, TPOS[1] + 1.0])
        if u < 1:
            p = lerp(p0, STUMP_PIP, ease(u)); p[1] += 1.5 * math.sin(math.pi * u)        # arcs high over Tumble's head
            return p, 1.0, True, 0.0, False, {}
        return STUMP_PIP, yaw_to_tumble - 0.5, False, 0.0, True, {}
    if n == "pip_ask":
        L = T.line("Setup A"); ex = {}
        p = STUMP_PIP.copy()
        for w in L["words"]:                                                # little hops on the stressed words
            d = t - w["t0"]
            if w["w"].lower().startswith(("help", "good", "things")) and 0 <= d < 0.3: p[1] += 0.12 * math.sin(math.pi * d / 0.3)
        if L["t0"] - 0.1 < t < L["t1"] + 0.4: ex["point"] = True             # wing up: "me! me!"
        return p, 0.1, False, 0.0, p[1] <= STUMP_PIP[1] + 1e-6, ex
    if n == "tumble_no":
        L = T.line("Setup B")
        sad = ease(clampu(t, L["t1"] - 0.3, L["t1"] + 0.5))
        return STUMP_PIP, yaw_to_tumble, False, 0.28 * sad, True, {"droop": sad}
    if n in ("gust", "topple"):
        g = gust_amt(t)
        return STUMP_PIP, yaw_to_tumble + 0.15 * g * math.sin(t * 15), False, -0.12 * g, True, {"cling": g}
    if n == "overhead_tangled":
        a, b = SH[n]
        dest, kc = knot_ground(R)
        u = clampu(t, a + 0.5, a + 1.8)
        if u < 1:
            p = lerp(STUMP_PIP, dest, ease(u)); p[1] += 1.2 * math.sin(math.pi * u)   # high enough to drop in clear of his arm (real "tangled" timing)
            return p, math.atan2(dest[0] - STUMP_PIP[0], dest[2] - STUMP_PIP[2]), u > 0, 0.0, False, {}
        kc = knot_ground(R)[1]
        return dest, math.atan2(kc[0] - dest[0], kc[2] - dest[2]), False, 0.0, False, {}
    if n == "peck":
        dest, c = knot_ground(R)
        pitch = 0.0
        for pt in T.PECKS:
            d = t - pt
            if -0.12 < d < 0.18: pitch = 0.65 * math.sin(math.pi * (d + 0.12) / 0.3)
        L = T.line("Twist"); hw = next((w for w in L["words"] if w["w"].lower().startswith("help")), None)
        ex = {"point": True} if hw and L["t0"] - 0.1 < t < hw["t1"] + 0.15 else {}     # wing up on "I can help!"
        return dest, math.atan2(c[0] - dest[0], c[2] - dest[2]), False, pitch, False, ex
    if n == "spin_out":
        a, b = SH[n]
        dest, _ = knot_ground(fox_mats(dict(tumble(SH["peck"][1] - 0.01)))[0])
        away = np.array([TPOS[0] + 1.3, 0, TPOS[1] + 0.6])                      # off to the front-right, clear of him and the stump
        u = clampu(t, a, a + 0.42)                                         # hops clear before Tumble starts to rise
        p = lerp(dest, on_ground(away[0], away[2]), ease(u)); p[1] += 1.0 * math.sin(math.pi * u)     # high arc, over him not across him
        ex = {}
        if t > T.SPIN1: ex["cheer"] = True
        return p, math.atan2(TPOS[0] - away[0], TPOS[1] - away[2]), u < 1 or t > T.SPIN1, 0.0, False, ex
    if n == "moral":
        a, b = SH[n]
        hand = apply(arms[0], FOXD["arm0"]["hand"])
        top = hand + np.array([0, PAW_TOP, 0]) + UP
        u = clampu(t, a, a + 0.6)
        if u < 1:
            start = on_ground(TPOS[0] + 1.3, TPOS[1] + 0.6)
            p = lerp(start, top, ease(u)); p[1] += 0.4 * math.sin(math.pi * u)
            return p, 0.35, True, 0.0, False, {}
        return top, 0.35, False, 0.0, True, {}
    if n == "chorus":
        a, b = SH[n]
        top = apply(arms[0], FOXD["arm0"]["hand"]) + np.array([0, PAW_TOP, 0]) + UP
        sway = math.sin(2 * math.pi * (t - a) / (2 * BEAT))
        hc = hf_curves(t)
        ex = {"sway": sway}
        if hc:                                                              # hops up; the rising paw meets his wing at the top
            top = top + np.array([0, hc[0] - hc[1], 0]); ex["highfive"] = True
            return top, 0.35, True, 0.0, False, ex
        return top, 0.35, False, 0.0, True, ex
    # button: Pip grabs the loose string end and flies the kite up
    a, b = SH["button_crane"]
    p0 = apply(fox_mats(tumble(a))[2][0], FOXD["arm0"]["hand"]) + np.array([0, PAW_TOP + 0.01, 0]) + UP
    g = GRAB_PT + UP + np.array([0.25, 0.03, 0.0])                           # just beside the string, next to the kite
    if t < a + GRAB:                                                        # round behind his head, then down to the string by the kite
        u = clampu(t, a, a + GRAB)
        w1 = np.array([p0[0] + 0.15, 3.0, TPOS[1] - 0.7])                     # up and back, beside his raised paw
        w2 = np.array([TPOS[0] - 1.0, 3.0, TPOS[1] - 0.7])                    # across, high behind his head
        legs_ = [(p0, w1), (w1, w2), (w2, g)]; k = min(int(u * 3), 2); v = ease(u * 3 - k)
        p = lerp(legs_[k][0], legs_[k][1], v)
        yaw = math.atan2(g[0] - p0[0], g[2] - p0[2]) if u < 0.85 else -math.pi / 2
        return p, yaw, u < 0.9, 0.35 * clampu(u, 0.85, 1.0), False, {"beak": u > 0.92}
    u = clampu(t, a + GRAB, b)                                              # then flies it up on the kite's side, away from Tumble
    p1 = np.array([TPOS[0] - 0.95, 2.45, TPOS[1] + 1.4])                      # below and in front of the kite, clear of its tail
    p = lerp(g, p1, ease(u)) + np.array([0, 0.06 * math.sin(t * 9), 0]) * u
    return p, lerp(-math.pi / 2, 0.0, ease(clampu(u, 0.0, 0.4))), True, 0.35 * (1 - clampu(u, 0.0, 0.2) / 0.2), False, {"beak": True}

# ---------------- camera (aspect-fitted) ----------------
def fit_cam(tgt, yaw_deg, pitch_deg, fit_w, fit_h, fov=38.0, lift=None):
    """eye on a sphere round tgt (yaw 0 = camera at +z looking towards -z); distance solved so the box fits"""
    a = W / H; th = math.tan(math.radians(fov) / 2)
    d = max(fit_h / th, fit_w / (th * a))
    yw, pt = math.radians(yaw_deg), math.radians(pitch_deg)
    dirv = np.array([math.sin(yw) * math.cos(pt), math.sin(pt), math.cos(yw) * math.cos(pt)])
    if lift is None: lift = 0.16 if not WIDE else 0.12                        # keep the caption band clear
    tgt = np.asarray(tgt, float) - np.array([0, 1.0, 0]) * lift * d * th
    eye = tgt + dirv * d
    eye[1] = max(eye[1], surf(eye[0], eye[2]) + 0.3)                       # never below the grass
    return eye, tgt, fov
def camera(t):
    i, name, u, lt = T.shot_at(t)
    st = tumble(t)
    tp = np.array([st["x"], 0.9, st["z"]])
    if name == "hook_track":                                                # low tracking beside him, kite rising behind
        e = ease(u)
        return fit_cam(tp + np.array([0.0, 0.55 + 0.6 * e, 0]), lerp(78, 40, e), lerp(-6, 4, e), lerp(1.6, 2.0, e), lerp(1.7, 2.2, e) if not WIDE else 1.6)
    if name == "title_wide":                                                # wide: meadow, stump, kite high
        e = ease(u)
        return fit_cam(np.array([2.0, 1.6 + 0.3 * e, -1.0]), -8, 12 - 2 * e, 3.4, 3.2 if not WIDE else 2.4, lift=0.05)
    if name == "pip_ask":                                                   # macro on Pip on the stump
        e = ease(u)
        return fit_cam(STUMP_PIP + np.array([0.12 if WIDE else 0.0, 0.25, 0]), lerp(28, 20, e) if not WIDE else lerp(16, 22, e), 6, 0.42, 0.55, fov=34)
    if name == "tumble_no":                                                 # over Pip's shoulder at Tumble
        e = ease(u)
        tgt = lerp(STUMP_PIP + np.array([0, 0.3, 0]), tp + np.array([0, 0.6, 0]), 0.78)
        return fit_cam(tgt, lerp(64, 58, e), 14, 0.95, 1.3, fov=36, lift=0.1 if not WIDE else 0.06)
    if name == "gust":                                                      # wide low angle, slow push-in
        e = ease(u)
        return fit_cam(np.array([TPOS[0], lerp(1.5, 1.25, e), TPOS[1]]), 4, lerp(16, 20, e), lerp(2.6, 2.0, e), lerp(2.6, 2.0, e))
    if name == "topple":                                                    # medium side
        return fit_cam(np.array([TPOS[0], 0.85, TPOS[1]]), 28, 6, 1.5, 1.35)
    if name == "overhead_tangled":                                          # top-down: wrapped like a parcel
        e = ease(u)
        bc = apply(fox_mats(st)[0], (0.0, 0.7, 0.25))
        return fit_cam(np.array([bc[0], 0.3, bc[2] - 0.2]), 0.01, 86, lerp(1.6, 1.4, e), lerp(1.8, 1.55, e), fov=45, lift=0.0)
    if name == "peck":                                                      # macro at the knot
        e = ease(u)
        R = fox_mats(st)[0]
        pg, kc = knot_ground(R)
        tgt = lerp(kc, pg, 0.5); tgt[1] = 0.4
        ax = math.degrees(math.atan2(kc[0] - pg[0], kc[2] - pg[2]))          # Pip-to-knot axis; film it side-on
        yaw = min((ax + 104, ax - 104), key=lambda y: -math.cos(math.radians(y)))   # three-quarter front of Pip, knot in profile
        return fit_cam(tgt, yaw + lerp(-6, 6, e), 8, 0.62, 0.62, fov=34, lift=0.12)
    if name == "spin_out":                                                  # wide: spins up like a top
        e = ease(clampu(t, SH[name][0], T.SPIN1))
        return fit_cam(np.array([lerp(TPOS[0] - 0.5, TPOS[0] + 0.35, e), 1.05, TPOS[1]]), -6, 6, lerp(2.4, 1.9, e), 1.7)
    if name == "moral":                                                     # slow push-in two-shot
        e = ease(u)
        return fit_cam(np.array([TPOS[0] + 0.35, lerp(1.35, 1.45, e), TPOS[1]]), lerp(12, 6, e), 5, lerp(1.25, 1.05, e), lerp(1.4, 1.1, e))
    if name == "chorus":                                                    # medium front, both in frame for the dance
        return fit_cam(np.array([TPOS[0] + 0.35, 1.2, TPOS[1]]), 6, 6, 1.3, 1.35)
    # button: crane up, keeping Tumble, Pip and the climbing kite all in frame
    e = ease(u)
    kp, _ = kite_state(t, st)
    cx = (st["x"] + kp[0]) / 2; cz = (st["z"] + kp[2]) / 2
    hw = max(1.7, abs(kp[0] - st["x"]) / 2 + 0.9)
    top = max(2.4, kp[1] + 0.7)
    return fit_cam(np.array([cx, top / 2, cz]), 4, lerp(4, 10, e), hw, top / 2 + 0.25, lift=0.0 if not WIDE else -0.08)

# ---------------- render ----------------
LDIR = np.array([-0.55, 0.85, 0.5]); LDIR /= np.linalg.norm(LDIR)
LVIEW = look_at(LDIR * 20 + np.array([0, 0, -1.0]), np.array([0, 0, -1.0]), (0, 1, 0))
LVP = ortho(-10, 10, -10, 10, 1, 45) @ LVIEW
shadow_tex = ctx.depth_texture((2048, 2048)); shadow_tex.compare_func = "<="
shadow_tex.repeat_x = shadow_tex.repeat_y = False
shadow_fbo = ctx.framebuffer(depth_attachment=shadow_tex)
SS = 2 if PREVIEW else 4
msaa_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4, samples=SS)],
                           depth_attachment=ctx.depth_renderbuffer((W, H), samples=SS))
res_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4)])

def blink(tsec, off=0.0, period=3.3):
    ph = (tsec + off) % period
    return 1.0 - 0.92 * math.exp(-((ph - 0.1) / 0.06) ** 2)
def eyes(draws, Mh, centers, er, bl, U):
    for c in centers:
        draws.append((EYE_W, Mh @ trans(*c) @ scale(er, er * bl, er * 0.7), U(mat=2, bump=0.0), False))
        if bl > 0.3:
            pc = np.array(c) + np.array([-np.sign(c[0]) * er * 0.08, -er * 0.05, er * 0.6])
            draws.append((EYE_P, Mh @ trans(*pc) @ scale(er * 0.58, er * 0.66 * bl, er * 0.45), U(mat=2, bump=0.0), False))
            hc = pc + np.array([er * 0.18, er * 0.28, er * 0.4])
            draws.append((EYE_W, Mh @ trans(*hc) @ scale(er * 0.16 * bl), U(mat=3, bump=0.0), False))
def seg_M(a, b, r):
    """stick mesh (capsule along +y, radius 0.05, length 1) stretched from a to b"""
    d = b - a; L = float(np.linalg.norm(d))
    if L < 1e-5: return None
    return trans(*a) @ align_up(d / L) @ scale(r / 0.05, L, r / 0.05)

def build_draws(t):
    U = lambda **k: k
    draws = []
    g = gust_amt(t)
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.8), False))
    draws.append((E2["appletree"], trans(APPLE_TREE[0], ground_h(*APPLE_TREE) - 0.05, APPLE_TREE[1]) @ rotz(0.03 * g * math.sin(t * 6)) @ scale(1.25), U(mat=0, bump=0.8, obj="tree"), True))
    for (x, z, s) in [(-7.5, -9.5, 1.6), (6.5, -9.0, 1.8), (-10.5, -13, 1.9), (10.0, -14, 2.0), (3.0, -15, 1.7), (-4.0, -16, 1.8), (8.5, -3.5, 1.5)]:
        draws.append((SC["tree"], trans(x, ground_h(x, z) - 0.05, z) @ roty(x) @ rotz(0.04 * g * math.sin(t * 5 + x)) @ scale(s), U(mat=0, bump=0.7), True))
    draws.append((SC["cottage"], trans(COTTAGE_FAR[0], ground_h(*COTTAGE_FAR) - 0.05, COTTAGE_FAR[1]) @ roty(-0.4), U(mat=0, bump=0.6), False))
    draws.append((E2["stump"], trans(STUMP[0], ground_h(*STUMP) - 0.02, STUMP[1]) @ roty(0.7), U(mat=0, bump=0.9, obj="stump"), True))
    for (x, z, s) in MUSH:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))
    for (x, y, z, sx, sy, sz, c) in [(-12, -1.5, -26, 10, 5.0, 4, (.62, .82, .66)), (11, -1.8, -28, 11, 6.0, 4, (.58, .78, .7)),
                                     (0, -2.8, -32, 15, 6.6, 5, (.66, .8, .78))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    for fi, (x, z, r, c, s) in enumerate(FLOWERS):
        wob = 0.06 * math.sin(t * 1.6 + fi) + 0.35 * g * math.sin(t * 9 + fi)
        draws.append((SC["flower"], trans(x, ground_h(x, z) - 0.01, z) @ roty(r) @ rotz(wob) @ scale(s), U(mat=0, bump=0.0, tint=c, tintMix=-1.0), False))
    for k, (x, y, z) in enumerate([(-5.0, 11.0, -18), (5.5, 13.5, -22), (-1.0, 15.5, -26)]):
        draws.append((SC["cloud"], trans(x + (0.08 + 0.6 * g) * t * (1 if k % 2 else -1), y + 0.15 * math.sin(t * 0.5 + k), z) @ scale(1.4), U(mat=0, bump=0.4), False))
    draws.append((SC["sun"], trans(5.5, 14.0, -24) @ rotz(t * 0.2) @ scale(1.3), U(mat=0, bump=0.4), False))
    if g > 0.01:                                                            # blowing leaves show the gust
        for k in range(16):
            ph = (t * 0.55 + k / 16.0) % 1.0
            x = TPOS[0] - 4.5 + 9.0 * ph; z = TPOS[1] - 1.5 - 2.4 * ((k * 0.37) % 1.0)          # a band behind him, clear of faces
            y = 0.25 + 1.0 * ((k * 0.61) % 1.0) + 0.15 * math.sin(t * 4 + k)
            draws.append((SC["leaf"], trans(x, y, z) @ rotz(t * 7 + k) @ rotx(t * 5 + k) @ scale(1.6 * g),
                          U(mat=0, bump=0.0, tint=(0.55, 0.8, 0.45) if k % 3 else (0.95, 0.75, 0.4), tintMix=1.0), False))
    # ---- Tumble ----
    st = tumble(t); mats = fox_mats(st); R, Mh, arms, legs = mats
    contacts = []
    u0 = U(mat=0, bump=1.0, seed=2.0, obj="fox")
    draws.append((FOXP["body"], R, u0, True))
    for li in range(2): draws.append((FOXP[f"leg{li}"], legs[li], u0, True))
    for ai in range(2): draws.append((FOXP[f"arm{ai}"], arms[ai], u0, True))
    draws.append((FOXP["head"], Mh, u0, True))
    tp = FOXD["tail"]["pivot"]
    draws.append((FOXP["tail"], R @ trans(*tp) @ roty(st["tail"] * 0.5) @ trans(*(-np.array(tp))), u0, True))
    dizzy = T.shot_at(t)[1] == "spin_out" and t > T.SPIN1 and t < T.SPIN1 + 0.9
    eyes(draws, Mh, FOXD["eyes"]["centers"], FOXD["eyes"]["r"], 0.35 if dizzy else blink(t), U)
    fi_ = min(int(t * FPS), len(MOUTH["tumble"]) - 1)
    mo = MOUTH["tumble"][fi_]
    if mo > 0.06:
        draws.append((PR["mouth"], Mh @ trans(*(np.array(FOXD["mouth"]["c"]) + np.array([0, -0.025, 0.035]))) @ scale(0.1, 0.035 + 0.05 * mo, 0.045), U(mat=2, bump=0.0), False))   # one mouth, covering the carved smile while singing
    if st["lie"] < 0.5: contacts.append((st["x"], st["z"], 0.75, max(0.0, 1 - st["y"] * 1.5)))
    else: contacts.append((st["x"] - 0.4, st["z"], 1.0, 1.0))
    # ---- Pip ----
    pp, pyaw, pfly, ppitch, pperch, pex = pip_state(t, st, mats)
    up = U(mat=0, bump=0.6, seed=7.0, obj="pip")
    sq = -0.12 * pex.get("cling", 0.0)
    Mp = trans(*pp) @ roty(pyaw) @ rotx(ppitch) @ scale(1.1 * (1 - sq * 0.5), 1.1 * (1 + sq), 1.1 * (1 - sq * 0.5))
    draws.append((PIPP["body"], Mp, dict(up, perch=pperch), True))
    if pfly and SH["button_crane"][0] <= t < SH["button_crane"][0] + 0.35: flap = -0.1 + 0.6 * clampu(t, SH["button_crane"][0], SH["button_crane"][0] + 0.35) * (0.5 + 0.5 * math.sin(t * 28))   # take-off flaps stay up, clear of his cheek
    elif pfly: flap = 0.9 * math.sin(t * 28)
    elif pex.get("droop"): flap = 0.04 - 0.25 * pex["droop"]
    elif pex.get("cheer"): flap = 1.1 + 0.5 * math.sin(t * 14)
    else: flap = 0.04 + 0.04 * math.sin(t * 3)
    for wi in range(2):
        pv = PIPD[f"wing{wi}"]["pivot"]; sgn = 1 if wi == 0 else -1
        fl = flap
        if wi == 0 and pex.get("point"): fl = 1.3 + 0.12 * math.sin(t * 10)
        if pex.get("link") and wi == 1: fl = 0.9 + 0.15 * pex.get("sway", 0.0)          # wing out to Tumble's paw
        if pex.get("highfive") and wi == 0: fl = -0.6                    # wing swings down onto the paw
        Mw = Mp @ trans(*pv) @ rotz(sgn * fl) @ trans(*(-np.array(pv)))
        draws.append((PIPP[f"wing{wi}"], Mw, up, True))
    eyes(draws, Mp, PIPD["eyes"]["centers"], PIPD["eyes"]["r"], blink(t, 1.3, 2.7), U)
    mp_ = MOUTH["pip"][min(int(t * FPS), len(MOUTH["pip"]) - 1)]
    if mp_ > 0.08 and not pex.get("beak"):
        draws.append((PR["mouth"], Mp @ trans(0, 0.295, 0.19) @ scale(0.028, 0.022 * mp_, 0.02), U(mat=0, bump=0.0), False))
    if not pfly: contacts.append((pp[0], pp[2], 0.2, 1.0))
    beak = apply(Mp, (0, 0.31, 0.27)) if pex.get("beak") else None
    d_hf = t - T.HIGH_FIVE
    if 0 <= d_hf < 0.4 and T.shot_at(t)[1] == "chorus":                     # star puff on the high-five
        hc = apply(arms[0], FOXD["arm0"]["hand"]) + np.array([0, 0.2, 0])
        for k in range(8):
            a_ = k * 2 * math.pi / 8
            q = hc + np.array([math.cos(a_), math.sin(a_), 0.3]) * (0.12 + 0.7 * d_hf)
            draws.append((PR["ball"], trans(*q) @ scale(0.05 * (1 - d_hf / 0.4)), U(mat=0, bump=0.0, tint=(1.0, 0.88, 0.35), tintMix=1.0), False))
    # ---- kite, string, knot ----
    kp, kR = kite_state(t, st)
    Mk = trans(*kp) @ kR @ scale(1.15)
    draws.append((PR["kite"], Mk, U(mat=0, bump=0.3, obj="kite"), True))
    tail_top = apply(Mk, (0, -0.63, 0))
    for k in range(5):                                                      # bow tail hanging under the kite
        s = (k + 1) / 5.0
        sway = 0.25 * math.sin(t * 3 + k * 0.8) * s
        on_ground = kp[1] < 0.5
        near = T.GUST0 - 0.2 < t < SH["topple"][0] + 0.5
        p = tail_top + (np.array([0.22 * s, 0.0, 0.55 * s]) if on_ground else (kR[:3, :3] @ np.array([sway, -0.42 * s * (1.4 if near else 3), 0.1 * s])))
        if on_ground: p[1] = surf(p[0], p[2]) + 0.04
        draws.append((PR["ball"], trans(*p) @ scale(0.06, 0.045, 0.06), U(mat=0, bump=0.0, tint=(1.0, 0.55, 0.65) if k % 2 else (1.0, 0.85, 0.35), tintMix=1.0), False))
    pts = string_path(t, st, mats, kp, beak)
    for a_, b_ in zip(pts[:-1], pts[1:]):
        M = seg_M(np.asarray(a_), np.asarray(b_), 0.02)
        if M is not None: draws.append((PR["stick"], M, U(mat=0, bump=0.0, tint=(0.98, 0.96, 0.9), tintMix=1.0), False))
    if wrap_amt(t) >= 0.999 and t < T.SHOTS[[n for a, b, n in T.SHOTS].index("spin_out")][0]:
        kc = apply(R, KNOT_L)
        pop = clampu(t, T.KNOT_POP, T.KNOT_POP + 0.12)
        if t < T.KNOT_POP + 0.25:
            jig = 0.0
            for pt in T.PECKS:
                d = t - pt
                if 0 <= d < 0.2: jig = 0.3 * math.sin(math.pi * d / 0.2)
            draws.append((PR["ball"], trans(*kc) @ scale(0.075 * (1 + jig + 0.8 * pop) * (1 - clampu(t, T.KNOT_POP + 0.12, T.KNOT_POP + 0.25))),
                          U(mat=0, bump=0.0, tint=(0.98, 0.96, 0.9), tintMix=1.0), False))
        if 0 <= t - T.KNOT_POP < 0.45:                                      # pop puff
            d = t - T.KNOT_POP
            for k in range(12):
                a_ = k * 2 * math.pi / 12
                p = kc + np.array([math.cos(a_), math.sin(a_), 0.5]) * (0.1 + 1.1 * d)
                draws.append((PR["ball"], trans(*p) @ scale(0.085 * (1 - d / 0.45)), U(mat=0, bump=0.0, tint=(1.0, 0.95, 0.7), tintMix=1.0), False))
    return draws, contacts

def draw_pass(draws, contacts, eye, tgt, fov, vp):
    x, y, w, h = vp
    VPm = perspective(fov, w / h, 0.12, 90.0) @ look_at(eye, tgt)
    ctx.viewport = vp
    ctx.disable(moderngl.DEPTH_TEST)
    skyprog["cTop"].value = SKY[0]; skyprog["cMid"].value = SKY[1]; skyprog["cHor"].value = SKY[2]
    sky_vao.render()
    ctx.enable(moderngl.DEPTH_TEST)
    shadow_tex.use(0); prog["shadowMap"].value = 0
    prog["VP"].value = gl(VPm); prog["LVP"].value = gl(LVP); prog["camPos"].value = tuple(eye)
    cvals = [tuple(c) for c in contacts] + [(0, 0, 1, 0)] * (8 - len(contacts))
    prog["contact"].value = cvals[:8]; prog["nContact"].value = len(contacts)
    prog["fade"].value = 1.0; prog["keyI"].value = 1.05
    for (mesh, M, u, cast) in draws:
        prog["M"].value = gl(M); prog["NM"].value = nmat(M)
        prog["mat"].value = u.get("mat", 0); prog["bump"].value = u.get("bump", 1.0)
        prog["tint"].value = tuple(u.get("tint", (1, 1, 1))); prog["tintMix"].value = u.get("tintMix", 0.0)
        prog["seed"].value = u.get("seed", 0.0)
        mesh.vao.render()

def render_frame(t):
    draws, contacts = build_draws(t)
    shadow_fbo.use(); shadow_fbo.clear(depth=1.0); ctx.viewport = (0, 0, 2048, 2048)
    sprog["LVP"].value = gl(LVP)
    ctx.disable(moderngl.CULL_FACE)
    for (mesh, M, u, cast) in draws:
        if cast: sprog["M"].value = gl(M); mesh.svao.render()
    msaa_fbo.use(); msaa_fbo.clear(0, 0, 0, 1, depth=1.0)
    eye, tgt, fov = camera(t)
    draw_pass(draws, contacts, eye, tgt, fov, (0, 0, W, H))
    ctx.viewport = (0, 0, W, H)
    ctx.copy_framebuffer(res_fbo, msaa_fbo)
    img = np.frombuffer(res_fbo.read(components=4), np.uint8).reshape(H, W, 4)[::-1].copy()
    img[..., 3] = 255
    return img

# ---------------- 2D overlay: captions, title, moral card ----------------
tf = skia.Typeface.MakeFromFile("assets/Fredoka.ttf")
def wght(v):
    try:
        arg = skia.FontArguments(); arg.setVariationDesignPosition(skia.FontArguments.VariationPosition(
            skia.FontArguments.VariationPosition.Coordinates([skia.FontArguments.VariationPosition.Coordinate(0x77676874, v)])))
        return tf.makeClone(arg)
    except Exception:
        return tf
TF6 = wght(620); TF7 = wght(700)
grain = np.random.default_rng(1).integers(0, 255, (H, W), dtype=np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
vig = (1 - 0.2 * np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.25, 0, 1)).astype(np.float32)
PLUMC = (74, 43, 69)
BIGC = (240, 90, 50); TINYC = (40, 150, 210); MORAL_BG = (255, 214, 80)
def word_style(w):
    k = re.sub(r"[^a-z]", "", w.lower())
    if k in ("big", "helpers"): return 1.35, BIGC
    if k in ("tiny", "small"): return 0.8, TINYC
    return 1.0, None
CAP_LINES = [L for L in T.LINES if L["section"] != "Sting"]            # the title card carries the sting
def current_line(t):
    for li, L in enumerate(CAP_LINES):
        ws = L["words"]
        start = ws[0]["t0"] - 0.12
        start = max(start, next((a for (a, b, n) in T.SHOTS if a <= ws[0]["t0"] < b), start))
        nxt = CAP_LINES[li + 1]["words"][0]["t0"] - 0.25 if li + 1 < len(CAP_LINES) else 1e9
        end = min(ws[-1]["t1"] + 0.55, nxt)
        sh_end = next((b for (a, b, n) in T.SHOTS if a <= ws[-1]["t1"] < b), end)
        end = min(end, sh_end)
        if start <= t < end: return L, start, end
    for s in T.SPOKEN:
        if s["t0"] - 0.05 <= t < s["t0"] + 1.1:
            return dict(section="spoken", words=[dict(w=x, t0=s["t0"], t1=s["t0"] + 0.8) for x in s["caption"].split()]), s["t0"] - 0.05, s["t0"] + 1.1
    return None, 0, 0

def outlined(cv, text, x, y, font, rgb, a, sw=16):
    st = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=sw * K, Color=skia.Color(*PLUMC, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
    fp = skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(255 * a)))
    cv.drawString(text, x, y, font, st); cv.drawString(text, x, y, font, fp)

def title_card(cv, t):
    a0, a1 = SH["title_wide"]
    if not (a0 <= t < a1): return
    a = clamp01((t - a0) / 0.35) * clamp01((a1 - t) / 0.35)
    f1 = skia.Font(TF7, 128 * K)
    y0 = (360 if not WIDE else 190) * K - 6 * K * math.sin(t * 3)
    x = (W - f1.measureText(T.TITLE)) / 2
    cols = [(255, 160, 100), (250, 190, 60), (110, 175, 235), (246, 120, 170), (160, 130, 230)]
    for k, ch in enumerate(T.TITLE):
        outlined(cv, ch, x, y0 + 6 * K * math.sin(t * 5 + k * 0.6), f1, cols[k % 5], a, 22); x += f1.measureText(ch)
    bf = skia.Font(TF7, 50 * K); bw = bf.measureText(T.SERIES_TAG)
    by = y0 + 30 * K
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - bw) / 2 - 30 * K, by, bw + 60 * K, 70 * K), 35 * K, 35 * K),
                 skia.Paint(AntiAlias=True, Color=skia.Color(*MORAL_BG, int(240 * a))))
    cv.drawString(T.SERIES_TAG, (W - bw) / 2, by + 52 * K, bf, skia.Paint(AntiAlias=True, Color=skia.Color(*PLUMC, int(255 * a))))
    sf = skia.Font(TF7, 92 * K)
    parts = [("Tiny ", skia.Font(TF7, 70 * K), TINYC), ("Pip, ", sf, (255, 255, 255)), ("BIG ", skia.Font(TF7, 120 * K), BIGC), ("Help!", sf, (255, 255, 255))]
    tw = sum(f.measureText(s) for s, f, c in parts); x = (W - tw) / 2
    for s, f, c in parts:
        outlined(cv, s, x, by + 200 * K, f, c, a, 16); x += f.measureText(s)

def overlay(img, t):
    surf_ = skia.Surface(img); cv = surf_.getCanvas()
    title_card(cv, t)
    L, start, end = current_line(t)
    if L:
        a = clamp01((t - start) / 0.15) * clamp01((end - t) / 0.15)
        moral = L["section"] == "Moral"
        base = (76 if moral else 72) * K
        maxw = (900 if not WIDE else 1400) * K
        items = []
        for w_ in L["words"]:
            sc_, col = word_style(w_["w"]); f = skia.Font(TF7, base * sc_)
            items.append((w_, f, f.measureText(w_["w"]), col))
        space = skia.Font(TF7, base).measureText(" ")
        rows, cur, wsum = [], [], 0
        for it in items:
            if cur and wsum + space + it[2] > maxw: rows.append(cur); cur, wsum = [], 0
            wsum += (space if cur else 0) + it[2]; cur.append(it)
        if cur: rows.append(cur)
        rh = 118 * K
        y = (1700 * K if not WIDE else H - 70 * K) - (rh / 2) * (len(rows) - 1) * (1 if not WIDE else 2)
        bw = max(sum(i[2] for i in r) + space * (len(r) - 1) for r in rows)
        bg = MORAL_BG if moral else (255, 250, 240)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - bw) / 2 - 40 * K, y - 98 * K, bw + 80 * K, rh * len(rows) + 30 * K), 50 * K, 50 * K),
                     skia.Paint(AntiAlias=True, Color=skia.Color(*bg, int((235 if moral else 210) * a))))
        if moral:                                                           # moral card label
            lf = skia.Font(TF7, 50 * K); lt = "The moral"; lw = lf.measureText(lt)
            cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - lw) / 2 - 28 * K, y - 172 * K, lw + 56 * K, 72 * K), 36 * K, 36 * K),
                         skia.Paint(AntiAlias=True, Color=skia.Color(*PLUMC, int(235 * a))))
            cv.drawString(lt, (W - lw) / 2, y - 119 * K, lf, skia.Paint(AntiAlias=True, Color=skia.Color(255, 250, 240, int(255 * a))))
        for row in rows:
            tw = sum(i[2] for i in row) + space * (len(row) - 1); x = (W - tw) / 2
            for (w_, f, wl, col) in row:
                on = w_["t0"] - 0.03 <= t < max(w_["t1"], w_["t0"] + 0.25)
                c = col or ((240, 110, 60) if on else PLUMC)
                if col and not on: c = tuple(int(v * 0.8) for v in col)
                p = skia.Paint(AntiAlias=True, Color=skia.Color(*c, int(255 * a)))
                ps = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.5 * K, Color=skia.Color(*c, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
                yb = y - (6 * K if on else 0)
                cv.drawString(w_["w"], x, yb, f, ps); cv.drawString(w_["w"], x, yb, f, p)
                x += wl + space
            y += rh
    out = img[..., :3].astype(np.float32) * vig[..., None]
    out += (grain[..., None].astype(np.float32) - 127) * (8 / 255.0)
    return np.clip(out, 0, 255).astype(np.uint8)

# ---------------- geometry QA ----------------
QA_EXPECTED_POPS = []
QA_MASKS = {}
def qa(fps=15, out="out/qa_report.json"):
    import qa_geom
    meshes = {}
    def walk(o):
        if isinstance(o, dict):
            if "v" in o and "f" in o and "name" in o: meshes[o["name"]] = o; return
            for v in o.values(): walk(v)
    walk(D)
    bank = qa_geom.Bank("out/sdf.pkl", meshes)
    issues = []; prev_exist, prev_on = set(), {}
    for fi in range(int(T.DURATION * fps)):
        t = fi / fps
        draws, _ = build_draws(t)
        items = [(u["obj"], m.name, M, u.get("perch", False)) for (m, M, u, c) in draws if u.get("obj") and m.name in bank.g]
        eye, tgt, fov = camera(t); VPm = perspective(fov, W / H, 0.2, 90.0) @ look_at(eye, tgt)
        exist, onscr = set(), {}
        for (m, M, u, c) in draws:
            if not (u.get("obj") and m.name in bank.g): continue
            o = u["obj"]; exist.add(o)
            cc, rr = bank.v[m.name + ":bs"]; p = VPm @ M @ np.r_[cc, 1]
            onscr[o] = onscr.get(o, False) or (p[3] > 0 and abs(p[0] / p[3]) < 0.95 and abs(p[1] / p[3]) < 0.95)
        if fi > 0:
            cut = any(abs(t - a) < 1.5 / fps for (a, b, n) in T.SHOTS)
            for o in (exist ^ prev_exist):
                seen = onscr.get(o, False) or prev_on.get(o, False)
                if seen and not cut:
                    issues.append(dict(t=round(t, 3), kind="pop_" + ("in" if o in exist else "out"), a=o, depth=0))
        prev_exist, prev_on = exist, onscr
        lying = tumble(t)["lie"] > 0.05
        for e in qa_geom.check_frame(t, items, bank, ground=ground_h, masks=QA_MASKS, ground_objs=("pip",) if lying else ("fox", "pip"), float_tol=0.02):
            issues.append(e)
    summ = qa_geom.summarize(issues, fps)
    json.dump(summ, open(out, "w"), indent=1, default=float)
    for s_ in summ: print(s_)
    print("issues:", len(summ))
    return summ

def sheets(step=0.5, per=12, cols=4, outdir="review"):
    """labelled contact sheets, one frame every `step` seconds, for the reviewer agent"""
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(outdir, exist_ok=True)
    ts = [round(k * step, 2) for k in range(int(T.DURATION / step) + 1)]
    tw = 270 if not WIDE else 400; th = int(tw * H / W)
    font = ImageFont.truetype("assets/Fredoka.ttf", 22)
    for si in range(0, len(ts), per):
        chunk = ts[si:si + per]; rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + 30)), (30, 30, 30))
        for k, s in enumerate(chunk):
            fr = overlay(render_frame(s), s)
            im = Image.fromarray(fr).resize((tw, th))
            x, y = (k % cols) * tw, (k // cols) * (th + 30)
            sheet.paste(im, (x, y + 30))
            ImageDraw.Draw(sheet).text((x + 8, y + 3), f"t={s:.1f}  {T.shot_at(s)[1]}", fill=(255, 255, 255), font=font)
        p = f"{outdir}/sheet_{T.ASPECT}_{si // per + 1:02d}.jpg"
        sheet.save(p, quality=88); print(p, flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "qa":
        qa(); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "sheet":
        sheets(); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "x":
        for s in sys.argv[2:]:
            t0 = time.time(); fr = overlay(render_frame(float(s)), float(s))
            skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/still_{T.ASPECT}_{float(s):05.2f}.png")
            print(s, round(time.time() - t0, 2), "s", flush=True)
        sys.exit()
    nfr = int(T.DURATION * FPS)
    have_audio = os.path.exists("out/audio.wav")
    if len(sys.argv) > 1 and sys.argv[1] == "seg":
        f0, f1, outp, audio = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], []
    else:
        outp = sys.argv[1] if len(sys.argv) > 1 else f"out/fable01_{T.ASPECT}.mp4"
        f0, f1 = 0, int(sys.argv[2]) if len(sys.argv) > 2 else nfr
        audio = ["-i", "out/audio.wav", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart"] if have_audio else ["-movflags", "+faststart"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + \
          (audio[:2] if have_audio and audio else []) + ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"] + \
          (audio[2:] if have_audio and audio else audio) + [outp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(f0, min(f1, nfr)):
        tsec = fi / FPS
        p.stdin.write(overlay(render_frame(tsec), tsec).tobytes())
        if fi % 90 == 0: print(f"frame {fi}/{min(f1, nfr)}  {time.time() - t0:.0f}s", flush=True)
    p.stdin.close(); p.wait()
    print(f"done: {min(f1, nfr) - f0} frames in {time.time() - t0:.0f}s -> {outp}", flush=True)
