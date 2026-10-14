"""Tumble & Pip Fables 3: Pebble, Pebble, Plop!  (Aesop: The Crow and the Pitcher)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa
Fable-local additions (the kit is not edited): the jug mesh from props_f3.py (SDF primitives), a dry stone wall made
of the shared stone mesh, a warm hot-day grade (wraps fablekit.render_frame), a "water" caption colour, and a
time-dependent QA ignore that only covers the jug while it is stuck on Tumble's paw (a held prop)."""
from fablekit import *
import fablekit, props_f3

P3 = props_f3.ensure()
JUGM = Mesh(P3["jug"]); D["f3"] = P3                     # D: the QA bank finds the jug mesh by name
COLORS["water"] = (40, 160, 225)

# Kit fix (no fablekit edit): render_base builds the shadow-pass VAOs as "3f 36x" but a vertex is 40 bytes, so
# shadows were drawn from scrambled vertices. Rebuild them with the right stride ("3f 28x").
for _grp in (FOXP, PIPP, PR, SC, E2, {"w": EYE_W, "p": EYE_P}, {"jug": JUGM}):
    for _m in _grp.values():
        _m.svao = ctx.vertex_array(sprog, [(_m.vbo, "3f 28x", "in_pos")], _m.ibo)

# ---------------- world: Tumble's cottage doorstep on a hot day (a new corner of Picnic Meadow) ----------------
J = (0.55, 0.0)                                            # the tall jug
JUG_YAW = -2.36                                            # handle at the back right, away from Tumble and the camera
RIM_R, RIM_Y = 0.245, props_f3.JUG_TOP
W0, WSTEP = 0.2, 0.12                                      # water level at the start, rise per pebble (5 -> 0.8)
PEB_R = 0.07
def jug_base(): return trans(J[0], ground_h(*J) - 0.01, J[1]) @ roty(JUG_YAW)
MJ0 = jug_base()
def jw(p): return apply(MJ0, p)                            # jug-local -> world (jug standing)

STUCK_ARM, STUCK_ROLL = [0.8, 0.8], -0.45                  # solved for clearance: only the arm meets the lip (stuck)
def _stuck_offset():
    st = tumble_base(0.0); st["arms"][0] = list(STUCK_ARM); st["roll"] = STUCK_ROLL; st["yaw"] = 0.0; st["sq"] = 0.0
    h = hand_pos(fox_mats(st)[2]); return np.array([h[0] + 0.06, h[2]])
_so = _stuck_offset()
TS = (J[0] - _so[0], J[1] - _so[1])                        # where Tumble stands with his paw in the jug (facing +z)
LAND = (TS[0] - 0.4, TS[1] - 1.9)
PICK = (LAND[0] + 0.3, LAND[1])                              # where he stands to lift the leaf off the wall                         # after the backward roll
HOLD = [0.3, 1.25, 0.62]                                   # two-paw hold (kit pose: paws together in front of the belly)
HOLD_UP = [0.3, 1.5, 0.62]                                 # the same, lifted a little
LEAF_FWD = 0.59                                            # the leaf sits this far in front of Tumble's feet (paws are at 0.448)
WALL_X = PICK[0] + 0.76                                   # dry stone wall: its top is where the paws hold the leaf
WALL_ZS = (LAND[1] + 0.0, LAND[1] - 0.55, LAND[1] - 1.1)
WALL_TOP = 0.96                                            # leaf rests at 0.986: paw 0.894 + PAW_TOP 0.072 + leaf thickness 0.02
WALL_N = 6
CT = (WALL_X + 0.9, LAND[1] - 3.2)                         # the cottage behind the wall
TRAY_ARM_LOW, TRAY_ARM_UP = HOLD, HOLD_UP                   # both paws under the leaf: on the wall, then lifted
CUP_D = 1.3                                               # count shot: jug axis this far in front of Tumble
CUP_YAW = math.atan2(1.0, 0.35)
CUP = (J[0] - CUP_D * math.sin(CUP_YAW), J[1] - CUP_D * math.cos(CUP_YAW))
DRINK_D = 1.4
DRINK = (J[0] - DRINK_D * math.sin(CUP_YAW), J[1] - DRINK_D * math.cos(CUP_YAW))
MSPOT = (TS[0] - 0.35, TS[1] + 0.55)                       # moral and dance spot, the jug at his paw side
LEAF_REST = (TS[0] + 0.15, TS[1] - 0.55)                   # the empty leaf on the grass after the count

FLOWERS = make_flowers([(J[0], J[1], 1.0), (TS[0], TS[1], 1.0), (LAND[0], LAND[1], 1.3), (MSPOT[0], MSPOT[1], 1.0),
                        (CUP[0], CUP[1], 0.8), (CT[0], CT[1], 7.0), ("box", WALL_X - 0.5, WALL_X + 0.5, WALL_ZS[0] - 0.5, WALL_ZS[-1] + 0.5),
                        ("box", TS[0] - 0.6, J[0] + 0.6, LAND[1] - 0.5, TS[1] + 1.2)], seed=53)

def _peb_bottom():
    """five resting spots on the jug floor (jug-local), placed from the jug's SDF"""
    out = []
    for k in range(5):
        a = k * 2 * math.pi / 5 + 0.4; x, z = 0.115 * math.cos(a), 0.115 * math.sin(a)
        lo, hi = 0.0, 0.5
        for _ in range(30):
            m = (lo + hi) / 2
            if props_f3.jug_sdf(np.array([[x, m, z]]))[0] < PEB_R + 0.004: lo = m
            else: hi = m
        out.append(np.array([x, hi + 0.003 * k, z]))
    return out
PEB_BOTTOM = _peb_bottom()
PEB_TINT = [(0.72, 0.7, 0.74), (0.62, 0.6, 0.66), (0.78, 0.74, 0.7), (0.66, 0.66, 0.72), (0.74, 0.7, 0.66)]

# fox ground contact for a forward/backward pitch about the middle of the body (the backward roll)
_FS = np.concatenate([D["fox"]["parts"][p]["mesh"]["v"][::7] for p in ("body", "head", "leg0", "leg1", "tail")])
def pitch_lift(p):
    y = 0.8 + (_FS[:, 1] - 0.8) * math.cos(p) - _FS[:, 2] * math.sin(p)
    return max(0.0, -float(y.min()))

def fox_mats_p(st):
    """fox_mats plus a pitch about the middle of the body (leaning over the jug, the backward roll)"""
    R, Mh, arms, legs = fox_mats(st)
    p = st.get("pitch", 0.0)
    if p == 0.0: return R, Mh, arms, legs
    root = trans(st["x"], surf(st["x"], st["z"]) + st.get("stand_h", 0.0) - 0.01 + st["y"], st["z"]) @ roty(st["yaw"])
    py = st.get("pivot", 0.8)
    P = root @ trans(0, py, 0) @ rotx(p) @ trans(0, -py, 0) @ np.linalg.inv(root)
    return P @ R, P @ Mh, [P @ a for a in arms], [P @ l for l in legs]

# ---------------- Tumble ----------------
def pant(st, t):                                           # hot: tongue out between sung words
    st["tongue"] = 0.0 if mouth_at("tumble", t) > 0.05 else 1.0
def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    st["x"], st["z"] = TS; st["yaw"] = 0.0
    if n in ("hook_peer", "hook_pov", "title_wide", "hot_walk"):
        a = SH["title_wide"][0]; b = SH["hot_walk"][0] + 2.2
        start = (TS[0] - 3.4, TS[1] + 0.9)
        if t < b:
            walk_to(st, t, start, TS, a, b, rate=1.8)      # a slow, hot trudge to the jug
            st["head"][0] = 0.12
        else:
            u = ease(clampu(t, b, b + 0.5)); st["yaw"] = lerp(math.atan2(TS[0] - start[0], TS[1] - start[1]), 0.0, u)
            L = T.line("Setup A")
            if L["t0"] < t < L["t1"] + 0.3: st["arms"][1] = [0.9, 0.3]   # paw fanning his face on "hot"
        if n == "hot_walk" and t < SH["hot_walk"][0] + 1.5: st["arms"][0] = [0.55 + 0.3 * math.sin(t * 9), 0.5]
        pant(st, t)
    elif n == "pip_try":                                   # watches Pip, head tilted, still panting
        st["yaw"] = 0.25; st["head"][2] = -0.1; st["head"][1] = 0.25
        L = T.line("Setup B")
        if t > L["t1"]: st["head"][0] = 0.1 * math.sin((t - L["t1"]) * 8) * math.exp(-(t - L["t1"]))
        pant(st, t)
    elif n == "paw_in":
        a = SH[n][0]
        u = ease(clampu(t, T.PAW_IN - 0.2, T.PAW_IN + 0.7))
        st["roll"] = STUCK_ROLL * u; st["y"] += 0.036 * u
        st["arms"][0] = lerp([0.5, 1.4], STUCK_ARM, ease(clampu(t, T.PAW_IN - 0.2, T.PAW_IN + 0.4))).tolist() if t > T.PAW_IN - 0.2 else [0.2, 0.3]
        if u >= 1:
            st["arms"][0] = list(STUCK_ARM)
            if t > T.STUCK - 0.6:                          # tries to pull: little tugs, then "stuck!" to camera
                d = t - (T.STUCK - 0.6)
                st["roll"] = STUCK_ROLL + 0.04 * abs(math.sin(d * 9)) * (t < T.STUCK + 0.2)
                st["head"][1] = 0.35 * ease(clampu(t, T.STUCK - 0.2, T.STUCK + 0.2)); st["head"][0] = -0.08
                st["arms"][1] = [0.7, 0.2] if t > T.STUCK else [0.15, 0.0]
    elif n == "pull":
        st["y"] += 0.036; st["roll"] = STUCK_ROLL; st["arms"][0] = list(STUCK_ARM); st["arms"][1] = [0.6, 0.0]
        for k, pt in enumerate(T.PULLS):                   # each pull leans him further back and lifts the jug
            d = t - pt
            if 0 <= d < 0.5:
                s = math.sin(math.pi * d / 0.5)
                st["roll"] = STUCK_ROLL + (0.2 + 0.04 * k) * s; st["sq"] -= 0.04 * s; st["head"][2] = 0.15 * s
                st["arms"][0] = [STUCK_ARM[0] + 0.3 * s, STUCK_ARM[1]]
        d = t - (T.POP - 0.35)
        if 0 <= d:                                         # the big final heave
            s = ease(clampu(t, T.POP - 0.35, T.POP))
            st["roll"] = STUCK_ROLL + 0.3 * s; st["head"][2] = 0.2 * s; st["sq"] -= 0.06 * s
            st["arms"][0] = [STUCK_ARM[0] + 0.4 * s, STUCK_ARM[1]]
        if t >= T.POP: roll_back(st, t)
    elif n == "roll_back":
        roll_back(st, t)
    elif n == "count":
        st["x"], st["z"] = CUP; st["yaw"] = CUP_YAW; st["arms"] = [list(TRAY_ARM_LOW), list(TRAY_ARM_LOW)]
        st["head"][0] = 0.1                                # watching the jug mouth
        for c in T.COUNT:                                  # a happy bounce on every plop
            d = t - (c + 0.25)
            if 0 <= d < 0.3: st["y"] += 0.03 * math.sin(math.pi * d / 0.3)
    elif n == "drink":
        st["x"], st["z"] = DRINK; st["yaw"] = CUP_YAW
        lean = ease(clampu(t, T.LAP - 0.45, T.LAP)) * (1 - ease(clampu(t, T.LAP + 0.9, T.LAP + 1.3)))
        st["pivot"] = 0.15; st["pitch"] = 0.55 * lean; st["y"] += 0.09 * lean; st["head"][0] = 0.1 + 0.1 * lean
        st["arms"] = [[0.35, 0.3], [0.35, 0.3]]
        st["tongue"] = 1.0 if T.LAP - 0.1 < t < T.LAP + 0.9 else 0.0
        if t > T.LAP + 1.0: st["head"][0] = 0.05
    elif n in ("moral", "chorus"):
        st["x"], st["z"] = MSPOT
        dance_tumble(st, t, n)
    else:                                                  # button: the splash lands on his nose; he giggles
        a = SH["button_crane"][0]; st["x"], st["z"] = MSPOT; st["yaw"] = -0.05
        down = ease(clampu(t, a + 0.45, a + 0.85))
        st["arms"] = [lerp(DANCE_ARM, [0.3, 0.3], down).tolist(), [0.3, 0.3]]
        if t > T.SPLASH:
            d = t - T.SPLASH
            st["head"][0] = -0.12 * math.exp(-d * 3); st["sq"] -= 0.05 * math.exp(-d * 5) * math.cos(d * 25)
            st["y"] += 0.03 * abs(math.sin(d * 10)); st["arms"][1] = [0.4, 1.2 * ease(clampu(t, T.SPLASH + 0.1, T.SPLASH + 0.4))]
    return st

def roll_back(st, t):
    """the cork-pop: his paw pops out, he tumbles backwards in a somersault and lands by the stone wall, dizzy"""
    u = clampu(t, T.POP, T.ROLL_END)
    st["x"], st["z"] = lerp(TS, LAND, ease(u)); st["yaw"] = 0.0
    st["roll"] = STUCK_ROLL * (1 - ease(clampu(t, T.POP, T.POP + 0.15)))
    st["arms"] = [[0.9, 1.6], [0.9, 1.6]] if u < 1 else [[0.3, 0.2], [0.3, 0.2]]
    if 0 < u < 1:
        p = -2 * math.pi * ease(clampu(t, T.POP + 0.08, T.ROLL_END - 0.1))
        st["pitch"] = p; st["sq"] = -0.12 * math.sin(math.pi * u); st["y"] += pitch_lift(p) + 0.05 * math.sin(math.pi * u)
        st["legs"] = [0.12, 0.12]; st["arms"] = [[0.4, 2.2], [0.4, 2.2]]
    if t >= T.ROLL_END:
        d = t - T.ROLL_END; fade = 1 - ease(clampu(t, T.ROLL_END + 0.5, T.ROLL_END + 0.8))   # wobble settles before the leaf is held
        st["roll"] = 0.12 * math.sin(d * 7) * math.exp(-d * 1.5) * fade; st["head"][2] = 0.15 * math.sin(d * 6) * math.exp(-d * 1.2) * fade
        st["sq"] = st["sq"] * fade - 0.1 * math.exp(-d * 8) * math.cos(d * 22)
        if t > T.IDEA:                                     # turns to the wall and lifts the leaf of pebbles
            v = ease(clampu(t, T.IDEA, T.IDEA + 0.5)); st["yaw"] = lerp(0.0, math.pi / 2, v)
            st["x"] = lerp(LAND[0], PICK[0], ease(clampu(t, T.IDEA, T.IDEA + 0.6)))
            st["head"][0] = 0.1
            st["arms"] = [list(TRAY_ARM_LOW), list(TRAY_ARM_LOW)] if t > T.IDEA + 0.35 else st["arms"]
            if t > T.SCOOP:
                w = ease(clampu(t, T.SCOOP, T.SCOOP + 0.4))
                st["arms"] = [lerp(TRAY_ARM_LOW, TRAY_ARM_UP, w).tolist() for _ in range(2)]
                st["x"] = PICK[0] - 0.12 * ease(clampu(t, T.SCOOP + 0.3, T.SCOOP + 0.8))   # steps back from the wall with it

def tumble_mats(t):
    st = tumble(t); return st, fox_mats_p(st)

# ---------------- the jug, the water and the pebbles ----------------
_A_STUCK = None
def jug_mat(t, arms):
    """the jug's world matrix: standing, or riding Tumble's stuck paw during the pulls (drops back on the pop)"""
    global _A_STUCK
    if _A_STUCK is None:
        s = tumble_base(0.0); s["x"], s["z"] = TS; s["yaw"] = 0.0; s["arms"][0] = list(STUCK_ARM); s["roll"] = STUCK_ROLL; s["sq"] = 0.0; s["y"] = 0.036
        _A_STUCK = fox_mats(s)[2][0]
    if SH["pull"][0] <= t < T.POP + 0.25:
        if t < T.POP:
            return arms[0] @ np.linalg.inv(_A_STUCK) @ MJ0
        d = t - T.POP                                      # drops back down with a little squash
        return MJ0 @ scale(1 + 0.06 * math.exp(-d * 15), 1 - 0.1 * math.exp(-d * 15) * math.cos(d * 30), 1 + 0.06 * math.exp(-d * 15))
    return MJ0
def n_in(t):
    """pebbles that have reached the water so far, and the eased level"""
    k = sum(1 for c in T.COUNT if t >= c + 0.22)
    lvl = W0
    for i, c in enumerate(T.COUNT):
        lvl += WSTEP * ease(clampu(t, c + 0.22, c + 0.55))
    if t >= SH["count"][1] - 1e-6 or T.shot_at(t)[1] in ("drink", "moral", "chorus", "button_crane"): lvl = W0 + 5 * WSTEP; k = 5
    return k, lvl

# ---------------- Pip ----------------
def rim_pt(a):
    """a point on top of the rolled lip (jug-local angle a, 0 = towards the jug's local +z), lifted for Pip's feet"""
    return jw((RIM_R * math.sin(a), RIM_Y + 0.057, RIM_R * math.cos(a))) + UP
def facing(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])
JC = jw((0, RIM_Y, 0))                                    # centre of the jug mouth
def rim_far():
    """rim point on the side away from Tumble (world +x), facing back across the mouth"""
    best = None
    for k in range(72):
        a = k * 2 * math.pi / 72; p = rim_pt(a)
        if best is None or p[0] > best[0]: best = p
    return best
RIM_FAR = rim_far()
HOVER_R = np.array([J[0] + 0.62, 1.38, TS[1] + 0.25])    # beside the jug at Tumble's depth, clear of his head
LEAF_SX, LEAF_SZ = 0.34, 0.27                              # the leaf is 0.7 long and 0.22 wide, a tray for five pebbles
def _hold_c():
    """leaf centre when held in the two-paw hold, Tumble facing +x at the wall"""
    st = tumble_base(0.0); st["x"], st["z"] = PICK; st["yaw"] = math.pi / 2; st["sq"] = 0.0; st["arms"] = [list(HOLD), list(HOLD)]
    m = fox_mats(st); return (hand_pos(m[2], 0) + hand_pos(m[2], 1)) / 2
_HC = _hold_c()
def tray_mats(t, st, mats):
    """the leaf tray: on top of the wall, then on Tumble's two paws (count), then on the grass after the cut.
    Returns its matrix and the five pebble seats on it (world)"""
    n = T.shot_at(t)[1]
    if n == "count" or (n == "roll_back" and t > T.SCOOP):
        R = mats[0]
        h0, h1 = hand_pos(mats[2], 0), hand_pos(mats[2], 1)
        side = h0 - h1; side[1] = 0; side /= np.linalg.norm(side)
        fwd = R[:3, 2].copy(); fwd[1] = 0; fwd /= np.linalg.norm(fwd)
        c = (h0 + h1) / 2 + np.array([0, PAW_TOP + 0.02, 0]) + fwd * (LEAF_FWD - 0.448)
    elif n in ("drink", "moral", "chorus", "button_crane"):
        c = np.array([LEAF_REST[0], ground_h(*LEAF_REST) + 0.02, LEAF_REST[1]]); side = np.array([math.cos(0.4), 0, -math.sin(0.4)])
    else:
        c = np.array([_HC[0] + LEAF_FWD - 0.448, _HC[1] + PAW_TOP + 0.02, LAND[1]]); side = np.array([0, 0, -1.0])
    M = trans(*c) @ roty(math.atan2(-side[2], side[0])) @ scale(LEAF_SX, 0.5, LEAF_SZ) @ trans(0.265, 0, 0)
    seats = [c + side * x + np.array([0, 0.03 + PEB_R * 0.8, 0]) for x in (-0.24, -0.12, 0.0, 0.12, 0.24)]
    return M, seats

def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    R, Mh, arms, legs = mats
    face = apply(Mh, (0, 1.5, 0.6))
    into = facing(RIM_FAR, JC)
    if n in ("hook_peer", "hook_pov"):                     # peering down into the jug
        pk = 0.45 + 0.08 * math.sin(t * 2.2)
        return RIM_FAR, into, False, pk, True, {"wings": (0.3, 0.3)}
    if n in ("title_wide", "hot_walk"):                    # hot: fanning himself with a wing on the rim
        yaw = into + 0.9 * ease(clampu(t, SH["title_wide"][0] + 0.5, SH["title_wide"][0] + 1.2))
        if n == "hot_walk": yaw = facing(RIM_FAR, face)
        return RIM_FAR, yaw, False, 0.0, True, {"wings": (0.9 + 0.5 * math.sin(t * 12), 0.05)}
    if n == "pip_try":                                     # leans in further and further, wobbles, can't reach
        a = SH[n][0]; L = T.line("Setup B")
        reach = ease(clampu(t, a + 0.1, L["t0"] + 1.0)) * (1 - ease(clampu(t, L["t1"] - 0.6, L["t1"] - 0.1)))
        pk = 0.35 + 0.45 * reach + 0.06 * math.sin(t * 13) * reach
        ex = {"wings": (1.0 + 0.3 * math.sin(t * 16), 1.0 + 0.3 * math.sin(t * 16 + 1))} if reach > 0.5 else {"wings": (0.2, 0.2)}
        if t > L["t1"] - 0.2: ex = {"point": True}         # "let me think!": wing up to his head
        return RIM_FAR, into, False, pk * (t < L["t1"] - 0.2) + 0.0, True, ex
    if n == "paw_in":                                      # hops off the rim to hover beside, clear of the paw
        a = SH[n][0]; u = clampu(t, a, a + 0.7)
        p = lerp(RIM_FAR, HOVER_R, ease(u)); p[1] += 0.3 * math.sin(math.pi * u)
        p = p + np.array([0, 0.05 * math.sin(t * 6), 0]) * (u >= 1)
        return p, facing(p, face), True, 0.0, False, {"gentle": True}
    if n == "pull" or (n == "roll_back" and t < T.ROLL_END):
        p = HOVER_R + np.array([0, 0.05 * math.sin(t * 6), 0])
        return p, facing(p, face), True, 0.0, False, ({"cheer": False} if t < T.POP else {"gentle": True})
    if n == "roll_back":                                   # flies to the wall (up, across, down) and points at the pebbles
        top = np.array([WALL_X + 0.1, WALL_TOP - 0.05 + PIP_FOOT, LAND[1] + 0.34])
        up1 = HOVER_R + np.array([0, 0.6, 0]); up2 = top + np.array([0, 0.75, 0])
        u = clampu(t, T.ROLL_END, T.IDEA)
        if u < 1:
            if u < 0.3: p = lerp(HOVER_R, up1, ease(u / 0.3))
            elif u < 0.7: p = lerp(up1, up2, ease((u - 0.3) / 0.4))
            else: p = lerp(up2, top, ease((u - 0.7) / 0.3))
            return p, facing(p, top) if u < 0.7 else -math.pi / 2, True, 0.0, False, {"gentle": True}
        return top, -math.pi / 2 + 0.3, False, 0.0, True, ({"point": True} if t < T.SCOOP else {"cheer": True})
    if n == "count":
        return count_pip(t, st, mats)
    if n == "drink":                                       # sips from the brim, then cheers
        sip = 0.0
        d = t - T.SIP
        if 0 <= d < 0.6: sip = 0.55 * math.sin(math.pi * d / 0.6)
        return RIM_FAR, into, False, sip, True, ({"cheer": True} if t > T.LAP + 0.3 else {})
    if n in ("moral", "chorus"):
        return dance_pip(t, st, mats, n, arrive_from=RIM_FAR)
    a, b = SH["button_crane"]                              # hops from the paw to the rim and splashes a wing
    p0 = paw_seat(fox_mats_p(tumble(a))[2]); rim = rim_pt_near(p0)
    if t < a + 0.2: return p0, 0.35, False, 0.0, True, {}          # still riding the paw after the cut
    u = clampu(t, a + 0.2, a + 0.8)
    if u < 1:
        p = lerp(p0, rim, ease(u)); p[1] += 0.35 * math.sin(math.pi * u)
        return p, facing(p, JC), True, 0.0, False, {"gentle": True}
    sp = 0.0
    d = t - (T.SPLASH - 0.15)
    if 0 <= d < 0.3: sp = 0.4 * math.sin(math.pi * d / 0.3)
    return rim, facing(rim, JC) + 0.5, False, sp, True, ({"wings": (-0.3, 0.1)} if 0 <= d < 0.3 else {"cheer": True} if d > 0.6 else {})
def rim_pt_near(p):
    best = None
    for k in range(72):
        q = rim_pt(k * 2 * math.pi / 72)
        if best is None or np.linalg.norm(q - p) < np.linalg.norm(best - p): best = q
    return best

def count_pip(t, st, mats):
    """Pip picks each pebble off the leaf and drops it into the jug on its sung number"""
    M, seats = tray_mats(t, st, mats)
    over = JC + np.array([0, 0.42, 0])
    k = 0
    for i, c in enumerate(T.COUNT):
        if t >= c - 0.45: k = i
    c = T.COUNT[k]
    seat = seats[4 - k]                                    # works from the jug side of the leaf
    yaw_to = facing(over, seat)
    grab = seat + np.array([0, 0.03, 0]) - apply(roty(yaw_to) @ rotx(0.6) @ scale(1.1), (0, 0.31, 0.27))
    # timeline per pebble: fly to the seat (c-0.45..c-0.25), grab, back over the mouth (c-0.25..c-0.02), release at c
    if t < T.COUNT[0] - 0.45:
        p = over + np.array([0, 0.04 * math.sin(t * 6), 0]); return p, yaw_to, True, 0.0, False, {"gentle": True}
    if t < c - 0.25:
        u = ease(clampu(t, c - 0.45, c - 0.25)); p = lerp(over, grab, u)
        return p, yaw_to, True, 0.6 * u, False, {"gentle": True, "beak": True}
    u = ease(clampu(t, c - 0.25, c - 0.02)); p = lerp(grab, over, u)
    return p, yaw_to, True, 0.6 * (1 - u), False, {"gentle": True, "beak": t < c}

def pebbles(t, st, mats, Mp, jugM):
    """world centres of the five pebbles and whether each is under water (hidden from QA as it sinks)"""
    n = T.shot_at(t)[1]
    M, seats = tray_mats(t, st, mats)
    out = []
    for k in range(5):
        seat = seats[4 - k]
        c = T.COUNT[k]
        if n in ("count",):
            if t < c - 0.25: out.append(seat)
            elif t < c: out.append(beak_pos(Mp) + np.array([0, -0.03, 0]) if Mp is not None else seat)
            else:                                          # falls straight down the neck, then sinks to the floor
                top = JC + np.array([0, 0.42 + 0.31 + 0.02 - 0.03, 0])
                _, lvl = n_in(c + 0.22)
                surf_y = jw((0, lvl, 0))[1]
                u = clampu(t, c, c + 0.22)
                p = top.copy(); p[1] = lerp(top[1], surf_y, u * u)
                if t > c + 0.22:
                    bot = jw(PEB_BOTTOM[k]); v = ease(clampu(t, c + 0.22, c + 0.9))
                    p = lerp(np.array([JC[0], surf_y, JC[2]]), bot, v)
                out.append(p)
        elif n in ("roll_back", "pull") or (n == "paw_in"):
            out.append(seat)
        elif n in ("hook_peer", "hook_pov", "title_wide", "hot_walk", "pip_try"):
            out.append(seat)
        else:
            out.append(apply(jugM, PEB_BOTTOM[k]))
    return out

# ---------------- camera ----------------
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    if name == "hook_peer":                                # side-on medium: Pip on the rim peering in
        tgt = lerp(RIM_FAR, JC, 0.5) + np.array([0, 0.05, 0])
        return fit_cam(tgt, lerp(8, 18, e), 14, 0.75, 0.75, lift=0.1)
    if name == "hook_pov":                                 # overhead down the neck: the water is way down there
        tgt = jw((0, 0.4, 0)) - np.array([0.1, 0, 0])
        return fit_cam(tgt, -60, lerp(78, 82, e), 0.5, 0.5, fov=40, lift=0.0)
    if name == "title_wide":
        return fit_cam(np.array([lerp(TS[0], J[0], 0.4) - 0.3, 1.5, J[1] - 0.6]), 8, 9, 3.0, 2.7 if not WIDE else 2.0, lift=0.05)
    if name == "hot_walk":                                 # low tracking alongside the trudge
        st = tumble(t)
        cx = lerp(st["x"], J[0], 0.35)
        return fit_cam(np.array([cx, 1.1, st["z"] + 0.1]), 50, -6, 1.6, 1.45, lift=0.08)
    if name == "pip_try":                                  # macro, side-on to Pip's beak and the mouth of the jug
        tgt = lerp(RIM_FAR, JC, 0.5) + np.array([0, 0.0, 0])
        return fit_cam(tgt, lerp(10, 2, e), 20, 0.62, 0.62, fov=34, lift=0.12)
    if name == "paw_in":                                   # medium front: the paw goes in, uh-oh
        return fit_cam(np.array([lerp(TS[0], J[0], 0.7), 1.0, TS[1] + 0.15]), lerp(24, 18, e), lerp(30, 40, e), 1.5, 1.5)   # high three-quarter: the paw goes down into the mouth
    if name == "pull":                                     # wide low angle: pull, pull, POP
        return fit_cam(np.array([lerp(TS[0], J[0], 0.6), 1.0, TS[1] + 0.15]), 20, 30, 1.9, 1.9)
    if name == "roll_back":                                # wide side: the roll back to the wall
        k = ease(clampu(t, SH["roll_back"][0], T.ROLL_END + 0.3))
        return fit_cam(np.array([lerp(TS[0] + 0.3, LAND[0] + 0.3, k), 1.1, lerp(TS[1] - 0.4, LAND[1] + 0.1, k)]), 8, 22, lerp(2.3, 1.9, k), lerp(2.0, 1.7, k))
    if name == "count":                                    # high three-quarter close-up into the jug mouth
        tgt = JC + np.array([0, 0.12, 0]) - np.array([math.sin(CUP_YAW), 0, math.cos(CUP_YAW)]) * 0.18
        return fit_cam(tgt, math.degrees(CUP_YAW) - lerp(28, 18, e), 58, 1.0, 1.0, fov=36, lift=0.1)
    if name == "drink":
        tgt = lerp(JC, np.array([DRINK[0], 1.0, DRINK[1]]), 0.45)
        return fit_cam(tgt, math.degrees(CUP_YAW) + 45, 10, 1.1, 1.1, lift=0.1)
    if name == "moral":
        return fit_cam(np.array([MSPOT[0] + 0.25, lerp(1.35, 1.45, e), MSPOT[1]]), lerp(14, 8, e), 5, lerp(1.3, 1.1, e), lerp(1.4, 1.15, e))
    if name == "chorus":
        return fit_cam(np.array([MSPOT[0] + 0.3, 1.2, MSPOT[1]]), 8, 6, 1.4, 1.35)
    return fit_cam(np.array([lerp(MSPOT[0], J[0], 0.4), lerp(1.2, 2.0, e), MSPOT[1] - 0.1]), 6, lerp(5, 16, e), lerp(1.4, 2.3, e), lerp(1.4, 2.2, e), lift=0.04)

# ---------------- draws ----------------
class QAIgnore:
    """held props only: pebbles in a paw or a beak, the leaf tray on the paws, and the jug while it is stuck on
    Tumble's paw (his arm is tagged 'fox_paw' so the rest of him is still checked against the jug)"""
    t = 0.0
    base = {("pebble", "fox"), ("fox", "pebble"), ("pebble", "fox_paw"), ("fox_paw", "pebble"), ("pebble", "pip"), ("pip", "pebble"),
            ("fox", "fox_paw"), ("fox_paw", "fox"), ("leaf", "fox_paw"), ("fox_paw", "leaf"), ("leaf", "pebble"), ("pebble", "leaf")}
    def __contains__(self, pair):
        if pair in self.base: return True
        return pair in (("jug", "fox_paw"), ("fox_paw", "jug")) and T.PAW_IN - 0.1 <= self.t < T.POP + 0.05
QAI = QAIgnore()

STONE_T = (0.84, 0.8, 0.74)
def build_draws(t):
    QAI.t = t
    draws, contacts = [], []
    meadow_backdrop(draws, t, cottage=None)
    draws.append((SC["cottage"], trans(CT[0], ground_h(*CT) - 0.05, CT[1]) @ roty(-0.35), U(mat=0, bump=0.6, obj="cottage"), True))
    for zi, z in enumerate(WALL_ZS):                       # dry stone wall: flat stones, staggered
        for k in range(WALL_N):
            x = WALL_X + 0.02 * math.sin(k * 2.1 + zi) * (k < WALL_N - 1); zz = z + 0.03 * math.sin(k * 1.7 + zi * 2) * (k < WALL_N - 1)
            draws.append((SC["stone"], trans(x, ground_h(WALL_X, z) + 0.07 + (WALL_TOP - 0.14) / (WALL_N - 1) * k, zz) @ roty(math.pi / 2 + 0.1 * math.sin(k + zi) * (k < WALL_N - 1)) @ scale(0.85, 1.2, 0.75),
                          U(mat=0, bump=0.9, tint=tuple(c * (0.92 + 0.08 * ((k + zi) % 3)) for c in STONE_T), tintMix=1.0, obj="wall"), True))
    for (x, z, s) in [(CT[0] - 2.0, CT[1] + 1.6, 0.2), (J[0] + 1.3, J[1] - 0.6, 0.16), (MSPOT[0] - 1.3, MSPOT[1] - 0.2, 0.18)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))
    draw_flowers(draws, t, FLOWERS)
    n = T.shot_at(t)[1]
    st = tumble(t); mats = fox_mats_p(st); R, Mh, arms, legs = mats
    k0 = len(draws)
    draw_tumble(draws, contacts, t, st, mats)
    for i in range(k0, len(draws)):                        # his right arm gets its own QA tag (see QAIgnore)
        if draws[i][0] is FOXP["arm0"]: draws[i] = (draws[i][0], draws[i][1], dict(draws[i][2], obj="fox_paw"), draws[i][3])
    if st.get("tongue", 0) > 0 and mouth_at("tumble", t) < 0.05:
        draws.append((PR["ball"], Mh @ trans(0, 1.17, 0.47) @ rotx(0.5) @ scale(0.06, 0.02, 0.085), U(mat=0, bump=0.0, tint=(0.95, 0.45, 0.55), tintMix=1.0), False))
    pip = pip_state(t, st, mats)
    Mp = draw_pip(draws, contacts, t, pip, arms)
    # jug, water, pebbles
    jugM = jug_mat(t, arms)
    draws.append((JUGM, jugM, U(mat=0, bump=0.7, seed=4.0, obj="jug"), True))
    contacts.append((jugM[0, 3], jugM[2, 3], 0.5, 1.0))
    k, lvl = n_in(t)
    r = props_f3.inner_radius(lvl) - 0.006
    wob = 0.0
    for c in T.COUNT:
        d = t - (c + 0.22)
        if 0 <= d < 0.6: wob = 0.012 * math.sin(d * 30) * math.exp(-d * 6)
    draws.append((PR["ball"], jugM @ trans(0, lvl + wob, 0) @ scale(r, 0.01, r), U(mat=3, bump=0.0, tint=(0.45, 0.78, 0.98), tintMix=1.0), False))
    draws.append((PR["ball"], jugM @ trans(-r * 0.35, lvl + wob + 0.004, r * 0.25) @ scale(r * 0.28, 0.008, r * 0.16), U(mat=3, bump=0.0, tint=(0.85, 0.95, 1.0), tintMix=1.0), False))
    TM, seats = tray_mats(t, st, mats)
    draws.append((E2["bigleaf"], TM, U(mat=0, bump=0.3, obj="leaf"), True))
    for i, p in enumerate(pebbles(t, st, mats, Mp, jugM)):
        draws.append((PR["ball"], trans(*p) @ scale(PEB_R, PEB_R * 0.8, PEB_R), U(mat=0, bump=0.4, tint=PEB_TINT[i], tintMix=1.0, obj="pebble"), True))
    for c in T.COUNT:                                      # plop: a splash out of the mouth on every pebble
        _, l2 = n_in(c + 0.22)
        puff(draws, jw((0, l2 + 0.05, 0)), c + 0.22, t, n=8, size=0.028, spread=0.35, dur=0.45, tint=(0.75, 0.9, 1.0), axis=(0, 0.9, 0))
    if T.POP - 0.02 < t < T.POP + 0.5:                       # the cork-pop
        puff(draws, jw((0, RIM_Y + 0.12, 0)), T.POP, t, n=10, size=0.06, spread=0.9, dur=0.45, tint=(1.0, 0.96, 0.85), axis=(0, 0.6, 0.2))
    if n == "button_crane":                                # the wing-splash arcs onto Tumble's nose
        nose = apply(Mh, (0, 1.35, 0.55)); a0 = T.SPLASH - 0.4
        u = clampu(t, a0, T.SPLASH)
        if 0 < u < 1:
            for j in range(4):
                q = lerp(JC + np.array([0, 0.05, 0]), nose, u - 0.04 * j); q[1] += 0.45 * math.sin(math.pi * (u - 0.04 * j))
                draws.append((PR["ball"], trans(*q) @ scale(0.022), U(mat=3, bump=0.0, tint=(0.6, 0.85, 1.0), tintMix=1.0), False))
        puff(draws, nose, T.SPLASH, t, n=8, size=0.025, spread=0.5, dur=0.4, tint=(0.7, 0.9, 1.0), axis=(0, 0.3, 0.3))
    return draws, contacts

# ---------------- hot-day grade ----------------
HOT_SKY = ((0.42, 0.68, 0.96), (0.72, 0.86, 0.98), (1.0, 0.88, 0.7))
_render_frame = fablekit.render_frame
def render_frame(t):
    img = _render_frame(t)
    f = img[..., :3].astype(np.float32)
    f[..., 0] *= 1.04; f[..., 1] *= 1.0; f[..., 2] *= 0.93     # warm, summery light
    img[..., :3] = np.clip(f, 0, 255).astype(np.uint8)
    return img
fablekit.render_frame = render_frame

HOOKS.update(build=build_draws, camera=camera, tumble=tumble, sky=lambda t: HOT_SKY,
             ground_objs=lambda t: ("pip",) if T.shot_at(t)[1] in ("pull", "roll_back") and T.POP <= t < T.ROLL_END else ("fox", "fox_paw", "pip"),
             qa_ignore=QAI)
if __name__ == "__main__":
    main()
