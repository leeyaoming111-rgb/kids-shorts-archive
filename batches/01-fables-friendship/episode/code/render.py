"""Tumble & Pip, Episode 01: the Story Stump scenes (intro, link01..link09, break, recap, outro). 16:9 only.
Shared renderer: fablekit.py (unchanged). Kit overrides, all in this file:
  - a copy of the clay shader with the key light, ambient and fog colours as uniforms (sunset to night light);
  - draw_pass sets them per frame; overlay() first draws the storybook pictures onto the page quads;
  - hf_curves takes several high-fives (the break sings the chorus twice); stills, sheets and QA go per scene.
python3 render.py --scene <name> [--preview] [out.mp4] | x <secs...> | seg f0 f1 out.mp4 | sheet | qa"""
import os, sys
if "--scene" in sys.argv:
    _i = sys.argv.index("--scene"); os.environ["SCENE"] = sys.argv[_i + 1]; del sys.argv[_i:_i + 2]
from fablekit import *
import fablekit as FK
import episode as EP
from functools import lru_cache
from scipy.optimize import minimize
SCENE = T.SCENE
LINK = T.LINK

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

# ---- the book's state through each scene ----
OPEN_DUR, TURN_DUR, CLOSE_DUR = 1.1, 0.75, 1.4
def cover_angle(t):
    if SCENE == "intro": return math.pi * ease(clampu(t, T.OPEN, T.OPEN + OPEN_DUR))
    if SCENE == "outro": return math.pi * (1 - ease(clampu(t, T.CLOSE, T.CLOSE + CLOSE_DUR)))
    return math.pi
def page_turn(t):
    for a, k in T.TURNS:
        if a <= t < a + TURN_DUR: return math.pi * ease(clampu(t, a, a + TURN_DUR)), k
    return None, None
def spread_index(t):
    """which picture is on the open spread (0-based within the scene), and its alpha"""
    idx, alpha = 0, 1.0
    for a, k in T.TURNS:
        if t >= a: idx = k
        if a - 0.2 <= t < a: alpha = min(alpha, (a - t) / 0.2)
        if a <= t < a + TURN_DUR + 0.25: alpha = min(alpha, clamp01((t - a - TURN_DUR) / 0.25))
    th = cover_angle(t)
    if th < math.pi * 0.98: alpha = 0.0 if SCENE == "intro" else alpha
    if SCENE == "intro": alpha *= clamp01((t - T.OPEN - OPEN_DUR) / 0.3)
    if SCENE == "outro": alpha *= clamp01((T.CLOSE - t) / 0.25)
    return idx, alpha

# ================= Tumble =================
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
def book_frame_local(t):
    """book frame in Tumble's (unsquashed) frame while he holds it; the spine slides right as the cover opens"""
    th = cover_angle(t)
    sx = -CW / 2 * (1 - th / math.pi)
    return trans(*(BOOK_C + np.array([sx, 0, 0]))) @ trans(0, -CH / 2, 0) @ rotx(-BOOK_TILT) @ trans(0, CH / 2, 0)
HOLD_Z = -0.035                                                     # paws just behind the cover edges
def grip(t, side):
    """paw target in the book frame: outer cover edge (side +1 right, -1 left); the left paw lets go while it opens"""
    th = cover_angle(t)
    if side > 0: return np.array([CW + 0.035, 0.02, HOLD_Z])
    closed = np.array([-0.035, 0.02, HOLD_Z]); opened = np.array([-(CW + 0.035), 0.02, HOLD_Z])
    away = np.array([-0.30, -0.45, HOLD_Z - 0.04])
    u = th / math.pi
    if u <= 0.0: return closed
    if u >= 1.0: return opened
    if u < 0.35: return lerp(closed, away, ease(u / 0.35))
    if u < 0.85: return away
    return lerp(away, opened, ease((u - 0.85) / 0.15))
def hold_book(st, t):
    """arms from IK onto the book edges (in the squashed body frame, so the paws stay on the edges)"""
    R = fox_root(st); B = book_frame_local(t)
    lift = page_flick(t)
    for i, side in ((0, 1), (1, -1)):
        g = grip(t, side) + (np.array([0, 0.06, 0.04]) * lift if i == 0 else 0)
        w = apply(fox_root(dict(st, sq=0.0)) @ B, g)
        st["arms"][i] = ik(i, apply(np.linalg.inv(R), w))
    return st
def page_flick(t):
    for a, k in T.TURNS:
        if a - 0.25 <= t < a + 0.35: return math.sin(math.pi * clampu(t, a - 0.25, a + 0.35))
    return 0.0
def talk_bob(st, t, who="tumble"):
    for L in T.LINES:
        if L["who"] in (who, "both") and L["t0"] <= t <= L["t1"]:
            st["y"] += 0.018 * abs(math.sin((t - L["t0"]) * 7)); st["head"][0] += 0.04 * math.sin((t - L["t0"]) * 5)
    return st
def speaking(who, t):
    return any(L["who"] in (who, "both") and L["t0"] - 0.2 <= t <= L["t1"] + 0.2 for L in T.LINES)

def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    if SCENE == "break":
        st["x"], st["z"] = DANCE_SPOT; st["yaw"] = -0.05
        if n == "call":
            L = T.TALK[0]
            up = ease(clampu(t, 0.6, 1.4))
            st["arms"][0] = lerp([0.15, 0.0], DANCE_ARM, up).tolist()
            st["arms"][1] = [0.5 + 1.2 * math.sin(math.pi * clampu(t, 0.2, 1.0)), 0.3]       # "stand up!" wave
            if L["t0"] < t < L["t1"]: st["y"] += 0.02 * abs(math.sin((t - L["t0"]) * 8))
        elif n == "chorus":
            dance_tumble(st, t, "chorus")
        else:
            st["arms"][0] = list(DANCE_ARM); st["head"][2] = 0.08
            st["arms"][1] = [0.6 + 0.9 * abs(math.sin((t - SH["well_done"][0]) * 3.2)), 0.25]   # waves goodbye to the dance
        return st
    st["x"], st["z"] = FOX_AT; st["stand_h"] = STUMP_TOP; st["yaw"] = 0.0; st["tail"] *= 0.6
    st["sq"] *= 0.5
    if speaking("pip", t) and not speaking("tumble", t): st["head"][1] = 0.32; st["head"][0] = 0.08     # listens to Pip
    else: st["head"][0] = -0.04
    turn, _ = page_turn(t)
    if turn is not None or (SCENE == "intro" and T.OPEN - 0.2 < t < T.OPEN + OPEN_DUR + 0.2):
        st["head"][0] = 0.28; st["head"][1] = 0.0                                                   # looks down at the book
    if SCENE == "outro" and t > T.CLOSE: st["head"][0] = 0.12 + 0.04 * math.sin(t * 1.2); st["head"][2] = 0.1 * math.sin(t * 0.9)
    if SCENE == "recap":                                                                       # sways to the song
        st["roll"] = 0.03 * math.sin(2 * math.pi * t / (2 * BEAT))
    talk_bob(st, t)
    return hold_book(st, t)

# ================= Pip =================
def hop(t, t0, h=0.14, dur=0.32):
    d = t - t0
    return h * math.sin(math.pi * d / dur) if 0 <= d < dur else 0.0
def legs_path(t, a, pts, dur):
    """straight flight legs through pts, starting at time a, total duration dur (time split by leg length)"""
    L = [np.linalg.norm(np.asarray(q) - np.asarray(p)) for p, q in zip(pts[:-1], pts[1:])]; tot = sum(L)
    u = clampu(t, a, a + dur) * tot
    for p, q, l in zip(pts[:-1], pts[1:], L):
        if u <= l: return lerp(p, q, ease(u / max(l, 1e-6)) if len(L) == 1 else u / max(l, 1e-6))
        u -= l
    return np.asarray(pts[-1], float)
PIP_YAW = -0.55                                                      # faces the audience, turned towards Tumble
def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    R, Mh, arms, legs = mats
    face = apply(Mh, (0, 1.55, 0.5))
    look = math.atan2(face[0] - PIP_SPOT[0], face[2] - PIP_SPOT[2])
    yaw = look if (speaking("tumble", t) and not speaking("pip", t)) else PIP_YAW
    p = PIP_SPOT.copy(); ex = {}
    if SCENE == "break":
        if n == "call":
            seat = paw_seat(fox_mats(tumble(2.5))[2])
            start = np.array([STUMP[0] + 0.55, TOPY, STUMP[1] + 0.55]) + UP
            if t < 0.9: return start, 0.3, False, 0.0, True, {}
            q = legs_path(t, 0.9, [start, start + np.array([0, 0.9, 0]), seat + np.array([0, 0.7, 0]), seat], 1.5)
            if t >= 2.4: return seat, 0.35, False, 0.0, True, {}
            return q, 0.35, True, 0.0, False, {"gentle": True}
        if n == "chorus": return dance_pip(t, st, mats, "chorus")
        top = paw_seat(arms)
        return top, 0.35, False, 0.0, True, {"cheer": speaking("pip", t)}
    if SCENE == "intro" and t < T.PIP_LAND + 0.05:                   # flies in during the title, lands as he speaks
        a, b = 0.5, T.PIP_LAND
        pts = [np.array([-3.2, TOPY + 2.5, STUMP[1] + 0.4]), np.array([1.35, TOPY + 2.5, STUMP[1] + 0.45]),
               np.array([1.35, TOPY + 0.45, STUMP[1] + 0.45]), PIP_SPOT + np.array([0, 0.12, 0])]
        if t < b - 0.12:
            q = legs_path(t, a, pts, b - 0.12 - a)
            return q, (1.4 if q[0] < 1.3 else -0.9), True, 0.0, False, {"gentle": True}
        u = clampu(t, b - 0.12, b)
        return lerp(PIP_SPOT + np.array([0, 0.12, 0]), PIP_SPOT, u), PIP_YAW, True, 0.0, False, {"gentle": True}
    # ---- small gags, one per scene ----
    if SCENE == "intro":
        L4 = T.TALK[3]
        for w in L4["words"][1:]: p[1] += hop(t, w["t0"])               # "Open it, open it!" hops
        if n == "thats_me": ex = {"point": True} if T.TALK[6]["t0"] - 0.1 < t < T.TALK[6]["t1"] + 0.6 else {}
    elif SCENE == "link01":
        A = T.TALK[0]
        if A["t0"] < t < A["t1"] + 0.4: ex = {"cheer": True}; p[1] += 0.02 * math.sin((t - A["t0"]) * 9)
    elif SCENE == "link03":                                             # one hop per counted pebble
        for k_ in ("one", "two", "three", "four", "five"):
            for tw in T.word_times(k_, [T.TALK[0]]): p[1] += hop(t, tw, 0.12, 0.3)
    elif SCENE == "link05":                                             # marches on the spot
        B = T.TALK[1]
        if B["t0"] < t < B["t1"] + 0.3: p[1] += 0.05 * abs(math.sin((t - B["t0"]) * 6)); yaw = PIP_YAW + 0.2 * math.sin((t - B["t0"]) * 6)
    elif SCENE == "link07":
        for tw in T.word_times("snap", [T.TALK[1]]):
            if tw - 0.05 < t < tw + 0.35: ex = {"wings": (1.25, 1.25)}
    elif SCENE == "link08":                                             # a big sleepy stretch after his line
        A = T.TALK[0]; u = clampu(t, A["t1"] + 0.3, A["t1"] + 1.6)
        if 0 < u < 1:
            s = math.sin(math.pi * u); ex = {"wings": (0.9 * s + 0.04, 0.9 * s + 0.04)}
            ex["cling"] = -0.6 * s
    elif SCENE == "link09":
        B = T.TALK[1]
        if B["t0"] - 0.1 < t < B["t1"] + 0.3: ex = {"droop": 0.6}
    elif SCENE == "recap":                                              # sways on every second beat
        p[0] += 0.03 * math.sin(2 * math.pi * t / (2 * BEAT)); ex = {"cheer": False}
    elif SCENE == "outro":
        G = T.TALK[0]
        if G["t0"] - 0.1 < t < G["t1"] + 0.8: ex = {"wings": (0.04, 1.0 + 0.3 * math.sin(t * 7))}   # waves goodnight
        if t > G["t1"] + 0.8: ex = {"tuck": True}
    return p, yaw, False, 0.0, True, ex

# ================= cameras =================
def cam_two(e, yaw=6.0, pitch=7.0, fw=1.75, fh=1.45, cx=0.18, cy=1.25):
    return fit_cam(np.array([STUMP[0] + cx, TOPY + cy, STUMP[1] + 0.2]), yaw, pitch, fw, fh)
def cam_spread(e, yaw=0.0, pitch=4.0, fh=0.31, cy=0.0, cx=0.0, fov=34):
    """insert on the book (centre of the book + offsets), framed so Pip stays out of shot"""
    return fit_cam(np.array([FOX_AT[0] - 0.06 + cx, TOPY + 0.79 + cy, FOX_AT[1] + 0.5]), yaw, pitch, fh * 1.78, fh, fov=fov, lift=0.0)
def cam_med(e, yaw=0.0, pitch=5.0, fh=1.0, cx=0.2, cy=1.25):
    """medium: book, Tumble's face and Pip"""
    return fit_cam(np.array([FOX_AT[0] + cx, TOPY + cy, FOX_AT[1] + 0.4]), yaw, pitch, fh * 1.78, fh, lift=0.04)
LINK_CAMS = {   # (shot a: yaw, pitch, fit_w, fit_h, cx, cy), (shot b: yaw, pitch, fit_h, cy, cx)
    1: ((-24, 6, 1.6, 1.35, 0.25, 1.2), (-6, 4, 0.66, 0.98, 0.05)),
    2: ((30, 9, 1.35, 1.2, 0.35, 1.1), (5, 3, 0.62, 0.95, 0.0)),
    3: ((4, -3, 1.6, 1.45, 0.25, 1.15), (0, 6, 0.75, 1.0, 0.1)),
    4: ((-34, 16, 1.7, 1.45, 0.2, 1.15), (-8, 8, 0.64, 0.98, 0.0)),
    5: ((12, 5, 1.75, 1.5, 0.15, 1.2), (4, 3, 0.66, 0.96, 0.05)),
    6: ((50, 7, 1.6, 1.4, 0.25, 1.15), (10, 5, 0.66, 0.98, 0.05)),
    7: ((-14, 5, 1.25, 1.1, 0.3, 1.0), (-4, 2, 0.6, 0.96, 0.0)),
    8: ((22, 10, 1.75, 1.5, 0.2, 1.2), (6, 6, 0.7, 1.0, 0.05)),
    9: ((-6, 6, 1.6, 1.4, 0.2, 1.2), (0, 4, 0.72, 1.0, 0.05)),
}
def camera(t):
    i, name, u, el = T.shot_at(t); e = ease(u)
    if SCENE == "intro":
        if name == "title_wide": return fit_cam(np.array([STUMP[0] + 0.2, TOPY + 1.0, STUMP[1]]), lerp(-8, -3, e), 6, 3.6, 2.7, lift=-0.22)
        if name == "arrive": return cam_two(e, lerp(10, 6, e), 6, 1.8, 1.5)
        if name == "show_cover": return cam_two(e, lerp(-10, -6, e), 7, 1.55, 1.3, cx=0.1, cy=1.15)
        if name == "cover_close": return cam_spread(e, lerp(-4, 2, e), 3, lerp(0.36, 0.33, e), cx=0.06)
        if name == "open_book": return cam_two(e, lerp(16, 12, e), 8, 1.6, 1.35, cx=0.2, cy=1.15)
        if name == "spread_close": return cam_spread(e, lerp(-3, 3, e), 4, lerp(0.33, 0.31, e))
        return cam_two(e, lerp(-14, -10, e), 6, 1.5, 1.3, cx=0.3, cy=1.05)
    if LINK:
        a, b = LINK_CAMS[int(SCENE[4:])]
        if name.startswith("a_"):
            yaw, pitch, fw, fh, cx, cy = a
            return cam_two(e, yaw + 4 * e, pitch, fw * lerp(1.0, 0.95, e), fh * lerp(1.0, 0.95, e), cx=cx, cy=cy)
        yaw, pitch, fh, cy, cx = b
        if name.startswith("b_"): return cam_spread(e, yaw + 2 * e, pitch, fh * 0.48, cx=cx * 0.3)   # the new picture
        fh = fh / 0.66 * 1.22                                           # medium: the spread, Tumble's face and Pip, clear of the caption
        if SCENE == "link09": fh *= lerp(1.0, 0.9, e)                  # slow push in
        return cam_med(e, yaw + 2 * e, pitch, fh, cx=0.22 + cx, cy=0.92)
    if SCENE == "break":
        tg = np.array([DANCE_SPOT[0] + 0.25, 1.25, DANCE_SPOT[1]])
        if name == "call": return fit_cam(tg, 4, 6, 1.75, 1.55)
        if name == "chorus": return fit_cam(tg, lerp(5, -5, u), 6, 1.55, 1.4)
        return fit_cam(tg, -4, 7, 1.7, 1.5)
    if SCENE == "recap":
        k = i % 3
        if name == "recap_end": return cam_two(e, lerp(-8, -4, e), 7, 1.7, 1.45)
        if k == 0: return cam_spread(e, lerp(-3, 2, e), 4, 0.31)
        if k == 1: return cam_med(e, lerp(10, 6, e), 6, 1.0)
        return cam_spread(e, lerp(4, -1, e), 8, 0.33)
    if SCENE == "outro":
        if name == "lullaby_a": return cam_two(e, lerp(8, 4, e), 6, 1.6, 1.35)
        if name == "lullaby_b": return fit_cam(np.array([STUMP[0] + 0.2, TOPY + 1.2, STUMP[1]]), lerp(-6, -10, e), 6, 2.9, 2.2)
        if name == "goodnight": return cam_two(e, lerp(4, 2, e), 5, 1.4, 1.2, cx=0.25, cy=1.05)
        eye, tgt, fov = cam_two(0, 2, 5, 1.6, 1.4, cx=0.2, cy=1.2)        # crane up to the moon and stars
        up = ease(clampu(t, SH["sky"][0] + 0.3, SH["sky"][0] + 3.6))
        tgt = lerp(tgt, np.array([3.0, 9.0, -30.0]), up); eye = eye + np.array([0, 1.6 * up, 1.2 * up])
        return eye, tgt, fov
    return cam_two(e)

# ================= pictures on the pages =================
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
def scene_pages():
    if SCENE == "intro": return [("hook", 1)]
    if LINK:
        k = EP.ORDER.index(SCENE); prev = next(x for x in EP.ORDER[k::-1] if isinstance(x, int))
        return [("hook", prev), ("hook", EP.LINK_NEXT[SCENE])]
    if SCENE == "recap": return [("story", n) for n in EP.RECAP_ORDER]
    if SCENE == "outro": return [("end", 0)]
    return []
PAGES = scene_pages()
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
_overlay = FK.overlay
def overlay(img, t):
    eye, tgt, fov = camera(t)
    q = QUADS.get(round(t, 4))
    if q:
        surf_ = skia.Surface(img); cv = surf_.getCanvas()
        cover_q, spread_q, facing = q
        if facing < -0.995 and cover_angle(t) < 0.02 and SCENE in ("intro", "outro"):  # gold title on the closed cover
            pq = _project(eye, tgt, fov, cover_q)
            if pq: _draw_quad(img, cv, cover_image(), pq, 1.0)
        idx, alpha = spread_index(t)
        if PAGES and alpha > 0.01 and SCENE != "break":
            pq = _project(eye, tgt, fov, spread_q)
            if pq: _draw_quad(img, cv, page_image(*PAGES[min(idx, len(PAGES) - 1)]), pq, alpha, ref=PAGE)
        del surf_
    out = _overlay(img, t)
    if T.FADE_OUT:
        out = (out.astype(np.float32) * (1 - ease(clampu(t, *T.FADE_OUT)))).astype(np.uint8)
    return out
FK.overlay = overlay

# ================= draws =================
def build_draws(t):
    NOW["t"] = t
    draws, contacts = [], []
    backdrop(draws, t)
    draws.append((E2["stump"], trans(STUMP[0], ground_h(*STUMP) - 0.02, STUMP[1]) @ roty(STUMP_YAW) @ scale(STUMP_S), U(mat=0, bump=0.9, obj="stump"), True))
    for (x, z, s) in [(STUMP[0] + 1.9, STUMP[1] + 0.9, 0.2), (STUMP[0] - 2.1, STUMP[1] + 0.4, 0.17), (STUMP[0] - 1.5, STUMP[1] - 1.4, 0.22)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6), True))
    draw_flowers(draws, t, FLOWERS)
    st = tumble(t); mats = fox_mats(st)
    draw_tumble(draws, contacts, t, st, mats)
    if SCENE == "break":                                                # the book lies open on the stump
        Mb = trans(STUMP[0] - 0.05, TOPY + CT + 0.002, STUMP[1] - 0.05) @ roty(0.15) @ rotx(-math.pi / 2)
        QUADS[round(t, 4)] = book_draws(draws, Mb, math.pi, None)
    else:
        Mb = fox_root(dict(st, sq=0.0)) @ book_frame_local(t)
        turn, _ = page_turn(t)
        QUADS[round(t, 4)] = book_draws(draws, Mb, cover_angle(t), turn)
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, mats[2])
    if SCENE == "break":                                                # the first high-five's star puff (the kit puffs the last)
        for hf in T.HIGH_FIVES[:-1]:
            puff(draws, hand_pos(mats[2]) + np.array([0, 0.2, 0]), hf, t, n=8, size=0.05, spread=0.7, dur=0.4, tint=(1.0, 0.88, 0.35), axis=(0, 0, 0.3))
    if len(QUADS) > 64: QUADS.pop(next(iter(QUADS)))
    return draws, contacts

HOOKS.update(build=build_draws, camera=camera, tumble=tumble, sky=sky_hook,
             ground_objs=lambda t: ("fox", "pip"),
             qa_ignore={("book", "fox"), ("fox", "book")})               # the held book: paws grip its edges

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
