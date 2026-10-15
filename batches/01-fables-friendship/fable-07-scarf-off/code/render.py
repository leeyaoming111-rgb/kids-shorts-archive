"""Tumble & Pip Fables 7: Scarf Off!  (Aesop: The North Wind and the Sun)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa
Kit override (no fablekit edit): draw_pass is replaced below so the key light can ramp with the sky (wind / sun)."""
from fablekit import *
import fablekit as FK

COLORS.update(windy=(90, 160, 220), sunny=(245, 160, 30), scarf=(225, 70, 80))

# ---------------- world: the little hill by Tumble's cottage (a new corner of Picnic Meadow) ----------------
SPOT = (0.0, 0.0)
COTTAGE = (3.1, -4.2)
POSTS = [(1.25, -0.6), (1.95, -1.0), (2.65, -1.4)]          # garden fence; Pip referees from the first post
POST_H = 0.95; POST_R = 0.07
def post_top(p): return float(surf(*p)) - 0.02 + 1.05 * POST_H
POST_PIP = np.array([POSTS[0][0], post_top(POSTS[0]) - 0.02, POSTS[0][1]]) + UP
FLOWER = (2.3, 0.3); FLOWER_S = 4.0                          # the big flower Pip clings to (downwind of the post)
STEM_R = 0.025 * FLOWER_S
WIND_P = np.array([-1.75, 5.5, -4.6])                         # the sky faces
SUN_P = np.array([1.95, 6.5, -6.2])
WIND_S, SUN_S = 0.95, 0.9
WIND_DIR = np.array([1.0, -0.12, 0.22]); WIND_DIR /= np.linalg.norm(WIND_DIR)
FLOWERS = make_flowers([(SPOT[0], SPOT[1], 1.6), ("box", -2.6, 0.4, -0.9, 0.9), (FLOWER[0], FLOWER[1], 0.4),
                        ("box", 0.4, 2.4, -0.4, 2.2), ("box", 0.8, 3.2, -1.8, -0.2), (COTTAGE[0], COTTAGE[1], 6.0)], seed=71)

# ---------------- weather: wind strength, sky colours and key light (ramps of 1.2 s or more: no flashing) ----------------
def wind_w(t):
    if t < T.SH_BUTTON: return ease(clampu(t, T.BLOW0, T.BLOW0 + 0.5)) * (1 - ease(clampu(t, T.BLOW1, T.BLOW1 + 0.9)))
    return 0.22 * ease(clampu(t, T.SH_BUTTON + 0.2, T.SH_BUTTON + 0.8))      # the gentle cooling breeze
def gusty(t):                                                # the big gust that spins him
    return ease(clampu(t, T.SPIN0 - 0.3, T.SPIN0)) * (1 - ease(clampu(t, T.SPIN1, T.SPIN1 + 0.5)))
SKY_WINDY = ((0.55, 0.68, 0.86), (0.74, 0.84, 0.94), (0.92, 0.92, 0.94))
SKY_SUNNY = ((0.40, 0.68, 0.98), (0.70, 0.87, 1.0), (1.0, 0.90, 0.72))
def weather(t):
    """(windy, sunny) mix weights, each ramped over 1.2-1.6 s"""
    wy = ease(clampu(t, T.BLOW0 - 0.2, T.BLOW0 + 1.0)) * (1 - ease(clampu(t, T.BLOW1, T.BLOW1 + 1.4)))
    sn = ease(clampu(t, T.SUN0, T.SUN0 + 1.6))
    return wy, sn
def sky(t):
    wy, sn = weather(t)
    return tuple(tuple(lerp(lerp(c0, c1, wy), c2, sn)) for c0, c1, c2 in zip(SKY, SKY_WINDY, SKY_SUNNY))
def key_i(t):
    wy, sn = weather(t)
    return 1.05 - 0.12 * wy + 0.12 * sn

def draw_pass(draws, contacts, eye, tgt, fov, vp, sky_):
    """the kit's draw_pass with the key light intensity from key_i(t) instead of a constant"""
    x, y, w, h = vp
    VPm = perspective(fov, w / h, 0.12, 90.0) @ look_at(eye, tgt)
    ctx.viewport = vp
    ctx.disable(moderngl.DEPTH_TEST)
    skyprog["cTop"].value = sky_[0]; skyprog["cMid"].value = sky_[1]; skyprog["cHor"].value = sky_[2]
    sky_vao.render()
    ctx.enable(moderngl.DEPTH_TEST)
    shadow_tex.use(0); prog["shadowMap"].value = 0
    prog["VP"].value = gl(VPm); prog["LVP"].value = gl(LVP); prog["camPos"].value = tuple(eye)
    cvals = [tuple(c) for c in contacts] + [(0, 0, 1, 0)] * (8 - len(contacts))
    prog["contact"].value = cvals[:8]; prog["nContact"].value = min(len(contacts), 8)
    prog["fade"].value = 1.0; prog["keyI"].value = key_i(_NOW[0])
    for (mesh, M, u, cast) in draws:
        prog["M"].value = gl(M); prog["NM"].value = nmat(M)
        prog["mat"].value = u.get("mat", 0); prog["bump"].value = u.get("bump", 1.0)
        prog["tint"].value = tuple(u.get("tint", (1, 1, 1))); prog["tintMix"].value = u.get("tintMix", 0.0)
        prog["seed"].value = u.get("seed", 0.0)
        mesh.vao.render()
FK.draw_pass = draw_pass
_NOW = [0.0]

# Kit fix (no fablekit edit): render_base builds the shadow-pass VAOs as "3f 36x" (48-byte stride) but a vertex is
# 10 floats (40 bytes), so shadows were drawn from scrambled vertices. Rebuild them with the right stride.
for _grp in (FOXP, PIPP, PR, SC, E2, {"w": EYE_W, "p": EYE_P}):
    for _m in _grp.values():
        _m.svao = ctx.vertex_array(sprog, [(_m.vbo, "3f 28x", "in_pos")], _m.ibo)

# ---------------- Tumble ----------------
def arm_hand(side, fwd, i=0):
    st = tumble_base(0.0); st["arms"][i] = [side, fwd]; st["yaw"] = 0.0; st["sq"] = 0.0
    return hand_pos(fox_mats(st)[2], i)
def solve_arm(target, i=0):
    best = None
    for sd in np.linspace(-0.3, 1.6, 39):
        for fw in np.linspace(-0.2, 2.2, 49):
            d = np.linalg.norm(arm_hand(sd, fw, i) - target)
            if best is None or d < best[0]: best = (d, sd, fw)
    return [best[1], best[2]]
HUG = [[0.3, 1.25, 0.62], [0.3, 1.25, 0.62]]                           # paws clutching the scarf at his chest
PULL_OUT = [1.4, 0.45]                                      # right paw out to the side, pulling the scarf through

def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    st["x"], st["z"] = SPOT; st["yaw"] = -0.05
    if n == "hook_sky":                                      # looking up at the faces in the sky
        st["head"][0] = -0.3 + 0.04 * math.sin(t * 2); st["arms"] = [[0.35, 0.5], [0.35, 0.5]]
    elif n == "title_wide":
        a = SH[n][0]; wv = clampu(t, a + 0.3, a + 1.9)       # waves to us
        st["arms"][1] = [1.5 + 0.35 * math.sin((t - a) * 9) * math.sin(math.pi * wv), 0.2] if 0 < wv < 1 else [0.2, 0.0]
    elif n in ("sky_faces", "whistle"):
        st["head"][0] = -0.25
        if n == "whistle": st["tail"] = 1.3 + 0.15 * math.sin(t * 2.6)   # tail curled to his left, out of Pip's macro
    elif n == "snug":                                        # pats and hugs his scarf, cosy little bounce
        L = T.line("Setup B")
        hug = ease(clampu(t, L["t0"] + 0.9, L["t0"] + 1.4))
        st["arms"] = [lerp([0.2, 0.3, 0.0], HUG[0], hug).tolist(), lerp([0.2, 0.3, 0.0], HUG[1], hug).tolist()]
        st["head"][2] = 0.12 * math.sin((t - L["t0"]) * 2.5) * hug; st["eyes_closed"] = L["t1"] - 0.6 < t < L["t1"] + 0.6
        st["y"] += 0.03 * abs(math.sin((t - L["t0"]) * 6)) * hug
    elif n in ("wind_puff", "hold_tight"):                   # hugs the scarf and leans into the wind, head wobbling
        w = wind_w(t)
        st["arms"] = [list(HUG[0]), list(HUG[1])]
        st["roll"] = 0.1 * w; st["head"][2] = 0.06 * w * math.sin(t * 17); st["head"][1] = 0.08 * w * math.sin(t * 11)
        st["sq"] += 0.02 * w * math.sin(t * 23); st["tail"] = 0.6 * w + 0.2 * math.sin(t * 13)
    elif n == "spin":                                        # the gust spins him round like a weathervane
        u = clampu(t, T.SPIN0, T.SPIN1)
        st["yaw"] = -0.05 + 4 * math.pi * ease(u)
        st["arms"] = [list(HUG[0]), list(HUG[1])]
        st["y"] += 0.06 * math.sin(math.pi * u); st["tail"] = 0.8 * gusty(t)
        d = t - T.SPIN1
        if d > 0:                                            # dizzy wobble to a stop
            st["roll"] = 0.12 * math.sin(d * 9) * math.exp(-d * 1.6); st["head"][2] = -0.15 * math.sin(d * 7) * math.exp(-d * 1.2)
    elif n in ("pip_cling", "wind_tired", "sun_shine"):
        st["arms"] = [list(HUG[0]), list(HUG[1])]; st["head"][0] = -0.2
    elif n == "scarf_off":                                   # warm: fans himself, then pulls the scarf off through his paw
        a = SH[n][0]
        st["head"][0] = -0.12; st["eyes_closed"] = t < a + 0.5
        st["arms"][1] = [0.9 + 0.25 * math.sin((t - a) * 14), 1.1] if t < T.GRAB - 0.1 else [0.25, 0.35]
        g = ease(clampu(t, T.GRAB - 0.35, T.GRAB))
        st["arms"][0] = lerp([0.2, 0.3], GRAB_ARM, g).tolist()
        if t > T.GRAB:
            u = ease(clampu(t, T.GRAB + 0.1, T.GRAB + 0.7))
            tug = 0.12 * max(0.0, math.sin((t - T.GRAB) * 11)) * (1 if t < T.FREE else 0)
            st["arms"][0] = lerp(GRAB_ARM, PULL_OUT, u).tolist(); st["arms"][0][0] += tug
            st["head"][1] = 0.25 * u; st["head"][2] = -0.08 * u
        if t > T.FREE: st["y"] += 0.04 * abs(math.sin((t - T.FREE) * 8))
    elif n == "sunbathe":                                    # drops the scarf, lies down in the sunshine
        st["arms"][0] = lerp(PULL_OUT, [0.4, 0.2], ease(clampu(t, T.DROP, T.DROP + 0.3))).tolist()
        lie = ease(clampu(t, T.LIE0, T.LIE1))
        st["lie"] = lie; st["eyes_closed"] = t > T.LIE1 - 0.2
        if lie > 0: st["arms"] = [[0.6 + 0.6 * lie, 0.2], [0.4, 0.2]]
        st["head"][2] = -1.1 * lie; st["head"][0] = 0.1 * lie                 # head stays up, resting, while the body lies on its side
        st["tail"] = 0.3 * math.sin(t * 2)
    elif n in ("moral", "chorus"):
        dance_tumble(st, t, n)
    else:                                                    # button: waves up to Wind and Sun, Pip on his paw
        a = SH["button_crane"][0]
        st["arms"] = [list(DANCE_ARM), [1.5 + 0.3 * math.sin((t - a) * 9), 0.2]]
        st["head"][0] = -0.3 * ease(clampu(t, a, a + 0.6)); st["tail"] = 0.4 * math.sin(t * 6)
    return st

# ---------------- the scarf: a chain of short striped segments ----------------
SEG = 0.075; SC_R = 0.06
LA, LB = 0.55, 0.45                                           # the two hanging ends
COL_RX, COL_RZ, COL_Y = 0.37, 0.34, 1.0                       # collar round his neck (body frame)
LC = 2 * math.pi * math.sqrt((COL_RX ** 2 + COL_RZ ** 2) / 2)
LTOT = LA + LC + LB
PHI_CALM = 1.0                                              # the ends hang at the front, on his right-paw side
BODY_C, BODY_R = np.array([0, 0.66, 0.0]), np.array([0.43, 0.51, 0.38])
HEAD_C, HEAD_R = np.array([0, 1.56, 0.06]), np.array([0.53, 0.54, 0.52])
def collar_pt(phi): return np.array([COL_RX * math.sin(phi), COL_Y + 0.025 * math.cos(phi), COL_RZ * math.cos(phi)])
def push_out(p, c, r, m):
    q = (p - c) / (r + m); d = np.linalg.norm(q)
    return c + q / d * (r + m) if d < 1.0 else p
def drape(root, length, wl, w, t, ph):
    """one hanging end in the body frame: steps down (gravity) or downwind (wind), kept out of his body and head"""
    pts = [root]; n = max(2, int(round(length / SEG)))
    g = np.array([0, -1.0, 0]); p = root.copy()
    for k in range(n):
        fl = math.sin(t * 15 + k * 0.7 + ph) * (0.15 + 0.35 * w) * (k / n)
        d = g * (1 - w) + (wl + np.array([0, -0.18, 0])) * w + np.array([0, fl, 0]) * w + np.array([fl * 0.3, 0, fl * 0.2]) * (1 - w)
        d = d / np.linalg.norm(d)
        p = p + d * (length / n)
        p = push_out(push_out(p, BODY_C, BODY_R, 0.07), HEAD_C, HEAD_R, 0.07)
        pts.append(p)
    return pts
def local_wind(R):
    Rinv = np.linalg.inv(R[:3, :3]); v = Rinv @ WIND_DIR; return v / np.linalg.norm(v)
def worn_parts(t, R, w):
    """worn scarf in world space: (tail A from its end up to the root, the collar loop, tail B from the root down)"""
    wl = local_wind(R)
    phi_w = math.atan2(wl[0], wl[2])
    dphi = (phi_w - PHI_CALM + math.pi) % (2 * math.pi) - math.pi
    phi = PHI_CALM + dphi * min(1.0, w * 1.3)
    root = collar_pt(phi)
    ta = drape(collar_pt(phi + 0.12), LA, wl, w, t, 0.0)
    tb = drape(collar_pt(phi - 0.12), LB, wl, w, t, 2.1)
    ring = [collar_pt(phi + 0.12 + k * (2 * math.pi - 0.24) / 30) for k in range(31)]
    W_ = lambda ps: [apply(R, p) for p in ps]
    return W_(ta[::-1]), W_(ring), W_(tb), apply(R, root)
def resample(pts, step=SEG):
    pts = [np.asarray(p, float) for p in pts]
    out = [pts[0]]; acc = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        L = np.linalg.norm(b - a)
        if L < 1e-9: continue
        s = step - acc
        while s <= L:
            out.append(a + (b - a) * (s / L)); s += step
        acc = L - (s - step)
    if np.linalg.norm(out[-1] - pts[-1]) > step * 0.3: out.append(pts[-1])
    return out
def take_len(pts, L):
    """the first L of a polyline"""
    out = [np.asarray(pts[0], float)]
    for a, b in zip(pts[:-1], pts[1:]):
        d = np.linalg.norm(b - a)
        if d >= L: out.append(a + (b - a) * (L / max(d, 1e-9))); return out
        out.append(np.asarray(b, float)); L -= d
    return out
def plen(pts): return sum(np.linalg.norm(np.asarray(b) - np.asarray(a)) for a, b in zip(pts[:-1], pts[1:]))
G1 = np.array([0.45, 0.0, 0.89]); G1 /= np.linalg.norm(G1)       # the gathered scarf runs along the grass this way
G2 = np.array([0.97, 0.0, -0.25]); G2 /= np.linalg.norm(G2)      # the hanging part falls this way when he lets go
def ground_run(foot, d, L):
    n = max(2, int(L / 0.1) + 1)
    return [np.array([foot[0] + d[0] * L * k / (n - 1), 0, foot[2] + d[2] * L * k / (n - 1)]) for k in range(n)]
def on_grass(p): return np.array([p[0], surf(p[0], p[2]) + SC_R * 0.9, p[2]])
def _drape(top, bottom_y, length):
    """points from the bottom (y=bottom_y) up to top: a soft cloth curve that bulges and sways, not a rod"""
    n = max(3, int(length / 0.08) + 1); amp = 0.16 + 0.05 * math.sin(_NOW[0] * 5.5); side = -G1
    out = []
    for k in range(n):
        f = k / (n - 1)                                          # 0 at the bottom, 1 at the paw
        off = amp * math.sin(math.pi * f) * (1 - 0.3 * f) + 0.03 * math.sin(_NOW[0] * 7 + f * 5) * f * (1 - f)
        out.append(np.array([top[0], bottom_y + (top[1] - bottom_y) * f, top[2]]) + side * off)
    return out
def hanging(hand, h):
    """scarf gathered through the paw: a drooping curve from the paw to the grass, then along the grass (G1)"""
    foot = np.array([hand[0], 0, hand[2]]); gy = surf(hand[0], hand[2]) + SC_R * 0.9
    drop = max(hand[1] - gy, 0.01)
    if h <= drop: return _drape(hand, hand[1] - h, h)[:] + []
    run = ground_run(foot, G1, h - drop)[::-1]
    return [on_grass(p) for p in run] + _drape(hand, gy, drop)[1:]
def scarf_points(t, st, mats):
    R, Mh, arms, legs = mats
    if t < T.GRAB:
        ta, ring, tb, root = worn_parts(t, R, wind_w(t))
        return ta + ring[1:] + tb[1:]
    hand = hand_pos(arms, 0)
    if t < T.DROP:
        ta, ring, tb, root = worn_parts(min(t, T.GRAB), fox_mats(tumble(T.GRAB))[0], 0.0)   # worn shape frozen while he pulls
        root = ta[-1]
        dA = np.linalg.norm(hand - root)
        u = ease(clampu(t, T.GRAB + 0.25, T.FREE))
        rem = min((LC + LB) * (1 - u), max(LTOT - dA, 0.0))
        if rem > 1e-3:
            h = LTOT - dA - rem
            far = take_len(ring + tb[1:], rem)
            return hanging(hand, h)[:-1] + [hand, root] + far[1:]
        line_len = min(dA, LTOT) * (1 - ease(clampu(t, T.FREE, T.FREE + 0.35)))
        h = LTOT - line_len
        tail = take_len([hand, root], line_len) if line_len > 1e-3 else []
        return hanging(hand, h)[:-1] + [hand] + tail[1:]
    return rest_points(t)
def _rest_base():
    st = tumble(T.DROP - 1e-3); hand = hand_pos(fox_mats(st)[2], 0)
    gy = surf(hand[0], hand[2]) + SC_R * 0.9; drop = hand[1] - gy
    foot = np.array([hand[0], gy, hand[2]])
    return hand, foot, drop
def rest_points(t):
    """after he lets go: the hanging part swings down onto the grass about its foot, then lies still"""
    hand, foot, drop = _rest_base()
    u = ease(clampu(t, T.DROP, T.DROP + 0.4))
    run = [on_grass(p) for p in ground_run(foot, G1, LTOT - drop)[::-1]]
    ang = u * math.pi / 2; n = max(2, int(drop / 0.08) + 1); up = []
    for k in range(1, n):
        s = drop * k / (n - 1)
        p = foot + np.array([0, math.cos(ang) * s, 0]) + G2 * math.sin(ang) * s
        up.append(p if u < 1 else on_grass(p))
    return run + up
STRIPES = [(0.92, 0.3, 0.33), (0.92, 0.3, 0.33), (1.0, 0.95, 0.86), (1.0, 0.95, 0.86), (0.3, 0.72, 0.74), (1.0, 0.95, 0.86)]
def draw_scarf(draws, t, st, mats):
    pts = resample(scarf_points(t, st, mats))
    for k, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        c = STRIPES[k % len(STRIPES)]
        M = seg_M(a, b, SC_R)
        if M is not None: draws.append((PR["stick"], M, U(mat=0, bump=0.5, tint=c, tintMix=1.0, obj="scarf"), True))
        draws.append((PR["ball"], trans(*b) @ scale(SC_R), U(mat=0, bump=0.5, tint=c, tintMix=1.0, obj="scarf"), True))
    for end in (pts[0], pts[-1]):                                # tassels
        for k in range(3):
            q = end + np.array([0.035 * math.cos(k * 2.1), -0.03, 0.035 * math.sin(k * 2.1)])
            draws.append((PR["ball"], trans(*q) @ scale(0.03), U(mat=0, bump=0.0, tint=(1.0, 0.95, 0.86), tintMix=1.0), False))

def _grab_target():
    st = tumble_base(0.0); st["x"], st["z"] = SPOT; st["yaw"] = -0.05; st["sq"] = 0.0
    R = fox_mats(st)[0]
    ta = worn_parts(T.GRAB, R, 0.0)[0]
    p = ta[0]                                                    # the end of tail A, world
    Rinv = np.linalg.inv(R); return apply(Rinv, p)
GRAB_ARM = solve_arm(_grab_target(), 0)

# ---------------- Pip ----------------
HOVER = np.array([0.95, 1.65, 0.25])
CLING_P = np.array([FLOWER[0] + 0.36, surf(*FLOWER) + 0.88, FLOWER[1]])
def flower_bend(t):
    g = wind_w(t)
    return 0.35 * g * math.sin(t * 9) + 0.25 * g + 0.04 * math.sin(t * 1.4)
def cling_p(t):                                              # Pip's seat on the petals of the swaying flower head (measured: top ~0.89 at r 0.36)
    a = 0.12 * flower_bend(t); v = np.array([0.36, 0.98])
    base = np.array([FLOWER[0], surf(*FLOWER) - 0.01, FLOWER[1]])
    return base + np.array([v[0] * math.cos(-a) - v[1] * math.sin(-a), v[0] * math.sin(-a) + v[1] * math.cos(-a), 0.0])
def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    R, Mh, arms, legs = mats
    face = apply(Mh, (0, 1.5, 0.6))
    to_tumble = math.atan2(st["x"] - POST_PIP[0], st["z"] - POST_PIP[2]) * 0.6
    if n == "hook_sky":
        p = HOVER + np.array([0, 0.05 * math.sin(t * 6), 0])
        ex = {"gentle": True}
        if abs(t - T.WHISTLE_HOOK - 0.2) < 0.45: ex["beak"] = True
        return p, 0.5, True, 0.0, False, ex
    if n == "title_wide":
        a = SH[n][0]; u = clampu(t, a + 0.2, a + 1.3)
        if u < 1:                                                # up, across, down onto the post
            top = np.array([POST_PIP[0], max(HOVER[1], POST_PIP[1]) + 0.3, POST_PIP[2]])
            p = lerp(HOVER, top, ease(min(u * 1.4, 1.0))) if u < 0.7 else lerp(top, POST_PIP, ease((u - 0.7) / 0.3))
            return p, 0.2, True, 0.0, False, {"gentle": True}
        return POST_PIP, to_tumble, False, 0.0, True, {}
    if n in ("sky_faces", "whistle", "snug", "wind_puff"):
        ex = {}
        if abs(t - T.WHISTLE_GO - 0.2) < 0.45: ex = {"beak": True, "point": True}
        return POST_PIP, (to_tumble if n != "whistle" else -1.75), False, 0.0, True, ex
    if n == "hold_tight":
        if t < T.BLOWN:                                          # feathers ruffling, hanging on
            return POST_PIP, to_tumble, False, 0.0, True, {"cling": 0.6 * wind_w(t)}
        u = clampu(t, T.BLOWN, T.CLING)                           # blown backwards, tumbling, onto the flower
        p = lerp(POST_PIP, cling_p(t), ease(u)); p[1] += 0.25 * math.sin(math.pi * u); p[2] += 1.6 * math.sin(math.pi * u)
        return p, lerp(to_tumble, -math.pi / 2, u), True, -2 * math.pi * ease(u), False, {"gentle": True}
    if n in ("spin", "pip_cling"):                               # clinging to the flower stem like a little flag
        w = wind_w(t)
        p = cling_p(t) + np.array([0.01 * math.sin(t * 19) * w, 0.015 * math.sin(t * 13) * w, 0])
        return p, -math.pi / 2 + 0.12 * math.sin(t * 9) * w, False, 0.0, False, \
            {"wings": (1.25 + 0.15 * math.sin(t * 30), 1.25 + 0.15 * math.sin(t * 30 + 1)), "cling": 0.4}
    if n in ("wind_tired", "sun_shine", "scarf_off"):
        return POST_PIP, to_tumble, False, 0.0, True, ({"cheer": True} if n == "scarf_off" and t > T.FREE else {})
    if n == "sunbathe":
        ex = {}
        if abs(t - T.WHISTLE_WIN - 0.2) < 0.45: ex = {"beak": True, "point": True}
        return POST_PIP, (-0.6 if ex else to_tumble), False, 0.0, True, ex
    if n in ("moral", "chorus"):
        return dance_pip(t, st, mats, n, arrive_from=POST_PIP)
    top = paw_seat(arms)
    return top, 0.35, False, 0.0, True, {"cheer": t > SH["button_crane"][0] + 0.5}
def pip_blowing(t):
    return any(abs(t - w_ - 0.2) < 0.45 for w_ in (T.WHISTLE_HOOK, T.WHISTLE_GO, T.WHISTLE_WIN))
def stick_between(p, q, r, tint):
    """a thin stick (mesh axis y, base at origin, length 1) from p to q"""
    d = np.asarray(q, float) - np.asarray(p, float); L = float(np.linalg.norm(d)); d = d / max(L, 1e-6)
    ax = np.cross([0, 1, 0], d); sn = float(np.linalg.norm(ax)); an = math.atan2(sn, d[1])
    if sn < 1e-6: R = np.eye(4)
    else:
        ax = ax / sn; K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
        R = np.eye(4); R[:3, :3] = np.eye(3) + math.sin(an) * K + (1 - math.cos(an)) * (K @ K)
    return trans(*p) @ R @ scale(r / 0.05, L, r / 0.05)
def draw_whistle(draws, t, Mp):
    """a little yellow whistle on a red cord round Pip's neck: lies on his chest, swings up into his beak to blow"""
    bl = 0.0
    for w_ in (T.WHISTLE_HOOK, T.WHISTLE_GO, T.WHISTLE_WIN):
        bl = max(bl, ease(clampu(t, w_ - 0.25, w_ - 0.1)) * (1 - ease(clampu(t, w_ + 0.5, w_ + 0.65))))
    base = lerp((-0.05, 0.14, 0.175), (0.0, 0.30, 0.25), bl)
    M = Mp @ trans(*base) @ roty((1 - bl) * math.pi / 2) @ rotx(math.pi / 2 - 0.15 * (1 - bl)) @ scale(0.42, 0.1, 0.42)
    yel = U(mat=0, bump=0.0, tint=(1.0, 0.82, 0.2), tintMix=1.0)
    draws.append((PR["stick"], M, yel, False))
    tip = apply(M, (0, 1.0, 0))
    draws.append((PR["ball"], Mp @ trans(*base) @ scale(0.026), yel, False))
    neck = np.array([0.0, 0.265, 0.12]); red = U(mat=0, bump=0.0, tint=(0.85, 0.2, 0.2), tintMix=1.0)
    for sx in (-1, 1):                                          # cord: over the shoulders down to the whistle ring
        draws.append((PR["stick"], Mp @ stick_between(neck + np.array([0.075 * sx, 0, -0.03]), base, 0.007, red), red, False))
    for w_ in (T.WHISTLE_HOOK, T.WHISTLE_GO, T.WHISTLE_WIN):
        for k in range(3):
            puff(draws, tip + np.array([0, 0.03, 0.03]), w_ + 0.12 * k, t, n=6, size=0.022, spread=0.5, dur=0.3, tint=(1.0, 1.0, 1.0), axis=(0, 0.2, 0.2))

# ---------------- Wind and Sun: soft clay faces in the sky ----------------
def face_mat(pos, look, s):
    d = np.asarray(look, float) - pos; yaw = math.atan2(d[0], d[2]); pitch = -math.atan2(d[1], math.hypot(d[0], d[2]))
    return trans(*pos) @ roty(yaw) @ rotx(pitch * 0.8) @ scale(s)
def wind_face(t):
    """(look target, puff 0..1, tired 0..1, drift)"""
    n = T.shot_at(t)[1]
    puffing = ease(clampu(t, T.BLOW0 - 0.6, T.BLOW0)) * (1 - ease(clampu(t, T.BLOW1 - 0.2, T.BLOW1 + 0.5)))
    tired = ease(clampu(t, T.BLOW1 - 0.2, T.BLOW1 + 0.5)) * (1 - ease(clampu(t, T.SUN0 + 1.5, T.SUN0 + 2.5)))
    look = np.array([0, 1.2, 0.5])
    if n == "sky_faces": look = lerp(look, SUN_P + np.array([0, 0, 5.0]), 0.6 * math.sin(math.pi * clampu(t, SH[n][0] + 0.2, SH[n][1] - 0.1)))
    return look, puffing, tired
def draw_wind(draws, t):
    look, pf, tired = wind_face(t)
    bob = np.array([0.1 * math.sin(t * 0.9), 0.12 * math.sin(t * 1.3), 0]) + np.array([-0.35, 0.1, -0.3]) * tired
    sq = 1 + 0.06 * pf - 0.05 * tired
    M = face_mat(WIND_P + bob, look, WIND_S) @ scale(sq, 1 / sq, 1)
    if T.shot_at(t)[1] == "sky_faces": M = M @ rotz(0.08 * math.sin(math.pi * clampu(t, SH["sky_faces"][0] + 0.3, SH["sky_faces"][1] - 0.2)))   # a friendly nod
    soft = U(mat=0, bump=0.4, tint=(0.94, 0.96, 1.0), tintMix=1.0)
    draws.append((SC["cloud"], M, soft, False))
    for sx in (-1, 1):                                            # cheeks: swell when he blows
        r = 0.26 + 0.24 * pf
        draws.append((PR["ball"], M @ trans((0.5 + 0.08 * pf) * sx, -0.2, 0.6 + 0.12 * pf) @ scale(r, r * 0.85, r * 0.75), soft, False))
        draws.append((PR["ball"], M @ trans((0.56 + 0.12 * pf) * sx, -0.17, 0.62 + 0.12 * pf + r * 0.72) @ scale(0.14, 0.09, 0.03), U(mat=0, bump=0.0, tint=(1.0, 0.62, 0.72), tintMix=1.0), False))
    bl = 0.25 if tired > 0.5 else blink(t, 0.7, 3.1)
    eyes(draws, M, [(0.32, 0.3, 0.66), (-0.32, 0.3, 0.66)], 0.2, bl)
    if pf > 0.2:                                                  # round blowing mouth
        o = 0.09 + 0.06 * pf + 0.015 * math.sin(t * 20)
        draws.append((PR["mouth"], M @ trans(0, -0.25, 0.78 + 0.1 * pf) @ scale(o, o * 1.1, 0.05), U(mat=2, bump=0.0), False))
    if pf > 0.35:                                                 # a fan of gust streaks pouring out of the mouth
        mouth = apply(M, (0, -0.25, 0.85))
        for k in range(9):
            ph = (t * (2.2 + 0.25 * (k % 3)) + k * 0.37) % 1.0
            side = (k - 4) * 0.07
            d = WIND_DIR + np.array([0, 0.04 * (k - 4), 0.05 * side])
            a = mouth + d * (0.2 + 2.2 * ph) + np.array([0, 0.08 * (k - 4) * ph, 0])
            b = a + d * (0.35 + 0.55 * ph) * pf
            Ms = seg_M(a, b, 0.022 * pf)
            if Ms is not None: draws.append((PR["stick"], Ms, U(mat=0, bump=0.0, tint=(1.0, 1.0, 1.0), tintMix=1.0), False))
    if pf <= 0.2:                                                         # smile (a laugh when tired)
        draws.append((PR["mouth"], M @ trans(0, -0.2, 0.7) @ scale(0.2, 0.05 + 0.06 * tired, 0.05), U(mat=2, bump=0.0), False))
    return M
def draw_wind_streaks(draws, t):
    w = wind_w(t)
    if w < 0.05: return
    for k in range(12):
        sp = 3.5 + (k % 4) * 0.7
        x = -4.5 + ((t * sp + k * 1.37) % 9.0)
        y = 2.9 + (k * 0.53) % 1.6 + 0.1 * math.sin(t * 3 + k)
        z = -0.6 - (k * 0.71) % 1.4
        L = (0.5 + 0.2 * (k % 3)) * w
        a = np.array([x, y, z]); b = a + WIND_DIR * L
        M = seg_M(a, b, 0.018 * w)
        if M is not None: draws.append((PR["stick"], M, U(mat=0, bump=0.0, tint=(1.0, 1.0, 1.0), tintMix=1.0), False))
    for k in range(8):                                            # a few leaves tumbling past, low and behind him
        x = -4.0 + ((t * (2.6 + 0.3 * k) + k * 1.9) % 8.0)
        p = np.array([x, 0.4 + (k * 0.37) % 0.9 + 0.2 * math.sin(t * 4 + k), -1.2 - (k * 0.5) % 1.6])
        draws.append((SC["leaf"], trans(*p) @ rotx(t * 5 + k) @ rotz(t * 3 + k) @ scale(1.6 * min(1, w * 2)), U(mat=0, bump=0.0, tint=[(0.6, 0.8, 0.4), (0.95, 0.75, 0.3)][k % 2], tintMix=1.0), False))
def sun_face(t):
    n = T.shot_at(t)[1]
    look = np.array([0, 1.2, 0.5])
    if n == "sky_faces": look = lerp(look, WIND_P + np.array([0, 0, 5.0]), 0.6 * math.sin(math.pi * clampu(t, SH[n][0] + 0.2, SH[n][1] - 0.1)))
    shine = ease(clampu(t, T.SUN0, T.SUN0 + 1.6))
    return look, shine
def draw_sun(draws, t):
    look, shine = sun_face(t)
    s = SUN_S * (1 + 0.08 * shine)
    M = face_mat(SUN_P + np.array([0.1 * 0 + (2.5 if T.shot_at(t)[1] == "wind_puff" else 0.0), 0.1 * math.sin(t * 1.1 + 1), 0]), look, s)
    if T.shot_at(t)[1] == "sky_faces": M = M @ rotz(-0.08 * math.sin(math.pi * clampu(t, SH["sky_faces"][0] + 0.3, SH["sky_faces"][1] - 0.2)))
    draws.append((SC["sun"], M @ rotz(0.15 * t + 0.6 * shine), U(mat=0, bump=0.3, tint=(1.0, 0.93 + 0.04 * shine, 0.6), tintMix=-1.0), False))
    for sx in (-1, 1):
        draws.append((PR["ball"], M @ trans(0.55 * sx, -0.15, 0.33) @ scale(0.16, 0.1, 0.05), U(mat=0, bump=0.0, tint=(1.0, 0.6, 0.45), tintMix=1.0), False))
    n = T.shot_at(t)[1]
    wink = n == "button_crane" and t > SH["button_crane"][0] + 1.2
    bl = blink(t, 2.0, 3.6)
    eyes(draws, M, [(0.32, 0.22, 0.34)], 0.13, 0.25 if wink else bl)
    eyes(draws, M, [(-0.32, 0.22, 0.34)], 0.13, bl)
    amp = 0.012 + 0.012 * shine                                   # a curved smile: beads on an arc, corners lifted
    for i in range(-4, 5):
        draws.append((PR["ball"], M @ trans(0.065 * i, -0.33 + amp * i * i / 4.0, 0.355) @ scale(0.034, 0.034, 0.03), U(mat=0, bump=0.0, tint=(0.62, 0.12, 0.18), tintMix=1.0), False))
    return M

# ---------------- camera ----------------
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    if name == "hook_sky":                                    # low angle close to Tumble, looking up at the faces (push-in)
        eye = np.array([0.25, 0.75, lerp(4.4, 3.9, e)] if not WIDE else [0.3, 1.0, lerp(4.9, 4.5, e)])
        return eye, np.array([0.15, 3.4 if not WIDE else 2.5, -2.5]), (58.0 if not WIDE else 46.0)
    if name == "title_wide":
        return fit_cam(np.array([0.9, 1.7, -1.0]), -10, 9, 3.4, 2.6 if not WIDE else 2.1, lift=0.05)
    if name == "sky_faces":
        return fit_cam(lerp(WIND_P, SUN_P, 0.5) + np.array([0, 0.1, 0]), 0, -2, 3.5, 1.5 if not WIDE else 2.3, fov=34, lift=0.1)
    if name == "whistle":                                     # macro on Pip at the post, side-on
        return fit_cam(POST_PIP + np.array([0, 0.25, 0]), lerp(-24, -16, e), 8, 0.45, 0.55 if not WIDE else 0.42, fov=34, lift=0.12)
    if name == "snug":
        return fit_cam(np.array([0.05, 1.4, 0]), lerp(-8, -4, e), 4, 0.95, 1.15)
    if name == "wind_puff":
        return fit_cam(WIND_P + np.array([0, 0.05, 0]), lerp(16, 20, e), -3, lerp(1.6, 1.35, e), lerp(1.5, 1.25, e), fov=34, lift=0.0)
    if name == "hold_tight":                                  # low three-quarter, room for Pip's tumble to the flower
        k = ease(clampu(t, T.BLOWN - 0.3, T.CLING))               # pull out to follow Pip's flight to the flower
        return fit_cam(lerp(np.array([0.45, 1.2, 0.0]), np.array([1.6, 1.0, 0.2]), k), -18, -4, lerp(1.5, 2.4, k), lerp(1.35, 2.0, k))
    if name == "spin":                                        # high angle wide
        return fit_cam(np.array([0.6, 0.9, 0.1]), 8, 42, 2.0, 1.7)
    if name == "pip_cling":
        return fit_cam(CLING_P + np.array([0.12 if WIDE else -0.05, 0.1, 0]), lerp(8, 14, e), 8, 0.85, 0.7, fov=34, lift=0.12)
    if name == "wind_tired":
        return fit_cam(lerp(WIND_P, SUN_P, 0.5) + np.array([0, -0.1, 0]), -4, -4, 3.5, 1.7, fov=34, lift=0.08)
    if name == "sun_shine":
        return fit_cam(SUN_P + np.array([-0.1, 0, 0]), lerp(-12, -16, e), -3, lerp(1.8, 1.5, e), lerp(1.8, 1.5, e), fov=34, lift=0.0)
    if name == "scarf_off":
        return fit_cam(np.array([0.35, 1.25, 0.1]), lerp(6, 10, e), 4, 1.4, 1.35)
    if name == "sunbathe":                                    # overhead
        return fit_cam(np.array([-0.3, 0.6, 0.2]), 12, 30, 2.0, 1.7, lift=0.1)
    if name == "moral":
        return fit_cam(np.array([0.3, lerp(1.35, 1.45, e), 0]), lerp(12, 6, e), 5, lerp(1.3, 1.1, e), lerp(1.4, 1.15, e))
    if name == "chorus":
        return fit_cam(np.array([0.3, 1.2, 0]), 6, 6, 1.35, 1.35)
    e = ease(clampu(t, SH["button_crane"][0] + 1.35, SH["button_crane"][1]))   # hold on Tumble and Pip through "Bye-bye!", then crane up to the sky faces
    tgt = lerp(np.array([0.3, 1.25, 0]), lerp(WIND_P, SUN_P, 0.5) + np.array([0, -1.3, 0]), e)
    return fit_cam(tgt, 2, lerp(4, -6, e), lerp(1.4, 3.6, e), lerp(1.4, 3.2, e), lift=lerp(0.15 if not WIDE else 0.1, 0.02, e))

# ---------------- draws ----------------
SKY_SHOTS = ("sky_faces", "wind_puff", "wind_tired", "sun_shine")
TREES = [(-6.5, -8.5, 1.6), (6.8, -8.0, 1.7), (-10.5, -13, 1.9), (10.0, -14, 2.0), (-3.5, -14, 1.8), (-7.5, -2.5, 1.5)]
def backdrop(draws, t):
    g = wind_w(t)
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.8), False))
    n_ = T.shot_at(t)[1]
    for k_, (x, z, s) in enumerate(TREES):
        if n_ in SKY_SHOTS or (k_ == 5 and n_ in ("moral", "chorus")): continue       # keep trees from sitting under faces / on Tumble's head
        draws.append((SC["tree"], trans(x, ground_h(x, z) - 0.05, z) @ roty(x) @ rotz(0.04 * g * math.sin(t * 5 + x)) @ scale(s), U(mat=0, bump=0.7), True))
    draws.append((SC["cottage"], trans(COTTAGE[0], ground_h(*COTTAGE) - 0.05, COTTAGE[1]) @ roty(-0.5), U(mat=0, bump=0.6), False))
    for (x, y, z, sx, sy, sz, c) in [(-12, -1.5, -26, 10, 5.0, 4, (.62, .82, .66)), (11, -1.8, -28, 11, 6.0, 4, (.58, .78, .7)),
                                     (0, -2.8, -32, 15, 6.6, 5, (.66, .8, .78))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    for k, (x, y, z) in enumerate([(-9.0, 12.0, -22), (9.5, 13.5, -24)]):          # small far clouds (no faces)
        draws.append((SC["cloud"], trans(x + 0.1 * t * (1 if k else -1) + 0.8 * g * t * 0.2, y, z) @ scale(1.2), U(mat=0, bump=0.4), False))
    for k, p in enumerate(POSTS):                                                     # garden fence
        gy = surf(*p) - 0.02
        draws.append((PR["stick"], trans(p[0], gy, p[1]) @ scale(POST_R / 0.05, POST_H, POST_R / 0.05), U(mat=0, bump=0.8, tint=(0.82, 0.62, 0.45), tintMix=1.0, obj="fence" if k == 0 else "fence2"), True))
    for a, b in zip(POSTS[:-1], POSTS[1:]):
        for hy in (0.42, 0.72):
            pa = np.array([a[0], surf(*a) + hy, a[1]]); pb = np.array([b[0], surf(*b) + hy, b[1]])
            draws.append((PR["stick"], seg_M(pa, pb, 0.04), U(mat=0, bump=0.8, tint=(0.82, 0.62, 0.45), tintMix=1.0), True))
    fb = flower_bend(t)                                                                      # the big flower bends in the wind
    draws.append((SC["flower"], trans(FLOWER[0], surf(*FLOWER) - 0.01, FLOWER[1]) @ rotz(-0.12 * fb) @ scale(FLOWER_S), U(mat=0, bump=0.0, tint=(1.0, 0.72, 0.82), tintMix=-1.0, obj="flower"), True))

def build_draws(t):
    _NOW[0] = t
    draws, contacts = [], []
    backdrop(draws, t)
    draw_flowers(draws, t, FLOWERS, gust=wind_w(t))
    draw_wind(draws, t); draw_sun(draws, t); draw_wind_streaks(draws, t)
    st = tumble(t); mats = fox_mats(st); R, Mh, arms, legs = mats
    draw_tumble(draws, contacts, t, st, mats)
    draw_scarf(draws, t, st, mats)
    pip = pip_state(t, st, mats)
    Mp = draw_pip(draws, contacts, t, pip, arms)
    draw_whistle(draws, t, Mp)
    return draws, contacts

T.SH_BUTTON = SH["button_crane"][0]
HOOKS.update(build=build_draws, camera=camera, tumble=tumble, sky=sky,
             ground_objs=lambda t: ("pip",) if T.shot_at(t)[1] == "sunbathe" else ("fox", "pip"),
             qa_ignore={("scarf", "fox"), ("fox", "scarf")})          # the scarf is worn round his neck and held in his paw
if __name__ == "__main__":
    main()
