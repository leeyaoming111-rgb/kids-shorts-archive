"""Tumble & Pip Fables 4: Slow and Steady Bo  (Aesop: The Tortoise and the Hare)
Shared renderer: fablekit.py. python3 render.py [--wide] [--preview] [out.mp4] | x <secs...> | sheet | qa
Bo the turtle comes from the Lulu & Bo one-off; his meshes live in this fable's meshes.py copy (keys "bo", "ep4")."""
from fablekit import *
import gc, render_base as _rb

def _fix_shadow_vaos():
    """Kit bug: render_base builds the shadow VAO with "3f 36x" but vertices are 40 bytes; the right skip is "28x"
    (override here, common/ is not edited). Rebuilds the shadow VAO of every Mesh already created."""
    for o in gc.get_objects():
        if isinstance(o, _rb.Mesh):
            o.svao = _rb.ctx.vertex_array(_rb.sprog, [(o.vbo, "3f 28x", "in_pos")], o.ibo)
_orig_mesh_init = _rb.Mesh.__init__
def _mesh_init(self, m):
    _orig_mesh_init(self, m)
    self.svao = _rb.ctx.vertex_array(_rb.sprog, [(self.vbo, "3f 28x", "in_pos")], self.ibo)
_rb.Mesh.__init__ = _mesh_init
_fix_shadow_vaos()

COLORS.update(slow=(60, 170, 140), bo=(240, 140, 50))
BOP = {k: Mesh(p["mesh"]) for k, p in D["bo"]["parts"].items() if "mesh" in p}
BOD = D["bo"]["parts"]
E4 = {k: Mesh(m) for k, m in D["ep4"].items()}
MOUTH["bo"] = mouth_track("bo").tolist()

# ---------------- world: a race course across open meadow, chalk line to the big stump ----------------
START = np.array([-3.6, 2.6])
DIR = np.array([0.8, -0.6]); NRM = np.array([0.6, 0.8])      # along the course; across it (towards the front camera)
YAW_RUN = math.atan2(DIR[0], DIR[1]); YAW_BACK = math.atan2(-DIR[0], -DIR[1])
def C(s, lane): return START + DIR * s + NRM * lane
LANE_T, LANE_B = -0.7, 0.75
BO_S = 1.15
STUMP_S = 1.3; STUMP = C(9.95, 0.55); STUMP_TOP = 0.55 * STUMP_S - 0.02; STUMP_ROT = 1.2
S_TOUCH = 7.94                                               # Bo's nose on the stump
RUN_S = 6.0                                                  # where Tumble skids to a stop
NAP = C(8.4, -1.9); NAP_YAW = math.atan2(NRM[0], NRM[1])   # lying on his side, face to the course-side cameras, head up-course under the mushroom, head towards the finish
MUSH1 = C(6.95, -2.85); MUSH1_S = 1.5                        # the giant mushroom his snores puff
MUSH2 = C(8.3, -3.8); MUSH2_S = 1.05
PEB = C(0.25, -2.0)                                          # Pip's referee pebble
PEB_TOP = 0.07 * 3.0
FIN_T = C(9.3, 2.35)                                        # Tumble skids in here
FIN_LOOK = (NRM - DIR * 0.6) / np.linalg.norm(NRM - DIR * 0.6)   # the finish camera's side
MSPOT = np.array([4.3, -0.85])                              # moral, chorus and button: Tumble here, Bo on his left
BO_M = np.array([2.8, -0.35])
def _on_course(x, z):
    q = np.array([x, z]) - START; sa, la = float(np.dot(q, DIR)), float(np.dot(q, NRM))
    return -1.5 < sa < 11.5 and abs(la) < 3.0
FLOWERS = [f for f in make_flowers([], n=150, seed=41) if not _on_course(f[0], f[1])]
BACK_TREES = [(6.5, -9.0, 1.8), (10.0, -14, 2.0), (3.0, -15, 1.7), (-4.0, -16, 1.8), (-12.0, -8.0, 1.8),   # clear of every camera line
              (8.5, -3.5, 1.5), (-3.0, 9.5, 1.9), (-8.5, 7.0, 1.8), (13.0, -1.0, 1.7), (-1.0, 12.5, 1.9)]
def ground_at(p): return surf(p[0], p[1])
def P3(p, y=0.0): return np.array([p[0], ground_at(p) + y, p[1]])

# ---------------- Bo ----------------
def bo_s_at(t):
    return S_TOUCH * clampu(t, T.GO, T.BO_TOUCH)
def bo(t):
    n = T.shot_at(t)[1]
    st = dict(p=C(0.0, LANE_B), yaw=YAW_RUN, walk=0.0, head=[0.0, 0.0], y=0.0, roll=0.0, legwave=0.0)
    if n in ("moral", "chorus", "button_crane"):
        st["p"] = BO_M.copy(); st["yaw"] = 0.25
        if n == "moral":
            L = T.line("Moral")
            st["head"] = [0.25, -0.12]
            if L and L["t0"] < t < L["t1"] + 0.3: st["y"] = 0.02 * abs(math.sin((t - L["t0"]) * 7))
        elif n == "chorus":
            sway = math.sin(2 * math.pi * (t - SH["chorus"][0]) / (2 * BEAT))
            st["roll"] = 0.07 * sway; st["head"] = [0.2 + 0.1 * sway, -0.1]
        else:
            s4 = [s for s in T.SPOKEN if s["who"] == "bo"][0]["t0"]
            st["legwave"] = ease(clampu(t, s4 - 0.3, s4 + 0.3)) * (0.8 + 0.25 * math.sin((t - s4) * 4))
            st["head"] = [0.2, -0.15]
        return st
    s = bo_s_at(t); st["p"] = C(s, LANE_B)
    if T.GO < t < T.BO_TOUCH:
        st["walk"] = (t - T.GO) * 5.0                          # slow, steady steps
        st["y"] = 0.015 * abs(math.sin(st["walk"]))
        st["roll"] = 0.03 * math.sin(st["walk"])
        st["head"][0] = 0.06 * math.sin(st["walk"] * 0.5)
    if n in ("bo_steps",):                                    # humming along, head bobbing to the song
        st["head"][1] = -0.08 + 0.05 * math.sin(t * 4)
    if t >= T.BO_TOUCH:
        d = t - T.BO_TOUCH
        st["head"][1] = -0.12 * math.exp(-d * 3) * math.sin(d * 12)   # little nod as his nose taps the stump
        if t > T.CHEER: st["head"][0] = -0.35 * ease(clampu(t, T.CHEER - 0.2, T.CHEER + 0.3))   # turns to Tumble
    return st
FEET = [np.array([0.45 * sx, 0.45 * sz]) for sx, sz in ((1, 1), (-1, 1), (1, -1), (-1, -1))]
def bo_mats(st):
    p = P3(st["p"], st["y"])
    c, s_ = math.cos(st["yaw"]), math.sin(st["yaw"])            # stand on the highest foot (the meadow is gently wavy)
    g0 = ground_at(st["p"])
    gmax = max(ground_at(st["p"] + BO_S * np.array([f[0] * c + f[1] * s_, -f[0] * s_ + f[1] * c])) for f in FEET)
    p[1] += max(0.0, gmax - g0) + 0.012 + 0.6 * BO_S * abs(math.sin(st["roll"])) + (0.035 if st["walk"] else 0.0)
    R = trans(*p) @ roty(st["yaw"]) @ rotz(st["roll"]) @ scale(BO_S)
    hp = BOD["head"]["pivot"]
    Mh = R @ trans(*hp) @ roty(st["head"][0]) @ rotx(st["head"][1]) @ trans(*(-np.array(hp)))
    legs = []
    for li in range(4):
        pv = BOD[f"leg{li}"]["pivot"]; ph = st["walk"] + (0 if li in (0, 3) else math.pi)
        a = 0.4 * math.sin(ph) if st["walk"] else 0.0
        if li == 1 and st["legwave"]: a = -st["legwave"]     # Bo's slow wave with his front-left foot
        legs.append(R @ trans(*pv) @ rotx(a) @ trans(*(-np.array(pv))))
    return R, Mh, legs
def draw_bo(draws, contacts, t, st):
    R, Mh, legs = bo_mats(st)
    ub = U(mat=0, bump=1.0, seed=5.0, obj="bo")
    draws.append((BOP["shell"], R, ub, True))
    draws.append((BOP["head"], Mh, ub, True))
    for li in range(4): draws.append((BOP[f"leg{li}"], legs[li], ub, True))
    draws.append((BOP["tail"], R, ub, True))
    eyes(draws, Mh, BOD["eyes"]["centers"], BOD["eyes"]["r"], blink(t, 0.7, 3.9))
    mo = mouth_at("bo", t)
    if mo > 0.06:
        draws.append((PR["mouth"], Mh @ trans(*BOD["mouth"]["c"]) @ scale(0.055, 0.042 * mo, 0.025), U(mat=2, bump=0.0), False))
    contacts.append((st["p"][0], st["p"][1], 0.85 * BO_S, 1.0))
    return R, Mh

# ---------------- Tumble ----------------
def run_s(t):
    """Tumble's distance along his lane while racing: a fast dash from the line, skidding to a stop at RUN_S"""
    u = clampu(t, T.GO, T.RUN_END)
    return RUN_S * (1 - (1 - u) ** 2)
def tumble(t):
    st = tumble_base(t); n = T.shot_at(t)[1]
    p0 = C(0.0, LANE_T)
    st["x"], st["z"] = p0; st["yaw"] = YAW_RUN
    if n == "start_line" and t < T.GO:                       # ready crouch, leaning forward, bouncing on his toes
        st["sq"] -= 0.06; st["arms"] = [[0.35, 0.9], [0.35, 0.9]]; st["head"][0] = 0.1
        st["y"] += 0.02 * abs(math.sin(t * 7))
    elif n in ("start_line", "title_wide", "zoom"):
        s = run_s(t); st["x"], st["z"] = C(s, LANE_T)
        if t < T.RUN_END - 0.5:                              # zooming: fast legs, arms back, leaning in
            ph = (t - T.GO) * 2 * math.pi * 4.0
            st["y"] += 0.09 * abs(math.sin(ph)); st["legs"] = [0.12 * max(0, math.sin(ph)), 0.12 * max(0, -math.sin(ph))]
            st["arms"] = [[0.35, -0.6 + 0.5 * math.sin(ph)], [0.35, -0.6 - 0.5 * math.sin(ph)]]
            st["pitch"] = 0.18; st["tail"] = 0.15 * math.sin(ph)
        else:                                                # skid: leans back, then a proud little bounce
            d = t - (T.RUN_END - 0.5)
            st["pitch"] = -0.15 * math.exp(-max(0, d - 0.4) * 4); st["arms"] = [[0.9, 0.3], [0.9, 0.3]]
            if t > T.RUN_END:
                dd = t - T.RUN_END
                st["pitch"] = 0.0; st["yaw"] = lerp(YAW_RUN, YAW_RUN + 0.6, ease(clampu(dd, 0, 0.5)))
                st["sq"] -= 0.06 * math.exp(-dd * 5) * math.cos(dd * 18)
                st["arms"] = [[0.6, 0.2], [0.6, 0.2]]
    elif n in ("bo_steps", "show_off"):                      # waiting at his stop, then looking back down the course
        st["x"], st["z"] = C(RUN_S, LANE_T)
        st["yaw"] = YAW_BACK if n == "show_off" else YAW_RUN + 0.6
        if n == "bo_steps": st["head"][1] = 0.4 * math.sin(t * 0.8)
        else:
            a = SH[n][0]
            st["yaw"] = lerp(YAW_RUN + 0.6, YAW_BACK, ease(clampu(t, a, a + 0.5)))
            hips = ease(clampu(t, a + 0.2, a + 0.6))            # paws on hips, chin up: "Too easy!"
            st["arms"] = [lerp([0.15, 0.0], [0.75, -0.55], hips).tolist(), lerp([0.15, 0.0], [0.75, -0.55], hips).tolist()]
            st["head"][0] = -0.12 * hips; st["head"][2] = 0.12 * math.sin((t - a) * 3) * hips
            if T.EASY - 0.1 < t < T.EASY + 0.8: st["y"] += 0.03 * abs(math.sin((t - T.EASY) * 9))
    elif n == "lie_down":                                    # yawn and stretch, step into the shade, lie down
        a = SH[n][0]; here = C(RUN_S, LANE_T)
        if t < a + 0.8:                                      # big stretch, arms up
            st["x"], st["z"] = here; st["yaw"] = YAW_BACK
            u = ease(clampu(t, a, a + 0.5)); st["arms"] = [[0.6 * u + 0.15, 2.6 * u], [0.6 * u + 0.15, 2.6 * u]]
            st["head"][0] = -0.3 * u; st["sq"] += 0.05 * u
        elif t < T.LIE:
            walk_to(st, t, here, NAP, a + 0.8, T.LIE - 0.25, rate=1.8)
            if t > T.LIE - 0.25: st["yaw"] = NAP_YAW
        else:
            u = ease(clampu(t, T.LIE, T.LIE + 0.6))
            st["x"], st["z"] = NAP; st["yaw"] = NAP_YAW; st["lie"] = u; st["eyes_closed"] = t > T.LIE + 0.4
            st["arms"] = [[0.15, 0.4 * u], [0.15, 0.4 * u]]
    elif n in ("snore", "bo_passes", "bo_near") or (n == "wake" and t < T.WAKE):
        st["x"], st["z"] = NAP; st["yaw"] = NAP_YAW; st["lie"] = 1.0; st["eyes_closed"] = True
        st["arms"] = [[0.15, 0.4], [0.15, 0.4]]
        st["sq"] = 0.03 * snore_amt(t) + 0.012 * math.sin(t * 2.2); st["tail"] = 0.1 * math.sin(t * 1.1)
    elif n == "wake":                                         # jolts up, legs spin in the air, zooms off
        d = t - T.WAKE
        st["x"], st["z"] = NAP
        u = ease(clampu(t, T.WAKE, T.WAKE + 0.3))
        st["lie"] = 1 - u; st["yaw"] = lerp(NAP_YAW, YAW_RUN, u)
        st["head"][0] = -0.2 * u
        if T.SPIN[0] <= t < T.SPIN[1]:
            v = clampu(t, T.SPIN[0], T.SPIN[1])
            st["y"] += 0.35 * math.sin(math.pi * min(v * 2.5, 1.0) / 2) * (1 - clampu(v, 0.85, 1.0))
            ph = t * 2 * math.pi * 9
            st["legs"] = [0.14 * max(0, math.sin(ph)), 0.14 * max(0, -math.sin(ph))]
            st["arms"] = [[0.5, 1.2], [0.5, 1.2]]; st["pitch"] = -0.1
        elif t >= T.SPIN[1]:
            dd = t - T.SPIN[1]; s = 4.5 * dd ** 1.0
            st["x"], st["z"] = NAP + DIR * s * 1.0 + NRM * min(s, 0.9) * 0.6
            ph = dd * 2 * math.pi * 4.5
            st["legs"] = [0.12 * max(0, math.sin(ph)), 0.12 * max(0, -math.sin(ph))]
            st["arms"] = [[0.35, -0.6 + 0.5 * math.sin(ph)], [0.35, -0.6 - 0.5 * math.sin(ph)]]; st["pitch"] = 0.2
        if t < T.SPIN[0]: st["arms"] = [[0.9, 0.6], [0.9, 0.6]]
    elif n == "finish":
        a = SH[n][0]; p_in = FIN_T - DIR * 3.2 + NRM * 0.2
        if t < T.FOX_ARRIVE:
            u = clampu(t, a, T.FOX_ARRIVE); st["x"], st["z"] = lerp(p_in, FIN_T, 1 - (1 - u) ** 1.6)
            ph = (t - a) * 2 * math.pi * 4.5
            st["y"] += 0.08 * abs(math.sin(ph)); st["legs"] = [0.12 * max(0, math.sin(ph)), 0.12 * max(0, -math.sin(ph))]
            st["arms"] = [[0.35, -0.6 + 0.5 * math.sin(ph)], [0.35, -0.6 - 0.5 * math.sin(ph)]]; st["pitch"] = 0.2 if u < 0.8 else -0.2
        else:                                                 # skid, see Bo is first, then the good-sport cheer
            d = t - T.FOX_ARRIVE
            st["x"], st["z"] = FIN_T
            to_bo = C(S_TOUCH, LANE_B) - FIN_T; to_bo = to_bo / np.linalg.norm(to_bo)
            look = 0.35 * to_bo + 0.65 * FIN_LOOK                 # turned to Bo, cheated open to the camera
            st["yaw"] = lerp(YAW_RUN, math.atan2(look[0], look[1]), ease(clampu(d, 0.0, 0.4)))
            st["sq"] -= 0.07 * math.exp(-d * 6) * math.cos(d * 18)
            c = ease(clampu(t, T.CHEER - 0.15, T.CHEER + 0.25))
            st["arms"] = [lerp([0.6, 0.3], [0.7, 2.5], c).tolist(), lerp([0.6, 0.3], [0.7, 2.5], c).tolist()]
            if t > T.CHEER: st["y"] += 0.06 * abs(math.sin((t - T.CHEER) * 8)) * math.exp(-(t - T.CHEER) * 0.8)
    elif n in ("moral", "chorus"):
        st["x"], st["z"] = MSPOT
        dance_tumble(st, t, n)
    else:                                                    # button: waves bye-bye with both paws
        a = SH["button_crane"][0]; st["x"], st["z"] = MSPOT; st["yaw"] = -0.05
        down = ease(clampu(t, a + 0.45, a + 0.85))
        wv = math.sin((t - a) * 9) * clampu(t, a + 0.3, a + 0.6)
        st["arms"] = [lerp(DANCE_ARM, [0.9, 2.3 + 0.3 * wv], down).tolist(), [0.3, 0.3]]
    return st
def snore_amt(t):
    """0..1 puff of the snore (big on the spoken snores, gentle breathing otherwise)"""
    v = 0.25 * (0.5 + 0.5 * math.sin(t * 2.2))
    for s0 in T.SNORES:
        d = t - s0
        if 0 <= d < 0.9: v = max(v, math.sin(math.pi * d / 0.9))
    return v

def fox_mats_p(st):
    """fox_mats plus a pitch about the middle of the body (lean into the run, lean back on a skid)"""
    R, Mh, arms, legs = fox_mats(st)
    p = st.get("pitch", 0.0)
    if p == 0.0: return R, Mh, arms, legs
    root = trans(st["x"], surf(st["x"], st["z"]) + st.get("stand_h", 0.0) - 0.01 + st["y"], st["z"]) @ roty(st["yaw"])
    P = root @ trans(0, 0.8, 0) @ rotx(p) @ trans(0, -0.8, 0) @ np.linalg.inv(root)
    return P @ R, P @ Mh, [P @ a for a in arms], [P @ l for l in legs]

# ---------------- Pip (referee, with the flag in his right wing until the moral) ----------------
WING_GRIP = np.array([0.25, 0.18, 0.02])
STUMP_PIP = np.array([STUMP[0], 0, STUMP[1]]) + np.array([-DIR[0] * 0.35 + NRM[0] * 0.3, 0, -DIR[1] * 0.35 + NRM[1] * 0.3])
STUMP_PIP[1] = surf(STUMP[0], STUMP[1]) + STUMP_TOP + 0.0
STUMP_PIP = STUMP_PIP + UP
PEB_PIP = P3(PEB, PEB_TOP) + UP
def pip_state(t, st, mats):
    n = T.shot_at(t)[1]
    if n == "start_line" or (n == "title_wide" and t < SH[n][0] + 0.6):
        yaw = math.atan2(NRM[0], NRM[1])                    # faces the lanes
        w0 = 1.5 + 0.1 * math.sin(t * 6) if t < T.GO - 0.1 else lerp(1.5, -0.2, ease(clampu(t, T.GO - 0.1, T.GO + 0.15)))
        if t > T.GO + 0.6: w0 = -0.2 + 0.9 * ease(clampu(t, T.GO + 0.6, T.GO + 1.0)) + 0.25 * math.sin(t * 12) * clampu(t, T.GO + 1.0, T.GO + 1.2)
        return PEB_PIP, yaw, False, 0.0, True, {"wings": (w0, 0.1), "flag": True}
    if n == "title_wide":                                    # flies off to the finish: straight up, then along the course
        a = SH[n][0] + 0.6
        up = PEB_PIP + np.array([0, 2.7, 0])
        far = STUMP_PIP + np.array([0, 2.7, 0])
        u1 = clampu(t, a, a + 0.6)
        p = lerp(PEB_PIP, up, ease(u1))
        if t > a + 0.6: p = lerp(up, far, clampu(t, a + 0.6, a + 4.0))
        return p, YAW_RUN, True, 0.0, False, {"gentle": True, "flag": True}
    if n == "zoom":                                          # still on the way, then lands on the stump (off to the side)
        a = SH["title_wide"][0] + 1.2
        up = PEB_PIP + np.array([0, 2.7, 0]); far = STUMP_PIP + np.array([0, 2.7, 0])
        if t < a + 3.4: return lerp(up, far, clampu(t, a, a + 3.4)), YAW_RUN, True, 0.0, False, {"gentle": True, "flag": True}
        u = clampu(t, a + 3.4, a + 4.2)
        if u < 1: return lerp(far, STUMP_PIP, ease(u)), YAW_BACK, True, 0.0, False, {"gentle": True, "flag": True}
    if n in ("zoom", "bo_steps", "show_off", "lie_down", "snore", "bo_passes", "bo_near", "wake", "finish"):
        yaw = YAW_BACK
        ex = {"wings": (0.2 + 0.05 * math.sin(t * 3), 0.04), "flag": True}
        if n == "bo_near":                                   # waves the flag and calls to Tumble
            ex = {"wings": (1.3 + 0.35 * math.sin(t * 9), 0.6 + 0.3 * math.sin(t * 9 + 1)), "flag": True}
        if n == "finish" and t > T.BO_TOUCH:
            yaw = lerp(YAW_BACK, YAW_BACK - 0.5, ease(clampu(t, T.BO_TOUCH, T.BO_TOUCH + 0.4)))
            ex = {"wings": (1.4 + 0.4 * math.sin(t * 12), 1.1 + 0.4 * math.sin(t * 12 + 1)), "flag": True}
        hop = 0.0
        if n == "finish" and T.BO_TOUCH < t < T.BO_TOUCH + 0.9:
            hop = 0.18 * abs(math.sin(math.pi * (t - T.BO_TOUCH) / 0.45))
        return STUMP_PIP + np.array([0, hop, 0]), yaw, hop > 0.01, 0.0, hop <= 0.01, ex
    if n in ("moral", "chorus"):
        return dance_pip(t, st, mats, n, arrive_from=np.array([MSPOT[0] + 1.3, 1.9, MSPOT[1] + 0.4]))
    a, b = SH["button_crane"]                               # hops up off the paw and flutters, waving
    p0 = paw_seat(fox_mats_p(tumble(a))[2])
    u = clampu(t, a, a + 0.5)
    p = p0 + np.array([0.45 * ease(clampu(u, 0, 0.5)), 0.5 * ease(clampu(u, 0.3, 1.0)), 0.2 * ease(u)])     # out to the side first, then up + np.array([0, 0.05 * math.sin(t * 6), 0])
    return p, 0.35 * (1 - ease(u)), True, 0.0, False, {"wings": (0.04, 0.04)} if u < 0.5 else {"gentle": True} if u < 1 else {"wings": (1.3 + 0.4 * math.sin(t * 10), 0.5 + 0.3 * math.sin(t * 10))}

def flag_M(t, pip):
    """the flag gripped at Pip's right wing tip, kept upright with a little swing"""
    pp, pyaw, pfly, ppitch, pperch, pex = pip
    Mp = trans(*pp) @ roty(pyaw) @ rotx(ppitch) @ scale(1.1)
    if "wings" in pex: fl = pex["wings"][0]
    elif pfly and pex.get("gentle"): fl = 0.7 + 0.35 * math.sin(t * 28)
    elif pfly: fl = 0.9 * math.sin(t * 28)
    else: fl = 0.04 + 0.04 * math.sin(t * 3)
    pv = PIPD["wing0"]["pivot"]
    Mw = Mp @ trans(*pv) @ rotz(fl) @ trans(*(-np.array(pv)))
    g = apply(Mw, WING_GRIP)
    tilt = 0.45 * math.sin(fl) - 0.25                        # the flag leans out with the wing
    return trans(*g) @ roty(pyaw) @ rotz(-tilt) @ trans(0, -0.12, 0)

# ---------------- camera ----------------
def yaw_of(v): return math.degrees(math.atan2(v[0], v[1]))
SG = 1
def camera(t):
    i, name, u, lt = T.shot_at(t); e = ease(u)
    st = tumble(t); b = bo(t)
    if name == "start_line":                                 # low front of the line: Pip, Tumble, Bo
        c = C(0.15, -0.45)
        return fit_cam(np.array([c[0], 0.8, c[1]]), yaw_of(DIR) - lerp(55, 62, e), 4, 3.0 if not WIDE else 4.6, 1.5, lift=0.05)
    if name == "title_wide":                                 # high behind the start, the whole course ahead
        c = C(4.2, -0.4)
        return fit_cam(np.array([c[0], 0.7, c[1]]), yaw_of(-DIR) + 22, 24, 3.6 if not WIDE else 5.6, 3.2 if not WIDE else 2.9, lift=0.0)
    if name == "zoom":                                       # side tracking, keeping pace with Tumble
        p = np.array([st["x"], 1.15, st["z"]])
        return fit_cam(p + np.array([DIR[0], 0, DIR[1]]) * 0.5, yaw_of(NRM) + 4, 6, 2.2, 1.6)
    if name == "bo_steps":                                   # ground level, close on Bo's face and feet, tracking
        p = P3(b["p"], 0.55)
        return fit_cam(p + np.array([DIR[0], 0, DIR[1]]) * 0.35, yaw_of(NRM) + 35, -2, 1.3, 1.0, lift=0.12)
    if name == "show_off":                                   # over Tumble's shoulder, back down the course to tiny Bo
        p = C(RUN_S - 1.6, 0.0)
        return fit_cam(np.array([p[0], 1.0, p[1]]), yaw_of(DIR) - 28, 7, 2.2, 1.6, lift=0.05)
    if name == "lie_down":                                   # medium, from the far side of the course
        c = (C(RUN_S, LANE_T) + NAP) / 2 + DIR * 0.5
        return fit_cam(np.array([c[0], 1.0, c[1]]), yaw_of(NRM) + SG * lerp(8, 4, e), 16, 2.8 if not WIDE else 3.2, 2.0)
    if name == "snore":                                      # close on the snoring face and the mushroom
        hd = NAP - DIR * 1.2
        return fit_cam(np.array([hd[0], 0.85, hd[1]]), yaw_of(NRM) + SG * lerp(12, 6, e), 12, 1.5, 1.1)
    if name == "bo_passes":                                  # low wide from behind the sleeper: Bo plods past beyond him
        c = (NAP - DIR * 0.3 + b["p"]) / 2
        return fit_cam(np.array([c[0], 0.7, c[1]]), yaw_of(NRM) + SG * lerp(20, 30, e), 20, 2.9 if not WIDE else 3.6, 2.0)
    if name == "bo_near":                                    # low angle at the stump: Pip with the flag, Bo coming
        c = (STUMP + b["p"]) / 2 + NRM * 0.1
        return fit_cam(np.array([c[0], 0.95, c[1]]), yaw_of(-DIR) + 50, -4, 2.2, 1.4, lift=0.06)
    if name == "wake":                                       # medium side: the jolt and the spinning legs
        c = NAP + DIR * 0.4
        return fit_cam(np.array([c[0], 1.0, c[1]]), yaw_of(-NRM) + 8, 6, 2.2, 1.6)
    if name == "finish":                                     # low wide past the stump: Bo touches, Tumble skids in
        c = (C(S_TOUCH, LANE_B) + FIN_T) / 2 + DIR * 0.2
        return fit_cam(np.array([c[0], 0.85, c[1]]), yaw_of(FIN_LOOK) + lerp(-4, 4, e), 8, 2.05, 1.3, lift=0.03)
    mid = (MSPOT + BO_M) / 2
    if name == "moral":
        return fit_cam(np.array([mid[0] + 0.2, lerp(1.3, 1.35, e), mid[1]]), lerp(10, 4, e), 6, lerp(2.0, 1.75, e), lerp(1.45, 1.3, e))
    if name == "chorus":
        return fit_cam(np.array([mid[0] + 0.2, 1.2, mid[1]]), 4, 6, 1.9, 1.45)
    return fit_cam(np.array([mid[0] + 0.1, lerp(1.2, 2.0, e), mid[1]]), 4, lerp(6, 16, e), lerp(1.9, 2.6, e), lerp(1.45, 2.2, e), lift=0.04)

def _cam_clear():
    """drop flowers that any camera passes close to (a flower in front of the lens fills the frame)"""
    segs = []
    for t in np.arange(0, T.DURATION, 0.1):
        eye, tgt, fov = camera(t); segs.append((np.array([eye[0], eye[2]]), np.array([tgt[0], tgt[2]]), eye[1]))
    out = []
    for f in FLOWERS:
        p = np.array([f[0], f[1]]); bad = False
        for a, b, ey in segs:
            u = np.clip(np.dot(p - a, b - a) / max(np.dot(b - a, b - a), 1e-9), 0, 1)
            if u < 0.5 and np.linalg.norm(a + (b - a) * u - p) < 0.5 + 0.8 * (1 - u) and ey < 2.5: bad = True; break
        if not bad: out.append(f)
    return out
FLOWERS = _cam_clear()

# ---------------- draws ----------------
def build_draws(t):
    draws, contacts = [], []
    meadow_backdrop(draws, t, cottage=(-7.0, -15.0), trees=BACK_TREES)
    n = T.shot_at(t)[1]
    draws.append((E2["stump"], trans(STUMP[0], ground_at(STUMP) - 0.02, STUMP[1]) @ roty(STUMP_ROT) @ scale(STUMP_S), U(mat=0, bump=0.9, obj="stump"), True))
    sn = snore_amt(t) if SH["lie_down"][1] <= t < T.WAKE else 0.0
    draws.append((E2["mushroom"], trans(MUSH1[0], ground_at(MUSH1) - 0.01, MUSH1[1]) @ scale(MUSH1_S, MUSH1_S * (1 + 0.13 * sn), MUSH1_S), U(mat=0, bump=0.6, obj="mush1"), True))
    draws.append((E2["mushroom"], trans(MUSH2[0], ground_at(MUSH2) - 0.01, MUSH2[1]) @ roty(1.0) @ scale(MUSH2_S), U(mat=0, bump=0.6, obj="mush2"), True))
    for (s_, l_, sc_) in [(2.4, -3.2, 0.22), (5.2, -3.4, 0.2), (8.4, 2.6, 0.18), (-1.2, 2.4, 0.2)]:
        q = C(s_, l_); draws.append((E2["mushroom"], trans(q[0], ground_at(q) - 0.01, q[1]) @ scale(sc_), U(mat=0, bump=0.6), True))
    draws.append((SC["stone"], trans(PEB[0], ground_at(PEB) - 0.01, PEB[1]) @ roty(0.4) @ scale(1.5, 3.0, 1.5), U(mat=0, bump=0.6, obj="pebble"), True))
    ls = C(0.0, 0.0) + DIR * 0.55                            # chalk start line just in front of their toes
    draws.append((E4["chalk"], trans(ls[0], ground_at(ls) - 0.004, ls[1]) @ roty(math.atan2(NRM[0], NRM[1]) - math.pi / 2), U(mat=0, bump=0.0, tint=(0.99, 0.98, 0.95), tintMix=1.0), False))
    draw_flowers(draws, t, FLOWERS)
    st = tumble(t); mats = fox_mats_p(st); R, Mh, arms, legs = mats
    draw_tumble(draws, contacts, t, st, mats)
    draw_bo(draws, contacts, t, bo(t))
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, arms)
    if pip[5].get("flag"):
        draws.append((E4["flag"], flag_M(t, pip), U(mat=0, bump=0.0), False))
    elif n in ("moral", "chorus", "button_crane"):           # planted in the stump after the race
        q = STUMP + DIR * 0.25 - NRM * 0.15
        draws.append((E4["flag"], trans(q[0], surf(*STUMP) + STUMP_TOP - 0.05, q[1]) @ roty(0.3) @ scale(1.6), U(mat=0, bump=0.0), False))
    # snore bubbles from his mouth, and the dust of the dash
    if SH["snore"][0] <= t < T.WAKE:
        mouth = apply(Mh, (0, 1.45, 0.5))
        for k in range(3):
            ph = ((t * 0.6 + k / 3.0) % 1.0)
            q = mouth + np.array([0, 0.25 + 0.7 * ph, 0]) + np.array([DIR[0], 0, DIR[1]]) * 0.2 * math.sin(ph * 6)
            draws.append((PR["ball"], trans(*q) @ scale(0.035 + 0.05 * ph), U(mat=0, bump=0.0, tint=(0.82, 0.9, 1.0), tintMix=1.0), False))
    for k, tg in enumerate([T.GO + 0.1, T.GO + 0.5, T.GO + 0.9, T.SPIN[0] + 0.1, T.SPIN[0] + 0.35, T.SPIN[1] + 0.05]):
        if 0 <= t - tg < 0.5:
            fs = tumble(tg); puff(draws, np.array([fs["x"], surf(fs["x"], fs["z"]) + 0.15, fs["z"]]), tg, t, n=7, size=0.07, spread=0.7, dur=0.5, tint=(0.93, 0.88, 0.75), axis=(0, 0.4, 0))
    if n == "finish":
        puff(draws, np.array([FIN_T[0], surf(*FIN_T) + 0.15, FIN_T[1]]), T.FOX_ARRIVE, t, n=8, size=0.07, spread=0.8, dur=0.5, tint=(0.93, 0.88, 0.75), axis=(0, 0.4, 0))
        nose = C(S_TOUCH, LANE_B) + DIR * 1.25
        puff(draws, np.array([nose[0], surf(*nose) + 0.75, nose[1]]), T.BO_TOUCH, t, n=8, size=0.05, spread=0.7, dur=0.45, tint=(1.0, 0.88, 0.35), axis=(0, 0.3, 0))
    return draws, contacts

HOOKS.update(build=build_draws, camera=camera, tumble=tumble,
             ground_objs=lambda t: ("pip", "bo") if (SH["lie_down"][0] <= t < SH["finish"][0]) else ("fox", "pip", "bo"),
             qa_ignore=set())
if __name__ == "__main__":
    main()
