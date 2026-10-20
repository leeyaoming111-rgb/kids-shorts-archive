"""Tumble & Pip long-form episode v2: one Story Stump scene per run (16:9).
Built on the Episode 01 stump renderer (sunset-to-night light, storybook with pictures, arm IK) plus:
  - TALK mode: Tumble on the grass, Pip on the stump edge, the book open on the stump; free gestures for both;
  - gestures and looks driven by the script (to the audience, to each other, to the book);
  - a shot planner (timeline.py): wide, two-shot, close-ups, audience shots, book inserts, picture-quiz pages;
  - the dance break (talk positions, Pip hops to Tumble's paw for each chorus) and the recap lullaby on the pages.
python3 render.py --scene <name> [--preview] [out.mp4] | x <secs...> | seg f0 f1 out.mp4 | sheet | qa"""
import os, sys
if "--scene" in sys.argv:
    _i = sys.argv.index("--scene"); os.environ["SCENE"] = sys.argv[_i + 1]; del sys.argv[_i:_i + 2]
os.environ["ASPECT"] = "wide"
from fablekit import *
import fablekit as FK
from functools import lru_cache
from scipy.optimize import minimize
SCENE = T.SCENE
MODE = T.MODE
HERE_ = os.path.dirname(os.path.abspath(__file__))
STILLS = os.path.join(HERE_, "stills")

# ================= light: sunset -> twilight -> night =================
FS2 = FS
for a, b in [("uniform float fade; uniform float keyI;", "uniform float fade; uniform float keyI; uniform vec3 keyCol; uniform vec3 skyCol; uniform float ambI; uniform vec3 fogCol;"),
             ("vec3 keyc = vec3(1.0, 0.93, 0.82)*2.3*keyI;", "vec3 keyc = keyCol*2.3*keyI;"),
             ("vec3 skyc = vec3(0.55, 0.68, 0.95)*0.85*(0.75+0.25*keyI);", "vec3 skyc = skyCol*0.85*(0.75+0.25*keyI)*ambI;"),
             ("vec3 gndc = vec3(0.45, 0.58, 0.32)*0.45;", "vec3 gndc = vec3(0.45, 0.58, 0.32)*0.45*ambI;"),
             ("vec3(0.75,0.8,1.0)*fill*ao", "skyCol*fill*ao*ambI"),
             ("vec3 fogc = srgb2lin(vec3(0.86, 0.90, 0.96));", "vec3 fogc = srgb2lin(fogCol);")]:
    assert a in FS2, a
    FS2 = FS2.replace(a, b)
prog2 = ctx.program(vertex_shader=VS, fragment_shader=FS2)
def _rebind(m):
    m.vao = ctx.vertex_array(prog2, [(m.vbo, "3f 3f 3f 1f", "in_pos", "in_nrm", "in_col", "in_ao")], m.ibo)
    # kit bug: render_base builds the shadow VAO with "3f 36x" but a vertex is 40 bytes (3f 3f 3f 1f); 3f + 28x is right
    m.svao = ctx.vertex_array(sprog, [(m.vbo, "3f 28x", "in_pos")], m.ibo)
for _d in (FOXP, PIPP, PR, SC, E2):
    for _m in _d.values(): _rebind(_m)
_rebind(EYE_W); _rebind(EYE_P)
FK.prog = prog2

def keyframes(d, keys):
    for (a, va), (b, vb) in zip(keys[:-1], keys[1:]):
        if d <= b: return lerp(va, vb, clampu(d, a, b))
    return np.asarray(keys[-1][1], float)
LIGHT = dict(   # dusk value -> (r, g, b) or scalar
    key=[(0.0, (1.0, 0.80, 0.60)), (0.35, (1.0, 0.70, 0.56)), (0.62, (0.88, 0.66, 0.74)), (1.0, (0.64, 0.72, 1.0))],
    keyI=[(0.0, 0.98), (0.35, 0.85), (0.62, 0.66), (1.0, 0.46)],
    amb=[(0.0, (0.78, 0.66, 0.80)), (0.62, (0.60, 0.52, 0.82)), (1.0, (0.42, 0.48, 0.82))],
    ambI=[(0.0, 1.0), (0.62, 0.9), (1.0, 0.78)],
    fog=[(0.0, (0.98, 0.80, 0.68)), (0.35, (0.92, 0.66, 0.66)), (0.62, (0.62, 0.50, 0.70)), (1.0, (0.20, 0.22, 0.38))],
    top=[(0.0, (0.46, 0.56, 0.86)), (0.35, (0.38, 0.42, 0.76)), (0.62, (0.22, 0.24, 0.52)), (1.0, (0.05, 0.07, 0.20))],
    mid=[(0.0, (0.98, 0.74, 0.66)), (0.35, (0.92, 0.58, 0.64)), (0.62, (0.56, 0.40, 0.64)), (1.0, (0.12, 0.14, 0.34))],
    hor=[(0.0, (1.0, 0.80, 0.50)), (0.35, (1.0, 0.64, 0.42)), (0.62, (0.95, 0.56, 0.48)), (1.0, (0.26, 0.23, 0.44))])
def light_at(t):
    d = T.dusk(t)
    return {k: keyframes(d, v) for k, v in LIGHT.items()}, d
NOW = dict(t=0.0)
def sky_hook(t):
    L, d = light_at(t); return tuple(L["top"]), tuple(L["mid"]), tuple(L["hor"])

def draw_pass(draws, contacts, eye, tgt, fov, vp, sky):
    L, d = light_at(NOW["t"])
    x, y, w, h = vp
    VPm = perspective(fov, w / h, 0.12, 90.0) @ look_at(eye, tgt)
    ctx.viewport = vp
    ctx.disable(moderngl.DEPTH_TEST)
    skyprog["cTop"].value = sky[0]; skyprog["cMid"].value = sky[1]; skyprog["cHor"].value = sky[2]
    sky_vao.render()
    ctx.enable(moderngl.DEPTH_TEST)
    shadow_tex.use(0); prog2["shadowMap"].value = 0
    prog2["VP"].value = gl(VPm); prog2["LVP"].value = gl(LVP); prog2["camPos"].value = tuple(eye)
    cvals = [tuple(c) for c in contacts] + [(0, 0, 1, 0)] * (8 - len(contacts))
    prog2["contact"].value = cvals[:8]; prog2["nContact"].value = min(len(contacts), 8)
    prog2["fade"].value = 1.0; prog2["keyI"].value = float(L["keyI"])
    prog2["keyCol"].value = tuple(L["key"]); prog2["skyCol"].value = tuple(L["amb"])
    prog2["ambI"].value = float(L["ambI"]); prog2["fogCol"].value = tuple(L["fog"])
    for (mesh, M, u, cast) in draws:
        prog2["M"].value = gl(M); prog2["NM"].value = nmat(M)
        prog2["mat"].value = u.get("mat", 0); prog2["bump"].value = u.get("bump", 1.0)
        prog2["tint"].value = tuple(u.get("tint", (1, 1, 1))); prog2["tintMix"].value = u.get("tintMix", 0.0)
        prog2["seed"].value = u.get("seed", 0.0)
        mesh.vao.render()
FK.draw_pass = draw_pass

def hf_curves(t):
    """the kit's high-five curve, for every high-five in T.HIGH_FIVES (the break has two)"""
    for hf in T.HIGH_FIVES:
        a0 = hf - 0.42; u = clampu(t, a0, a0 + 0.7)
        if 0 < u < 1:
            r = HF_RISE * math.sin(math.pi * u) ** 2
            return 0.34 * math.sin(math.pi * min(u / 0.6, 1.0)) + r, r
    return None
FK.hf_curves = hf_curves

# ================= world: the big stump at sunset =================
STUMP = (0.0, -1.0); STUMP_S = 1.6; STUMP_YAW = 0.9                 # roots point back-left, back-right and front-right
STUMP_TOP = 0.55 * STUMP_S - 0.02                                   # stump drawn 0.02 into the grass
TOPY = surf(*STUMP) + STUMP_TOP
FOX_AT = (STUMP[0] - 0.05, STUMP[1] - 0.12)                         # Tumble stands on the stump like a little stage
PIP_SPOT = np.array([STUMP[0] + 0.74, TOPY, STUMP[1] + 0.32]) + UP  # Pip on the stump top, beside his feet
DANCE_SPOT = (STUMP[0] - 0.15, STUMP[1] + 2.05)                     # the break: on the grass in front of the stump
FLOWERS = make_flowers([(STUMP[0], STUMP[1], 3.2), (DANCE_SPOT[0], DANCE_SPOT[1], 1.6),
                        ("box", -2.2, 2.2, STUMP[1] - 0.5, 4.0)], n=70, seed=91)
SUN_X, MOON_X = -8.5, 9.5
_rng = np.random.default_rng(12)
STARS = []
while len(STARS) < 90:
    az, el = _rng.uniform(-1.1, 1.1), _rng.uniform(0.08, 0.75)
    STARS.append((np.array([math.sin(az) * math.cos(el), math.sin(el), -math.cos(az) * math.cos(el)]) * 42.0,
                  _rng.uniform(0.68, 0.97), _rng.uniform(0.06, 0.14), _rng.uniform(0, 6.28)))
FLIES = [(np.array([_rng.uniform(-5, 5), _rng.uniform(0.5, 1.8), _rng.uniform(-7.0, -2.6)]), _rng.uniform(0, 6.28)) for _ in range(14)]

def backdrop(draws, t):
    L, d = light_at(t)
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.8), False))
    for (x, z, s) in [(-7.5, -9.5, 1.6), (6.5, -9.0, 1.8), (-10.5, -13, 1.9), (10.0, -14, 2.0), (3.0, -15, 1.7), (-4.0, -16, 1.8), (8.5, -3.5, 1.5), (-8.0, -2.5, 1.4)]:
        draws.append((SC["tree"], trans(x, ground_h(x, z) - 0.05, z) @ roty(x) @ scale(s), U(mat=0, bump=0.7), True))
    draws.append((SC["cottage"], trans(7.5, ground_h(7.5, -17.0) - 0.05, -17.0) @ roty(-0.4), U(mat=0, bump=0.6), False))
    # the sun sinks behind the far hills; the moon rises on the other side; then the stars come out
    sun_y = lerp(7.0, -2.5, clampu(d, 0.0, 0.5))
    if sun_y > -2.0:
        draws.append((SC["sun"], trans(SUN_X, sun_y, -38) @ rotz(t * 0.05) @ scale(1.9),
                      U(mat=3, bump=0.0, tint=tuple(lerp((1.0, 0.72, 0.38), (1.0, 0.5, 0.35), clampu(d, 0, 0.45))), tintMix=1.0), False))
    for (x, y, z, sx, sy, sz, c) in [(-12, -1.5, -26, 10, 5.0, 4, (.62, .78, .62)), (11, -1.8, -28, 11, 6.0, 4, (.56, .72, .66)),
                                     (0, -2.8, -32, 15, 6.6, 5, (.62, .74, .72))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    moon_y = lerp(-2.0, 9.5, clampu(d, 0.5, 1.0))
    if moon_y > -1.5:
        draws.append((PR["ball"], trans(MOON_X, moon_y, -38) @ scale(1.25), U(mat=3, bump=0.0, tint=(1.0, 0.96, 0.82), tintMix=1.0), False))
    cloud_tint = tuple(lerp(lerp((1.0, 0.82, 0.78), (0.86, 0.66, 0.78), clampu(d, 0, 0.62)), (0.36, 0.38, 0.56), clampu(d, 0.62, 1.0)))
    for k, (x, y, z) in enumerate([(-5.0, 11.0, -18), (5.5, 13.5, -22), (-1.0, 15.5, -26)]):
        draws.append((SC["cloud"], trans(x + 0.05 * t * (1 if k % 2 else -1), y + 0.15 * math.sin(t * 0.5 + k), z) @ scale(1.4),
                      U(mat=0, bump=0.4, tint=cloud_tint, tintMix=-1.0), False))
    for k, (p, thr, s, ph) in enumerate(STARS):                     # each star twinkles in over 2 s as night deepens
        th = 0.66 + 0.3 * thr if k % 3 else thr
        g = clampu(d, th, th + 0.04) * (0.85 + 0.15 * math.sin(t * 1.7 + ph))
        if g > 0.02: draws.append((PR["ball"], trans(*p) @ scale(s * g), U(mat=3, bump=0.0, tint=(1.0, 0.95, 0.75), tintMix=1.0), False))
    fl = clampu(d, 0.42, 0.5)
    if fl > 0:                                                      # fireflies far behind the stump from link 6 on
        for k, (p, ph) in enumerate(FLIES):
            q = p + np.array([0.4 * math.sin(t * 0.6 + ph), 0.2 * math.sin(t * 0.9 + 2 * ph), 0.3 * math.cos(t * 0.5 + ph)])
            g = fl * (0.6 + 0.4 * math.sin(t * 2.2 + ph * 3))
            draws.append((PR["ball"], trans(*q) @ scale(0.035 * g), U(mat=3, bump=0.0, tint=(0.95, 1.0, 0.55), tintMix=1.0), False))

# ================= the storybook (new prop from primitives) =================
PW, PH = 0.40, 0.50            # one page
CW, CH = 0.43, 0.54            # one cover
CT, PT = 0.025, 0.035          # cover and page-block thickness
HZ = PT                        # cover hinge height (top of the right block)
HZP = PT + 0.003               # turning-page hinge
COVER = (0.16, 0.48, 0.56); PAGE = (0.98, 0.94, 0.84); EDGE = (0.92, 0.86, 0.74); GOLD = (0.95, 0.74, 0.30)
BOOK_C = np.array([0.0, 0.76, 0.45])                                 # spine foot in Tumble's frame
BOOK_TILT = 0.12                                                     # top edge leans towards the audience
def box(c, w, h, th):
    """blanket mesh (2.44 x 0.08 x 1.84) as a box in the book's x-y plane, centre c, thickness along z"""
    return trans(*c) @ rotx(math.pi / 2) @ scale(w / 2.44, th / 0.08, h / 1.84)
def book_draws(draws, Mb, cover_th, turn, obj=True):
    """Mb: book frame (spine at x=0, pages face +z). cover_th 0 closed .. pi open. turn: None or angle 0..pi of the
    turning page. Returns the front-cover and spread quads (world corners) for the pictures."""
    o = dict(obj="book") if obj else {}
    draws.append((E2["blanket"], Mb @ box((CW / 2, 0, -CT / 2), CW, CH, CT), U(mat=0, bump=0.5, tint=COVER, tintMix=1.0, **o), True))
    draws.append((E2["blanket"], Mb @ box((PW / 2 + 0.008, 0, PT / 2), PW, PH, PT), U(mat=0, bump=0.2, tint=PAGE, tintMix=1.0), True))
    G = Mb @ trans(0, 0, HZ) @ roty(-cover_th) @ trans(0, 0, -HZ)
    draws.append((E2["blanket"], G @ box((PW / 2 + 0.008, 0, HZ + PT / 2), PW, PH, PT), U(mat=0, bump=0.2, tint=PAGE, tintMix=1.0), True))
    draws.append((E2["blanket"], G @ box((CW / 2, 0, HZ + PT + CT / 2), CW, CH, CT), U(mat=0, bump=0.5, tint=COVER, tintMix=1.0), True))
    draws.append((PR["stick"], Mb @ trans(0, -CH / 2 + 0.01, -CT * 0.6) @ scale(0.5, CH - 0.02, 0.5), U(mat=0, bump=0.3, tint=GOLD, tintMix=1.0), True))
    if turn is not None:
        P = Mb @ trans(0, 0, HZP) @ roty(-turn) @ trans(0, 0, -HZP)
        draws.append((E2["blanket"], P @ box((PW / 2 + 0.008, 0, HZP + 0.003), PW - 0.004, PH - 0.006, 0.006), U(mat=0, bump=0.0, tint=PAGE, tintMix=1.0), False))
    fz = HZ + PT + CT + 0.002
    cover_q = [apply(G, (x, y, fz)) for x, y in [(0.03, CH / 2 - 0.03), (CW - 0.03, CH / 2 - 0.03), (CW - 0.03, -CH / 2 + 0.03), (0.03, -CH / 2 + 0.03)]]
    ix, iy = PW - 0.06, PH / 2 - 0.035
    spread_q = [apply(Mb, (x, y, PT + 0.001)) for x, y in [(-ix, iy), (ix, iy), (ix, -iy), (-ix, -iy)]]
    return cover_q, spread_q, -math.cos(cover_th)



@lru_cache(maxsize=4096)
def _ik(i, tx, ty, tz):
    """arm angles [side, fwd, inward] (the kit's 3-angle arm) that put the paw at the target, in Tumble's frame.
    Tumble's arms are short and set wide; the inward swing brings the paws in to the book edges."""
    pv = np.array(FOXD[f"arm{i}"]["pivot"]); hd = np.array(FOXD[f"arm{i}"]["hand"]); sgn = 1 if i == 0 else -1
    tgt = np.array([tx, ty, tz])
    def hand(x):
        M = trans(*pv) @ roty(-sgn * x[2]) @ rotz(sgn * x[0]) @ rotx(-x[1]) @ trans(*(-pv)); return apply(M, hd)
    f = lambda x: float(np.sum((hand(x) - tgt) ** 2)) + 1e-4 * x[2] ** 2
    grid = ((s_, fw, iw) for s_ in np.linspace(-0.4, 1.6, 9) for fw in np.linspace(0.0, 2.2, 10) for iw in np.linspace(0.0, 1.5, 7))
    best = min(grid, key=f)
    r = minimize(f, best, method="Nelder-Mead", options=dict(xatol=1e-4, fatol=1e-9, maxiter=800))
    return float(r.x[0]), float(r.x[1]), float(r.x[2]), math.sqrt(float(np.sum((hand(r.x) - tgt) ** 2)))
def ik(i, tgt_local):
    s, fw, iw, err = _ik(i, *[round(float(v), 3) for v in tgt_local]); return [s, fw, iw]
def fox_root(st):
    gy = surf(st["x"], st["z"]) + st.get("stand_h", 0.0)
    sq = st["sq"]; lift = 0.22 * abs(math.sin(st["roll"]))
    return trans(st["x"], gy - 0.01 + st["y"] + lift, st["z"]) @ roty(st["yaw"]) @ rotz(st["roll"]) @ scale(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5)



# ================= talk-mode stage =================
TALK_FOX = (STUMP[0] - 1.6, STUMP[1] + 0.75)                        # Tumble on the grass, left of the stump, level with Pip
TALK_PIP = np.array([STUMP[0] + 0.6, TOPY, STUMP[1] + 0.62]) + UP   # Pip on the stump's front-right edge
TALK_YAW = 0.55                                                     # Tumble turned towards Pip and the audience
PIP_AUD_YAW = -0.35                                                 # Pip facing the audience, a little towards Tumble
BOOK_FLAT = trans(STUMP[0] - 0.12, TOPY + CT + 0.002, STUMP[1] - 0.18) @ roty(0.2) @ rotx(-math.pi / 2)
FLOWERS = make_flowers([(STUMP[0], STUMP[1], 3.2), (TALK_FOX[0], TALK_FOX[1], 1.4), ("box", -2.6, 1.8, STUMP[1] - 0.5, 4.0)], n=70, seed=91)

# ---- the book's state ----
OPEN_DUR, TURN_DUR, CLOSE_DUR = 1.1, 0.75, 1.4
def cover_angle(t):
    if T.CLOSED_BOOK: return math.pi * ease(clampu(t, T.OPEN, T.OPEN + OPEN_DUR)) if T.OPEN is not None else 0.0
    if T.CLOSE is not None: return math.pi * (1 - ease(clampu(t, T.CLOSE, T.CLOSE + CLOSE_DUR)))
    return math.pi
def page_turn(t):
    for a, k in T.TURNS:
        if a <= t < a + TURN_DUR: return math.pi * ease(clampu(t, a, a + TURN_DUR)), k
    return None, None
def spread_index(t):
    idx, alpha = 0, 1.0
    for a, k in T.TURNS:
        if t >= a: idx = k
        if a - 0.2 <= t < a: alpha = min(alpha, (a - t) / 0.2)
        if a <= t < a + TURN_DUR + 0.25: alpha = min(alpha, clamp01((t - a - TURN_DUR) / 0.25))
    if T.CLOSED_BOOK: alpha *= clamp01((t - T.OPEN - OPEN_DUR) / 0.3) if T.OPEN is not None else 0.0
    if T.CLOSE is not None: alpha *= clamp01((T.CLOSE - t) / 0.25)
    return idx, alpha
def book_frame_local(t):
    th = cover_angle(t)
    sx = -CW / 2 * (1 - th / math.pi)
    return trans(*(BOOK_C + np.array([sx, 0, 0]))) @ trans(0, -CH / 2, 0) @ rotx(-BOOK_TILT) @ trans(0, CH / 2, 0)
HOLD_Z = -0.035
def grip(t, side):
    th = cover_angle(t)
    if side > 0: return np.array([CW + 0.035, 0.02, HOLD_Z])
    closed = np.array([-0.035, 0.02, HOLD_Z]); opened = np.array([-(CW + 0.035), 0.02, HOLD_Z])
    away = np.array([-0.30, -0.45, HOLD_Z - 0.04]); u = th / math.pi
    if u <= 0.0: return closed
    if u >= 1.0: return opened
    if u < 0.35: return lerp(closed, away, ease(u / 0.35))
    if u < 0.85: return away
    return lerp(away, opened, ease((u - 0.85) / 0.15))
def page_flick(t):
    for a, k in T.TURNS:
        if a - 0.25 <= t < a + 0.35: return math.sin(math.pi * clampu(t, a - 0.25, a + 0.35))
    return 0.0
def hold_book(st, t):
    R = fox_root(st); B = book_frame_local(t); lift = page_flick(t)
    for i, side in ((0, 1), (1, -1)):
        g = grip(t, side) + (np.array([0, 0.06, 0.04]) * lift if i == 0 else 0)
        w = apply(fox_root(dict(st, sq=0.0)) @ B, g)
        st["arms"][i] = ik(i, apply(np.linalg.inv(R), w))
    return st

# ================= who is speaking, gestures =================
def speaking(who, t, pad=0.15):
    return any(L["who"] in (who, "both") and L["t0"] - pad <= t <= L["t1"] + pad for L in T.LINES)
def cur_line(t, pad=0.2):
    for L in T.LINES:
        if L["t0"] - pad <= t <= L["t1"] + pad: return L
    return None
def gesture(who, t):
    """(name, weight, local time) of the active gesture for 'tumble' / 'pip' at t"""
    key = "tg" if who == "tumble" else "pg"
    for L in T.TALK:
        g = L.get(key)
        if g and L["t0"] - 0.2 <= t <= L["t1"] + 0.45:
            w = clamp01((t - L["t0"] + 0.2) / 0.25) * clamp01((L["t1"] + 0.45 - t) / 0.3)
            return g, w, t - L["t0"], L
    for P in T.PAUSES:
        g = P.get(key)
        if g and P["t0"] - 0.1 <= t <= P["t1"] + 0.2:
            w = clamp01((t - P["t0"] + 0.1) / 0.25) * clamp01((P["t1"] + 0.2 - t) / 0.3)
            return g, w, t - P["t0"], None
    return None, 0.0, 0.0, None
def looking(t):
    """the look of the line being spoken (or the pause after it)"""
    L = cur_line(t, 0.35)
    if L: return L.get("look", "other"), L
    for P in T.PAUSES:
        if P["t0"] - 0.1 <= t <= P["t1"] + 0.2: return "cam", None
    return "other", None
def pad3(a): return list(a) + [0.0] * (3 - len(a))
def blend_arms(st, tgt, w, which=(0, 1)):
    for i in which:
        a = pad3(st["arms"][i]); b = pad3(tgt[i] if isinstance(tgt[0], (list, tuple)) else tgt)
        st["arms"][i] = list(lerp(a, b, w))
def word_pulse(L, t, dur=0.25):
    if not L: return 0.0
    for w in L["words"]:
        d = t - w["t0"]
        if 0 <= d < dur: return math.sin(math.pi * d / dur)
    return 0.0

def tumble_gesture(st, t, free_arms=True):
    g, w, u, L = gesture("tumble", t)
    if not g or w <= 0: return st
    s = math.sin
    if g == "wave": blend_arms(st, [[0.15, 0.0], [2.2 + 0.35 * s(t * 9), 0.3]], w)
    elif g == "excited":
        blend_arms(st, [[2.3 + 0.15 * s(t * 10), 0.3], [2.3 + 0.15 * s(t * 10 + 1), 0.3]], w); st["y"] += w * 0.06 * abs(s(t * 8))
    elif g == "think":
        blend_arms(st, [[0.15, 0.0], [0.2, 1.55, 0.6]], w); st["head"][2] += w * 0.15; st["head"][0] -= w * 0.1
    elif g == "point_cam": blend_arms(st, [[0.15, 0.0], [0.6, 1.45, 0.0]], w)
    elif g == "point_pip": blend_arms(st, [[1.15, 0.55], [0.15, 0.0]], w)
    elif g == "shrug":
        blend_arms(st, [[0.95, 0.55], [0.95, 0.55]], w); st["head"][2] += w * 0.12 * s(u * 4)
    elif g == "big": blend_arms(st, [[1.7, 0.15], [1.7, 0.15]], w)
    elif g == "tiny": blend_arms(st, [[0.3, 1.25, 0.62], [0.3, 1.25, 0.62]], w)
    elif g == "hug":
        blend_arms(st, [[0.15, 1.42, 0.85], [0.15, 1.42, 0.85]], w); st["roll"] += w * 0.05 * s(t * 3)
    elif g == "laugh":
        blend_arms(st, [[0.3, 1.0, 0.5], [0.3, 1.0, 0.5]], w); st["head"][0] -= w * 0.18; st["y"] += w * 0.04 * abs(s(t * 12))
    elif g == "nod": st["head"][0] += w * 0.18 * abs(s(t * 6))
    elif g == "shake": st["head"][1] += w * 0.3 * s(t * 9)
    elif g == "clap":
        c = 0.5 + 0.5 * s(t * 14)
        blend_arms(st, [[0.3, 1.25, 0.62 - 0.22 * c], [0.3, 1.25, 0.62 - 0.22 * c]], w)
    elif g in ("stretch", "yawn"):
        r = ease(clampu(u, 0.0, 0.8)) if g == "yawn" else 1.0
        blend_arms(st, [[2.7, 0.15], [2.7, 0.15]], w * r); st["sq"] += w * 0.04 * r; st["head"][0] -= w * 0.25 * r
    elif g == "peck": st["head"][0] += w * 0.25 * max(0.0, s(t * 10))
    elif g == "pull":
        blend_arms(st, [[0.3, 1.25, 0.62], [0.3, 1.25, 0.62]], w); st["head"][0] -= w * 0.1; st["y"] += w * 0.03 * abs(s(t * 4))
        st["x_off"] = w * 0.08 * s(t * 4)
    elif g == "blow": st["head"][0] += w * 0.12; st["sq"] -= w * 0.03
    elif g == "flex":
        blend_arms(st, [[1.9, 0.6], [1.9, 0.6]], w); st["y"] += w * 0.04 * abs(s(t * 7))
    elif g == "count":
        p = word_pulse(L, t, 0.35)
        blend_arms(st, [[0.15, 0.0], [1.3 + 0.7 * p, 0.6]], w); st["y"] += w * 0.05 * p
    elif g == "silly": st["head"][1] += w * 0.25 * s(t * 16); st["head"][2] += w * 0.15 * s(t * 11)
    elif g == "slow":
        ph = t * 2.4; st["legs"] = [0.06 * max(0, s(ph)) * w, 0.06 * max(0, -s(ph)) * w]; st["y"] += w * 0.02 * abs(s(ph))
    elif g in ("stomp", "run"):
        ph = t * (9 if g == "run" else 5); st["legs"] = [0.12 * max(0, s(ph)) * w, 0.12 * max(0, -s(ph)) * w]; st["y"] += w * 0.04 * abs(s(ph))
    return st

def talk_bob(st, t, who="tumble"):
    for L in T.LINES:
        if L["who"] in (who, "both") and L["t0"] <= t <= L["t1"]:
            st["y"] += 0.016 * abs(math.sin((t - L["t0"]) * 7)); st["head"][0] += 0.035 * math.sin((t - L["t0"]) * 5)
    return st

def head_yaw_to(st, target, base_yaw, lim=0.78):
    hx = st["x"]; hz = st["z"]
    a = math.atan2(target[0] - hx, target[2] - hz) - base_yaw
    a = (a + math.pi) % (2 * math.pi) - math.pi
    return max(-lim, min(lim, a))

def tumble(t):
    st = tumble_base(t)
    if MODE == "read":
        st["x"], st["z"] = FOX_AT; st["stand_h"] = STUMP_TOP; st["yaw"] = 0.0; st["tail"] *= 0.6; st["sq"] *= 0.5
        look, L = looking(t)
        if T.kind_at(t) == "r_spread" or page_turn(t)[0] is not None or (T.OPEN and T.OPEN - 0.2 < t < T.OPEN + OPEN_DUR + 0.2) \
                or (look == "book" and L and L["who"] == "tumble"):
            st["head"][0] = 0.28                                            # looks down at the book
        elif look == "cam" or (L is None):
            st["head"][0] = -0.06
        elif speaking("pip", t) and not speaking("tumble", t):
            st["head"][1] = 0.32; st["head"][0] = 0.08                      # listens to Pip
        g, w, u, _ = gesture("tumble", t)
        if g in ("nod",): st["head"][0] += w * 0.16 * abs(math.sin(t * 6))
        if g in ("excited", "laugh"): st["y"] += w * 0.04 * abs(math.sin(t * 9))
        if g == "shake": st["head"][1] += w * 0.28 * math.sin(t * 9)
        if T.NIGHT and T.CLOSE and t > T.CLOSE: st["head"][0] = 0.12 + 0.04 * math.sin(t * 1.2); st["head"][2] = 0.1 * math.sin(t * 0.9)
        if T.RECAP and T.RECAP["t0"] <= t <= T.RECAP["t1"]: st["roll"] = 0.03 * math.sin(2 * math.pi * t / (2 * BEAT))
        talk_bob(st, t)
        return hold_book(st, t)
    # talk and dance: on the grass, arms free
    st["x"], st["z"] = TALK_FOX; st["yaw"] = TALK_YAW
    D = T.DANCE
    if D and D["t0"] <= t <= D["t1"]:
        return dance(st, t, D)
    look, L = looking(t)
    eye = camera(t)[0]
    head_c = np.array([st["x"], 1.6, st["z"]])
    if look == "cam" and (L is None or L["who"] in ("tumble", "both")) or (L is None and any(P["t0"] - 0.1 <= t <= P["t1"] + 0.2 for P in T.PAUSES)):
        st["head"][1] = head_yaw_to(st, eye, st["yaw"]); st["head"][0] = -0.05
    else:
        st["head"][1] = head_yaw_to(st, TALK_PIP, st["yaw"]) * 0.85; st["head"][0] = 0.12
    tumble_gesture(st, t)
    st["x"] += st.pop("x_off", 0.0) * math.sin(st["yaw"]); talk_bob(st, t)
    return st

def sec_of(D, t):
    for (n, a, b) in D["sections"]:
        if a <= t < b: return n, a, b
    return D["sections"][-1]
def dance(st, t, D):
    n, a, b = sec_of(D, t); s = math.sin; ph = 2 * math.pi * (t - D["t0"]) / BEAT
    st["head"][1] = 0.0
    if n.startswith("Chorus"):
        dance_tumble(st, t, "chorus"); st["yaw"] = TALK_YAW * 0.5
    elif n == "Stretch":
        u = (t - a) / (b - a)
        if u < 0.5: blend_arms(st, [[2.7, 0.15], [2.7, 0.15]], 1.0); st["sq"] += 0.04
        else: st["roll"] = 0.1 * s(ph); blend_arms(st, [[1.4 + 0.3 * s(ph), 0.3], [1.4 - 0.3 * s(ph), 0.3]], 1.0)
    elif n == "Flap":
        f = 1.2 + 0.7 * s(ph * 2); blend_arms(st, [[f, 0.2], [f, 0.2]], 1.0); st["y"] += 0.03 * abs(s(ph))
    elif n == "Stomp":
        st["legs"] = [0.13 * max(0, s(ph)), 0.13 * max(0, -s(ph))]; st["y"] += 0.04 * abs(s(ph))
        tw = [x for x in T.word_times("turn") if a <= x < b]; jw = [x for x in T.word_times("jump") if a <= x < b]
        if tw: st["yaw"] += 2 * math.pi * ease(clampu(t, tw[0], tw[0] + 1.2))
        if jw:
            d = t - jw[0]
            if 0 <= d < 0.6: st["y"] += 0.45 * s(math.pi * d / 0.6); blend_arms(st, [[2.3, 0.3], [2.3, 0.3]], 1.0)
    elif n == "Button":
        u = clampu(t, a, a + 0.6); blend_arms(st, [[2.3, 0.3], [2.3, 0.3]], ease(u) * (1 - clampu(t, b - 1.2, b - 0.4)))
    else:                                                               # intro: bounce on the beat
        st["y"] += 0.035 * abs(s(ph / 2)); blend_arms(st, [[0.6 + 0.3 * s(ph / 2), 0.3], [0.6 - 0.3 * s(ph / 2), 0.3]], 1.0)
    return st

# ================= Pip =================
def hop(t, t0, h=0.14, dur=0.32):
    d = t - t0
    return h * math.sin(math.pi * d / dur) if 0 <= d < dur else 0.0
def legs_path(t, a, pts, dur):
    L = [np.linalg.norm(np.asarray(q) - np.asarray(p)) for p, q in zip(pts[:-1], pts[1:])]; tot = sum(L)
    u = clampu(t, a, a + dur) * tot
    for p, q, l in zip(pts[:-1], pts[1:], L):
        if u <= l: return lerp(p, q, ease(u / max(l, 1e-6)) if len(L) == 1 else u / max(l, 1e-6))
        u -= l
    return np.asarray(pts[-1], float)
def yaw_to(p, q): return math.atan2(q[0] - p[0], q[2] - p[2])
def pip_gesture(p, yaw, t, ex):
    g, w, u, L = gesture("pip", t)
    pitch = 0.0; fly = False
    if not g or w <= 0: return p, yaw, pitch, fly, ex
    if g == "hop":
        for wd in (L["words"] if L else []): p[1] += hop(t, wd["t0"], 0.12, 0.3)
        if not L: p[1] += hop(t, math.floor(u / 0.6) * 0.6 + (t - u), 0.1, 0.3)
    elif g == "cheer": ex["cheer"] = True; p[1] += 0.03 * abs(math.sin(t * 9))
    elif g == "wave": ex["wings"] = (0.04, 1.0 + 0.3 * math.sin(t * 8))
    elif g == "point": ex["point"] = True
    elif g == "droop": ex["droop"] = 0.6 * w
    elif g == "tilt": yaw += 0.3 * w * math.sin(min(u, 1.2) * 2.6); pitch = 0.12 * w
    elif g == "spin": yaw += 2 * math.pi * ease(clampu(u, 0.0, 0.7))
    elif g == "peck": pitch = 0.45 * w * max(0.0, math.sin(t * 10))
    elif g == "flutter":
        h = 0.32 * math.sin(math.pi * clampu(u, 0.0, (L["t1"] - L["t0"] + 0.4) if L else 1.6))
        if h > 0.01: p[1] += h * w; fly = True; ex["gentle"] = True
    elif g == "clap": ex["wings"] = (0.9 + 0.5 * math.sin(t * 14), 0.9 + 0.5 * math.sin(t * 14))
    elif g == "sleepy": ex["tuck"] = True; ex["droop"] = 0.3 * w; pitch = 0.1 * w
    return p, yaw, pitch, fly, ex

def pip_state(t, st, mats):
    R, Mh, arms, legs = mats
    face = apply(Mh, (0, 1.55, 0.5)); eye = camera(t)[0]
    look, L = looking(t); ex = {}
    if MODE == "read":
        A = T.act("pip_arrive")
        if A and t < A["t1"] + 0.05:                                    # flies in during the title, lands on the stump
            a, b = 0.5, A["t1"]
            pts = [np.array([-3.2, TOPY + 2.5, STUMP[1] + 0.4]), np.array([1.35, TOPY + 2.5, STUMP[1] + 0.45]),
                   np.array([1.35, TOPY + 0.45, STUMP[1] + 0.45]), PIP_SPOT + np.array([0, 0.12, 0])]
            if t < b - 0.12:
                q = legs_path(t, a, pts, b - 0.12 - a)
                return q, (1.4 if q[0] < 1.3 else -0.9), True, 0.0, False, {"gentle": True}
            u = clampu(t, b - 0.12, b)
            return lerp(PIP_SPOT + np.array([0, 0.12, 0]), PIP_SPOT, u), -0.55, True, 0.0, False, {"gentle": True}
        p = PIP_SPOT.copy(); base = p[1]
        if look == "cam" and L and L["who"] in ("pip", "both"): yaw = yaw_to(p, eye) * 0.8
        elif speaking("tumble", t) and not speaking("pip", t): yaw = yaw_to(p, face)
        else: yaw = -0.55
        p, yaw, pitch, fly, ex = pip_gesture(p, yaw, t, ex)
        if T.RECAP and T.RECAP["t0"] <= t <= T.RECAP["t1"]: p[0] += 0.03 * math.sin(2 * math.pi * t / (2 * BEAT))
        if T.NIGHT and T.CLOSE and t > T.CLOSE + 1.0 and not speaking("pip", t): ex["tuck"] = True
        return p, yaw, fly, pitch, (not fly) and p[1] - base < 0.012, ex
    D = T.DANCE
    if D and D["t0"] - 0.1 <= t <= D["t1"] + 0.2:
        return pip_dance(t, st, mats, D)
    p = TALK_PIP.copy(); base = p[1]
    if look == "cam" and (L is None or L["who"] in ("pip", "both")): yaw = yaw_to(p, eye) * 0.85
    elif speaking("tumble", t) and not speaking("pip", t): yaw = yaw_to(p, face)
    elif L and L["who"] == "pip": yaw = 0.5 * yaw_to(p, face) + 0.5 * PIP_AUD_YAW
    else: yaw = PIP_AUD_YAW
    p, yaw, pitch, fly, ex = pip_gesture(p, yaw, t, ex)
    return p, yaw, fly, pitch, (not fly) and p[1] - base < 0.012, ex

def pip_dance(t, st, mats, D):
    n, a, b = sec_of(D, t); ph = 2 * math.pi * (t - D["t0"]) / BEAT
    seat = paw_seat(mats[2]); p0 = TALK_PIP
    for (cn, ca, cb) in D["sections"]:
        if not cn.startswith("Chorus"): continue
        if ca - 0.7 <= t < ca:                                          # flies from the stump to the paw
            q = legs_path(t, ca - 0.7, [p0, p0 + np.array([0, 0.7, 0]), seat + np.array([0, 0.5, 0]), seat], 0.7)
            return q, 0.45, True, 0.0, False, {"gentle": True}
        if ca <= t < cb - 0.05: return dance_pip(t, st, mats, "chorus")
        if cb - 0.05 <= t < cb + 0.65:                                  # and back to the stump
            q = legs_path(t, cb - 0.05, [seat, seat + np.array([0, 0.5, 0]), p0 + np.array([0, 0.7, 0]), p0], 0.7)
            return q, -0.4, True, 0.0, False, {"gentle": True}
    p = p0.copy(); yaw = PIP_AUD_YAW; ex = {}
    if n == "Flap": ex["wings"] = (0.9 + 0.6 * math.sin(ph * 2), 0.9 + 0.6 * math.sin(ph * 2))
    elif n == "Stretch": ex["cheer"] = True
    elif n == "Stomp":
        p[1] += hop(t, a + (math.floor((t - a) / BEAT)) * BEAT, 0.1, 0.28)
        tw = [x for x in T.word_times("turn") if a <= x < b]
        if tw: yaw += 2 * math.pi * ease(clampu(t, tw[0], tw[0] + 1.0))
    else: p[1] += hop(t, a + (math.floor((t - a) / (2 * BEAT))) * 2 * BEAT, 0.08, 0.28)
    return p, yaw, False, 0.0, p[1] - p0[1] < 0.012, ex

# ================= cameras =================
def _jit(i, amp=5.0): return ((i * 37) % 11 - 5) / 5.0 * amp
def cam_two(e, yaw=6.0, pitch=7.0, fw=1.75, fh=1.45, cx=0.18, cy=1.25):
    return fit_cam(np.array([STUMP[0] + cx, TOPY + cy, STUMP[1] + 0.2]), yaw, pitch, fw, fh)
def cam_spread(e, yaw=0.0, pitch=4.0, fh=0.31, cy=0.0, cx=0.0, fov=34):
    return fit_cam(np.array([FOX_AT[0] - 0.06 + cx, TOPY + 0.79 + cy, FOX_AT[1] + 0.5]), yaw, pitch, fh * 1.78, fh, fov=fov, lift=0.0)
def cam_med(e, yaw=0.0, pitch=5.0, fh=1.0, cx=0.2, cy=1.25):
    return fit_cam(np.array([FOX_AT[0] + cx, TOPY + cy, FOX_AT[1] + 0.4]), yaw, pitch, fh * 1.78, fh, lift=0.04)
FOX_HEAD = np.array([TALK_FOX[0], 1.62, TALK_FOX[1]])
MID = (FOX_HEAD + TALK_PIP) / 2
def camera(t):
    i, name, u, el = T.shot_at(t); e = ease(u); k = name.split(":")[0]; j = _jit(i)
    push = lerp(1.0, 0.95, e)
    if k == "title_wide": return fit_cam(np.array([STUMP[0] + 0.2, TOPY + 1.0, STUMP[1]]), lerp(-8, -3, e), 6, 3.6, 2.7, lift=-0.22)
    if k == "page": return cam_two(e)
    if MODE == "read":
        if k == "r_two": return cam_two(e, 6 + j + 3 * e, 7, 1.75 * push, 1.45 * push)
        if k == "r_med": return cam_med(e, j + 2 * e, 5, 1.85 * push, cx=0.22, cy=0.92)
        if k == "r_spread": return cam_spread(e, j * 0.5 + 2 * e, 4, 0.33 * push)
        if k == "r_aud": return cam_med(e, j * 0.4, 4, 1.4 * push, cx=0.28, cy=1.02)
        if k == "r_cu_p": return fit_cam(PIP_SPOT + np.array([0.05, 0.32, 0]), 18 + j, 6, 1.3 * push, 0.75 * push, lift=0.06)
        return cam_two(e)
    # talk / dance
    if k in ("wide", "d_wide"): return fit_cam(MID + np.array([0.0, -0.25, 0.0]), 6 + j + 2 * e, 9, 4.4 * push, 2.5 * push, lift=0.1)
    if k in ("two", "d_med", "chorus"):
        return fit_cam(MID + np.array([0.0, -0.05, 0.0]), 8 + j + (lerp(5, -5, u) if k == "chorus" else 2 * e), 7, 3.7 * push, 2.0 * push, lift=0.1)
    if k == "cu_t": return fit_cam(FOX_HEAD + np.array([0.0, -0.15, 0.0]), 38 + j, 6, 2.2 * push, 1.3 * push, lift=0.08)
    if k == "aud_t": return fit_cam(FOX_HEAD + np.array([0.08, -0.12, 0.0]), math.degrees(TALK_YAW) * 0.6 + j * 0.4, 5, 2.0 * push, 1.2 * push, lift=0.08)
    if k == "cu_p": return fit_cam(TALK_PIP + np.array([0.0, 0.3, 0.0]), -28 + j, 7, 1.35 * push, 0.78 * push, lift=0.08)
    if k == "aud_p": return fit_cam(TALK_PIP + np.array([0.0, 0.3, 0.0]), math.degrees(PIP_AUD_YAW) + j * 0.4, 6, 1.3 * push, 0.75 * push, lift=0.08)
    return fit_cam(MID, 8, 7, 3.3, 1.85)


# ================= stills from the fables (book pictures and quiz pages) =================
import subprocess as _sp
BATCH_ = os.path.normpath(os.path.join(HERE_, "..", ".."))
import script as SCR
class _EP:                                                           # what the Episode 01 page art expects
    HOOK_STILL, STORY_STILL = 2.6, 29.0
    FABLES = {n: dict(title=tt) for n, tt in SCR.FABLE_TITLES.items()}
    @staticmethod
    def fable_still(n, near): return still_path(n, near)
EP = _EP
def still_path(n, t):
    """a 16:9 frame of fable n at t seconds: stills/fNN_<t>.png (shipped with the job), else cut from its wide render"""
    os.makedirs(STILLS, exist_ok=True)
    p = os.path.join(STILLS, f"f{n:02d}_{t:05.2f}.png")
    if not os.path.exists(p):
        cands = [os.path.expanduser(f"~/Movies/kids-shorts/videos/episode2/fable-{n:02d}_wide.mp4"),
                 os.path.join(BATCH_, "renders", f"fable-{n:02d}_wide.mp4")]
        src = next((c for c in cands if os.path.exists(c)), None)
        if not src: return None
        _sp.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-vf", "scale=1280:-2", p])
    return p if os.path.exists(p) else None

import glob
from PIL import Image
PAGE_PX = (1100, 680)
def _skimg(arr):
    a = np.ascontiguousarray(arr)
    return skia.Image.fromarray(a, colorType=skia.ColorType.kRGBA_8888_ColorType)
def _text(cv, s, x, y, size, rgb, sw=10, center=True):
    f = skia.Font(TF7, size); w = f.measureText(s)
    x0 = x - w / 2 if center else x
    cv.drawString(s, x0, y, f, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=sw, Color=skia.Color(*PLUMC), StrokeJoin=skia.Paint.kRound_Join))
    cv.drawString(s, x0, y, f, skia.Paint(AntiAlias=True, Color=skia.Color(*rgb)))
def _fit_title(s, maxw, size):
    while skia.Font(TF7, size).measureText(s) > maxw and size > 30: size -= 4
    return size
@lru_cache(maxsize=None)
def page_image(kind, n):
    """RGBA page art: a fable still (caption band cropped) with a number badge and, for links, its title banner;
    a painted placeholder when the fable has no stills yet; 'end' for the outro."""
    w, h = PAGE_PX
    arr = np.zeros((h, w, 4), np.uint8); surf_ = skia.Surface(arr); cv = surf_.getCanvas()
    cv.clear(skia.Color(250, 240, 214))
    still = EP.fable_still(n, EP.HOOK_STILL if kind == "hook" else EP.STORY_STILL) if kind in ("hook", "story") else None
    if still:
        im = Image.open(still).convert("RGB"); iw, ih = im.size
        ch = int(ih * 0.80); cw = min(iw, int(ch * w / h))                # crop off the caption band, keep the middle
        x0 = (iw - cw) // 2
        im = im.crop((x0, 0, x0 + cw, ch)).resize((w, h), Image.LANCZOS)
        rgba = np.dstack([np.asarray(im), np.full((h, w), 255, np.uint8)])
        cv.drawImage(_skimg(rgba), 0, 0)
    elif kind == "end":
        cv.clear(skia.Color(40, 46, 96))
        for k in range(40):
            r = np.random.default_rng(k); x, y = r.uniform(40, w - 40), r.uniform(30, h * 0.55)
            cv.drawCircle(x, y, r.uniform(3, 7), skia.Paint(AntiAlias=True, Color=skia.Color(255, 236, 170)))
        cv.drawCircle(w * 0.78, h * 0.25, 70, skia.Paint(AntiAlias=True, Color=skia.Color(255, 244, 205)))
        _text(cv, "The End", w / 2, h * 0.78, 130, (255, 214, 80), 14)
        _text(cv, "Goodnight!", w / 2, h * 0.93, 70, (255, 250, 240), 10)
    else:                                                                 # placeholder: painted page with the title
        p = skia.Paint(AntiAlias=True, Color=skia.Color(255, 214, 140))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(40, 40, w - 80, h - 80), 50, 50), p)
        rng = np.random.default_rng(n)
        for k in range(14):
            x, y = rng.uniform(80, w - 80), rng.uniform(80, h - 80)
            cv.drawCircle(x, y, rng.uniform(10, 26), skia.Paint(AntiAlias=True, Color=skia.Color(255, 236, 190)))
        _text(cv, str(n), w / 2, h * 0.48, 240, (110, 175, 235), 18)
        t_ = EP.FABLES[n]["title"]; _text(cv, t_, w / 2, h * 0.80, _fit_title(t_, w - 140, 96), (255, 250, 240), 12)
    if kind in ("hook", "story"):                                       # number badge, top left
        cv.drawCircle(78, 78, 54, skia.Paint(AntiAlias=True, Color=skia.Color(255, 214, 80)))
        _text(cv, str(n), 78, 104, 74, (255, 250, 240), 10)
    if kind == "hook" and still:                                        # title banner along the bottom
        t_ = EP.FABLES[n]["title"]; size = _fit_title(t_, w - 260, 80)
        tw = skia.Font(TF7, size).measureText(t_)
        cx = (w + 150) / 2                                                 # banner along the top, right of the badge
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - tw / 2 - 36, 28, tw + 72, 104), 52, 52),
                     skia.Paint(AntiAlias=True, Color=skia.Color(255, 250, 240, 235)))
        _text(cv, t_, cx, 28 + 78, size, (240, 110, 60), 0)
    g = np.linspace(-1, 1, w)[None, :, None]                             # the gutter: a soft fold down the middle
    fold = 1 - 0.28 * np.exp(-(g / 0.035) ** 2)
    arr[..., :3] = (arr[..., :3] * fold).astype(np.uint8)
    return _skimg(arr)
@lru_cache(maxsize=None)
def cover_image():
    w, h = 600, 760
    arr = np.zeros((h, w, 4), np.uint8); cv = skia.Surface(arr).getCanvas()
    _text(cv, "Tumble & Pip", w / 2, 150, 78, (255, 214, 80), 10)
    for k, s in enumerate(["Fables", "About", "Friendship"]):
        _text(cv, s, w / 2, 330 + k * 130, 112 if k != 1 else 84, (255, 250, 240) if k != 2 else (255, 214, 80), 12)
    cv.drawCircle(w / 2, 690, 22, skia.Paint(AntiAlias=True, Color=skia.Color(255, 214, 80)))
    return _skimg(arr)


QUADS = {}
def _project(eye, tgt, fov, pts):
    VPm = perspective(fov, W / H, 0.12, 90.0) @ look_at(eye, tgt); out = []
    for p in pts:
        q = VPm @ np.r_[p, 1.0]
        if q[3] <= 0.05: return None
        out.append(((q[0] / q[3] * 0.5 + 0.5) * W, (1 - (q[1] / q[3] * 0.5 + 0.5)) * H))
    return out
def _draw_quad(img, cv, im, quad, alpha, ref=None):
    src = [skia.Point(0, 0), skia.Point(im.width(), 0), skia.Point(im.width(), im.height()), skia.Point(0, im.height())]
    dst = [skia.Point(*p) for p in quad]
    m = skia.Matrix()
    if not m.setPolyToPoly(src, dst): return
    tint = (1.0, 1.0, 1.0)
    if ref is not None:                       # match the page's own light (sunset, twilight, night)
        cx, cy = np.mean([p[0] for p in quad]), np.mean([p[1] for p in quad])
        xs = [int(lerp(quad[0][0], quad[1][0], f)) for f in (0.2, 0.8)]; y0 = int(lerp(quad[0][1], quad[3][1], 0.5))
        samp = []
        for x in xs:
            if 3 <= x < W - 3 and 3 <= y0 < H - 3: samp.append(img[y0 - 2:y0 + 3, x - 2:x + 3, :3].reshape(-1, 3).mean(0))
        if samp:
            tint = tuple(np.clip(np.mean(samp, 0) / (255 * np.array(ref)), 0.25, 1.1))
    p = skia.Paint(AntiAlias=True, Alphaf=float(alpha),
                   ColorFilter=skia.ColorFilters.Matrix([tint[0], 0, 0, 0, 0, 0, tint[1], 0, 0, 0, 0, 0, tint[2], 0, 0, 0, 0, 0, 1, 0]))
    cv.save(); cv.concat(m); cv.drawImage(im, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p); cv.restore()


def scene_pages():
    if T.CLOSED_BOOK: return [("hook", 1)]
    if MODE == "read":
        if T.RECAP:
            import json as _j
            order = _j.load(open(os.path.join(HERE_, "..", "songs", "recap", "code", "out", "song_check.json")))["lines"]
            ns = [int(L["sec"].split()[1]) for L in order if L["sec"].startswith("Moral")]
            return [("hook", T.PAGE_FROM)] + [("story", n) for n in ns] + [("end", 0)]
        return [("hook", T.PAGE_FROM), ("hook", T.PAGE_TO)]
    return [("story", T.FABLE or 5)]
PAGES = scene_pages()

@lru_cache(maxsize=None)
def quiz_image(n, at):
    """full-frame picture insert: the fable still on a storybook page (cream paper, rounded frame, number badge)"""
    arr = np.zeros((H, W, 4), np.uint8); cv = skia.Surface(arr).getCanvas()
    cv.clear(skia.Color(250, 240, 214))
    rng = np.random.default_rng(n)
    for k in range(60):                                                 # paper speckle
        cv.drawCircle(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3), skia.Paint(AntiAlias=True, Color=skia.Color(232, 218, 188)))
    p = still_path(n, at)
    mx, my = int(W * 0.07), int(H * 0.08); iw, ih = W - 2 * mx, H - 2 * my - int(H * 0.06)
    if p:
        im = Image.open(p).convert("RGB"); sw, sh = im.size
        ch = int(sh * 0.80); cw = min(sw, int(ch * iw / ih)); x0 = (sw - cw) // 2
        im = im.crop((x0, 0, x0 + cw, ch)).resize((iw, ih), Image.LANCZOS)
        rgba = np.dstack([np.asarray(im), np.full((ih, iw), 255, np.uint8)])
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx - 14 + 10, my - 14 + 14, iw + 28, ih + 28), 46, 46),
                     skia.Paint(AntiAlias=True, Color=skia.Color(150, 120, 90, 90)))                     # soft shadow
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx - 14, my - 14, iw + 28, ih + 28), 46, 46),
                     skia.Paint(AntiAlias=True, Color=skia.Color(255, 250, 240)))
        cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx, my, iw, ih), 34, 34), True)
        cv.drawImage(_skimg(rgba), mx, my); cv.restore()
    cv.drawCircle(mx + 40, my + 40, 62, skia.Paint(AntiAlias=True, Color=skia.Color(255, 214, 80)))
    _text(cv, "?", mx + 40, my + 72, 96, (255, 250, 240), 10)
    return arr
def page_insert(t):
    for P in T.PAGES:
        if P["t0"] <= t < P["t1"]: return P
    return None

_render_frame = FK.render_frame
def render_frame(t):
    if T.kind_at(t) == "page":                                         # a 2D picture insert: no 3D needed
        P = page_insert(t) or T.PAGES[0]
        base = quiz_image(P["fable"], float(P["still"]))
        u = clampu(t, P["t0"], P["t1"]); z = 1.0 + 0.05 * u                # slow push in
        img = np.zeros((H, W, 4), np.uint8); cv = skia.Surface(img).getCanvas()
        cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-W / 2, -H / 2)
        cv.drawImage(_skimg(base), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        img[..., 3] = 255
        return img
    return _render_frame(t)
FK.render_frame = render_frame

_overlay = FK.overlay
def overlay(img, t):
    if T.kind_at(t) != "page":
        eye, tgt, fov = camera(t)
        q = QUADS.get(round(t, 4))
        if q:
            surf_ = skia.Surface(img); cv = surf_.getCanvas()
            cover_q, spread_q, facing = q
            if facing < -0.995 and cover_angle(t) < 0.02:
                pq = _project(eye, tgt, fov, cover_q)
                if pq: _draw_quad(img, cv, cover_image(), pq, 1.0)
            idx, alpha = spread_index(t) if MODE == "read" else (0, 1.0)
            if PAGES and alpha > 0.01:
                pq = _project(eye, tgt, fov, spread_q)
                if pq: _draw_quad(img, cv, page_image(*PAGES[min(idx, len(PAGES) - 1)]), pq, alpha, ref=PAGE)
            del surf_
    return _overlay(img, t)
FK.overlay = overlay

# ================= draws =================
def build_draws(t):
    NOW["t"] = t
    draws, contacts = [], []
    backdrop(draws, t)
    draws.append((E2["stump"], trans(STUMP[0], ground_h(*STUMP) - 0.02, STUMP[1]) @ roty(STUMP_YAW) @ scale(STUMP_S), U(mat=0, bump=0.9, obj="stump"), True))
    for (x, z, s) in [(STUMP[0] + 1.9, STUMP[1] + 0.9, 0.2), (STUMP[0] - 2.6, STUMP[1] - 0.6, 0.17), (STUMP[0] - 1.5, STUMP[1] - 1.6, 0.22)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6, obj="mushroom"), True))
    draw_flowers(draws, t, FLOWERS)
    st = tumble(t); mats = fox_mats(st)
    draw_tumble(draws, contacts, t, st, mats)
    if MODE == "read":
        Mb = fox_root(dict(st, sq=0.0)) @ book_frame_local(t); turn, _ = page_turn(t)
        QUADS[round(t, 4)] = book_draws(draws, Mb, cover_angle(t), turn)
    else:
        QUADS[round(t, 4)] = book_draws(draws, BOOK_FLAT, math.pi, None)
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, mats[2])
    for hf in T.HIGH_FIVES[:-1]:                                        # the kit puffs the last high-five only
        puff(draws, hand_pos(mats[2]) + np.array([0.08, 0.12, 0.16]), hf, t, n=6, size=0.032, spread=0.55, dur=0.35, tint=(1.0, 0.88, 0.35), axis=(0, 0.25, 0.25))
    if len(QUADS) > 64: QUADS.pop(next(iter(QUADS)))
    return draws, contacts

HOOKS.update(build=build_draws, camera=camera, tumble=tumble, sky=sky_hook,
             ground_objs=lambda t: ("fox", "pip"),
             qa_ignore={("book", "fox"), ("fox", "book")})

def main_episode():
    os.makedirs("out", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "qa": FK.qa(out=f"out/qa_{SCENE}.json"); return
    if len(sys.argv) > 1 and sys.argv[1] == "sheet": FK.sheets(outdir=f"review/{SCENE}"); return
    if len(sys.argv) > 1 and sys.argv[1] == "x":
        for s in sys.argv[2:]:
            t0 = time.time(); fr = overlay(render_frame(float(s)), float(s))
            skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/still_{SCENE}_{float(s):05.2f}.png")
            print(s, round(time.time() - t0, 2), "s", flush=True)
        return
    FK.main()
if __name__ == "__main__":
    main_episode()
