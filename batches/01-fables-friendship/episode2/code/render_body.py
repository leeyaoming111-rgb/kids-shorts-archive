
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
