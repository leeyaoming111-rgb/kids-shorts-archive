"""Tumble & Pip, Episode 2: Big and Small!  Shot-based 3D claymation renderer driven by the ElevenLabs song timings.
python3 render.py [out.mp4] | x <secs...> | seg f0 f1 out.mp4 | qa"""
from render_base import *

def ease(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def lerp(a, b, u): return np.asarray(a, float) * (1 - u) + np.asarray(b, float) * u
def clampu(t, a, b): return min(max((t - a) / max(b - a, 1e-6), 0.0), 1.0)
def apply(M, p): return (M @ np.array([p[0], p[1], p[2], 1.0]))[:3]
SEC = T.sec
SH = {n: (a, b) for a, b, n in T.SHOTS}

FOXP = {k: Mesh(p["mesh"]) for k, p in D["fox"]["parts"].items() if "mesh" in p}
FOXD = D["fox"]["parts"]
PIPP = {k: Mesh(p["mesh"]) for k, p in D["pip"]["parts"].items() if "mesh" in p}
PIPD = D["pip"]["parts"]
PR = {k: Mesh(m) for k, m in D["props"].items()}
SC = {k: Mesh(m) for k, m in D["scene"].items()}
E2 = {k: Mesh(m) for k, m in D["ep2"].items()}
EYE_W, EYE_P = Mesh(D["eye_w"]), Mesh(D["eye_p"])
MOUTH = {w: json.load(open(f"out/mouth_{w}.json")) for w in ("tumble", "pip")}

# ---------------- world layout ----------------
BLANKET = (0.0, 0.3, 1.2, 0.9)                 # centre x, z, half sizes
def on_blanket(x, z): return abs(x - BLANKET[0]) < BLANKET[2] and abs(z - BLANKET[1]) < BLANKET[3]
def surf(x, z): return ground_h(x, z) + (0.04 if on_blanket(x, z) else 0.0)
BASKET = (-0.62, 0.78)
APPLE_TREE = (-3.3, -2.8)
STUMP = (2.7, -1.0); STUMP_TOP = 0.548 - 0.02          # mesh top, drawn 0.02 below ground level
FOX_SEAT = float(D["fox"]["parts"]["body"]["mesh"]["v"][:, 1].min()) - 0.012   # body's lowest vertex (+ squash margin)
MUSH = (1.75, -0.2); MUSH_S = 0.32; MUSH_TOP = 0.976 * MUSH_S - 0.01
BERRY = (0.6, 1.0)
R1POS = (0.15, -0.95)
COTTAGE_FAR = (7.5, -17.0)
APPLE_R = 0.42 * 0.85            # upright (held)
ROLL_R = 0.46 * 0.85             # rolling on its side: stem along the roll axis, round cross-section
rng = np.random.default_rng(9)
FLOWERS = []
pastel = [(1.0, .72, .82), (1.0, .85, .6), (.78, .72, 1.0), (.7, .86, 1.0), (1.0, 1.0, 1.0), (1.0, .78, .7)]
while len(FLOWERS) < 70:
    x, z = rng.uniform(-8, 8), rng.uniform(-9, 3.5)
    if abs(x) < 1.6 and -0.9 < z < 1.5: continue
    if (x - STUMP[0]) ** 2 + (z - STUMP[1]) ** 2 < 1.2 or (x - MUSH[0]) ** 2 + (z - MUSH[1]) ** 2 < 0.5: continue
    if (x - APPLE_TREE[0]) ** 2 + (z - APPLE_TREE[1]) ** 2 < 1.2: continue
    if -6.6 < z < -4.4: continue
    if 0.3 < z < 1.6 and -0.2 < x < 3.4: continue           # the apple's rolling lane
    FLOWERS.append((x, z, rng.uniform(0, 6.28), pastel[len(FLOWERS) % 6], rng.uniform(0.9, 1.4)))
SKY = ((0.48, 0.74, 0.97), (0.72, 0.87, 1.0), (1.0, 0.94, 0.84))

def stomp_shake(t):
    s = 0.0
    for st_ in T.STOMPS + [T.BIG_HOP + 0.95]:
        d = t - st_
        if 0 <= d < 0.5: s += math.exp(-d * 9) * math.sin(d * 60)
    return s

# ---------------- props over time ----------------
def apple_state(t):
    """returns (world pos, roll angle, held)"""
    a0, a1 = SH["big0"]; g0, g1 = SH["gag0"]
    if t < a0: return None
    if t < SH["small0"][0]: return "held", 0.0
    start = np.array([0.0, 0, 1.6]); end = np.array([4.4, 0, 1.95])
    if t < g0 + 0.35: p = start
    else:
        u = clampu(t, g0 + 0.35, g1 - 0.1); p = lerp(start, end, 1 - (1 - u) ** 1.6)
    dist = p[0] - start[0]
    return np.array([p[0], surf(p[0], p[2]) + ROLL_R, p[2]]), -dist / ROLL_R

def mush_squash(t):
    d = t - T.SQUASH
    if d < 0: return 1.0
    if d < 0.35: return 1 - 0.62 * ease(d / 0.2)
    return 1 - 0.62 * math.exp(-(d - 0.35) * 7) * math.cos((d - 0.35) * 18)

# ---------------- Tumble ----------------
def tumble(t):
    st = dict(x=-0.4, z=-0.4, yaw=0.0, y=0.0, sq=0.015 * math.sin(t * 3.7), roll=0.0, sit=0.0,
              head=[0.0, 0.06 * math.sin(t * 1.3), 0.0], arms=[[0.15, 0.0], [0.15, 0.0]], legs=[0.0, 0.0],
              tail=0.25 * math.sin(t * 2.6), carry=None, vis=True)
    pulse = (t / (60 / 88.0)) % 1.0                                      # dotted-quarter pulse
    def walk(p0, p1, a, b):
        u = clampu(t, a, b); st["x"], st["z"] = lerp(p0, p1, ease(u))
        if 0 < u < 1:
            ph = (t - a) * 2 * math.pi * 2.2
            st["y"] += 0.05 * abs(math.sin(ph)); st["legs"] = [0.08 * max(0, math.sin(ph)), 0.08 * max(0, -math.sin(ph))]
            st["yaw"] = math.atan2(p1[0] - p0[0], p1[1] - p0[1])
    n = T.shot_at(t)[1]
    if n == "flyover":
        walk((-3.6, 1.6), (BASKET[0], BASKET[1] - 1.05), 0.4, 3.6)
        st["carry"] = "basket"; st["arms"] = [[0.2, 1.35], [0.2, 1.35]]
        if t > 3.6: st["yaw"] = 0.0
    elif n == "overhead":
        a, b = SH["overhead"]
        if t < a + 0.9: st["carry"] = "basket"; st["arms"] = [[0.35, 1.25 - 0.6 * clampu(t, a, a + 0.9)], [0.35, 1.25 - 0.6 * clampu(t, a, a + 0.9)]]
        st["x"], st["z"] = BASKET[0], BASKET[1] - 1.05
        sway = math.sin(2 * math.pi * pulse)
        st["roll"] = 0.1 * sway; st["y"] += 0.05 * abs(sway); st["head"][2] = 0.12 * sway
        if t > a + 1.0: st["arms"] = [[0.7 + 0.3 * sway, 0.3], [0.7 - 0.3 * sway, 0.3]]
    elif n in ("big0", "small0"):
        st["x"], st["z"] = R1POS
        if n == "big0":
            u = clampu(t, SH["big0"][0], SH["big0"][0] + 0.5)
            st["arms"] = [[0.15 + 0.5 * u, 1.15 * u], [0.15 + 0.5 * u, 1.15 * u]]; st["head"][0] = -0.12 * u
            st["y"] += 0.06 * abs(math.sin((t - SH["big0"][0]) * 5)) * u
            st["sq"] += 0.03 * math.sin(t * 9) * u
    elif n == "gag0":
        a, b = SH["gag0"]
        ap = apple_state(t)[0]
        u = ease(clampu(t, a + 0.2, a + 0.9))
        uz = ease(clampu(t, a + 0.5, a + 0.95))
        st["x"] = lerp(R1POS[0], max(ap[0] - 1.05, 0.6), u); st["z"] = lerp(R1POS[1], ap[2] - 0.35, uz)
        if t > a + 0.2:
            ph = (t - a) * 2 * math.pi * 2.6
            st["y"] += 0.06 * abs(math.sin(ph)); st["legs"] = [0.1 * max(0, math.sin(ph)), 0.1 * max(0, -math.sin(ph))]
            st["yaw"] = 1.35 * u
        st["arms"] = [[1.4, 1.0], [1.4, 1.0]]
    elif n == "big1":
        st["x"], st["z"] = 0.1, -0.5
        sw = math.sin((t - SH["big1"][0]) * 3.4)
        if T.WHOOSH and abs(t - T.WHOOSH - 0.2) < 0.45: sw = math.sin((t - T.WHOOSH + 0.25) * 7)
        st["arms"] = [[1.5 + 0.6 * sw, 0.3], [0.5, 0.4]]; st["roll"] = -0.1 * sw
        st["carry"] = "bigleaf"; st["leaf_swing"] = sw
    elif n == "gag1":
        st["x"], st["z"] = 0.1, -0.5
        st["carry"] = "bigleaf"; st["leaf_swing"] = 1.0 - 1.6 * ease(clampu(t, SH["gag1"][0], SH["gag1"][0] + 0.35))
        st["arms"] = [[1.5 + 0.6 * st["leaf_swing"], 0.3], [0.5, 0.4]]; st["yaw"] = 0.55
    elif n == "small1":
        st["x"], st["z"] = 0.1, -0.5; st["carry"] = "bigleaf"; st["leaf_swing"] = 0.0; st["arms"] = [[1.5, 0.3], [0.5, 0.4]]
    elif n == "big2":
        a, b = SH["big2"]
        front = (STUMP[0] - 1.15, STUMP[1] - 0.5)
        walk((0.6, -0.6), front, a - 0.01, a + 1.0)
        if t > a + 1.0:
            u = ease(clampu(t, a + 1.0, a + 1.45))
            st["x"], st["z"] = lerp(front, (STUMP[0], STUMP[1] + 0.05), u); st["yaw"] = 1.15 * (1 - u) - 0.5 * u
            st["y"] += 0.95 * math.sin(math.pi * u) + 0.12 * math.sin(math.pi * u) ** 0.5; st["sit"] = u
            st["arms"] = [[1.7 - 0.6 * u, 0.4 + 0.2 * u], [1.7 - 0.6 * u, 0.4 + 0.2 * u]]
    elif n == "small2":
        st["x"], st["z"] = STUMP[0], STUMP[1] + 0.05; st["yaw"] = -0.5; st["sit"] = 1.0
    elif n == "gag2":
        a, b = SH["gag2"]
        dq = t - T.SQUASH
        u0 = ease(clampu(t, a + 0.05, T.SQUASH))
        side = (MUSH[0] - 0.65, MUSH[1] + 0.35)
        st["x"], st["z"] = lerp(side, MUSH, u0); st["yaw"] = 0.25
        st["y"] += 0.6 * math.sin(math.pi * u0) if dq < 0 else 0.0
        st["sit"] = u0
        if dq > 0.35:                                                     # boinged up and lands beside it
            u = clampu(dq, 0.35, 1.25)
            st["x"], st["z"] = lerp(MUSH, (MUSH[0] - 0.75, MUSH[1] + 0.35), u)
            st["y"] += 0.75 * math.sin(math.pi * u) + (MUSH_TOP + 0.02) * (1 - u); st["sit"] = 1.0
            st["roll"] = 0.35 * math.sin(math.pi * u); st["arms"] = [[2.3, 0.4], [2.3, 0.4]]
        st["mush_seat"] = dq <= 0.35
    elif n == "big3":
        st["x"], st["z"] = -0.2, -0.3
        for s_ in T.STOMPS:
            d = t - s_
            if -0.3 < d < 0: st["legs"] = [0.22 * math.sin(math.pi * (d + 0.3) / 0.3), 0]; st["y"] += 0.08 * math.sin(math.pi * (d + 0.3) / 0.3)
            if 0 <= d < 0.5: st["sq"] -= 0.15 * math.exp(-d * 7) * math.cos(d * 12)
        st["arms"] = [[0.9, 0.2], [0.9, 0.2]]
    elif n in ("small3", "gag3"):
        st["x"], st["z"] = -0.2, -0.3
        d = t - T.BIG_HOP
        if 0 <= d < 0.95:
            u = d / 0.95; st["y"] += 1.5 * math.sin(math.pi * u); st["sq"] += 0.08 * math.sin(math.pi * u)
            st["arms"] = [[2.5, 0.2], [2.5, 0.2]]; st["legs"] = [0.1, 0.1]
        elif -0.25 < d < 0: st["sq"] -= 0.12 * math.sin(math.pi * (d + 0.25) / 0.25)
        elif 0.95 <= d < 1.6: st["sq"] -= 0.2 * math.exp(-(d - 0.95) * 6) * math.cos((d - 0.95) * 12)
    elif n in ("split", "together", "crane_out"):
        st["x"], st["z"] = -0.2, -0.3
        sway = math.sin(2 * math.pi * pulse)
        st["roll"] = 0.08 * sway; st["head"][2] = 0.1 * sway
        st["arms"] = [[0.8 + 0.3 * sway, 0.3], [0.8 - 0.3 * sway, 0.3]]
        if n == "crane_out":
            ph = (t - SH["crane_out"][0]) * 2 * math.pi * 1.4
            st["arms"][0] = [2.35 + 0.35 * math.sin(ph), 0.2]
    return st

def fox_mats(st):
    gy = surf(st["x"], st["z"])
    sit = st["sit"]
    seat = None
    if sit > 0:
        if st.get("mush_seat"): seat = ground_h(*MUSH) + (MUSH_TOP + 0.01) * mush_squash_now - 0.01
        elif abs(st["x"] - STUMP[0]) < 0.3: seat = ground_h(*STUMP) + STUMP_TOP
        else: seat = gy
    base_y = gy
    if seat is not None: base_y = gy * (1 - sit) + (seat - FOX_SEAT + 0.01) * sit
    sq = st["sq"]
    R = trans(st["x"], base_y - 0.01 + st["y"] + 0.22 * abs(math.sin(st["roll"])), st["z"]) @ roty(st["yaw"]) @ rotz(st["roll"]) @ scale(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5)
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
        legs.append(R @ trans(0, st["legs"][li], 0) @ trans(*pv) @ rotx(-1.35 * sit) @ trans(*(-np.array(pv))))
    return R, Mh, arms, legs
mush_squash_now = 1.0

# ---------------- Pip ----------------
PIP_FOOT = 0.060
UP = np.array([0, PIP_FOOT, 0])
def pip_state(t, st, mats):
    """returns pos, yaw, flying, flip(rotation about x), perch flag, extra dict"""
    R, Mh, arms, legs = mats
    n = T.shot_at(t)[1]
    hop_y = 0.0
    def on_ground(x, z): return np.array([x, surf(x, z), z]) + UP
    if n == "flyover":
        u = clampu(t, 0.3, 3.7)
        p = lerp((-3.0, 2.6, 2.2), (0.2, 1.6, 1.1), ease(u)) + np.array([0, 0.25 * math.sin(t * 5), 0])
        return p, 1.4, True, 0.0, False, {}
    if n == "overhead":
        a, b = SH["overhead"]
        ang = (t - a) * 0.9
        x, z = 0.6 + 0.45 * math.cos(ang), 0.4 + 0.33 * math.sin(ang)
        pulse = ((t - a) / (60 / 88.0)) % 1.0
        p = on_ground(x, z) + np.array([0, 0.18 * math.sin(math.pi * pulse), 0])
        return p, ang + math.pi, False, 0.0, False, {}
    if n == "big0":
        return on_ground(0.95, -0.55), -0.7, False, 0.0, False, {}
    if n == "small0":
        return on_ground(*BERRY) + np.array([0.0, 0, -0.05]), 0.25, False, 0.0, False, {"point": True}
    if n == "gag0":
        a, b = SH["gag0"]
        ap, roll = apple_state(t)
        top = ap + np.array([0, ROLL_R + 0.012, 0]) + UP
        return top - np.array([0, 0.016, 0]), 1.2 + 0.25 * math.sin(t * 16), False, -0.18 + 0.12 * math.sin(t * 32), True, {"run": True}
    if n == "big1":
        return on_ground(1.0, 0.25), -0.6, False, 0.0, False, {}
    if n == "gag1":
        a, b = SH["gag1"]
        u = clampu(t, a, b - 0.25)
        p0, p1 = on_ground(1.0, 0.25), np.array([BASKET[0] + 0.25, surf(*BASKET) + 0.51, BASKET[1]])
        p = lerp(p0, p1 + np.array([0, 0.05 * (1 - u), 0]), ease(u)); p[1] += 2.4 * math.sin(math.pi * u) ** 0.55; p[2] += 0.9 * math.sin(math.pi * u)
        return p, -0.6 + 2.17 * ease(u), False, -2 * math.pi * ease(min(1.0, u / 0.8)), False, {"tucked": True}      # tumbling, wings tucked, lands wings along the handle
    if n == "small1":
        return on_ground(1.0, 0.25), -0.35, False, 0.0, False, {"tinyleaf": True}
    if n == "big2":
        return on_ground(1.8, -0.55), -0.5, False, 0.0, False, {}
    if n == "small2":
        a, b = SH["small2"]
        top = np.array([MUSH[0], ground_h(*MUSH) + MUSH_TOP, MUSH[1]]) + UP - np.array([0, 0.004, 0])
        u = clampu(t, a, a + 0.3)
        if u < 1:
            p = lerp(on_ground(MUSH[0] - 0.2, MUSH[1] + 0.5), top, ease(u)); p[1] += 0.3 * math.sin(math.pi * u)
            return p, 0.2, True, 0.0, False, {}
        return top, 0.2, False, 0.0, True, {}
    if n == "gag2":
        a, b = SH["gag2"]
        top = np.array([MUSH[0], ground_h(*MUSH) + MUSH_TOP, MUSH[1]]) + UP
        u = clampu(t, a - 0.25, a + 0.05); dest = on_ground(MUSH[0] + 0.75, MUSH[1] + 0.55)
        p = lerp(top, dest, ease(u)); p[1] += 0.25 * math.sin(math.pi * u)
        return p, -0.5, u < 1, 0.0, False, {}
    if n in ("big3", "small3", "gag3"):
        x, z = 0.75, 0.65
        p = on_ground(x, z); flip = 0.0; fly = False
        for s_ in T.STOMPS:                               # Tumble's stomps bounce Pip
            d = t - s_
            if 0 <= d < 0.35: p[1] += 0.25 * math.sin(math.pi * d / 0.35)
        if T.PIP_HOP and 0 <= t - T.PIP_HOP < 0.3: p[1] += 0.18 * math.sin(math.pi * (t - T.PIP_HOP) / 0.3)
        d = t - (T.BIG_HOP + 0.95)                        # the giant landing flips him
        if 0 <= d < 0.7: p[1] += 0.8 * math.sin(math.pi * d / 0.7); flip = 2 * math.pi * ease(d / 0.7); fly = True
        ex = {}
        d0 = t - (T.TINY_STOMP - 0.35)
        if 0 <= d0 < 0.35: p[1] += 0.22 * math.sin(math.pi * d0 / 0.35); flip = -0.25 * math.sin(math.pi * d0 / 0.35)
        if 0 <= t - T.TINY_STOMP < 0.4: ex["tinystomp"] = (t - T.TINY_STOMP) / 0.4
        return p, -0.3, fly, flip, False, ex
    if n == "split":
        p = on_ground(0.75, 0.65); pulse = (t / (60 / 88.0)) % 1.0
        return p + np.array([0, 0.1 * math.sin(math.pi * pulse), 0]), 0.0, False, 0.0, False, {}
    # together / crane_out: fly up onto Tumble's forehead
    a = SH["together"][0]
    head = apply(Mh, (0, 1.85, 0.15)) + UP
    u = clampu(t, a, a + 0.7)
    if u < 1:
        p = lerp(on_ground(0.75, 0.65), head, ease(u)); p[1] += 0.5 * math.sin(math.pi * u)
        return p, 0.0, True, 0.0, False, {}
    return head, st["yaw"], False, 0.0, True, {}

# ---------------- camera ----------------
def camera(t, which=None):
    i, name, u, lt = T.shot_at(t)
    fov = 40.0
    if name == "flyover":
        e = ease(lt / 3.8)
        eye, tgt = lerp((-6.5, 7.5, 9.0), (-1.2, 1.7, 5.4), e), lerp((2.0, 0.5, -10), (-1.0, 1.0, 0.6), e)
    elif name == "overhead":
        e = ease(u)
        eye, tgt = np.array([-0.6 + 0.1 * e, 7.4 - 0.4 * e, 1.3]), np.array([-0.55, 0.0, 0.2])
        fov = 50.0
    elif name == "big0":
        eye, tgt = lerp((R1POS[0] + 1.0, 0.95, R1POS[1] + 4.7), (R1POS[0] + 0.9, 1.0, R1POS[1] + 4.1), ease(u)), np.array([R1POS[0], 1.4, R1POS[1]])
        fov = 46.0
    elif name == "small0":
        eye, tgt = lerp((1.0, 0.5, 2.85), (0.95, 0.48, 2.65), ease(u)), np.array([0.68, 0.2, 1.05])
        fov = 36.0
    elif name == "gag0":
        ap = apple_state(t)[0]
        cx = 0.5 * (ap[0] + tumble(t)["x"])
        eye, tgt = np.array([cx + 0.1, 1.3, 6.6]), np.array([cx, 0.8, 1.0])
        fov = 50.0
    elif name == "big1":
        eye, tgt = lerp((1.2, 1.2, 5.3), (1.1, 1.25, 4.9), ease(u)), np.array([0.65, 1.75, -0.4])
        fov = 46.0
    elif name == "gag1":
        eye, tgt = np.array([1.6, 1.55, 5.6]), np.array([0.3, 1.25, 0.1])
        fov = 54.0
    elif name == "small1":
        eye, tgt = lerp((1.55, 0.55, 2.55), (1.5, 0.52, 2.3), ease(u)), np.array([1.05, 0.33, 0.25])
        fov = 38.0
    elif name == "big2":
        eye, tgt = lerp((1.5, 0.75, 3.3), (1.6, 0.8, 3.0), ease(u)), np.array([2.45, 1.35, -0.8])
        fov = 48.0
    elif name == "small2":
        mx, mz = MUSH
        eye, tgt = lerp((mx + 0.3, 0.48, mz + 1.8), (mx + 0.26, 0.48, mz + 1.6), ease(u)), np.array([mx, 0.45, mz])
        fov = 38.0
    elif name == "gag2":
        eye, tgt = np.array([MUSH[0] + 1.3, 1.7, MUSH[1] + 5.6]), np.array([MUSH[0] - 0.3, 1.0, MUSH[1] + 0.2])
        fov = 52.0
    elif name == "big3":
        eye, tgt = np.array([0.3, 0.35, 4.4]), np.array([0.0, 1.05, -0.2])
        fov = 46.0
    elif name == "small3":
        eye, tgt = lerp((0.95, 0.32, 2.4), (0.92, 0.32, 2.2), ease(u)), np.array([0.75, 0.3, 0.65])
        fov = 36.0
    elif name == "gag3":
        eye, tgt = np.array([0.6, 1.1, 5.6]), np.array([0.2, 1.4, -0.1])
        fov = 48.0
    elif name == "split":
        if which == "bottom":
            eye, tgt = np.array([0.9, 0.34, 2.3]), np.array([0.75, 0.33, 0.65]); fov = 32.0
        else:
            eye, tgt = np.array([-0.15, 1.55, 2.3]), np.array([-0.2, 1.45, -0.3]); fov = 30.0
    elif name == "together":
        eye, tgt = lerp((0.0, 1.55, 4.3), (0.0, 1.6, 3.9), ease(u)), np.array([-0.15, 1.65, -0.3])
    else:
        e = ease(lt / 2.7)
        eye, tgt = lerp((0.0, 1.6, 3.9), (0.6, 6.5, 13.5), e), lerp((-0.15, 1.65, -0.3), (0.0, 1.0, -3.5), e)
    sh = stomp_shake(t)
    if sh:
        eye = eye + np.array([0.03 * sh, 0.02 * sh, 0]); tgt = tgt + np.array([0.03 * sh, 0.02 * sh, 0])
    return eye, tgt, fov

# ---------------- draws ----------------
LDIR = np.array([-0.55, 0.85, 0.5]); LDIR /= np.linalg.norm(LDIR)
LVIEW = look_at(LDIR * 20 + np.array([0, 0, -1.0]), np.array([0, 0, -1.0]), (0, 1, 0))
LVP = ortho(-10, 10, -10, 10, 1, 45) @ LVIEW
shadow_tex = ctx.depth_texture((2048, 2048)); shadow_tex.compare_func = "<="
shadow_tex.repeat_x = shadow_tex.repeat_y = False
shadow_fbo = ctx.framebuffer(depth_attachment=shadow_tex)
SS = 4
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

def leaf_M(arms, st, small=False):
    hand = apply(arms[0], FOXD["arm0"]["hand"])
    sw = st.get("leaf_swing", 0.0)
    return trans(*hand) @ roty(st["yaw"]) @ rotz(0.55 + 0.55 * sw) @ rotx(math.pi / 2 - 0.25) @ trans(1.28, 0, 0)

def build_draws(t):
    global mush_squash_now
    U = lambda **k: k
    draws = []
    mush_squash_now = mush_squash(t)
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.8), False))
    draws.append((E2["blanket"], trans(BLANKET[0], ground_h(BLANKET[0], BLANKET[1]) + 0.0, BLANKET[1]), U(mat=0, bump=0.3), False))
    draws.append((E2["appletree"], trans(APPLE_TREE[0], ground_h(*APPLE_TREE) - 0.05, APPLE_TREE[1]) @ scale(1.25), U(mat=0, bump=0.8, obj="tree"), True))
    for (x, z, s) in [(-7.5, -9.5, 1.6), (6.5, -9.0, 1.8), (-10.5, -13, 1.9), (10.0, -14, 2.0), (3.0, -15, 1.7), (-4.0, -16, 1.8)]:
        draws.append((SC["tree"], trans(x, ground_h(x, z) - 0.05, z) @ roty(x) @ scale(s), U(mat=0, bump=0.7), True))
    draws.append((SC["cottage"], trans(COTTAGE_FAR[0], ground_h(*COTTAGE_FAR) - 0.05, COTTAGE_FAR[1]) @ roty(-0.4), U(mat=0, bump=0.6), False))
    draws.append((E2["stump"], trans(STUMP[0], ground_h(*STUMP) - 0.02, STUMP[1]) @ roty(0.7), U(mat=0, bump=0.9, obj="stump"), True))
    ms = mush_squash_now
    draws.append((E2["mushroom"], trans(MUSH[0], ground_h(*MUSH) - 0.01, MUSH[1]) @ scale(MUSH_S * (1 + 0.35 * (1 - ms)), MUSH_S * ms, MUSH_S * (1 + 0.35 * (1 - ms))),
                  U(mat=0, bump=0.6, obj="mushroom"), True))
    for (x, z, s) in [(MUSH[0] + 0.35, MUSH[1] - 0.25, 0.18), (MUSH[0] - 0.3, MUSH[1] - 0.35, 0.14), (STUMP[0] + 0.8, STUMP[1] + 0.5, 0.2)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))
    for (x, y, z, sx, sy, sz, c) in [(-12, -1.5, -26, 10, 5.0, 4, (.62, .82, .66)), (11, -1.8, -28, 11, 6.0, 4, (.58, .78, .7)),
                                     (0, -2.8, -32, 15, 6.6, 5, (.66, .8, .78))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    shake = stomp_shake(t)
    for fi, (x, z, r, c, s) in enumerate(FLOWERS):
        wob = 0.06 * math.sin(t * 1.6 + fi) + 0.25 * shake * math.sin(fi)
        draws.append((SC["flower"], trans(x, ground_h(x, z) - 0.01, z) @ roty(r) @ rotz(wob) @ scale(s), U(mat=0, bump=0.0, tint=c, tintMix=-1.0), False))
    for k, (x, y, z) in enumerate([(-5.0, 11.0, -18), (5.5, 13.5, -22), (-1.0, 15.5, -26)]):
        draws.append((SC["cloud"], trans(x + 0.08 * t * (1 if k % 2 else -1), y + 0.15 * math.sin(t * 0.5 + k), z) @ scale(1.4), U(mat=0, bump=0.4), False))
    draws.append((SC["sun"], trans(5.5, 14.0, -24) @ rotz(t * 0.2) @ scale(1.3), U(mat=0, bump=0.4), False))
    # berry (Pip holds it in small0)
    st = tumble(t); mats = fox_mats(st); R, Mh, arms, legs = mats
    pp, pyaw, pfly, pflip, pperch, pex = pip_state(t, st, mats)
    Mp = trans(*pp) @ roty(pyaw) @ rotx(pflip) @ scale(1.1)
    BERRY_REST = (BERRY[0] + 0.12, BERRY[1] + 0.22)
    if pex.get("berry"):
        pv = PIPD["wing0"]["pivot"]
        bpos = apply(Mp @ trans(*pv) @ rotz(0.9) @ trans(*(-np.array(pv))), (0.36, 0.25, 0.04))
    else: bpos = np.array([BERRY_REST[0], surf(*BERRY_REST) + 0.037, BERRY_REST[1]])
    draws.append((E2["berry"], trans(*bpos) @ scale(0.075), U(mat=0, bump=0.4, obj="berry"), True))
    # basket
    if st["carry"] == "basket":
        Mb = R @ trans(0, 0.45, 1.05) @ roty(math.pi / 2) @ scale(1.15)
    else:
        a = SH["overhead"][0]
        u = clampu(t, a + 0.6, a + 0.9)
        if u < 1 and t >= a:
            p0 = apply(R, (0, 0.45, 1.05)); p1 = np.array([BASKET[0], surf(*BASKET), BASKET[1]])
            p = lerp(p0, p1, ease(u))
            Mb = trans(*p) @ roty(math.pi / 2) @ scale(1.15)
        else:
            Mb = trans(BASKET[0], surf(*BASKET), BASKET[1]) @ roty(math.pi / 2) @ scale(1.15)
    draws.append((E2["basket"], Mb, U(mat=0, bump=0.7, obj="basket"), True))
    # apple
    a_st = apple_state(t)
    if a_st is not None:
        if isinstance(a_st[0], str):
            Ma = R @ trans(0, 0.66, 0.43 + APPLE_R) @ rotx(0.85) @ scale(0.85)        # hugged in front of the belly
        else:
            ap, roll = a_st
            Ma = trans(*ap) @ rotz(roll) @ rotx(math.pi / 2) @ scale(0.85)
        draws.append((E2["apple"], Ma, U(mat=0, bump=0.5, obj="apple"), True))
    # ---- Tumble ----
    contacts = []
    u0 = U(mat=0, bump=1.0, seed=2.0, obj="fox")
    draws.append((FOXP["body"], R, u0, True))
    for li in range(2): draws.append((FOXP[f"leg{li}"], legs[li], u0, True))
    for ai in range(2): draws.append((FOXP[f"arm{ai}"], arms[ai], u0, True))
    draws.append((FOXP["head"], Mh, u0, True))
    tp = FOXD["tail"]["pivot"]
    draws.append((FOXP["tail"], R @ trans(*tp) @ roty(st["tail"] * 0.5) @ trans(*(-np.array(tp))), u0, True))
    eyes(draws, Mh, FOXD["eyes"]["centers"], FOXD["eyes"]["r"], blink(t), U)
    mo = MOUTH["tumble"][min(int(t * FPS), len(MOUTH["tumble"]) - 1)]
    if mo > 0.06:
        draws.append((PR["mouth"], Mh @ trans(*FOXD["mouth"]["c"]) @ scale(0.075, 0.065 * mo, 0.03), U(mat=0, bump=0.0), False))
    contacts.append((st["x"], st["z"], 0.75, max(0.0, 1 - st["y"] * 1.5)))
    if st["carry"] == "bigleaf":
        draws.append((E2["bigleaf"], leaf_M(arms, st), U(mat=0, bump=0.5, obj="leaf"), True))
    # ---- Pip ----
    up = U(mat=0, bump=0.6, seed=7.0, obj="pip")
    sq = 0.0
    if "tinystomp" in pex: sq = -0.4 * math.sin(math.pi * pex["tinystomp"])
    Mp = trans(*pp) @ roty(pyaw) @ rotx(pflip) @ scale(1.1 * (1 - sq * 0.5), 1.1 * (1 + sq), 1.1 * (1 - sq * 0.5))
    draws.append((PIPP["body"], Mp, dict(up, perch=pperch), True))
    flap = (0.9 * math.sin(t * 28)) if (pfly or pex.get("run")) else 0.04 + 0.04 * math.sin(t * 3)
    if pex.get("berry"): flap = None                 # wing0 raised holding the berry
    if pex.get("tinyleaf") or pex.get("point"): flap = None
    for wi in range(2):
        pv = PIPD[f"wing{wi}"]["pivot"]; sgn = 1 if wi == 0 else -1
        fl = ((0.6 + 0.5 * math.sin(t * 9)) if pex.get("tinyleaf") else (1.3 + 0.1 * math.sin(t * 6) if pex.get("point") else 0.9)) if wi == 0 else 0.1
        fl = fl if flap is None else flap
        Mw = Mp @ trans(*pv) @ rotz(sgn * fl) @ trans(*(-np.array(pv)))
        draws.append((PIPP[f"wing{wi}"], Mw, up, True))

    if pex.get("tinyleaf"):                       # tiny leaf held up in his wing and fanned
        pv = PIPD["wing0"]["pivot"]; fan = 0.5 * math.sin(t * 9)
        Mw0 = Mp @ trans(*pv) @ rotz(0.6 + fan) @ trans(*(-np.array(pv)))
        draws.append((E2["bigleaf"], Mw0 @ trans(0.25, 0.16, 0.03) @ rotz(0.9) @ rotx(math.pi / 2 - 0.25) @ scale(0.11) @ trans(1.28, 0, 0),
                      U(mat=0, bump=0.3, obj="tinyleaf"), False))
    eyes(draws, Mp, PIPD["eyes"]["centers"], PIPD["eyes"]["r"], blink(t, 1.3, 2.7), U)
    mp_ = MOUTH["pip"][min(int(t * FPS), len(MOUTH["pip"]) - 1)]
    if mp_ > 0.08:
        draws.append((PR["mouth"], Mp @ trans(0, 0.295, 0.19) @ scale(0.028, 0.022 * mp_, 0.02), U(mat=0, bump=0.0), False))
    if pex.get("run") or pfly: pass
    else: contacts.append((pp[0], pp[2], 0.2, 1.0))
    # dust / pollen puffs on stomps and the big landing
    for s_ in T.STOMPS + [T.BIG_HOP + 0.95]:
        d = t - s_
        if 0 <= d < 0.5:
            for k in range(8):
                a = k * 2 * math.pi / 8
                r = 0.4 + 1.4 * d
                x, z = st["x"] + r * math.cos(a), st["z"] + 0.7 * r * math.sin(a)
                sz = 0.07 * (1 - d / 0.5) ** 1.5
                draws.append((PR["ball"], trans(x, surf(x, z) + 0.05 + d * 0.5, z) @ scale(sz), U(mat=0, bump=0.0, tint=(0.98, 0.95, 0.82), tintMix=1.0), False))
    return draws, contacts

def draw_pass(draws, contacts, eye, tgt, fov, vp):
    x, y, w, h = vp
    VPm = perspective(fov, w / h, 0.15, 90.0) @ look_at(eye, tgt)
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
    if T.shot_at(t)[1] == "split":
        for which, vp in (("top", (0, H // 2, W, H // 2)), ("bottom", (0, 0, W, H // 2))):
            eye, tgt, fov = camera(t, which)
            msaa_fbo.clear(0, 0, 0, 1, depth=1.0, viewport=vp)
            draw_pass(draws, contacts, eye, tgt, fov, vp)
    else:
        eye, tgt, fov = camera(t)
        draw_pass(draws, contacts, eye, tgt, fov, (0, 0, W, H))
    ctx.viewport = (0, 0, W, H)
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
TF6 = wght(620); TF7 = wght(700)
EFONT = skia.Font(TF6, 44)
grain = np.random.default_rng(1).integers(0, 255, (H, W), dtype=np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
vig = (1 - 0.2 * np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.25, 0, 1)).astype(np.float32)
PLUMC = (74, 43, 69)
BIGC, SMALLC = (240, 90, 50), (20, 150, 150)
def word_style(w):
    k = re.sub(r"[^a-z]", "", w.lower())
    if k == "big": return 1.55, BIGC
    if k in ("tiny", "small"): return 0.68, SMALLC
    return 1.0, None
import re

def current_line(t):
    for li, ws in enumerate(LINE_LIST):
        start = ws[0]["t0"] - 0.1
        start = max(start, next((a for (a, b, n) in T.SHOTS if a <= ws[0]["t0"] < b), start))
        nxt = LINE_LIST[li + 1][0]["t0"] - 0.25 if li + 1 < len(LINE_LIST) else 1e9
        end = min(ws[-1]["t1"] + 0.5, nxt)
        sh_end = next((b for (a, b, n) in T.SHOTS if a <= ws[-1]["t1"] < b), end)
        end = min(end, sh_end)
        if start <= t < end: return ws, start, end
    return None, 0, 0

def outlined(cv, text, x, y, font, rgb, a, sw=16):
    st = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=sw, Color=skia.Color(*PLUMC, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
    fp = skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(255 * a)))
    cv.drawString(text, x, y, font, st); cv.drawString(text, x, y, font, fp)

def overlay(img, t):
    surf_ = skia.Surface(img); cv = surf_.getCanvas()
    if T.shot_at(t)[1] == "split":                               # divider and labels
        a = clamp01((t - SH["split"][0]) / 0.3) * clamp01((SH["split"][1] - t) / 0.2)
        cv.drawRect(skia.Rect.MakeXYWH(0, H / 2 - 9, W, 18), skia.Paint(Color=skia.Color(255, 250, 240)))
        cv.drawRect(skia.Rect.MakeXYWH(0, H / 2 - 9, W, 3), skia.Paint(Color=skia.Color(*PLUMC)))
        cv.drawRect(skia.Rect.MakeXYWH(0, H / 2 + 6, W, 3), skia.Paint(Color=skia.Color(*PLUMC)))
        outlined(cv, "BIG", 50, 290, skia.Font(TF7, 270), BIGC, a, 28)
        outlined(cv, "small", 60, H / 2 + 110, skia.Font(TF7, 84), SMALLC, a, 14)
    if t < 3.9:                                                   # title card: BIG letters big, small letters small
        a = clamp01(t / 0.4) * clamp01((3.9 - t) / 0.4)
        f1 = skia.Font(TF7, 132); x = (W - f1.measureText(T.TITLE)) / 2; y0 = 420 - 8 * math.sin(t * 3)
        cols = [(255, 160, 100), (250, 190, 60), (110, 175, 235), (246, 120, 170), (160, 130, 230)]
        for k, ch in enumerate(T.TITLE):
            outlined(cv, ch, x, y0 + 7 * math.sin(t * 5 + k * 0.6), f1, cols[k % 5], a, 22); x += f1.measureText(ch)
        fb, fs = skia.Font(TF7, 150), skia.Font(TF7, 64)
        parts = [("BIG", fb, BIGC), (" and ", skia.Font(TF7, 80), (255, 255, 255)), ("small!", fs, SMALLC)]
        tw = sum(f.measureText(s) for s, f, c in parts); x = (W - tw) / 2
        for s, f, c in parts:
            outlined(cv, s, x, 600, f, c, a, 18 if f is fb else 12); x += f.measureText(s)
        ep = T.EPISODE; ew = EFONT.measureText(ep)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - ew) / 2 - 26, 650, ew + 52, 64), 32, 32), skia.Paint(AntiAlias=True, Color=skia.Color(255, 140, 120, int(235 * a))))
        cv.drawString(ep, (W - ew) / 2, 696, EFONT, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(255 * a))))
    ws, start, end = current_line(t)
    if ws:
        a = clamp01((t - start) / 0.15) * clamp01((end - t) / 0.15)
        base = 72
        items = []
        for w_ in ws:
            sc_, col = word_style(w_["w"]); f = skia.Font(TF7, base * sc_)
            items.append((w_, f, f.measureText(w_["w"]), col))
        space = skia.Font(TF7, base).measureText(" ")
        rows, cur, wsum = [], [], 0
        for it in items:
            if cur and wsum + space + it[2] > 900: rows.append(cur); cur, wsum = [], 0
            wsum += (space if cur else 0) + it[2]; cur.append(it)
        if cur: rows.append(cur)
        y = 1690 - 60 * (len(rows) - 1)
        if T.shot_at(t)[1] == "split": y = 1800 - 120 * (len(rows) - 1)
        maxw = max(sum(i[2] for i in r) + space * (len(r) - 1) for r in rows)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - maxw) / 2 - 40, y - 100, maxw + 80, 120 * len(rows) + 30), 50, 50),
                     skia.Paint(AntiAlias=True, Color=skia.Color(255, 250, 240, int(210 * a))))
        for row in rows:
            tw = sum(i[2] for i in row) + space * (len(row) - 1); x = (W - tw) / 2
            for (w_, f, wl, col) in row:
                on = w_["t0"] - 0.03 <= t < max(w_["t1"], w_["t0"] + 0.25)
                c = col or ((240, 110, 60) if on else PLUMC)
                if col and not on: c = tuple(int(v * 0.8) for v in col)
                p = skia.Paint(AntiAlias=True, Color=skia.Color(*c, int(255 * a)))
                ps = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.5, Color=skia.Color(*c, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
                yb = y - (6 if on else 0)
                cv.drawString(w_["w"], x, yb, f, ps); cv.drawString(w_["w"], x, yb, f, p)
                x += wl + space
            y += 120
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
    ignore = {("fox:fox/parts/arm0/mesh", "leaf:ep2/bigleaf"), ("leaf:ep2/bigleaf", "fox:fox/parts/arm0/mesh")}   # paw grips the leaf stem
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
        for e in qa_geom.check_frame(t, items, bank, ground=ground_h, masks=QA_MASKS, ground_objs=("fox", "pip"), float_tol=0.02):
            if (e["a"], e.get("b", "")) in ignore: continue
            issues.append(e)
    summ = qa_geom.summarize(issues, fps)
    json.dump(summ, open(out, "w"), indent=1, default=float)
    for s_ in summ: print(s_)
    print("issues:", len(summ))
    return summ

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "qa":
        qa(); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "x":
        for s in sys.argv[2:]:
            t0 = time.time(); fr = overlay(render_frame(float(s)), float(s))
            skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/still_{float(s):05.2f}.png")
            print(s, round(time.time() - t0, 2), "s", flush=True)
        sys.exit()
    nfr = int(T.DURATION * FPS)
    if len(sys.argv) > 1 and sys.argv[1] == "seg":
        f0, f1, outp, audio = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], []
    else:
        outp = sys.argv[1] if len(sys.argv) > 1 else "out/tumble_pip_ep2.mp4"
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
    print(f"done: {min(f1, nfr) - f0} frames in {time.time() - t0:.0f}s -> {outp}", flush=True)
