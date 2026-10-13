"""Tumble & Pip Fables 8: Pip Who Cried Help  (Aesop: The Boy Who Cried Wolf, softened: no wolf, no danger)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | seg f0 f1 out.mp4 | sheet | qa"""
from fablekit import *

# ---------------- world: the picnic corner of the meadow (giant flower, puddle, blanket and basket) ----------------
FLOWER = (-2.0, -1.2); FLOWER_S = 6.0; FLOWER_TINT = (1.0, 0.62, 0.78)
FLOWER_TOP = surf(*FLOWER) - 0.01 + 0.252 * FLOWER_S                    # top of the flower's middle
PIP_FLOWER = np.array([FLOWER[0], FLOWER_TOP + 0.012, FLOWER[1]]) + UP
PIP_PETAL = np.array([FLOWER[0] + 0.1, surf(*FLOWER) - 0.01 + 1.335, FLOWER[1] - 0.45]) + UP   # crouched behind the middle, on the petals
PUDDLE = (-0.3, -0.9); PUDDLE_S = 1.05                                  # x half-width 1.0, z half-depth 0.69
BASKET = (2.6, -1.9); BS = 1.8
BLANKET = (BASKET[0] - 0.7, BASKET[1] - 0.1); BLANKET_S = 1.2
BLANKET_TOP = 0.04 * BLANKET_S
BASE_Y = surf(*BASKET) + 0.03 + BLANKET_TOP + 0.02 * BS                 # basket origin (its floor sits on the blanket)
RIM = BASE_Y + 0.44 * BS                                                 # top of the basket wall
FLOOR = BASE_Y + 0.09 * BS                                               # inside floor
LX, LY, LZ = 0.98, 0.07, 0.80                                            # lid half-sizes (a flattened clay ball)
HINGE = np.array([BASKET[0], RIM + 0.06, BASKET[1] - LZ])               # hinged on the basket's back edge
LID_OPEN = 1.72                                                          # standing open, leaning back a little past upright
LID_TINT = (0.80, 0.58, 0.36)
PIP_IN = np.array([BASKET[0] - 0.25, FLOOR - 0.035, BASKET[1] + 0.15]) + UP      # Pip inside, on the basket floor
RIM_FRONT = np.array([BASKET[0] - 0.35, RIM, BASKET[1] + 0.385 * BS * 0.98]) + UP   # front rim, left of centre
T_HOME = (BASKET[0] - 0.6, BASKET[1] + 1.75)                             # Tumble by the picnic, off the blanket
TRIPPT = (PUDDLE[0] + 1.15, PUDDLE[1] + 0.15)                             # foot catches the puddle's edge
FLOPPT = (PUDDLE[0] + 0.75, PUDDLE[1] + 0.05)                            # where his feet end up as he belly-flops
LEAP_A = (PUDDLE[0] + 1.2, PUDDLE[1] + 0.45); LEAP_B = (PUDDLE[0] - 1.3, PUDDLE[1] + 1.0)
SPINPT = (FLOWER[0] - 1.35, FLOWER[1] + 1.85)                            # skids past the flower's front, spins here
LIFTPT = (BASKET[0] + 1.5, BASKET[1] + 0.3)                              # at the basket's right end
MSPOT = (BASKET[0] - 1.5, BASKET[1] + 1.9)                               # moral, dance and button
BERRIES = [(BLANKET[0] - 0.7, BLANKET[1] + 0.3), (BLANKET[0] - 0.55, BLANKET[1] + 0.45), (BLANKET[0] - 0.85, BLANKET[1] + 0.5)]
FLOWERS = make_flowers([(FLOWER[0], FLOWER[1], 1.2), (PUDDLE[0], PUDDLE[1], 1.3), ("box", PUDDLE[0] - 1.6, PUDDLE[0] + 1.6, PUDDLE[1] - 0.6, PUDDLE[1] + 1.4),
                        ("box", BLANKET[0] - 1.6, BASKET[0] + 1.6, BLANKET[1] - 1.3, MSPOT[1] + 0.7), (SPINPT[0], SPINPT[1], 1.4),
                        ("box", FLOWER[0] - 2.2, BASKET[0] + 1.5, FLOWER[1] + 0.2, FLOWER[1] + 2.2)], seed=81)

# ---------------- the lid ----------------
def lid_angle(t):
    """0 = shut, LID_OPEN = standing open"""
    if t < T.P_IN: return LID_OPEN
    if t < T.LID_FLOP:                                                   # Pip's hop jolts it: a wobble ...
        d = t - T.P_IN; return LID_OPEN - 0.12 * math.sin(d * 16) * math.exp(-d * 2) - 0.2 * clampu(t, T.P_IN, T.LID_FLOP) ** 2
    if t < T.LID_SHUT:                                                   # ... then it tips forward and flops shut
        u = clampu(t, T.LID_FLOP, T.LID_SHUT); return (LID_OPEN - 0.2) * (1 - u * u)
    if t < T.LIFT:
        d = t - T.LID_SHUT; a = 0.12 * abs(math.sin(d * 11)) * math.exp(-d * 6)       # little bounce
        if SH["muffled"][0] <= t < SH["is_it_a_joke"][1]:                 # Pip pushing from inside
            a += 0.035 * max(0.0, math.sin(t * 13)) * clampu(t, SH["muffled"][0], SH["muffled"][0] + 0.3)
        return a
    if t < T.LOWER: return 0.5 * ease(clampu(t, T.LIFT, T.LIFT + 0.4))   # Tumble lifts the lid
    return 0.5 * (1 - ease(clampu(t, T.LOWER, T.LOWER + 0.5)))          # and lowers it gently once Pip is out
def basket_rock(t):
    if SH["muffled"][0] <= t < T.LIFT: return 0.03 * math.sin(t * 13) * clampu(t, SH["muffled"][0], SH["muffled"][0] + 0.3)
    return 0.0
def basket_M(t):
    r = basket_rock(t)
    px = BASKET[0] + (0.95 if r > 0 else -0.95)                          # rocks on its bottom edge, never into the blanket
    return trans(px, BASE_Y, BASKET[1]) @ rotz(r) @ trans(BASKET[0] - px, 0, 0) @ scale(BS)
def rock_M(t):
    r = basket_rock(t); px = BASKET[0] + (0.95 if r > 0 else -0.95)
    return trans(px, BASE_Y, BASKET[1]) @ rotz(r) @ trans(-px, -BASE_Y, -BASKET[1])
def pip_in(t): return apply(rock_M(t), PIP_IN)
def lid_M(t):
    r = basket_rock(t); px = BASKET[0] + (0.95 if r > 0 else -0.95)
    Rk = trans(px, BASE_Y, BASKET[1]) @ rotz(r) @ trans(-px, -BASE_Y, -BASKET[1])
    return Rk @ trans(*HINGE) @ rotx(-lid_angle(t)) @ trans(0, 0, LZ)
def lid_front(t):
    return apply(lid_M(t), (0.0, 0.0, LZ))

# ---------------- Tumble ----------------
def solve_arm(st, i, target, side=(-0.2, 2.0), fwd=(-0.3, 3.0), n=36):
    """arm angles that put paw i nearest target (grid search on the real rig)"""
    best, arg = 9.0, None
    for s_ in np.linspace(*side, n):
        for f_ in np.linspace(*fwd, n):
            st["arms"][i] = [s_, f_]; d = np.linalg.norm(hand_pos(fox_mats(st)[2], i) - target)
            if d < best: best, arg = d, [s_, f_]
    st["arms"][i] = arg
    return best
def yaw_to(a, b): return math.atan2(b[0] - a[0], b[1] - a[1])
RUN_YAW = yaw_to(T_HOME, TRIPPT)
LIFT_YAW = -math.pi / 2
_arm_cache = {}
def lift_arms(st, t):
    """both paws under the lid's front edge (cached per frame time)"""
    k = round(t, 3)
    if k not in _arm_cache:
        F = lid_M(t); s2 = dict(st, arms=[list(a) for a in st["arms"]])
        tg0 = apply(F, (0.68, -0.05, 0.5)); tg1 = apply(F, (0.95, -0.05, -0.05))   # front-right corner, right end
        solve_arm(s2, 0, tg0, n=24); solve_arm(s2, 1, tg1, side=(-0.2, 1.2), n=24)
        _arm_cache[k] = [list(a) for a in s2["arms"]]
    st["arms"] = [list(a) for a in _arm_cache[k]]
HUG_ARMS = [[0.25, 1.0], [0.35, 0.95]]
def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    st["x"], st["z"] = T_HOME; st["yaw"] = RUN_YAW
    L = T.line("Setup A")
    if n in ("hook_flower", "title_wide"):
        st["yaw"] = -0.5; st["arms"] = [[0.3, 0.3], [0.3, 0.6]]
        if n == "hook_flower" and t > T.line("Hook")["t0"] + 0.4: st["yaw"] = RUN_YAW * 0.6; st["head"][0] = -0.05
    elif n in ("rush", "splash"):
        run0 = L["t0"] + 0.9
        if t < run0:                                                    # turns to the call, waves
            st["arms"][0] = [1.2 + 0.2 * math.sin(t * 12), 0.6]
        elif t < T.TRIP:
            walk_to(st, t, T_HOME, TRIPPT, run0, T.TRIP, rate=3.2); st["arms"] = [[0.3, 0.9 + 0.5 * math.sin(t * 20)], [0.3, 0.9 - 0.5 * math.sin(t * 20)]]
            st["yaw"] = RUN_YAW; st["head"][0] = -0.1
        else:                                                           # trips and belly-flops into the puddle
            u = clampu(t, T.TRIP, T.FLOP)
            st["x"], st["z"] = lerp(TRIPPT, FLOPPT, ease(u)); st["yaw"] = RUN_YAW
            st["pitch"] = 1.45 * ease(u) ** 1.5; st["y"] += 0.35 * math.sin(math.pi * u) - 0.45 * ease(u) ** 2
            st["arms"] = [[1.4, 2.4 * u], [1.4, 2.4 * u]]; st["legs"] = [0.1, 0.0]
            if t >= T.FLOP:
                d = t - T.FLOP
                st["pitch"] = 1.45; st["y"] = -0.45; st["sq"] = -0.1 * math.exp(-d * 6) * math.cos(d * 20)
                st["arms"] = [[1.4, 2.4], [1.4, 2.4]]; st["tail"] = 0.6 * math.sin(d * 8)
    elif n == "giggle":                                                  # lies in the puddle, then pushes himself up
        a = SH[n][0]; up = ease(clampu(t, a + 1.0, a + 2.0))
        st["x"], st["z"] = FLOPPT; st["yaw"] = RUN_YAW
        st["pitch"] = 1.45 * (1 - up); st["y"] = -0.45 * (1 - up)
        st["arms"] = lerp([[1.4, 2.4], [1.4, 2.4]], [[0.3, 0.2], [0.3, 0.2]], up).tolist()
        st["head"][0] = -0.2 * (1 - up)
    elif n == "drip":                                                    # shakes off, then walks back to the picnic
        a = SH[n][0]
        st["x"], st["z"] = FLOPPT; st["yaw"] = yaw_to(FLOPPT, PIP_FLOWER[[0, 2]]) * 0.0 + RUN_YAW + 0.4
        if t < a + 0.9:
            d = t - a; st["roll"] = 0.12 * math.sin(d * 26) * math.sin(math.pi * d / 0.9); st["arms"] = [[0.5, 0.2], [0.5, 0.2]]
        else:
            walk_to(st, t, FLOPPT, T_HOME, a + 0.9, a + 2.35, rate=2.0); st["head"][0] = 0.15
            if t >= a + 2.35: st["yaw"] = RUN_YAW
    elif n == "rush2":
        a = SH[n][0]
        if t < T.RUN2:
            st["yaw"] = RUN_YAW; st["head"][0] = 0.05
        elif t < T.LEAP2:
            walk_to(st, t, T_HOME, LEAP_A, T.RUN2, T.LEAP2, rate=3.4)
            st["arms"] = [[0.3, 0.9 + 0.5 * math.sin(t * 20)], [0.3, 0.9 - 0.5 * math.sin(t * 20)]]
        elif t < T.LEAP2 + 0.7:                                         # leaps the puddle this time
            u = clampu(t, T.LEAP2, T.LEAP2 + 0.7)
            st["x"], st["z"] = lerp(LEAP_A, LEAP_B, u); st["y"] += 0.6 * math.sin(math.pi * u)
            st["yaw"] = yaw_to(LEAP_A, LEAP_B); st["arms"] = [[1.2, 0.8], [1.2, 0.8]]; st["legs"] = [0.12, 0.05]
        elif t < T.SPIN:                                                # skids on past the flower
            u = clampu(t, T.LEAP2 + 0.7, T.SPIN)
            st["x"], st["z"] = lerp(LEAP_B, SPINPT, 1 - (1 - u) ** 2); st["yaw"] = yaw_to(LEAP_B, SPINPT)
            st["arms"] = [[0.9, 0.3], [0.9, 0.3]]; st["head"][0] = -0.1; st["legs"] = [0.06, 0.0]
            st["roll"] = -0.08 * math.sin(math.pi * u)
        else:                                                           # spins like a top, slowing down
            d = t - T.SPIN
            st["x"], st["z"] = SPINPT
            spin = 4.0 * math.pi * (1 - math.exp(-d * 1.8)) / (1 - math.exp(-1.8 * 2.0))
            st["yaw"] = yaw_to(LEAP_B, SPINPT) + min(spin, 4.0 * math.pi)
            st["arms"] = [[1.5, 0.2], [1.5, 0.2]]; st["legs"] = [0.08 * abs(math.sin(d * 9)), 0.0]
    elif n == "not_again":                                               # dizzy, faces Pip
        a = SH[n][0]
        st["x"], st["z"] = SPINPT; st["yaw"] = yaw_to(SPINPT, PIP_FLOWER[[0, 2]]) * 0.7
        dz = math.exp(-(t - a) * 0.7)
        st["head"][2] = 0.18 * math.sin(t * 6) * dz; st["roll"] = 0.06 * math.sin(t * 6 + 1) * dz
        L2 = T.line("Problem B")
        if L2["t0"] < t < L2["t1"] + 0.3:                               # paws out: "Oh, Pip!"
            st["arms"] = [[0.6, 0.9], [0.6, 0.9]]
        if t > L2["t1"] + 0.3: st["head"][0] = 0.12; st["arms"] = [[0.2, 0.1], [0.2, 0.1]]
    elif n == "basket":                                                  # stays by the flower, sitting the dizziness out
        st["x"], st["z"] = SPINPT; st["yaw"] = yaw_to(SPINPT, PIP_FLOWER[[0, 2]]) * 0.7; st["head"][0] = 0.12
    elif n == "muffled":
        st["x"], st["z"] = SPINPT; st["yaw"] = 0.3; st["head"][0] = 0.05
    elif n == "is_it_a_joke":                                            # turns, paw to chin, decides, runs off
        a = SH[n][0]
        st["x"], st["z"] = SPINPT
        turn = ease(clampu(t, a, a + 0.4)); st["yaw"] = lerp(0.3, 0.9, turn)
        if t < T.TW_SPLIT2 - 0.55:
            st["arms"][1] = [0.25, 2.1]; st["head"][2] = 0.12 * ease(clampu(t, T.JOKE, T.JOKE + 0.4))
        else:
            u = clampu(t, T.TW_SPLIT2 - 0.55, T.TW_SPLIT2)
            walk_to(st, t, SPINPT, (SPINPT[0] + 1.3, SPINPT[1] + 0.2), T.TW_SPLIT2 - 0.55, T.TW_SPLIT2 + 0.1, rate=3.4)
            st["arms"] = [[0.3, 0.9 + 0.5 * math.sin(t * 20)], [0.3, 0.9 - 0.5 * math.sin(t * 20)]]
    elif n == "rescue":
        a = SH[n][0]
        if t < T.LIFT - 0.1:                                            # runs in to the basket corner
            p0 = (LIFTPT[0] + 0.7, LIFTPT[1] + 1.1)
            walk_to(st, t, p0, LIFTPT, a, T.LIFT - 0.2, rate=3.4); st["yaw"] = lerp(yaw_to(p0, LIFTPT), LIFT_YAW, clampu(t, T.LIFT - 0.5, T.LIFT - 0.2))
            if t >= T.LIFT - 0.2: st["yaw"] = LIFT_YAW
        else:
            st["x"], st["z"] = LIFTPT; st["yaw"] = LIFT_YAW
        if T.LIFT - 0.1 <= t < T.LOWER + 0.5:
            lift_arms(st, t); st["head"][0] = -0.1
        if t >= T.CUDDLE - 0.35:                                        # the hug: paws to his chest for Pip
            u = ease(clampu(t, T.CUDDLE - 0.35, T.CUDDLE))
            st["yaw"] = lerp(LIFT_YAW, 0.2, u); st["x"] += 0.3 * u                 # steps back from the basket as he turns
            st["arms"] = lerp(st["arms"], HUG_ARMS, u).tolist(); st["head"][0] = 0.05 * u
            if t > T.CUDDLE + 0.2: st["roll"] = 0.05 * math.sin((t - T.CUDDLE) * 5)
    elif n in ("moral", "chorus"):
        st["x"], st["z"] = MSPOT
        dance_tumble(st, t, n)
    else:                                                               # button: waves bye-bye
        a = SH["button_crane"][0]; st["x"], st["z"] = MSPOT; st["yaw"] = -0.05
        down = ease(clampu(t, a + 0.3, a + 0.7))
        st["arms"][0] = lerp(DANCE_ARM, [1.6 + 0.25 * math.sin(t * 12), 1.2], down).tolist()
        st["head"][2] = 0.1 * (1 - down)
    return st

def fox_mats_p(st):
    """fox_mats plus a forward pitch about the middle of the body (the belly-flop)"""
    R, Mh, arms, legs = fox_mats(st)
    p = st.get("pitch", 0.0)
    if p == 0.0: return R, Mh, arms, legs
    root = trans(st["x"], surf(st["x"], st["z"]) + st.get("stand_h", 0.0) - 0.01 + st["y"], st["z"]) @ roty(st["yaw"])
    P = root @ trans(0, 0.8, 0) @ rotx(p) @ trans(0, -0.8, 0) @ np.linalg.inv(root)
    return P @ R, P @ Mh, [P @ a for a in arms], [P @ l for l in legs]

# ---------------- Pip ----------------
def hop(p0, p1, u, h):
    p = lerp(p0, p1, ease(u)); p[1] += h * math.sin(math.pi * u); return p
def legs3(pts, u):
    """explicit straight legs through pts (no corner cutting)"""
    k = len(pts) - 1; s = min(int(u * k), k - 1); v = u * k - s
    return lerp(pts[s], pts[s + 1], ease(v))
def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    R, Mh, arms, legs = mats
    face = apply(Mh, (0, 1.5, 0.6))
    def look(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])
    giggle = {"wings": (0.25 + 0.15 * math.sin(t * 22), 0.25 + 0.15 * math.sin(t * 22 + 0.5))}
    if n == "hook_flower":                                              # pops up in the flower, grins, flaps, calls
        if t < 0.25: return PIP_PETAL, 0.25, False, 0.0, True, {"cling": 1.0, "tuck": True}
        u = clampu(t, 0.25, 0.7)
        if u < 1: return hop(PIP_PETAL, PIP_FLOWER, u, 0.3), 0.25, True, 0.0, False, {"gentle": True}
        ex = {"cheer": True} if T.line("Hook")["t0"] < t < T.line("Hook")["t1"] + 0.2 else {}
        return PIP_FLOWER, 0.25, False, 0.0, True, ex
    if n in ("title_wide", "rush", "splash", "giggle", "drip", "rush2", "not_again"):
        ex = {}
        if n in ("giggle", "not_again"): ex = giggle
        if n == "not_again" and t > T.line("Problem B")["t1"] + 0.1: ex = {"droop": 0.6}
        tgt = np.array([st["x"], 1.0, st["z"]])
        yaw = look(PIP_FLOWER, tgt)
        if n == "rush2" and t > T.SPIN - 0.4: yaw = look(PIP_FLOWER, np.array([SPINPT[0], 0, SPINPT[1]]))
        if n == "giggle": yaw = math.radians(-75)                      # giggles to us, Tumble behind him
        if n == "giggle" and SH[n][0] + 0.2 < t < SH[n][0] + 1.6:        # giggle hop
            d = (t - SH[n][0] - 0.2) % 0.45; p = PIP_FLOWER + np.array([0, 0.08 * math.sin(math.pi * d / 0.45), 0])
            return p, yaw, False, 0.0, d < 0.03 or d > 0.42, giggle
        return PIP_FLOWER, yaw, False, 0.0, True, ex
    if n == "basket":                                                   # flies to the basket, peeks, hops in
        if t < T.P_FLY: return PIP_FLOWER, look(PIP_FLOWER, RIM_FRONT), False, 0.0, True, {}
        if t < T.P_RIM:
            u = clampu(t, T.P_FLY, T.P_RIM)
            pts = [PIP_FLOWER, PIP_FLOWER + np.array([0.3, 0.5, 0.2]), RIM_FRONT + np.array([0, 0.5, 0.3]), RIM_FRONT]
            p = legs3(pts, u)
            return p, look(PIP_FLOWER, RIM_FRONT), True, 0.0, False, {"gentle": True}
        if t < T.P_IN:                                                  # peeks over the rim at the berries
            d = t - T.P_RIM
            return RIM_FRONT, math.pi, False, 0.35 * math.sin(math.pi * min(d / 0.4, 1.0)), True, {}
        if t < T.P_IN + 0.35:
            u = clampu(t, T.P_IN, T.P_IN + 0.35)
            return hop(RIM_FRONT, PIP_IN, u, 0.25), math.pi, True, 0.0, False, {"wings": (0.5, 0.5)}
        return PIP_IN, 0.0, False, 0.0, True, {"cling": 1.0}
    if n in ("muffled", "is_it_a_joke"):
        return pip_in(t), 0.0, False, 0.0, True, {"cling": 1.0, "wings": (0.6 + 0.3 * math.sin(t * 13), 0.6 + 0.3 * math.sin(t * 13))}
    if n == "rescue":
        out1 = np.array([BASKET[0] - 0.35, RIM + 0.15, BASKET[1] + 0.95])   # just outside the front, left of Tumble
        if t < T.POP: return PIP_IN, 0.0, False, 0.0, True, {"cling": 1.0}
        if t < T.POP + 0.5:                                             # squeezes out under the lifted lid: a forward dive
            u = clampu(t, T.POP, T.POP + 0.5)
            x0 = PIP_IN[0] - 0.05
            p = legs3([PIP_IN, np.array([x0, RIM - 0.22, BASKET[1] + 0.2]), np.array([x0, RIM + 0.03, BASKET[1] + 0.62]),
                       np.array([x0, RIM + 0.05, BASKET[1] + 1.0]), out1], u)
            pitch = 1.15 * math.sin(math.pi * clampu(u, 0.1, 0.8))
            return p, 0.0, True, pitch, False, {"cling": 1.0 - u, "wings": (0.1, 0.1)}
        seat = paw_seat(arms)
        if t < T.CUDDLE - 0.3:                                          # hovers, a bit wobbly, says sorry
            hov = out1 + np.array([0, 0.25 + 0.05 * math.sin(t * 7), 0]) + np.array([0.04 * math.sin(t * 9), 0, 0])
            return hov, look(hov, face), True, 0.0, False, {"gentle": True} if t < T.SORRY else {"droop": 0.5, "wings": (0.9 + 0.3 * math.sin(t * 26), 0.9 + 0.3 * math.sin(t * 26))}
        hov = out1 + np.array([0, 0.25, 0])
        u = clampu(t, T.CUDDLE - 0.3, T.CUDDLE)
        if u < 1: return hop(hov, seat, u, 0.15), look(hov, face), True, 0.0, False, {"gentle": True}
        return seat, look(seat, face), False, 0.0, True, {"cheer": True}
    if n in ("moral", "chorus"):
        return dance_pip(t, st, mats, n)                                # already on his paw from the hug (across the cut)
    a, b = SH["button_crane"]                                           # hops over to sit on the closed lid
    top = apply(lid_M(t), (0.0, LY, 0.0)) + UP
    p0 = paw_seat(fox_mats_p(tumble(a))[2])
    u = clampu(t, a, a + 0.8)
    if u < 1:
        pts = [p0, p0 + np.array([0.35, 0.5, 0]), top + np.array([0, 0.6, 0]), top]
        return legs3(pts, u), 0.0, True, 0.0, False, ({"wings": (0.15, 0.15)} if u < 0.35 else {"gentle": True})
    return top, 0.0, False, 0.0, True, ({"cheer": True} if t > a + 0.9 else {})

# ---------------- camera ----------------
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    st = tumble(t)
    if name == "hook_flower":                                           # macro, low, push-in on Pip in the flower
        return fit_cam(PIP_FLOWER + np.array([0, -0.05, 0]), lerp(20, 12, e), lerp(22, 16, e), lerp(1.3, 0.95, e), lerp(1.2, 0.9, e), lift=0.12)
    if name == "title_wide":                                            # high wide over the picnic corner
        return fit_cam(np.array([0.3, lerp(1.2, 1.0, e), -0.9]), -4, lerp(30, 26, e), 3.4, 2.8 if not WIDE else 2.2, lift=0.02)
    if name == "rush":                                                  # tracking, front three-quarter
        p = np.array([st["x"], 1.15, st["z"]])
        return fit_cam(p + np.array([-0.3, 0, 0]), -62, 6, 1.6, 1.5)
    if name == "splash":                                                # ground level, side
        return fit_cam(np.array([FLOPPT[0] - 0.35, 0.6, FLOPPT[1]]), lerp(-62, -70, e), 5, 1.8, 1.2, lift=0.08)
    if name == "giggle":                                                # close on Pip, Tumble in the puddle behind
        return fit_cam(PIP_FLOWER + np.array([0.3, -0.05, 0]), -75, 6, 1.0, 0.95, lift=0.1)
    if name == "drip":
        return fit_cam(np.array([lerp(FLOPPT[0], T_HOME[0], 0.5), 1.1, lerp(FLOPPT[1], T_HOME[1], 0.5)]), 25, 8, 2.0, 1.6)
    if name == "rush2":                                                 # wide side, tracking the leap, the skid and the spin
        cx = lerp(T_HOME[0] - 0.8, SPINPT[0] + 0.9, ease(clampu(t, T.RUN2, T.SPIN + 0.3)))
        return fit_cam(np.array([cx, 1.15, -0.45]), 4, 7, 2.6, 1.7)
    if name == "not_again":                                             # two-shot, Tumble and Pip on the flower
        c = lerp(np.array([SPINPT[0], 1.25, SPINPT[1]]), PIP_FLOWER, 0.45)
        return fit_cam(c, side_on_yaw(np.array([SPINPT[0], 0, SPINPT[1]]), PIP_FLOWER, 100) + lerp(-4, 4, e), 4, 1.5, 1.3)
    if name == "basket":                                                # Pip arrives at the basket, the lid flops
        return fit_cam(np.array([BASKET[0] - 0.25, lerp(1.3, 1.15, clampu(t, T.P_IN, T.LID_SHUT)), BASKET[1] + 0.2]), lerp(-14, -8, e), 14, 1.6, 1.5)
    if name == "muffled":                                               # low angle on the wobbling basket
        return fit_cam(np.array([BASKET[0], 0.85, BASKET[1] + 0.2]), lerp(-24, -18, e), -8, 1.3, 1.05, lift=0.1)
    if name == "is_it_a_joke":
        return fit_cam(np.array([SPINPT[0] + 0.15, 1.45, SPINPT[1]]), 38, 4, 1.0, 1.15)
    if name == "rescue":                                                # side-on to Tumble and the basket front
        c = np.array([BASKET[0] + 0.55, 1.05, BASKET[1] + 0.6])
        return fit_cam(c, -24, 7, 1.9, 1.45)
    if name == "moral":
        return fit_cam(np.array([MSPOT[0] + 0.25, lerp(1.35, 1.45, e), MSPOT[1]]), lerp(-12, -6, e), 5, lerp(1.3, 1.1, e), lerp(1.4, 1.15, e))
    if name == "chorus":
        return fit_cam(np.array([MSPOT[0] + 0.25, 1.2, MSPOT[1]]), -6, 6, 1.35, 1.35)
    c = lerp(np.array([MSPOT[0] + 0.3, 1.2, MSPOT[1] - 0.3]), np.array([BASKET[0] - 0.2, 1.1, BASKET[1] + 0.9]), 0.5)
    return fit_cam(c, -10, lerp(6, 22, e), lerp(1.6, 2.4, e), lerp(1.5, 2.2, e), lift=0.04)

# ---------------- draws ----------------
WATER = (0.62, 0.82, 0.98)
def build_draws(t):
    draws, contacts = [], []
    meadow_backdrop(draws, t, cottage=(6.0, -12.0))
    draw_flowers(draws, t, FLOWERS)
    n = T.shot_at(t)[1]
    # the giant flower (Pip's hiding place); sways a touch when Tumble skids past
    sway = 0.04 * math.sin(t * 1.3) + 0.08 * math.exp(-max(0.0, t - T.SPIN + 0.6) * 2.5) * math.sin(t * 9) * (t > T.SPIN - 0.6)
    draws.append((SC["flower"], trans(FLOWER[0], surf(*FLOWER) - 0.01, FLOWER[1]) @ roty(0.4) @ rotz(sway) @ scale(FLOWER_S),
                  U(mat=0, bump=0.0, tint=FLOWER_TINT, tintMix=-1.0, obj="flower"), True))
    # puddle, blanket, berries, basket and lid
    draws.append((SC["puddle"], trans(PUDDLE[0], surf(*PUDDLE) + 0.005, PUDDLE[1]) @ scale(PUDDLE_S, 1.0, PUDDLE_S), U(mat=0, bump=0.0), False))
    draws.append((E2["blanket"], trans(BLANKET[0], surf(*BLANKET) + 0.03, BLANKET[1]) @ scale(BLANKET_S, 1.0, BLANKET_S), U(mat=0, bump=0.3), False))
    for (x, z) in BERRIES:
        draws.append((E2["berry"], trans(x, surf(*BLANKET) + 0.03 + BLANKET_TOP + 0.07, z) @ scale(0.12), U(mat=0, bump=0.4), True))
    draws.append((E2["basket"], basket_M(t), U(mat=0, bump=0.9, obj="basket"), True))
    LM = lid_M(t)
    draws.append((PR["ball"], LM @ scale(LX, LY, LZ), U(mat=0, bump=0.9, tint=LID_TINT, tintMix=1.0, obj="lid"), True))
    for hx in (-0.45, 0.45):                                            # two leather hinge straps over the back rim
        a_ = apply(LM, (hx, 0.0, -LZ + 0.08)); b_ = np.array([BASKET[0] + hx, RIM - 0.12, BASKET[1] - 0.42 * BS + 0.02])
        Ms = seg_M(a_, b_, 0.035)
        if Ms is not None: draws.append((PR["stick"], Ms, U(mat=0, bump=0.3, tint=(0.55, 0.36, 0.22), tintMix=1.0), False))
    draws.append((PR["ball"], LM @ trans(0, 0.07, LZ - 0.12) @ scale(0.09, 0.05, 0.07), U(mat=0, bump=0.4, tint=(0.62, 0.4, 0.25), tintMix=1.0), True))
    for k in range(3):                                                   # berries in the basket (seen when it is open)
        draws.append((E2["berry"], trans(BASKET[0] + 0.25 + 0.15 * k, FLOOR + 0.07, BASKET[1] - 0.25 + 0.1 * (k % 2)) @ scale(0.12), U(mat=0, bump=0.4), False))
    st = tumble(t); mats = fox_mats_p(st); R, Mh, arms, legs = mats
    draw_tumble(draws, contacts, t, st, mats)
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, arms)
    # splash, drips, dust
    puff(draws, np.array([FLOPPT[0] - 0.6, 0.15, FLOPPT[1]]), T.FLOP - 0.05, t, n=14, size=0.08, spread=1.4, dur=0.55, tint=WATER, axis=(0, 0.9, 0.3))
    if n == "drip" and t < SH["drip"][0] + 1.0:
        puff(draws, np.array([FLOPPT[0], 1.0, FLOPPT[1]]), SH["drip"][0] + 0.05, t, n=12, size=0.045, spread=1.3, dur=0.8, tint=WATER, axis=(0, 0.2, 0.3))
    if n in ("giggle", "drip"):                                         # a few drips falling off him
        for k in range(4):
            ph = (t * 1.3 + k * 0.25) % 1.0
            q = apply(R, (0.25 * math.cos(k * 1.7), 1.0 - 0.9 * ph, 0.3 * math.sin(k * 1.7)))
            draws.append((PR["ball"], trans(*q) @ scale(0.03), U(mat=0, bump=0.0, tint=WATER, tintMix=1.0), False))
    puff(draws, np.array([BASKET[0], RIM + 0.15, BASKET[1] + 0.7]), T.LID_SHUT - 0.03, t, n=10, size=0.06, spread=1.0, dur=0.5, tint=(0.95, 0.88, 0.72), axis=(0, 0.3, 0.4))
    puff(draws, np.array([SPINPT[0], 0.3, SPINPT[1]]), T.SPIN + 0.1, t, n=10, size=0.06, spread=1.0, dur=0.6, tint=(0.75, 0.9, 0.6), axis=(0, 0.3, 0.2))
    return draws, contacts

def ground_objs(t):
    n = T.shot_at(t)[1]
    if (n in ("splash", "giggle") or (n == "rush" and t > T.TRIP)) and not (n == "giggle" and t > SH["giggle"][0] + 2.0): return ("pip",)
    return ("fox", "pip")
HOOKS.update(build=build_draws, camera=camera, tumble=tumble, ground_objs=ground_objs,
             qa_ignore={("lid", "fox"), ("fox", "lid")})                  # the lid in his paws while he lifts it
if __name__ == "__main__":
    main()
