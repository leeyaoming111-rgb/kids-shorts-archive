"""Tumble & Pip Fables 6: Busy Little Ants  (Aesop: The Ant and the Grasshopper)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa"""
from fablekit import *

COLORS["ant"] = (205, 95, 60)                             # caption colour for "ant(s)" (the ants' cocoa-red)

# =====================================================================================================================
# ANTS (reused by Fable 10, "One Good Turn": copy this block as is)
# A low-poly clay ant: three kit balls (head, thorax, abdomen), six stick legs walking a tripod gait, two stick feelers
# with ball tips, big kit eyes and pink cheeks. Local frame: forward +z, up +y, feet on y = 0. ANT_S = 1.0 is about
# 0.31 long and 0.17 tall (0.22 with a seed held over its head).
#   draw_ant(draws, contacts, t, pos, yaw, ...)   one ant standing on the ground point pos (x, ground y, z)
#   AntPath(points) / ant_line(...)               an instanced marching line along a polyline
# Every part is tagged obj="ant" (one QA object for the whole crowd; a carried seed belongs to its ant).
# =====================================================================================================================
ANT_S = 0.8
ANT_BODY = (0.62, 0.28, 0.2)                              # warm cocoa-red clay
ANT_BELLY = (0.78, 0.42, 0.3)
ANT_LEG = (0.36, 0.18, 0.14)
SEED_C = (0.96, 0.82, 0.52)
ANT_PARTS = [((0, 0.105, -0.135), (0.085, 0.072, 0.1), ANT_BELLY),     # abdomen
             ((0, 0.095, -0.01), (0.05, 0.045, 0.055), ANT_BODY),      # thorax
             ((0, 0.125, 0.095), (0.072, 0.066, 0.064), ANT_BODY)]     # head (big, for a friendly face)
ANT_HIPS = [(0.035, 0.035), (0.04, -0.005), (0.035, -0.045)]         # (x, z) of each leg pair on the thorax
ANT_SPLAY = [0.07, 0.0, -0.07]                                         # front legs reach forward, back legs back
ANT_EYES = [(0.03, 0.15, 0.142), (-0.03, 0.15, 0.142)]
ANT_EYE_R = 0.026
ANT_SEED_AT = (0, 0.215, 0.12)                                         # a carried seed, held up over the head
def ant_matrix(pos, yaw, s=ANT_S, bob=0.0, pitch=0.0, roll=0.0):
    return trans(pos[0], pos[1] + bob, pos[2]) @ roty(yaw) @ rotx(pitch) @ rotz(roll) @ scale(s)
def draw_ant(draws, contacts, t, pos, yaw, phase=0.0, s=ANT_S, walk=1.0, carry=None, wave=0.0, pitch=0.0, roll=0.0,
             look=0.0, obj="ant", seed_c=SEED_C):
    """one ant. pos: ground point under the ant. phase: gait phase (radians, advance it with distance walked).
    walk: 0 standing .. 1 full stride. carry: None or seed size (1.0 = a normal seed) held over the head.
    wave: feelers waving (0..1, a cheer). look: head turn (radians). Returns the body matrix."""
    bob = 0.006 * walk * abs(math.sin(phase))
    M = ant_matrix(pos, yaw, s, bob * s, pitch, roll)
    uo = U(mat=0, bump=0.5, seed=11.0, obj=obj)
    for k, (c, r, col) in enumerate(ANT_PARTS):
        Mk = M @ trans(*c)
        if k == 2: Mk = Mk @ roty(look)
        draws.append((PR["ball"], Mk @ scale(*r), dict(uo, tint=col, tintMix=1.0), True))
    Mh = M @ trans(*ANT_PARTS[2][0]) @ roty(look) @ trans(*(-np.array(ANT_PARTS[2][0])))
    eyes(draws, Mh, ANT_EYES, ANT_EYE_R, blink(t, phase * 0.37 % 3.0, 3.1))
    for sx in (1, -1):                                                 # cheeks
        draws.append((PR["ball"], Mh @ trans(sx * 0.052, 0.112, 0.135) @ scale(0.016, 0.011, 0.008), U(mat=0, bump=0.0, tint=(1.0, 0.62, 0.62), tintMix=1.0), False))
    for sx in (1, -1):                                                 # feelers
        w = wave * 0.5 * math.sin(t * 11 + sx)
        a = np.array([sx * 0.025, 0.18, 0.12]); b = np.array([sx * (0.065 + 0.02 * w), 0.27 + 0.02 * math.sin(t * 3 + phase), 0.165 + 0.03 * w])
        Ms = seg_M(apply(Mh, a), apply(Mh, b), 0.0075 * s)
        if Ms is not None: draws.append((PR["stick"], Ms, U(mat=0, bump=0.0, tint=ANT_LEG, tintMix=1.0), False))
        draws.append((PR["ball"], Mh @ trans(*b) @ scale(0.017), U(mat=0, bump=0.0, tint=ANT_BODY, tintMix=1.0), False))
    for i, ((hx, hz), sp) in enumerate(zip(ANT_HIPS, ANT_SPLAY)):    # tripod gait: L0 R1 L2 together, then R0 L1 R2
        for sx in (1, -1):
            grp = (i + (0 if sx > 0 else 1)) % 2
            ph = phase + grp * math.pi
            fz = 0.028 * walk * math.sin(ph); fy = 0.022 * walk * max(0.0, math.cos(ph))
            hip = np.array([sx * hx, 0.09, hz]); knee = np.array([sx * (hx + 0.07), 0.115 + fy * 0.5, hz + sp * 0.6 + fz * 0.5])
            foot = np.array([sx * (hx + 0.1), 0.012 + fy, hz + sp + fz])
            uo2 = U(mat=0, bump=0.0, tint=ANT_LEG, tintMix=1.0, obj=obj)
            for a, b in ((hip, knee), (knee, foot)):
                Ms = seg_M(apply(M, a), apply(M, b), 0.011 * s)
                if Ms is not None: draws.append((PR["stick"], Ms, uo2, True))
    if carry:
        draws.append((PR["ball"], M @ trans(*ANT_SEED_AT) @ rotx(0.25) @ scale(0.042 * carry, 0.032 * carry, 0.062 * carry), dict(uo, tint=seed_c, tintMix=1.0), True))
    contacts.append((pos[0], pos[2], 0.16 * s / 0.8, 0.6))
    return M
class AntPath:
    """polyline on the ground; at(s) -> (x, z, yaw). s < 0 or beyond the end extends the first / last leg"""
    def __init__(self, pts):
        self.p = [np.asarray(q, float) for q in pts]
        self.L = [float(np.linalg.norm(self.p[i + 1] - self.p[i])) for i in range(len(self.p) - 1)]
        self.total = sum(self.L)
    def at(self, s, round_r=0.35):
        if s <= 0:
            d = (self.p[1] - self.p[0]) / self.L[0]; q = self.p[0] + d * s
            return q[0], q[1], math.atan2(d[0], d[1])
        acc = 0.0
        for i, L in enumerate(self.L):
            if s <= acc + L or i == len(self.L) - 1:
                d = (self.p[i + 1] - self.p[i]) / L; u = s - acc; q = self.p[i] + d * u
                yaw = math.atan2(d[0], d[1])
                if i + 1 < len(self.L) and L - u < round_r:              # turn smoothly into the next leg
                    d2 = (self.p[i + 2] - self.p[i + 1]) / self.L[i + 1]
                    k = (round_r - (L - u)) / (2 * round_r); yaw = math.atan2(*(d * (1 - k) + d2 * k))
                elif i > 0 and u < round_r:
                    d0 = (self.p[i] - self.p[i - 1]) / self.L[i - 1]
                    k = (round_r - u) / (2 * round_r); yaw = math.atan2(*(d * (1 - k) + d0 * k))
                return q[0], q[1], yaw
            acc += L
def ant_line(draws, contacts, t, path, svals, carry=1.0, walk=1.0, stride=0.1, skip=None):
    """an instanced marching line: one ant at each arc length in svals (gait phase follows the distance walked)"""
    for k, s in enumerate(svals):
        if skip and skip(k, s): continue
        x, z, yaw = path.at(s)
        draw_ant(draws, contacts, t, (x, surf(x, z), z), yaw, phase=s / stride * math.pi + k * 0.7, walk=walk,
                 carry=carry if not callable(carry) else carry(k, s))
# ============================================ end of the ant block ===================================================

# ---------------- world: the anthill corner of Picnic Meadow (autumn) ----------------
HILL = np.array([1.7, -0.7]); HILL_R = (0.78, 0.46, 0.7); HILL_YAW = 0.25
PILE = (-1.75, -0.35)                                      # the leaf pile Tumble plays in
NOSE_Z = 2.2                                               # the ant road runs along z = 2.2 in front of the pile
A0 = (-9.0, NOSE_Z); A1 = (-0.3, NOSE_Z)
def _hill_local(): return trans(HILL[0], ground_h(*HILL) - 0.06, HILL[1]) @ roty(HILL_YAW)
HILL_M = _hill_local() @ scale(*HILL_R)
DOOR_DIR = np.array([-0.45, 0.89]); DOOR_DIR /= np.linalg.norm(DOOR_DIR)
def hill_surface(dirxz, y):
    """point on the mound's surface in horizontal direction dirxz at height y above its base, and the normal"""
    Mi = np.linalg.inv(HILL_M)
    lo = Mi @ np.array([HILL[0] + dirxz[0], ground_h(*HILL) - 0.06 + y, HILL[1] + dirxz[1], 1.0])
    uy = lo[1]; h = math.sqrt(max(1 - uy * uy, 1e-6)); hd = np.array([lo[0], lo[2]]); hd /= np.linalg.norm(hd)
    pl = np.array([hd[0] * h, uy, hd[1] * h, 1.0])
    p = (HILL_M @ pl)[:3]; n = np.linalg.inv(HILL_M[:3, :3]).T @ pl[:3]; n /= np.linalg.norm(n)
    return p, n
DOOR_P, DOOR_N = hill_surface(DOOR_DIR, 0.13)             # middle of the doorway
DOOR_GROUND = np.array([DOOR_P[0], DOOR_P[2]]) + DOOR_DIR * 0.12
A2 = tuple(DOOR_GROUND + DOOR_DIR * 1.25)
ROAD = AntPath([A0, A1, A2, tuple(DOOR_GROUND), tuple(HILL + DOOR_DIR * 0.05)])
S_DOOR = ROAD.total - float(np.linalg.norm(DOOR_GROUND - (HILL + DOOR_DIR * 0.05)))
HILL_TOP = apply(HILL_M, (0, 1.0, 0)) + UP + np.array([0, -0.01, 0])
GAG = (-2.2, NOSE_Z)                                       # Tumble straddles the ant road here, facing along it
GAG2 = (-2.0, NOSE_Z - 0.95)                               # ...and steps back off it at the cut
LIE = (-1.7, 0.45)                                         # hook: on his tummy at the front of the pile, nose to the road
SIDE = np.array([DOOR_DIR[1], -DOOR_DIR[0]])               # along the hill front, to the right of the door (seen from the front)
LEAF_PLATE = DOOR_GROUND + DOOR_DIR * 0.95                 # the big leaf the ants set the seeds on
SNACK_LIE = DOOR_GROUND + DOOR_DIR * 2.0                  # Tumble on his tummy, facing the door
MSPOT = tuple(DOOR_GROUND + DOOR_DIR * 1.55 - SIDE * 0.75)
MOVE0 = (MSPOT[0] - 2.0, MSPOT[1] + 0.1)                   # next morning he walks in from the left with the seed
BIG_SEED_AT = np.array([MSPOT[0] + 0.85, MSPOT[1]])         # the biggest seed, set down near the door
PIP_WAIT = BIG_SEED_AT + np.array([0.55, -0.45])           # Pip waits here next morning, then hops to the paw
KNOCK_AT = np.array([DOOR_P[0], DOOR_P[2]]) + DOOR_DIR * 0.46   # Pip's spot: a full peck (pitch 0.6) reaches the door
WATCHERS = [DOOR_GROUND + SIDE * (0.35 + 0.3 * k) + DOOR_DIR * (0.25 + 0.12 * k) for k in range(5)]   # ants who watch the dance
STASH = np.array([-0.78, NOSE_Z - 0.42])                   # loose seeds by the road (Pip takes one)
PIPW = np.array([-1.15, NOSE_Z - 0.5])                     # Pip by the road (pile side), singing
# ant march: one arc-length offset per ant; they hurry home once the snow starts
ANT_V = 0.55; ANT_GAP = 0.36
N_MARCH = 34
S0 = [7.7 - k * ANT_GAP for k in range(N_MARCH)]
def march_s(t):
    hurry = 0.0 if t < T.FLAKE_LAND + 0.4 else min(t - (T.FLAKE_LAND + 0.4), 1.5) ** 2 / 3.0 + max(0.0, t - (T.FLAKE_LAND + 1.9)) * 1.0
    return ANT_V * t + hurry
S_INSIDE = S_DOOR + 0.5

# autumn trees (built from primitives: a clay trunk and a cluster of canopy balls)
AUTUMN = [(0.98, 0.58, 0.22), (0.95, 0.42, 0.24), (0.99, 0.78, 0.3), (0.86, 0.5, 0.25)]
TREES = [(-4.6, -3.4, 1.15, 0), (4.6, -3.8, 1.3, 1), (-7.5, -9.0, 1.6, 2), (6.8, -9.5, 1.7, 3), (-10.5, -13, 1.9, 1),
         (10.0, -14, 2.0, 0), (2.5, -15, 1.7, 2), (-4.0, -16, 1.8, 3)]
_rng = np.random.default_rng(6)
GROUND_LEAVES = []
while len(GROUND_LEAVES) < 110:
    x, z = _rng.uniform(-7, 7), _rng.uniform(-6, 5)
    if abs(z - NOSE_Z) < 0.35 and x < 0.5: continue          # keep the ant road clear
    if np.linalg.norm(np.array([x, z]) - HILL) < 1.0: continue
    if -6.6 < z < -4.4: continue                               # not in the stream
    GROUND_LEAVES.append((x, z, _rng.uniform(0, 6.28), AUTUMN[len(GROUND_LEAVES) % 4], _rng.uniform(1.1, 1.6)))
PILE_LEAVES = []
for k in range(80):
    r = 0.8 * math.sqrt(_rng.uniform(0, 1)); a = _rng.uniform(0, 6.28)
    h = 0.4 * (1 - (r / 0.85) ** 2) * _rng.uniform(0.55, 1.0)
    PILE_LEAVES.append(((r * math.cos(a), h, r * math.sin(a)), _rng.uniform(0, 6.28, 3), _rng.uniform(2.6, 3.4), AUTUMN[k % 4]))
MUSH = [(-3.9, 0.4, 0.17), (3.2, 1.2, 0.2), (0.6, -2.4, 0.15)]

# ---------------- sky: autumn afternoon, cooling as the snow comes, a bright next morning ----------------
SKY_AUT = ((0.5, 0.68, 0.92), (0.8, 0.85, 0.95), (1.0, 0.86, 0.7))
SKY_COLD = ((0.6, 0.68, 0.8), (0.79, 0.83, 0.9), (0.9, 0.9, 0.93))
SKY_MORN = ((0.44, 0.7, 0.96), (0.74, 0.88, 1.0), (1.0, 0.95, 0.86))
def sky(t):
    if t >= SH["next_day"][0]: return SKY_MORN
    u = ease(clampu(t, SH["snowflake"][0] + 0.2, SH["snowflake"][0] + 2.6))     # a slow 2.4 s ramp (no-flash rule)
    return tuple(tuple(lerp(a, b, u)) for a, b in zip(SKY_AUT, SKY_COLD))
def cold(t): return 0.0 if t >= SH["next_day"][0] else ease(clampu(t, SH["snowflake"][0] + 0.2, SH["snowflake"][0] + 2.6))

# ---------------- Tumble ----------------
CARRY_ARM = [0.25, 1.15]                                   # both paws out in front, holding something
TOSS_ARM = [0.45, 2.3]                                     # paws flung up after the toss
def lie_pose(st, spot, yaw):
    """on his tummy, chin up (pitched forward about the middle of the body; fox_mats_p applies it)"""
    st["x"], st["z"] = spot; st["yaw"] = yaw; st["pitch"] = 1.45; st["y"] = -0.36
    st["head"] = [-1.25, st["head"][1], 0.0]; st["arms"] = [[0.25, 2.6], [0.25, 2.6]]; st["legs"] = [0.0, 0.0]
    st["tail"] = 0.6 * math.sin(st.get("_t", 0) * 2.2)
def tumble(t):
    st = tumble_base(t); st["_t"] = t; n = T.shot_at(t)[1]
    st["x"], st["z"] = PILE[0] + 0.1, PILE[1] + 0.55; st["yaw"] = 0.0
    if n == "hook_ants":                                    # eyes follow the ants passing his nose
        lie_pose(st, LIE, 0.0); st["head"][1] = 0.35 * math.sin(t * 1.3)
    elif n == "title_wide":
        st["arms"][0] = [1.1 + 0.35 * math.sin(t * 9), 0.4]; st["yaw"] = 0.25           # waves
    elif n == "leaf_play":                                   # hops into the pile on "leaves" and on "play"
        st["yaw"] = 0.15; st["arms"] = [[0.6, 0.5], [0.6, 0.5]]
        for k, j in enumerate(T.LEAF_HOPS):
            d = t - j
            if 0 <= d < 0.6:
                st["y"] += 0.5 * math.sin(math.pi * d / 0.6); st["arms"] = [[2.2, 0.3], [2.2, 0.3]]; st["legs"] = [0.08, 0.08]
            if 0.6 <= d < 0.9: st["sq"] -= 0.1 * math.exp(-(d - 0.6) * 9) * math.cos((d - 0.6) * 25)
        if t > T.LEAF_HOPS[-1] + 0.6:                        # "come and play!": waves to the ants
            st["arms"][0] = [1.2 + 0.35 * math.sin(t * 9), 0.5]; st["head"][1] = 0.2
    elif n in ("pip_work", "pip_carry"):                     # still in the pile, listening
        st["yaw"] = 0.1; st["arms"] = [[0.35, 0.3], [0.35, 0.3]]; st["head"][2] = 0.12 * math.sin(t * 2)
    elif n == "ant_hat":                                     # tosses a seed onto his head, legs wide, the ant road under him
        st["x"], st["z"] = GAG; st["yaw"] = math.pi / 2; st["splay"] = 0.3; st["y"] += 0.1; st["legs"] = [-0.1, -0.1]
        dip = math.sin(math.pi * clampu(t, T.SEED_LIFT, T.TOSS))
        up = ease(clampu(t, T.TOSS - 0.05, T.TOSS + 0.15))
        arm = lerp(lerp(CARRY_ARM, [0.2, 0.75], dip), TOSS_ARM, up)
        st["arms"] = [arm.tolist(), arm.tolist()]; st["head"][0] = -0.25 * up
        st["sq"] += 0.05 * dip
        if t > T.SEED_ON:                                    # lands on his crown: arms out for balance, wobbles
            out = ease(clampu(t, T.SEED_ON, T.SEED_ON + 0.4))
            st["arms"] = [lerp(TOSS_ARM, [1.5, 0.2], out).tolist(), lerp(TOSS_ARM, [1.5, 0.2], out).tolist()]
            st["head"][0] = -0.25 * (1 - out)
            w = clampu(t, T.SEED_ON + 0.3, T.SEED_ON + 0.8)
            st["roll"] = 0.07 * w * math.sin((t - T.SEED_ON) * 7.5)
            st["head"][2] = -0.08 * w * math.sin((t - T.SEED_ON) * 7.5)
        if t > T.TIP_OFF - 0.25:                             # arms drop as it slides off his far side
            dn = ease(clampu(t, T.TIP_OFF - 0.25, T.TIP_OFF + 0.1))
            st["arms"] = [lerp([1.5, 0.2], [0.35, 0.2], dn).tolist(), lerp([1.5, 0.2], [0.35, 0.2], dn).tolist()]
            st["head"][0] = 0.25 * ease(clampu(t, T.TIP_OFF, T.TIP_OFF + 0.4)); st["roll"] *= 1 - clampu(t, T.TIP_OFF, T.TIP_OFF + 0.4)
    elif n in ("snowflake", "chilly"):
        st["x"], st["z"] = GAG2; st["yaw"] = 0.55
        if n == "snowflake":                                 # looks up at the falling flake, cross-eyed when it lands
            u = clampu(t, SH[n][0], T.FLAKE_LAND)
            st["head"][0] = -0.3 * (1 - u) + 0.08 * u
            if t > T.RUMBLE - 0.3:                           # hugs his rumbling tummy
                h = ease(clampu(t, T.RUMBLE - 0.3, T.RUMBLE + 0.1))
                st["arms"] = [lerp([0.15, 0.0], [0.0, 1.0], h).tolist(), lerp([0.15, 0.0], [0.0, 1.0], h).tolist()]
                st["sq"] += 0.03 * math.sin((t - T.RUMBLE) * 30) * math.exp(-max(0, t - T.RUMBLE) * 2)
        else:
            st["arms"] = [[0.0, 1.0], [0.0, 1.0]]
            d = t - T.SNEEZE
            if -0.6 < d < 0:                                 # ah... (head back)
                st["head"][0] = -0.3 * ease(clampu(t, T.SNEEZE - 0.6, T.SNEEZE - 0.1))
            elif 0 <= d < 0.5:                               # CHOO!
                st["head"][0] = -0.3 + 0.55 * math.sin(math.pi * min(d / 0.25, 1.0) / 2); st["sq"] -= 0.06 * math.exp(-d * 8)
            elif d >= 0.5:
                st["head"][0] = 0.25 * (1 - clampu(t, T.SNEEZE + 0.5, T.SNEEZE + 0.9))
                st["x"] += 0.012 * math.sin(t * 40) * (1 - clampu(t, SH[n][1] - 0.6, SH[n][1]))   # shiver
    elif n == "knock":                                       # watches from behind Pip
        st["x"], st["z"] = SNACK_LIE + DOOR_DIR * 0.4; st["yaw"] = math.atan2(-DOOR_DIR[0], -DOOR_DIR[1])
        st["arms"] = [[0.0, 1.0], [0.0, 1.0]]; st["head"][0] = 0.3
        if t > T.DOOR_OPEN: st["arms"] = [[0.5, 0.5], [0.5, 0.5]]; st["head"][0] = 0.3
    elif n == "snack":                                       # on his tummy at the leaf, nibbles a seed
        lie_pose(st, SNACK_LIE, math.atan2(-DOOR_DIR[0], -DOOR_DIR[1]))
        d = t - T.NIBBLE
        if -0.4 < d < 0.6: st["head"][0] = -1.25 + 0.3 * math.sin(math.pi * clampu(t, T.NIBBLE - 0.4, T.NIBBLE + 0.6))
    elif n == "next_day":                                    # carries the biggest seed to the door
        a = SH[n][0]
        st["arms"] = [list(CARRY_ARM), list(CARRY_ARM)]
        walk_to(st, t, MOVE0, MSPOT, a, T.SET_DOWN - 0.15, rate=2.0)
        if t >= T.SET_DOWN - 0.15:
            st["yaw"] = math.pi / 2; st["head"][0] = 0.25
            down = ease(clampu(t, T.SET_DOWN - 0.15, T.SET_DOWN + 0.25))
            st["arms"] = [lerp(CARRY_ARM, [0.3, 0.3], down).tolist(), lerp(CARRY_ARM, [0.3, 0.3], down).tolist()]
    elif n in ("moral", "chorus"):
        st["x"], st["z"] = MSPOT
        dance_tumble(st, t, n)
    else:                                                    # button: keeps the dance paw up; waves bye-bye
        st["x"], st["z"] = MSPOT; st["yaw"] = -0.05; st["arms"][0] = list(DANCE_ARM); st["head"][2] = 0.08
        st["arms"][1] = [1.2 + 0.3 * math.sin(t * 9), 0.5] if t > SH["button_crane"][0] + 0.5 else [0.3, 0.3]
    return st

def fox_mats_p(st):
    """fox_mats plus a forward pitch about the middle of the body (lying on his tummy) and splayed legs (wide stance)"""
    R, Mh, arms, legs = fox_mats(st)
    sp = st.get("splay", 0.0)
    if sp:
        legs = []
        for li in range(2):
            pv = np.array(FOXD[f"leg{li}"]["pivot"]); sgn = 1 if li == 0 else -1
            legs.append(R @ trans(0, st["legs"][li], 0) @ trans(*pv) @ rotz(sgn * sp) @ trans(*(-pv)))
    p = st.get("pitch", 0.0)
    if p == 0.0: return R, Mh, arms, legs
    root = trans(st["x"], surf(st["x"], st["z"]) + st.get("stand_h", 0.0) - 0.01 + st["y"], st["z"]) @ roty(st["yaw"])
    P = root @ trans(0, 0.8, 0) @ rotx(p) @ trans(0, -0.8, 0) @ np.linalg.inv(root)
    return P @ R, P @ Mh, [P @ a for a in arms], [P @ l for l in legs]
CROWN = (0.0, 1.88, 0.0); NOSE = (0.0, 1.368, 0.59)

# ---------------- props: seeds, the head seed, the biggest seed ----------------
HEAD_SEED_R = (0.18, 0.13, 0.27)
def head_seed(t, mats):
    """the seed Tumble balances on his head: (matrix, state) or None. Paws reach only 1.36 high, so he tosses it up:
    out in front of his snout, up, back over the crown (explicit straight legs), then it sits on his crown."""
    n = T.shot_at(t)[1]
    if n != "ant_hat": return None
    R, Mh, arms, legs = mats
    on = Mh @ trans(*CROWN) @ trans(0, HEAD_SEED_R[1] - 0.006, 0)
    if t < T.TOSS:
        held = (hand_pos(arms, 0) + hand_pos(arms, 1)) / 2 + np.array([0, 0.05, 0])
        return trans(*held) @ roty(math.pi / 2), "held"
    if t < T.SEED_ON:
        st0 = tumble(T.TOSS); a0 = fox_mats_p(st0)[2]
        p0 = (hand_pos(a0, 0) + hand_pos(a0, 1)) / 2 + np.array([0, 0.05, 0])
        legs_ = [p0, apply(Mh, (0, 1.3, 1.05)), apply(Mh, (0, 2.55, 0.95)), apply(on, (0, 0, 0))]
        u = clampu(t, T.TOSS, T.SEED_ON) * 3; i = min(int(u), 2)
        p = lerp(legs_[i], legs_[i + 1], ease(u - i) if i == 2 else u - i)
        return trans(*p) @ roty(math.pi / 2 * (1 - clampu(t, T.TOSS, T.SEED_ON))) @ rotx(2 * math.pi * clampu(t, T.TOSS, T.SEED_ON)), "toss"
    if t < T.TIP_OFF:
        w = clampu(t, T.SEED_ON + 0.3, T.SEED_ON + 0.8)
        return on @ rotz(-0.15 * w * math.sin((t - T.SEED_ON) * 7.5)), "head"
    # slides off his far side (out past the shoulder first), then drops into the leaves and bounces once
    st0 = tumble(T.TIP_OFF); M0 = fox_mats_p(st0)[1] @ trans(*CROWN) @ trans(0, HEAD_SEED_R[1] - 0.006, 0)
    p0 = apply(M0, (0, 0, 0)); side = np.array([0, 0, 1.0])
    p1 = p0 + side * 0.85 + np.array([0, -0.25, 0])
    land = np.array([SEED_ON_GROUND[0], surf(*SEED_ON_GROUND) + HEAD_SEED_R[1] - 0.01, SEED_ON_GROUND[1]])
    u = clampu(t, T.TIP_OFF, T.TIP_OFF + 0.6)
    if u < 0.4: p = lerp(p0, p1, u / 0.4)
    else: p = lerp(p1, land, ((u - 0.4) / 0.6) ** 1.6)
    p[1] += 0.06 * math.sin(math.pi * clampu(t, T.TIP_OFF + 0.6, T.TIP_OFF + 0.85))
    return trans(*p) @ rotx(-1.2 * u), "fall"
SEED_ON_GROUND = np.array([GAG[0], GAG[1] + 0.9])
BIG_SEED_R = (0.22, 0.16, 0.34)

# ---------------- Pip ----------------
def pip_ground(xz): return np.array([xz[0], surf(xz[0], xz[1]), xz[1]]) + UP
def hop_path(p0, p1, u, h=0.35):
    p = lerp(p0, p1, ease(u)); p[1] += h * math.sin(math.pi * u); return p
def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    R, Mh, arms, legs = mats
    face = apply(Mh, (0, 1.5, 0.6))
    fy = lambda p: math.atan2(face[0] - p[0], face[2] - p[2])
    if n in ("hook_ants", "title_wide", "leaf_play"):
        if n == "title_wide":                                # lands on the anthill
            a = SH[n][0]; u = clampu(t, a, a + 1.2)
            src = HILL_TOP + np.array([-1.4, 1.2, 0.6])
            if u < 1:
                p = lerp(src, HILL_TOP + np.array([0, 0.4, 0]), clampu(u, 0, 0.7) / 0.7) if u < 0.7 else lerp(HILL_TOP + np.array([0, 0.4, 0]), HILL_TOP, (u - 0.7) / 0.3)
                return p, 0.9, True, 0.0, False, {"gentle": True}
        ex = {"cheer": True} if n == "leaf_play" and any(0 <= t - j < 0.8 for j in T.LEAF_HOPS) else {}
        return HILL_TOP, -0.6, False, 0.0, True, ex
    if n == "pip_work":                                      # by the road, singing to Tumble; nods on the beat
        L = T.line("Setup B")
        p = pip_ground(PIPW)
        nod = 0.15 * max(0.0, math.sin((t - SH[n][0]) * math.pi / BEAT)) if L["t0"] < t < L["t1"] else 0.0
        ex = {"point": True} if L["t0"] < t < L["t0"] + 0.9 else {}
        return p, 0.25, False, nod, True, ex
    if n == "pip_carry":                                     # picks up a seed and hops along beside the line
        a, b = SH[n]
        p0 = pip_ground(PIPW); p1 = pip_ground(STASH + np.array([-0.2, 0.0]))
        if t < a + 0.5:
            u = clampu(t, a, a + 0.45); return hop_path(p0, p1, u, 0.15), math.atan2(p1[0] - p0[0], p1[2] - p0[2]), u < 1, 0.0, u >= 1, {}
        if t < a + 0.8:                                      # bends to pick it up
            return p1, math.pi / 2, False, 0.5 * math.sin(math.pi * clampu(t, a + 0.5, a + 0.8)), True, {"beak": t > a + 0.65}
        k = (t - (a + 0.8)) / 0.33; i = int(k); u = k - i    # little hops along the road towards the anthill
        q0 = p1 + np.array([0.22 * i, 0, 0]); q1 = p1 + np.array([0.22 * (i + 1), 0, 0])
        q0[1] = surf(q0[0], q0[2]) + PIP_FOOT; q1[1] = surf(q1[0], q1[2]) + PIP_FOOT
        return hop_path(q0, q1, u, 0.09), math.pi / 2, False, 0.0, u < 0.08 or u > 0.92, {"beak": True}
    if n in ("ant_hat", "snowflake"):
        return HILL_TOP, -0.9, False, 0.0, True, {}
    if n == "chilly":                                        # hops down from the top to the door
        a, b = SH[n]
        dst = pip_ground(KNOCK_AT)
        u = clampu(t, b - 1.6, b - 0.7)
        up = HILL_TOP + np.array([0, 0.45, 0])
        if u <= 0: return HILL_TOP, -0.9, False, 0.0, True, {}
        if u < 1:
            p = lerp(HILL_TOP, up, clampu(u, 0, 0.3) / 0.3) if u < 0.3 else lerp(up, dst + np.array([0, 0.0, 0]), ease((u - 0.3) / 0.7))
            return p, math.atan2(-DOOR_DIR[0], -DOOR_DIR[1]), True, 0.0, False, {"gentle": True}
        return dst, math.atan2(-DOOR_DIR[0], -DOOR_DIR[1]), False, 0.0, True, {}
    if n == "knock":                                         # pecks the little door on each "knock", hops aside
        p = pip_ground(KNOCK_AT)
        yaw = math.atan2(DOOR_P[0] - p[0], DOOR_P[2] - p[2])
        pk = 0.0
        for kt in T.KNOCKS:
            d = t - kt
            if 0 <= d < 0.25: pk = 0.6 * math.sin(math.pi * d / 0.25)
        aside = pip_ground(DOOR_GROUND + DOOR_DIR * 0.55 - SIDE * 0.75)
        u = clampu(t, T.DOOR_OPEN - 0.1, T.DOOR_OPEN + 0.35)
        if u > 0:
            q = hop_path(p, aside, u, 0.2)
            return q, yaw if u < 1 else math.atan2(SIDE[0], SIDE[1]) * 0.0 + yaw, u < 1, 0.0, u >= 1, {"cheer": u >= 1}
        return p, yaw, False, pk, True, {}
    if n == "snack":                                         # pecks a seed on the leaf too
        p = pip_ground(LEAF_PLATE + SIDE * 0.5 - DOOR_DIR * 0.1)
        pk = 0.0
        for k in range(3):
            d = t - (SH[n][0] + 0.5 + 0.4 * k)
            if 0 <= d < 0.22: pk = 0.5 * math.sin(math.pi * d / 0.22)
        return p, math.atan2(-SIDE[0], -SIDE[1]), False, pk, True, {}
    if n == "next_day":                                      # waits by the door with the ants, cheers the big seed
        p = pip_ground(PIP_WAIT)
        return p, math.atan2(st["x"] - p[0], st["z"] - p[2]), False, 0.0, True, {"cheer": t > T.SET_DOWN}
    if n in ("moral", "chorus"):
        return dance_pip(t, st, mats, n, arrive_from=pip_ground(PIP_WAIT))
    # button: on the paw; a snowflake lands on his head and he shakes it off
    top = paw_seat(arms)
    d = t - (SH["button_crane"][0] + 1.0)
    roll = 0.0
    if 0 <= d < 0.6: roll = 0.25 * math.sin(d * 30) * (1 - d / 0.6)
    return top, 0.35 + roll, False, 0.0, True, {"cheer": d > 0.7}

def big_seed_M(t, st, mats):
    """the biggest seed (matrix of the unit ball): carried in both paws, then set down beside the door"""
    if t < T.SET_DOWN - 0.15 or (T.shot_at(t)[1] == "next_day" and t < T.SET_DOWN + 0.25):
        arms = mats[2]
        held = (hand_pos(arms, 0) + hand_pos(arms, 1)) / 2 + np.array([0, BIG_SEED_R[1] * 0.55, 0])
        rest = np.array([BIG_SEED_AT[0], surf(*BIG_SEED_AT) + BIG_SEED_R[1] - 0.01, BIG_SEED_AT[1]])
        u = ease(clampu(t, T.SET_DOWN - 0.15, T.SET_DOWN + 0.25))
        p = lerp(held, rest, u)
        return trans(*p) @ roty(st["yaw"] + math.pi / 2) @ scale(*BIG_SEED_R)
    return trans(BIG_SEED_AT[0], surf(*BIG_SEED_AT) + BIG_SEED_R[1] - 0.01, BIG_SEED_AT[1]) @ roty(0.4) @ scale(*BIG_SEED_R)

# ---------------- camera ----------------
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    st = tumble(t)
    if name == "hook_ants":                                  # ant height, the line crossing in front of his nose
        return fit_cam(np.array([LIE[0] + 0.05, 0.42, NOSE_Z - 0.35]), lerp(8, 2, e), 6, 0.9, 0.7, lift=0.04)
    if name == "title_wide":
        return fit_cam(np.array([-0.2, 0.9, 0.6]), -4, 18, 3.4, 2.4 if not WIDE else 1.9, lift=0.03)
    if name == "leaf_play":
        return fit_cam(np.array([PILE[0] + 0.2, 1.15, PILE[1] + 1.2]), lerp(-24, -18, e), 7, 1.5, 1.55)
    if name == "pip_work":                                   # side-on macro: Pip, the line, Tumble beyond
        tgt = np.array([PIPW[0] + 0.1, 0.4, PIPW[1] + 0.25])
        return fit_cam(tgt, lerp(24, 18, e), 7, 0.8, 0.62, lift=0.04)
    if name == "pip_carry":                                  # low tracking with Pip
        pp = pip_state(t, st, fox_mats_p(st))[0]
        return fit_cam(np.array([pp[0] - 0.1, 0.35, pp[2] - 0.2]), 18, 5, 0.85, 0.6, lift=0.03)
    if name == "ant_hat":                                    # low, from the front, the line coming between his feet
        return fit_cam(np.array([GAG[0] + 0.05, lerp(1.05, 1.0, e), GAG[1]]), 90 + lerp(-12, -5, e), -4, 1.2, 1.25, lift=0.05)
    if name == "snowflake":                                  # face close-up
        fx = apply(fox_mats_p(st)[1], NOSE)
        return fit_cam(fx + np.array([0, 0.05, 0]), math.degrees(st["yaw"]) + lerp(-8, -2, e), 4, 0.6, 0.62, lift=0.08)
    if name == "chilly":
        return fit_cam(np.array([(GAG2[0] + DOOR_P[0]) / 2 - 0.2, 0.85, (GAG2[1] + DOOR_P[2]) / 2 + 0.3]), -8 + 4 * e, 14, 2.3, 1.45)
    if name == "knock":                                      # side-on at the door
        tgt = DOOR_P + DOOR_DIR3() * 0.4 + np.array([0, 0.05, 0])
        return fit_cam(tgt, side_on_yaw(DOOR_P, DOOR_P + DOOR_DIR3(), 70) + lerp(-4, 4, e), 8, 0.85, 0.7, lift=0.04)
    if name == "snack":                                      # high three-quarter over the leaf
        mid = np.array([LEAF_PLATE[0] * 0.6 + SNACK_LIE[0] * 0.4, 0.45, LEAF_PLATE[1] * 0.6 + SNACK_LIE[1] * 0.4])
        return fit_cam(mid, math.degrees(math.atan2(DOOR_DIR[0], DOOR_DIR[1])) + 180 + lerp(48, 42, e), 30, 1.3, 1.0, lift=0.04)
    if name == "next_day":                                   # tracking, low
        return fit_cam(np.array([st["x"] + 0.35, 0.95, st["z"] + 0.1]), lerp(52, 40, e), 5, 1.8, 1.35)
    if name == "moral":
        return fit_cam(np.array([MSPOT[0] + 0.25, lerp(1.35, 1.45, e), MSPOT[1]]), lerp(14, 8, e), 5, lerp(1.35, 1.15, e), lerp(1.4, 1.15, e))
    if name == "chorus":
        return fit_cam(np.array([MSPOT[0] + 0.3, 1.15, MSPOT[1]]), 8, 6, 1.45, 1.4)
    return fit_cam(np.array([MSPOT[0] + 0.2, lerp(1.25, 1.9, e), MSPOT[1] - 0.2 * e]), 6, lerp(5, 24, e), lerp(1.35, 2.4, e), lerp(1.4, 2.2, e), lift=0.04)
def DOOR_DIR3(): return np.array([DOOR_DIR[0], 0, DOOR_DIR[1]])

# ---------------- draws ----------------
FLAKE_COL = (0.86, 0.94, 1.0)
def draw_flake(draws, p, s, spin=0.0, tilt=0.6):
    M = trans(*p) @ roty(spin) @ rotx(tilt)
    for k in range(3):
        a = k * math.pi / 3
        d = np.array([math.cos(a), math.sin(a), 0.0]) * s
        Ms = seg_M(apply(M, -d), apply(M, d), 0.12 * s)
        if Ms is not None: draws.append((PR["stick"], Ms, U(mat=3, bump=0.0, tint=FLAKE_COL, tintMix=1.0), False))
    draws.append((PR["ball"], M @ scale(0.28 * s), U(mat=3, bump=0.0, tint=FLAKE_COL, tintMix=1.0), False))
_frng = np.random.default_rng(9)
FLURRY = [(_frng.uniform(-1, 1), _frng.uniform(0, 1), _frng.uniform(-1, 1), _frng.uniform(0, 6.28)) for _ in range(70)]
def flurry(draws, t, eye, tgt, amount):
    """a light snowfall in a box in front of the camera; flakes grow in at the top so none pops"""
    if amount <= 0: return
    f = tgt - eye; dist = np.linalg.norm(f); f /= dist
    rgt = np.cross(f, [0, 1, 0]); rgt /= np.linalg.norm(rgt)
    span = 0.6 * dist + 0.6
    for k, (a, b, c, ph) in enumerate(FLURRY):
        if k >= int(len(FLURRY) * amount): break
        y01 = (b - t * 0.12) % 1.0
        p = eye + f * (0.35 + (c + 1) * 0.5) * dist + rgt * a * span * 0.7 + np.array([0, (y01 - 0.5) * span * 1.3, 0])
        p = p + rgt * 0.08 * math.sin(t * 1.5 + ph)
        if p[1] < surf(p[0], p[2]) + 0.05: continue
        g = min(1.0, (1 - y01) * 8) * min(1.0, y01 * 8)
        draw_flake(draws, p, 0.03 * g * (0.5 + 0.5 * dist / 3), spin=t * 0.8 + ph, tilt=ph)

def draw_tree(draws, x, z, s, ci, t):
    g = ground_h(x, z)
    draws.append((PR["stick"], trans(x, g - 0.05, z) @ scale(3.2 * s, 1.6 * s, 3.2 * s), U(mat=0, bump=0.8, tint=(0.62, 0.44, 0.32), tintMix=1.0), True))
    for k, (dx, dy, dz, r) in enumerate([(0, 2.1, 0, 0.95), (0.6, 1.8, 0.2, 0.62), (-0.62, 1.85, -0.1, 0.6), (0.1, 2.6, 0.05, 0.6)]):
        draws.append((PR["ball"], trans(x + dx * s, g + dy * s, z + dz * s) @ roty(x) @ scale(r * s, r * s * 0.9, r * s),
                      U(mat=0, bump=0.8, tint=AUTUMN[(ci + k) % 4], tintMix=0.85, seed=3.0 + k), True))
def backdrop(draws, t):
    c = cold(t)
    gt = tuple(lerp((1.12, 1.0, 0.72), (1.02, 1.0, 0.92), c))
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.8, tint=gt, tintMix=-1.0), False))
    for (x, z, s, ci) in TREES: draw_tree(draws, x, z, s, ci, t)
    draws.append((SC["cottage"], trans(7.5, ground_h(7.5, -17.0) - 0.05, -17.0) @ roty(-0.4), U(mat=0, bump=0.6), False))
    for (x, y, z, sx, sy, sz, col) in [(-12, -1.5, -26, 10, 5.0, 4, (.78, .76, .6)), (11, -1.8, -28, 11, 6.0, 4, (.74, .72, .6)),
                                       (0, -2.8, -32, 15, 6.6, 5, (.76, .78, .72))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=col, tintMix=1.0), False))
    for k, (x, y, z) in enumerate([(-5.0, 11.0, -18), (5.5, 13.5, -22), (-1.0, 15.5, -26)]):
        draws.append((SC["cloud"], trans(x + (0.08 + 0.3 * c) * t * (1 if k % 2 else -1), y + 0.15 * math.sin(t * 0.5 + k), z) @ scale(1.4 + 0.4 * c), U(mat=0, bump=0.4), False))
    if c < 0.95: draws.append((SC["sun"], trans(5.5, 14.0 - 4 * c, -24) @ rotz(t * 0.2) @ scale(1.3), U(mat=0, bump=0.4), False))
    for (x, z, r, col, s) in GROUND_LEAVES:
        draws.append((SC["leaf"], trans(x, ground_h(x, z) + 0.008, z) @ roty(r) @ scale(s, 1.0, s), U(mat=0, bump=0.0, tint=col, tintMix=1.0), False))
    for (x, z, s) in MUSH:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))

def draw_hill(draws, t):
    draws.append((PR["ball"], HILL_M, U(mat=0, bump=1.0, tint=(0.84, 0.64, 0.44), tintMix=1.0, seed=5.0, obj="hill"), True))
    for k in range(9):                                       # little crumbs of earth round the base
        a = k * 0.7 + 0.3; p = HILL + np.array([math.cos(a), math.sin(a)]) * (0.85 + 0.08 * (k % 3))
        if np.dot(p - HILL, DOOR_DIR) / np.linalg.norm(p - HILL) > 0.6: continue
        draws.append((PR["ball"], trans(p[0], surf(*p), p[1]) @ scale(0.05 + 0.015 * (k % 3), 0.035, 0.05), U(mat=0, bump=0.5, tint=(0.8, 0.6, 0.42), tintMix=1.0), False))
    # doorway (a dark arch on the surface) and the little wooden door on its hinge
    Z = DOOR_N; X = np.cross([0, 1, 0], Z); X /= np.linalg.norm(X); Y = np.cross(Z, X)
    B = np.eye(4); B[:3, 0], B[:3, 1], B[:3, 2] = X, Y, Z
    Mdoor = trans(*DOOR_P) @ B
    draws.append((PR["ball"], Mdoor @ trans(0, 0, -0.01) @ scale(0.105, 0.13, 0.04), U(mat=0, bump=0.0, tint=(0.24, 0.14, 0.11), tintMix=1.0), False))
    ang = door_angle(t)
    hinge = Mdoor @ trans(-0.1, 0, 0.025) @ roty(-ang) @ trans(0.1, 0, 0)
    draws.append((PR["ball"], hinge @ scale(0.095, 0.12, 0.018), U(mat=0, bump=0.6, tint=(0.72, 0.46, 0.28), tintMix=1.0), False))
    draws.append((PR["ball"], hinge @ trans(0.05, -0.01, 0.02) @ scale(0.014), U(mat=0, bump=0.0, tint=(0.95, 0.8, 0.35), tintMix=1.0), False))
def door_angle(t):
    """open while the line marches in, shut by the last ant in the snow, opened again after the knock"""
    if t < SH["chilly"][0]: return 1.9
    if t < SH["knock"][0]: return 1.9 * (1 - ease(clampu(t, SH["chilly"][1] - 0.9, SH["chilly"][1] - 0.4)))
    if t < SH["snack"][0]: return 1.9 * ease(clampu(t, T.DOOR_OPEN - 0.15, T.DOOR_OPEN + 0.35))
    return 1.9

def scripted_ants(draws, contacts, t, n):
    """the ants once the march is over: out of the door with seeds, round the leaf, watching the dance"""
    out = DOOR_GROUND; dst = LEAF_PLATE
    if n == "knock":                                         # three ants march out with seeds after the door opens
        for k in range(3):
            s = (t - T.DOOR_OPEN - 0.25) * 0.5 - k * 0.32
            if s < -0.3: continue                            # still inside
            q = out + DOOR_DIR * s + SIDE * (0.0)
            draw_ant(draws, contacts, t, (q[0], surf(*q), q[1]), math.atan2(DOOR_DIR[0], DOOR_DIR[1]), phase=s / 0.1 * math.pi, carry=1.0)
        for k in range(3, 6):                                # the rest wait inside
            q = HILL + DOOR_DIR * 0.05
            draw_ant(draws, contacts, t, (q[0], surf(*q) - 0.3, q[1]), 0.0, walk=0.0)
    elif n == "snack":                                       # ants round the leaf, seeds set down on it
        for k in range(4):
            a = -1.0 + k * 0.65
            q = LEAF_PLATE + np.array([math.cos(a) * SIDE[0] - math.sin(a) * DOOR_DIR[0], math.cos(a) * SIDE[1] - math.sin(a) * DOOR_DIR[1]]) * 0.0
            q = LEAF_PLATE - DOOR_DIR * 0.4 + SIDE * (-0.36 + 0.24 * k)
            draw_ant(draws, contacts, t, (q[0], surf(*q), q[1]), math.atan2(DOOR_DIR[0], DOOR_DIR[1]), walk=0.0, wave=1.0 if t > T.NIBBLE else 0.3)
    elif n == "next_day":                                    # waiting at the door, cheering the big seed
        for k, q in enumerate(WATCHERS[:4]):
            draw_ant(draws, contacts, t, (q[0], surf(*q), q[1]), math.atan2(-DOOR_DIR[0] - SIDE[0], -DOOR_DIR[1] - SIDE[1]), walk=0.0, wave=1.0 if t > T.SET_DOWN else 0.4,
                     phase=k * 1.3)
    else:                                                    # watching the moral, swaying in the chorus, waving bye-bye
        for k, q in enumerate(WATCHERS):
            sway = math.sin(2 * math.pi * (t - SH["chorus"][0]) / (2 * BEAT) + k * 0.4) if n != "moral" else 0.0
            draw_ant(draws, contacts, t, (q[0], surf(*q), q[1]), math.atan2(MSPOT[0] - q[0], MSPOT[1] - q[1]) + 0.3, walk=0.0, wave=0.7,
                     roll=0.12 * sway, phase=k * 1.3)

def build_draws(t):
    draws, contacts = [], []
    backdrop(draws, t)
    n = T.shot_at(t)[1]
    draw_hill(draws, t)
    # leaf pile (Tumble's hops kick some up; they settle again)
    burst = 0.0
    for j in T.LEAF_HOPS:
        if 0.35 < t - j < 1.3: burst = max(burst, math.sin(math.pi * (t - j - 0.35) / 0.95))
    for k, (off, rot, s, tint) in enumerate(PILE_LEAVES):
        fly = burst * (0.4 + 0.5 * (k % 5) / 5) if k % 3 == 0 else 0.0
        p = np.array([PILE[0] + off[0] * (1 + 0.6 * fly), surf(PILE[0] + off[0], PILE[1] + off[2]) + off[1] + fly, PILE[1] + off[2] * (1 + 0.6 * fly)])
        draws.append((SC["leaf"], trans(*p) @ rotx(rot[0] + 3 * fly) @ roty(rot[1]) @ rotz(rot[2] * 0.3) @ scale(s), U(mat=0, bump=0.0, tint=tint, tintMix=1.0), False))
    st = tumble(t); mats = fox_mats_p(st); R, Mh, arms, legs = mats
    draw_tumble(draws, contacts, t, st, mats)
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, arms)
    # the ants
    if t < SH["knock"][0]:
        s_now = march_s(t)
        svals = [s0 + s_now for s0 in S0]
        ant_line(draws, contacts, t, ROAD, [min(s, S_INSIDE) for s in svals],
                 skip=lambda k, s: s >= S_INSIDE and k > 0)
        if any(s >= S_INSIDE for s in svals):               # ants home inside the hill (kept as one object, out of sight)
            q = HILL + DOOR_DIR * 0.05
            draw_ant(draws, contacts, t, (q[0], surf(*q) - 0.3, q[1]), 0.0, walk=0.0)
    else:
        scripted_ants(draws, contacts, t, n)
    # seeds by the road (Pip takes one), the head seed, seeds on the leaf, the biggest seed
    if t < SH["ant_hat"][0]:
        for k, (dx, dz) in enumerate([(0.0, 0.0), (0.12, 0.08), (-0.1, 0.1)]):
            if k == 0 and (t > SH["pip_carry"][0] + 0.65): continue      # picked up (visible action)
            q = STASH + np.array([dx, dz])
            draws.append((PR["ball"], trans(q[0], surf(*q) + 0.025, q[1]) @ roty(k) @ scale(0.034, 0.025, 0.05), U(mat=0, bump=0.3, tint=SEED_C, tintMix=1.0), False))
    if n == "pip_carry" and pip[5].get("beak"):
        Mp = trans(*pip[0]) @ roty(pip[1]) @ rotx(pip[3]) @ scale(1.1)
        draws.append((PR["ball"], Mp @ trans(0, 0.3, 0.33) @ roty(math.pi / 2) @ scale(0.03, 0.022, 0.045), U(mat=0, bump=0.3, tint=SEED_C, tintMix=1.0, obj="pip"), False))
    hs = head_seed(t, mats)
    if hs: draws.append((PR["ball"], hs[0] @ scale(*HEAD_SEED_R), U(mat=0, bump=0.4, tint=(0.93, 0.74, 0.45), tintMix=1.0, obj="hseed_held" if hs[1] == "held" else "hseed"), True))
    if n in ("snowflake", "chilly"):
        p = SEED_ON_GROUND
        draws.append((PR["ball"], trans(p[0], surf(*p) + HEAD_SEED_R[1] - 0.01, p[1]) @ rotx(-1.2) @ scale(*HEAD_SEED_R), U(mat=0, bump=0.4, tint=(0.93, 0.74, 0.45), tintMix=1.0, obj="hseed"), True))
    if n == "snack":
        Mleaf = trans(LEAF_PLATE[0], surf(*LEAF_PLATE) + 0.02, LEAF_PLATE[1]) @ roty(math.atan2(SIDE[0], SIDE[1]) + math.pi / 2) @ scale(0.6)
        draws.append((E2["bigleaf"], Mleaf, U(mat=0, bump=0.3, tint=(0.95, 0.6, 0.25), tintMix=0.6), False))
        for k, (dx, dz) in enumerate([(-0.2, 0.05), (0.0, -0.08), (0.18, 0.06), (0.05, 0.14)]):
            q = LEAF_PLATE + SIDE * dx + DOOR_DIR * dz
            sc = 1.0
            if k == 3: sc = 1.0 - clampu(t, T.NIBBLE - 0.05, T.NIBBLE + 0.3)        # nibbled (visible action)
            if sc > 0.02:
                draws.append((PR["ball"], trans(q[0], surf(*q) + 0.05, q[1]) @ roty(k * 0.8) @ scale(0.042 * sc, 0.032 * sc, 0.062 * sc), U(mat=0, bump=0.3, tint=SEED_C, tintMix=1.0), False))
    if t >= SH["next_day"][0]:
        draws.append((PR["ball"], big_seed_M(t, st, mats), U(mat=0, bump=0.4, tint=(0.95, 0.76, 0.42), tintMix=1.0, obj="bigseed"), True))
    # snow: the first flake, the flurry, the button flake on Pip's head
    eye, tgt, fov = camera(t)
    if n == "snowflake":
        if t < T.FLAKE_LAND:
            nose = apply(fox_mats_p(tumble(T.FLAKE_LAND))[1], NOSE) + np.array([0, 0.03, 0])
            u = clampu(t, SH[n][0], T.FLAKE_LAND)
            p = nose + np.array([0.15 * math.sin(u * 7), 1.6 * (1 - u), 0.05 * math.cos(u * 5)])
            draw_flake(draws, p, 0.08, spin=t, tilt=0.9)
        else:
            draw_flake(draws, apply(Mh, NOSE) + apply(Mh, (0, 0.03, 0.05)) - apply(Mh, (0, 0, 0)), 0.08, spin=0.3, tilt=1.2)
    if n == "chilly" and t < T.SNEEZE + 0.5:
        if t < T.SNEEZE:
            draw_flake(draws, apply(Mh, NOSE) + apply(Mh, (0, 0.03, 0.05)) - apply(Mh, (0, 0, 0)), 0.08, spin=0.3, tilt=1.2)
        else:                                                # blown off by the sneeze, spinning away
            u = clampu(t, T.SNEEZE, T.SNEEZE + 0.5)
            p = apply(Mh, NOSE) + apply(Mh, (0, 0.4 * u, 0.9 * u)) - apply(Mh, (0, 0, 0))
            draw_flake(draws, p, 0.08 * (1 - u), spin=t * 9, tilt=1.2)
    if n == "chilly": puff(draws, apply(Mh, NOSE) + np.array([0, 0, 0.1]), T.SNEEZE, t, n=8, size=0.04, spread=0.6, dur=0.4, tint=(0.95, 0.97, 1.0))
    amount = 0.0
    if n == "snowflake": amount = 0.2 * clampu(t, T.FLAKE_LAND + 0.3, SH[n][1])
    elif n in ("chilly", "knock", "snack"): amount = 0.55
    elif n == "button_crane": amount = 0.12
    flurry(draws, t, eye, tgt, amount)
    if n == "button_crane":
        a = SH[n][0]; ph = pip[0] + np.array([0, 0.55, 0])
        if t < a + 1.0:
            u = clampu(t, a, a + 1.0); draw_flake(draws, ph + np.array([0.1 * math.sin(u * 6), 1.0 * (1 - u), 0]), 0.04, spin=t, tilt=0.9)
        elif t < a + 1.6:
            u = clampu(t, a + 1.0, a + 1.6)
            draw_flake(draws, ph + np.array([0.5 * u, 0.2 * math.sin(math.pi * u) - 0.4 * u * u, 0]), 0.04 * (1 - u * 0.8), spin=t * 9, tilt=0.9)
        puff(draws, ph, a + 1.0, t, n=7, size=0.03, spread=0.5, dur=0.35, tint=(0.95, 0.97, 1.0))
    # bursts
    for j in T.LEAF_HOPS: puff(draws, np.array([PILE[0], 0.45, PILE[1] + 0.3]), j + 0.35, t, n=12, size=0.06, spread=1.1, dur=0.5, tint=(0.97, 0.66, 0.3), axis=(0, 0.8, 0.3))
    if n == "next_day": puff(draws, np.array([BIG_SEED_AT[0], 0.35, BIG_SEED_AT[1]]), T.SET_DOWN + 0.2, t, n=8, size=0.045, spread=0.7, dur=0.45, tint=(1.0, 0.88, 0.35))
    return draws, contacts

def ground_objs(t):
    n = T.shot_at(t)[1]
    return ("pip",) if n in ("hook_ants", "snack") else ("fox", "pip")
HOOKS.update(build=build_draws, camera=camera, tumble=tumble, sky=sky, ground_objs=ground_objs,
             qa_ignore={("ant", "hill"), ("hill", "ant"), ("hseed_held", "fox"), ("fox", "hseed_held"), ("bigseed", "fox"), ("fox", "bigseed")})   # ants walk in at their door; seeds held in his paws / on his head
if __name__ == "__main__":
    main()
