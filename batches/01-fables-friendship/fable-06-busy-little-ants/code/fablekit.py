"""fablekit: shared renderer for Batch 01 (Tumble & Pip, Fables About Friendship).

Each fable's render.py does `from fablekit import *`, then defines its world, tumble(t), pip_state(t, st, mats),
camera(t), extra_draws(t, st, mats, pip, draws, contacts) and calls main(). The kit holds everything that is the same
in every fable: aspect handling (9:16 Short / 16:9 episode), the clay renderer, Tumble and Pip drawing, the series
dance (moral pose, chorus sway, paw-to-wing high-five), aspect-fitted cameras, captions, the title and moral cards,
geometry QA and reviewer contact sheets. Lessons from Fable 1's six review rounds are built in (see comments).

Copy this file into each fable's code/ folder (tools: ../common/sync_kit.sh) so the Mac helper finds it next to
render.py. Command line:
  python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | seg f0 f1 out.mp4 | sheet | qa"""
import os, sys
if "--wide" in sys.argv: os.environ["ASPECT"] = "wide"; sys.argv.remove("--wide")
PREVIEW = "--preview" in sys.argv
if PREVIEW: sys.argv.remove("--preview")
import timeline as T
if PREVIEW:
    T.W, T.H = T.W // 2, T.H // 2
from render_base import *
import re
WIDE = T.ASPECT == "wide"
K = min(W, H) / 1080.0                      # overlay scale (1.0 at full size, 0.5 in preview)

def lerp(a, b, u): return np.asarray(a, float) * (1 - u) + np.asarray(b, float) * u
def clampu(t, a, b): return min(max((t - a) / max(b - a, 1e-6), 0.0), 1.0)
def apply(M, p): return (M @ np.array([p[0], p[1], p[2], 1.0]))[:3]
def surf(x, z): return ground_h(x, z)
SH = {n: (a, b) for a, b, n in T.SHOTS}
BEAT = 60.0 / T.BPM
U = lambda **k: k

FOXP = {k: Mesh(p["mesh"]) for k, p in D["fox"]["parts"].items() if "mesh" in p}
FOXD = D["fox"]["parts"]
PIPP = {k: Mesh(p["mesh"]) for k, p in D["pip"]["parts"].items() if "mesh" in p}
PIPD = D["pip"]["parts"]
PR = {k: Mesh(m) for k, m in D["props"].items()}
SC = {k: Mesh(m) for k, m in D["scene"].items()}
E2 = {k: Mesh(m) for k, m in D["ep2"].items()}
EYE_W, EYE_P = Mesh(D["eye_w"]), Mesh(D["eye_p"])
SKY = ((0.46, 0.72, 0.97), (0.70, 0.86, 1.0), (1.0, 0.93, 0.86))

def make_flowers(avoid, n=80, seed=21):
    """avoid: list of (x, z, r2) circles and ('band', zmin, zmax) / ('box', x0, x1, z0, z1) keep-outs"""
    rng = np.random.default_rng(seed); out = []
    pastel = [(1.0, .72, .82), (1.0, .85, .6), (.78, .72, 1.0), (.7, .86, 1.0), (1.0, 1.0, 1.0), (1.0, .78, .7)]
    while len(out) < n:
        x, z = rng.uniform(-8, 8), rng.uniform(-9, 3.5); bad = False
        for a in avoid:
            if a[0] == "band": bad |= a[1] < z < a[2]
            elif a[0] == "box": bad |= a[1] < x < a[2] and a[3] < z < a[4]
            else: bad |= (x - a[0]) ** 2 + (z - a[1]) ** 2 < a[2]
        if -6.6 < z < -4.4 or bad: continue
        out.append((x, z, rng.uniform(0, 6.28), pastel[len(out) % 6], rng.uniform(0.9, 1.4)))
    return out

# ---------------- mouths from word times (sung lines + spoken gags) ----------------
def mouth_track(who):
    n = int(T.DURATION * FPS) + 2; m = np.zeros(n)
    for L in T.LINES:
        if L["who"] not in (who, "both"): continue
        for w in L["words"]:
            a, b = int(w["t0"] * FPS), int(max(w["t1"], w["t0"] + 0.18) * FPS)
            for f in range(a, min(b + 1, n)):
                m[f] = max(m[f], math.sin(math.pi * (f - a + 0.5) / (b - a + 1)) * 0.95)
    for s in T.SPOKEN:
        if s["who"] not in (who, "both"): continue
        a, b = int(s["t0"] * FPS), int((s["t0"] + 0.75) * FPS)
        for f in range(a, min(b + 1, n)): m[f] = max(m[f], 0.6 + 0.35 * math.sin((f - a) * 0.9))
    return m
MOUTH = {}
for w_ in ("tumble", "pip"):
    p_ = f"out/mouth_{w_}.json"
    MOUTH[w_] = json.load(open(p_)) if (T.ALIGNED and os.path.exists(p_)) else mouth_track(w_).tolist()
def mouth_at(who, t): return MOUTH[who][min(int(t * FPS), len(MOUTH[who]) - 1)]

# ---------------- Tumble ----------------
def tumble_base(t):
    return dict(x=0.0, z=0.0, yaw=-0.05, y=0.0, sq=0.015 * math.sin(t * 3.7), roll=0.0, lie=0.0,
                head=[0.0, 0.05 * math.sin(t * 1.3), 0.0], arms=[[0.15, 0.0], [0.15, 0.0]], legs=[0.0, 0.0],
                tail=0.25 * math.sin(t * 2.6), eyes_closed=False)
def walk_to(st, t, p0, p1, a, b, rate=2.2):
    """walk along a straight line between times a and b; sets position, yaw, bob and leg swing"""
    u = clampu(t, a, b); st["x"], st["z"] = lerp(p0, p1, ease(u))
    if 0 < u < 1:
        ph = (t - a) * 2 * math.pi * rate
        st["y"] += 0.05 * abs(math.sin(ph)); st["legs"] = [0.08 * max(0, math.sin(ph)), 0.08 * max(0, -math.sin(ph))]
        st["yaw"] = math.atan2(p1[0] - p0[0], p1[1] - p0[1])
    return u
FOX_SIDE_LIFT = 0.6                     # lying on his side: lowest point of the rotated model sits on the ground
FOX_SEAT = float(D["fox"]["parts"]["body"]["mesh"]["v"][:, 1].min()) - 0.012
def fox_mats(st):
    gy = surf(st["x"], st["z"]) + st.get("stand_h", 0.0)                   # stand_h: standing on a stump, a rock, ...
    sq = st["sq"]; lie = st["lie"]
    tip = lie * math.pi / 2
    lift = FOX_SIDE_LIFT * abs(math.sin(tip)) + 0.22 * abs(math.sin(st["roll"]))
    R = trans(st["x"], gy - 0.01 + st["y"] + lift, st["z"]) @ roty(st["yaw"]) @ rotz(tip + st["roll"]) @ scale(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5)
    hp = FOXD["head"]["pivot"]; hd = st["head"]
    Mh = R @ trans(*hp) @ rotx(hd[0]) @ roty(hd[1]) @ rotz(hd[2]) @ trans(*(-np.array(hp)))
    arms = []
    for ai in range(2):
        # arm pose [side, fwd] or [side, fwd, inward]. Tumble's arms are short (paw reach about 1.36 high) and set
        # wide: swinging them forward leaves the paws at shoulder width (x about +-0.5). To bring the paws together in
        # front of him (crossed arms, a two-paw catch, holding something to his mouth) use inward (about 0.6-1.0).
        # Note arm0 is Tumble's LEFT paw (screen right when he faces the camera), arm1 his right.
        pv = FOXD[f"arm{ai}"]["pivot"]; sgn = 1 if ai == 0 else -1
        side, fwd = st["arms"][ai][0], st["arms"][ai][1]
        inward = st["arms"][ai][2] if len(st["arms"][ai]) > 2 else 0.0
        arms.append(R @ trans(*pv) @ roty(-sgn * inward) @ rotz(sgn * side) @ rotx(-fwd) @ trans(*(-np.array(pv))))
    legs = []
    for li in range(2):
        pv = FOXD[f"leg{li}"]["pivot"]
        legs.append(R @ trans(0, st["legs"][li], 0) @ trans(*pv) @ trans(*(-np.array(pv))))
    return R, Mh, arms, legs
def hand_pos(arms, i=0): return apply(arms[i], FOXD[f"arm{i}"]["hand"])

# ---------------- Pip ----------------
PIP_FOOT = 0.060
UP = np.array([0, PIP_FOOT, 0])
PAW_TOP = 0.072                               # Pip's feet on Tumble's paw (paw radius 0.1, minus a little so they rest on the clay)

# ---------------- series dance (same in every fable) ----------------
# Moral and chorus: Tumble's left paw (arm0, screen right) out at shoulder height (pose solved for clearance from his face in Fable 1),
# head tipped away from Pip (positive roll moves his crown away), Pip riding the paw. High-five: Pip hops up and lands
# back on the paw as it bumps up to meet him (the paw can only rise 0.11 before Pip would touch his head), star puff.
DANCE_ARM = [1.3, 0.35]
HF_RISE = 0.11
def _paw_table():
    pv = np.array(FOXD["arm0"]["pivot"]); hd = np.array(FOXD["arm0"]["hand"]); out = []
    for sd in np.linspace(1.3, 1.9, 61):
        M = trans(*pv) @ rotz(sd) @ rotx(-DANCE_ARM[1]) @ trans(*(-pv)); out.append((sd, apply(M, hd)[1]))
    return np.array(out)
PAW_TAB = _paw_table()
def paw_side_for_rise(r):
    y = PAW_TAB[:, 1] - PAW_TAB[0, 1]; i = np.argmax(y)
    return float(np.interp(r, y[:i + 1], PAW_TAB[:i + 1, 0]))
def hf_curves(t):
    a0 = T.HIGH_FIVE - 0.42; u = clampu(t, a0, a0 + 0.7)
    if not (0 < u < 1): return None
    r = HF_RISE * math.sin(math.pi * u) ** 2
    g = 0.34 * math.sin(math.pi * min(u / 0.6, 1.0))
    return g + r, r
def dance_tumble(st, t, shot):
    """moral and chorus poses (fable code sets position and anything held in the other paw)"""
    if shot == "moral":
        st["yaw"] = -0.05; st["arms"][0] = list(DANCE_ARM); st["head"][0] = -0.05; st["head"][2] = 0.08
        L = T.line("Moral")
        if L and L["t0"] < t < L["t1"] + 0.3: st["y"] += 0.025 * abs(math.sin((t - L["t0"]) * 8))
    elif shot == "chorus":
        a = SH["chorus"][0]
        sway = math.sin(2 * math.pi * (t - a) / (2 * BEAT))
        st["yaw"] = -0.05; st["roll"] = 0.06 * sway; st["head"][2] = 0.1
        st["arms"] = [list(DANCE_ARM), [0.6 - 0.3 * sway, 0.3]]
        hc = hf_curves(t)
        if hc: st["arms"][0] = [paw_side_for_rise(hc[1]), DANCE_ARM[1]]
    return st
def paw_seat(arms): return hand_pos(arms) + np.array([0, PAW_TOP, 0]) + UP
def dance_pip(t, st, mats, shot, arrive_from=None):
    """Pip on Tumble's paw for the moral (arriving from arrive_from) and the chorus (with the high-five)"""
    arms = mats[2]; top = paw_seat(arms)
    if shot == "moral":
        a = SH["moral"][0]; u = clampu(t, a, a + 0.6)
        if u < 1 and arrive_from is not None:
            p = lerp(arrive_from, top, ease(u)); p[1] += 0.4 * math.sin(math.pi * u)
            return p, 0.35, True, 0.0, False, {}
        return top, 0.35, False, 0.0, True, {}
    hc = hf_curves(t)
    if hc: return top + np.array([0, hc[0] - hc[1], 0]), 0.35, True, 0.0, False, {"highfive": True}
    return top, 0.35, False, 0.0, True, {}

# ---------------- cameras (aspect-fitted) ----------------
def fit_cam(tgt, yaw_deg, pitch_deg, fit_w, fit_h, fov=38.0, lift=None):
    """eye on a sphere round tgt (yaw 0 = camera at +z looking towards -z); distance solved so the box fits.
    Width decides in 9:16, height in 16:9. lift pushes the subject up, clear of the caption band."""
    a = W / H; th = math.tan(math.radians(fov) / 2)
    d = max(fit_h / th, fit_w / (th * a))
    yw, pt = math.radians(yaw_deg), math.radians(pitch_deg)
    dirv = np.array([math.sin(yw) * math.cos(pt), math.sin(pt), math.cos(yw) * math.cos(pt)])
    if lift is None: lift = 0.16 if not WIDE else 0.12
    tgt = np.asarray(tgt, float) - np.array([0, 1.0, 0]) * lift * d * th
    eye = tgt + dirv * d
    eye[1] = max(eye[1], surf(eye[0], eye[2]) + 0.3)                       # never below the grass
    return eye, tgt, fov
def side_on_yaw(a, b, off=104):
    """camera yaw that films the a->b axis three-quarter from the front side (Fable 1 peck lesson)"""
    ax = math.degrees(math.atan2(b[0] - a[0], b[2] - a[2]))
    return min((ax + off, ax - off), key=lambda y: -math.cos(math.radians(y)))

# ---------------- render infrastructure ----------------
LDIR = np.array([-0.55, 0.85, 0.5]); LDIR /= np.linalg.norm(LDIR)
LVIEW = look_at(LDIR * 20 + np.array([0, 0, -1.0]), np.array([0, 0, -1.0]), (0, 1, 0))
LVP = ortho(-10, 10, -10, 10, 1, 45) @ LVIEW
shadow_tex = ctx.depth_texture((2048, 2048)); shadow_tex.compare_func = "<="
shadow_tex.repeat_x = shadow_tex.repeat_y = False
shadow_fbo = ctx.framebuffer(depth_attachment=shadow_tex)
SS = 2 if PREVIEW else 4
msaa_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4, samples=SS)],
                           depth_attachment=ctx.depth_renderbuffer((W, H), samples=SS))
res_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4)])

def blink(tsec, off=0.0, period=3.3):
    ph = (tsec + off) % period
    return 1.0 - 0.92 * math.exp(-((ph - 0.1) / 0.06) ** 2)
def eyes(draws, Mh, centers, er, bl):
    for c in centers:
        draws.append((EYE_W, Mh @ trans(*c) @ scale(er, er * bl, er * 0.7), U(mat=2, bump=0.0), False))
        if bl > 0.3:
            pc = np.array(c) + np.array([-np.sign(c[0]) * er * 0.08, -er * 0.05, er * 0.6])
            draws.append((EYE_P, Mh @ trans(*pc) @ scale(er * 0.58, er * 0.66 * bl, er * 0.45), U(mat=2, bump=0.0), False))
            hc = pc + np.array([er * 0.18, er * 0.28, er * 0.4])
            draws.append((EYE_W, Mh @ trans(*hc) @ scale(er * 0.16 * bl), U(mat=3, bump=0.0), False))
def seg_M(a, b, r):
    """stick mesh (capsule along +y, radius 0.05, length 1) stretched from a to b"""
    d = b - a; L = float(np.linalg.norm(d))
    if L < 1e-5: return None
    return trans(*a) @ align_up(d / L) @ scale(r / 0.05, L, r / 0.05)
def puff(draws, c, t0, t, n=10, size=0.06, spread=0.9, dur=0.45, tint=(1.0, 0.95, 0.7), axis=(0, 0, 0.4)):
    d = t - t0
    if not (0 <= d < dur): return
    for k in range(n):
        a_ = k * 2 * math.pi / n
        q = np.asarray(c) + np.array([math.cos(a_), math.sin(a_), 0]) * (0.1 + spread * d) + np.array(axis) * d
        draws.append((PR["ball"], trans(*q) @ scale(size * (1 - d / dur)), U(mat=0, bump=0.0, tint=tint, tintMix=1.0), False))

def draw_tumble(draws, contacts, t, st, mats):
    R, Mh, arms, legs = mats
    u0 = U(mat=0, bump=1.0, seed=2.0, obj="fox")
    draws.append((FOXP["body"], R, u0, True))
    for li in range(2): draws.append((FOXP[f"leg{li}"], legs[li], u0, True))
    for ai in range(2): draws.append((FOXP[f"arm{ai}"], arms[ai], u0, True))
    draws.append((FOXP["head"], Mh, u0, True))
    tp = FOXD["tail"]["pivot"]
    draws.append((FOXP["tail"], R @ trans(*tp) @ roty(st["tail"] * 0.5) @ trans(*(-np.array(tp))), u0, True))
    eyes(draws, Mh, FOXD["eyes"]["centers"], FOXD["eyes"]["r"], 0.35 if st.get("eyes_closed") else blink(t))
    mo = mouth_at("tumble", t)
    if mo > 0.06:                                                           # one mouth, covering the carved smile while singing
        draws.append((PR["mouth"], Mh @ trans(*(np.array(FOXD["mouth"]["c"]) + np.array([0, -0.025, 0.035]))) @ scale(0.1, 0.035 + 0.05 * mo, 0.045), U(mat=2, bump=0.0), False))
    if st["lie"] < 0.5: contacts.append((st["x"], st["z"], 0.75, max(0.0, 1 - st["y"] * 1.5)))
    else: contacts.append((st["x"] - 0.4, st["z"], 1.0, 1.0))

def draw_pip(draws, contacts, t, pip, arms=None):
    """pip = (pos, yaw, flying, pitch, perch, extra). Returns Pip's matrix. extra keys: point, droop, cheer,
    highfive, beak (mouth hidden, holding something), cling, wings=(w0, w1) explicit, tuck"""
    pp, pyaw, pfly, ppitch, pperch, pex = pip
    up = U(mat=0, bump=0.6, seed=7.0, obj="pip")
    sq = -0.12 * pex.get("cling", 0.0)
    Mp = trans(*pp) @ roty(pyaw) @ rotx(ppitch) @ scale(1.1 * (1 - sq * 0.5), 1.1 * (1 + sq), 1.1 * (1 - sq * 0.5))
    draws.append((PIPP["body"], Mp, dict(up, perch=pperch), True))
    if pfly and pex.get("gentle"): flap = 0.7 + 0.35 * math.sin(t * 28)    # take-off flaps stay up, clear of faces
    elif pfly: flap = 0.9 * math.sin(t * 28)
    elif pex.get("droop"): flap = 0.04 - 0.25 * pex["droop"]
    elif pex.get("cheer"): flap = 1.1 + 0.5 * math.sin(t * 14)
    elif pex.get("tuck"): flap = -0.05
    else: flap = 0.04 + 0.04 * math.sin(t * 3)
    for wi in range(2):
        pv = PIPD[f"wing{wi}"]["pivot"]; sgn = 1 if wi == 0 else -1
        fl = flap
        if wi == 0 and pex.get("point"): fl = 1.3 + 0.12 * math.sin(t * 10)
        if pex.get("highfive") and wi == 0: fl = -0.6
        if "wings" in pex: fl = pex["wings"][wi]
        Mw = Mp @ trans(*pv) @ rotz(sgn * fl) @ trans(*(-np.array(pv)))
        draws.append((PIPP[f"wing{wi}"], Mw, up, True))
    eyes(draws, Mp, PIPD["eyes"]["centers"], PIPD["eyes"]["r"], blink(t, 1.3, 2.7))
    mp_ = mouth_at("pip", t)
    if mp_ > 0.08 and not pex.get("beak"):
        draws.append((PR["mouth"], Mp @ trans(0, 0.295, 0.19) @ scale(0.028, 0.022 * mp_, 0.02), U(mat=0, bump=0.0), False))
    if not pfly: contacts.append((pp[0], pp[2], 0.2, 1.0))
    if arms is not None and T.shot_at(t)[1] == "chorus":                    # star puff on the series high-five
        puff(draws, hand_pos(arms) + np.array([0.12, 0.24, 0.12]), T.HIGH_FIVE, t, n=8, size=0.05, spread=0.7, dur=0.4, tint=(1.0, 0.88, 0.35), axis=(0, 0, 0.3))   # where wing meets paw
    return Mp
def beak_pos(Mp): return apply(Mp, (0, 0.31, 0.27))

def meadow_backdrop(draws, t, trees=None, cottage=(7.5, -17.0), gust=0.0):
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.8), False))
    for (x, z, s) in trees or [(-7.5, -9.5, 1.6), (6.5, -9.0, 1.8), (-10.5, -13, 1.9), (10.0, -14, 2.0), (3.0, -15, 1.7), (-4.0, -16, 1.8), (8.5, -3.5, 1.5)]:
        draws.append((SC["tree"], trans(x, ground_h(x, z) - 0.05, z) @ roty(x) @ rotz(0.04 * gust * math.sin(t * 5 + x)) @ scale(s), U(mat=0, bump=0.7), True))
    if cottage: draws.append((SC["cottage"], trans(cottage[0], ground_h(*cottage) - 0.05, cottage[1]) @ roty(-0.4), U(mat=0, bump=0.6), False))
    for (x, y, z, sx, sy, sz, c) in [(-12, -1.5, -26, 10, 5.0, 4, (.62, .82, .66)), (11, -1.8, -28, 11, 6.0, 4, (.58, .78, .7)),
                                     (0, -2.8, -32, 15, 6.6, 5, (.66, .8, .78))]:
        draws.append((PR["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    for k, (x, y, z) in enumerate([(-5.0, 11.0, -18), (5.5, 13.5, -22), (-1.0, 15.5, -26)]):
        draws.append((SC["cloud"], trans(x + (0.08 + 0.6 * gust) * t * (1 if k % 2 else -1), y + 0.15 * math.sin(t * 0.5 + k), z) @ scale(1.4), U(mat=0, bump=0.4), False))
    draws.append((SC["sun"], trans(5.5, 14.0, -24) @ rotz(t * 0.2) @ scale(1.3), U(mat=0, bump=0.4), False))
def draw_flowers(draws, t, flowers, gust=0.0):
    for fi, (x, z, r, c, s) in enumerate(flowers):
        wob = 0.06 * math.sin(t * 1.6 + fi) + 0.35 * gust * math.sin(t * 9 + fi)
        draws.append((SC["flower"], trans(x, ground_h(x, z) - 0.01, z) @ roty(r) @ rotz(wob) @ scale(s), U(mat=0, bump=0.0, tint=c, tintMix=-1.0), False))

# fable hooks (set by render.py before main())
HOOKS = dict(build=None, camera=None, tumble=None, ground_objs=lambda t: ("fox", "pip"), qa_ignore=set(), sky=None)

def draw_pass(draws, contacts, eye, tgt, fov, vp, sky):
    x, y, w, h = vp
    VPm = perspective(fov, w / h, 0.12, 90.0) @ look_at(eye, tgt)
    ctx.viewport = vp
    ctx.disable(moderngl.DEPTH_TEST)
    skyprog["cTop"].value = sky[0]; skyprog["cMid"].value = sky[1]; skyprog["cHor"].value = sky[2]
    sky_vao.render()
    ctx.enable(moderngl.DEPTH_TEST)
    shadow_tex.use(0); prog["shadowMap"].value = 0
    prog["VP"].value = gl(VPm); prog["LVP"].value = gl(LVP); prog["camPos"].value = tuple(eye)
    cvals = [tuple(c) for c in contacts] + [(0, 0, 1, 0)] * (8 - len(contacts))
    prog["contact"].value = cvals[:8]; prog["nContact"].value = min(len(contacts), 8)
    prog["fade"].value = 1.0; prog["keyI"].value = 1.05
    for (mesh, M, u, cast) in draws:
        prog["M"].value = gl(M); prog["NM"].value = nmat(M)
        prog["mat"].value = u.get("mat", 0); prog["bump"].value = u.get("bump", 1.0)
        prog["tint"].value = tuple(u.get("tint", (1, 1, 1))); prog["tintMix"].value = u.get("tintMix", 0.0)
        prog["seed"].value = u.get("seed", 0.0)
        mesh.vao.render()

def render_frame(t):
    draws, contacts = HOOKS["build"](t)
    shadow_fbo.use(); shadow_fbo.clear(depth=1.0); ctx.viewport = (0, 0, 2048, 2048)
    sprog["LVP"].value = gl(LVP)
    ctx.disable(moderngl.CULL_FACE)
    for (mesh, M, u, cast) in draws:
        if cast: sprog["M"].value = gl(M); mesh.svao.render()
    msaa_fbo.use(); msaa_fbo.clear(0, 0, 0, 1, depth=1.0)
    eye, tgt, fov = HOOKS["camera"](t)
    sky = HOOKS["sky"](t) if HOOKS["sky"] else SKY
    draw_pass(draws, contacts, eye, tgt, fov, (0, 0, W, H), sky)
    ctx.viewport = (0, 0, W, H)
    ctx.copy_framebuffer(res_fbo, msaa_fbo)
    img = np.frombuffer(res_fbo.read(components=4), np.uint8).reshape(H, W, 4)[::-1].copy()
    img[..., 3] = 255
    return img

# ---------------- 2D overlay: captions, title card, moral card ----------------
tf = skia.Typeface.MakeFromFile("assets/Fredoka.ttf")
def wght(v):
    try:
        arg = skia.FontArguments(); arg.setVariationDesignPosition(skia.FontArguments.VariationPosition(
            skia.FontArguments.VariationPosition.Coordinates([skia.FontArguments.VariationPosition.Coordinate(0x77676874, v)])))
        return tf.makeClone(arg)
    except Exception:
        return tf
TF6 = wght(620); TF7 = wght(700)
grain = np.random.default_rng(1).integers(0, 255, (H, W), dtype=np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
vig = (1 - 0.2 * np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.25, 0, 1)).astype(np.float32)
PLUMC = (74, 43, 69)
COLORS = dict(big=(240, 90, 50), tiny=(40, 150, 210), white=(255, 255, 255), sour=(120, 190, 60), sweet=(240, 80, 110),
              gold=(245, 175, 40))
MORAL_BG = (255, 214, 80)
WORD_STYLE = {"big": (1.35, "big"), "helpers": (1.35, "big"), "tiny": (0.8, "tiny"), "small": (0.8, "tiny")}
WORD_STYLE.update(getattr(T, "WORD_STYLE", {}))
def word_style(w):
    k = re.sub(r"[^a-z]", "", w.lower())
    if k in WORD_STYLE: sc, c = WORD_STYLE[k]; return sc, COLORS[c]
    return 1.0, None
CAP_LINES = [L for L in T.LINES if L["section"] != "Sting"]            # the title card carries the sting
def current_line(t):
    for li, L in enumerate(CAP_LINES):
        ws = L["words"]
        start = ws[0]["t0"] - 0.12
        start = max(start, next((a for (a, b, n) in T.SHOTS if a <= ws[0]["t0"] < b), start))
        nxt = CAP_LINES[li + 1]["words"][0]["t0"] - 0.25 if li + 1 < len(CAP_LINES) else 1e9
        end = min(ws[-1]["t1"] + 0.55, nxt)
        sh_end = next((b for (a, b, n) in T.SHOTS if a <= ws[-1]["t1"] < b), end)
        end = min(end, sh_end)
        if start <= t < end: return L, start, end
    for s in T.SPOKEN:
        if s["t0"] - 0.05 <= t < s["t0"] + 1.1:
            return dict(section="spoken", words=[dict(w=x, t0=s["t0"], t1=s["t0"] + 0.8) for x in s["caption"].split()]), s["t0"] - 0.05, s["t0"] + 1.1
    return None, 0, 0
def outlined(cv, text, x, y, font, rgb, a, sw=16):
    st = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=sw * K, Color=skia.Color(*PLUMC, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
    fp = skia.Paint(AntiAlias=True, Color=skia.Color(*rgb, int(255 * a)))
    cv.drawString(text, x, y, font, st); cv.drawString(text, x, y, font, fp)
def title_card(cv, t):
    """series title, 'Fables' badge, and T.TITLE_PARTS [(text, size, colour key)] for this fable's name"""
    a0, a1 = SH[T.TITLE_SHOT]
    if not (a0 <= t < a1): return
    a = clamp01((t - a0) / 0.35) * clamp01((a1 - t) / 0.35)
    f1 = skia.Font(TF7, 128 * K)
    y0 = (360 if not WIDE else 190) * K - 6 * K * math.sin(t * 3)
    x = (W - f1.measureText(T.TITLE)) / 2
    cols = [(255, 160, 100), (250, 190, 60), (110, 175, 235), (246, 120, 170), (160, 130, 230)]
    for k, ch in enumerate(T.TITLE):
        outlined(cv, ch, x, y0 + 6 * K * math.sin(t * 5 + k * 0.6), f1, cols[k % 5], a, 22); x += f1.measureText(ch)
    bf = skia.Font(TF7, 50 * K); bw = bf.measureText(T.SERIES_TAG)
    by = y0 + 30 * K
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - bw) / 2 - 30 * K, by, bw + 60 * K, 70 * K), 35 * K, 35 * K),
                 skia.Paint(AntiAlias=True, Color=skia.Color(*MORAL_BG, int(240 * a))))
    cv.drawString(T.SERIES_TAG, (W - bw) / 2, by + 52 * K, bf, skia.Paint(AntiAlias=True, Color=skia.Color(*PLUMC, int(255 * a))))
    parts = [(s, skia.Font(TF7, sz * K), COLORS[c]) for s, sz, c in T.TITLE_PARTS]
    tw = sum(f.measureText(s) for s, f, c in parts); x = (W - tw) / 2
    for s, f, c in parts:
        outlined(cv, s, x, by + 200 * K, f, c, a, 16); x += f.measureText(s)
def overlay(img, t):
    surf_ = skia.Surface(img); cv = surf_.getCanvas()
    title_card(cv, t)
    L, start, end = current_line(t)
    if L:
        a = clamp01((t - start) / 0.15) * clamp01((end - t) / 0.15)
        moral = L["section"] == "Moral"
        base = (76 if moral else 72) * K
        maxw = (900 if not WIDE else 1400) * K
        items = []
        for w_ in L["words"]:
            sc_, col = word_style(w_["w"]); f = skia.Font(TF7, base * sc_)
            items.append((w_, f, f.measureText(w_["w"]), col))
        space = skia.Font(TF7, base).measureText(" ")
        rows, cur, wsum = [], [], 0
        for it in items:
            if cur and wsum + space + it[2] > maxw: rows.append(cur); cur, wsum = [], 0
            wsum += (space if cur else 0) + it[2]; cur.append(it)
        if cur: rows.append(cur)
        rh = 118 * K
        y = (1700 * K if not WIDE else H - 70 * K) - (rh / 2) * (len(rows) - 1) * (1 if not WIDE else 2)
        bw = max(sum(i[2] for i in r) + space * (len(r) - 1) for r in rows)
        bg = MORAL_BG if moral else (255, 250, 240)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - bw) / 2 - 40 * K, y - 98 * K, bw + 80 * K, rh * len(rows) + 30 * K), 50 * K, 50 * K),
                     skia.Paint(AntiAlias=True, Color=skia.Color(*bg, int((235 if moral else 210) * a))))
        if moral:
            lf = skia.Font(TF7, 50 * K); lt = "The moral"; lw = lf.measureText(lt)
            cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH((W - lw) / 2 - 28 * K, y - 172 * K, lw + 56 * K, 72 * K), 36 * K, 36 * K),
                         skia.Paint(AntiAlias=True, Color=skia.Color(*PLUMC, int(235 * a))))
            cv.drawString(lt, (W - lw) / 2, y - 119 * K, lf, skia.Paint(AntiAlias=True, Color=skia.Color(255, 250, 240, int(255 * a))))
        for row in rows:
            tw = sum(i[2] for i in row) + space * (len(row) - 1); x = (W - tw) / 2
            for (w_, f, wl, col) in row:
                on = w_["t0"] - 0.03 <= t < max(w_["t1"], w_["t0"] + 0.25)
                c = col or ((240, 110, 60) if on else PLUMC)
                if col and not on: c = tuple(int(v * 0.8) for v in col)
                p = skia.Paint(AntiAlias=True, Color=skia.Color(*c, int(255 * a)))
                ps = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.5 * K, Color=skia.Color(*c, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
                yb = y - (6 * K if on else 0)
                cv.drawString(w_["w"], x, yb, f, ps); cv.drawString(w_["w"], x, yb, f, p)
                x += wl + space
            y += rh
    out = img[..., :3].astype(np.float32) * vig[..., None]
    out += (grain[..., None].astype(np.float32) - 127) * (8 / 255.0)
    return np.clip(out, 0, 255).astype(np.uint8)

# ---------------- geometry QA and reviewer sheets ----------------
def qa(fps=15, out="out/qa_report.json"):
    import qa_geom
    meshes = {}
    def walk(o):
        if isinstance(o, dict):
            if "v" in o and "f" in o and "name" in o: meshes[o["name"]] = o; return
            for v in o.values(): walk(v)
    walk(D)
    bank = qa_geom.Bank("out/sdf.pkl", meshes)
    issues = []; prev_exist, prev_on = set(), {}
    for fi in range(int(T.DURATION * fps)):
        t = fi / fps
        draws, _ = HOOKS["build"](t)
        items = [(u["obj"], m.name, M, u.get("perch", False)) for (m, M, u, c) in draws if u.get("obj") and m.name in bank.g]
        eye, tgt, fov = HOOKS["camera"](t); VPm = perspective(fov, W / H, 0.2, 90.0) @ look_at(eye, tgt)
        exist, onscr = set(), {}
        for (m, M, u, c) in draws:
            if not (u.get("obj") and m.name in bank.g): continue
            o = u["obj"]; exist.add(o)
            cc, rr = bank.v[m.name + ":bs"]; p = VPm @ M @ np.r_[cc, 1]
            onscr[o] = onscr.get(o, False) or (p[3] > 0 and abs(p[0] / p[3]) < 0.95 and abs(p[1] / p[3]) < 0.95)
        if fi > 0:
            cut = any(abs(t - a) < 1.5 / fps for (a, b, n) in T.SHOTS)
            for o in (exist ^ prev_exist):
                seen = onscr.get(o, False) or prev_on.get(o, False)
                if seen and not cut:
                    issues.append(dict(t=round(t, 3), kind="pop_" + ("in" if o in exist else "out"), a=o, depth=0))
        prev_exist, prev_on = exist, onscr
        for e in qa_geom.check_frame(t, items, bank, ground=ground_h, masks={}, ground_objs=HOOKS["ground_objs"](t), float_tol=0.02):
            if (e["a"].split(":")[0], (e.get("b") or ":").split(":")[0]) in HOOKS["qa_ignore"]: continue
            issues.append(e)
    summ = qa_geom.summarize(issues, fps)
    json.dump(summ, open(out, "w"), indent=1, default=float)
    for s_ in summ: print(s_)
    print("issues:", len(summ))
    return summ
def sheets(step=0.5, per=12, cols=4, outdir="review"):
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(outdir, exist_ok=True)
    ts = [round(k * step, 2) for k in range(int(T.DURATION / step) + 1)]
    tw = 270 if not WIDE else 400; th = int(tw * H / W)
    font = ImageFont.truetype("assets/Fredoka.ttf", 22)
    for si in range(0, len(ts), per):
        chunk = ts[si:si + per]; rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + 30)), (30, 30, 30))
        for k, s in enumerate(chunk):
            fr = overlay(render_frame(s), s)
            im = Image.fromarray(fr).resize((tw, th))
            x, y = (k % cols) * tw, (k // cols) * (th + 30)
            sheet.paste(im, (x, y + 30))
            ImageDraw.Draw(sheet).text((x + 8, y + 3), f"t={s:.1f}  {T.shot_at(s)[1]}", fill=(255, 255, 255), font=font)
        p = f"{outdir}/sheet_{T.ASPECT}_{si // per + 1:02d}.jpg"
        sheet.save(p, quality=88); print(p, flush=True)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "qa": qa(); return
    if len(sys.argv) > 1 and sys.argv[1] == "sheet": sheets(); return
    if len(sys.argv) > 1 and sys.argv[1] == "x":
        for s in sys.argv[2:]:
            t0 = time.time(); fr = overlay(render_frame(float(s)), float(s))
            skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/still_{T.ASPECT}_{float(s):05.2f}.png")
            print(s, round(time.time() - t0, 2), "s", flush=True)
        return
    nfr = int(T.DURATION * FPS)
    have_audio = os.path.exists("out/audio.wav")
    if len(sys.argv) > 1 and sys.argv[1] == "seg":
        f0, f1, outp = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]; ain, aout = [], []
    else:
        outp = sys.argv[1] if len(sys.argv) > 1 else f"out/{T.JOB}_{T.ASPECT}.mp4"
        f0, f1 = 0, int(sys.argv[2]) if len(sys.argv) > 2 else nfr
        ain = ["-i", "out/audio.wav"] if have_audio else []
        aout = (["-c:a", "aac", "-b:a", "192k", "-shortest"] if have_audio else []) + ["-movflags", "+faststart"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + \
          ain + ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"] + aout + [outp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(f0, min(f1, nfr)):
        tsec = fi / FPS
        p.stdin.write(overlay(render_frame(tsec), tsec).tobytes())
        if fi % 90 == 0: print(f"frame {fi}/{min(f1, nfr)}  {time.time() - t0:.0f}s", flush=True)
    p.stdin.close(); p.wait()
    print(f"done: {min(f1, nfr) - f0} frames in {time.time() - t0:.0f}s -> {outp}", flush=True)
