"""Tumble & Pip Fables 5: The Other Fox  (Aesop: The Dog and His Reflection)
Shared renderer: fablekit.py (wrapped here, not edited: render_frame gains a mirrored reflection pass and a
translucent water plane). python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa"""
from fablekit import *
import fablekit as FK
from meshes import sstep

# ---------------- world: the log bridge over the meadow stream ----------------
LX = 1.5                                                   # the log runs across the stream along z at x = LX
LZ_N, LZ_F = -3.75, -7.25                                  # near-bank and far-bank ends
LOG_R = 0.2
YW = -0.06                                                 # water line (flat); every bank edge stays above it
TZ = -5.5                                                  # Tumble's spot, mid-stream
def log_axis_y(z):
    y0 = float(ground_h(LX, LZ_N)) + LOG_R - 0.04; y1 = float(ground_h(LX, LZ_F)) + LOG_R - 0.04
    return y0 + (y1 - y0) * (z - LZ_N) / (LZ_F - LZ_N)
def log_top(z): return log_axis_y(z) + LOG_R
TP = (LX, TZ)
STAND = log_top(TZ) - float(surf(*TP))                     # stand_h on the log top
FACE_YAW = math.pi / 2                                     # facing +x: down the stream, towards the low camera
PIP_Z = -6.3
PIP_SPOT = np.array([LX, log_top(PIP_Z), PIP_Z]) + UP
BS = 0.12                                                  # berry scale (mesh y -0.5..0.58)
BERRY_LOG = np.array([LX, log_top(-6.6) + 0.5 * BS - 0.004, -6.6])
APPLE_S = 0.44; APPLE_TOP = 0.61 * APPLE_S; APPLE_BOT = 0.41 * APPLE_S
HOLD1 = [0.3, 1.25, 0.62]                                  # two-paw hold: both paws under the apple (coordinator pose)
PAW_OUT = [0.85, 0.95]                                     # berry paw: out to the side, towards Pip
def half_w(x):
    """the stream's half width: 0.7 at the bridge, opening into a pool downstream (towards the low camera)"""
    return 0.7 + 0.85 * sstep(LX + 1.2, LX + 5.5, x)
def bank_z(x, side, out=0.15): return -5.5 + side * (float(half_w(x)) + out)
FLOWERS = make_flowers([(LX, LZ_N, 0.6), (LX, LZ_F, 0.7), ("band", -7.0, -4.0), ("box", LX + 0.8, 16.5, -8.4, -2.6)], seed=55)
REEDS = [(LX - 1.35, bank_z(LX - 1.35, 1), 7), (LX + 2.6, bank_z(LX + 2.6, -1), 6), (LX - 2.4, bank_z(LX - 2.4, -1), 5), (LX + 4.3, bank_z(LX + 4.3, 1), 6)]
STONES = [(LX + 0.85, bank_z(LX + 0.85, 1, 0.3), 0.9, 0.3), (LX - 0.75, bank_z(LX - 0.75, -1, 0.35), 1.1, 1.2),
          (LX + 1.8, bank_z(LX + 1.8, 1, 0.35), 0.7, 2.0), (LX + 3.4, bank_z(LX + 3.4, -1, 0.35), 1.0, 0.7)]
LILY = (LX + 3.0, -6.05)

# ---------------- ground with a clean channel, the water plane ----------------
def _ground5():
    nx, nz = 260, 300
    xs = np.linspace(-16, 16, nx); zs = np.linspace(-24, 12, nz)
    X, Z = np.meshgrid(xs, zs, indexing="ij"); G = ground_h(X, Z)
    hw = half_w(X); zr = Z + 5.5
    b = sstep(-hw - 0.16, -hw + 0.04, zr) * sstep(hw + 0.16, hw - 0.04, zr)     # steep banks: a crisp water edge
    Y = G - 0.3 * b
    P = np.stack([X, Y, Z], -1)
    gy, gx = np.gradient(Y, zs, axis=1), np.gradient(Y, xs, axis=0)
    N = np.stack([-gx, np.ones_like(gx), -gy], -1); N /= np.linalg.norm(N, axis=-1, keepdims=True)
    from meshes import hexc, mixc
    g1, g2, g3 = hexc("#A6D27F"), hexc("#8FC46E"), hexc("#CFE6A0")
    n1 = 0.5 + 0.5 * np.sin(X * 1.1 + np.sin(Z * 0.9) * 2) * np.sin(Z * 1.4 + np.sin(X * 0.5) * 1.5)
    C = mixc(np.broadcast_to(g1, P.shape), g2, n1 * 0.7)
    C = mixc(C, g3, sstep(-8, -16, Z) * 0.6)
    bank = sstep(-hw - 0.5, -hw - 0.15, zr) * sstep(hw + 0.5, hw + 0.15, zr)
    C = mixc(C, hexc("#B8B98A"), bank * 0.4)                # sandy banks down to the water line
    C = mixc(C, hexc("#3E6E78"), sstep(YW + 0.01, YW - 0.08, Y))    # under the water: dark teal walls
    idx = np.arange(nx * nz).reshape(nx, nz)
    a, b_, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
    F = np.concatenate([np.stack([a, d, c], -1).reshape(-1, 3), np.stack([a, c, b_], -1).reshape(-1, 3)])
    Yf = Y.reshape(-1)
    F = F[~(Yf[F] < YW - 0.012).all(1)]                     # the bed under the water is cut out (the reflection shows there)
    return Mesh(dict(v=P.reshape(-1, 3).astype(np.float32), n=N.reshape(-1, 3).astype(np.float32), c=C.reshape(-1, 3).astype(np.float32),
                     ao=np.ones(nx * nz, np.float32), f=F.astype(np.uint32), name="ground5"))
GROUND5 = _ground5()
def _quad(x0, x1, z0, z1, y):
    v = np.array([[x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1]], np.float32)
    return Mesh(dict(v=v, n=np.tile([0, 1, 0], (4, 1)).astype(np.float32), c=np.ones((4, 3), np.float32), ao=np.ones(4, np.float32),
                     f=np.array([[0, 2, 1], [0, 3, 2]], np.uint32), name="water"))
WATER = _quad(-16, 16, -8.0, -3.0, YW)
WATER_U = U(mat=0, bump=0.0, tint=(0.36, 0.62, 0.82), tintMix=1.0, alpha=0.28)
SKYDOWN = _quad(-120, 120, -60, 40, YW - 3.0)             # the sky seen in the water (flat colour, under the mirror world)
SKYDOWN_U = U(mat=3, bump=0.0, tint=(0.5, 0.68, 0.85), tintMix=1.0)
MIR = trans(0, 2 * YW, 0) @ np.diag([1.0, -1.0, 1.0, 1.0])

# ---------------- Tumble ----------------
def hop_y(t, t0, hgt=0.14, dur=0.32):
    d = t - t0
    return hgt * math.sin(math.pi * d / dur) if 0 <= d < dur else 0.0
def face_amt(t):
    """the silly face: on from FACE, off a little after 'Blehhh!'"""
    return clampu(t, T.FACE, T.FACE + 0.3) * (1 - clampu(t, T.BLEH + 0.9, T.BLEH + 1.25))
def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    st["x"], st["z"] = TP; st["stand_h"] = STAND; st["yaw"] = FACE_YAW
    if t < T.SLIP: st["arms"][0] = list(HOLD1)
    st["arms"][1] = list(HOLD1)
    if n in ("hook_mirror", "title_wide"):                     # peering down at the other fox; startles on "Hey!"
        st["head"][0] = 0.38; st["lean"] = 0.12
        st["y"] += hop_y(t, T.HEY - 0.05, 0.12, 0.3)
        pt = ease(clampu(t, T.HEY + 0.15, T.HEY + 0.5)) * (1 - ease(clampu(t, 2.9, 3.4)))
        st["arms"][0] = lerp(HOLD1, [0.25, 0.85, 0.0], pt).tolist()      # points down at the water
        if n == "title_wide":                                   # looks round as Pip flies in
            u = ease(clampu(t, 4.3, 5.0)); st["head"][1] = 0.55 * u; st["head"][0] = 0.38 * (1 - u); st["lean"] = 0.12 * (1 - u)
    elif n == "proud":                                          # turns to Pip and lifts his apple high
        a = SH[n][0]; u = ease(clampu(t, a, a + 0.6))
        st["yaw"] = FACE_YAW + 0.55 * u; st["head"][1] = 0.25 * u; st["head"][0] = -0.12 * u
        up = ease(clampu(t, T.SHINY[0] - 0.4, T.SHINY[0]) if T.SHINY else u)
        st["arms"][1] = lerp(HOLD1, [0.6, 1.75, 0.0], up).tolist()
        for w in T.SHINY: st["y"] += hop_y(t, w - 0.05, 0.06, 0.3)
        dn = ease(clampu(t, SH[n][1] - 0.8, SH[n][1] - 0.2))     # back to facing the water before the cut
        st["yaw"] = lerp(st["yaw"], FACE_YAW, dn); st["arms"][1] = lerp(st["arms"][1], HOLD1, dn).tolist()
        st["head"][1] *= 1 - dn; st["head"][0] = lerp(st["head"][0], 0.3, dn)
    elif n == "bigger":
        st["head"][0] = 0.42; st["lean"] = 0.15
        g = ease(clampu(t, T.BIGGER - 0.2, T.BIGGER + 0.3))
        st["lean"] += 0.06 * g; st["sq"] += 0.05 * g * math.exp(-max(0, t - T.BIGGER) * 2)
    elif n in ("silly_face", "copycat"):
        f = face_amt(t); st["head"][0] = 0.3; st["lean"] = 0.1
        st["head"][2] = 0.22 * f * math.sin((t - T.FACE) * 8.5)
        st["arms"][0] = lerp(HOLD1, [2.1 + 0.18 * math.sin(t * 22), 0.55, 0.0], f).tolist()   # paw waggling by his cheek
        st["face"] = f
        if t > T.BLEH: st["y"] += 0.025 * abs(math.sin((t - T.BLEH) * 9)) * (1 - clampu(t, T.BLEH + 1.4, T.BLEH + 1.6))
    elif n == "reach":                                          # "I want THAT one!": leans and reaches down with both paws
        u = ease(clampu(t, T.REACH - 0.1, T.REACH + 0.5))
        st["lean"] = 0.1 + 0.2 * u; st["head"][0] = 0.3 + 0.2 * u
        st["arms"][0] = lerp(HOLD1, [0.12, 0.75, 0.0], u).tolist()
        st["arms"][1] = lerp(HOLD1, [0.12, 0.75, 0.0], u).tolist()
        if t > T.SLIP:                                          # the apple slips: paws fly up in surprise
            v = ease(clampu(t, T.SLIP, T.SLIP + 0.3))
            st["arms"] = [lerp([0.12, 0.75], [0.7, 1.3], v).tolist(), lerp([0.12, 0.75], [0.7, 1.3], v).tolist()]
            st["lean"] = lerp(0.3, 0.15, v)
    elif n == "wobble":
        a = SH[n][0]
        st["lean"] = 0.12; st["head"][0] = 0.4
        st["arms"] = [[0.7, 1.3], [0.7, 1.3]]
        rel = ease(clampu(t, a + 0.3, a + 1.0)); st["arms"] = [lerp([0.7, 1.3], [0.25, 0.3], rel).tolist()] * 2
        if T.WOBBLY - 0.1 < t < T.WOBBLY + 1.0: st["head"][2] = 0.15 * math.sin((t - T.WOBBLY) * 10)
        dr = ease(clampu(t, SH[n][1] - 1.6, SH[n][1] - 0.6))    # droops: the apple is gone
        st["head"][0] = 0.4 + 0.15 * dr; st["sq"] -= 0.05 * dr; st["arms"] = [lerp(st["arms"][0], [0.08, 0.0], dr).tolist()] * 2
    elif n == "berry":                                          # holds his paw out for Pip's berry
        a = SH[n][0]; u = ease(clampu(t, a + 0.3, a + 1.0))
        st["head"][0] = lerp(0.5, 0.2, u); st["head"][1] = 0.3 * u; st["sq"] -= 0.05 * (1 - u)
        st["arms"][0] = lerp([0.08, 0.0], PAW_OUT, u).tolist(); st["arms"][1] = [0.08, 0.0]
        if t > T.HALF: st["head"][0] = 0.2 - 0.12 * ease(clampu(t, T.HALF, T.HALF + 0.4))
    elif n == "share":
        st["head"][1] = 0.3; st["head"][0] = 0.08; st["arms"][0] = list(PAW_OUT); st["arms"][1] = [0.08, 0.0]
        e = ease(clampu(t, T.BITE - 0.45, T.BITE)) * (1 - ease(clampu(t, T.BITE + 0.35, T.BITE + 0.8)))
        st["arms"][0] = lerp(PAW_OUT, [0.05, 2.05], e).tolist()   # paw to his mouth: one bite
        if t > T.BITE + 0.3:                                    # laughs, happy wiggle
            d = t - T.BITE - 0.3
            st["head"][0] = 0.08 - 0.15 * min(1, d * 3); st["y"] += 0.035 * abs(math.sin(d * 9)); st["roll"] = 0.05 * math.sin(d * 7)
    elif n in ("moral", "chorus"):
        dance_tumble(st, t, n); st["yaw"] = FACE_YAW - 0.05
        if n == "moral":
            u = ease(clampu(t, SH[n][0], SH[n][0] + 0.3)); st["arms"][0] = lerp(PAW_OUT, DANCE_ARM, u).tolist()
            st["arms"][1] = [0.3, 0.3]
    else:                                                       # button: waves bye-bye, then laughs at Pip's silly face
        a = SH["button_crane"][0]
        dance_tumble(st, SH["chorus"][0] + 0.01, "moral"); st["yaw"] = FACE_YAW - 0.05; st["y"] = 0.0
        down = ease(clampu(t, a + 0.45, a + 0.85))
        wave = ease(clampu(t, a + 0.6, a + 0.9))
        st["arms"] = [lerp(DANCE_ARM, [0.3, 0.3], down).tolist(), [0.3 + 2.0 * wave + 0.25 * wave * math.sin(t * 12), 0.5]]
        st["head"][2] = 0.08 * (1 - down)
        if t > a + 1.5:
            d = t - a - 1.5; st["head"][0] = -0.12 * min(1, d * 4); st["y"] += 0.03 * abs(math.sin(d * 9))
    return st

def fox_mats_p(st):
    """fox_mats plus a forward lean pivoting at his feet (peering over the water)"""
    R, Mh, arms, legs = fox_mats(st)
    p = st.get("lean", 0.0)
    if p == 0.0: return R, Mh, arms, legs
    root = trans(st["x"], surf(st["x"], st["z"]) + st.get("stand_h", 0.0) - 0.01 + st["y"], st["z"]) @ roty(st["yaw"])
    P = root @ trans(0, 0.05, 0) @ rotx(p) @ trans(0, -0.05, 0) @ np.linalg.inv(root)
    return P @ R, P @ Mh, [P @ a for a in arms], [P @ l for l in legs]

# ---------------- the apple ----------------
def apple_held(arms):
    """on both paws while they are together (two-paw hold); rides the right paw when the left one gestures"""
    h0, h1 = hand_pos(arms, 0), hand_pos(arms, 1)
    w = 1 - ease(clampu(np.linalg.norm(h0 - h1), 0.3, 0.7))
    return lerp(h1, 0.5 * (h0 + h1), w) + np.array([0, 0.0 + APPLE_BOT, 0.04])
_slip_from = {}
def apple_state(t, mats):
    """('held', p) | ('fall', p) | ('float', p, spin) | None (gone, after the wobble shot)"""
    if t < T.SLIP: return ("held", apple_held(mats[2]))
    if "p" not in _slip_from:
        st = tumble(T.SLIP); _slip_from["p"] = apple_held(fox_mats_p(st)[2])
    p0 = _slip_from["p"]
    land = np.array([max(p0[0], LX + 0.55) + 0.12, YW + 0.02, p0[2]])
    if t < T.SPLASH:
        u = clampu(t, T.SLIP, T.SPLASH)
        p = lerp(p0, land, u); p[1] = p0[1] + (land[1] - p0[1]) * u * u + 0.12 * math.sin(math.pi * u)
        return ("fall", p, t * 3)
    if t >= SH["wobble"][1]: return None
    d = t - T.SPLASH
    dx = 0.55 * max(0.0, d - 0.4) + 0.1 * min(d, 0.4)         # bobs, then drifts away down the stream (towards the camera)
    z = land[2] + (TZ - land[2]) * min(1.0, d / 2.5)
    y = YW + 0.02 - 0.09 * math.exp(-d * 4) * math.cos(d * 12) + 0.015 * math.sin(d * 4)
    return ("float", np.array([land[0] + dx, y, z]), T.SPLASH * 3 + 0.8 * d)

# ---------------- Pip and the berry ----------------
def pip_M(p, yaw, pitch=0.0): return trans(*p) @ roty(yaw) @ rotx(pitch) @ scale(1.1)
BEAK_HOLD = (0, 0.28, 0.37)                                # a berry held in Pip's beak (local)
TITLE_A = SH["title_wide"][0]
FLY_IN = [np.array([LX + 3.2, 2.3, -7.9]), np.array([LX + 0.25, 1.05, PIP_Z]), PIP_SPOT]   # across and down, then down onto the log
def paw_berry(arms): return hand_pos(arms, 0) + np.array([0, 0.1 + 0.5 * BS - 0.01, 0])
def hover_spot(arms):
    """beside the open paw on the far side from Tumble, beak towards the berry (side by side from the front camera)"""
    return paw_berry(arms) + np.array([0.0, -0.12, -0.42])
_cache = {}
def hover_ref():
    if "h" not in _cache:
        _cache["h"] = hover_spot(fox_mats_p(tumble(SH["berry"][0] + 1.5))[2])
    return _cache["h"]
def pip_state(t, st, mats):
    """kit tuple (pos, yaw, flying, pitch, perch, extra) or None while Pip is off screen (the hook)"""
    n = T.shot_at(t)[1]
    arms = mats[2]
    to_tumble = math.atan2(TP[0] + 0.3 - PIP_SPOT[0], TP[1] - PIP_SPOT[2])
    if n == "hook_mirror": return None
    if n == "title_wide":
        a = TITLE_A
        if t < a + 1.0:
            u = ease(clampu(t, a, a + 1.0)); p = lerp(FLY_IN[0], FLY_IN[1], u)
            return p, math.atan2(FLY_IN[1][0] - FLY_IN[0][0], FLY_IN[1][2] - FLY_IN[0][2]), True, 0.0, False, {"beak": True, "gentle": True}
        if t < a + 1.4:
            u = ease(clampu(t, a + 1.0, a + 1.4)); return lerp(FLY_IN[1], FLY_IN[2], u), lerp(-1.6, -math.pi, u), True, 0.0, False, {"beak": True, "gentle": True}
        dip = math.sin(math.pi * clampu(t, a + 1.5, a + 1.9))   # bends down and sets the berry on the log
        turn = ease(clampu(t, a + 1.95, a + 2.3))
        return PIP_SPOT, lerp(-math.pi, to_tumble - 2 * math.pi, turn) if turn < 1 else to_tumble, False, 0.55 * dip, True, {"beak": t < a + 1.75}
    if n == "proud":
        hop = sum(hop_y(t, w, 0.07, 0.28) for w in T.SHINY)
        ex = {"cheer": True} if (T.SHINY and T.SHINY[-1] < t < T.SHINY[-1] + 1.0) else {}
        return PIP_SPOT + np.array([0, hop, 0]), to_tumble, False, 0.0, hop == 0, ex
    if n in ("bigger", "silly_face", "copycat", "reach", "wobble"):
        yaw = lerp(to_tumble, FACE_YAW, 0.6)
        ex = {}
        if n == "copycat" and t > T.BLEH: ex = {"cheer": True}                 # giggles at the two silly faces
        if n == "reach" and t > T.SLIP: ex = {"wings": (1.2, 1.2)} if t < T.SPLASH + 0.6 else {}
        if n == "wobble": yaw = to_tumble; ex = {"droop": ease(clampu(t, SH[n][1] - 1.6, SH[n][1] - 0.6))}
        return PIP_SPOT, yaw, False, 0.0, True, ex
    if n == "berry":
        a = SH[n][0]
        if t < a + 0.45:                                        # picks the berry up off the log
            dip = math.sin(math.pi * clampu(t, a + 0.05, a + 0.45))
            yaw = lerp(to_tumble, -math.pi, ease(clampu(t, a, a + 0.15)))
            return PIP_SPOT, yaw, False, 0.55 * dip, True, {"beak": t > a + 0.25}
        hv = hover_ref(); top = np.array([PIP_SPOT[0], hv[1] + 0.35, PIP_SPOT[2]]); over = np.array([hv[0], hv[1] + 0.35, hv[2]])
        legs = [(a + 0.45, a + 0.75, PIP_SPOT, top), (a + 0.75, a + 1.3, top, over), (a + 1.3, a + 1.6, over, hv)]   # up, across, down
        for (t0, t1, p0, p1) in legs:
            if t < t1:
                u = ease(clampu(t, t0, t1)); p = lerp(p0, p1, u)
                return p, 0.0, True, 0.0, False, {"beak": True, "gentle": True}
        p = hv + np.array([0, 0.03 * math.sin(t * 7), 0])
        pk = 0.0
        d = t - T.HALF
        if -0.25 < d < 0.05: pk = 0.6 * math.sin(math.pi * (d + 0.25) / 0.3)            # the peck that splits it
        if 0.3 < d < 0.6: pk = 0.45 * math.sin(math.pi * (d - 0.3) / 0.3)               # takes his half
        return p, 0.0, True, pk, False, {"beak": t < a + 1.75 or d > 0.45, "gentle": True}
    if n == "share":
        p = hover_ref() + np.array([0.0, 0.03 * math.sin(t * 7), -0.04])
        g = T.BITE + 0.25; pk = -0.5 * math.sin(math.pi * clampu(t, g, g + 0.4))          # gulps his half, beak up
        ex = {"beak": t < g + 0.2, "gentle": True}
        if t > T.BEST + 0.3: ex = {"wings": (1.2 + 0.4 * math.sin(t * 16), 1.2 + 0.4 * math.sin(t * 16))}
        return p, 0.0, True, pk, False, ex
    if n in ("moral", "chorus"):
        r = dance_pip(t, st, mats, n, arrive_from=hover_ref() + np.array([0.0, 0, -0.04]))
        return (r[0], r[1] + math.pi / 2 - 0.1) + tuple(r[2:])
    a = SH["button_crane"][0]                                   # hops off the paw onto the log, waves, pulls the silly face
    p0 = paw_seat(fox_mats_p(tumble(a))[2])
    u = clampu(t, a, a + 0.6)
    if u < 1:
        p = lerp(p0, PIP_SPOT, ease(u)); p[1] += 0.5 * math.sin(math.pi * u); p[0] += 0.3 * math.sin(math.pi * u)
        return p, FACE_YAW - 0.3, True, 0.0, False, {"wings": (0.3, 0.3)} if u < 0.3 else {"gentle": True}
    ex = {"cheer": True} if t < a + 1.4 else {"tongue": True}
    return PIP_SPOT, FACE_YAW - 0.3, False, 0.0, True, ex

def berry_draws(t, pip, arms):
    """the berry: carried in, on the log, carried to the paw, split in two, eaten. Returns list of (M, obj)"""
    n = T.shot_at(t)[1]; out = []
    def at(p, s=BS, rz=0.0): return trans(*p) @ rotz(rz) @ scale(s)
    if n == "hook_mirror": return out
    Mp = pip_M(pip[0], pip[1], pip[3]) if pip else None
    if n == "title_wide":
        rel = TITLE_A + 1.75
        if t < rel: out.append(at(apply(Mp, BEAK_HOLD)))
        else:
            u = clampu(t, rel, rel + 0.12); out.append(at(lerp(apply(Mp, BEAK_HOLD) if u < 1 else BERRY_LOG, BERRY_LOG, u)))
        return out
    if n in ("proud", "bigger", "silly_face", "copycat", "reach", "wobble"): return [at(BERRY_LOG)]
    if n == "berry":
        a = SH[n][0]
        if t < a + 0.25: return [at(BERRY_LOG)]
        if t < a + 1.75: return [at(apply(Mp, BEAK_HOLD))]
        pb = paw_berry(arms)
        if t < a + 1.9: return [at(lerp(apply(Mp, BEAK_HOLD), pb, clampu(t, a + 1.75, a + 1.9)))]
        if t < T.HALF: return [at(pb)]
    if n in ("berry", "share"):                                 # two halves: Tumble's on the paw, Pip's in his beak
        pb = paw_berry(arms); d = t - T.HALF
        sep = 0.055 * ease(clampu(d, 0, 0.15))
        mine = pb + np.array([-sep, -0.012, 0])
        if t < T.BITE + 0.25: out.append(trans(*mine) @ roty(FACE_YAW) @ rotz(0.25) @ scale(BS * 0.55, BS * 0.9, BS))
        pip_half = pb + np.array([sep, -0.012, 0])
        if d > 0.45: pip_half = apply(Mp, BEAK_HOLD)
        if t < T.BITE + 0.45: out.append(trans(*pip_half) @ roty(FACE_YAW) @ rotz(-0.25) @ scale(BS * 0.55, BS * 0.9, BS))
    return out

# ---------------- camera ----------------
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    if name == "hook_mirror":                                   # low, down the stream: the fox and the other fox
        return fit_cam(np.array([LX, -0.7, TZ - 0.1]), lerp(94, 91, e), 1.5, 1.3, lerp(3.45, 3.25, e), lift=0.0)
    if name == "title_wide":
        return fit_cam(np.array([LX + 0.4, 0.7, TZ - 0.2]), 38, 20, 3.0, 2.7 if not WIDE else 2.1, lift=0.0)
    if name == "proud":                                         # medium, eye level, three-quarter
        return fit_cam(np.array([LX + 0.1, 1.45 if WIDE else 1.25, TZ - 0.3]), lerp(62, 70, e), 5, 1.1, 1.75 if WIDE else 1.35)
    if name == "bigger":                                        # down at the water: real apple above, bigger water apple below
        return fit_cam(np.array([LX + 0.4, lerp(-0.1, -0.3, e), TZ + 0.15]), lerp(78, 86, e), 4, 1.25, lerp(3.4, 3.0, e), lift=0.0)
    if name == "silly_face":                                    # close front
        return fit_cam(np.array([LX + 0.3, 1.6, TZ]), 96, 10, 0.75, 0.85)
    if name == "copycat":
        return fit_cam(np.array([LX, -0.7, TZ - 0.1]), 92, 1.5, 1.25, 3.35, lift=0.0)
    if name == "reach":                                         # side-on from the near bank
        return fit_cam(np.array([LX + 0.45, 0.75, TZ]), 14, 6, 1.45, 1.45)
    if name == "wobble":                                        # low down the stream, wider: ripples and the apple bobbing away
        return fit_cam(np.array([LX + 0.6, -0.7, TZ]), 90, 3, 1.4, 3.45, lift=0.0)
    if name == "berry":                                         # macro: the paw, the berry and Pip, from the far-bank side
        pb = paw_berry(fox_mats_p(tumble(SH["berry"][0] + 1.5))[2])
        return fit_cam(pb + np.array([0.0, 0.15, -0.15]), lerp(76, 84, e), 8, 0.62, 0.62, fov=34)
    if name == "share":
        return fit_cam(np.array([LX + 0.2, 1.3, TZ - 0.4]), lerp(96, 88, e), 6, 1.05, 1.15)
    if name == "moral":
        return fit_cam(np.array([LX, lerp(-0.7, -0.6, e), TZ - 0.25]), lerp(100, 94, e), 1.5, 1.25, lerp(3.45, 3.2, e), lift=0.0)
    if name == "chorus":
        return fit_cam(np.array([LX, -0.6, TZ - 0.25]), 93, 1.5, 1.3, 3.25, lift=0.0)
    return fit_cam(np.array([LX, lerp(-0.6, 0.5, e), TZ - 0.25]), lerp(93, 82, e), lerp(1.5, 24, e), lerp(1.3, 2.4, e), lerp(3.25, 2.7, e), lift=0.0)

# ---------------- draws ----------------
BARK = (0.56, 0.39, 0.25)
def log_draws(draws):
    a = np.array([LX, log_axis_y(LZ_N), LZ_N]); b = np.array([LX, log_axis_y(LZ_F), LZ_F])
    draws.append((PR["stick"], seg_M(a, b, LOG_R), U(mat=0, bump=1.0, seed=3.0, tint=BARK, tintMix=1.0, obj="log"), True))
    for z in (-4.25, -6.75):                                    # bark rings, clear of feet and perches
        c = np.array([LX, log_axis_y(z), z])
        draws.append((PR["ball"], trans(*c) @ scale(LOG_R + 0.012, LOG_R + 0.012, 0.035), U(mat=0, bump=0.6, tint=(0.45, 0.3, 0.19), tintMix=1.0), False))
    for z, s in ((LZ_N - 0.02, 1), (LZ_F + 0.02, -1)):           # pale end grain
        c = np.array([LX, log_axis_y(z), z + s * 0.03])
        draws.append((PR["ball"], trans(*c) @ scale(LOG_R * 0.75, LOG_R * 0.75, 0.03), U(mat=0, bump=0.3, tint=(0.93, 0.8, 0.6), tintMix=1.0), False))
    s0 = np.array([LX - LOG_R * 0.7, log_axis_y(-4.7) + 0.08, -4.7]); s1 = s0 + np.array([-0.32, 0.3, 0.06])   # branch stub on the upstream side
    draws.append((PR["stick"], seg_M(s0, s1, 0.045), U(mat=0, bump=0.8, tint=BARK, tintMix=1.0), True))
    draws.append((SC["leaf"], trans(*(s1 + np.array([-0.08, 0.04, 0]))) @ roty(2.6) @ rotz(0.5) @ scale(2.6), U(mat=0, bump=0.0, tint=(0.45, 0.75, 0.38), tintMix=1.0), False))

def bank_draws(draws, t):
    for (x, z, s, r) in STONES:
        draws.append((SC["stone"], trans(x, ground_h(x, z) - 0.02, z) @ roty(r) @ scale(s), U(mat=0, bump=0.7), True))
    for k, (x, z, n_) in enumerate(REEDS):                      # reeds at the water's edge
        for j in range(n_):
            ang = j * 2.4; r = 0.06 + 0.05 * (j % 3)
            b = np.array([x + r * math.cos(ang), ground_h(x, z) - 0.02, z + r * math.sin(ang)])
            h = 0.55 + 0.12 * ((j * 7) % 5)
            tip = b + np.array([0.08 * math.sin(ang + t * 1.3 + k), h, 0.08 * math.cos(ang)])
            draws.append((PR["stick"], seg_M(b, tip, 0.022), U(mat=0, bump=0.2, tint=(0.42, 0.66, 0.32), tintMix=1.0), False))
            if j % 3 == 0:
                draws.append((PR["ball"], trans(*(tip - np.array([0, 0.1, 0]))) @ scale(0.04, 0.11, 0.04), U(mat=0, bump=0.5, tint=(0.55, 0.36, 0.22), tintMix=1.0), False))
    for (x, z, s) in [(LX - 1.0, -3.6, 0.17), (LX + 1.2, -7.3, 0.2), (LX - 2.6, -7.1, 0.15)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))

def water_draws(t):
    """translucent extras on the water: lily pad, flow streaks, ripple rings, the splash drops (drawn after the water plane)"""
    out = []
    lx, lz = LILY
    out.append((E2["bigleaf"], trans(lx, YW + 0.006, lz) @ roty(0.8 + 0.05 * math.sin(t * 0.7)) @ scale(0.42, 0.25, 0.42), U(mat=0, bump=0.3, tint=(0.5, 0.78, 0.42), tintMix=1.0, alpha=1.0)))
    rng = np.random.default_rng(9)
    for k in range(26):                                         # streaks drift down the stream (+x)
        x0 = rng.uniform(-14, 14); zf = rng.uniform(-0.65, 0.65); sp = rng.uniform(0.25, 0.4)
        x = (x0 + sp * t + 14) % 28 - 14; z = -5.5 + zf * float(half_w(x))
        if abs(x - LX) < 0.3 or x > LX + 3.5: continue           # none right under the lens
        out.append((PR["ball"], trans(x, YW + 0.003, z) @ scale(0.24, 0.002, 0.018), U(mat=0, bump=0.0, tint=(1, 1, 1), tintMix=1.0, alpha=0.35)))
    rings = []
    if t > T.SPLASH:
        ap = apple_state(T.SPLASH + 0.01, None)[1]
        rings += [(ap, T.SPLASH + k * 0.3) for k in range(4)]
    if T.FACE < t < SH["copycat"][1]:                           # a tiny drip ring under the waggling face
        rings += [(np.array([LX + 0.75, YW, TZ]), T.BLEH - 0.1)]
    for (c, t0) in rings:
        d = t - t0
        if not (0 <= d < 2.4): continue
        r = 0.12 + 0.75 * d; a = 0.6 * (1 - d / 2.4)
        for j in range(40):
            ang = j * 2 * math.pi / 40
            p = c + np.array([r * math.cos(ang), 0, r * math.sin(ang)])
            if abs(p[2] + 5.5) > float(half_w(p[0])) - 0.06: continue
            out.append((PR["ball"], trans(p[0], YW + 0.004, p[2]) @ roty(-ang) @ scale(0.03, 0.002, 0.05 + 0.02 * r), U(mat=0, bump=0.0, tint=(1, 1, 1), tintMix=1.0, alpha=a)))
    return out

def splash_draws(draws, t):
    d = t - T.SPLASH
    if not (0 <= d < 0.7): return
    c = apple_state(T.SPLASH + 0.01, None)[1]
    for k in range(14):
        ang = k * 2 * math.pi / 14; v = 0.9 + 0.5 * ((k * 5) % 3) / 2
        p = c + np.array([0.6 * math.cos(ang) * d, YW - c[1] + 0.05 + v * 2.2 * d - 4.5 * d * d, 0.6 * math.sin(ang) * d])
        if p[1] < YW: continue
        draws.append((PR["ball"], trans(*p) @ scale(0.045 * (1 - d / 0.7) + 0.01), U(mat=0, bump=0.0, tint=(0.82, 0.93, 1.0), tintMix=1.0), False))

EXTRA = {}
def wobble_amp(t):
    if t < T.SPLASH: return 0.0
    d = t - T.SPLASH
    return 0.16 * clampu(t, T.SPLASH, T.SPLASH + 0.25) * math.exp(-d / 1.8)
def apple_grow(t):
    if t >= T.SLIP: return 1.0
    return 1.0 + 0.4 * ease(clampu(t, T.BIGGER - 0.3, T.BIGGER + 0.4))

def build_draws(t):
    draws, contacts = [], []
    meadow_backdrop(draws, t)
    draws[0] = (GROUND5, np.eye(4), U(mat=1, bump=0.8), False)
    for (x, y, z, sx, sy, sz, c) in [(-30, -2.0, -2, 9, 4.5, 14, (.62, .8, .68)), (-32, -2.6, 12, 10, 5.5, 10, (.6, .78, .7)), (30, -2.2, -4, 9, 4.2, 14, (.64, .82, .68))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    bg = [d for d in draws if d[0] is SC["cloud"] or d[0] is SC["sun"] or (d[0] is PR["ball"] and d[1][1, 1] > 3)]
    draws = [d for d in draws if not any(d is b for b in bg)]   # far backdrop: drawn first (its under-ground half must not show in the stream)
    EXTRA["bg"] = bg
    draw_flowers(draws, t, FLOWERS)
    bank_draws(draws, t)
    i0 = len(draws)
    log_draws(draws)
    n = T.shot_at(t)[1]
    st = tumble(t); mats = fox_mats_p(st); R, Mh, arms, legs = mats
    draw_tumble(draws, contacts, t, st, mats)
    f = st.get("face", 0.0)
    if f > 0.02:                                                # the silly face: tongue out
        draws.append((PR["ball"], Mh @ trans(0, 1.165, 0.47 + 0.05 * f) @ rotx(0.5) @ scale(0.07 * f, 0.028, 0.085 * f), U(mat=0, bump=0.0, tint=(0.95, 0.45, 0.55), tintMix=1.0), False))
    pip = pip_state(t, st, mats)
    if pip is not None:
        Mp = draw_pip(draws, contacts, t, pip, arms)
        if pip[5].get("tongue"):
            draws.append((PR["ball"], Mp @ trans(0, 0.27, 0.3) @ rotx(0.4) @ scale(0.028, 0.012, 0.045), U(mat=0, bump=0.0, tint=(0.95, 0.45, 0.55), tintMix=1.0), False))
    for M in berry_draws(t, pip, arms):
        draws.append((E2["berry"], M, U(mat=0, bump=0.4, obj="berry"), True))
    a = apple_state(t, mats)
    ap = None
    if a is not None:
        ap = a[1]; spin = a[2] if len(a) > 2 else 0.0
        Ma = trans(*ap) @ roty(spin) @ scale(APPLE_S)
        draws.append((E2["apple"], Ma, U(mat=0, bump=0.5, obj="apple"), True))
        draws.append((PR["stick"], Ma @ trans(0, 0.55, 0) @ rotz(0.25) @ scale(0.6, 0.35, 0.6), U(mat=0, bump=0.0, tint=(0.48, 0.32, 0.2), tintMix=1.0), False))
    splash_draws(draws, t)
    # mirrored copies of everything on and over the stream (the reflection), with the ripple wobble
    refl = []; amp = wobble_amp(t); grow = apple_grow(t)
    for (mesh, M, u, cast) in draws[i0:]:
        c = M[:3, 3]
        if not (-7.6 < c[2] < -3.4 and abs(c[0] - LX) < 7 and c[1] > YW - 0.05): continue
        Mx = M
        if mesh is E2["apple"] or (mesh is PR["stick"] and ap is not None and np.linalg.norm(c - ap) < 0.4):
            if grow > 1.0: Mx = trans(*ap) @ scale(grow) @ trans(*(-ap)) @ M
        Mr = MIR @ Mx
        if amp > 0:
            dep = YW - (Mr[:3, 3][1])
            ph = 7.0 * dep - 9.0 * t
            Mr = trans(0, 0, amp * math.sin(ph)) @ trans(0, YW, 0) @ np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0.9 * amp * math.cos(ph), 1, 0], [0, 0, 0, 1.0]]) @ trans(0, -YW, 0) @ Mr
        refl.append((mesh, Mr, u, Mx))
    EXTRA["refl"] = refl
    EXTRA["water"] = [(WATER, np.eye(4), WATER_U)] + water_draws(t)
    return draws, contacts

# ---------------- render pass: reflection, scene, water ----------------
_blank = ctx.depth_texture((4, 4)); _blank.compare_func = "<="
_bfbo = ctx.framebuffer(depth_attachment=_blank); _bfbo.use(); _bfbo.clear(depth=1.0)
def _draw(mesh, M, u, Mn=None):
    prog["M"].value = gl(M); prog["NM"].value = nmat(M if Mn is None else Mn)
    prog["mat"].value = u.get("mat", 0); prog["bump"].value = u.get("bump", 1.0)
    prog["tint"].value = tuple(u.get("tint", (1, 1, 1))); prog["tintMix"].value = u.get("tintMix", 0.0)
    prog["seed"].value = u.get("seed", 0.0)
    mesh.vao.render()
def _clear_depth():
    msaa_fbo.color_mask = (False, False, False, False); msaa_fbo.use(); msaa_fbo.clear(depth=1.0)
    msaa_fbo.color_mask = (True, True, True, True); msaa_fbo.use()          # (moderngl applies the mask on use())
def render_frame5(t):
    draws, contacts = HOOKS["build"](t)
    shadow_fbo.use(); shadow_fbo.clear(depth=1.0); ctx.viewport = (0, 0, 2048, 2048)
    sprog["LVP"].value = gl(LVP)
    ctx.disable(moderngl.CULL_FACE)
    for (mesh, M, u, cast) in draws:
        if cast: sprog["M"].value = gl(M); mesh.svao.render()
    msaa_fbo.use(); msaa_fbo.clear(0, 0, 0, 1, depth=1.0)
    eye, tgt, fov = HOOKS["camera"](t)
    VPm = perspective(fov, W / H, 0.12, 90.0) @ look_at(eye, tgt)
    ctx.viewport = (0, 0, W, H)
    ctx.disable(moderngl.DEPTH_TEST)
    skyprog["cTop"].value, skyprog["cMid"].value, skyprog["cHor"].value = FK.SKY
    sky_vao.render()
    ctx.enable(moderngl.DEPTH_TEST)
    prog["VP"].value = gl(VPm); prog["LVP"].value = gl(LVP); prog["camPos"].value = tuple(eye)
    cvals = [tuple(c) for c in contacts] + [(0, 0, 1, 0)] * (8 - len(contacts))
    prog["contact"].value = cvals[:8]; prog["nContact"].value = min(len(contacts), 8)
    prog["fade"].value = 1.0; prog["keyI"].value = 1.05
    shadow_tex.use(0); prog["shadowMap"].value = 0
    for (mesh, M, u, cast) in EXTRA.get("bg", []): _draw(mesh, M, u)   # 0. far hills, clouds, sun
    _clear_depth()
    refl = EXTRA.get("refl", [])
    if refl:                                                     # 1. the mirror world, lit like the real one, no shadows
        _blank.use(0); prog["shadowMap"].value = 0
        _draw(SKYDOWN, np.eye(4), SKYDOWN_U)
        ctx.front_face = "cw"
        for (mesh, Mr, u, Mn) in refl: _draw(mesh, Mr, u, Mn)
        ctx.front_face = "ccw"
        _clear_depth()
    shadow_tex.use(0); prog["shadowMap"].value = 0               # 2. the scene (the stream bed is cut out of the ground)
    for (mesh, M, u, cast) in draws: _draw(mesh, M, u)
    ctx.enable(moderngl.BLEND); ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    for (mesh, M, u) in EXTRA.get("water", []):                  # 3. the tinted water plane and what floats on it
        prog["fade"].value = u.get("alpha", 1.0); _draw(mesh, M, u)
    ctx.disable(moderngl.BLEND); prog["fade"].value = 1.0
    ctx.copy_framebuffer(res_fbo, msaa_fbo)
    img = np.frombuffer(res_fbo.read(components=4), np.uint8).reshape(H, W, 4)[::-1].copy()
    img[..., 3] = 255
    return img
FK.render_frame = render_frame5

HOOKS.update(build=build_draws, camera=camera, tumble=tumble,
             ground_objs=lambda t: ("fox", "pip"),
             qa_ignore={("apple", "fox"), ("fox", "apple"), ("berry", "fox"), ("fox", "berry"), ("berry", "pip"), ("pip", "berry")})   # held apple and berry
if __name__ == "__main__":
    main()
