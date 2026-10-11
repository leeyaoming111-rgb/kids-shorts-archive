"""My Turn, Your Turn! (Lulu & Bo at the Pond). Shot-based 3D claymation renderer.
python3 render.py [out.mp4]          -> full video with audio
python3 render.py x 3 10 20          -> stills out/still_XX.png
python3 render.py seg f0 f1 out.mp4  -> silent segment"""
from render_base import *

B = T.BEAT
tb = T.t
def win(t, a, b, fi=0.3, fo=0.3):
    return clamp01((t - a) / fi) * clamp01((b - t) / fo)

FROGP = {k: Mesh(p["mesh"]) for k, p in D["frog"]["parts"].items() if "mesh" in p}
FROGD = D["frog"]["parts"]
TURP = {k: Mesh(p["mesh"]) for k, p in D["turtle"]["parts"].items() if "mesh" in p}
TURD = D["turtle"]["parts"]
PR = {k: Mesh(m) for k, m in D["props"].items()}
SC = {k: Mesh(m) for k, m in D["scene"].items()}
EYE_W, EYE_P = Mesh(D["eye_w"]), Mesh(D["eye_p"])
MOUTH = json.load(open("out/mouth.json"))

def gh(x, z): return float(ground_h(x, z))

# ---------------- set dressing ----------------
PAD_L = (-1.6, -1.8, 1.2)          # big pad: Lulu's landing pad and the finale stage
PAD_B = (-0.3, -3.55, 0.8)         # Bo's landing pad
PAD_A = (-3.4, -2.3, 0.7)          # intro hop pads
PAD_A2 = (-2.35, -1.45, 0.62)
rng = np.random.default_rng(3)
PADS = [PAD_L, PAD_B, PAD_A, PAD_A2, (-3.6, -4.2, 0.75), (-1.8, -4.9, 0.6), (0.4, -4.6, 0.55), (-4.3, -3.2, 0.5), (1.0, -3.6, 0.5)]
PAD_ROT = [rng.uniform(0, 6.28) for _ in PADS]
LILIES = [(-3.75, -4.0), (-1.55, -4.75), (0.55, -4.45), (-4.2, -3.05), (-2.6, -2.2)]
CATTAILS = []
for k in range(26):
    a = rng.uniform(-math.pi, math.pi); q = rng.uniform(1.0, 1.12)
    x = -1.4 + 3.6 * math.sqrt(q) * math.cos(a); z = -3.4 + 2.6 * math.sqrt(q) * math.sin(a)
    if z > -1.6 and x > -0.6: continue
    if 0.0 < x < 3.6 and -3.2 < z < -0.4: continue
    if -2.6 < x < 1.0 and z > -2.6: continue
    CATTAILS.append((x, z, rng.uniform(0, 6.28), rng.uniform(0.8, 1.25)))
BUSHES = [(-5.0, -1.0, 1.2), (5.0, -2.6, 1.4), (-6.2, -5.5, 1.5), (4.3, 0.6, 0.9), (-3.8, 1.2, 1.0), (6.5, -6.5, 1.6)]
TREES = [(-7.0, -8.0, 1.6), (6.5, -9.0, 1.8), (-10, -12, 1.9), (9.5, -13, 2.0), (2.5, -14.5, 1.7), (-3.5, -15, 1.8), (-0.5, -11, 1.5)]
FLOWERS = [(rng.uniform(-6, 6), rng.uniform(-1.0, 3.0)) for _ in range(30)]
FLOWERS = [(x, z) for x, z in FLOWERS if ((x + 1.4) / 3.6) ** 2 + ((z + 3.4) / 2.6) ** 2 > 1.3]
FLC = [(1.0, .75, .85), (1.0, .95, .7), (.85, .78, 1.0), (1.0, 1.0, 1.0)]

# ---------------- character tracks ----------------
L_TOP = np.array([1.3, ROCK_TOP, -1.85])
B_TOP = np.array([2.7, ROCK_TOP, -1.85])
R0 = RIDE[0]
LULU_BUMP_LAND = np.array([0.55, gh(0.55, -0.45), -0.45])
BO_BUMP_LAND = np.array([3.45, gh(3.45, -0.35), -0.35])
LULU_BANK = np.array([1.3, gh(1.3, -0.35), -0.35])
BO_BANK = np.array([2.35, gh(2.35, -0.4), -0.4])
BO_OTS = np.array([0.15, gh(0.15, -0.35), -0.35])
def P3(x, z, y=None): return np.array([x, gh(x, z) if y is None else y, z])
PAD_Y = 0.045

def hop_arc(p0, p1, u, h):
    u = clamp01(u); p = lerp(p0, p1, u); p[1] += h * 4 * u * (1 - u); return p
def yaw_to(d): return math.atan2(d[0], d[2])

def slide_state(t, key):
    """position, tangent, phase ('pre','slide','under','up','pad') for a slide event"""
    a, b = T.SLIDES[key]; ta, tb_ = tb(a), tb(b)
    if t < ta: return None
    if t < tb_:
        u = (t - ta) / (tb_ - ta); s = u ** 1.7
        p, d = ride(s); return dict(ph="slide", p=p, d=d, u=u)
    p, d = ride(1.0)
    dt = t - tb_
    if dt < 0.28:
        q = p + d * (1.2 * dt) ; q = q.copy(); q[1] = p[1] - 2.6 * dt ** 0.9
        return dict(ph="dive", p=q, d=d, u=dt / 0.28)
    return dict(ph="under", p=p, d=d, u=dt)
def entry_point(key):
    p, d = ride(1.0); e = p + d * 0.34; return np.array([e[0], 0.0, e[2]])

POP_DELAY = 0.95       # seconds under water before popping up
def pop_up(t, key, pad, offs=(0, 0)):
    """None if not yet; else (pos, u) emerging from the water beside the pad and hopping on"""
    t0 = tb(T.SLIDES[key][1]) + POP_DELAY
    if t < t0: return None
    u = (t - t0) / 0.55
    e = entry_point(key); target = np.array([pad[0] + offs[0], PAD_Y, pad[1] + offs[1]])
    start = lerp(e, target, 0.35); start[1] = -0.5
    if u < 1:
        p = lerp(start, target, ease(u)); p[1] = -0.5 + (PAD_Y + 0.5) * math.sin(math.pi / 2 * min(1, u * 1.15)) + 0.35 * math.sin(math.pi * u)
        return p, u
    return target, 1.0

def frog_state(t):
    beat = t / B
    st = dict(p=np.array([PAD_A[0], PAD_Y, PAD_A[1]]), yaw=0.4, pitch=0.0, roll=0.0, sq=0.012 * math.sin(t * 3.3), legs=0.0,
              arms=[[0.15, 0.0], [0.15, 0.0]], vis=True, dizzy=0.0, ride=False)
    wps = [np.array([PAD_A[0], PAD_Y, PAD_A[1]]), np.array([PAD_A2[0], PAD_Y, PAD_A2[1]]), P3(-0.95, -0.4), P3(-0.2, -0.3), P3(0.45, -0.3),
           P3(1.0, -0.3), P3(0.85, -0.75)]
    hops = T.HOPS_INTRO
    cur = wps[0]
    for i, h0 in enumerate(hops):
        if t >= h0:
            u = (t - h0) / 0.55
            if u < 1:
                st["p"] = hop_arc(wps[i], wps[i + 1], ease(u * 0.9 + 0.05), 0.55); st["yaw"] = yaw_to(wps[i + 1] - wps[i])
                st["legs"] = math.sin(math.pi * u); st["sq"] += 0.1 * math.sin(math.pi * u); st["pitch"] = -0.25 * math.sin(math.pi * u)
                cur = None; break
            cur = wps[i + 1]; st["yaw"] = yaw_to(wps[i + 1] - wps[i]) * 0.5
    if cur is not None: st["p"] = cur.copy()
    if t >= hops[-1] + 0.55:
        st["yaw"] = 0.8 if t < tb(19) else st["yaw"]
    # hop up onto the rock top
    h_up = tb(18.95)
    if t >= h_up:
        u = (t - h_up) / 0.6
        st["p"] = hop_arc(wps[-1], L_TOP, ease(u), 1.0) if u < 1 else L_TOP.copy()
        st["yaw"] = yaw_to(L_TOP - wps[-1]) if u < 1 else math.pi / 2
        if u < 1: st["legs"] = math.sin(math.pi * u)
        if 0 <= u - 1 < 0.6: st["sq"] -= 0.12 * math.exp(-(u - 1) * 6) * math.cos((u - 1) * 12)
    # push toward Bo, bump, tumble back onto the moss
    if t >= tb(23.6):
        u = (t - tb(23.6)) / (tb(T.BUMP) - tb(23.6))
        if u < 1:
            st["p"] = lerp(L_TOP, L_TOP + np.array([0.12, 0, 0]), ease(u)); st["yaw"] = math.pi / 2; st["arms"] = [[1.2, 0.8], [1.2, 0.8]]
        else:
            v = (t - tb(T.BUMP)) / 0.65
            if v < 1:
                st["p"] = hop_arc(L_TOP + np.array([0.12, 0, 0]), LULU_BUMP_LAND, v, 0.5); st["yaw"] = math.pi / 2
                st["pitch"] = 1.8 * v; st["arms"] = [[1.6, 0.0], [1.6, 0.0]]; st["legs"] = 0.6
            else:
                w = t - tb(T.BUMP) - 0.65
                st["p"] = LULU_BUMP_LAND.copy(); st["yaw"] = 0.35
                st["sq"] -= 0.15 * math.exp(-w * 5) * math.cos(w * 12)
                st["dizzy"] = win(t, tb(T.BUMP) + 0.65, tb(29.6), 0.2, 0.4)
                st["roll"] = 0.08 * math.sin(w * 4) * st["dizzy"]
    # walk to the two-shot mark; Bo's idea; leap up
    if t >= tb(29.6):
        u = (t - tb(29.6)) / (tb(30.6) - tb(29.6))
        if u < 1:
            st["p"] = hop_arc(LULU_BUMP_LAND, LULU_BANK, ease(u), 0.25); st["yaw"] = yaw_to(LULU_BANK - LULU_BUMP_LAND); st["legs"] = math.sin(math.pi * u)
        else:
            st["p"] = LULU_BANK.copy(); st["yaw"] = 0.55; st["pitch"] = 0.0; st["roll"] = 0.0
            if tb(33.9) <= t < tb(34.4):
                st["sq"] += 0.06 * math.sin((t - tb(33.9)) * 18); st["arms"] = [[2.2, 0.3], [0.3, 0.0]]
    a, b = T.LULU_LEAP
    if t >= tb(a):
        u = (t - tb(a)) / (tb(b) - tb(a))
        if u < 1:
            st["p"] = hop_arc(LULU_BANK, L_TOP, ease(u), 1.3); st["yaw"] = yaw_to(L_TOP - LULU_BANK); st["legs"] = math.sin(math.pi * u)
        else:
            st["p"] = L_TOP.copy(); st["yaw"] = -math.pi / 2 - 0.5
    # turn 1: scoot to the slide, slide, splash, pop onto the big pad
    if t >= tb(35.8):
        u = (t - tb(35.8)) / (tb(T.SLIDES["lulu1"][0]) - tb(35.8))
        st["p"] = lerp(L_TOP, R0, ease(u)); st["yaw"] = -math.pi / 2 - 0.45
        if u >= 1: st["p"] = R0.copy()
    lulu_pad_off = (0.0, 0.0)
    for key, off, until in (("lulu1", (0.0, 0.05), tb(48)), ("lulu2", (-0.35, 0.05), 99)):
        s = slide_state(t, key)
        if s is None or t >= until: continue
        if s["ph"] in ("slide", "dive"):
            st["p"] = s["p"]; st["yaw"] = yaw_to(s["d"]); st["pitch"] = -math.asin(max(-1, min(1, s["d"][1]))) * 0.8
            st["arms"] = [[2.6, 0.2], [2.6, 0.2]]; st["legs"] = 0.0; st["ride"] = True
        else:
            pu = pop_up(t, key, PAD_L, off)
            if pu is None: st["vis"] = False
            else:
                st["p"], uu = pu; st["yaw"] = 0.3; st["pitch"] = 0.0
                st["legs"] = math.sin(math.pi * min(uu, 1)) if uu < 1 else 0.0
                if uu >= 1:
                    w = t - (tb(T.SLIDES[key][1]) + POP_DELAY + 0.55)
                    st["sq"] -= 0.12 * math.exp(-w * 5) * math.cos(w * 12)
    # Bo's first turn: Lulu claps on her pad
    if tb(42) <= t < tb(48):
        ph = (t - tb(42)) * 2 * math.pi / B
        st["arms"] = [[0.9 + 0.25 * math.sin(ph), 1.1], [0.9 + 0.25 * math.sin(ph), 1.1]]; st["yaw"] = 0.7
    # question 1: Lulu waits on top with the star, waves; then turn 2
    if tb(48) <= t < tb(54.2):
        st["p"] = R0 + np.array([0.3, -0.03, 0.05]); st["yaw"] = 0.25; st["pitch"] = 0.0; st["vis"] = True; st["ride"] = False
        ph = (t - tb(48)) * 2 * math.pi * 1.2
        st["arms"] = [[2.3 + 0.35 * math.sin(ph), 0.2], [0.3, 0.0]]
        if t >= tb(53.6): st["yaw"] = lerp(0.25, -math.pi / 2 - 0.45, ease((t - tb(53.6)) / 0.35)); st["arms"] = [[1.5, 0.3], [1.5, 0.3]]
    # question 2 onward: Lulu on the big pad cheering for Bo
    if tb(57) <= t < tb(66):
        st["p"] = np.array([PAD_L[0] - 0.35, PAD_Y, PAD_L[1] + 0.05]); st["vis"] = True; st["ride"] = False
        st["yaw"] = 1.0; st["pitch"] = 0.0
        ph = (t - tb(57)) * 2 * math.pi / (2 * B)
        st["arms"] = [[1.0 + 0.3 * math.sin(ph), 0.7], [1.0 + 0.3 * math.sin(ph + 1), 0.7]]
        if t >= tb(64): st["arms"] = [[2.5, 0.2], [2.5, 0.2]]
    if t >= tb(66):
        st["p"] = np.array([PAD_L[0] - 0.38, PAD_Y, PAD_L[1] + 0.05]); st["vis"] = True; st["ride"] = False
        st["yaw"] = 0.2; st["pitch"] = 0.0
        bb = t / B
        st["roll"] = 0.1 * math.sin(math.pi * bb / 2); st["sq"] += 0.04 * abs(math.sin(math.pi * bb))
        st["arms"] = [[0.6 + 0.3 * math.sin(math.pi * bb), 0.4], [0.6 + 0.3 * math.cos(math.pi * bb), 0.4]]
        if tb(69) <= t < tb(70.5): st["arms"][0] = [2.6, -0.3]        # high five
        if t >= tb(72):
            ph = (t - tb(72)) * 2 * math.pi * 1.3
            st["arms"][0] = [2.3 + 0.35 * math.sin(ph), 0.2]
    st["p"] = np.asarray(st["p"], float)
    return st

def turtle_state(t):
    st = dict(p=P3(5.6, -0.4), yaw=-math.pi / 2, pitch=0.0, roll=0.0, sq=0.0, walk=0.0, head=[0.0, 0.0], vis=True, flip=0.0, ride=False, dizzy=0.0, tuck=0.0)
    def walk_seg(a, b, p0, p1):
        u = (t - a) / (b - a)
        if 0 <= u < 1:
            st["p"] = lerp(p0, p1, u); st["yaw"] = yaw_to(p1 - p0); st["walk"] = (t - a) * 7.0
            return True
        return False
    BO_IN = P3(3.25, -0.45); BO_STEP0 = P3(3.85, -0.95)
    S1 = np.array([STEPS[0][0], STEPS[0][1] + 0.07, STEPS[0][2]]); S2 = np.array([STEPS[1][0], STEPS[1][1] + 0.07, STEPS[1][2]])
    if t < 4.6: walk_seg(0.0, 4.6, P3(5.6, -0.4), BO_IN)
    elif t < tb(15): st["p"] = BO_IN; st["yaw"] = -0.4
    elif t < tb(18.5): walk_seg(tb(15), tb(18.5), BO_IN, BO_STEP0)
    else: st["p"] = BO_STEP0; st["yaw"] = -math.pi * 0.85
    # climb the steps
    for (a, b, p0, p1) in ((18.6, 19.4, BO_STEP0, S1), (19.6, 20.4, S1, S2), (20.6, 21.5, S2, B_TOP)):
        if t >= tb(a):
            u = (t - tb(a)) / (tb(b) - tb(a))
            if u < 1:
                st["p"] = hop_arc(p0, p1, ease(u), 0.2); st["yaw"] = yaw_to(p1 - p0); st["walk"] = t * 7; st["pitch"] = -0.35 * math.sin(math.pi * u)
            else:
                st["p"] = p1.copy(); st["yaw"] = yaw_to(p1 - p0) if p1 is not B_TOP else -math.pi / 2
    if t >= tb(21.5): st["yaw"] = lerp(yaw_to(B_TOP - S2), 0.15, ease((t - tb(21.5)) / 0.3))
    if t >= tb(23.2): st["yaw"] = lerp(0.15, -math.pi / 2, ease((t - tb(23.2)) / 0.3))
    if t >= tb(23.6):
        u = (t - tb(23.6)) / (tb(T.BUMP) - tb(23.6))
        if u < 1:
            st["p"] = lerp(B_TOP, B_TOP - np.array([0.12, 0, 0]), ease(u)); st["walk"] = t * 10
        else:
            v = (t - tb(T.BUMP)) / 0.7
            if v < 1:
                st["p"] = hop_arc(B_TOP - np.array([0.12, 0, 0]), BO_BUMP_LAND, v, 0.45); st["flip"] = v
            else:
                w = t - tb(T.BUMP) - 0.7
                st["p"] = BO_BUMP_LAND.copy(); st["yaw"] = -math.pi / 2 - 0.4
                f_back = tb(28.0)
                st["flip"] = 1.0 if t < f_back else 1.0 - ease((t - f_back) / 0.5)
                st["roll"] = 0.25 * math.sin(w * 5) * (1 if t < f_back else 0)
                st["dizzy"] = win(t, tb(T.BUMP) + 0.7, tb(29.6), 0.2, 0.4)
    if t >= tb(29.4):
        if not walk_seg(tb(29.4), tb(30.6), BO_BUMP_LAND, BO_BANK) and t >= tb(30.6):
            st["p"] = BO_BANK.copy(); st["yaw"] = -0.6
            st["head"] = [0.15 * math.sin(t * 2.0), -0.15]
            if tb(31.0) <= t < tb(33.0): st["head"] = [0.25 * math.sin((t - tb(31)) * 6) * 0.5, 0.2]
            if t >= tb(34.3): st["head"] = [0.0, -0.45 * ease((t - tb(34.3)) / 0.4)]
            st["flip"] = 0.0; st["roll"] = 0.0
    # climb for turn 1
    if t >= tb(36):
        S0b = BO_STEP0
        segs = [(36.0, 37.6, BO_BANK, S0b), (37.6, 38.5, S0b, S1), (38.6, 39.5, S1, S2), (39.6, 40.8, S2, B_TOP), (41.4, 42.6, B_TOP, R0)]
        for (a, b, p0, p1) in segs:
            if t >= tb(a):
                u = (t - tb(a)) / (tb(b) - tb(a))
                if u < 1:
                    st["p"] = hop_arc(p0, p1, ease(u), 0.2 if a > 37 else 0.0); st["yaw"] = yaw_to(p1 - p0); st["walk"] = t * 7; st["head"] = [0, 0]
                else:
                    st["p"] = p1.copy(); st["yaw"] = yaw_to(p1 - p0)
        if tb(40.8) <= t < tb(41.4): st["yaw"] = lerp(-math.pi / 2, 0.2, ease((t - tb(40.8)) / 0.3)); st["head"] = [0, -0.2]
    for key, pad, off, until in (("bo1", PAD_B, (0, 0), tb(48)), ("bo2", PAD_L, (0.42, 0.0), 99)):
        s = slide_state(t, key)
        if s is None or t >= until: continue
        if s["ph"] in ("slide", "dive"):
            st["p"] = s["p"] + np.array([0, 0.03, 0]); st["yaw"] = yaw_to(s["d"]); st["pitch"] = -math.asin(max(-1, min(1, s["d"][1]))) * 0.9
            st["tuck"] = 0.0; st["head"] = [0.0, -0.25]; st["ride"] = True; st["walk"] = 0.0
        else:
            pu = pop_up(t, key, pad, off)
            if pu is None: st["vis"] = False
            else:
                st["p"], uu = pu; st["yaw"] = -0.4; st["pitch"] = 0.0; st["vis"] = True; st["ride"] = False
    if tb(46.5) <= t < tb(48): st["head"] = [0.3 * math.sin(t * 5), -0.1]
    # question 1: Bo on the bank watching Lulu (over-the-shoulder)
    if tb(48) <= t < tb(57):
        st["p"] = BO_OTS.copy(); st["yaw"] = yaw_to(R0 - BO_OTS) - 0.1; st["pitch"] = 0.0; st["vis"] = True; st["ride"] = False
        st["head"] = [0.1 * math.sin(t * 1.5), -0.4]
        if tb(55) <= t: st["head"] = [0.25 * math.sin(t * 6), -0.2]
    # question 2: Bo on top with the star; turn 2
    if tb(57) <= t < tb(T.SLIDES["bo2"][0]):
        st["p"] = R0 + np.array([0.15, 0.0, 0.08]); st["yaw"] = 0.35; st["pitch"] = 0.0; st["vis"] = True; st["ride"] = False
        st["head"] = [0.15 * math.sin(t * 2.2), 0.05]
        if t >= tb(62.8): st["yaw"] = lerp(0.35, -math.pi / 2 - 0.45, ease((t - tb(62.8)) / 0.5)); st["p"] = lerp(st["p"], R0, ease((t - tb(62.8)) / 0.5))
    if t >= tb(66):
        st["p"] = np.array([PAD_L[0] + 0.42, PAD_Y, PAD_L[1] + 0.0]); st["yaw"] = -0.25; st["vis"] = True; st["ride"] = False; st["pitch"] = 0.0
        bb = t / B
        st["head"] = [0.15 * math.sin(math.pi * bb / 2), -0.1]; st["roll"] = 0.06 * math.sin(math.pi * bb / 2 + 1)
        st["walk"] = 0.0
    st["p"] = np.asarray(st["p"], float)
    return st

def frog_mats(st):
    p = st["p"]; sq = st["sq"]
    R = trans(*p) @ roty(st["yaw"]) @ rotx(st["pitch"]) @ rotz(st["roll"]) @ scale(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5)
    legs = []
    for li in range(2):
        pv = FROGD[f"leg{li}"]["pivot"]
        legs.append(R @ trans(*pv) @ rotx(1.15 * st["legs"]) @ trans(*(-np.array(pv))))
    arms = []
    for ai in range(2):
        pv = FROGD[f"arm{ai}"]["pivot"]; sgn = 1 if ai == 0 else -1
        side, fwd = st["arms"][ai]
        arms.append(R @ trans(*pv) @ rotz(sgn * side) @ rotx(-fwd) @ trans(*(-np.array(pv))))
    return R, legs, arms

def turtle_mats(st):
    p = st["p"]
    f = st["flip"]; lift = 0.6 * math.sin(math.pi * f) if 0 < f < 1 else 0.0
    R = trans(*p) @ roty(st["yaw"]) @ rotx(st["pitch"])
    if f > 0: R = R @ trans(0, 0.42 + lift, 0) @ rotz(math.pi * f + st["roll"]) @ trans(0, -0.42, 0)
    else: R = R @ rotz(st["roll"])
    hp = TURD["head"]["pivot"]
    Mh = R @ trans(*hp) @ roty(st["head"][0]) @ rotx(st["head"][1]) @ trans(*(-np.array(hp)))
    legs = []
    for li in range(4):
        pv = TURD[f"leg{li}"]["pivot"]; ph = st["walk"] + (0 if li in (0, 3) else math.pi)
        legs.append(R @ trans(*pv) @ rotx(0.45 * math.sin(ph) if st["walk"] else 0.0) @ trans(*(-np.array(pv))))
    return R, Mh, legs

# ---------------- turn star ----------------
STAR_PLAN = [(tb(31.3), "mid"), (tb(34.1), "lulu"), (tb(41.6), "bo"), (tb(47.2), "none"), (tb(48.0), "lulu"), (tb(56.8), "none"),
             (tb(57.0), "bo"), (tb(66.0), "none")]
def star_anchor(name, t, fr, tu):
    if name == "lulu":
        if not fr["vis"]: return None
        return fr["p"] + np.array([0, 1.75, 0])
    if name == "bo":
        if not tu["vis"]: return None
        return tu["p"] + np.array([0, 1.45, 0])
    if name == "mid":
        return (LULU_BANK + BO_BANK) / 2 + np.array([0, 1.9, 0])
    return None
def star_pos(t, fr, tu):
    cur = -1
    for i, (a, n) in enumerate(STAR_PLAN):
        if t >= a: cur = i
    if cur < 0: return None, 0
    a, n = STAR_PLAN[cur]
    p1 = star_anchor(n, t, fr, tu)
    if n == "none": return None, 0
    if p1 is None: return None, 0
    u = (t - a) / 0.6
    if u < 1 and cur > 0:
        p0 = star_anchor(STAR_PLAN[cur - 1][1], t, fr, tu)
        if p0 is not None:
            e = ease(u); p = lerp(p0, p1, e); p[1] += 0.5 * math.sin(math.pi * e); return p, 1.0
        return p1, ease(u)
    if u < 1: return p1, ease(u)
    return p1, 1.0

# ---------------- camera ----------------
def smooth_follow(fn, t, lag=0.25):
    acc = np.zeros(3); wsum = 0.0
    for k in range(6):
        w = math.exp(-k / 2.0); acc += w * fn(max(0.0, t - lag * k / 5)); wsum += w
    return acc / wsum

def camera(t):
    i, name, u, lt = T.shot_at(t)
    up = (0, 1, 0); fov = 40.0
    if name == "crane_down":
        e = ease(lt / 4.4)
        eye = lerp((-0.6, 11.0, 6.5), (1.0, 2.6, 9.0), e); tgt = lerp((-0.9, 0.0, -2.6), (0.9, 0.7, -1.4), e); fov = 44
    elif name == "track_side":
        fx = smooth_follow(lambda s: frog_state(s)["p"], t)
        eye = np.array([fx[0] + 0.3, 1.25, fx[2] + 5.6]); tgt = np.array([fx[0] + 0.25, 0.85, fx[2]]); fov = 40
    elif name == "low_water":
        e = ease(u)
        eye = lerp((-1.0, 0.3, 4.3), (-0.6, 0.28, 4.0), e); tgt = lerp((1.9, 1.15, -1.7), (2.1, 1.25, -1.7), e); fov = 46
    elif name == "cu_lulu":
        fx = smooth_follow(lambda s: frog_state(s)["p"], t, 0.3)
        eye = fx + np.array([1.7, 1.0, 2.5]); tgt = fx + np.array([0.0, 0.75, 0.0]); fov = 38
    elif name == "cu_bo":
        eye = B_TOP + np.array([0.35, 0.85, 2.6]); tgt = B_TOP + np.array([0.0, 0.5, 0.5]); fov = 38
    elif name == "wide_bump":
        eye = lerp((2.1, 2.3, 7.6), (2.1, 2.0, 7.1), ease(u)); tgt = np.array([2.1, 1.0, -1.3]); fov = 52
    elif name == "two_shot":
        e = ease(u)
        eye = lerp((1.8, 1.1, 5.0), (1.8, 1.1, 4.1), e); tgt = lerp((1.8, 0.8, -0.4), (1.8, 0.9, -0.6), e); fov = 44
    elif name == "track_slide":
        def pf(s):
            fr = frog_state(s); return fr["p"] if fr["vis"] else entry_point("lulu1")
        fx = smooth_follow(pf, t, 0.35)
        fx = np.array([max(fx[0], -1.6), max(fx[1], 0.0), fx[2]])
        eye = fx + np.array([0.3, 0.65, 5.2]); tgt = fx + np.array([-0.25, 0.4, 0.0]); fov = 46
    elif name == "overhead":
        eye = np.array([-0.35, 7.6, -1.5]); tgt = np.array([-0.4, 0.0, -2.45]); up = (0, 0, -1); fov = 50
        eye = lerp(eye, eye + np.array([0, -0.6, 0]), ease(u))
    elif name == "ots_bo":
        e = ease(u)
        eye = BO_OTS + np.array([-0.45, 1.0, 2.7]); tgt = lerp(R0 + np.array([0.2, 0.75, 0]), R0 + np.array([0.25, 0.65, 0]), e); fov = 44
    elif name == "ride_along":
        def pf(s):
            ss = slide_state(s, "lulu2")
            if ss is None: return ride(0.0)[0]
            return ss["p"] if ss["ph"] != "under" else ride(1.0)[0]
        p = smooth_follow(pf, t, 0.15)
        s_now = slide_state(t, "lulu2")
        if s_now is not None and s_now["ph"] == "slide":
            d = ride(min(1.0, s_now["u"] ** 1.7 + 0.03))[1]
        else:
            d = ride(1.0)[1]
        dh = np.array([d[0], 0, d[2]]); dh /= np.linalg.norm(dh)
        eye = p - dh * 2.8 + np.array([0.0, 2.9, 0.0]); tgt = p + dh * 3.0 + np.array([0, -0.7, 0]); fov = 54
        if s_now is None:
            eye = R0 - dh * 2.8 + np.array([0, 2.9, 0]); tgt = R0 + dh * 3.0 + np.array([0, -0.7, 0])
    elif name == "low_up_slide":
        p3, d3 = ride(1.0)
        e = ease(u)
        eye = p3 + np.array([d3[0], 0, d3[2]]) / np.linalg.norm([d3[0], d3[2]]) * 2.6 + np.array([0.2, 0.18, 0.4])
        eye[1] = 0.32
        tgt = lerp(R0 + np.array([0, 0.75, 0]), R0 + np.array([0.0, 0.6, 0]), e); fov = 46
    elif name == "pad_push":
        e = ease(u)
        eye = lerp((-1.55, 1.05, 2.4), (-1.55, 0.9, 1.25), e); tgt = np.array([-1.55, 0.6, -1.8]); fov = 42
    else:  # crane_up
        e = ease(lt / 4.0)
        eye = lerp((-1.55, 0.9, 1.25), (-0.6, 5.0, 6.8), e); tgt = lerp((-1.55, 0.6, -1.8), (-0.6, 0.6, -2.4), e); fov = lerp(42, 46, e)
    return np.asarray(eye, float), np.asarray(tgt, float), float(fov), up

# ---------------- light ----------------
LDIR = np.array([-0.62, 0.48, 0.62]); LDIR /= np.linalg.norm(LDIR)
LC = np.array([0.6, 0.0, -2.0])
LVIEW = look_at(LDIR * 22 + LC, LC, (0, 1, 0))
LVP = ortho(-8, 8, -8, 8, 1, 50) @ LVIEW
shadow_tex = ctx.depth_texture((2048, 2048)); shadow_tex.compare_func = "<="
shadow_tex.repeat_x = shadow_tex.repeat_y = False
shadow_fbo = ctx.framebuffer(depth_attachment=shadow_tex)
SS = 4
msaa_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4, samples=SS)], depth_attachment=ctx.depth_renderbuffer((W, H), samples=SS))
res_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4)])
SKY = ((0.56, 0.62, 0.86), (0.99, 0.80, 0.72), (1.0, 0.86, 0.6))
KEYC = (1.0 * 2.25, 0.80 * 2.25, 0.58 * 2.25); SKYC = (0.62 * 0.85, 0.6 * 0.85, 0.8 * 0.85); GNDC = (0.5 * 0.45, 0.48 * 0.45, 0.3 * 0.45)
FOGC = (0.98, 0.84, 0.74)

def blink(tsec, off=0.0, period=3.3):
    ph = (tsec + off) % period
    return 1.0 - 0.92 * math.exp(-((ph - 0.1) / 0.06) ** 2)
def eyes(draws, M, centers, er, bl, U, look=(0, 0)):
    for c in centers:
        draws.append((EYE_W, M @ trans(*c) @ scale(er, er * bl, er * 0.8), U(mat=2, bump=0.0), False))
        if bl > 0.3:
            pc = np.array(c) + np.array([-np.sign(c[0]) * er * 0.05 + look[0] * er * 0.25, -er * 0.02 + look[1] * er * 0.2, er * 0.6])
            draws.append((EYE_P, M @ trans(*pc) @ scale(er * 0.6, er * 0.68 * bl, er * 0.45), U(mat=2, bump=0.0), False))
            hc = pc + np.array([er * 0.18, er * 0.28, er * 0.4])
            draws.append((EYE_W, M @ trans(*hc) @ scale(er * 0.17 * bl), U(mat=3, bump=0.0), False))

def splash_draws(draws, rips, t, e, t0, U, big=1.0):
    dt = t - t0
    if 0 <= dt < 3.0: rips.append((e[0], e[2], t0, 0.035 * big))
    if 0 <= dt < 0.75:
        r = np.random.default_rng(int(t0 * 100))
        for k in range(16):
            a = r.uniform(0, 6.28); sp = r.uniform(0.8, 1.8); vy = r.uniform(2.2, 3.6)
            x = e[0] + math.cos(a) * sp * dt; z = e[2] + math.sin(a) * sp * dt; y = vy * dt - 6.5 * dt * dt
            if y < -0.02: continue
            s = 0.05 * (1 - dt / 0.9)
            draws.append((PR["ball"], trans(x, y, z) @ scale(s), U(mat=2, bump=0.0, tint=(0.85, 0.95, 1.0), tintMix=1.0), False))
        # crown of water
        h = 0.45 * math.sin(math.pi * min(dt / 0.5, 1)) * big
        if h > 0.01:
            draws.append((PR["ring"], trans(e[0], 0.0, e[2]) @ scale(0.25 + 0.5 * dt, h * 4, 0.25 + 0.5 * dt), U(mat=2, bump=0.0, tint=(0.88, 0.96, 1.0), tintMix=1.0), False))
    if 0 <= dt < 1.6:
        for k in range(2):
            rr = 0.3 + 1.0 * (dt - 0.15 * k)
            if rr < 0.3: continue
            th = max(0.0, 1 - dt / 1.6)
            draws.append((PR["ring"], trans(e[0], 0.01, e[2]) @ scale(rr, 0.05 * th, rr), U(mat=3, bump=0.0, tint=(0.95, 0.98, 1.0), tintMix=1.0), False))

def build_draws(t):
    U = lambda **k: k
    draws = []; rips = []
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.8), False))
    draws.append((SC["water"], np.eye(4), U(mat=5, bump=0.0), False))
    draws.append((SC["rock"], np.eye(4), U(mat=0, bump=0.7, seed=4.0), True))
    draws.append((SC["slide"], np.eye(4), U(mat=0, bump=0.35, seed=9.0), True))
    # reed stilts under the slide
    for s in (0.5, 0.78):
        p, d = ride(s)
        draws.append((SC["reed"], trans(p[0], -0.3, p[2]) @ scale(0.55, p[1] + 0.32, 0.55), U(mat=0, bump=0.5), True))
    for k, (x, z, r) in enumerate(PADS):
        bob = 0.01 * math.sin(t * 1.4 + k)
        sc = r
        draws.append((SC["pad"], trans(x, 0.012 + bob, z) @ roty(PAD_ROT[k] + 0.05 * math.sin(t * 0.5 + k)) @ scale(sc, 1.0, sc), U(mat=0, bump=0.3), False))
    for k, (x, z) in enumerate(LILIES):
        draws.append((SC["lily"], trans(x, 0.03 + 0.01 * math.sin(t * 1.4 + k), z) @ roty(k) @ scale(1.1), U(mat=0, bump=0.2), False))
    for (x, z, r, s) in CATTAILS:
        sw = 0.04 * math.sin(t * 1.1 + x)
        draws.append((SC["cattail"], trans(x, min(gh(x, z), 0.0) - 0.05, z) @ roty(r) @ rotz(sw) @ scale(s), U(mat=0, bump=0.3), True))
    for (x, z, s) in BUSHES:
        draws.append((SC["bush"], trans(x, gh(x, z) - 0.05, z) @ roty(x) @ scale(s), U(mat=0, bump=0.7), True))
    for (x, z, s) in TREES:
        draws.append((SC["tree"], trans(x, gh(x, z) - 0.05, z) @ roty(x) @ rotz(0.03 * math.sin(t * 0.9 + x)) @ scale(s), U(mat=0, bump=0.7), True))
    for k, (x, z) in enumerate(FLOWERS):
        draws.append((SC["lily"], trans(x, gh(x, z) + 0.0, z) @ roty(k) @ scale(0.55), U(mat=0, bump=0.0, tint=FLC[k % 4], tintMix=0.6), False))
    for (x, y, z, sx, sy, sz, c) in [(-12, -1.6, -26, 11, 5.0, 4, (.86, .72, .62)), (11, -1.9, -27, 12, 5.8, 4, (.82, .7, .66)),
                                     (0, -3.0, -31, 16, 6.4, 5, (.8, .7, .74))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    draws.append((PR["ball"], trans(-4.5, 3.4, -34) @ scale(2.0), U(mat=3, bump=0.0, tint=(1.0, 0.93, 0.62), tintMix=1.0), False))
    for k, (x, y, z, s) in enumerate([(-5.5, 9.0, -22, 1.5), (4.5, 11.0, -24, 1.7), (0.5, 13.0, -26, 1.4), (7.0, 7.0, -20, 1.2)]):
        draws.append((SC["cloud"], trans(x + 0.06 * t, y, z) @ scale(s), U(mat=0, bump=0.3, tint=(1.0, 0.86, 0.82), tintMix=-1.0), False))
    # ---- splashes ----
    for key in T.SLIDES:
        e = entry_point(key); t0 = tb(T.SPLASH[key])
        splash_draws(draws, rips, t, e, t0, U)
        tp = t0 + POP_DELAY
        if 0 <= t - tp < 3: rips.append((e[0] * 0.65 + (PAD_L[0] if key != "bo1" else PAD_B[0]) * 0.35, e[2] * 0.65 + (PAD_L[1] if key != "bo1" else PAD_B[1]) * 0.35, tp, 0.015))
    # ---- Lulu ----
    fr = frog_state(t); tu = turtle_state(t)
    contacts = []
    fidx = min(int(t * FPS), len(MOUTH["lulu"]) - 1)
    if fr["vis"]:
        R, legs, arms = frog_mats(fr)
        u0 = U(mat=0, bump=1.0, seed=2.0)
        draws.append((FROGP["body"], R, u0, True))
        for li in range(2): draws.append((FROGP[f"leg{li}"], legs[li], u0, True))
        for ai in range(2): draws.append((FROGP[f"arm{ai}"], arms[ai], u0, True))
        eyes(draws, R, FROGD["eyes"]["centers"], FROGD["eyes"]["r"], blink(t), U)
        mo = MOUTH["lulu"][fidx]
        if mo > 0.06:
            mc = FROGD["mouth"]["c"]
            draws.append((PR["mouth"], R @ trans(*mc) @ scale(0.085, 0.06 * mo, 0.03), U(mat=0, bump=0.0), False))
        if fr["p"][1] < 0.3 and abs(fr["p"][1] - gh(fr["p"][0], fr["p"][2])) < 0.4:
            contacts.append((fr["p"][0], fr["p"][2], 0.6, 1.0))
        if fr["dizzy"] > 0.01:
            for k in range(3):
                a = t * 4 + k * 2.09
                c = fr["p"] + np.array([0.35 * math.cos(a), 1.5 + 0.05 * math.sin(a * 2), 0.35 * math.sin(a)])
                draws.append((PR["star"], trans(*c) @ roty(t * 3) @ scale(0.07 * fr["dizzy"]), U(mat=0, bump=0.0), False))
    # ---- Bo ----
    if tu["vis"]:
        R, Mh, legs = turtle_mats(tu)
        ub = U(mat=0, bump=1.0, seed=5.0)
        draws.append((TURP["shell"], R, ub, True))
        draws.append((TURP["head"], Mh, ub, True))
        for li in range(4): draws.append((TURP[f"leg{li}"], legs[li], ub, True))
        draws.append((TURP["tail"], R, ub, True))
        eyes(draws, Mh, TURD["eyes"]["centers"], TURD["eyes"]["r"], blink(t, 1.4, 3.7), U)
        mo = MOUTH["bo"][fidx]
        if mo > 0.06:
            mc = TURD["mouth"]["c"]
            draws.append((PR["mouth"], Mh @ trans(*mc) @ scale(0.055, 0.042 * mo, 0.025), U(mat=0, bump=0.0), False))
        if tu["p"][1] < 0.3: contacts.append((tu["p"][0], tu["p"][2], 0.85, 1.0))
        if tu["dizzy"] > 0.01:
            for k in range(3):
                a = t * 4 + k * 2.09
                c = tu["p"] + np.array([0.35 * math.cos(a), 1.25 + 0.05 * math.sin(a * 2), 0.35 * math.sin(a)])
                draws.append((PR["star"], trans(*c) @ roty(t * 3) @ scale(0.07 * tu["dizzy"]), U(mat=0, bump=0.0), False))
    # ---- turn star ----
    sp, sa = star_pos(t, fr, tu)
    if sp is not None and sa > 0.02:
        bob = 0.06 * math.sin(t * 3.0)
        ce = camera(t)[0]; fy = math.atan2(ce[0] - sp[0], ce[2] - sp[2])
        draws.append((PR["star"], trans(sp[0], sp[1] + bob, sp[2]) @ roty(fy + 0.4 * math.sin(t * 1.7)) @ rotz(0.12 * math.sin(t * 2.3)) @ scale(0.24 * sa),
                      U(mat=0, bump=0.25, seed=1.0), False))
        for k in range(5):
            a = t * 2.2 + k * 1.2566
            c = sp + np.array([0.42 * math.cos(a), bob + 0.1 * math.sin(a * 2), 0.42 * math.sin(a)])
            draws.append((PR["ball"], trans(*c) @ scale(0.025 * sa), U(mat=3, bump=0.0, tint=(1.0, 0.95, 0.6), tintMix=1.0), False))
    # finale sparkles
    if t >= tb(76):
        dtc = t - tb(76); r = np.random.default_rng(9)
        for k in range(26):
            a = r.uniform(0, 6.28); sp_ = r.uniform(0.6, 1.4)
            c = np.array([PAD_L[0] + math.cos(a) * sp_ * dtc, 0.8 + 2.4 * dtc - 1.8 * dtc * dtc + r.uniform(0, 0.6), PAD_L[1] + math.sin(a) * sp_ * dtc])
            if c[1] < 0.05: continue
            draws.append((PR["star"], trans(*c) @ roty(a + dtc * 3) @ scale(0.06), U(mat=0, bump=0.0, tint=FLC[k % 4], tintMix=0.5), False))
    return draws, contacts, rips

def render_frame(t):
    draws, contacts, rips = build_draws(t)
    eye, tgt, fov, up = camera(t)
    VPm = perspective(fov, W / H, 0.1, 90.0) @ look_at(eye, tgt, up)
    shadow_fbo.use(); shadow_fbo.clear(depth=1.0)
    sprog["LVP"].value = gl(LVP)
    ctx.disable(moderngl.CULL_FACE)
    for (mesh, M, u, cast) in draws:
        if cast: sprog["M"].value = gl(M); mesh.svao.render()
    msaa_fbo.use(); msaa_fbo.clear(0, 0, 0, 1, depth=1.0)
    ctx.disable(moderngl.DEPTH_TEST)
    fwd = (tgt - eye) / np.linalg.norm(tgt - eye)
    pitch = math.asin(max(-1, min(1, fwd[1])))
    hor = 0.5 - pitch / math.radians(fov) if up[1] > 0.5 else -2.0
    skyprog["cTop"].value = SKY[0]; skyprog["cMid"].value = SKY[1]; skyprog["cHor"].value = SKY[2]; skyprog["horY"].value = float(hor)
    sky_vao.render()
    ctx.enable(moderngl.DEPTH_TEST)
    shadow_tex.use(0); prog["shadowMap"].value = 0
    prog["VP"].value = gl(VPm); prog["LVP"].value = gl(LVP); prog["camPos"].value = tuple(eye)
    cvals = [tuple(c) for c in contacts] + [(0, 0, 1, 0)] * (8 - len(contacts))
    prog["contact"].value = cvals[:8]; prog["nContact"].value = len(contacts)
    rv = [tuple(r) for r in rips][:8]; prog["nRip"].value = len(rv); rv += [(0, 0, -99, 0)] * (8 - len(rv)); prog["rip"].value = rv
    prog["Ldir"].value = tuple(LDIR); prog["keyCol"].value = KEYC; prog["skyCol"].value = SKYC; prog["gndCol"].value = GNDC
    prog["fogCol"].value = FOGC; prog["skyHor"].value = SKY[2]; prog["skyMid"].value = SKY[1]; prog["time"].value = float(t)
    for (mesh, M, u, cast) in draws:
        prog["M"].value = gl(M); prog["NM"].value = nmat(M)
        prog["mat"].value = u.get("mat", 0); prog["bump"].value = u.get("bump", 1.0)
        prog["tint"].value = tuple(u.get("tint", (1, 1, 1))); prog["tintMix"].value = u.get("tintMix", 0.0)
        prog["seed"].value = u.get("seed", 0.0)
        mesh.vao.render()
    ctx.copy_framebuffer(res_fbo, msaa_fbo)
    img = np.frombuffer(res_fbo.read(components=4), np.uint8).reshape(H, W, 4)[::-1].copy()
    img[..., 3] = 255
    return img

# ---------------- 2D overlay ----------------
WORDS = json.load(open("out/word_times.json"))
LINES = {}
for w_ in WORDS: LINES.setdefault(w_["line"], []).append(w_)
LINE_LIST = sorted(LINES.values(), key=lambda ws: ws[0]["t0"])
tf = skia.Typeface.MakeFromFile("assets/Fredoka.ttf")
def wght(v):
    try:
        arg = skia.FontArguments(); arg.setVariationDesignPosition(skia.FontArguments.VariationPosition(
            skia.FontArguments.VariationPosition.Coordinates([skia.FontArguments.VariationPosition.Coordinate(0x77676874, v)])))
        return tf.makeClone(arg)
    except Exception:
        return tf
TF6 = wght(600); TF7 = wght(700)
FONT = skia.Font(TF7, 68); TFONT = skia.Font(TF7, 128); SFONT = skia.Font(TF6, 56); NFONT = skia.Font(TF7, 44)
grain = np.random.default_rng(1).integers(0, 255, (H, W), dtype=np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
vig = (1 - 0.22 * np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.25, 0, 1)).astype(np.float32)
INK = (52, 34, 60)
def hexrgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
WHO_COL = {"lulu": (74, 170, 40), "bo": (232, 120, 30), "both": (52, 34, 60)}

def current_line(t):
    for li, ws in enumerate(LINE_LIST):
        start = ws[0]["t0"] - 0.25
        nxt = LINE_LIST[li + 1][0]["t0"] - 0.25 if li + 1 < len(LINE_LIST) else 1e9
        end = min(ws[-1]["t1"] + 0.55, nxt)
        if start <= t < end: return ws, start, end
    return None, 0, 0

def outlined(cv, text, x, y, font, rgb, a, sw=16, oc=INK):
    st = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=sw, Color=skia.Color(*oc, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
    fp = skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(255 * a)))
    cv.drawString(text, x, y, font, st); cv.drawString(text, x, y, font, fp)

def overlay(img, t):
    surf = skia.Surface(img); cv = surf.getCanvas()
    # title: a swinging clay sign hung from two strings
    if t < 4.4:
        a = clamp01(t / 0.35) * clamp01((4.4 - t) / 0.4)
        drop = 160 * (1 - ease(t / 0.7))
        ang = 3.0 * math.sin(t * 2.4) * math.exp(-t * 0.3)
        cv.save(); cv.translate(W / 2, 250 - drop); cv.rotate(ang)
        sp = skia.Paint(AntiAlias=True, Color=skia.Color(120, 80, 60, int(255 * a)), StrokeWidth=6, Style=skia.Paint.kStroke_Style)
        cv.drawLine(-300, -250, -300, 40, sp); cv.drawLine(300, -250, 300, 40, sp)
        sh = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-430, 40 + 14, 860, 330), 70, 70)
        cv.drawRRect(sh, skia.Paint(AntiAlias=True, Color=skia.Color(90, 50, 40, int(70 * a))))
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-430, 40, 860, 330), 70, 70)
        cv.drawRRect(rr, skia.Paint(AntiAlias=True, Color=skia.Color(255, 246, 228, int(250 * a))))
        cv.drawRRect(rr, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=14, Color=skia.Color(246, 156, 70, int(255 * a))))
        l1, l2 = "My Turn,", "Your Turn!"
        outlined(cv, l1, -TFONT.measureText(l1) / 2, 165, TFONT, (255, 70, 120), a, 14, (255, 255, 255))
        outlined(cv, l2, -TFONT.measureText(l2) / 2, 290, TFONT, (0, 160, 220), a, 14, (255, 255, 255))
        sub = T.SUBTITLE
        cv.drawString(sub, -SFONT.measureText(sub) / 2, 345, SFONT, skia.Paint(AntiAlias=True, Color=skia.Color(*INK, int(230 * a))))
        cv.restore()
    # lesson badges
    for (t0, t1, txt, col) in T.BADGES:
        if t0 <= t < t1:
            a = clamp01((t - t0) / 0.15) * clamp01((t1 - t) / 0.3)
            pop = 1 + 0.22 * math.exp(-(t - t0) * 6) * math.sin((t - t0) * 15)
            f = skia.Font(TF7, 128 * pop); tw = f.measureText(txt)
            bw, bh = tw + 110, 190 * pop
            cy = 330 + 6 * math.sin(t * 3)
            cv.save(); cv.translate(W / 2, cy); cv.rotate(-3 + 2 * math.sin(t * 1.7))
            shd = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-bw / 2, -bh / 2 + 14, bw, bh), bh / 2, bh / 2)
            cv.drawRRect(shd, skia.Paint(AntiAlias=True, Color=skia.Color(60, 30, 40, int(80 * a))))
            rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-bw / 2, -bh / 2, bw, bh), bh / 2, bh / 2)
            cv.drawRRect(rr, skia.Paint(AntiAlias=True, Color=skia.Color(*hexrgb(col), int(255 * a))))
            cv.drawRRect(rr, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=12, Color=skia.Color(255, 255, 255, int(255 * a))))
            cv.drawString(txt, -tw / 2, 44 * pop, f, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(255 * a))))
            cv.restore()
    # guessing pause: a big "?" bubble
    QX, QY = W - 210, 520
    for (a0, a1) in T.GUESS_PAUSES:
        if a0 <= t < a1 + 0.1:
            a = clamp01((t - a0) / 0.2) * clamp01((a1 + 0.1 - t) / 0.2)
            s = 1 + 0.08 * math.sin((t - a0) * 7)
            cv.drawCircle(QX, QY, 120 * s, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(235 * a))))
            cv.drawCircle(QX, QY, 120 * s, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=10, Color=skia.Color(255, 196, 30, int(255 * a))))
            f = skia.Font(TF7, 190 * s); q = "?"
            cv.drawString(q, QX - f.measureText(q) / 2, QY + 66 * s, f, skia.Paint(AntiAlias=True, Color=skia.Color(255, 150, 20, int(255 * a))))
    # lyric captions: teal bar, white words, sunshine highlight; speaker chip for spoken lines
    ws, start, end = current_line(t)
    if ws:
        a = clamp01((t - start) / 0.15) * clamp01((end - t) / 0.15)
        space = FONT.measureText(" ")
        rows, cur, wsum = [], [], 0
        for w_ in ws:
            wl = FONT.measureText(w_["w"])
            if cur and wsum + space + wl > 860: rows.append(cur); cur, wsum = [], 0
            wsum += (space if cur else 0) + wl; cur.append((w_, wl))
        if cur: rows.append(cur)
        y = 1500 - 42 * (len(rows) - 1)
        maxw = max(sum(wl for _, wl in r) + space * (len(r) - 1) for r in rows)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - maxw) / 2 - 44, y - 76, maxw + 88, 86 * len(rows) + 36), 30, 30)
        cv.drawRRect(rr, skia.Paint(AntiAlias=True, Color=skia.Color(24, 88, 104, int(200 * a))))
        if not ws[0]["sung"]:
            who = ws[0]["who"]; nm = "Lulu" if who == "lulu" else "Bo"; nw = NFONT.measureText(nm)
            cx0 = (W - maxw) / 2 - 44 + 20; cy0 = y - 76 - 44
            chip = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx0, cy0, nw + 44, 62), 31, 31)
            cv.drawRRect(chip, skia.Paint(AntiAlias=True, Color=skia.Color(*WHO_COL[who], int(255 * a))))
            cv.drawString(nm, cx0 + 22, cy0 + 46, NFONT, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(255 * a))))
        for row in rows:
            tw = sum(wl for _, wl in row) + space * (len(row) - 1); x = (W - tw) / 2
            for (w_, wl) in row:
                on = w_["t0"] - 0.03 <= t < max(w_["t1"], w_["t0"] + 0.25)
                col = (255, 214, 60) if on else (255, 255, 255)
                p = skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(255 * a)))
                cv.drawString(w_["w"], x, y - (5 if on else 0), FONT, p)
                x += wl + space
            y += 86
    out = img[..., :3].astype(np.float32) * vig[..., None]
    out *= np.array([1.02, 1.0, 0.97], np.float32)
    out += (grain[..., None].astype(np.float32) - 127) * (7 / 255.0)
    return np.clip(out, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "x":
        for s in sys.argv[2:]:
            t0 = time.time(); fr = overlay(render_frame(float(s)), float(s))
            skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/still_{float(s):05.2f}.png")
            print(s, round(time.time() - t0, 2), "s", flush=True)
        sys.exit()
    nfr = int(T.DURATION * FPS)
    if len(sys.argv) > 1 and sys.argv[1] == "prev":
        step = int(sys.argv[2]); outp = sys.argv[3]
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS / step), "-i", "-",
               "-i", "out/audio.wav", "-c:v", "libx264", "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", outp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE); t0 = time.time()
        for fi in range(0, nfr, step):
            p.stdin.write(render_frame(fi / FPS)[..., :3].tobytes())
        p.stdin.close(); p.wait(); print("preview", round(time.time() - t0), "s"); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "seg":
        f0, f1, outp, audio = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], []
    else:
        outp = sys.argv[1] if len(sys.argv) > 1 else "out/my_turn_your_turn.mp4"
        f0, f1 = 0, int(sys.argv[2]) if len(sys.argv) > 2 else nfr
        audio = ["-i", "out/audio.wav", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + \
          audio[:2] + ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"] + audio[2:] + [outp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(f0, min(f1, nfr)):
        tsec = fi / FPS
        p.stdin.write(overlay(render_frame(tsec), tsec).tobytes())
        if fi % 90 == 0: print(f"frame {fi}/{min(f1, nfr)}  {time.time() - t0:.0f}s", flush=True)
    p.stdin.close(); p.wait()
    n = min(f1, nfr) - f0
    print(f"done: {n} frames in {time.time() - t0:.0f}s ({(time.time() - t0) / max(n, 1):.2f} s/frame) -> {outp}", flush=True)
