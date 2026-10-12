"""Tumble & Pip Fables 9: Stronger Together!  (Aesop: The Bundle of Sticks)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa"""
from fablekit import *

# ---------------- world: the stream bank (a new corner of Picnic Meadow) ----------------
# A bundle of 7 twigs lies like a bench across the old stump and a round rock, with the stream behind.
BZ = -3.6                                                  # the bench line (along x)
STUMP = (-1.95, BZ); STUMP_TOP = 0.55 - 0.02
ROCK = (-0.05, BZ)
SUP_Y = max(surf(*STUMP) + STUMP_TOP, surf(*ROCK) + 0.53)  # top of both supports
ROCK_H = SUP_Y - surf(*ROCK)                               # stone mesh half-height 0.07, scaled up to stump height
ROCK_S = (2.0, ROCK_H / 0.07, 1.7)
BL = 2.6                                                   # bundle length
BR = 0.15                                                  # bundle radius (7 sticks of radius 0.05)
B0 = np.array([-2.3, SUP_Y + BR + 0.004, BZ]); B1 = B0 + np.array([BL, 0, 0])
SA, SB = (STUMP[0] + 0.62 - B0[0]) / BL, (ROCK[0] - 0.42 - B0[0]) / BL   # inner edges of the supports: the bundle bends between them
SPOT = (-3.1, -1.9)                                       # Tumble's hook spot, in front of the bench
PULLP = (-1.0, -4.05)                                      # behind the bench (stream side), facing the camera
LANDP = (0.5, -1.95)                                       # where he lands on his bottom after the boing
BRX = 2.6                                                  # the bridge line (along z) across the stream
BZ0, BZ1 = -4.2, -6.8
MSPOT = (BRX - 1.0, -7.45)                                 # far bank: moral, chorus, button
HALVES = [(-3.5, -1.25, 0.3), (-2.65, -1.2, -0.25)]       # where the two twig halves land (x, z, yaw)
PIP_S = 0.86                                               # Pip's perch along the bench bundle (by the rock)
FLOWERS = make_flowers([(STUMP[0], STUMP[1], 1.2), (ROCK[0], ROCK[1], 1.0), ("box", -2.6, 0.6, -4.7, -1.0),
                        ("box", -3.6, 1.2, -2.6, -0.9), ("box", -0.5, 3.5, -3.2, 2.0), (LANDP[0], LANDP[1], 1.3), ("box", BRX - 0.8, BRX + 0.8, -4.6, -3.0),
                        ("box", BRX - 2.2, BRX + 0.8, -8.3, -6.4), ("box", 0.3, 2.0, -3.4, -2.2)], seed=91)

# ---------------- the bundle ----------------
STICK_OFF = [(0.0, 0.0)] + [(0.1 * math.cos(math.radians(90 + 60 * k)), 0.1 * math.sin(math.radians(90 + 60 * k))) for k in range(6)]
_rng = np.random.default_rng(9)
STICK_END = [(_rng.uniform(0.0, 0.03), _rng.uniform(0.97, 1.0)) for _ in STICK_OFF]
STICK_TINT = [(0.62 + 0.08 * _rng.uniform(), 0.42 + 0.06 * _rng.uniform(), 0.26 + 0.04 * _rng.uniform()) for _ in STICK_OFF]
TIES = (0.3, 0.7)
def bend_y(s, A, sa, sb):
    """sag of the bundle axis at s (A > 0 bows down between the supports; the overhanging ends flick up)"""
    u = (s - sa) / (sb - sa)
    if u < 0: return max(0.0, -A * math.pi * u)          # ends lift off the supports, never sink into them
    if u > 1: return max(0.0, A * math.pi * (u - 1))
    return -A * math.sin(math.pi * u)
def spring(t, t0, amp, f=6.0, k=4.0):
    d = t - t0
    return amp * math.cos(2 * math.pi * f * d / 2) * math.exp(-k * d) if d >= 0 else 0.0

def bridge_ends():
    p0 = np.array([BRX, surf(BRX, BZ0) + BR + 0.004, BZ0]); p1 = np.array([BRX, surf(BRX, BZ1) + BR + 0.004, BZ1])
    return p0, p1
BR0, BR1 = bridge_ends()

def bundle_state(t):
    """(P0, P1, A, sa, sb): the bundle axis from P0 to P1, bent by A between supports sa and sb"""
    n = T.shot_at(t)[1]
    if t < T.TW_SPLIT:
        A = 0.0
        if n == "pull_push":
            up = ease(clampu(t, T.PULL - 0.15, T.PULL + 0.3)) * (1 - ease(clampu(t, T.PULL + 0.45, T.PULL + 0.6)))
            dn = ease(clampu(t, T.PUSH - 0.1, T.PUSH + 0.3)) * (1 - ease(clampu(t, T.PUSH + 0.55, T.PUSH + 0.7)))
            A = -0.11 * up + 0.11 * dn
            A += spring(t, T.PULL + 0.6, -0.05) + spring(t, T.PUSH + 0.7, 0.05)
        elif n == "sit_boing" or (n == "land" and t < T.LAUNCH + 2.0):
            if T.SAT <= t < T.STRAIN:                       # bounces as he sits and sings
                A = 0.035 + spring(t, T.SAT, 0.04)
            elif T.STRAIN <= t < T.LAUNCH:                   # sits down HARD: it bows...
                A = 0.035 + 0.2 * ease(clampu(t, T.STRAIN, T.LAUNCH - 0.1))
            elif t >= T.LAUNCH:                             # ...and springs back: BOING
                A = spring(t, T.LAUNCH, 0.235, f=5.0, k=3.0)
        elif n in ("land", "pip_idea"):
            A = spring(t, T.LAUNCH, 0.235, f=5.0, k=3.0)
        return B0, B1, A, SA, SB
    if t < T.TIP:                                           # stood up on its end at the bank
        th = 0.0
    else:
        u = clampu(t, T.TIP, T.THUMP); th = u * u          # tips over, faster and faster
    if th < 1.0:
        d_flat = (BR1 - BR0) / np.linalg.norm(BR1 - BR0)
        w = d_flat - np.array([0, d_flat[1], 0]); w /= np.linalg.norm(w)
        phi = math.acos(float(np.clip(d_flat[1], -1, 1))) * th
        d = np.array([0, math.cos(phi), 0]) + w * math.sin(phi)
        base = np.array([BRX, surf(BRX, BZ0) + 0.05 + (BR + 0.004 - 0.05) * math.sin(phi), BZ0 - 0.0])
        if th == 0.0: base[2] = BZ0 + 0.0
        return base, base + d * np.linalg.norm(BR1 - BR0), 0.0, 0.04, 0.96
    A = spring(t, T.THUMP, 0.05, f=6.0, k=5.0)
    if n == "button_crane":                                # Pip's springy landing on the middle
        for k, tb in enumerate(BOINGS):
            A += spring(t, tb, 0.05 * (0.7 ** k), f=6.0, k=6.0) if t >= tb else 0.0
    return BR0, BR1, A, 0.04, 0.96

def _frame(P0, P1):
    ax = (P1 - P0) / np.linalg.norm(P1 - P0)
    e1 = np.cross(ax, np.array([0, 1.0, 0]))
    if np.linalg.norm(e1) < 1e-3: e1 = np.array([1.0, 0, 0])
    e1 /= np.linalg.norm(e1); e2 = np.cross(e1, ax)
    if e2[1] < 0: e1, e2 = -e1, -e2
    return ax, e1, e2
def axis_pt(st, s):
    P0, P1, A, sa, sb = st
    return P0 + (P1 - P0) * s + np.array([0, bend_y(s, A, sa, sb), 0])
def top_at(st, s):
    """highest point of the bundle's top stick at s"""
    _, e1, e2 = _frame(st[0], st[1])
    return axis_pt(st, s) + e2 * (BR + 0.0)
def s_of_x(x): return (x - B0[0]) / BL
def s_of_z(z): return (z - BR0[2]) / (BR1[2] - BR0[2])

def draw_bundle(draws, t):
    st = bundle_state(t); P0, P1 = st[0], st[1]
    ax, e1, e2 = _frame(P0, P1)
    for j, (ox, oy) in enumerate(STICK_OFF):
        s0, s1 = STICK_END[j]; ss = np.linspace(s0, s1, 9)
        pts = [axis_pt(st, s) + e1 * ox + e2 * oy for s in ss]
        for a_, b_ in zip(pts[:-1], pts[1:]):
            M = seg_M(a_, b_, 0.05)
            if M is not None: draws.append((PR["stick"], M, U(mat=0, bump=0.7, tint=STICK_TINT[j], tintMix=0.85, obj="bundle"), True))
    for k, s in enumerate(TIES):                            # grass ties: rings of little green balls
        c = axis_pt(st, s)
        for i in range(12):
            a_ = i * 2 * math.pi / 12
            q = c + (e1 * math.cos(a_) + e2 * math.sin(a_)) * (BR + 0.012)
            draws.append((PR["ball"], trans(*q) @ scale(0.032), U(mat=0, bump=0.0, tint=(0.42, 0.68, 0.3), tintMix=1.0), False))
        if k == 0:                                         # a little grass bow on the first tie
            q = c + e2 * (BR + 0.04)
            R = np.eye(4); R[:3, 0], R[:3, 1], R[:3, 2] = ax, e2, -e1
            for sgn in (1, -1):
                draws.append((SC["leaf"], trans(*q) @ R @ roty(0.5 * sgn) @ trans(0.11 * sgn, 0, 0) @ rotz(0.35 * sgn) @ scale(1.3), U(mat=0, bump=0.0, tint=(0.5, 0.74, 0.32), tintMix=1.0), False))
    return st

# ---------------- the single twig (hook) ----------------
TWIG_R = 0.032
def twig_draws(draws, t, arms):
    """held in both paws, snapped on the sung 'Snap!', dropped into the grass where the halves stay"""
    tint = U(mat=0, bump=0.6, tint=(0.66, 0.46, 0.28), tintMix=0.85, obj="twig")
    hl, hr = hand_pos(arms, 1), hand_pos(arms, 0)
    drop0, drop1 = T.SNAP + 0.55, T.SNAP + 0.95
    if t < T.SNAP:
        mid = (hl + hr) / 2 + np.array([0, 0.1 + TWIG_R + 0.004, 0.0])
        bow = 0.06 * ease(clampu(t, T.SNAP - 0.45, T.SNAP))
        dirv = (hr - hl) / np.linalg.norm(hr - hl)
        a_, b_ = mid - dirv * 0.55, mid + dirv * 0.55
        m_ = mid + np.array([0, bow, 0])
        for p, q in ((a_, m_), (m_, b_)):
            draws.append((PR["stick"], seg_M(p, q, TWIG_R), tint, True))
        return
    for i, (h, sgn) in enumerate(((hl, -1), (hr, 1))):
        if t < drop0:                                       # one half in each paw, broken ends up
            base = h + np.array([0, 0.1 + TWIG_R + 0.004, 0])
            tip = base + np.array([-sgn * 0.12, 0.42, 0.1])
            p, q = base + (base - tip) * 0.08, tip
        else:
            x, z, yw = HALVES[i]
            gp = np.array([x, surf(x, z) + TWIG_R + 0.004, z]); d = np.array([math.cos(yw), 0, math.sin(yw)]) * 0.25
            if t < drop1:
                u = clampu(t, drop0, drop1)
                base0 = h + np.array([0, 0.1 + TWIG_R + 0.004, 0])
                c = lerp(base0 + np.array([-sgn * 0.06, 0.21, 0.05]), gp, u * u)
                ang = lerp(0.0, 1.0, u)
                dd = lerp(np.array([-sgn * 0.12, 0.42, 0.1]) * 0.55, d, ang)
                p, q = c - dd, c + dd
            else:
                p, q = gp - d, gp + d
        draws.append((PR["stick"], seg_M(p, q, TWIG_R), tint, True))

# ---------------- Tumble ----------------
def hand_table():
    """hand position (relative to the root, facing +z) for the two-paw grip [0.3, fwd, 0.62]"""
    out = {}
    for fwd in np.linspace(0.0, 2.6, 53):
        st = tumble_base(0.0); st["arms"] = [[0.3, fwd, 0.62], [0.3, fwd, 0.62]]; st["sq"] = 0.0
        out[round(float(fwd), 3)] = hand_pos(fox_mats(st)[2]) - np.array([0, surf(0, 0), 0])
    return out
HT = hand_table()
def fwd_for_height(y):
    ks = sorted(HT); ys = [HT[k][1] for k in ks]
    i = int(np.argmax(ys)); return float(np.interp(y, ys[:i + 1], ks[:i + 1]))

def sit_pose(st, seat_y):
    """sitting: body bottom on seat_y (world), legs stuck out in front"""
    st["sit"] = True
    st["y"] = seat_y - surf(st["x"], st["z"]) - st.get("stand_h", 0.0) - FOX_SEAT + 0.006
def fox_mats_x(st):
    """fox_mats plus the sitting legs and a pitch about the middle of the body (the flight)"""
    R, Mh, arms, legs = fox_mats(st)
    if st.get("sit"):
        legs = [R @ trans(0, 0.15, st.get("sit_fwd", 0.3)) for _ in range(2)]
    p = st.get("pitch", 0.0)
    if p == 0.0: return R, Mh, arms, legs
    root = trans(st["x"], surf(st["x"], st["z"]) + st.get("stand_h", 0.0) - 0.01 + st["y"], st["z"]) @ roty(st["yaw"])
    P = root @ trans(0, 0.8, 0) @ rotx(p) @ trans(0, -0.8, 0) @ np.linalg.inv(root)
    return P @ R, P @ Mh, [P @ a for a in arms], [P @ l for l in legs]

def seat_y_bench(t):
    """his body's underside (an ellipsoid, half-width 0.42, half-height 0.5) resting on the bent bundle"""
    st = bundle_state(t); best = -9.0
    for dx in np.linspace(-0.4, 0.4, 17):
        prof = 0.5 * (1 - math.sqrt(max(0.0, 1 - (dx / 0.42) ** 2)))
        best = max(best, float(top_at(st, s_of_x(-1.0 + dx))[1]) - prof)
    return best + 0.006
def flight(t):
    """launch from the bench seat to LANDP: (x, z, seat_y_world)"""
    y0 = seat_y_bench(T.LAUNCH); y1 = surf(*LANDP) + 0.0
    u = clampu(t, T.LAUNCH, T.LANDED)
    x, z = lerp((-1.0, BZ), LANDP, u)
    y = lerp(y0, y1, u) + 3.4 * 4 * u * (1 - u) * (1 - 0.15 * u)
    return x, z, y

def strain(t):
    """0..1 how red his face is"""
    r = 0.0
    for a_, b_ in ((T.PULL - 0.15, T.PULL + 0.55), (T.PUSH - 0.1, T.PUSH + 0.65), (T.STRAIN - 0.05, T.LAUNCH)):
        r = max(r, ease(clampu(t, a_, a_ + 0.25)) * (1 - ease(clampu(t, b_, b_ + 0.4))))
    return r

def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    st["x"], st["z"] = SPOT; st["yaw"] = 0.0
    if n == "hook_snap":                                    # the twig in both paws at chest height
        st["arms"] = [[0.3, 1.25, 0.62], [0.3, 1.25, 0.62]]
        d = t - T.SNAP
        if -0.45 < d < 0:                                   # effort...
            st["sq"] -= 0.04 * ease(clampu(t, T.SNAP - 0.45, T.SNAP)); st["head"][0] = 0.12
        if 0 <= d < 0.55:                                   # SNAP: paws fly apart
            v = ease(clampu(d, 0, 0.12)); st["arms"] = [[0.3 + 0.3 * v, 1.25, 0.62 * (1 - v)] for _ in range(2)]
            st["sq"] += 0.06 * math.exp(-d * 8) * math.cos(d * 25); st["head"][0] = -0.08
        if d >= 0.55:                                       # drops the halves, then a proud "so easy"
            u = ease(clampu(t, T.SNAP + 0.55, T.SNAP + 0.95))
            st["arms"] = [lerp([0.6, 1.25, 0.0], [0.35, 0.3, 0.0], u).tolist() for _ in range(2)]
            st["head"][0] = -0.12 * u; st["head"][2] = 0.12 * u
    elif n == "title_wide":                                 # waves
        a = SH[n][0]
        st["arms"][0] = [2.2 + 0.25 * math.sin((t - a) * 9), 0.3]; st["head"][2] = 0.1
    elif n == "pip_ask":                                    # turns to listen to Pip on the bundle
        a = SH[n][0]; u = ease(clampu(t, a, a + 0.6))
        st["yaw"] = 0.55 * u; st["head"][1] = 0.35 * u; st["head"][0] = 0.1 * u
        L = T.line("Setup A")
        if t > L["t1"]: st["head"][0] = 0.1 + 0.12 * math.sin((t - L["t1"]) * 9) * math.exp(-(t - L["t1"]) * 2)   # nods
    elif n == "watch_me":                                   # rubs his paws, then leaps over the bundle and lands behind it
        L = T.line("Setup B"); a = SH[n][0]
        w0 = (T.word_times("watch", "Setup B") or [a + 2.0])[0]
        j0, j1 = w0 + 0.25, w0 + 1.15
        if t < j0:
            ph = t * 14
            st["arms"] = [[0.3, 1.2 + 0.12 * math.sin(ph), 0.6], [0.3, 1.2 - 0.12 * math.sin(ph), 0.6]]
            st["head"][2] = 0.08 * math.sin(t * 4)
            crouch = ease(clampu(t, j0 - 0.35, j0)); st["sq"] -= 0.1 * crouch
        elif t < j1:                                        # a show-off spin over the bundle
            u = clampu(t, j0, j1)
            st["x"], st["z"] = lerp(SPOT, PULLP, ease(u))
            st["y"] += 1.25 * math.sin(math.pi * u); st["yaw"] = 2 * math.pi * ease(u)
            st["arms"] = [[1.9, 0.3], [1.9, 0.3]]; st["legs"] = [0.12, 0.12]
        else:                                               # ta-da!
            d = t - j1
            st["x"], st["z"] = PULLP
            st["sq"] -= 0.12 * math.exp(-d * 7) * math.cos(d * 22)
            v = ease(clampu(d, 1.2, 1.6)); st["arms"] = [lerp([2.3, 0.2], [0.3, 0.5], v).tolist() for _ in range(2)]
    elif n == "pull_push":                                  # grips the middle from behind and pulls, then pushes
        st["x"], st["z"] = PULLP
        bs = bundle_state(t)
        top = float(top_at(bs, s_of_x(-1.0))[1]) - surf(*PULLP)
        hy = top + 0.1 + 0.004
        f = fwd_for_height(hy)
        a = SH[n][0]; grip = ease(clampu(t, a, a + 0.5))
        st["arms"] = [lerp([0.3, 0.5, 0.0], [0.3, f, 0.62], grip).tolist(), lerp([0.3, 0.5, 0.0], [0.3, f, 0.62], grip).tolist()]
        r = strain(t)
        st["sq"] += 0.05 * r * (1 if t < T.PUSH - 0.1 else -1); st["head"][0] = 0.1 * r
        st["y"] += 0.03 * r * abs(math.sin(t * 40))
        L = T.line("Problem A")
        if t > L["t1"] + 0.2:                               # lets go and scratches his head
            v = ease(clampu(t, L["t1"] + 0.2, L["t1"] + 0.6))
            st["arms"][0] = lerp([0.3, f, 0.62], [0.5, 2.6, 0.0], v).tolist(); st["head"][2] = -0.15 * v
    elif n in ("sit_boing", "land", "pip_idea"):
        if t < T.SAT:                                       # hops up onto the bundle and turns to sit
            a = SH["sit_boing"][0]; u = clampu(t, a + 0.15, T.SAT)
            st["x"], st["z"] = lerp(PULLP, (-1.0, BZ), ease(clampu(u, 0.35, 0.85)))   # up first, then over, then down
            if u > 0:                                       # a tucked hop: legs forward like sitting
                sit_pose(st, lerp(surf(*PULLP) + FOX_SEAT + 0.01, seat_y_bench(t), ease(u)) + 0.95 * math.sin(math.pi * u))
                st["sit_fwd"] = 0.3 * ease(clampu(u, 0.7, 1.0))   # legs tucked under until he is over the bundle
            st["arms"] = [[1.4, 0.4], [1.4, 0.4]]
        elif t < T.LAUNCH:                                  # sitting on the bundle, bouncing with it
            st["x"], st["z"] = (-1.0, BZ)
            sit_pose(st, seat_y_bench(t))
            st["arms"] = [[0.5, 0.6], [0.5, 0.6]]
            if t >= T.STRAIN:                               # HARD: arms up, squash down
                r = ease(clampu(t, T.STRAIN, T.STRAIN + 0.3))
                st["arms"] = [lerp([0.5, 0.6], [1.0, 2.4], r).tolist()] * 2; st["sq"] += 0.06 * r; st["eyes_closed"] = True
        elif t < T.LANDED:                                  # BOING: thrown up into the air
            x, z, y = flight(t); st["x"], st["z"] = x, z
            sit_pose(st, y)
            st["arms"] = [[2.3 + 0.3 * math.sin(t * 22), 0.3], [2.3 - 0.3 * math.sin(t * 22), 0.3]]
            st["roll"] = 0.3 * math.sin(clampu(t, T.LAUNCH, T.LANDED) * 2 * math.pi)
            st["sq"] -= 0.06 * math.exp(-(t - T.LAUNCH) * 5)
        else:                                               # bump! sitting in the grass, dizzy
            d = t - T.LANDED
            st["x"], st["z"] = LANDP; sit_pose(st, surf(*LANDP))
            st["sq"] = -0.14 * math.exp(-d * 6) * math.cos(d * 18)
            st["arms"] = [[0.6, 0.2], [0.6, 0.2]]
            dz = math.exp(-d * 0.9)
            st["head"][2] = 0.2 * dz * math.sin(d * 6); st["head"][0] = 0.12 * dz * math.cos(d * 6)
            st["yaw"] = -0.35
            if n == "pip_idea":                             # listens, nods, then jumps up, ready
                L = T.line("Twist")
                st["head"][1] = -0.3 * ease(clampu(t, SH[n][0], SH[n][0] + 0.5))
                if t > L["t1"] - 0.3:
                    st["head"][0] = 0.15 * math.sin((t - L["t1"]) * 10) * math.exp(-max(0, t - L["t1"]) * 1.5)
    elif n == "bridge":                                     # tips the bundle over the stream, walks across
        tb0 = (BRX + 0.5, -3.53)
        st["x"], st["z"] = tb0; st["yaw"] = math.pi
        if t < T.TIP + 0.25:                                # a paw on the upright bundle, push!
            st["arms"][0] = [0.15, 1.5]; st["arms"][1] = [0.4, 0.5]
            st["sq"] += 0.03 * ease(clampu(t, T.TIP - 0.2, T.TIP))
        elif t < T.CROSS0:
            v = ease(clampu(t, T.TIP + 0.25, T.TIP + 0.6))
            st["arms"] = [lerp([0.15, 1.5], [2.0, 0.3], v).tolist(), lerp([0.4, 0.5], [2.0, 0.3], v).tolist()]
            st["head"][0] = -0.1
        else:                                               # onto the bridge and across, arms out for balance
            path = [tb0, (BRX, -3.85), (BRX, -7.15), (BRX - 0.2, -7.4)]
            c0, c1 = T.CROSS0, T.CROSS1
            ts = [c0, c0 + 0.35, c1 - 0.3, c1]
            for k in range(3):
                if t < ts[k + 1] or k == 2:
                    walk_to(st, t, path[k], path[k + 1], ts[k], ts[k + 1], rate=2.6); break
            st["arms"] = [[1.5, 0.15 + 0.1 * math.sin(t * 5)], [1.5, 0.15 - 0.1 * math.sin(t * 5)]]
            st["roll"] = 0.06 * math.sin(t * 5)
            st["stand_h"] = bridge_stand(st["x"], st["z"], t)
    elif n in ("moral", "chorus"):
        st["x"], st["z"] = MSPOT
        dance_tumble(st, t, n)
    else:                                                   # button: waves goodbye
        a = SH["button_crane"][0]; st["x"], st["z"] = MSPOT; st["yaw"] = -0.05
        down = ease(clampu(t, a + 0.45, a + 0.85))
        st["arms"] = [lerp(DANCE_ARM, [0.3, 0.3], down).tolist(), [2.2 + 0.25 * math.sin((t - a) * 9) * down, 0.3]]
        st["head"][1] = 0.3 * down; st["head"][2] = 0.1 * (1 - down)
    return st

def bridge_stand(x, z, t):
    """height of the bridge top under him (0 off the bridge), ramped over the ends so he steps up and down"""
    bs = bundle_state(t)
    s = s_of_z(z)
    top = float(top_at(bs, min(max(s, 0.0), 1.0))[1]) - surf(x, z) + 0.004
    on = clampu(-z, 3.83, 4.05) * clampu(z, -7.38, -7.12)
    return max(0.0, top) * ease(on)

# ---------------- Pip ----------------
def bench_perch(t, s=PIP_S):
    return top_at(bundle_state(t), s) + UP
BOINGS = []
def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    R, Mh, arms, legs = mats
    face = apply(Mh, (0, 1.5, 0.6))
    p = bench_perch(t)
    to_t = math.atan2(face[0] - p[0], face[2] - p[2])
    if n in ("hook_snap", "title_wide"):
        return p, to_t, False, 0.0, True, {"cheer": n == "title_wide"}
    if n == "pip_ask":                                      # points along the bundle, "the whole big bundle"
        L = T.line("Setup A")
        ex = {"point": True} if L["t0"] + 1.0 < t < L["t1"] + 0.4 else {}
        hop = 0.0
        for w in T.word_times("big", "Setup A") + T.word_times("bundle", "Setup A"):
            d = t - w
            if 0 <= d < 0.3: hop = 0.12 * math.sin(math.pi * d / 0.3)
        q = p + np.array([0, hop, 0])
        return q, to_t, hop > 0, 0.0, hop == 0, ex
    if n in ("watch_me", "pull_push"):
        yaw = to_t
        ex = {"cheer": True} if n == "watch_me" and t > SH[n][0] + 3.0 else {}
        return p, yaw, False, 0.0, True, ex
    if n == "sit_boing":
        d = t - T.LAUNCH                                    # the boing bumps Pip up too
        if 0 <= d < 0.45:
            return p + np.array([0, 0.35 * math.sin(math.pi * d / 0.45), 0]), to_t, True, 0.0, False, {"gentle": True}
        return p, to_t, False, 0.0, True, {}
    if n == "land":
        return p, to_t, False, 0.0, True, {"cheer": t > T.LANDED + 0.2}
    if n == "pip_idea":                                     # pats the bundle: one stick snaps, lots stay strong
        L = T.line("Twist")
        pat = 0.0
        for w in T.word_times("lots", "Twist") + T.word_times("strong", "Twist"):
            d = t - w
            if 0 <= d < 0.3: pat = math.sin(math.pi * d / 0.3)
        ex = {"wings": (-0.5 * pat + 0.05, 0.05)} if pat > 0 else ({"point": True} if t < L["t1"] else {"cheer": True})
        return p, to_t, False, 0.0, True, ex
    if n == "bridge":                                       # flies across ahead of him, in straight legs
        legs_ = [np.array([BRX - 0.7, 1.95, -3.7]), np.array([BRX - 0.7, 2.9, -4.4]), np.array([BRX + 0.4, 2.9, -6.9]), PIP_ARRIVE]
        ts = [T.TW_SPLIT, T.THUMP, T.THUMP + 0.4, T.THUMP + 1.7, T.THUMP + 2.2]
        bob = np.array([0, 0.05 * math.sin(t * 6), 0])
        if t < ts[1]: return legs_[0] + bob, math.pi, True, 0.0, False, {"gentle": True}
        for k in range(3):
            if t < ts[k + 2] or k == 2:
                u = clampu(t, ts[k + 1], ts[k + 2]); q = lerp(legs_[k], legs_[k + 1], ease(u))
                return q + bob, math.pi if k < 2 else 0.4, True, 0.0, False, {"gentle": True}
    if n in ("moral", "chorus"):
        return dance_pip(t, st, mats, n, arrive_from=PIP_ARRIVE)
    a, b = SH["button_crane"]                               # hops from the paw onto the middle of the bridge: boing, boing
    land_s = 0.5
    bs = bundle_state(t)
    dest = top_at(bs, land_s) + UP
    p0 = paw_seat(fox_mats_x(tumble(a))[2])
    u = clampu(t, a + 0.1, a + 0.8)
    if u < 1:
        q = lerp(p0, dest, ease(u)); q[1] += 0.8 * math.sin(math.pi * u)
        return q, math.atan2(dest[0] - p0[0], dest[2] - p0[2]), True, 0.0, False, ({"wings": (0.15, 0.15)} if u < 0.5 else {"gentle": True})
    hop = 0.0
    for k, tb in enumerate(BOINGS):
        d = t - tb; hh = 0.3 * (0.6 ** k)
        if 0 <= d < 0.4: hop = hh * math.sin(math.pi * d / 0.4)
    yaw = math.atan2(face[0] - dest[0], face[2] - dest[2]) * 0 + 0.3
    return dest + np.array([0, hop, 0]), yaw, hop > 0, 0.0, hop == 0, {"cheer": True}
PIP_ARRIVE = np.array([MSPOT[0] + 2.3, 1.8, MSPOT[1] - 0.15])
_ba = SH["button_crane"][0]
BOINGS[:] = [_ba + 0.8, _ba + 1.2, _ba + 1.55]

# ---------------- camera ----------------
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    st = tumble(t)
    if name == "hook_snap":                                 # medium front, slow push-in on the twig
        return fit_cam(np.array([SPOT[0] + 1.2, lerp(1.15, 1.2, e), SPOT[1] - 0.8]), lerp(4, 0, e), 7, lerp(2.2, 1.95, e), lerp(1.55, 1.4, e))
    if name == "title_wide":                                # high wide: bench, stream, far bank
        return fit_cam(np.array([-1.5, 1.2, -3.6]), 10, 16, 3.3, 2.6 if not WIDE else 2.5, lift=0.05)
    if name == "pip_ask":                                   # low macro along the bundle on Pip
        pp = bench_perch(t)
        return fit_cam(pp + np.array([-0.05, 0.25, 0]), lerp(58, 50, e), 4, 0.55, 0.62, fov=34)
    if name == "watch_me":                                  # medium three-quarter, wide enough for the leap
        return fit_cam(np.array([-1.95, 1.35, -3.0]), -18, 7, 2.35, 2.05)
    if name == "pull_push":                                 # medium front, the bundle in the foreground
        return fit_cam(np.array([-0.85, 1.15, -3.9]), lerp(10, 4, e), 8, 1.45, 1.35)
    if name == "sit_boing":                                 # side-on low angle, tilting up with the launch
        up = ease(clampu(t, T.LAUNCH, SH[name][1]))
        return fit_cam(np.array([-0.65, lerp(1.35 if not WIDE else 1.6, 2.6, up), BZ + 0.2]), 16, lerp(-4, -12, up), 1.75, 1.55 if not WIDE else 1.95)
    if name == "land":                                      # medium, high: he drops in and bumps down
        return fit_cam(np.array([LANDP[0] + 0.1, 1.05, LANDP[1]]), -14, 18, 1.4, 1.45)
    if name == "pip_idea":                                  # two-shot: Pip on the bundle, Tumble in the grass
        pp = bench_perch(t)
        c = lerp(pp, np.array([LANDP[0], 1.0, LANDP[1]]), 0.55)
        return fit_cam(c + np.array([0, 0.1, 0]), lerp(-40, -34, e), 8, 1.75, 1.35)
    if name == "bridge":                                    # high-angle wide, side-on to the stream
        return fit_cam(np.array([BRX - 0.1, 1.1, lerp(-4.9, -5.8, e)]), 92, 20, 2.7, 1.8)
    if name == "moral":
        return fit_cam(np.array([MSPOT[0] + 0.25, lerp(1.35, 1.45, e), MSPOT[1]]), lerp(14, 8, e), 5, lerp(1.3, 1.1, e), lerp(1.4, 1.15, e))
    if name == "chorus":
        return fit_cam(np.array([MSPOT[0] + 0.3, 1.2, MSPOT[1]]), 10, 6, 1.35, 1.35)
    return fit_cam(np.array([MSPOT[0] + 0.6, lerp(0.95, 1.5, e), MSPOT[1] + 0.9]), 14, lerp(8, 24, e), lerp(1.7, 2.4, e), lerp(1.5, 2.2, e), lift=0.0 if not WIDE else 0.1)

# ---------------- draws ----------------
STONES = [(-2.8, -4.45, 0.9, 1.0), (-0.9, -4.6, 1.4, 0.7), (1.0, -4.5, 1.1, 1.0), (3.4, -4.45, 1.0, 1.0),
          (0.2, -6.6, 1.2, 1.0), (3.6, -6.55, 1.1, 1.0), (-2.2, -6.6, 1.3, 1.0)]
TREES = [(-7.5, -9.5, 1.6), (6.5, -9.0, 1.8), (-10.5, -13, 1.9), (10.0, -14, 2.0), (3.0, -15, 1.7), (-4.0, -16, 1.8)]
def build_draws(t):
    draws, contacts = [], []
    meadow_backdrop(draws, t, trees=TREES)
    draws.append((E2["stump"], trans(STUMP[0], ground_h(*STUMP) - 0.02, STUMP[1]) @ roty(0.3), U(mat=0, bump=0.9, obj="stump"), True))
    draws.append((SC["stone"], trans(ROCK[0], surf(*ROCK), ROCK[1]) @ roty(0.4) @ scale(*ROCK_S), U(mat=0, bump=0.8, tint=(0.72, 0.72, 0.76), tintMix=0.5, obj="rock"), True))
    for (x, z, r, s) in STONES:                             # pebbles along both banks
        draws.append((SC["stone"], trans(x, surf(x, z) + 0.01, z) @ roty(x * 2) @ scale(s * 1.2, 1.4, s), U(mat=0, bump=0.6), True))
    for (x, z, s) in [(STUMP[0] - 0.8, STUMP[1] + 0.55, 0.2), (ROCK[0] + 0.85, ROCK[1] - 0.4, 0.16), (MSPOT[0] - 1.3, MSPOT[1] - 0.3, 0.22), (BRX + 1.1, -7.6, 0.17)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))
    draw_flowers(draws, t, FLOWERS)
    draw_bundle(draws, t)
    n = T.shot_at(t)[1]
    st = tumble(t); mats = fox_mats_x(st); R, Mh, arms, legs = mats
    k0 = len(draws)
    draw_tumble(draws, contacts, t, st, mats)
    r = strain(t)
    if r > 0:                                               # red in the face from trying so hard
        for k in range(k0, len(draws)):
            m, M, u, c = draws[k]
            if m is FOXP["head"]: draws[k] = (m, M, dict(u, tint=lerp((1, 1, 1), (1.0, 0.62, 0.55), r).tolist(), tintMix=-1.0), c)
    twig_draws(draws, t, arms)
    if T.SNAP <= t < T.SNAP + 0.5:
        puff(draws, (hand_pos(arms, 0) + hand_pos(arms, 1)) / 2 + np.array([0, 0.15, 0.1]), T.SNAP, t, n=9, size=0.04, spread=0.8, dur=0.4, tint=(0.8, 0.62, 0.42))
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, arms)
    if n == "bridge":                                       # thump on the far bank
        puff(draws, BR1 + np.array([0, 0.05, -0.1]), T.THUMP, t, n=10, size=0.07, spread=0.9, dur=0.5, tint=(0.85, 0.8, 0.65), axis=(0, 0.6, 0))
    if n in ("sit_boing",):
        puff(draws, np.array([-1.0, SUP_Y + 0.3, BZ + 0.2]), T.LAUNCH, t, n=10, size=0.06, spread=1.0, dur=0.45, tint=(1.0, 0.92, 0.6))
    if n == "land":
        puff(draws, np.array([LANDP[0], surf(*LANDP) + 0.15, LANDP[1] + 0.2]), T.LANDED, t, n=10, size=0.07, spread=1.1, dur=0.5, tint=(0.9, 0.95, 0.75), axis=(0, 0.4, 0.3))
    return draws, contacts

def _ground_objs(t):
    return ("pip",) if T.shot_at(t)[1] in ("sit_boing", "land", "pip_idea") else ("fox", "pip")
HOOKS.update(build=build_draws, camera=camera, tumble=tumble, ground_objs=_ground_objs,
             qa_ignore={("twig", "fox"), ("fox", "twig")})   # the twig is held in his paws in the hook
if __name__ == "__main__":
    main()
