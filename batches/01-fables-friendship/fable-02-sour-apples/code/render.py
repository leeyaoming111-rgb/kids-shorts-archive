"""Tumble & Pip Fables 2: Sour Apples!  (Aesop: The Fox and the Grapes)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa"""
from fablekit import *

# ---------------- world: under the big apple tree (a new corner of Picnic Meadow) ----------------
TREE = (-0.9, -1.7); TREE_S = 2.2
APPLE_S = 0.5
A = np.array([TREE[0] + 1.03, 2.85, TREE[1] + 0.78])     # the red apple under the canopy (underside ~3.05): just above his jumping ears
APPLE_TOP = 0.61 * APPLE_S; APPLE_BOT = 0.41 * APPLE_S
SPOT0 = (A[0] - 0.05, A[2] + 0.12)
STUMP = (SPOT0[0] + 1.95, SPOT0[1] - 0.95); STUMP_TOP = 0.55 - 0.02     # back-right, clear of him and the tree
PILE = (SPOT0[0] + 1.62, SPOT0[1] + 0.6)                  # autumn leaf pile, front-right
MSPOT = (SPOT0[0] + 0.2, SPOT0[1] + 1.0)                  # where they do the moral and the dance (clear of the pile, tail included)
REACH_ARM = [2.0, 0.3]                                     # paw up and out: a reach that reads from the front (paw at 1.22)
CROSS0, CROSS1 = [0.1, 1.5, 1.3], [0.1, 1.35, 1.3]         # arms crossed in front of his chest (inward swing)
CATCH = [0.8, 0.3]                                         # paws out at his sides, palms up; the apple lands in his right paw (screen left).
                                                           # His arms are too short to hold it in front without the apple hitting his chin or tummy
HOLD_ARM = [0.75, 0.1, 0.12]                                 # moral and chorus: apple paw [side, fwd] + beat lift (fwd added on the beat)
BITE = [0.0, 1.0, 0.0]                                     # apple paw up beside his muzzle: a side chomp (solved against the head SDF)
BITE_HEAD = (0.25, -0.5)                                   # head pitch (nose down) and yaw (to his right, to the apple) for the bite
HELD1_DY, HELD2_DY = 0.325, 0.26                           # apple centre above the paw (one paw / between two paws): resting, not sunk in
def _reach_offset():
    st = tumble_base(0.0); st["arms"][0] = REACH_ARM; st["yaw"] = 0.0
    return hand_pos(fox_mats(st)[2])
_ho = _reach_offset()
SPOT = (A[0] - 0.05, A[2] + 0.12)                         # right under the apple
RUN0 = (SPOT[0] - 2.3, SPOT[1] + 0.9)                     # run-up starts front-left, clear of the trunk
DIVE_DIR = np.array([PILE[0] - SPOT[0], PILE[1] - SPOT[1]]); DIVE_DIR /= np.linalg.norm(DIVE_DIR)
DIVE_YAW = math.atan2(DIVE_DIR[0], DIVE_DIR[1])
BURIED = (PILE[0] - DIVE_DIR[0] * 0.35, PILE[1] - DIVE_DIR[1] * 0.35)
POPPED = (PILE[0] - DIVE_DIR[0] * 1.45, PILE[1] - DIVE_DIR[1] * 1.45 + 0.25)  # outside the pile's leaves
OUT = np.array([A[0] - TREE[0], A[2] - TREE[1]]); OUT /= np.linalg.norm(OUT)    # away from the tree's middle (higher canopy)
A_OUT = math.atan2(-OUT[1], OUT[0])                       # apple yaw that points its stalk outwards, towards Pip
STUMP_PIP = np.array([STUMP[0] + 0.25, surf(*STUMP) + STUMP_TOP, STUMP[1] + 0.25]) + UP
FLOWERS = make_flowers([(TREE[0], TREE[1], 2.0), (STUMP[0], STUMP[1], 1.3), (PILE[0], PILE[1], 2.6), (SPOT[0], SPOT[1], 1.2),
                        (MSPOT[0], MSPOT[1], 1.5), (STUMP[0] + 0.95, STUMP[1] + 0.45, 0.8), ("box", RUN0[0] - 0.6, SPOT[0] + 0.3, RUN0[1] - 0.7, RUN0[1] + 0.6),
                        ("box", SPOT[0] - 0.3, PILE[0] + 0.5, SPOT[1] - 0.6, PILE[1] + 0.6)], seed=37)
_rng = np.random.default_rng(5)
PILE_LEAVES = []                                          # (offset, rotation angles, scale, tint)
for k in range(70):
    r = 0.75 * math.sqrt(_rng.uniform(0, 1)); a = _rng.uniform(0, 6.28)
    h = 0.42 * (1 - (r / 0.8) ** 2) * _rng.uniform(0.55, 1.0)
    tint = [(0.95, 0.62, 0.25), (0.92, 0.42, 0.25), (0.98, 0.8, 0.3), (0.75, 0.45, 0.22)][k % 4]
    sc_ = _rng.uniform(2.6, 3.4) * (0.72 if r > 0.5 else 1.0)          # smaller leaves round the rim keep the pile's footprint tidy
    if math.hypot(PILE[0] + r * math.cos(a) - STUMP[0], PILE[1] + r * math.sin(a) - STUMP[1]) < 1.12: continue   # none against the stump
    PILE_LEAVES.append(((r * math.cos(a), h, r * math.sin(a)), _rng.uniform(0, 6.28, 3), sc_, tint))

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
            st["yaw"] = RUN_YAW                             # heading set from the first frame (no one-frame flip)
        else:                                               # leap: just misses the apple, then dives into the leaves
            u = clampu(t, T.LEAP, T.LAND)
            st["x"], st["z"] = lerp(SPOT, BURIED, u); st["yaw"] = lerp(RUN_YAW, DIVE_YAW, ease(min(1.0, u * 3)))
            st["y"] += 0.55 * math.sin(math.pi * min(u * 1.25, 1.0)) + 0.3 * ease(clampu(u, 0.6, 1.0))
            st["arms"][0] = REACH_ARM if u < 0.45 else [0.3, 2.6]; st["arms"][1] = [0.3, 2.6] if u > 0.45 else [0.5, 0.6]
            st["pitch"] = 2.6 * ease(clampu(u, 0.45, 1.0)); st["legs"] = [0.12, 0.12]
            if t >= T.LAND:                                 # buried head-first, legs kicking, tail wagging
                d = t - T.LAND
                st["x"], st["z"] = BURIED; st["yaw"] = DIVE_YAW; st["pitch"] = 2.6; st["y"] = 0.3
                st["sq"] = -0.12 * math.exp(-d * 6) * math.cos(d * 20)
                st["legs"] = [0.22 * max(0, math.sin(d * 11)), 0.22 * max(0, -math.sin(d * 11))]; st["tail"] = 0.9 * math.sin(d * 8)
            if t >= T.POP_OUT: pop_out(st, t)               # pops out backwards at the end of the leaf-pile shot
    elif n == "sour_face":
        st["x"], st["z"] = POPPED; st["yaw"] = SULK_YAW       # already out of the pile: grumps, arms crossed, nose in the air
        L = T.line("Problem A")
        cross = ease(clampu(t, L["t0"] - 0.3, L["t0"] + 0.2))
        st["arms"] = [lerp([0.3, 0.3, 0.0], CROSS0, cross).tolist(), lerp([0.3, 0.3, 0.0], CROSS1, cross).tolist()]
        st["head"][0] = -0.4 * cross; st["head"][1] = -0.35 * cross   # nose up and turned away from Pip (who arrives on the other side)
        if L["t0"] < t < L["t1"]: st["y"] += 0.02 * abs(math.sin((t - L["t0"]) * 7))
    elif n == "pip_idea":
        st["x"], st["z"] = POPPED
        L = T.line("Problem B")
        un = ease(clampu(t, L["t0"], L["t0"] + 0.6))         # uncrosses his arms, turns to Pip (screen right), nods
        st["arms"] = [lerp(CROSS0, [0.3, 0.3, 0.0], un).tolist(), lerp(CROSS1, [0.3, 0.3, 0.0], un).tolist()]
        st["head"][1] = lerp(-0.35, 0.45, un); st["head"][0] = lerp(-0.4, 0.0, un); st["yaw"] = lerp(SULK_YAW, 0.1, un)
        tn = L["t0"] + 1.9
        if t > tn: st["head"][0] = 0.22 * math.sin((t - tn) * 8) * math.exp(-(t - tn) * 1.5)   # a big nod on "you and me"
    elif n == "climb":
        a = SH[n][0]
        base = (STUMP[0] - 1.25, STUMP[1] + 0.45)           # clear of the roots and of the leaf pile
        if t < a + 1.3:
            walk_to(st, t, POPPED, base, a, a + 1.3); st["yaw"] = math.atan2(base[0] - POPPED[0], base[1] - POPPED[1])
        else:                                               # hops up onto the stump
            u = clampu(t, a + 1.3, a + 1.9)
            st["x"], st["z"] = lerp(base, STUMP, ease(u)); st["stand_h"] = STUMP_TOP * ease(min(1.0, u * 1.8))   # up first, then over
            st["y"] += 0.3 * math.sin(math.pi * u); st["yaw"] = lerp(math.atan2(STUMP[0] - base[0], STUMP[1] - base[1]), -0.4, ease(u))
            st["arms"] = [[1.8, 0.6], [1.8, 0.6]]               # arms up and out for balance, clear of the stump
            if u >= 1: st["head"][0] = -0.35; st["arms"] = [[0.4, 1.9], [0.4, 1.9]]
    elif n in ("ready", "tug", "catch"):
        st["x"], st["z"] = STUMP; st["stand_h"] = STUMP_TOP; st["yaw"] = -0.4; st["head"][0] = -0.35
        st["arms"] = [list(CATCH), list(CATCH)]             # paws out at his sides, ready to catch
        if n == "tug": st["arms"] = [[0.3, 0.3], [0.3, 0.3]]   # paws down while we are up in the tree (his paw stays out of that frame)
        st["yaw"] = lerp(-0.4, CATCH_TURN, ease(clampu(t, T.RELEASE + 0.05, T.CATCH)))   # turns to us as it falls, so it lands at his side
        if t > T.CATCH:                                     # caught! a happy squish and wiggle
            d = t - T.CATCH
            st["head"][0] = -0.05; st["sq"] -= 0.08 * math.exp(-d * 7) * math.cos(d * 20)
            st["y"] += 0.05 * abs(math.sin(d * 9)) * math.exp(-d * 1.2)
        u = clampu(t, HOP_DOWN, HOP_DOWN + 0.6)              # hops down off the stump with the apple, before the moral
        if u > 0:
            st["x"], st["z"] = lerp(STUMP, DOWNPT, ease(u)); st["stand_h"] = STUMP_TOP * (1 - ease(clampu(u, 0.5, 1.0)))
            st["y"] += 0.28 * math.sin(math.pi * u); st["yaw"] = lerp(CATCH_TURN, 0.15, ease(min(1.0, u * 2)))   # turns side-on to the hop so his tail swings clear
    elif n in ("moral", "chorus"):
        st["x"], st["z"] = MSPOT
        dance_tumble(st, t, n)
        sway = math.sin(2 * math.pi * (t - SH["chorus"][0]) / (2 * BEAT)) if n == "chorus" else 0.0
        st["arms"][1] = [HOLD_ARM[0] + 0.1 * sway, HOLD_ARM[1] + HOLD_ARM[2] * abs(sway) * (1.0 if n == "chorus" else 0.3)]   # the apple in his other paw: lifted in time with the beat, clear of his face
        if n == "chorus":
            st["y"] += 0.045 * abs(math.sin(math.pi * (t - SH["chorus"][0]) / BEAT)) * (1.0 if t < T.HIGH_FIVE + 0.5 else 0.0)   # bounces on the beat
            calm = 1 - ease(clampu(t, T.HIGH_FIVE - 0.9, T.HIGH_FIVE - 0.5)) * (1 - ease(clampu(t, T.HIGH_FIVE + 0.3, T.HIGH_FIVE + 0.7)))
            st["yaw"] += 0.12 * sway * calm; st["head"][1] = 0.12 * sway * calm   # holds still for the high-five so Pip's hop stays clear of his ear
            k = bite_k(t)
            if k > 0:                                       # the first crunchy bite: apple up beside his muzzle, a side chomp, chewing
                g = T.GAG_SWEET
                st["arms"][1] = lerp(np.array(st["arms"][1] + [0.0]), np.array(BITE), k).tolist()
                st["roll"] *= (1 - k); st["yaw"] = lerp(st["yaw"], -0.05, k); st["head"][2] *= (1 - k)
                chew = 0.06 * max(0.0, math.sin((t - g) * 14)) * clampu(t, g - 0.1, g + 0.1)
                st["head"][0] = (BITE_HEAD[0] - chew) * k; st["head"][1] = BITE_HEAD[1] * k
    else:                                                   # button: holds the apple out at his side; Pip flies round low and pecks it
        a = SH["button_crane"][0]; st["x"], st["z"] = MSPOT; st["yaw"] = -0.05
        down = ease(clampu(t, a + 0.45, a + 0.85))           # keeps the dance paw up until Pip has flown off it
        out = ease(clampu(t, a, a + 0.8))                    # the apple paw goes out to the side, clear of his head
        st["arms"] = [lerp(DANCE_ARM, [0.3, 0.3], down).tolist(), lerp(HOLD_ARM[:2], APPLE_OUT_ARM, out).tolist()]
        by = T.SPOKEN[-1]["t0"]
        w = clampu(t, by - 0.3, by) * (1 - clampu(t, by + 1.0, by + 1.3))   # a goodbye wave with the free paw on "Bye-bye!"
        if w > 0: st["arms"][0] = lerp([0.3, 0.3], [1.9 + 0.3 * math.sin((t - by) * 13), 0.3], w).tolist()
        st["head"][1] = -0.25 * down; st["head"][0] = 0.05 * down; st["head"][2] = 0.1 * (1 - down)
        st["y"] += 0.025 * abs(math.sin((t - by) * 9)) * w
    return st

RUN_YAW = math.atan2(SPOT[0] - RUN0[0], SPOT[1] - RUN0[1])
SULK_YAW = -0.12
DOWNPT = (STUMP[0] + 0.95, STUMP[1] + 0.45)                 # where he hops down off the stump (the side away from the leaf pile, so the pile never hides him)
HOP_DOWN = SH["catch"][1] - 1.05
CATCH_TURN = 0.45
APPLE_OUT_ARM = [1.3, 0.0]                                  # button: apple paw out at his side (paw about 0.78 out)
def bite_k(t):
    g = T.GAG_SWEET
    return ease(clampu(t, g - 0.5, g - 0.1)) * (1 - ease(clampu(t, g + 0.9, g + 1.3))) if SH["chorus"][0] < t < SH["chorus"][1] else 0.0
def pop_out(st, t):
    """out of the pile backwards, turning upright to face the camera (end of the leaf-pile shot)"""
    u = clampu(t, T.POP_OUT, T.POP_OUT + 0.7); e = ease(u)
    st["x"], st["z"] = lerp(BURIED, POPPED, e); st["yaw"] = lerp(DIVE_YAW, SULK_YAW, e)
    st["pitch"] = 2.6 * (1 - e); st["y"] = 0.3 * (1 - e) + 0.35 * math.sin(math.pi * u)
    st["legs"] = [0.1, 0.1] if u < 1 else [0.0, 0.0]; st["sq"] = 0.015 * math.sin(t * 3.7) - (0.08 * math.exp(-(t - T.POP_OUT - 0.7) * 8) if u >= 1 else 0.0)
    st["arms"] = [[0.6, 0.6], [0.6, 0.6]] if u < 1 else [[0.3, 0.3, 0.0], [0.3, 0.3, 0.0]]
_kit_draw_pip = draw_pip
def draw_pip(draws, contacts, t, pip, arms=None):
    """kit draw, with Pip's singing mouth made a thin dark opening tucked under the beak base: the kit's red ball
    read as a berry in his beak in side views"""
    n0 = len(draws); Mp = _kit_draw_pip(draws, contacts, t, pip, arms)
    mp_ = mouth_at("pip", t)
    for i in range(n0, len(draws)):
        if draws[i][0] is PR["mouth"]:
            draws[i] = (PR["mouth"], Mp @ trans(0, 0.3, 0.2) @ scale(0.026, 0.006 + 0.014 * mp_, 0.014),
                        U(mat=0, bump=0.0, tint=(0.33, 0.1, 0.14), tintMix=1.0), False)
    return Mp
_kit_draw_tumble = draw_tumble
def draw_tumble(draws, contacts, t, st, mats):
    """kit draw, with the singing mouth sunk flatter into the muzzle when his head is turned and tipped (sulk, bite):
    from those angles the kit's glossy lozenge stands proud of the face"""
    n0 = len(draws); _kit_draw_tumble(draws, contacts, t, st, mats)
    n = T.shot_at(t)[1]
    if n == "sour_face" or bite_k(t) > 0:
        mo = mouth_at("tumble", t)
        for i in range(n0, len(draws)):
            if draws[i][0] is PR["mouth"]:
                M = mats[1] @ trans(*(np.array(FOXD["mouth"]["c"]) + np.array([0, -0.02, 0.0]))) @ scale(0.085, 0.028 + 0.042 * mo, 0.04)
                draws[i] = (PR["mouth"], M, U(mat=0, bump=0.0, tint=(0.5, 0.13, 0.2), tintMix=1.0), False)
def fox_mats_p(st):
    """fox_mats plus a forward pitch about the middle of the body (the dive into the leaf pile)"""
    R, Mh, arms, legs = fox_mats(st)
    p = st.get("pitch", 0.0)
    if p == 0.0: return R, Mh, arms, legs
    root = trans(st["x"], surf(st["x"], st["z"]) + st.get("stand_h", 0.0) - 0.01 + st["y"], st["z"]) @ roty(st["yaw"])
    P = root @ trans(0, 0.8, 0) @ rotx(p) @ trans(0, -0.8, 0) @ np.linalg.inv(root)
    return P @ R, P @ Mh, [P @ a for a in arms], [P @ l for l in legs]

# ---------------- the apple ----------------
# The apple has a short side stalk with a leaf (TWIG_DL, in apple-local units before APPLE_S). Pip grips the stalk's
# end in his beak for the tug; the apple swings out on its stem towards him, so beak, stalk and apple stay joined.
STEM_TOP = A + np.array([0, APPLE_TOP + 0.16, 0])
TWIG_EL = -0.35
TWIG_DL = np.array([math.cos(TWIG_EL), math.sin(TWIG_EL), 0.0])
TWIG_R0, TWIG_R1 = 0.40, 0.66
HELD_STALK = (-0.5, -0.87)                                   # held: stalk to his right and back (body frame x, z), away from the camera
def held_yaw(body_yaw):
    """apple yaw that points the stalk back and out to his side when he holds it (not onto the apple's front)"""
    dx, dz = HELD_STALK
    wx = dx * math.cos(body_yaw) + dz * math.sin(body_yaw); wz = -dx * math.sin(body_yaw) + dz * math.cos(body_yaw)
    return math.atan2(-wz, wx)
def tug_pull(t):
    """how far Pip has the apple pulled out on its stem"""
    back = 0.0
    for k, tg in enumerate(T.TUGS):
        d = t - tg
        if 0 <= d < 0.4: back = max(back, (0.2 + 0.04 * k) * math.sin(math.pi * d / 0.4))
    s0 = T.TUGS[-1] + 0.5                                   # "here it comes": one long strain until the stem lets go
    if s0 < t < T.RELEASE: back = max(back, 0.27 * ease(clampu(t, s0, T.RELEASE - 0.05)) + 0.02 * math.sin(t * 30))
    return back
def hang_mat(back):
    """apple matrix while it hangs: swung out on its stem (pivot above it, in the leaves) by back towards Pip"""
    ang = back / (APPLE_TOP + 0.16)
    Mpiv = trans(*STEM_TOP) @ rotz(OUT[0] * ang) @ rotx(-OUT[1] * ang) @ trans(*(-STEM_TOP))
    return Mpiv, Mpiv @ trans(*A) @ roty(A_OUT) @ scale(APPLE_S)
def apple_state(t, mats):
    """(kind, centre, matrix). kind: hang, fall, held1 (resting on his right paw)"""
    if t < T.RELEASE:
        Mpiv, Ma = hang_mat(tug_pull(t))
        return "hang", Ma[:3, 3].copy(), Ma
    arms = mats[2]
    if t < T.CATCH:                                         # drops into Tumble's paws on the stump
        u = clampu(t, T.RELEASE, T.CATCH)
        m_c = fox_mats_p(tumble(T.CATCH + 0.01))
        dest = hand_pos(m_c[2], 1) + np.array([0, HELD1_DY, 0])
        p0 = hang_mat(tug_pull(T.RELEASE - 1e-3))[1][:3, 3]
        p = lerp(p0, dest, u); p[1] += 0.4 * math.sin(math.pi * u) * (1 - u)
        yw = lerp(A_OUT, A_OUT + _wrap(held_yaw(-0.4) - A_OUT), ease(u))
        return "fall", p, trans(*p) @ roty(yw) @ scale(APPLE_S)
    by = tumble(t)["yaw"]
    p = hand_pos(arms, 1) + np.array([0, HELD1_DY + 0.04 * math.sin(math.pi * bite_k(t)), 0])   # sits a touch higher while the paw turns to and from the bite
    return "held1", p, trans(*p) @ roty(held_yaw(by)) @ scale(APPLE_S)
def _wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi

# ---------------- Pip ----------------
TUG_YAW = math.atan2(-OUT[0], -OUT[1])                    # Pip faces back in towards the apple
BEAK_L = np.array([0, 0.31, 0.27]) * 1.1                    # beak tip in Pip's frame
def twig_tip(Ma): return apply(Ma, TWIG_DL * TWIG_R1)
def tug_body(back, pitch=0.0):
    """Pip's position with his beak tip on the end of the apple's stalk (the apple swung out by back)"""
    tip = twig_tip(hang_mat(back)[1])
    d = tip - apply(hang_mat(back)[1], TWIG_DL * TWIG_R0); d /= np.linalg.norm(d)
    return tip + d * 0.012 - apply(roty(TUG_YAW) @ rotx(pitch), BEAK_L)
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
PECK_YAW = math.radians(90)                                 # button: Pip faces in towards the apple from its outer side
BEHIND = STUMP[1] - 0.95                                    # flights past the stump keep a body-width behind him, above his ears
W0 = np.array([STUMP[0] + 0.9, 2.95, BEHIND])               # waiting point, behind-right of the stump
PIP_LIFT = np.array([0.5, 0.3, 0.1])
HOVER_YAW = math.radians(-10)                               # the two-shot camera's direction (Pip's offset is set from it)
_hr, _ht = np.array([math.cos(HOVER_YAW), 0, -math.sin(HOVER_YAW)]), np.array([math.sin(HOVER_YAW), 0, math.cos(HOVER_YAW)])
HEAD_C = np.array([POPPED[0], surf(*POPPED) + 1.55, POPPED[1] + 0.05])
HOVER = HEAD_C + _hr * 0.95 + _ht * 0.1 - np.array([0, 0.3, 0])   # beside his cheek on the camera's right: a clear gap from ear and snout
def hover(t): return HOVER + np.array([0, 0.05 * math.sin(t * 6), 0])
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
        hov = hover(t)
        u = clampu(t, L["t1"] - 0.5, SH[n][1] - 0.1)          # flies over from the stump and arrives before the cut
        if u <= 0: return STUMP_PIP, to_tumble, False, 0.0, True, {}
        p = lerp(STUMP_PIP, hov, ease(u)); p[1] += 0.4 * math.sin(math.pi * u)
        return p, math.atan2(face[0] - p[0], face[2] - p[2]), True, 0.0, False, {}
    if n == "pip_idea":
        hov = hover(t)                                      # beside his face, in world space (not parented to the turning head)
        hov = hov + PIP_LIFT * ease(clampu(t, SH[n][1] - 0.6, SH[n][1]))                   # lifts off before the cut
        L = T.line("Problem B")
        ex = {"wings": (1.4 + 0.1 * math.sin(t * 10), 0.9 * math.sin(t * 28))} if L["t0"] < t < L["t1"] + 0.3 else {}
        return hov, math.atan2(face[0] - hov[0], face[2] - hov[2]), True, 0.0, False, ex
    if n == "climb":
        a = SH[n][0]; hov = hover(a - 0.01) + PIP_LIFT
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
        pitch = -0.3 * min(back, 0.27) / 0.27                 # leans back on each pull
        p = tug_body(back, pitch)                           # beak stays on the stalk's end as the apple swings out
        return p, TUG_YAW, True, pitch, False, {"gentle": True}
    if n == "catch":
        a = SH[n][0]
        side = SIDE2 + np.array([0, 0.05 * math.sin(t * 6), 0])
        start = tug_spot + np.array([OUT[0] * 0.25, -0.1, OUT[1] * 0.25])
        u = clampu(t, a, a + 0.8); p, yw = leg_path([start, side], u)       # away from the leaves, round behind him
        ex = {"cheer": True} if t > T.CATCH + 0.3 and u >= 1 else {}
        return p, (math.atan2(st["x"] - p[0], st["z"] - p[2]) if u >= 1 else yw), True, 0.0, False, ex
    if n in ("moral", "chorus"):
        return dance_pip(t, st, mats, n, arrive_from=SIDE2)
    a, b = SH["button_crane"]                               # flies off the paw, round low in front of his tummy, to peck the apple
    held = apple_state(t, mats)[1]
    m_end = fox_mats_p(tumble(a + 1.4)); held_end = apple_state(a + 1.4, m_end)[1]
    peck = held_end + np.array([-0.33, 0.06, 0.0])           # beak on the apple's upper outer side (his right, screen left)
    side = peck - apply(roty(PECK_YAW), BEAK_L)
    p0 = paw_seat(fox_mats_p(tumble(a))[2])
    u = clampu(t, a + 0.15, a + 1.4)
    if u < 1:                                               # straight legs: down-forward, across low in front, up and out to the apple
        pts = [p0, p0 + np.array([0.3, 0.1, 0.35]), p0 + np.array([0.3, -0.7, 0.85]), np.array([held_end[0] - 0.35, p0[1] - 0.7, p0[2] + 0.85]), side]   # out off the paw first, then down
        p, yw = leg_path(pts, u)
        return p, yw, True, 0.0, False, {"gentle": True}
    pk = 0.0
    for k in range(3):
        d = t - (a + 1.55 + 0.32 * k)
        if 0 <= d < 0.22: pk = 0.35 * math.sin(math.pi * d / 0.22)
    by = T.SPOKEN[-1]["t0"]; hop = 0.06 * abs(math.sin((t - by) * 9)) * clampu(t, by, by + 0.1) * (1 - clampu(t, by + 0.9, by + 1.0))
    off = held - held_end                                   # follows the apple if the paw moves
    return side + off + np.array([0, hop, 0]), PECK_YAW, True, pk, False, {"gentle": True, "hover": True}

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
            fwd = (tgt - eye) / np.linalg.norm(tgt - eye); rt = np.cross(fwd, [0, 1, 0]); rt /= np.linalg.norm(rt)
            trunk = 0.0                                                # keep the tree trunk out of the frame (polish pass)
            for ty in (1.2, 2.0):
                v = np.array([TREE[0], ty, TREE[1]]) - eye; z = np.dot(v, fwd)
                if z > 0 and abs(np.dot(v, rt)) / z < math.tan(math.radians(34) / 2) * W / H + 0.25 * 0.33 / max(z, 0.5): trunk = 0.5
            score = min(sep, 0.6) + 0.3 * (1 - facing) - trunk
            if best is None or score > best[0]: best = (score, yw)
    return best[1]
TUG_CAM_YAW = 168.0      # polish pass: chosen by projecting the tree mesh; yaws 160-175 keep the trunk and Tumble out of frame in both aspects
TUG_FIT = (0.9, 0.8) if not WIDE else (0.75, 0.67)
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
        return fit_cam(np.array([cx, 1.45, lerp(RUN0[1], PILE[1], e) - 0.2]), 6, 6, 2.1, 2.1)
    if name == "leaf_pile":                                 # close on the pile: legs and tail sticking out, then wider as he pops out
        a, b = SH[name]; e1 = ease(clampu(t, a, T.POP_OUT)); e2 = ease(clampu(t, T.POP_OUT - 0.1, T.POP_OUT + 0.5))
        c = lerp(np.array([PILE[0] - 0.2, 0.95, PILE[1]]), np.array([PILE[0], 0.85, PILE[1]]), e1)     # starts wide enough to keep him in as he comes down
        c = lerp(c, np.array([(PILE[0] + POPPED[0]) / 2, 1.15, (PILE[1] + POPPED[1]) / 2]), e2)
        return fit_cam(c, lerp(lerp(30, 22, e1), 12, e2), lerp(12, 8, e2), lerp(lerp(1.9, 1.05, e1), 1.55, e2), lerp(lerp(1.9, 1.25, e1), 1.45, e2))
    if name == "sour_face":
        return fit_cam(np.array([POPPED[0] + 0.25, 1.35, POPPED[1]]), lerp(-14, -8, e), 5, 1.0, 1.25)
    if name == "pip_idea":                                  # two-shot: Tumble's face and Pip beside it
        fc = HEAD_C + _hr * 0.42 - np.array([0, 0.08, 0])
        return fit_cam(fc, lerp(-12, -8, e), 4, 1.2, 0.95)
    if name == "climb":
        return fit_cam(np.array([lerp(POPPED[0], STUMP[0], 0.55), 1.75, (POPPED[1] + STUMP[1]) / 2 + 0.1]), -2, 8, 1.9, 2.5)
    if name == "tug":                                       # up in the tree with Pip and the apple
        pb = tug_body(0.0) + np.array([0, 0.3, 0])
        return fit_cam(lerp(A, pb, 0.55) - np.array([0, 0.05, 0]), TUG_CAM_YAW + lerp(-4, 4, e), -4, TUG_FIT[0], TUG_FIT[1], fov=34, lift=0.1)   # angle solved so Tumble stays out of line
    if name == "ready":                                     # tall frame on the stump: Tumble below, the apple at the top, Pip flying up
        return fit_cam(np.array([STUMP[0] - 0.6, 1.95, STUMP[1] - 0.2]), lerp(36, 42, e), -4, 2.4, 3.2)
    if name == "catch":                                     # tall enough to see the apple fall into his paws
        hx = ease(clampu(t, HOP_DOWN - 0.2, HOP_DOWN + 0.6))   # follows him as he hops down
        c = lerp(np.array([STUMP[0] - 0.4, lerp(2.0, 1.8, e), STUMP[1] - 0.2]), np.array([(STUMP[0] + DOWNPT[0]) / 2 - 0.15, 1.55, (STUMP[1] + DOWNPT[1]) / 2]), hx)
        return fit_cam(c, lerp(42, 34, e), -4, lerp(2.2, 1.6, e) + 0.2 * hx, lerp(2.7, 2.2, e))
    if name == "moral":
        return fit_cam(np.array([MSPOT[0] + 0.25, lerp(1.35, 1.45, e), MSPOT[1]]), lerp(12, 6, e), 5, lerp(1.3, 1.1, e), lerp(1.4, 1.15, e))
    if name == "chorus":
        return fit_cam(np.array([MSPOT[0] + 0.25, 1.2, MSPOT[1]]), -3, 6, 1.35, 1.35)
    a = SH["button_crane"][0]; e = ease(clampu(t, a, FREEZE))   # crane up, settled before the end hold
    return fit_cam(np.array([MSPOT[0] - 0.35, lerp(1.25, 1.7, e), MSPOT[1]]), 4, lerp(4, 10, e), lerp(1.45, 1.8, e), lerp(1.4, 1.75, e), lift=0.04)

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
    burst = clampu(t, T.LAND - 0.05, T.LAND + 0.6)
    burst2 = clampu(t, T.POP_OUT + 0.05, T.POP_OUT + 0.65)    # a smaller flurry as he pops out
    in_pile = n in ("big_jump", "leaf_pile")                  # he dives into the pile on purpose: its leaves are untagged for QA in these two shots
    for k, (off, rot, s, tint) in enumerate(PILE_LEAVES):     # the pile; leaves fly up when he lands, settle again
        fly = 0.0
        if 0 < burst < 1 and k % 3 == 0: fly = math.sin(math.pi * burst) * (0.4 + 0.5 * (k % 5) / 5)
        if 0 < burst2 < 1 and k % 4 == 1: fly = 0.6 * math.sin(math.pi * burst2) * (0.4 + 0.5 * (k % 5) / 5)
        p = np.array([PILE[0] + off[0] * (1 + 0.6 * fly), surf(PILE[0] + off[0], PILE[1] + off[2]) + off[1] + fly, PILE[1] + off[2] * (1 + 0.6 * fly)])
        u_ = U(mat=0, bump=0.0, tint=tint, tintMix=1.0)
        if not in_pile: u_["obj"] = "pile"
        draws.append((SC["leaf"], trans(*p) @ rotx(rot[0] + 3 * fly) @ roty(rot[1]) @ rotz(rot[2] * 0.3) @ scale(s), u_, False))
    st = tumble(t); mats = fox_mats_p(st); R, Mh, arms, legs = mats
    draw_tumble(draws, contacts, t, st, mats)
    if t >= SH["leaf_pile"][0]:                              # one pile leaf sticks to his crown as he pops out (stays on: a running gag)
        k = ease(clampu(t, T.POP_OUT + 0.05, T.POP_OUT + 0.4))
        Mw = Mh @ HEADLEAF_M
        if k < 1:                                           # until then it lies on top of the pile where his head comes out
            Mw = Mw.copy(); Mw[:3, 3] = lerp(HEADLEAF_PILE, Mw[:3, 3], k)
            if k == 0: Mw = trans(*HEADLEAF_PILE) @ rotx(0.2) @ roty(0.7) @ scale(1.1)
        u_ = U(mat=0, bump=0.0, tint=(0.93, 0.5, 0.22), tintMix=1.0)
        if not in_pile: u_["obj"] = "headleaf"
        draws.append((SC["leaf"], Mw, u_, False))
        uv = dict(u_, tint=(0.62, 0.3, 0.14))                # a darker midrib and a little stalk, so it reads as a leaf
        draws.append((PR["stick"], seg_M(apply(Mw, (-0.1, 0.016, 0.0)), apply(Mw, (0.11, 0.016, 0.0)), 0.005), uv, False))
        draws.append((PR["stick"], seg_M(apply(Mw, (0.11, 0.012, 0.0)), apply(Mw, (0.18, 0.035, 0.01)), 0.009), uv, False))
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, arms)
    # apple, its hanging stem (up into the leaves) and its side stalk with a leaf
    kind, val, Ma = apple_state(t, mats)
    stalk = U(mat=0, bump=0.0, tint=(0.48, 0.32, 0.2), tintMix=1.0, obj="apple")
    if kind == "hang":
        Mpiv = hang_mat(tug_pull(t))[0]
        draws.append((PR["stick"], Mpiv @ trans(*(A + np.array([0, APPLE_TOP - 0.03, 0]))) @ scale(0.6, 0.55, 0.6), U(mat=0, bump=0.0, tint=(0.48, 0.32, 0.2), tintMix=1.0), False))
    draws.append((E2["apple"], Ma, U(mat=0, bump=0.5, obj="apple"), True))
    b0, b1 = apply(Ma, TWIG_DL * (TWIG_R0 - 0.06)), apply(Ma, TWIG_DL * TWIG_R1)
    draws.append((PR["stick"], seg_M(b0, b1, 0.021), stalk, False))
    lf = apply(Ma, TWIG_DL * (TWIG_R0 + 0.1) + np.array([0, 0.09, 0.0]))     # a small green leaf on the stalk
    draws.append((SC["leaf"], trans(*lf) @ roty(math.atan2(*(b1 - b0)[[0, 2]]) + 1.2) @ rotz(0.5) @ scale(0.75),
                  U(mat=0, bump=0.0, tint=(0.45, 0.72, 0.3), tintMix=1.0, obj="apple"), False))
    if kind != "hang" and t > T.GAG_SWEET + 0.3:            # the bite mark: a flat pale patch, flush with the skin, where his mouth met it
        draws.append((PR["ball"], Ma @ BITE_MARK_M, U(mat=0, bump=0.0, tint=(0.95, 0.85, 0.58), tintMix=1.0), False))
    puff(draws, np.array([PILE[0], 0.5, PILE[1]]), T.LAND, t, n=12, size=0.07, spread=1.2, dur=0.5, tint=(0.95, 0.7, 0.35), axis=(0, 0.8, 0.3))
    return draws, contacts

# ---------------- end hold and precomputed placements ----------------
def _pick_freeze():
    """last action settles by DURATION - 0.8; hold a frame with everyone's eyes open so the fade lands on a still"""
    c = [T.DURATION - 0.8 - 0.02 * k for k in range(11)]
    return max(c, key=lambda f: min(blink(f), blink(f, 1.3, 2.7)))
FREEZE = _pick_freeze()
def _headleaf():
    """leaf resting on the front of his crown, between and in front of the ears, tilted to the head surface"""
    c = np.array([0.04, 1.758, 0.3]); nrm = np.array([0, math.cos(0.7), math.sin(0.7)])    # head surface there (from the head SDF), front of the crown
    return trans(*(c + nrm * 0.01)) @ rotx(0.7) @ roty(0.12) @ scale(1.1)
HEADLEAF_M = _headleaf()
HEADLEAF_PILE = np.array([BURIED[0] - DIVE_DIR[0] * 0.25, surf(*BURIED) + 0.47, BURIED[1] - DIVE_DIR[1] * 0.25])
def _bite_mark():
    """apple-local placement of the bite: the point of the apple nearest his mouth at the bite"""
    g = T.GAG_SWEET; st = tumble(g); mats = fox_mats_p(st)
    Ma = apple_state(g, mats)[2]; mouth = apply(mats[1], np.array(FOXD["mouth"]["c"]) + np.array([0, -0.01, 0.02]))
    v = D["ep2"]["apple"]["v"]; Wv = (Ma @ np.c_[v, np.ones(len(v))].T).T[:, :3]
    i = int(np.argmin(np.linalg.norm(Wv - mouth, axis=1))); pl = v[i]
    nl = pl - np.array([0, 0.1, 0]); nl /= np.linalg.norm(nl)
    return trans(*(pl - nl * 0.035)) @ align_up(nl) @ scale(0.14, 0.04, 0.14)   # sunk so its rim meets the curved skin (no raised edge)
BITE_MARK_M = _bite_mark()
def build_frozen(t): return build_draws(min(t, FREEZE))
def camera_frozen(t): return camera(min(t, FREEZE))
HOOKS.update(build=build_frozen, camera=camera_frozen, tumble=tumble,
             ground_objs=lambda t: ("pip",) if T.shot_at(t)[1] in ("big_jump", "leaf_pile") or t < T.POP_OUT + 0.75 and T.shot_at(t)[1] == "sour_face" else ("fox", "pip"),
             qa_ignore={("apple", "tree"), ("tree", "apple")})   # the hanging apple's top is tucked into the leaves
if __name__ == "__main__":
    main()
