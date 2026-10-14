"""Tumble & Pip Fables 2: Sour Apples!  (Aesop: The Fox and the Grapes)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa"""
from fablekit import *

# Kit bug override: render_base builds the shadow VAO with "3f 36x", but a vertex is 40 bytes (pos+nrm+col+ao): "3f 28x".
import gc as _gc
import render_base as _rb
def _fix_svao(m):
    m.svao = _rb.ctx.vertex_array(_rb.sprog, [(m.vbo, "3f 28x", "in_pos")], m.ibo)
for _m in [o for o in _gc.get_objects() if isinstance(o, _rb.Mesh)]:
    _fix_svao(_m)
_orig_mesh_init = _rb.Mesh.__init__
def _mesh_init(self, m):
    _orig_mesh_init(self, m); _fix_svao(self)
_rb.Mesh.__init__ = _mesh_init

# ---------------- world: under the big apple tree (a new corner of Picnic Meadow) ----------------
TREE = (-0.9, -1.7); TREE_S = 2.2
APPLE_S = 0.5
A = np.array([TREE[0] + 1.03, 2.85, TREE[1] + 0.78])     # the red apple under the canopy (underside ~3.05): just above his jumping ears
APPLE_TOP = 0.61 * APPLE_S; APPLE_BOT = 0.41 * APPLE_S
SPOT0 = (A[0] - 0.05, A[2] + 0.12)
STUMP = (SPOT0[0] + 1.95, SPOT0[1] - 0.95); STUMP_TOP = 0.55 - 0.02     # back-right, clear of him and the tree
PILE = (SPOT0[0] + 1.62, SPOT0[1] + 0.6)                  # autumn leaf pile, front-right
MSPOT = (SPOT0[0] + 0.5, SPOT0[1] + 0.9)                  # where they do the moral and the dance (clear of the pile)
REACH_ARM = [2.0, 0.3]                                     # paw up and out: a reach that reads from the front (paw at 1.22)
CROSS0, CROSS1 = [0.1, 1.5, 1.3], [0.1, 1.35, 1.3]         # arms crossed in front of his chest (inward swing)
CATCH = [0.3, 1.25, 0.62]                                  # both paws in front, 0.44 apart: holds the apple
BITE = [0.2, 1.6, 0.6]
def _reach_offset():
    st = tumble_base(0.0); st["arms"][0] = REACH_ARM; st["yaw"] = 0.0
    return hand_pos(fox_mats(st)[2])
_ho = _reach_offset()
SPOT = (A[0] - 0.05, A[2] + 0.12)                         # right under the apple
RUN0 = (SPOT[0] - 2.3, SPOT[1] + 0.9)                     # run-up starts front-left, clear of the trunk
DIVE_DIR = np.array([PILE[0] - SPOT[0], PILE[1] - SPOT[1]]); DIVE_DIR /= np.linalg.norm(DIVE_DIR)
DIVE_YAW = math.atan2(DIVE_DIR[0], DIVE_DIR[1])
BURIED = (PILE[0] - DIVE_DIR[0] * 0.35, PILE[1] - DIVE_DIR[1] * 0.35)
POPPED = (PILE[0] - DIVE_DIR[0] * 0.95, PILE[1] - DIVE_DIR[1] * 0.95 + 0.15)
STUMP_PIP = np.array([STUMP[0] + 0.25, surf(*STUMP) + STUMP_TOP, STUMP[1] + 0.25]) + UP
FLOWERS = make_flowers([(TREE[0], TREE[1], 2.0), (STUMP[0], STUMP[1], 1.3), (PILE[0], PILE[1], 2.6), (SPOT[0], SPOT[1], 1.2),
                        (MSPOT[0], MSPOT[1], 1.5), ("box", RUN0[0] - 0.6, SPOT[0] + 0.3, RUN0[1] - 0.7, RUN0[1] + 0.6),
                        ("box", SPOT[0] - 0.3, PILE[0] + 0.5, SPOT[1] - 0.6, PILE[1] + 0.6)], seed=37)
_rng = np.random.default_rng(5)
PILE_LEAVES = []                                          # (offset, rotation angles, scale, tint)
for k in range(70):
    r = 0.75 * math.sqrt(_rng.uniform(0, 1)); a = _rng.uniform(0, 6.28)
    h = 0.42 * (1 - (r / 0.8) ** 2) * _rng.uniform(0.55, 1.0)
    tint = [(0.95, 0.62, 0.25), (0.92, 0.42, 0.25), (0.98, 0.8, 0.3), (0.75, 0.45, 0.22)][k % 4]
    PILE_LEAVES.append(((r * math.cos(a), h, r * math.sin(a)), _rng.uniform(0, 6.28, 3), _rng.uniform(2.6, 3.4), tint))

# ---------------- Tumble ----------------
def jump_y(t, t0, hgt=0.4, dur=0.5):
    d = t - t0
    return hgt * math.sin(math.pi * d / dur) if 0 <= d < dur else 0.0
def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    st["x"], st["z"] = SPOT; st["yaw"] = 0.0
    if n == "hook_reach":                                   # on tiptoe, stretching for the apple
        st["arms"][0] = REACH_ARM; st["arms"][1] = [2.0 - 0.25 * math.sin(t * 5), 0.3]
        st["y"] += 0.08 + 0.05 * math.sin(t * 5); st["legs"] = [0.04, 0.04]; st["head"][0] = -0.35; st["sq"] += 0.03
    elif n == "title_wide":
        st["head"][0] = -0.3; st["arms"] = [[0.5, 0.6], [0.5, 0.6]]
    elif n == "jumps":                                      # three jumps on the three sung "jump"s
        st["head"][0] = -0.3
        for j in T.JUMPS:
            y = jump_y(t, j, hgt=0.42, dur=0.55)
            if y > 0: st["y"] += y; st["arms"][0] = REACH_ARM; st["arms"][1] = [2.0, 0.3]; st["legs"] = [0.1, 0.1]
            d = t - (j + 0.55)
            if 0 <= d < 0.3: st["sq"] -= 0.1 * math.exp(-d * 9) * math.cos(d * 25)
        if not any(0 <= t - j < 0.55 for j in T.JUMPS): st["arms"][0] = [1.6, 0.4]
    elif n in ("big_jump", "leaf_pile"):
        if t < T.LEAP:                                      # run-up
            walk_to(st, t, RUN0, SPOT, SH["big_jump"][0], T.LEAP, rate=3.0); st["arms"] = [[0.6, 0.8], [0.6, 0.8]]
        else:                                               # leap: just misses the apple, then dives into the leaves
            u = clampu(t, T.LEAP, T.LAND)
            st["x"], st["z"] = lerp(SPOT, BURIED, u); st["yaw"] = DIVE_YAW * min(1.0, u * 3)
            st["y"] += 0.55 * math.sin(math.pi * min(u * 1.25, 1.0)) + 0.3 * ease(clampu(u, 0.6, 1.0))
            st["arms"][0] = REACH_ARM if u < 0.45 else [0.3, 2.6]; st["arms"][1] = [0.3, 2.6] if u > 0.45 else [0.5, 0.6]
            st["pitch"] = 2.6 * ease(clampu(u, 0.45, 1.0)); st["legs"] = [0.12, 0.12]
            if t >= T.LAND:                                 # buried head-first, legs kicking, tail wagging
                d = t - T.LAND
                st["x"], st["z"] = BURIED; st["yaw"] = DIVE_YAW; st["pitch"] = 2.6; st["y"] = 0.3
                st["sq"] = -0.12 * math.exp(-d * 6) * math.cos(d * 20)
                st["legs"] = [0.22 * max(0, math.sin(d * 11)), 0.22 * max(0, -math.sin(d * 11))]; st["tail"] = 0.9 * math.sin(d * 8)
    elif n == "sour_face":
        a = SH[n][0]; u = clampu(t, a, a + 0.7)              # pops out, then grumps: arms crossed, nose in the air
        st["x"], st["z"] = lerp(BURIED, POPPED, ease(u)); st["yaw"] = lerp(DIVE_YAW, -0.35, ease(u))
        st["pitch"] = 2.6 * (1 - ease(u)); st["y"] = 0.3 * (1 - ease(u)) + 0.35 * math.sin(math.pi * u)
        L = T.line("Problem A")
        cross = ease(clampu(t, L["t0"] - 0.3, L["t0"] + 0.2))
        st["arms"] = [lerp([0.3, 0.3, 0.0], CROSS0, cross).tolist(), lerp([0.3, 0.3, 0.0], CROSS1, cross).tolist()]
        st["head"][0] = -0.55 * cross; st["head"][1] = 0.35 * cross; st["yaw"] = lerp(st["yaw"], -0.12, cross)   # faces the camera, arms crossed, nose in the air
        if L["t0"] < t < L["t1"]: st["y"] += 0.02 * abs(math.sin((t - L["t0"]) * 7))
    elif n == "pip_idea":
        st["x"], st["z"] = POPPED; st["yaw"] = -0.35
        L = T.line("Problem B")
        un = ease(clampu(t, L["t0"], L["t0"] + 0.6))         # uncrosses his arms, turns to Pip, nods
        st["arms"] = [lerp(CROSS0, [0.3, 0.3, 0.0], un).tolist(), lerp(CROSS1, [0.3, 0.3, 0.0], un).tolist()]
        st["head"][1] = lerp(0.5, -0.35, un); st["head"][0] = lerp(-0.35, 0.0, un); st["yaw"] = -0.35 - 0.25 * (1 - un)
        if t > L["t1"]: st["head"][0] = 0.22 * math.sin((t - L["t1"]) * 8) * math.exp(-(t - L["t1"]) * 1.5)   # a big nod
    elif n == "climb":
        a = SH[n][0]
        base = (STUMP[0] - 1.05, STUMP[1] + 0.55)           # clear of the roots
        if t < a + 1.5:
            walk_to(st, t, POPPED, base, a, a + 1.5)
        else:                                               # hops up onto the stump
            u = clampu(t, a + 1.5, a + 2.1)
            st["x"], st["z"] = lerp(base, STUMP, ease(u)); st["stand_h"] = STUMP_TOP * ease(min(1.0, u * 1.8))   # up first, then over
            st["y"] += 0.3 * math.sin(math.pi * u); st["yaw"] = lerp(math.atan2(STUMP[0] - base[0], STUMP[1] - base[1]), -0.4, ease(u))
            st["arms"] = [[1.8, 0.6], [1.8, 0.6]]               # arms up and out for balance, clear of the stump
            if u >= 1: st["head"][0] = -0.35; st["arms"] = [[0.4, 1.9], [0.4, 1.9]]
    elif n in ("ready", "tug", "catch"):
        st["x"], st["z"] = STUMP; st["stand_h"] = STUMP_TOP; st["yaw"] = -0.4; st["head"][0] = -0.35
        st["arms"] = [list(CATCH), list(CATCH)]             # both paws together in front, ready to catch
        if t > T.CATCH:                                     # caught! a happy squish and wiggle
            d = t - T.CATCH
            st["head"][0] = -0.05; st["sq"] -= 0.08 * math.exp(-d * 7) * math.cos(d * 20)
            st["y"] += 0.05 * abs(math.sin(d * 9)) * math.exp(-d * 1.2)
    elif n in ("moral", "chorus"):
        st["x"], st["z"] = MSPOT
        dance_tumble(st, t, n)
        sway = math.sin(2 * math.pi * (t - SH["chorus"][0]) / (2 * BEAT)) if n == "chorus" else 0.0
        st["arms"][1] = [0.45, 0.95 + 0.12 * sway]           # the apple in his other paw
        if n == "chorus":
            st["y"] += 0.045 * abs(math.sin(math.pi * (t - SH["chorus"][0]) / BEAT)) * (1.0 if t < T.HIGH_FIVE + 0.5 else 0.0)   # bounces on the beat
            st["yaw"] += 0.12 * sway; st["head"][1] = 0.12 * sway
            g = T.GAG_SWEET
            if g - 0.5 < t < g + 1.3:                        # the first crunchy bite: apple up to his mouth, chewing, happy wiggle
                k = ease(clampu(t, g - 0.5, g - 0.1)) * (1 - ease(clampu(t, g + 0.9, g + 1.3)))
                st["arms"][1] = lerp(np.array([0.45, 0.95, 0.0]), np.array(BITE), k).tolist()
                st["roll"] += 0.06 * math.sin((t - g) * 12) * k; st["head"][0] = 0.12 * math.sin((t - g) * 14) * k
                st["y"] += 0.03 * abs(math.sin((t - g) * 10)) * k
    else:                                                   # button: holds the apple out; Pip pecks a bite
        a = SH["button_crane"][0]; st["x"], st["z"] = MSPOT; st["yaw"] = -0.05
        down = ease(clampu(t, a + 0.45, a + 0.85))           # keeps the dance paw up until Pip has hopped off it
        st["arms"] = [lerp(DANCE_ARM, [0.3, 0.3], down).tolist(), [0.45, 1.1]]
        w = clampu(t, a + 0.6, a + 0.8) * (1.0 if t < a + 2.3 else 0.0)   # a goodbye wave with the free paw on "Bye-bye!"
        if w > 0: st["arms"][0] = [1.9 + 0.35 * math.sin((t - a) * 14), 0.3 * w + 0.3 * (1 - w)]
        st["head"][1] = -0.25 * down; st["head"][0] = 0.05 * down; st["head"][2] = 0.1 * (1 - down)
        st["y"] += 0.03 * abs(math.sin(t * 9)) * clampu(t, SH["button_crane"][0] + 1.0, SH["button_crane"][0] + 1.2)
    return st

def fox_mats_p(st):
    """fox_mats plus a forward pitch about the middle of the body (the dive into the leaf pile)"""
    R, Mh, arms, legs = fox_mats(st)
    p = st.get("pitch", 0.0)
    if p == 0.0: return R, Mh, arms, legs
    root = trans(st["x"], surf(st["x"], st["z"]) + st.get("stand_h", 0.0) - 0.01 + st["y"], st["z"]) @ roty(st["yaw"])
    P = root @ trans(0, 0.8, 0) @ rotx(p) @ trans(0, -0.8, 0) @ np.linalg.inv(root)
    return P @ R, P @ Mh, [P @ a for a in arms], [P @ l for l in legs]

# ---------------- the apple ----------------
def apple_state(t, mats):
    """apple position; None while it hangs (drawn on its stem)"""
    if t < T.RELEASE:
        return "hang", tug_pull(t)
    arms = mats[2]
    if t < T.CATCH:                                         # drops into Tumble's paws on the stump
        u = clampu(t, T.RELEASE, T.CATCH)
        st_c = tumble(T.CATCH + 0.01); m_c = fox_mats_p(st_c)
        dest = (hand_pos(m_c[2], 0) + hand_pos(m_c[2], 1)) / 2 + np.array([0, 0.1, 0])
        p = lerp(A, dest, u); p[1] += 0.4 * math.sin(math.pi * u) * (1 - u)
        return "fall", p
    n = T.shot_at(t)[1]
    if n == "catch":
        return "held2", (hand_pos(arms, 0) + hand_pos(arms, 1)) / 2 + np.array([0, 0.1, 0])
    return "held1", hand_pos(arms, 1) + np.array([0, 0.1 + APPLE_BOT - 0.01, 0])

def tug_pull(t):
    """how far Pip has the apple pulled out on its stem (the apple follows his beak, so they stay attached)"""
    back = 0.0
    for k, tg in enumerate(T.TUGS):
        d = t - tg
        if 0 <= d < 0.4: back = max(back, (0.12 + 0.04 * k) * math.sin(math.pi * d / 0.4))
    s0 = T.TUGS[-1] + 0.5                                   # "here it comes": one long strain until the stem lets go
    if s0 < t < T.RELEASE: back = max(back, 0.2 * ease(clampu(t, s0, T.RELEASE - 0.05)) + 0.02 * math.sin(t * 30))
    return back

# ---------------- Pip ----------------
OUT = np.array([A[0] - TREE[0], A[2] - TREE[1]]); OUT /= np.linalg.norm(OUT)    # away from the tree's middle (higher canopy)
TUG_YAW = math.atan2(-OUT[0], -OUT[1])                    # Pip faces back in towards the apple
def tug_body(back):
    """Pip's position when his beak grips the outer side of the apple, below the leaves; back pulls him outward"""
    beak = A + np.array([OUT[0] * 0.17, -0.15, OUT[1] * 0.17])
    fwd = np.array([-OUT[0], 0, -OUT[1]])
    return beak - fwd * (0.27 * 1.1 + back) - np.array([0, 0.31 * 1.1 + back * 0.4, 0])
def leg_path(pts, u):
    """straight legs through pts at constant speed; u in 0..1 (eased). Returns position and heading yaw"""
    pts = [np.asarray(p, float) for p in pts]; seg = [np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])]
    def at(x):
        d = clampu(x, 0, 1) * sum(seg)
        for (a, b), l in zip(zip(pts, pts[1:]), seg):
            if d <= l: return a + (b - a) * (d / max(l, 1e-9))
            d -= l
        return pts[-1]
    e = ease(u); p = at(e); q = at(min(1.0, e + 0.03)) - at(max(0.0, e - 0.03))
    return p, math.atan2(q[0], q[2])
BEHIND = STUMP[1] - 0.95                                    # flights past the stump keep a body-width behind him, above his ears
W0 = np.array([STUMP[0] + 0.9, 2.95, BEHIND])               # waiting point, behind-right of the stump
SIDE2 = np.array([STUMP[0] + 0.5, 3.0, BEHIND - 0.15])      # cheer point after the catch
def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    R, Mh, arms, legs = mats
    face = apply(Mh, (0, 1.5, 0.6))
    to_tumble = math.atan2(st["x"] - STUMP_PIP[0], st["z"] - STUMP_PIP[2])
    stem_pt = A + np.array([0, APPLE_TOP + 0.04, 0])
    tug_spot = tug_body(0.0)
    if n in ("hook_reach", "title_wide", "jumps", "big_jump", "leaf_pile"):
        ex = {}
        if n == "leaf_pile" and t > T.LAND: ex = {"cheer": False, "point": False}
        return STUMP_PIP, to_tumble, False, 0.0, True, ex
    if n == "sour_face":
        a = SH[n][0]; L = T.line("Problem A")
        hov = apply(Mh, (0.62, 1.5, 0.55)) + np.array([0, 0.05 * math.sin(t * 6), 0])
        u = clampu(t, L["t1"] - 0.2, L["t1"] + 0.9)
        if u <= 0: return STUMP_PIP, to_tumble, False, 0.0, True, {}
        p = lerp(STUMP_PIP, hov, ease(u)); p[1] += 0.4 * math.sin(math.pi * u)
        return p, math.atan2(face[0] - p[0], face[2] - p[2]), True, 0.0, False, {}
    if n == "pip_idea":
        hov = apply(Mh, (0.62, 1.5, 0.55)) + np.array([0, 0.05 * math.sin(t * 6), 0])   # right at his face
        L = T.line("Problem B")
        ex = {"wings": (1.4 + 0.1 * math.sin(t * 10), 0.9 * math.sin(t * 28))} if L["t0"] < t < L["t1"] + 0.3 else {}
        return hov, math.atan2(face[0] - hov[0], face[2] - hov[2]), True, 0.0, False, ex
    if n == "climb":
        a = SH[n][0]; hov = apply(fox_mats_p(tumble(a - 0.01))[1], (0.62, 1.5, 0.55))
        u = clampu(t, a, a + 1.5)                           # straight up from his face, then across above him to the far side of the stump
        p, yw = leg_path([hov, hov + np.array([0, 0.9, 0]), W0], u)
        return p, yw if u < 1 else 0.0, True, 0.0, False, {"gentle": True}
    if n == "ready":
        a, b = SH[n]; u = clampu(t, a + 0.4, b - 0.15)      # waits behind the stump, then flies round behind him to the apple
        w1 = tug_spot + np.array([OUT[0] * 0.9, -0.05, -0.6])
        if u <= 0: return W0 + np.array([0, 0.05 * math.sin(t * 6), 0]), 0.0, True, 0.0, False, {"gentle": True}
        p, yw = leg_path([W0, w1, tug_spot], u)
        return p, (yw if u < 0.92 else math.atan2(stem_pt[0] - p[0], stem_pt[2] - p[2])), True, 0.0, False, {"gentle": True}
    if n == "tug":
        back = tug_pull(t) if t < T.RELEASE else 0.0
        pitch = -0.35 * min(back, 0.2) / 0.12
        p = tug_body(0.0) + np.array([OUT[0] * back, 0.0, OUT[1] * back])   # the apple moves with him: beak stays on it
        if t > T.RELEASE: p = p + np.array([OUT[0] * 0.25, -0.1, OUT[1] * 0.25]) * clampu(t, T.RELEASE, T.RELEASE + 0.3)
        return p, TUG_YAW, True, pitch, False, {"beak": t < T.RELEASE, "gentle": True}
    if n == "catch":
        a = SH[n][0]
        side = SIDE2 + np.array([0, 0.05 * math.sin(t * 6), 0])
        start = tug_spot + np.array([OUT[0] * 0.25, -0.1, OUT[1] * 0.25])
        u = clampu(t, a, a + 0.8); p, yw = leg_path([start, side], u)       # away from the leaves, round behind him
        ex = {"cheer": True} if t > T.GAG_SWEET else {}
        return p, (math.atan2(st["x"] - p[0], st["z"] - p[2]) if u >= 1 else yw), True, 0.0, False, ex
    if n in ("moral", "chorus"):
        return dance_pip(t, st, mats, n, arrive_from=SIDE2)
    a, b = SH["button_crane"]                               # hops from the paw onto the apple for a peck
    held = apple_state(t, mats)[1]
    top = held + np.array([0, APPLE_TOP, 0]) + UP
    p0 = paw_seat(fox_mats_p(tumble(a))[2])
    u = clampu(t, a, a + 0.7)
    if u < 1:
        p = lerp(p0, top, ease(u)); p[1] += 0.55 * math.sin(math.pi * u); p[2] += 0.5 * math.sin(math.pi * u)   # high arc in front of him, over to the apple paw
        return p, -0.6, True, 0.0, False, ({"wings": (0.15, 0.15)} if u < 0.3 else {"gentle": True})   # wings tucked as he hops off, clear of Tumble's cheek
    pk = 0.0
    for k in range(3):
        d = t - (a + 0.95 + 0.35 * k)
        if 0 <= d < 0.22: pk = 0.55 * math.sin(math.pi * d / 0.22)
    return top, 0.0, False, pk, True, {}

# ---------------- camera ----------------
def _tug_cam_yaw():
    """side-on-ish yaw for the tug close-up that keeps Tumble (standing on the stump) well away from the apple on
    screen: search yaws within 45 degrees of side-on and maximise the angle between apple and Tumble's head"""
    pb = tug_body(0.0) + np.array([0, 0.3, 0])
    head = np.array([STUMP[0], surf(*STUMP) + STUMP_TOP + 1.6, STUMP[1]])
    best = None
    for base in (side_on_yaw(pb, A, 90), side_on_yaw(pb, A, 90) + 180):
        for dy in range(-45, 50, 5):
            yw = base + dy
            eye, tgt, _ = fit_cam(lerp(A, pb, 0.45), yw, -4, 0.62, 0.62, fov=34, lift=0.1)
            v1, v2 = tgt - eye, head - eye
            if np.dot(v2, v1) < 0: sep = math.pi                      # Tumble behind the camera: ideal
            else: sep = math.acos(np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2))
            facing = abs(math.cos(math.radians(yw) - TUG_YAW))        # keep Pip's face side-on, not his back
            score = min(sep, 0.6) + 0.3 * (1 - facing)
            if best is None or score > best[0]: best = (score, yw)
    return best[1]
TUG_CAM_YAW = _tug_cam_yaw()
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    st = tumble(t)
    if name == "hook_reach":                                # low angle, looking up past him at the apple
        return fit_cam(np.array([SPOT[0] + 0.1, lerp(1.55, 1.7, e), SPOT[1]]), lerp(18, 10, e), -12, 0.95, 1.6, lift=0.06)
    if name == "title_wide":
        return fit_cam(np.array([0.7, 1.6, -1.0]), -6, 10, 2.9, 2.6 if not WIDE else 2.0, lift=0.05)
    if name == "jumps":                                     # medium side, apple at the top of frame
        return fit_cam(np.array([SPOT[0], 1.55, SPOT[1]]), 62, 4, 1.05, 1.9, lift=0.1)
    if name == "big_jump":                                  # wide, following the run and the leap
        cx = lerp(RUN0[0] + 1.0, PILE[0] - 0.4, e)
        return fit_cam(np.array([cx, 1.2, lerp(RUN0[1], PILE[1], e) - 0.2]), 6, 6, 2.1, 1.7)
    if name == "leaf_pile":                                 # close on the pile: legs and tail sticking out
        c = lerp(np.array([PILE[0] - 0.2, 0.95, PILE[1]]), np.array([PILE[0], 0.85, PILE[1]]), e)     # starts wide enough to keep him in as he comes down
        return fit_cam(c, lerp(30, 22, e), 12, lerp(1.9, 1.05, e), lerp(1.9, 1.25, e))
    if name == "sour_face":
        return fit_cam(np.array([POPPED[0] + 0.25, 1.35, POPPED[1]]), lerp(-14, -8, e), 5, 1.0, 1.25)
    if name == "pip_idea":                                  # two-shot, Pip at his face
        fc = apply(fox_mats_p(st)[1], (0.3, 1.5, 0.4))
        return fit_cam(fc, lerp(-14, -8, e), 4, 0.9, 0.95)
    if name == "climb":
        return fit_cam(np.array([lerp(POPPED[0], STUMP[0], 0.55), 1.4, (POPPED[1] + STUMP[1]) / 2 + 0.1]), -2, 8, 1.9, 1.7)
    if name == "tug":                                       # up in the tree with Pip and the apple
        pb = tug_body(0.0) + np.array([0, 0.3, 0])
        return fit_cam(lerp(A, pb, 0.55) - np.array([0, 0.05, 0]), TUG_CAM_YAW + lerp(-4, 4, e), -4, 0.72, 0.66, fov=34, lift=0.1)   # angle solved so Tumble stays out of line
    if name == "ready":                                     # tall frame on the stump: Tumble below, the apple at the top, Pip flying up
        return fit_cam(np.array([STUMP[0] - 0.3, 1.95, STUMP[1] - 0.2]), lerp(36, 42, e), -4, 2.2, 3.2)
    if name == "catch":                                     # tall enough to see the apple fall into his paws
        return fit_cam(np.array([STUMP[0] - 0.4, lerp(2.0, 1.8, e), STUMP[1] - 0.2]), lerp(42, 34, e), -4, lerp(2.2, 1.6, e), lerp(2.7, 2.2, e))
    if name == "moral":
        return fit_cam(np.array([MSPOT[0] + 0.25, lerp(1.35, 1.45, e), MSPOT[1]]), lerp(12, 6, e), 5, lerp(1.3, 1.1, e), lerp(1.4, 1.15, e))
    if name == "chorus":
        return fit_cam(np.array([MSPOT[0] + 0.25, 1.2, MSPOT[1]]), 6, 6, 1.35, 1.35)
    return fit_cam(np.array([MSPOT[0] - 0.1, lerp(1.25, 2.2, e), MSPOT[1]]), 4, lerp(4, 14, e), lerp(1.3, 2.2, e), lerp(1.4, 2.2, e), lift=0.04)

# ---------------- draws ----------------
def build_draws(t):
    draws, contacts = [], []
    meadow_backdrop(draws, t)
    draws.append((E2["appletree"], trans(TREE[0], ground_h(*TREE) - 0.05, TREE[1]) @ scale(TREE_S), U(mat=0, bump=0.8, obj="tree"), True))
    draws.append((E2["stump"], trans(STUMP[0], ground_h(*STUMP) - 0.02, STUMP[1]) @ roty(0.3), U(mat=0, bump=0.9, obj="stump"), True))
    for (x, z, s) in [(STUMP[0] + 0.8, STUMP[1] + 0.5, 0.2), (TREE[0] - 1.3, TREE[1] + 0.9, 0.16), (MSPOT[0] - 1.4, MSPOT[1] + 0.3, 0.18)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))
    draw_flowers(draws, t, FLOWERS)
    n = T.shot_at(t)[1]
    burst = clampu(t, T.LAND - 0.05, T.LAND + 0.6) if t < SH["sour_face"][1] else 1.0
    for k, (off, rot, s, tint) in enumerate(PILE_LEAVES):     # the pile; leaves fly up when he lands, settle again
        fly = 0.0
        if 0 < burst < 1 and k % 3 == 0: fly = math.sin(math.pi * burst) * (0.4 + 0.5 * (k % 5) / 5)
        p = np.array([PILE[0] + off[0] * (1 + 0.6 * fly), surf(PILE[0] + off[0], PILE[1] + off[2]) + off[1] + fly, PILE[1] + off[2] * (1 + 0.6 * fly)])
        draws.append((SC["leaf"], trans(*p) @ rotx(rot[0] + 3 * fly) @ roty(rot[1]) @ rotz(rot[2] * 0.3) @ scale(s), U(mat=0, bump=0.0, tint=tint, tintMix=1.0), False))
    st = tumble(t); mats = fox_mats_p(st); R, Mh, arms, legs = mats
    draw_tumble(draws, contacts, t, st, mats)
    if n == "sour_face":                                    # leaves stuck on his head after the dive (gone at the next cut)
        for (c, rz) in [((0.12, 2.0, 0.05), 0.6), ((-0.2, 1.93, 0.15), -0.8)]:
            draws.append((SC["leaf"], Mh @ trans(*c) @ rotz(rz) @ scale(2.6), U(mat=0, bump=0.0, tint=(0.95, 0.6, 0.25), tintMix=1.0), False))
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, arms)
    # apple + stem
    kind, val = apple_state(t, mats)
    stem_top = A + np.array([0, APPLE_TOP + 0.16, 0])
    if kind == "hang":
        back = val; ang = back / (APPLE_TOP + 0.16)            # swings out on its stem towards Pip
        Mpiv = trans(*stem_top) @ rotz(-OUT[0] * ang) @ rotx(OUT[1] * ang) @ trans(*(-stem_top))
        Ma = Mpiv @ trans(*A) @ scale(APPLE_S)
        draws.append((PR["stick"], Mpiv @ trans(*(A + np.array([0, APPLE_TOP - 0.03, 0]))) @ scale(0.25, 0.2, 0.25), U(mat=0, bump=0.0, tint=(0.48, 0.32, 0.2), tintMix=1.0), False))
    else:
        Ma = trans(*val) @ roty(t * 0.5 if kind == "fall" else 0.0) @ scale(APPLE_S)
        draws.append((PR["stick"], trans(*stem_top) @ trans(0, -0.2, 0) @ scale(0.25, 0.2, 0.25), U(mat=0, bump=0.0, tint=(0.48, 0.32, 0.2), tintMix=1.0), False))
    draws.append((E2["apple"], Ma, U(mat=0, bump=0.5, obj="apple"), True))
    if kind != "hang" and T.GAG_SWEET - 0.1 < t < T.GAG_SWEET + 0.6:
        puff(draws, val + np.array([0, 0.1, 0.25]), T.GAG_SWEET - 0.05, t, n=8, size=0.04, spread=0.6, dur=0.4, tint=(1.0, 0.96, 0.85))
    puff(draws, np.array([PILE[0], 0.5, PILE[1]]), T.LAND, t, n=12, size=0.07, spread=1.2, dur=0.5, tint=(0.95, 0.7, 0.35), axis=(0, 0.8, 0.3))
    return draws, contacts

HOOKS.update(build=build_draws, camera=camera, tumble=tumble,
             ground_objs=lambda t: ("pip",) if T.shot_at(t)[1] in ("big_jump", "leaf_pile", "sour_face") else ("fox", "pip"),
             qa_ignore={("apple", "fox"), ("fox", "apple"), ("apple", "tree"), ("tree", "apple")})   # held apple; apple top tucked into the leaves
if __name__ == "__main__":
    main()
