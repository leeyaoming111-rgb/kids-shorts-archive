"""Tumble & Pip Fables 10: One Good Turn  (Aesop: The Dove and the Ant)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa"""
from fablekit import *

# KIT FIX (local override, reported to the coordinator): render_base.Mesh builds its shadow VAO with the layout
# "3f 36x" (48 bytes per vertex) but the buffer holds 10 floats (40 bytes), so shadow casters read garbage
# vertices and throw huge, wrong shadows. Rebuild every shadow VAO with the right stride.
def _fix_shadow_vaos():
    seen = set()
    for group in (FOXP, PIPP, PR, SC, E2, {"w": EYE_W, "p": EYE_P}):
        for m in group.values():
            if id(m) in seen: continue
            seen.add(id(m)); m.svao = ctx.vertex_array(sprog, [(m.vbo, "3f 28x", "in_pos")], m.ibo)
_fix_shadow_vaos()

# ---------------- world: the stream bank, with a big golden flower dripping honey ----------------
TWIG_Z = -5.6; TWIG_X0 = -2.7; CURRENT = 0.17         # the twig raft drifts downstream (+x) and spins slowly
TWIG_L, TWIG_R = 0.42, 0.05
LEAF_S = 0.4                                           # Episode 2's bigleaf, scaled: blade 0.64 long, stem tip 0.5 behind the centre
LEAF0 = (-1.3, -4.25)                                  # the leaf lying on the bank, blade towards the water
LEAF_YAW0 = math.pi / 2                                # blade direction (0, -1): towards the stream
LEAF_STEM = (LEAF0[0], LEAF0[1] + 1.25 * LEAF_S)       # its stem tip
PIP_GRAB = (LEAF_STEM[0], LEAF_STEM[1] + 0.45)         # Pip stands here, leaning forward, to take the stem in his beak
GRAB_PITCH = 0.7
LEAF_BANK = (-0.95, -4.7)                               # where the leaf boat touches the bank
ANT_BANK = (-0.5, -4.45)                               # the ant ashore
PIP_BANK = (-0.05, -4.3)                               # Pip on the grass, facing the ant
T0 = (0.65, -3.5)                                       # Tumble on the bank, watching
FLOWER = (2.3, -3.6); FLOWER_S = 4.5; FLOWER_LEAN = 0.25
FLOWER_M = trans(FLOWER[0], ground_h(*FLOWER) - 0.02, FLOWER[1]) @ rotx(FLOWER_LEAN) @ roty(-math.pi / 2) @ scale(FLOWER_S)
DRIP_TIP = apply(FLOWER_M, (0.135, 0.2 - 0.03, 0.0))   # underside of the front petal's tip: the honey drips from here
HPC = (FLOWER[0] + 0.1, -2.12)                                # the honey puddle (centre)
HP_R = (0.34, 0.03, 0.36)
HP = (FLOWER[0], -2.25)                                 # Pip stuck in the honey, facing +x
HONEY_TOP = 0.03
PB = 0.5                                                # the ant line runs from Pip back-left, away from the camera, at this angle
DIRL = np.array([-math.cos(PB), 0.0, -math.sin(PB)])    # unit vector from Pip towards the line (xz)
PIP_YAW_STUCK = math.atan2(-DIRL[0], -DIRL[2])          # Pip faces away from the line (towards the camera, a bit right)
TS = (0.05, -4.5)                                       # Tumble behind the line, facing Pip
TS_YAW = math.atan2(HP[0] - TS[0], HP[1] - TS[1])
HONEY = (1.0, 0.7, 0.12)
FLOWERS = make_flowers([(T0[0], T0[1], 1.0), (TS[0], TS[1], 1.6), (FLOWER[0], FLOWER[1], 1.0), (HPC[0], HPC[1], 0.8),
                        ("box", -3.5, 3.6, -4.9, -3.0), ("box", -4.5, 1.6, -4.9, -0.8), ("box", -1.0, 3.6, -3.3, -1.3), ("box", 0.8, 3.8, -1.3, 0.8), ("band", -6.8, -4.3)], seed=53)

def twig_c(t):
    x = TWIG_X0 + CURRENT * t + 2.2 * max(0.0, t - T.ANT_HOP - 0.12) ** 1.5   # the current takes the empty twig away
    z = TWIG_Z - 0.5 * ease(clampu(t, T.ANT_HOP + 0.05, T.ANT_HOP + 0.9))        # and out round the back of the leaf
    return np.array([x, surf(x, z) + 0.025 + 0.012 * math.sin(t * 2.3), z])
def twig_spin(t): return 1.1 * t

# ---------------- the leaf boat ----------------
def leaf_on_beak(Mp, droop):
    b = beak_pos(Mp); yaw = math.atan2(Mp[0, 2], Mp[2, 2])   # Pip's heading
    return trans(*b) @ roty(yaw - math.pi / 2) @ rotz(-droop) @ trans(1.25 * LEAF_S, 0, 0) @ scale(LEAF_S)
REL_X = TWIG_X0 + CURRENT * (T.DROP + 0.45) + 1.0      # release so the leaf lands just beside the drifting twig
REL_P = np.array([REL_X, 0.85, TWIG_Z + 0.05 + 0.75])     # Pip's position at the drop (the blade hangs out over the water)
LAND_T = T.DROP + 0.45
BOARD = T.ANT_HOP + 0.4
ASHORE = T.ASHORE

# ---------------- Tumble ----------------
def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    st["x"], st["z"] = T0
    if n in ("hook_water", "title_wide"):
        st["yaw"] = 0.25
        if n == "title_wide":                              # waves hello
            a = SH[n][0]; w = ease(clampu(t, a + 0.2, a + 0.6)) * (1 - ease(clampu(t, a + 1.8, a + 2.3)))
            st["arms"][0] = [0.15 + w * (2.0 + 0.25 * math.sin(t * 9)), 0.25 * w]
    elif n in ("leaf_pickup", "leaf_drop", "thank_you"):  # watching the rescue
        st["yaw"] = -2.1; st["head"][0] = 0.12
        if n == "thank_you" and t > ASHORE + 0.3:
            st["yaw"] = lerp(-2.1, -0.9, ease(clampu(t, ASHORE + 0.3, ASHORE + 1.0)))
            st["arms"][1] = [0.3 + 0.5 * ease(clampu(t, ASHORE + 0.5, ASHORE + 1.0)), 0.6]
    elif n in ("fly_off", "splat"):                       # calls after Pip and follows him along the bank
        a = SH["fly_off"][0]
        walk_to(st, t, T0, TS, a + 0.3, a + 2.6)
        if t >= a + 2.6: st["yaw"] = TS_YAW
        L = T.line("Problem A")
        if L and L["t0"] - 0.2 < t < L["t1"] + 0.4: st["arms"][0] = [0.45, 1.35]   # pointing after Pip
        if n == "splat":
            st["yaw"] = TS_YAW
            d = t - T.SPLAT
            if 0 < d < 0.8: st["sq"] -= 0.05 * math.sin(d * 12) * math.exp(-d * 3)   # a little flinch at the splat
    else:
        st["x"], st["z"] = TS; st["yaw"] = TS_YAW
        if n == "stuck":
            st["head"][0] = 0.1
        elif n == "ants_march":
            d = t - (SH[n][0] + 0.25)                       # "Uh-oh!": paws up, head shake
            k = ease(clampu(d, 0, 0.3)) * (1 - ease(clampu(d, 1.4, 1.9)))
            st["arms"] = [[0.35, 0.3 + 1.0 * k], [0.35, 0.3 + 1.0 * k]]
            st["head"][1] = 0.15 * math.sin(d * 10) * k; st["head"][0] = 0.12
        elif n == "tug":                                    # cheering the ants on, a bob on every heave
            st["arms"] = [[0.5, 0.9], [0.5, 0.9]]; st["head"][0] = 0.15
            for tg in T.TUGS:
                st["y"] += 0.04 * max(0.0, math.sin(math.pi * clampu(t, tg, tg + 0.4)))
        elif n == "pop":
            st["yaw"] = lerp(TS_YAW, 0.0, ease(clampu(t, T.LANDING - 0.3, T.LANDING + 0.5)))   # turns to the camera with Pip on his nose
            st["head"][0] = 0.15 * (1 - ease(clampu(t, T.POP + 0.3, T.LANDING - 0.2)))
            st["arms"] = [[0.5, 0.9], [0.5, 0.9]]
            if t > T.LANDING:                              # Pip lands on his nose: a little wobble, then a giggle
                d = t - T.LANDING
                st["sq"] -= 0.06 * math.exp(-d * 6) * math.cos(d * 22)
                st["arms"] = [[0.75, 0.55], [0.75, 0.55]]
                if d > 0.5: st["y"] += 0.025 * abs(math.sin((d - 0.5) * 9)) * min(1.0, (d - 0.5) * 3)
        elif n in ("moral", "chorus"):
            dance_tumble(st, t, n)
            sway = math.sin(2 * math.pi * (t - SH["chorus"][0]) / (2 * BEAT)) if n == "chorus" else 0.0
            st["arms"][1] = list(ANT_PAW); st["arms"][1][1] += 0.12 * sway   # the ant rides his other paw
        else:                                              # button: still holding both friends, a happy bounce
            a = SH["button_crane"][0]
            st["yaw"] = -0.05; st["arms"] = [list(DANCE_ARM), list(ANT_PAW)]; st["head"][2] = 0.08
            st["y"] += 0.025 * abs(math.sin((t - a) * 8)) * clampu(t, a + 0.3, a + 0.6)
    return st
ANT_PAW = [0.45, 0.95]

def nose_seat(mats):
    """where Pip stands on Tumble's nose (front-top of the nose ball, measured from the head mesh)"""
    return apply(mats[1], (0.0, 1.43, 0.71)) + UP

# ======================================================================================================
# ANT (Fable 10's own clay ant, built from kit primitives; the coordinator will unify it with Fable 6's)
#   root at the feet, facing +z: bottom ball, middle ball, big head ball, six two-part stick legs,
#   two feelers with ball tips, big kit eyes, a tiny mouth when it sings. The hero ant wears a leaf hat.
# ======================================================================================================
ANT_S = 0.9
ANT_RED, ANT_DK = (0.88, 0.33, 0.3), (0.55, 0.2, 0.24)
ANT_HAT = (0.45, 0.78, 0.38)
def ant_mouth_track():
    n = int(T.DURATION * FPS) + 2; m = np.zeros(n)
    for L in T.LINES:
        if L["who"] != "ant": continue
        for w in L["words"]:
            a, b = int(w["t0"] * FPS), int(max(w["t1"], w["t0"] + 0.18) * FPS)
            for f in range(a, min(b + 1, n)): m[f] = max(m[f], math.sin(math.pi * (f - a + 0.5) / (b - a + 1)) * 0.95)
    return m
ANT_MOUTH = ant_mouth_track()
def ant_mouth(t): return ANT_MOUTH[min(int(t * FPS), len(ANT_MOUTH) - 1)]
def ant_M(a):
    """a: dict(p, yaw, lean, roll, s). lean > 0 tips it back about the ground under its bottom (tug, sit)."""
    p, s = np.asarray(a["p"], float), a.get("s", ANT_S)
    piv = -0.12 * s
    return trans(*p) @ roty(a.get("yaw", 0.0)) @ trans(0, 0, piv) @ rotx(-a.get("lean", 0.0)) @ trans(0, 0, -piv) @ \
        rotz(a.get("roll", 0.0)) @ scale(s)
def draw_ant(draws, contacts, t, a, obj, hero=False, sing=False):
    M = ant_M(a); ph = a.get("walk", None); seed = 3.0 + (hash(obj) % 7)
    body = U(mat=0, bump=0.5, tint=ANT_RED, tintMix=1.0, seed=seed, obj=obj)
    dark = U(mat=0, bump=0.0, tint=ANT_DK, tintMix=1.0, obj=obj)
    for c, r in [((0, 0.10, -0.12), (0.075, 0.07, 0.095)), ((0, 0.095, -0.01), (0.045, 0.045, 0.05)), ((0, 0.135, 0.085), (0.07, 0.07, 0.07))]:
        draws.append((PR["ball"], M @ trans(*c) @ scale(*r), body, True))
    for side in (1, -1):                                   # legs: hip -> knee (up and out) -> foot
        for k, z in enumerate((-0.045, -0.01, 0.025)):
            sw = 0.0; lift = 0.0
            if ph is not None:
                q = ph + (k % 2) * math.pi + (0 if side > 0 else math.pi)
                sw = 0.035 * math.sin(q); lift = 0.02 * max(0.0, math.cos(q))
            if a.get("legs_up"): lift += 0.03
            hip = np.array([0.03 * side, 0.085, z])
            knee = np.array([0.095 * side, 0.125, z * 1.6 + sw * 0.5])
            foot = np.array([0.13 * side, 0.004 + lift, z * 2.4 + sw])
            if k == 2 and a.get("grip_pt") is not None:           # front legs hold Pip's tail
                foot = (np.linalg.inv(M) @ np.r_[a["grip_pt"], 1.0])[:3] + np.array([0.012 * side, 0.0, 0.0])
                knee = (hip + foot) / 2 + np.array([0.02 * side, 0.05, 0.0])
            for a_, b_ in ((hip, knee), (knee, foot)):
                A, B = apply(M, a_), apply(M, b_)
                Ms = seg_M(A, B, 0.012 * a.get("s", ANT_S))
                if Ms is not None: draws.append((PR["stick"], Ms, dark, True))
    wig = a.get("feelers", 0.0)
    for side in (1, -1):                                   # feelers with ball tips
        base = np.array([0.03 * side, 0.19, 0.11])
        tip = np.array([(0.075 + 0.02 * math.sin(t * 6 + side)) * side, 0.29 + 0.03 * wig * math.sin(t * 14 + side), 0.15 + 0.03 * wig])
        A, B = apply(M, base), apply(M, tip)
        Ms = seg_M(A, B, 0.009 * a.get("s", ANT_S))
        if Ms is not None: draws.append((PR["stick"], Ms, dark, False))
        draws.append((PR["ball"], M @ trans(*tip) @ scale(0.02), U(mat=0, bump=0.0, tint=ANT_RED, tintMix=1.0), False))
    eyes(draws, M, [(0.033, 0.15, 0.135), (-0.033, 0.15, 0.135)], 0.032, blink(t, 0.7 + 0.37 * (hash(obj) % 5), 3.1))
    if sing:
        mo = ant_mouth(t)
        if mo > 0.06: draws.append((PR["mouth"], M @ trans(0, 0.103, 0.148) @ scale(0.026, 0.008 + 0.022 * mo, 0.014), U(mat=2, bump=0.0), False))
    if hero:                                               # the leaf hat (from the leaf boat)
        draws.append((SC["leaf"], M @ trans(0, 0.205, 0.07) @ rotx(-0.25) @ rotz(0.2) @ scale(0.75), U(mat=0, bump=0.0, tint=ANT_HAT, tintMix=1.0), False))
    if not a.get("air"): contacts.append((float(M[0, 3]), float(M[2, 3]), 0.18, 0.8))
    return M
def ant_on(x, z, yaw, **k):
    return dict(p=(x, surf(x, z), z), yaw=yaw, **k)
# ======================================================================================================

# ---------------- the ant line ----------------
GAP = 0.34
ANT_YAW = math.atan2(-DIRL[0], -DIRL[2])               # the line faces Pip
TAIL_LOCAL = np.array([0.0, 0.2, -0.32]) * 1.1         # Pip's tail tip (his own frame, feet at the origin)
def path_pt(pts, s):
    """point and heading at arc length s along a polyline of (x, z) points"""
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if s <= L or b is pts[-1]:
            u = min(max(s / max(L, 1e-6), 0.0), 1.0)
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), math.atan2(b[0] - a[0], b[1] - a[1])
        s -= L
def path_len(pts): return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:]))
LEAD_D = -TAIL_LOCAL[2] + 0.12                         # the hero ant's distance behind Pip's feet: its front legs reach his tail tip
def slot(k, shift=0.0):
    d = LEAD_D + GAP * k + shift; return (HP[0] + DIRL[0] * d, HP[1] + DIRL[2] * d)
PEND = slot(0, 2.2)                                    # the ants join the line here and walk up it to their places
def ant_path(k):
    start = ANT_BANK if k == 0 else (-4.5 - 0.3 * k, -2.7)
    return [start, (PEND[0] - 0.4, PEND[1] + 0.35), PEND, slot(k)]
MARCH_SPEED = 1.7
def march_start(k):
    if k == 0: return T.MARCH
    arrive0 = T.MARCH + path_len(ant_path(0)) / MARCH_SPEED
    return arrive0 + 0.18 * k - path_len(ant_path(k)) / MARCH_SPEED

def tug_env(t):
    """Pip's stretch (1 = none) and the line's lean from the three tugs, plus the release at the pop"""
    amps = [0.55, 0.95, 1.5]; s, lean = 1.0, 0.0
    for k, tg in enumerate(T.TUGS[:3]):
        a = amps[min(k, 2)]
        if k == len(T.TUGS[:3]) - 1:                      # the last tug holds until the pop
            u = ease(clampu(t, tg, tg + 0.35)); hold = t < T.POP
            if t < tg: continue
            if hold: s += a * u; lean += 0.55 * u
            else:
                d = t - T.POP; s += a * max(0.0, 1 - d / 0.08)
            continue
        if t < tg: continue
        d = t - tg
        if d < 0.35: v = ease(d / 0.35)
        elif d < 0.55: v = 1.0
        else:
            e = d - 0.55; v = math.exp(-e * 5) * math.cos(e * 16)   # toffee snaps back with a wobble
        s += a * v; lean += 0.5 * max(0.0, v) if d < 0.9 else 0.0
    return max(s, 0.8), lean
STRETCH_AX = DIRL + np.array([0, 0.45, 0]); STRETCH_AX = STRETCH_AX / np.linalg.norm(STRETCH_AX)   # back towards the ants, a little up
def stretch_M(anchor, axis, s):
    k = 1 / math.sqrt(max(s, 1e-3)); A = np.outer(axis, axis)
    L = np.eye(4); L[:3, :3] = k * (np.eye(3) - A) + s * A
    return trans(*anchor) @ L @ trans(*(-np.asarray(anchor)))
def pip_feet_world(): return np.array([HP[0], surf(*HP) + HONEY_TOP - 0.015, HP[1]])

def ants(t):
    """list of (state, obj, hero, sing) for every ant on screen at t"""
    n = T.shot_at(t)[1]; out = []
    if n in ("hook_water", "title_wide", "leaf_pickup", "leaf_drop", "thank_you", "fly_off", "splat", "stuck") or \
       (n == "ants_march" and t < T.MARCH):
        out.append((hero_ant(t), "ant0", True, True))
        return out
    if n in ("ants_march", "tug", "pop"):
        s, lean = tug_env(t) if n != "ants_march" else (1.0, 0.0)
        tail = stretch_M(pip_feet_world(), STRETCH_AX, s) @ trans(*(pip_feet_world() + UP)) @ roty(PIP_YAW_STUCK) @ np.r_[TAIL_LOCAL, 1]
        shift = float((tail[0] - HP[0]) * DIRL[0] + (tail[2] - HP[1]) * DIRL[2]) + TAIL_LOCAL[2] if n != "ants_march" else 0.0   # + = longer
        for k in range(6):
            pts = ant_path(k); sk = (t - march_start(k)) * MARCH_SPEED
            Lk = path_len(pts)
            if n in ("ants_march", "tug") and sk < Lk:
                if sk < 0: continue
                (x, z), yaw = path_pt(pts, sk)
                st = ant_on(x, z, yaw, walk=t * 26 + k, feelers=0.5)
            else:
                x, z = slot(k, shift)
                st = ant_on(x, z, ANT_YAW, lean=lean, feelers=0.6)
                if n == "pop" and t > T.POP:                # everyone sits down in a heap, legs up
                    d = t - T.POP; u = ease(clampu(d, 0.0, 0.25 + 0.04 * k))
                    x, z = slot(k, shift * (1 - u) + 0.12 * u)
                    st = ant_on(x, z, ANT_YAW, lean=lean + (0.9 - lean) * u, legs_up=u > 0.5, feelers=1.0)
                    st["p"] = np.asarray(st["p"]) + np.array([0, 0.05 * u, 0])
                    if d > 1.2:                              # then they cheer, feelers waving
                        st["feelers"] = 1.5
                if k == 0 and (n != "pop" or t <= T.POP): st["grip_pt"] = tail[:3] + np.array([0, 0.0, 0])
            out.append((st, f"ant{k}", k == 0, k == 0))
        return out
    # moral, chorus, button: the hero rides Tumble's paw; the line stands beside the flower facing the camera
    for k in range(1, 6):
        x = TS[0] + (-1.05, -0.78, -0.5, 0.78, 1.05)[k - 1]; z = TS[1] + 0.3
        st = ant_on(x, z, -0.2 if x < TS[0] else 0.2)
        if n == "chorus":
            sway = math.sin(2 * math.pi * (t - SH["chorus"][0]) / (2 * BEAT))
            st["roll"] = 0.18 * sway; st["feelers"] = 1.0
        if n == "button_crane":                             # march home with the honey drop
            a = SH["button_crane"][0]; sk = max(0.0, t - (a + 0.3 + 0.12 * (k - 1))) * 1.2
            if sk > 0:
                pts = [(x, z), (x - 0.3, z + 0.35), (x - 6.0, z + 0.35)]
                (px, pz), yaw = path_pt(pts, sk); st = ant_on(px, pz, yaw, walk=t * 22 + k)
        out.append((st, f"ant{k}", False, False))
    return out

def hero_ant(t):
    """the rescued ant: on the twig, the leaf boat, ashore by Pip (before the march)"""
    if t < T.ANT_HOP:                                       # balancing on the spinning twig, feelers up
        c = twig_c(t); sp = twig_spin(t)
        p = c + np.array([0, TWIG_R * 1.0 + 0.004, 0])
        return dict(p=p, yaw=sp + math.pi / 2, roll=0.12 * math.sin(t * 5.5), feelers=1.4)
    lp, lyaw = leaf_center(t)
    on_leaf = np.array([lp[0], lp[1] + 0.05, lp[2]])
    if t < T.ANT_HOP + 0.4:                                 # hop from the twig to the leaf
        u = clampu(t, T.ANT_HOP, T.ANT_HOP + 0.4); c = twig_c(T.ANT_HOP)
        p0 = c + np.array([0, TWIG_R + 0.004, 0]); p = lerp(p0, on_leaf, u); p[1] += 0.22 * math.sin(math.pi * u)
        return dict(p=p, yaw=0.0, feelers=0.8, air=True, walk=None)
    if t < ASHORE:                                          # riding the leaf to the bank
        return dict(p=on_leaf, yaw=0.15, feelers=0.6, roll=0.05 * math.sin(t * 3))
    bank = np.array([ANT_BANK[0], surf(*ANT_BANK), ANT_BANK[1]])
    to_pip = math.atan2(PIP_BANK[0] - ANT_BANK[0], PIP_BANK[1] - ANT_BANK[1])
    if t < ASHORE + 0.45:
        u = clampu(t, ASHORE, ASHORE + 0.45); p = lerp(on_leaf, bank, u); p[1] += 0.25 * math.sin(math.pi * u)
        return dict(p=p, yaw=lerp(0.15, to_pip, u), air=True)
    st = dict(p=bank, yaw=to_pip, feelers=0.8)
    L = T.line("Setup B")
    if L and L["t0"] < t < L["t1"] + 0.3: st["feelers"] = 1.6; st["p"] = bank + np.array([0, 0.02 * abs(math.sin(t * 9)), 0])
    if t > T.WHISTLE - 0.2 and t < T.MARCH:                 # whistles for its friends: up on tiptoe, facing the flower
        st["yaw"] = math.atan2(PEND[0] - ANT_BANK[0], PEND[1] - ANT_BANK[1]); st["feelers"] = 1.8
    return st

# ---------------- the leaf ----------------
def leaf_center(t):
    """(centre, yaw) of the leaf boat once it is on the water"""
    x0 = REL_X; z0 = REL_P[2] - 0.75
    x = x0 + CURRENT * (min(t, BOARD) - LAND_T)
    yaw = LEAF_YAW0 + 0.25 * math.sin((t - LAND_T) * 0.8)
    if t > BOARD:
        u = ease(clampu(t, BOARD, ASHORE - 0.1))
        x, z = lerp((x, z0), LEAF_BANK, u); yaw = lerp(yaw, LEAF_YAW0 + 0.6, u)
    else: z = z0
    return np.array([x, surf(x, z) + 0.012 + 0.006 * math.sin(t * 2.1), z]), yaw
def leaf_M(t, Mp):
    if t < T.GRAB:
        return trans(LEAF0[0], surf(*LEAF0) + 0.01, LEAF0[1]) @ roty(LEAF_YAW0) @ scale(LEAF_S), "ground"
    if t < T.DROP:
        dr = 0.45 * ease(clampu(t, T.GRAB + 0.2, T.GRAB + 0.8))
        return leaf_on_beak(Mp, dr), "held"
    if t < LAND_T:                                          # flutters down and lands flat
        u = clampu(t, T.DROP, LAND_T)
        M0 = leaf_on_beak(PIP_AT_DROP, 0.45); c0 = M0[:3, 3]
        c1, y1 = leaf_center(LAND_T)
        c = lerp(c0, c1, u * u); rz = 0.45 * (1 - u) * math.cos(u * 9)
        return trans(*c) @ roty(lerp(LEAF_YAW0, y1, u)) @ rotx(0.25 * math.sin(u * 8) * (1 - u)) @ rotz(rz * 0.3) @ scale(LEAF_S), "fall"
    c, y = leaf_center(t)
    return trans(*c) @ roty(y) @ scale(LEAF_S), "water"

# ---------------- Pip ----------------
def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    if n == "hook_water":                                   # flutters in beside the spinning ant
        hov = twig_c(t) + np.array([0.5, 0.55, 0.05]) + np.array([0, 0.05 * math.sin(t * 6), 0])
        p0 = np.array([-0.4, 1.6, -4.4]); u = clampu(t, 0.0, 1.3)
        p = lerp(p0, hov, ease(u))
        yaw = math.atan2(twig_c(t)[0] - p[0], twig_c(t)[2] - p[2])
        L = T.line("Hook")
        ex = {"wings": (1.3 + 0.15 * math.sin(t * 12), 1.3 + 0.15 * math.sin(t * 12 + 1))} if L and L["t0"] < t < L["t1"] else {"gentle": True}
        return p, yaw, True, 0.0, False, ex
    if n == "title_wide":                                   # over to the leaf on the bank: up, across, down; takes its stem
        a = SH[n][0]
        h0 = twig_c(a) + np.array([0.5, 0.55, 0.05])
        g = np.array([PIP_GRAB[0], surf(*PIP_GRAB), PIP_GRAB[1]]) + UP
        legs = [(a, h0), (a + 0.35, h0 + np.array([0, 0.35, 0])), (a + 1.2, g + np.array([0, 0.7, 0])), (T.GRAB - 0.25, g)]
        p = legs[-1][1]
        for (ta, pa), (tb, pb) in zip(legs[:-1], legs[1:]):
            if ta <= t < tb: p = lerp(pa, pb, ease(clampu(t, ta, tb))); break
        if t < T.GRAB - 0.25:
            return p, math.pi, True, 0.0, False, {"gentle": True}
        pt = GRAB_PITCH * ease(clampu(t, T.GRAB - 0.25, T.GRAB))
        return g, math.pi, False, pt, False, {}
    if n == "leaf_pickup":                                  # lifts the leaf and carries it out over the water
        g = np.array([PIP_GRAB[0], surf(*PIP_GRAB), PIP_GRAB[1]]) + UP
        a = SH[n][0]
        if t < a + 0.35:
            pt = GRAB_PITCH * (1 - ease(clampu(t, a, a + 0.35)))
            return g + np.array([0, 0.15 * ease(clampu(t, a + 0.1, a + 0.35)), 0]), math.pi, True, pt, False, {"gentle": True}
        up = g + np.array([0, 0.15, 0])
        p = lerp(up, REL_P, ease(clampu(t, a + 0.35, T.DROP - 0.05)))
        return p, math.pi, True, 0.0, False, {"gentle": True, "beak": True}
    if n == "leaf_drop":
        if t < T.DROP:
            a = SH[n][0]; g = np.array([PIP_GRAB[0], surf(*PIP_GRAB), PIP_GRAB[1]]) + UP + np.array([0, 0.15, 0])
            p = lerp(g, REL_P, ease(clampu(t, SH["leaf_pickup"][0] + 0.35, T.DROP - 0.05)))
            return p, math.pi, True, 0.0, False, {"gentle": True, "beak": True}
        if t < T.ANT_HOP + 0.6:                             # hovers, cheering the ant on
            p = REL_P + np.array([0, 0.05 * math.sin(t * 6), 0])
            return p, math.pi, True, 0.0, False, ({"wings": (1.4 + 0.1 * math.sin(t * 10), 1.4 + 0.1 * math.sin(t * 10 + 1))} if t > T.ANT_HOP else {"gentle": True})
        g = np.array([PIP_BANK[0], surf(*PIP_BANK), PIP_BANK[1]]) + UP
        u = clampu(t, T.ANT_HOP + 0.6, SH[n][1] - 0.2)
        p = lerp(REL_P, g, ease(u)); p[1] += 0.25 * math.sin(math.pi * u)
        yaw = lerp(math.pi, math.atan2(ANT_BANK[0] - PIP_BANK[0], ANT_BANK[1] - PIP_BANK[1]), ease(u))
        return p, yaw, u < 1, 0.0, False, {"gentle": True}
    g_bank = np.array([PIP_BANK[0], surf(*PIP_BANK), PIP_BANK[1]]) + UP
    to_ant = math.atan2(ANT_BANK[0] - PIP_BANK[0], ANT_BANK[1] - PIP_BANK[1])
    hp = np.array([HP[0], surf(*HP) + HONEY_TOP - 0.015, HP[1]]) + UP
    if n == "thank_you":
        L = T.line("Setup B")
        ex = {"cheer": True} if L and t > L["t1"] else {}
        return g_bank, to_ant, False, 0.0, False, ex
    if n in ("fly_off", "splat"):                           # up (clear of Tumble's head), across, down into the honey
        a = SH["fly_off"][0]
        legs = [(a + 0.25, g_bank), (a + 0.85, g_bank + np.array([0, 2.4, 0])),
                (T.SPLAT - 0.6, np.array([HP[0] - 0.75, 2.5, HP[1]])), (T.SPLAT, hp)]
        if t < legs[0][0]: return g_bank, to_ant, False, 0.0, False, {}
        if t < T.SPLAT:
            for (ta, pa), (tb, pb) in zip(legs[:-1], legs[1:]):
                if ta <= t < tb:
                    u = clampu(t, ta, tb); p = lerp(pa, pb, ease(u) if tb != T.SPLAT else u * u)
                    d = pb - pa; yaw = math.atan2(d[0], d[2]) if abs(d[0]) + abs(d[2]) > 0.3 else PIP_YAW_STUCK
                    return p, yaw, True, 0.0, False, {"gentle": True}
        d = t - T.SPLAT                                     # splat: squashed into the honey
        return hp, PIP_YAW_STUCK, False, 0.0, True, {"cling": max(0.0, math.exp(-d * 5) * math.cos(d * 14)), "droop": 0.0}
    if n == "stuck":
        flap = any(0 <= t - ta < 0.9 for ta in STUCK_TRIES)
        return hp, PIP_YAW_STUCK, False, 0.0, True, ({"wings": (0.9 * math.sin(t * 30) + 0.5, 0.9 * math.sin(t * 30 + 0.4) + 0.5)} if flap else {"droop": 0.6})
    if n == "ants_march":
        return hp, PIP_YAW_STUCK, False, 0.0, True, {"droop": 0.8}
    if n == "tug" or (n == "pop" and t < T.POP):
        return hp, PIP_YAW_STUCK, False, 0.0, True, {"wings": (0.6 + 0.6 * math.sin(t * 24), 0.6 + 0.6 * math.sin(t * 24 + 0.5))}
    if n == "pop":
        if t < T.LANDING:                                   # backwards somersault over the ants, onto Tumble's nose
            u = clampu(t, T.POP, T.LANDING); end = nose_seat(mats)
            p = lerp(hp, end, u); p[1] += 1.1 * math.sin(math.pi * u)
            return p, lerp(PIP_YAW_STUCK, st["yaw"], ease(clampu(u, 0.6, 1.0))), True, 0.0, False, {"wings": (1.2, 1.2), "flip": u}
        d = t - T.LANDING
        return nose_seat(mats), st["yaw"], False, 0.0, True, ({"cling": math.exp(-d * 6) * math.cos(d * 18)} if d < 0.6 else {"cheer": d > 1.1})
    if n in ("moral", "chorus"):
        st_m = tumble(SH["moral"][0] + 1e-3)
        return dance_pip(t, st, mats, n, arrive_from=nose_seat(fox_mats(st_m)))
    top = paw_seat(mats[2])                                 # button: cheering on the paw
    return top, 0.35, False, 0.0, True, {"cheer": True}
STUCK_TRIES = [x for x in ([T.line("Problem B")["t0"] + 0.15] if T.line("Problem B") else []) + T.STUCK[:1]]

def pip_post(t, pip):
    """extra transform for Pip's clay toffee stretch (stuck tries, tugs) and the somersault; None if none"""
    n = T.shot_at(t)[1]; feet = pip_feet_world()
    if n == "stuck":
        s = 1.0
        for ta in STUCK_TRIES:
            d = t - ta
            if 0 <= d < 0.45: s = max(s, 1 + 0.6 * math.sin(math.pi * min(d / 0.3, 1.0) / 2) ** 2 if d < 0.3 else 1.6)
            elif 0.45 <= d < 1.3: s = max(s, 1 + 0.6 * math.exp(-(d - 0.45) * 6) * math.cos((d - 0.45) * 18)) if True else s
        if s != 1.0: return stretch_M(feet, np.array([0, 1.0, 0]), s)
        return None
    if n == "tug" or (n == "pop" and t < T.POP + 0.12):
        s, _ = tug_env(t)
        return stretch_M(feet, STRETCH_AX, s) if abs(s - 1) > 1e-4 else None
    if n == "pop" and "flip" in pip[5]:
        u = pip[5]["flip"]; c = pip[0] + np.array([0, 0.2, 0])
        ang = -2 * math.pi * ease(u)                        # two-thirds of the way it has done one full backwards flip
        ax = PIP_YAW_STUCK
        R = trans(*c) @ roty(ax) @ rotx(ang) @ roty(-ax) @ trans(*(-c))
        s = 1 + 0.5 * math.exp(-u * 8)                       # still a bit stretched as he pops loose
        return R @ stretch_M(pip[0], STRETCH_AX, s)
    return None

# ---------------- camera ----------------
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    if name == "hook_water":                                # low, at water level, on the spinning ant
        c = twig_c(t)
        return fit_cam(np.array([c[0] + 0.25, 0.4, c[2] + 0.2]), lerp(14, 6, e), 3, 0.85, 0.8, lift=0.05)
    if name == "title_wide":
        return (fit_cam(np.array([0.5, 0.75, -3.95]), 4, 16, 3.9, 2.9, lift=0.02) if not WIDE else fit_cam(np.array([0.7, 1.75, -3.95]), 4, 10, 3.9, 2.5, lift=0.0))
    if name == "leaf_pickup":                               # tracking Pip and the leaf
        a = SH[name][0]; g = np.array([PIP_GRAB[0], 0.45, PIP_GRAB[1] - 0.4])
        tgt = lerp(g, REL_P + np.array([0, -0.25, -0.4]), ease(clampu(t, a + 0.3, T.DROP)))
        return fit_cam(tgt, -30, 10, 1.4, 1.2)
    if name == "leaf_drop":                                 # overhead on the stream
        c = twig_c(T.ANT_HOP)
        return fit_cam(np.array([c[0] + 0.3, 0.1, -5.25]), 0, 72, 1.8, 1.3, lift=0.02)
    if name == "thank_you":                                 # macro, low, side-on to the ant and Pip
        return fit_cam(np.array([(ANT_BANK[0] + PIP_BANK[0]) / 2 - 0.78, 0.22, -4.5]), lerp(-14, -8, e), 7, 1.35, 0.75, lift=0.05)
    if name == "fly_off":                                   # following Pip off and Tumble along the bank
        return fit_cam(np.array([lerp(0.8, 1.4, e), 1.5 if not WIDE else 1.7, -3.3]), lerp(-8, 2, e), 8, 2.3, 2.4)
    if name == "splat":                                     # low close on the honey puddle
        return fit_cam(np.array([HP[0] - 0.05, 0.42, HP[1]]), lerp(30, 24, e), 7, 1.0, 0.95, lift=0.05)
    if name == "stuck":                                     # close, side-on
        return fit_cam(np.array([HP[0], 0.5, HP[1]]), lerp(-6, 4, e), 6, 0.95, 1.05, lift=0.06)
    if name == "ants_march":                                # wide: Tumble, the line marching in, Pip in the honey
        a = SH[name][0]; tp = lerp(np.array([-0.2, 0.35, -3.3]), np.array([1.3, 0.45, -2.9]), ease(u))
        return fit_cam(tp + (np.array([0, 0.6, 0]) if WIDE else 0), lerp(-8, -22, e), 13, 2.1, 1.3 if not WIDE else 1.9)
    if name == "tug":                                       # side-on along the line
        return fit_cam(np.array([HP[0] - 0.85, 0.5, HP[1] - 0.5]), lerp(-6, -18, e), 8, 2.0, 0.9 if not WIDE else 1.7, lift=0.06)
    if name == "pop":                                       # wide side: the pop and the somersault onto his nose
        k = ease(clampu(t, T.POP + 0.05, T.LANDING))
        return fit_cam(np.array([lerp(1.15, 0.35, k), lerp(1.3, 1.5, k), -3.5]), -4, 8, lerp(1.95, 1.45, k), lerp(2.2, 1.7, k), lift=0.05)
    if name == "moral":
        return fit_cam(np.array([TS[0] + 0.05, lerp(1.3, 1.38, e), TS[1]]), lerp(8, 3, e), 5, lerp(1.75, 1.55, e), lerp(1.45, 1.25, e))
    if name == "chorus":
        return fit_cam(np.array([TS[0] + 0.1, 1.15, TS[1]]), 4, 6, 1.75, 1.45)
    tgt = np.array([lerp(TS[0] + 0.2, TS[0] - 0.5, e), lerp(1.15, 1.8, e), TS[1]])
    return fit_cam(tgt, 4, lerp(6, 18, e), lerp(1.75, 3.6, e), lerp(1.45, 2.4, e), lift=0.04)

# ---------------- draws ----------------
PIP_AT_DROP = None
def build_draws(t):
    global PIP_AT_DROP
    draws, contacts = [], []
    meadow_backdrop(draws, t)
    _eye = camera(t)[0]                                         # no meadow flower right in front of the lens
    draw_flowers(draws, t, [f for f in FLOWERS if (f[0] - _eye[0]) ** 2 + (f[1] - _eye[2]) ** 2 > 1.6])
    for (x, z, s) in [(T0[0] + 1.3, T0[1] - 0.5, 0.18), (TS[0] - 1.5, TS[1] + 0.3, 0.16), (FLOWER[0] + 1.1, FLOWER[1] + 0.2, 0.2)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))
    n = T.shot_at(t)[1]
    # the big golden flower, its drip and the honey puddle
    draws.append((SC["flower"], FLOWER_M @ rotz(0.02 * math.sin(t * 1.3)), U(mat=0, bump=0.4, tint=(1.0, 0.8, 0.32), tintMix=-1.0, obj="flower"), True))
    hp_y = surf(*HPC)
    draws.append((PR["ball"], trans(HPC[0], hp_y, HPC[1]) @ scale(*HP_R), U(mat=2, bump=0.0, tint=HONEY, tintMix=1.0, obj="honey"), False))
    ph = (t % (2 * T.BAR)) / (2 * T.BAR)                        # a drop swells at the petal tip, falls, plips into the puddle
    grow = 0.035 + 0.03 * min(ph / 0.8, 1.0)
    draws.append((PR["ball"], trans(*(DRIP_TIP - np.array([0, grow * 0.9, 0]))) @ scale(grow * 0.8, grow * 1.3, grow * 0.8), U(mat=2, bump=0.0, tint=HONEY, tintMix=1.0), False))
    if ph > 0.8:
        u = (ph - 0.8) / 0.2; y = lerp(DRIP_TIP[1] - 0.08, hp_y + 0.03, u * u)
        if u < 0.97:
            draws.append((PR["ball"], trans(DRIP_TIP[0], y, DRIP_TIP[2]) @ scale(0.04, 0.055, 0.04), U(mat=2, bump=0.0, tint=HONEY, tintMix=1.0), False))
    # twig raft
    c = twig_c(t); M = trans(*c) @ roty(twig_spin(t)) @ rotz(math.pi / 2) @ scale(TWIG_R / 0.05, TWIG_L, TWIG_R / 0.05) @ trans(0, -0.5, 0)
    draws.append((PR["stick"], M, U(mat=0, bump=0.6, tint=(0.6, 0.42, 0.28), tintMix=1.0, obj="twig"), True))
    st = tumble(t); mats = fox_mats(st); R, Mh, arms, legs = mats
    draw_tumble(draws, contacts, t, st, mats)
    pip = pip_state(t, st, mats)
    i0 = len(draws)
    Mp = draw_pip(draws, contacts, t, pip, arms)
    post = pip_post(t, pip)
    if post is not None:
        for j in range(i0, len(draws)):
            m_, M_, u_, c_ = draws[j]; draws[j] = (m_, post @ M_, u_, c_)
        Mp = post @ Mp
    if PIP_AT_DROP is None:
        st_d = tumble(T.DROP - 1e-3); pd = pip_state(T.DROP - 1e-3, st_d, fox_mats(st_d))
        PIP_AT_DROP = trans(*pd[0]) @ roty(pd[1]) @ scale(1.1)
    # the leaf
    LM, kind = leaf_M(t, Mp)
    draws.append((E2["bigleaf"], LM, U(mat=0, bump=0.3, obj="leaf"), True))
    if kind == "fall" or (kind == "water" and t < LAND_T + 0.6):
        lc = leaf_center(LAND_T)[0]
        puff(draws, lc + np.array([0, 0.02, 0]), LAND_T, t, n=10, size=0.035, spread=0.7, dur=0.5, tint=(0.85, 0.95, 1.0), axis=(0, 0.3, 0))
    # ants
    for (a, obj, hero, sing) in ants(t):
        if n in ("moral", "chorus", "button_crane") and hero: continue
        Ma = draw_ant(draws, contacts, t, a, obj, hero=hero, sing=sing)
        if n == "button_crane" and obj == "ant3":              # the honey drop, carried like a golden ball
            draws.append((PR["ball"], Ma @ trans(0, 0.3, -0.05) @ scale(0.12), U(mat=2, bump=0.0, tint=HONEY, tintMix=1.0), False))
    if n in ("moral", "chorus", "button_crane"):            # the hero ant rides Tumble's other paw and sings the moral
        hp1 = hand_pos(arms, 1) + np.array([0, 0.085, 0])
        yaw = math.atan2(-0.6, 1.0)
        draw_ant(draws, contacts, t, dict(p=hp1, yaw=-0.35, feelers=1.2 if n != "moral" else 0.8, s=ANT_S), "ant0", hero=True, sing=True)
    # whistle notes from the ant
    if n == "ants_march" and T.WHISTLE <= t < T.WHISTLE + 1.4:
        hb = np.array([ANT_BANK[0], surf(*ANT_BANK) + 0.3, ANT_BANK[1]])
        for k in range(3):
            d = t - (T.WHISTLE + 0.25 * k)
            if 0 <= d < 0.9:
                q = hb + np.array([0.15 * k + 0.25 * d, 0.5 * d, 0.05]); sc_ = 0.045 * (1 - d / 0.9) + 0.02
                draws.append((PR["ball"], trans(*q) @ scale(sc_, sc_ * 0.8, sc_ * 0.8), U(mat=0, bump=0.0, tint=(1.0, 0.92, 0.4), tintMix=1.0), False))
                s_ = seg_M(q + np.array([sc_ * 0.8, 0, 0]), q + np.array([sc_ * 0.8, sc_ * 3.0, 0]), 0.01)
                if s_ is not None: draws.append((PR["stick"], s_, U(mat=0, bump=0.0, tint=(1.0, 0.92, 0.4), tintMix=1.0), False))
    # splat drops and the honey strings at the pop
    puff(draws, np.array([HP[0], surf(*HP) + 0.1, HP[1]]), T.SPLAT, t, n=10, size=0.04, spread=0.7, dur=0.45, tint=HONEY, axis=(0, 0.6, 0.0))
    if n == "pop" and T.POP <= t < T.POP + 0.3:
        feet = pip_feet_world()
        top = Mp @ np.array([0, 0.0, 0, 1.0])
        for k, dx in enumerate((-0.05, 0.0, 0.05)):
            A = feet + np.array([dx, 0, 0.03 * (k - 1)]); B = lerp(A, top[:3], 0.95)
            Ms = seg_M(A, B, 0.012 * (1 - (t - T.POP) / 0.3) + 0.003)
            if Ms is not None: draws.append((PR["stick"], Ms, U(mat=2, bump=0.0, tint=HONEY, tintMix=1.0), False))
    puff(draws, pip_feet_world() + np.array([0, 0.1, 0]), T.POP + 0.25, t, n=8, size=0.035, spread=0.6, dur=0.4, tint=HONEY, axis=(0, 0.4, 0))
    if n == "pop": puff(draws, nose_seat(mats) + np.array([0, 0.15, 0.1]), T.LANDING, t, n=8, size=0.04, spread=0.6, dur=0.4, tint=(1.0, 0.95, 0.75), axis=(0, 0.2, 0.3))
    return draws, contacts

HOOKS.update(build=build_draws, camera=camera, tumble=tumble,
             ground_objs=lambda t: ("fox", "pip") + tuple(f"ant{k}" for k in range(6)),
             qa_ignore={("pip", "honey"), ("honey", "pip"), ("ant0", "pip"), ("pip", "ant0")})   # Pip's feet are stuck in the honey on purpose
if __name__ == "__main__":
    main()
