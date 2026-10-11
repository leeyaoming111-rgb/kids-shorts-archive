"""Tumble & Pip, Episode 1: What's the Weather?  Shot-based 3D claymation renderer.
python3 render.py [out.mp4]          -> full video with audio
python3 render.py x 3 10 20          -> stills out/still_XX.png
python3 render.py seg f0 f1 out.mp4  -> silent segment"""
from render_base import *

B = T.BEAT
def ease(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def lerp(a, b, u): return np.asarray(a, float) * (1 - u) + np.asarray(b, float) * u
def ts(k): return T.t(T.seg_start(k))
def win(t, a, b, fi=0.3, fo=0.3):
    return clamp01((t - a) / fi) * clamp01((b - t) / fo)

# ---------------- meshes ----------------
FOXP = {k: Mesh(p["mesh"]) for k, p in D["fox"]["parts"].items() if "mesh" in p}
FOXD = D["fox"]["parts"]
PIPP = {k: Mesh(p["mesh"]) for k, p in D["pip"]["parts"].items() if "mesh" in p}
PIPD = D["pip"]["parts"]
PR = {k: Mesh(m) for k, m in D["props"].items()}
SC = {k: Mesh(m) for k, m in D["scene"].items()}
EYE_W, EYE_P = Mesh(D["eye_w"]), Mesh(D["eye_p"])
MOUTH = json.load(open("out/mouth.json"))

HOME = (0.0, 0.6)
COTTAGE = (-2.6, -3.4, 0.22)
TREE = (2.9, -2.4)
rng = np.random.default_rng(5)
FLOWERS = []
pastel = [(1.0, .72, .82), (1.0, .85, .6), (.78, .72, 1.0), (.7, .86, 1.0), (1.0, 1.0, 1.0), (1.0, .78, .7)]
while len(FLOWERS) < 40:
    x, z = rng.uniform(-6, 6), rng.uniform(-6, 2.5)
    if abs(x) < 1.3 and z > -1.0: continue
    if (x - COTTAGE[0]) ** 2 + (z - COTTAGE[1]) ** 2 < 2.6 ** 2: continue
    if (x - TREE[0]) ** 2 + (z - TREE[1]) ** 2 < 0.8: continue
    FLOWERS.append((x, z, rng.uniform(0, 6.28), pastel[len(FLOWERS) % 6], rng.uniform(1.0, 1.5)))
for k in range(8):                                           # window-box flowers
    FLOWERS.append((COTTAGE[0] - 0.78 + 0.1 * (k - 3.5) + 0.25, COTTAGE[1] + 1.35 + 0.12, k, pastel[k % 6], 0.7))
STONES = [(lerp((-2.25, -1.9), (0.0, 0.1), u), rng.uniform(0, 3), rng.uniform(0.85, 1.1)) for u in np.linspace(0, 1, 6)]
DROPS = [(rng.uniform(-6, 6), rng.uniform(0, 9), rng.uniform(-7, 5), rng.uniform(7, 10)) for _ in range(260)]
LEAVES = [(rng.uniform(0, 16), rng.uniform(0.4, 5.0), rng.uniform(-5, 3), rng.uniform(2.5, 4.5), rng.uniform(0, 6.3),
           [(.62, .82, .45), (.95, .8, .4), (.98, .65, .45), (.7, .88, .5)][i % 4]) for i in range(46)]
CONF = [(rng.uniform(-3, 3), rng.uniform(4.0, 7.5), rng.uniform(-1.5, 2.5), rng.uniform(0, 6.28), rng.uniform(2, 5),
         pastel[i % 6], rng.uniform(1.0, 1.6)) for i in range(120)]

# ---------------- weather ----------------
SKY = [((0.56, 0.78, 0.95), (0.74, 0.87, 0.98), (0.99, 0.91, 0.82)),
       ((0.45, 0.74, 0.98), (0.70, 0.87, 1.00), (1.00, 0.93, 0.78)),
       ((0.66, 0.72, 0.84), (0.78, 0.82, 0.90), (0.92, 0.90, 0.90)),
       ((0.58, 0.76, 0.90), (0.76, 0.86, 0.94), (0.95, 0.93, 0.86)),
       ((0.52, 0.58, 0.72), (0.64, 0.69, 0.80), (0.78, 0.80, 0.86)),
       ((0.50, 0.76, 0.97), (0.74, 0.88, 1.00), (1.00, 0.92, 0.84))]
KEY = [1.0, 1.12, 0.8, 0.95, 0.66, 1.05]
def weather(t):
    w = T.weather_weights(t)
    sky = [sum(w[i] * np.array(SKY[i][j]) for i in range(6)) for j in range(3)]
    key = sum(w[i] * KEY[i] for i in range(6))
    return w, sky, key

# ---------------- Tumble ----------------
def tumble(t):
    beat = t / B
    st = dict(x=HOME[0], z=HOME[1], yaw=0.0, y=0.0, sq=0.015 * math.sin(t * 3.7), roll=0.0,
              head=[0.0, 0.0, 0.0], arms=[[0.15, 0.0], [0.15, 0.0]], legs=[0.0, 0.0], tail=0.25 * math.sin(t * 2.6),
              hat=0.0, hat_y=0.0, umb=0.0, kite=0.0, boots=0.0, vis=True)
    st["head"][1] = 0.06 * math.sin(t * 1.3)
    # ---- intro: slide in from the right, skid, wave ----
    if t < 2.0:
        st["vis"] = False; return st
    if t < 3.3:
        u = (t - 2.0) / 1.3; e = 1 - (1 - u) ** 3
        st["x"] = 5.2 * (1 - e); st["roll"] = -0.28 * (1 - u); st["yaw"] = -0.5 * (1 - u)
        st["arms"] = [[0.9, 0.0], [0.9, 0.0]]; st["tail"] = 0.6
    dts = t - 3.3
    if 0 <= dts < 0.8: st["sq"] -= 0.16 * math.exp(-dts * 6) * math.cos(dts * 10)
    if 3.4 <= t < 5.3:
        ph = (t - 3.4) * 2 * math.pi * 1.6
        st["arms"][0] = [2.35 + 0.35 * math.sin(ph), 0.2]; st["head"][2] = 0.12 * math.sin(ph * 0.5)
    # ---- chorus: waltz sway ----
    if 5.45 <= t < 10.9:
        bb = beat - 12; amp = win(t, 5.45, 10.9, 0.4, 0.4)
        st["roll"] = 0.13 * amp * math.sin(2 * math.pi * bb / 6)
        st["yaw"] = 0.3 * amp * math.sin(2 * math.pi * bb / 6 + 0.6)
        st["y"] = 0.07 * amp * abs(math.sin(math.pi * bb / 3))
        st["arms"] = [[0.6 + 0.25 * math.sin(math.pi * bb / 3), 0.3], [0.6 + 0.25 * math.cos(math.pi * bb / 3), 0.3]]
        st["legs"] = [0.06 * max(0, math.sin(math.pi * bb / 3)), 0.06 * max(0, -math.sin(math.pi * bb / 3))]
        st["head"][2] = 0.1 * amp * math.sin(2 * math.pi * bb / 6)
    # ---- weather segments ----
    for k in range(5):
        a = ts(k); b2 = a + 12 * B
        if not (a <= t < b2): continue
        lt = t - a
        if lt < 6 * B:                                  # question + guessing pause: look up at the sky
            u = ease(lt / 0.5)
            st["head"][0] = -0.45 * u
            st["arms"][1] = [0.55, 1.75] if k == 4 else [0.3, 1.9 * u]   # paw to brow (still holding the umbrella in k=4)
        if k == 1 and 3 * B <= lt:                       # turn around to watch the clouds
            st["yaw"] = math.pi * ease((lt - 3 * B) / (2 * B))
        if lt >= 6 * B:
            v = lt - 6 * B
            if k == 0:
                if t > T.t(T.seg_start(0) + 8.5):
                    st["yaw"] = 2 * math.pi * ease((t - T.t(T.seg_start(0) + 8.5)) / 1.0)
                st["arms"] = [[1.9, 0.2], [1.9, 0.2]] if t > T.t(T.seg_start(0) + 8.5) else [[0.5, 0.2], [0.5, 0.2]]
            if k == 1:
                st["yaw"] = math.pi; st["head"][0] = -0.38
                st["arms"][0] = [2.4, 0.9]; st["arms"][1] = [0.2, 0.0]
                st["head"][1] = 0.2 * math.sin(v * 1.2)
            if k == 2:
                st["arms"][0] = [2.2, 0.5]; st["roll"] = 0.08 * math.sin(v * 3); st["tail"] = 0.9 + 0.3 * math.sin(v * 9)
                st["head"][0] = -0.3; st["x"] = HOME[0] - 0.2
            if k == 3:
                st["arms"][1] = [0.55, 1.75]
                for hb in T.HOPS_RAIN:
                    dh = (t - T.t(hb)) / 0.36
                    if 0 <= dh <= 1: st["y"] += 0.28 * math.sin(math.pi * dh)
                    if 1 < dh < 2.2: st["sq"] -= 0.12 * math.exp(-(dh - 1) * 3) * math.cos((dh - 1) * 7)
                st["legs"] = [0.05, 0.05] if st["y"] > 0.05 else [0, 0]
            if k == 4:
                st["arms"] = [[2.6, 0.3], [2.6, 0.3]]
                for jb in (T.seg_start(4) + 8.5, T.seg_start(4) + 9.75, T.seg_start(4) + 10.9):
                    dh = (t - T.t(jb)) / 0.5
                    if 0 <= dh <= 1: st["y"] += 0.45 * math.sin(math.pi * dh); st["sq"] += 0.05 * math.sin(math.pi * dh)
                st["head"][2] = 0.12 * math.sin(v * 5)
    # ---- props state ----
    t_hat = T.t(T.HAT_DROP); t_blow = ts(2) + 2.4 * B
    if t_hat <= t < t_blow + 4.0:
        u = (t - t_hat) / 0.45
        st["hat"] = 1.0
        st["hat_y"] = 1.6 * (1 - ease(u)) if u < 1 else 0.06 * math.exp(-(u - 1) * 4) * abs(math.sin((u - 1) * 7))
        if t >= t_blow: st["hat_fly"] = (t - t_blow) / 4.0
    if ts(2) + 3 * B <= t < ts(3) + 3 * B: st["kite"] = 1.0
    if t >= T.t(T.UMBRELLA_POP) and t < ts(4) + 5 * B:          # open, then folds shut when the rain stops; leaves at the cut
        u = (t - T.t(T.UMBRELLA_POP)) / 0.35
        st["umb"] = min(1.0, u) * (1 + 0.15 * math.exp(-max(u - 1, 0) * 5) * math.sin(max(u - 1, 0) * 12)) if u > 0 else 0
        tf = ts(4) + 2.5 * B
        if t > tf: st["umb"] = 1 - 0.88 * ease((t - tf) / 0.45)
    tb = T.t(T.seg_start(3) + 8.5)
    if tb <= t: st["boots"] = ease((t - tb) / 0.2)
    # ---- outro: wave goodbye ----
    if t >= T.t(84):
        ph = (t - T.t(84)) * 2 * math.pi * 1.4
        st["arms"][0] = [2.35 + 0.35 * math.sin(ph), 0.2]; st["arms"][1] = [0.3, 0.0]
        st["roll"] = 0.07 * math.sin(ph * 0.5); st["head"][2] = 0.1 * math.sin(ph * 0.5)
    return st

def fox_mats(st):
    gy = ground_h(st["x"], st["z"])
    sq = st["sq"]
    R = trans(st["x"], gy - 0.01 + st["y"] + 0.22 * abs(math.sin(st["roll"])), st["z"]) @ roty(st["yaw"]) @ rotz(st["roll"]) @ scale(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5)
    hp = FOXD["head"]["pivot"]; hd = st["head"]
    Mh = R @ trans(*hp) @ rotx(hd[0]) @ roty(hd[1]) @ rotz(hd[2]) @ trans(*(-np.array(hp)))
    arms = []
    for ai in range(2):
        pv = FOXD[f"arm{ai}"]["pivot"]; sgn = 1 if ai == 0 else -1
        side, fwd = st["arms"][ai]
        arms.append(R @ trans(*pv) @ rotz(sgn * side) @ rotx(-fwd) @ trans(*(-np.array(pv))))
    return R, Mh, arms

def apply(M, p): return (M @ np.array([p[0], p[1], p[2], 1.0]))[:3]
PIP_FOOT = 0.060                                   # Pip's feet sit this far below his origin (measured from the SDF)
def hat_M(Mh, st):
    M = Mh @ trans(0, 1.865 + st["hat_y"], 0.03) @ rotx(-0.1) @ scale(0.37, 0.55, 0.55)
    if st.get("hat_fly", 0) > 0:                    # the wind blows the hat away, spinning
        u = st["hat_fly"]
        M = trans(-14 * u ** 2.2 - 0.6 * u, 9 * u ** 1.3 + 0.25 * math.sin(u * 14), -3 * u) @ M @ roty(-14 * u) @ rotz(-1.2 * min(1, 4 * u))
    return M
def umb_M(R, t): return R @ trans(-0.25, 2.0, 0.25) @ rotz(0.08 * math.sin(t * 2)) @ scale(0.85)
def tree_M(t):
    windy = T.weather_weights(t)[3]
    sway = 0.05 * math.sin(t * 1.1) + windy * (0.12 + 0.06 * math.sin(t * 4.3))
    return trans(TREE[0], ground_h(*TREE) - 0.05, TREE[1]) @ rotz(-sway) @ scale(1.15)
UP = np.array([0, PIP_FOOT, 0])

# ---------------- Pip ----------------
def pip_anchor(t, idx, st, mats):
    R, Mh, arms = mats
    head_top = apply(Mh, (0, 1.85, 0.15)) + UP          # forehead, in front of the ears
    if idx == 0: return np.array([4.5, 5.0, 1.5]), True
    if idx == 1: return head_top, False
    if idx == 2:
        a = (t - 5.6) * 2 * math.pi / 2.7
        return np.array([0.95 * math.sin(a), 2.35 + 0.15 * math.sin(a * 2), HOME[1] + 0.95 * math.cos(a)]), True
    if idx == 3: return (apply(hat_M(Mh, st), (0, 0.295, 0)) + UP + np.array([0, 0.012, 0])) if st["hat"] > 0 else head_top, False
    if idx == 4: return head_top, False
    if idx == 5:
        kp = kite_pos(t); a = t * 1.7
        return kp + np.array([1.15 * math.cos(a), 0.55 * math.sin(a) - 0.2, 0.55]), True
    if idx == 6: return apply(umb_M(R, t), (0, 0.945, 0)) + UP - np.array([0, 0.025, 0]), False
    if idx == 8: return apply(tree_M(t), (0.05, 2.995, 0.0)) + UP, False
    if idx == 7:
        a = (t - ts(4)) * 2 * math.pi / 3.0
        return np.array([1.4 * math.sin(a), 2.8 + 0.3 * math.sin(a * 2), HOME[1] - 0.4 + 0.6 * math.cos(a)]), True
    return head_top, False

PIP_PLAN = [(0.0, 0), (3.7, 1), (5.6, 2), (ts(0) + 9.6 * B, 3), (ts(2) + 2.1 * B, 5), (ts(3) + 7 * B, 6),
            (ts(4) + 2.1 * B, 8), (ts(4) + 6 * B, 7), (T.t(84) - 0.6, 1)]
def pip(t, st, mats):
    cur = 0
    for i, (a, idx) in enumerate(PIP_PLAN):
        if t >= a: cur = i
    a, idx = PIP_PLAN[cur]
    p1, fly1 = pip_anchor(t, idx, st, mats)
    if cur > 0:
        u = (t - a) / 0.8
        if u < 1:
            p0, _ = pip_anchor(t, PIP_PLAN[cur - 1][1], st, mats)
            e = ease(u); p = lerp(p0, p1, e); p[1] += 0.35 * math.sin(math.pi * e)
            return p, True, (p1 - p0)
    return p1, fly1, None

def kite_pos(t):
    return np.array([1.6 + 0.35 * math.sin(t * 1.7), 3.4 + 0.3 * math.sin(t * 2.3), -0.6 + 0.2 * math.sin(t * 1.1)])

# ---------------- camera ----------------
def camera(t):
    i, name, u, lt = T.shot_at(t)
    fov = 40.0
    if name == "crane_in":
        e = ease(lt / 3.2)
        eye, tgt = lerp((0, 8.5, 12.5), (0.3, 1.9, 6.6), e), lerp((0, 6.5, 0), (0, 1.25, 0.4), e)
    elif name == "track_arc":
        a = -0.5 + 1.0 * ease(u)
        eye, tgt = np.array([4.6 * math.sin(a), 1.75, HOME[1] + 4.6 * math.cos(a)]), np.array([0, 1.3, HOME[1]])
    elif name.startswith("tilt"):
        e = ease((lt - 0.9) / 1.1)
        eye, tgt = lerp((0.35, 0.95, 2.95), (0.35, 1.25, 2.75), e), lerp((0, 1.55, HOME[1]), (0, 7.0, -8.0), e)
        fov = 42.0
    elif name == "sunny":
        eye, tgt = lerp((0, 1.55, 5.3), (0, 1.5, 4.8), ease(u)), np.array([0, 1.45, HOME[1]])
    elif name == "cloudy":
        eye, tgt = lerp((1.0, 1.3, 5.3), (0.9, 1.35, 5.0), ease(u)), np.array([-0.6, 3.0, -8.0])
        fov = 46.0
    elif name == "windy":
        eye, tgt = lerp((-1.9, 0.55, 6.2), (-1.7, 0.6, 5.7), ease(u)), np.array([0.7, 2.5, -1.0])
        fov = 46.0
    elif name == "rainy":
        eye, tgt = lerp((0, 2.0, 6.9), (0, 1.95, 4.9), ease(u)), np.array([0, 2.05, HOME[1]])
    elif name == "rainbow":
        eye, tgt = np.array([0, 2.3, 9.8]), np.array([0, 2.8, -2.0])
        fov = 44.0
    else:  # pullback
        e = ease(lt / 5.6)
        eye, tgt = lerp((0, 1.6, 4.4), (0, 4.6, 12.5), e), lerp((0, 1.3, HOME[1]), (0, 2.8, -1.0), e)
    return eye, tgt, fov

# ---------------- light & targets ----------------
LDIR = np.array([-0.55, 0.85, 0.5]); LDIR /= np.linalg.norm(LDIR)
LVIEW = look_at(LDIR * 20 + np.array([0, 0, -1.0]), np.array([0, 0, -1.0]), (0, 1, 0))
LVP = ortho(-9, 9, -9, 9, 1, 45) @ LVIEW
shadow_tex = ctx.depth_texture((2048, 2048)); shadow_tex.compare_func = "<="
shadow_tex.repeat_x = shadow_tex.repeat_y = False
shadow_fbo = ctx.framebuffer(depth_attachment=shadow_tex)
SS = 4
msaa_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4, samples=SS)],
                           depth_attachment=ctx.depth_renderbuffer((W, H), samples=SS))
res_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4)])

def blink(tsec, off=0.0, period=3.3):
    ph = (tsec + off) % period
    return 1.0 - 0.92 * math.exp(-((ph - 0.1) / 0.06) ** 2)

def eyes(draws, Mh, centers, er, bl, U):
    for c in centers:
        draws.append((EYE_W, Mh @ trans(*c) @ scale(er, er * bl, er * 0.7), U(mat=2, bump=0.0), False))
        if bl > 0.3:
            pc = np.array(c) + np.array([-np.sign(c[0]) * er * 0.08, -er * 0.05, er * 0.6])
            draws.append((EYE_P, Mh @ trans(*pc) @ scale(er * 0.58, er * 0.66 * bl, er * 0.45), U(mat=2, bump=0.0), False))
            hc = pc + np.array([er * 0.18, er * 0.28, er * 0.4])
            draws.append((EYE_W, Mh @ trans(*hc) @ scale(er * 0.16 * bl), U(mat=3, bump=0.0), False))

def build_draws(t):
    beat = t / B
    U = lambda **k: k
    draws = []
    w, sky, key = weather(t)
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.8), False))
    cx, cz, cy = COTTAGE
    draws.append((SC["cottage"], trans(cx, ground_h(cx, cz) - 0.05, cz) @ roty(cy), U(mat=0, bump=0.6), True))
    windy = w[3]
    sway = 0.05 * math.sin(t * 1.1) + windy * (0.12 + 0.06 * math.sin(t * 4.3))
    draws.append((SC["tree"], tree_M(t), U(mat=0, bump=0.8, obj="tree"), True))
    for (x, z, s) in [(-6.5, -8.5, 1.5), (6.2, -9.0, 1.7), (-9.5, -12, 1.8), (9.0, -13, 1.9), (2.0, -14, 1.6), (-3.5, -15, 1.7)]:
        draws.append((SC["tree"], trans(x, ground_h(x, z) - 0.05, z) @ roty(x) @ rotz(-sway * 0.7) @ scale(s), U(mat=0, bump=0.7), True))
    for (x, y, z, sx, sy, sz, c) in [(-11, -1.5, -24, 10, 5.0, 4, (.62, .82, .66)), (10, -1.8, -26, 11, 6.0, 4, (.58, .78, .7)),
                                     (0, -2.8, -30, 15, 6.6, 5, (.66, .8, .78))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    for fi, (x, z, r, c, s) in enumerate(FLOWERS):
        wob = 0.06 * math.sin(t * 1.6 + fi) + windy * 0.3 * math.sin(t * 6 + fi)
        draws.append((SC["flower"], trans(x, ground_h(x, z) - 0.01, z) @ roty(r) @ rotz(wob) @ scale(s), U(mat=0, bump=0.0, tint=c, tintMix=-1.0), False))
    for (p, r, s) in STONES:
        draws.append((SC["stone"], trans(p[0], ground_h(p[0], p[1]) + 0.01, p[1]) @ roty(r) @ scale(s), U(mat=0, bump=0.8), False))
    # sky objects
    sun_s = w[1] + 0.35 * w[2] + 0.8 * w[3] + w[5]
    sx = 2.2 + 11 * (1 - ease(sun_s))
    draws.append((SC["sun"], trans(sx, 9.8, -14) @ rotz(t * 0.2) @ scale(1.25), U(mat=0, bump=0.4), False))
    grey = w[4]
    ctint = tuple(lerp((1.0, 1.0, 1.0), (0.72, 0.75, 0.86), grey))
    base_clouds = [(-4.5, 11.0, -16, 1.4), (5.5, 13.5, -20, 1.6), (-1.0, 15.5, -24, 1.5)]
    for k, (x, y, z, s) in enumerate(base_clouds):
        dx = 0.08 * t * (1 if k % 2 else -1) + windy * ((t * 2.0 + k * 5) % 22 - 11)
        draws.append((SC["cloud"], trans(x + dx, y + 0.15 * math.sin(t * 0.5 + k), z) @ scale(s), U(mat=0, bump=0.4, tint=ctint, tintMix=-1.0), False))
    big = w[2] + w[4] + 0.4 * w[3]
    for k, (x, y, z, s) in enumerate([(1.5, 9.4, -13, 1.9), (3.8, 10.6, -15, 1.6), (-1.6, 8.6, -12.5, 1.7), (-4.2, 10.2, -15, 1.8)]):
        off = (1 - ease(big)) * (16 + 3 * k) * (1 if k % 2 == 0 else -1)
        if abs(off) > 15.5: continue
        drift = windy * ((t * 2.2 + k * 4) % 8 - 4)
        draws.append((SC["cloud"], trans(x + off + drift + 0.1 * math.sin(t * 0.6 + k), y, z) @ scale(s), U(mat=0, bump=0.4, tint=ctint, tintMix=-1.0), False))
    if w[5] > 0.01:
        g = ease(w[5])
        draws.append((SC["rainbow"], trans(0.3, -0.6, -9.5) @ scale(1.35 * (0.3 + 0.7 * g), 1.35 * g, 1.35), U(mat=0, bump=0.15), False))
    # puddle
    pud = max(ease(clamp01(w[4] * 1.4)), 0.7 * w[5])
    if pud > 0.02:
        draws.append((SC["puddle"], trans(HOME[0], ground_h(*HOME) + 0.012, HOME[1] + 0.1) @ scale(0.95 * pud), U(mat=2, bump=0.0), False))
    # rain
    if w[4] > 0.02:
        nd = int(len(DROPS) * w[4])
        for (x, y0, z, sp) in DROPS[:nd]:
            y = (y0 - sp * t) % 9.0 - 0.3
            draws.append((PR["ball"], trans(x, y, z) @ scale(0.009, 0.09, 0.009), U(mat=3, bump=0.0, tint=(0.82, 0.9, 1.0), tintMix=1.0), False))
    # wind leaves
    if windy > 0.02:
        nl = int(len(LEAVES) * windy); ceye = camera(t)[0]
        for (x0, y0, z, sp, ph, c) in LEAVES[:nl]:
            x = (x0 + sp * t) % 16 - 8
            if np.linalg.norm(np.array([x, y0, z]) - ceye) < 1.6: continue      # never through the lens
            draws.append((SC["leaf"], trans(x, y0 + 0.4 * math.sin(t * 3 + ph), z) @ roty(t * 4 + ph) @ rotx(t * 3 + ph) @ scale(1.4),
                          U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    # ---- Tumble ----
    st = tumble(t)
    mats = fox_mats(st)
    contacts = []
    if st["vis"]:
        R, Mh, arms = mats
        u0 = U(mat=0, bump=1.0, seed=2.0, obj="fox")
        draws.append((FOXP["body"], R, u0, True))
        for li in range(2):
            pv = FOXD[f"leg{li}"]["pivot"]
            Ml = R @ trans(0, st["legs"][li], 0)
            draws.append((FOXP[f"leg{li}"], Ml, U(mat=0, bump=1.0, seed=2.0, tint=(1.0, 0.78, 0.25), tintMix=0.9 * st["boots"], obj="fox"), True))
        for ai in range(2):
            draws.append((FOXP[f"arm{ai}"], arms[ai], u0, True))
        draws.append((FOXP["head"], Mh, u0, True))
        tp = FOXD["tail"]["pivot"]
        draws.append((FOXP["tail"], R @ trans(*tp) @ roty(st["tail"] * 0.5) @ trans(*(-np.array(tp))), u0, True))
        eyes(draws, Mh, FOXD["eyes"]["centers"], FOXD["eyes"]["r"], blink(t), U)
        fr = min(int(t * FPS), len(MOUTH) - 1)
        mo = MOUTH[fr] if t > 5.0 or 2.1 < t < 4.8 else 0.0
        if mo > 0.06:
            mc = FOXD["mouth"]["c"]
            draws.append((PR["mouth"], Mh @ trans(*mc) @ scale(0.075, 0.065 * mo, 0.03), U(mat=0, bump=0.0), False))
        contacts.append((st["x"], st["z"], 0.75, max(0.0, 1 - st["y"] * 1.5)))
        if st["hat"] > 0:
            draws.append((PR["hat"], hat_M(Mh, st), U(mat=0, bump=0.7, obj="hat"), True))
        if st["umb"] > 0:
            Mu = umb_M(R, t)
            draws.append((PR["umbrella"], Mu @ scale(st["umb"], 1, st["umb"]), U(mat=0, bump=0.5, obj="umb"), True))
            hand = apply(arms[1], FOXD["arm1"]["hand"]); hb_ = apply(Mu, (0, -0.2, 0))
            dv = hb_ - hand; Ld = np.linalg.norm(dv)
            if Ld > 0.02:
                draws.append((PR["stick"], trans(*hand) @ align_up(dv / Ld) @ scale(0.6, Ld, 0.6), U(mat=0, bump=0.0, tint=(0.6, 0.42, 0.31), tintMix=1.0, obj="pole"), False))
        if st["kite"] > 0:
            hand = apply(arms[0], FOXD["arm0"]["hand"]); kp = kite_pos(t)
            dvec = kp - hand; L = np.linalg.norm(dvec)
            draws.append((PR["stick"], trans(*hand) @ align_up(dvec / L) @ scale(0.12, L, 0.12), U(mat=3, bump=0.0, tint=(0.95, 0.95, 0.95), tintMix=1.0), False))
            draws.append((PR["kite"], trans(*kp) @ roty(-0.3) @ rotz(0.25 * math.sin(t * 2.5)) @ scale(1.2), U(mat=0, bump=0.4, obj="kite"), True))
            for j in range(4):                       # tail bows
                tp_ = kp + np.array([-0.12 * j - 0.1 * math.sin(t * 4 + j), -0.75 - 0.32 * j, 0])
                draws.append((PR["ball"], trans(*tp_) @ scale(0.07, 0.05, 0.03), U(mat=0, bump=0.0, tint=[(1, .55, .65), (.5, .85, .8)][j % 2], tintMix=1.0), False))
        # splash droplets
        for hb in T.HOPS_RAIN:
            dts_ = t - T.t(hb) - 0.36
            if 0 <= dts_ < 0.45:
                for k in range(9):
                    a = k * 2 * math.pi / 9
                    r = 0.3 + 1.5 * dts_
                    y = ground_h(*HOME) + 0.05 + 2.2 * dts_ - 5 * dts_ ** 2
                    draws.append((PR["ball"], trans(HOME[0] + r * math.cos(a), max(y, 0.02), HOME[1] + 0.1 + r * 0.7 * math.sin(a)) @ scale(0.045),
                                  U(mat=2, bump=0.0, tint=(0.75, 0.86, 1.0), tintMix=1.0), False))
    # ---- Pip ----
    if t >= 3.0:
        p, flying, vel = pip(t, st, mats)
        yaw = 0.0
        if vel is not None and np.linalg.norm(vel[[0, 2]]) > 1e-3: yaw = math.atan2(vel[0], vel[2])
        elif flying: yaw = math.atan2(p[0] - HOME[0], p[2] - HOME[1]) + math.pi / 2
        else: yaw = st["yaw"] * 0.7
        Mp = trans(*p) @ roty(yaw) @ scale(1.1)
        up = U(mat=0, bump=0.6, seed=7.0, obj="pip")
        draws.append((PIPP["body"], Mp, dict(up, perch=not flying), True))
        flap = (0.9 * math.sin(t * 28)) if flying else 0.04 + 0.04 * math.sin(t * 3)
        for wi in range(2):
            pv = PIPD[f"wing{wi}"]["pivot"]; sgn = 1 if wi == 0 else -1
            draws.append((PIPP[f"wing{wi}"], Mp @ trans(*pv) @ rotz(sgn * flap) @ trans(*(-np.array(pv))), up, True))
        eyes(draws, Mp, PIPD["eyes"]["centers"], PIPD["eyes"]["r"], blink(t, 1.3, 2.7), U)
    # confetti for the rainbow cheer
    if ts(4) + 8.5 * B <= t < ts(4) + 12 * B + 0.5:
        dtc = t - (ts(4) + 8.5 * B)
        for (x, y0, z, r0, spin, c, sp) in CONF:
            y = y0 - sp * dtc
            if y < 0.03: continue
            draws.append((PR["ball"], trans(x + 0.2 * math.sin(dtc * 2 + r0), y, z) @ roty(r0 + dtc * spin) @ rotx(r0) @ scale(0.06, 0.012, 0.045),
                          U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    return draws, contacts, sky, key

def render_frame(t):
    draws, contacts, sky, key = build_draws(t)
    eye, tgt, fov = camera(t)
    VPm = perspective(fov, W / H, 0.2, 90.0) @ look_at(eye, tgt)
    shadow_fbo.use(); shadow_fbo.clear(depth=1.0)
    sprog["LVP"].value = gl(LVP)
    ctx.disable(moderngl.CULL_FACE)
    for (mesh, M, u, cast) in draws:
        if cast: sprog["M"].value = gl(M); mesh.svao.render()
    msaa_fbo.use(); msaa_fbo.clear(0, 0, 0, 1, depth=1.0)
    ctx.disable(moderngl.DEPTH_TEST)
    skyprog["cTop"].value = tuple(sky[0]); skyprog["cMid"].value = tuple(sky[1]); skyprog["cHor"].value = tuple(sky[2])
    sky_vao.render()
    ctx.enable(moderngl.DEPTH_TEST)
    shadow_tex.use(0); prog["shadowMap"].value = 0
    prog["VP"].value = gl(VPm); prog["LVP"].value = gl(LVP); prog["camPos"].value = tuple(eye)
    cvals = [tuple(c) for c in contacts] + [(0, 0, 1, 0)] * (8 - len(contacts))
    prog["contact"].value = cvals[:8]; prog["nContact"].value = len(contacts)
    prog["fade"].value = 1.0; prog["keyI"].value = float(key)
    for (mesh, M, u, cast) in draws:
        prog["M"].value = gl(M); prog["NM"].value = nmat(M)
        prog["mat"].value = u.get("mat", 0); prog["bump"].value = u.get("bump", 1.0)
        prog["tint"].value = tuple(u.get("tint", (1, 1, 1))); prog["tintMix"].value = u.get("tintMix", 0.0)
        prog["seed"].value = u.get("seed", 0.0)
        mesh.vao.render()
    ctx.copy_framebuffer(res_fbo, msaa_fbo)
    img = np.frombuffer(res_fbo.read(components=4), np.uint8).reshape(H, W, 4)[::-1].copy()
    img[..., 3] = 255
    return img

# ---------------- 2D overlay ----------------
WORDS = json.load(open("out/word_times.json"))
LINES = {}
for w_ in WORDS: LINES.setdefault(w_["line"], []).append(w_)
LINE_LIST = sorted(LINES.values(), key=lambda ws: ws[0]["t0"])
tf = skia.Typeface.MakeFromFile("assets/Fredoka.ttf")
def wght(v):
    try:
        arg = skia.FontArguments(); arg.setVariationDesignPosition(skia.FontArguments.VariationPosition(
            skia.FontArguments.VariationPosition.Coordinates([skia.FontArguments.VariationPosition.Coordinate(0x77676874, v)])))
        return tf.makeClone(arg)
    except Exception:
        return tf
TF6 = wght(620); TF7 = wght(700)
FONT = skia.Font(TF7, 70); TFONT = skia.Font(TF7, 138); SFONT = skia.Font(TF6, 64); WFONT = skia.Font(TF7, 172); EFONT = skia.Font(TF6, 44)
grain = np.random.default_rng(1).integers(0, 255, (H, W), dtype=np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
vig = (1 - 0.2 * np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.25, 0, 1)).astype(np.float32)
PLUMC = (74, 43, 69)
def hexrgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
WORD_Y = [1555, 270, 270, 1555, 270]      # sunny/rainy shots keep the top clear for the hat, umbrella and Pip
RBC = [hexrgb(c) for c in ("#FF4D5E", "#FF9A2E", "#FFC21F", "#30B85C", "#3D8BFF", "#9B5CF0", "#FF4D9E")]

def current_line(t):
    for li, ws in enumerate(LINE_LIST):
        start = ws[0]["t0"] - 0.25
        nxt = LINE_LIST[li + 1][0]["t0"] - 0.25 if li + 1 < len(LINE_LIST) else 1e9
        end = min(ws[-1]["t1"] + 0.5, nxt)
        if start <= t < end: return ws, start, end
    return None, 0, 0

def outlined(cv, text, x, y, font, rgb, a, sw=16):
    st = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=sw, Color=skia.Color(*PLUMC, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
    fp = skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(255 * a)))
    cv.drawString(text, x, y, font, st); cv.drawString(text, x, y, font, fp)

def overlay(img, t):
    surf = skia.Surface(img); cv = surf.getCanvas()
    # title card
    if t < 3.7:
        a = clamp01(t / 0.4) * clamp01((3.7 - t) / 0.4)
        ttl = T.TITLE; x = (W - TFONT.measureText(ttl)) / 2; y0 = 470 - 10 * math.sin(t * 3)
        cols = [(255, 160, 100), (250, 190, 60), (110, 175, 235), (246, 120, 170), (160, 130, 230)]
        for k, ch in enumerate(ttl):
            outlined(cv, ch, x, y0 + 8 * math.sin(t * 5 + k * 0.6), TFONT, cols[k % 5], a, 22); x += TFONT.measureText(ch)
        sub = T.SUBTITLE; outlined(cv, sub, (W - SFONT.measureText(sub)) / 2, 580, SFONT, (255, 255, 255), a, 14)
        ep = "Episode 1"; ew = EFONT.measureText(ep)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - ew) / 2 - 26, 618, ew + 52, 64), 32, 32)
        cv.drawRRect(rr, skia.Paint(AntiAlias=True, Color=skia.Color(255, 140, 120, int(235 * a))))
        cv.drawString(ep, (W - ew) / 2, 664, EFONT, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(255 * a))))
    # weather word (answer + action shots)
    for k in range(5):
        a0 = T.t(T.seg_start(k) + 5.5) - 0.05; a1 = ts(k) + 12 * B - 0.2
        if a0 <= t < a1:
            a = clamp01((t - a0) / 0.2) * clamp01((a1 - t) / 0.3)
            pop = 1 + 0.18 * math.exp(-(t - a0) * 6) * math.sin((t - a0) * 14)
            word = T.WORD[k]; font = skia.Font(TF7, 160 * pop)
            x = (W - font.measureText(word)) / 2; y = WORD_Y[k]
            for j, ch in enumerate(word):
                col = RBC[j % 7] if T.WORD_COL[k] is None else hexrgb(T.WORD_COL[k])
                outlined(cv, ch, x, y + 8 * math.sin(t * 4 + j * 0.7), font, col, a, 24); x += font.measureText(ch)
    # lyric captions in a soft pill near the bottom
    ws, start, end = current_line(t)
    if ws:
        a = clamp01((t - start) / 0.15) * clamp01((end - t) / 0.15)
        space = FONT.measureText(" ")
        rows, cur, wsum = [], [], 0
        for w_ in ws:
            wl = FONT.measureText(w_["w"])
            if cur and wsum + space + wl > 880: rows.append(cur); cur, wsum = [], 0
            wsum += (space if cur else 0) + wl; cur.append((w_, wl))
        if cur: rows.append(cur)
        y = 1665 - 44 * (len(rows) - 1)
        maxw = max(sum(wl for _, wl in r) + space * (len(r) - 1) for r in rows)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - maxw) / 2 - 40, y - 78, maxw + 80, 88 * len(rows) + 34), 46, 46)
        cv.drawRRect(rr, skia.Paint(AntiAlias=True, Color=skia.Color(255, 250, 240, int(205 * a))))
        for row in rows:
            tw = sum(wl for _, wl in row) + space * (len(row) - 1); x = (W - tw) / 2
            for (w_, wl) in row:
                on = w_["t0"] - 0.03 <= t < max(w_["t1"], w_["t0"] + 0.25)
                col = (240, 110, 60) if on else PLUMC
                p = skia.Paint(AntiAlias=True, Color=skia.Color(*col, int(255 * a)))
                ps = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.5, Color=skia.Color(*col, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
                cv.drawString(w_["w"], x, y - (5 if on else 0), FONT, ps)
                cv.drawString(w_["w"], x, y - (5 if on else 0), FONT, p)
                x += wl + space
            y += 88
    out = img[..., :3].astype(np.float32) * vig[..., None]
    out += (grain[..., None].astype(np.float32) - 127) * (8 / 255.0)
    return np.clip(out, 0, 255).astype(np.uint8)

# hat sits on the head: only brim points outside the crown footprint may not touch the head (that is ear clipping)
# designed appearances: the umbrella grows open from nothing with a pop sound (cartoon magic, intended)
QA_EXPECTED_POPS = [("umb", T.t(T.UMBRELLA_POP)), ("pole", T.t(T.UMBRELLA_POP))]
QA_MASKS = {("hat", "fox"): lambda P: (P[:, 0] ** 2 + P[:, 2] ** 2) > 0.33 ** 2}
def qa(fps=15, out="out/qa_report.json"):
    import qa_geom
    meshes = {}
    def walk(o):
        if isinstance(o, dict):
            if "v" in o and "f" in o and "name" in o: meshes[o["name"]] = o; return
            for v in o.values(): walk(v)
    walk(D)
    bank = qa_geom.Bank("out/sdf.pkl", meshes)
    issues = []
    ignore = {("pole", "fox:fox/parts/arm1/mesh"), ("fox", "pole:props/stick"), ("pole", "umb:props/umbrella"), ("umb", "pole:props/stick"),
              ("fox", "hat:props/hat")}          # head inside the worn hat is hidden by the hat
    for fi in range(int(T.DURATION * fps)):
        t = fi / fps
        draws, _, _, _ = build_draws(t)
        items = [(u["obj"], m.name, M, u.get("perch", False)) for (m, M, u, c) in draws if u.get("obj") and m.name in bank.g]
        eye, tgt, fov = camera(t); VPm = perspective(fov, W / H, 0.2, 90.0) @ look_at(eye, tgt)
        exist, onscr = set(), {}
        for (m, M, u, c) in draws:
            if not (u.get("obj") and m.name in bank.g): continue
            o = u["obj"]; exist.add(o)
            cc, rr = bank.v[m.name + ":bs"]; p = VPm @ M @ np.r_[cc, 1]
            onscr[o] = onscr.get(o, False) or (p[3] > 0 and abs(p[0] / p[3]) < 0.95 and abs(p[1] / p[3]) < 0.95)
        if fi > 0:
            cut = any(abs(t - a) < 1.5 / fps for (a, b, n) in T.SHOTS)
            for o in (exist ^ prev_exist):          # an object starts or stops being drawn while in view, away from a cut
                seen = onscr.get(o, False) or prev_on.get(o, False)
                expected = any(o == eo and abs(t - et) < 2.0 / fps for eo, et in QA_EXPECTED_POPS)
                if seen and not cut and not expected:
                    issues.append(dict(t=round(t, 3), kind="pop_" + ("in" if o in exist else "out"), a=o, depth=0))
        prev_exist, prev_on = exist, onscr
        for e in qa_geom.check_frame(t, items, bank, ground=ground_h, masks=QA_MASKS, ground_objs=("fox", "pip"), float_tol=0.02):
            if (e["a"].split(":")[0], e.get("b", "")) in ignore or (e.get("b", "").split(":")[0], e["a"]) in ignore: continue
            issues.append(e)
    summ = qa_geom.summarize(issues, fps)
    json.dump(summ, open(out, "w"), indent=1)
    for s_ in summ: print(s_)
    print("issues:", len(summ))
    return summ

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "qa":
        qa(); sys.exit()
    if len(sys.argv) > 1 and sys.argv[1] == "x":
        for s in sys.argv[2:]:
            t0 = time.time(); fr = overlay(render_frame(float(s)), float(s))
            skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/still_{float(s):05.2f}.png")
            print(s, round(time.time() - t0, 2), "s", flush=True)
        sys.exit()
    nfr = int(T.DURATION * FPS)
    if len(sys.argv) > 1 and sys.argv[1] == "seg":
        f0, f1, outp, audio = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], []
    else:
        outp = sys.argv[1] if len(sys.argv) > 1 else "out/tumble_pip_ep1.mp4"
        f0, f1 = 0, int(sys.argv[2]) if len(sys.argv) > 2 else nfr
        audio = ["-i", "out/audio.wav", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + \
          audio[:2] + ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"] + audio[2:] + [outp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(f0, min(f1, nfr)):
        tsec = fi / FPS
        p.stdin.write(overlay(render_frame(tsec), tsec).tobytes())
        if fi % 90 == 0: print(f"frame {fi}/{min(f1, nfr)}  {time.time() - t0:.0f}s", flush=True)
    p.stdin.close(); p.wait()
    n = min(f1, nfr) - f0
    print(f"done: {n} frames in {time.time() - t0:.0f}s ({(time.time() - t0) / max(n, 1):.2f} s/frame) -> {outp}", flush=True)
