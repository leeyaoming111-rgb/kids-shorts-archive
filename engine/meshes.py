"""Clay models built as signed distance fields, meshed with marching cubes.
Every mesh vertex carries: position (rest/local), normal, colour, baked AO."""
import numpy as np
from skimage.measure import marching_cubes
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

# ---------------- SDF primitives (numpy, P[...,3]) ----------------
def V(*a): return np.array(a, dtype=np.float64)
def length(v): return np.sqrt(np.sum(v * v, axis=-1))
def sphere(P, c, r): return length(P - V(*c)) - r
def ellipsoid(P, c, rad):
    q = (P - V(*c)) / V(*rad)
    k0 = length(q); k1 = length(q / V(*rad))
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)
def capsule(P, a, b, r):
    a, b = V(*a), V(*b); pa, ba = P - a, b - a
    h = np.clip(np.sum(pa * ba, -1) / np.dot(ba, ba), 0, 1)
    return length(pa - ba * h[..., None]) - r
def round_cone(P, a, b, r1, r2):
    a, b = V(*a), V(*b); pa, ba = P - a, b - a
    h = np.clip(np.sum(pa * ba, -1) / np.dot(ba, ba), 0, 1)
    return length(pa - ba * h[..., None]) - (r1 + (r2 - r1) * h)
def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)
def smax(a, b, k): return -smin(-a, -b, k)
def rot_y(P, ang, c=(0, 0, 0)):
    c = V(*c); q = P - c; ca, sa = np.cos(ang), np.sin(ang)
    return np.stack([ca * q[..., 0] + sa * q[..., 2], q[..., 1], -sa * q[..., 0] + ca * q[..., 2]], -1) + c
def rot_z(P, ang, c=(0, 0, 0)):
    c = V(*c); q = P - c; ca, sa = np.cos(ang), np.sin(ang)
    return np.stack([ca * q[..., 0] + sa * q[..., 1], -sa * q[..., 0] + ca * q[..., 1], q[..., 2]], -1) + c
def rot_x(P, ang, c=(0, 0, 0)):
    c = V(*c); q = P - c; ca, sa = np.cos(ang), np.sin(ang)
    return np.stack([q[..., 0], ca * q[..., 1] + sa * q[..., 2], -sa * q[..., 1] + ca * q[..., 2]], -1) + c

def hexc(h, mul=1.0):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]) * mul
def mixc(a, b, t):
    t = np.clip(t, 0, 1)[..., None]; return a * (1 - t) + b * t
def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

# ---------------- mesher ----------------
def mesh_sdf(f, colf, lo, hi, step=0.026, ao=True):
    lo, hi = np.array(lo, float), np.array(hi, float)
    n = np.ceil((hi - lo) / step).astype(int) + 1
    xs = [lo[i] + step * np.arange(n[i]) for i in range(3)]
    P = np.stack(np.meshgrid(*xs, indexing="ij"), -1)
    vol = f(P)
    vol[0], vol[-1], vol[:, 0], vol[:, -1], vol[:, :, 0], vol[:, :, -1] = 1, 1, 1, 1, 1, 1
    verts, faces, _, _ = marching_cubes(vol.astype(np.float32), 0.0, spacing=(step, step, step))
    verts = verts + lo
    e = step * 0.5
    nrm = np.stack([f(verts + V(*d)) - f(verts - V(*d)) for d in ((e, 0, 0), (0, e, 0), (0, 0, e))], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True) + 1e-9
    col = colf(verts, nrm)
    if ao:
        occ = np.zeros(len(verts))
        for i, hd in enumerate((0.04, 0.09, 0.16, 0.25)):
            occ += (hd - f(verts + nrm * hd)) * (0.5 ** i) * 2.2
        a = np.clip(1 - occ, 0.35, 1)
    else:
        a = np.ones(len(verts))
    tri = verts[faces]
    # faces from marching cubes: ensure outward winding
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    if np.mean(np.sum(fn * nrm[faces].mean(1), -1)) < 0: faces = faces[:, ::-1]
    return dict(v=verts.astype(np.float32), n=nrm.astype(np.float32), c=col.astype(np.float32),
                ao=a.astype(np.float32), f=faces.astype(np.uint32))

def solid(c):
    return lambda P, N: np.broadcast_to(c, P.shape).copy()

# ---------------- dinosaurs ----------------
PALETTE = {  # base pastel, belly, accent, number colour (saturated)
    "pink":     ("#F6A9C6", "#FCDCE8", "#E57AA6", "#F0468C"),
    "peach":    ("#FFC197", "#FFE5CF", "#F29A66", "#FF7A2E"),
    "butter":   ("#FBE38A", "#FFF4C8", "#F2B65C", "#F5B800"),
    "sky":      ("#A6D3F5", "#DDF0FD", "#6FAEE3", "#2E8FEA"),
    "lavender": ("#C8B4F2", "#EAE1FC", "#9E86DE", "#8A5CF0"),
}
CREAM = hexc("#FFF6E4"); PLUM = hexc("#4A2B45"); BLUSH = hexc("#FF8FA8")
EYE_W = hexc("#FFFFFF"); EYE_P = hexc("#2A1E2C")

def face_bits(P, head_c, snout_c, snout_r, smile_r=0.11, smile_y=-0.05, cheek_dz=0.2):
    """returns (groove sdf to subtract near surface, smile mask fn inputs)"""
    sx, sy, sz = snout_c
    q_y = P[..., 1] - (sy + smile_y + smile_r * 0.9)
    q_z = P[..., 2] - sz
    ang = np.arctan2(q_y, q_z)
    ring = np.abs(np.sqrt(q_y ** 2 + q_z ** 2) - smile_r)
    lower = (ang < -0.45) & (ang > -2.7)
    arcd = np.where(lower, ring, 9.0)
    return arcd, P[..., 0] - sx

def make_dino(kind, colname):
    base, belly, accent, numc = (hexc(c) for c in PALETTE[colname])
    parts = {}
    # ---- species geometry ----
    if kind == "rex":
        body_c, body_r = (0.0, 0.98, 0.0), (0.52, 0.62, 0.46)
        legs = [((-0.02, 0.62, 0.24), 0.17, 0.2), ((-0.02, 0.62, -0.24), 0.17, 0.2)]
        neck_a, neck_b, neck_r = (0.25, 1.30, 0), (0.42, 1.55, 0), (0.30, 0.26)
        head_c, head_r = (0.48, 1.78, 0), (0.42, 0.36, 0.36)
        snout_c, snout_r = (0.78, 1.70, 0), (0.24, 0.22, 0.30)
        tail = [(-0.38, 0.85, 0), (-0.95, 0.42, 0), (-1.22, 0.36, 0)], (0.34, 0.16, 0.07)
    elif kind == "longneck":
        body_c, body_r = (0.0, 0.74, 0.0), (0.62, 0.48, 0.47)
        legs = [((0.32, 0.55, 0.26), 0.15, 0.0), ((0.32, 0.55, -0.26), 0.15, 0.0),
                ((-0.32, 0.55, 0.26), 0.15, 0.0), ((-0.32, 0.55, -0.26), 0.15, 0.0)]
        neck_a, neck_b, neck_r = (0.38, 0.92, 0), (0.70, 1.80, 0), (0.24, 0.15)
        head_c, head_r = (0.80, 2.00, 0), (0.30, 0.24, 0.25)
        snout_c, snout_r = (0.99, 1.95, 0), (0.18, 0.16, 0.21)
        tail = [(-0.45, 0.68, 0), (-1.05, 0.45, 0), (-1.32, 0.55, 0)], (0.28, 0.1, 0.05)
    elif kind == "ankylo":
        body_c, body_r = (0.0, 0.62, 0.0), (0.70, 0.40, 0.58)
        legs = [((0.34, 0.45, 0.33), 0.14, 0.0), ((0.34, 0.45, -0.33), 0.14, 0.0),
                ((-0.34, 0.45, 0.33), 0.14, 0.0), ((-0.34, 0.45, -0.33), 0.14, 0.0)]
        neck_a, neck_b, neck_r = (0.5, 0.70, 0), (0.70, 0.85, 0), (0.22, 0.2)
        head_c, head_r = (0.80, 0.95, 0), (0.32, 0.27, 0.30)
        snout_c, snout_r = (1.0, 0.89, 0), (0.18, 0.17, 0.24)
        tail = [(-0.55, 0.6, 0), (-1.05, 0.42, 0), (-1.15, 0.4, 0)], (0.24, 0.1, 0.08)
    else:  # stego / trike share the quadruped frame
        body_c, body_r = (0.0, 0.76, 0.0), (0.63, 0.50, 0.49)
        legs = [((0.32, 0.56, 0.27), 0.155, 0.0), ((0.32, 0.56, -0.27), 0.155, 0.0),
                ((-0.32, 0.56, 0.27), 0.155, 0.0), ((-0.32, 0.56, -0.27), 0.155, 0.0)]
        if kind == "trike":
            neck_a, neck_b, neck_r = (0.40, 0.92, 0), (0.60, 1.12, 0), (0.28, 0.24)
            head_c, head_r = (0.72, 1.28, 0), (0.38, 0.32, 0.33)
            snout_c, snout_r = (0.98, 1.20, 0), (0.22, 0.2, 0.26)
        else:
            neck_a, neck_b, neck_r = (0.40, 0.95, 0), (0.62, 1.25, 0), (0.25, 0.19)
            head_c, head_r = (0.72, 1.40, 0), (0.36, 0.30, 0.31)
            snout_c, snout_r = (0.96, 1.33, 0), (0.21, 0.19, 0.25)
        tail = [(-0.46, 0.68, 0), (-1.05, 0.44, 0), (-1.30, 0.55, 0)], (0.30, 0.11, 0.055)

    # ---- body ----
    def body_f(P):
        d = ellipsoid(P, body_c, body_r)
        if kind == "rex":   # tiny arms
            for s in (1, -1):
                d = smin(d, capsule(P, (0.36, 1.12, 0.30 * s), (0.56, 1.02, 0.33 * s), 0.055), 0.05)
        if kind == "stego":
            for i, a in enumerate(np.linspace(-0.95, 0.95, 5)):
                cx = body_c[0] + np.sin(a) * body_r[0] * 0.92; cy = body_c[1] + np.cos(a) * body_r[1] * 0.92
                hh = 0.2 - 0.05 * abs(a)
                Q = rot_z(P, -a * 0.8, (cx, cy, 0))
                plate = ellipsoid(Q, (cx, cy + hh * 0.7, 0), (0.14 - 0.02 * abs(a), hh, 0.045))
                d = smin(d, plate, 0.04)
        if kind == "ankylo":
            for ix in np.linspace(-0.5, 0.5, 5):
                for iz in np.linspace(-0.42, 0.42, 4):
                    q = (ix / body_r[0]) ** 2 + (iz / body_r[2]) ** 2
                    if q > 0.85: continue
                    y = body_c[1] + body_r[1] * np.sqrt(max(0, 1 - q))
                    d = smin(d, sphere(P, (ix, y, iz), 0.085), 0.03)
            for iz in (-1, 1):   # side spikes
                for ix in (-0.35, 0.05, 0.4):
                    d = smin(d, round_cone(P, (ix, 0.62, iz * 0.5), (ix, 0.6, iz * 0.72), 0.07, 0.02), 0.03)
        return d
    def body_col(P, N):
        c = np.broadcast_to(base, P.shape).copy()
        bel = sstep(0.0, -0.55, N[..., 1]) * sstep(body_c[1] + 0.1, body_c[1] - 0.25, P[..., 1])
        c = mixc(c, belly, bel)
        if kind == "stego":
            c = mixc(c, accent, sstep(body_c[1] + body_r[1] * 0.97, body_c[1] + body_r[1] * 1.08, P[..., 1]))
        if kind == "ankylo":
            top = sstep(body_c[1] + body_r[1] * 0.82, body_c[1] + body_r[1] * 0.97, P[..., 1] + 0 * P[..., 0])
            c = mixc(c, accent, top)
            c = mixc(c, CREAM, sstep(0.55, 0.66, np.abs(P[..., 2])) * sstep(0.45, 0.7, P[..., 1]))
        if kind == "longneck":   # soft spots
            for (x, y, z) in [(-0.2, 1.1, 0.25), (0.15, 1.15, -0.2), (-0.35, 0.95, -0.35), (0.25, 0.95, 0.38), (0.0, 1.22, 0.05)]:
                c = mixc(c, accent, sstep(0.11, 0.07, length(P - V(x, y, z))))
        return c
    lo = np.array(body_c) - np.array(body_r) - 0.35; hi = np.array(body_c) + np.array(body_r) + 0.35
    parts["body"] = dict(mesh=mesh_sdf(body_f, body_col, lo, hi), pivot=body_c)

    # ---- legs ----
    for li, (hip, r, extra) in enumerate(legs):
        hx, hy, hz = hip
        def leg_f(P, hx=hx, hy=hy, hz=hz, r=r, extra=extra):
            d = round_cone(P, (hx, hy + 0.05, hz), (hx + 0.02, 0.15, hz), r * 1.15, r)
            d = smin(d, ellipsoid(P, (hx + 0.05, 0.11, hz), (r * 1.25 + extra * 0.3, 0.11, r * 1.1 + extra * 0.2)), 0.06)
            d = smax(d, -(P[..., 1] - 0.0), 0.02)
            for dz in (-0.07, 0.0, 0.07):
                d = smin(d, sphere(P, (hx + r * 1.15 + extra * 0.25, 0.06, hz + dz * (1 + extra)), 0.042), 0.015)
            return d
        def leg_col(P, N, hx=hx, hz=hz, r=r, extra=extra):
            c = np.broadcast_to(base, P.shape).copy()
            nail = (P[..., 0] > hx + r * 1.02 + extra * 0.25) & (P[..., 1] < 0.11)
            c[nail] = CREAM
            return mixc(c, base * 0.93, sstep(0.3, 0.05, P[..., 1]) * 0.6)
        lo = (hx - 0.4, -0.02, hz - 0.4); hi = (hx + 0.45, hy + 0.3, hz + 0.4)
        parts[f"leg{li}"] = dict(mesh=mesh_sdf(leg_f, leg_col, lo, hi), pivot=(hx, hy, hz))

    # ---- head + neck ----
    def head_f(P):
        d = round_cone(P, neck_a, neck_b, *neck_r)
        d = smin(d, ellipsoid(P, head_c, head_r), 0.12)
        d = smin(d, ellipsoid(P, snout_c, snout_r), 0.1)
        if kind == "trike":
            Q = rot_z(P, 0.55, (head_c[0] - 0.12, head_c[1] + 0.12, 0))
            fr = ellipsoid(Q, (head_c[0] - 0.18, head_c[1] + 0.2, 0), (0.07, 0.42, 0.5))
            for a in np.linspace(-1.2, 1.2, 7):    # scalloped frill edge
                fr = smin(fr, sphere(Q, (head_c[0] - 0.18, head_c[1] + 0.2 + 0.42 * np.cos(a), 0.5 * np.sin(a)), 0.07), 0.04)
            d = smin(d, fr, 0.06)
            for s in (1, -1):
                d = smin(d, round_cone(P, (head_c[0] + 0.12, head_c[1] + 0.22, 0.14 * s), (head_c[0] + 0.36, head_c[1] + 0.5, 0.2 * s), 0.065, 0.015), 0.04)
            d = smin(d, round_cone(P, (snout_c[0] + 0.1, snout_c[1] + 0.14, 0), (snout_c[0] + 0.22, snout_c[1] + 0.3, 0), 0.05, 0.012), 0.03)
        arcd, front = face_bits(P, head_c, snout_c, snout_r, smile_r=0.13 if kind == "rex" else 0.1,
                                smile_y=-0.06)
        groove = np.maximum(arcd - 0.02, np.maximum(-front, -(d + 0.045)))
        d = np.maximum(d, -groove)
        for s in (1, -1):   # nostrils
            d = smax(d, -sphere(P, (snout_c[0] + snout_r[0] * 0.92, snout_c[1] + 0.07, 0.07 * s), 0.025), 0.01)
        return d
    def head_col(P, N):
        c = np.broadcast_to(base, P.shape).copy()
        c = mixc(c, belly, sstep(0.0, -0.6, N[..., 1]) * sstep(snout_c[1], snout_c[1] - 0.15, P[..., 1]))
        if kind == "trike":
            Q = rot_z(P, 0.55, (head_c[0] - 0.12, head_c[1] + 0.12, 0))
            fr = ellipsoid(Q, (head_c[0] - 0.18, head_c[1] + 0.2, 0), (0.09, 0.44, 0.52))
            c = mixc(c, accent, sstep(0.02, -0.02, fr))
            horn = P[..., 1] > head_c[1] + 0.3
            c = mixc(c, CREAM, sstep(head_c[1] + 0.3, head_c[1] + 0.36, P[..., 1]) * (P[..., 0] > head_c[0] + 0.1))
            c = mixc(c, CREAM, sstep(snout_c[1] + 0.18, snout_c[1] + 0.22, P[..., 1]) * (P[..., 0] > snout_c[0]))
        arcd, front = face_bits(P, head_c, snout_c, snout_r, smile_r=0.13 if kind == "rex" else 0.1, smile_y=-0.06)
        c = mixc(c, PLUM, sstep(0.034, 0.02, arcd) * (front > 0))
        for s in (1, -1):
            cheek = V(snout_c[0] + snout_r[0] * 0.35, snout_c[1] + 0.0, s * snout_r[2] * 0.85)
            c = mixc(c, BLUSH, 0.75 * sstep(0.085, 0.03, length(P - cheek)))
        return c
    hl = np.minimum(np.minimum(neck_a, neck_b), np.minimum(head_c, snout_c)) - 0.65
    hh = np.maximum(np.maximum(neck_a, neck_b), np.maximum(head_c, snout_c)) + 0.65
    parts["head"] = dict(mesh=mesh_sdf(head_f, head_col, hl, hh, step=0.019), pivot=neck_a)

    # ---- eyes (follow head) ----
    er = 0.095 if kind != "rex" else 0.11
    ex = head_c[0] + head_r[0] * 0.62; ey = head_c[1] + head_r[1] * 0.42; ez = head_r[2] * 0.5
    eyes = []
    for s in (1, -1):
        c = (ex, ey, ez * s)
        eyes.append(c)
    parts["eyes"] = dict(centers=eyes, r=er, pivot=neck_a)

    # ---- tail ----
    (ta, tb, tc), (r1, r2, r3) = tail
    def tail_f(P):
        d = round_cone(P, ta, tb, r1, r2)
        d = smin(d, round_cone(P, tb, tc, r2, r3), 0.06)
        if kind == "stego":
            for s in (1, -1):
                for k, off in enumerate((0.0, 0.15)):
                    b = (tb[0] - 0.1 - off, tb[1] + 0.08, 0.0)
                    d = smin(d, round_cone(P, b, (b[0] - 0.05, b[1] + 0.2, 0.16 * s), 0.045, 0.01), 0.03)
        if kind == "ankylo":
            d = smin(d, ellipsoid(P, (tc[0] - 0.08, tc[1], 0), (0.2, 0.15, 0.2)), 0.05)
        return d
    def tail_col(P, N):
        c = np.broadcast_to(base, P.shape).copy()
        c = mixc(c, belly, sstep(0.0, -0.6, N[..., 1]) * 0.8)
        if kind == "stego":
            c = mixc(c, CREAM, sstep(tb[1] + 0.12, tb[1] + 0.17, P[..., 1]))
        if kind == "ankylo":
            c = mixc(c, accent, sstep(tc[0] + 0.15, tc[0] + 0.05, P[..., 0]))
        return c
    tl = np.minimum(np.minimum(ta, tb), tc) - 0.45; th = np.maximum(np.maximum(ta, tb), tc) + 0.45
    parts["tail"] = dict(mesh=mesh_sdf(tail_f, tail_col, tl, th), pivot=ta)
    return dict(parts=parts, kind=kind, color=colname, numcol=numc, base=base, legs=len(legs),
                head_top=head_c[1] + head_r[1] + (0.45 if kind == "trike" else 0.0),
                body_c=body_c)

def eye_meshes():
    w = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(EYE_W), (-1.2,) * 3, (1.2,) * 3, step=0.2, ao=False)
    p = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(EYE_P), (-1.2,) * 3, (1.2,) * 3, step=0.22, ao=False)
    return w, p

# ---------------- numbers (puffy clay digits with white sticker backing) ----------------
def digit_meshes(font_path, ch):
    S = 400
    img = Image.new("L", (S, S), 0); d = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 330)
    try: font.set_variation_by_axes([650, 100])
    except Exception: pass
    bb = d.textbbox((0, 0), ch, font=font)
    d.text(((S - (bb[2] - bb[0])) / 2 - bb[0], (S - (bb[3] - bb[1])) / 2 - bb[1]), ch, fill=255, font=font)
    m = np.array(img) > 127
    dist = np.where(m, -ndimage.distance_transform_edt(m), ndimage.distance_transform_edt(~m))
    hgt = (bb[3] - bb[1])
    sc = 1.0 / hgt                          # world units per pixel; digit height = 1.0
    dist = dist * sc
    def d2(P, grow=0.0):
        u = (P[..., 0] / sc + S / 2); v = (S / 2 - P[..., 1] / sc)
        return ndimage.map_coordinates(dist, [v.ravel(), u.ravel()], order=1, mode="nearest").reshape(P.shape[:-1]) - grow
    def puff(P, grow, th, r):
        a = d2(P, grow) + r; b = np.abs(P[..., 2]) - th + r
        return np.sqrt(np.maximum(a, 0) ** 2 + np.maximum(b, 0) ** 2) + np.minimum(np.maximum(a, b), 0) - r
    lo, hi = (-0.75, -0.75, -0.3), (0.75, 0.75, 0.3)
    front = mesh_sdf(lambda P: puff(P - V(0, 0, 0.06), 0.0, 0.11, 0.07), solid(np.ones(3)), lo, hi, step=0.02, ao=False)
    back = mesh_sdf(lambda P: puff(P, 0.075, 0.07, 0.05), solid(np.ones(3)), lo, hi, step=0.024, ao=False)
    return front, back

# ---------------- scenery ----------------
def hill_height(x, z):
    h = 2.2 * np.exp(-((x / 3.9) ** 2 + ((z + 1.3) / 2.5) ** 2))
    h += 0.35 * np.exp(-(((x + 4.5) / 3.0) ** 2 + ((z + 4.0) / 3.0) ** 2))
    h += 0.45 * np.exp(-(((x - 5.0) / 3.2) ** 2 + ((z + 5.0) / 3.0) ** 2))
    h += 0.04 * np.sin(x * 1.3 + 0.5) * np.sin(z * 1.1)
    return h

def ground_mesh():
    nx, nz = 150, 130
    xs = np.linspace(-14, 14, nx); zs = np.linspace(-16, 10, nz)
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    Y = hill_height(X, Z)
    P = np.stack([X, Y, Z], -1)
    e = 0.01
    dx = (hill_height(X + e, Z) - hill_height(X - e, Z)) / (2 * e)
    dz = (hill_height(X, Z + e) - hill_height(X, Z - e)) / (2 * e)
    N = np.stack([-dx, np.ones_like(dx), -dz], -1); N /= np.linalg.norm(N, axis=-1, keepdims=True)
    rng = np.random.default_rng(3)
    moss1, moss2, moss3 = hexc("#8CC870"), hexc("#6FB25E"), hexc("#B5DC8A")
    n1 = 0.5 + 0.5 * np.sin(X * 1.7 + np.sin(Z * 1.3) * 2) * np.sin(Z * 1.9 + np.sin(X * 0.7) * 1.5)
    C = mixc(np.broadcast_to(moss1, P.shape), moss2, n1 * 0.7)
    C = mixc(C, moss3, sstep(1.6, 2.2, Y) * 0.5)
    idx = np.arange(nx * nz).reshape(nx, nz)
    a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
    faces = np.concatenate([np.stack([a, d, c], -1).reshape(-1, 3), np.stack([a, c, b], -1).reshape(-1, 3)])
    return dict(v=P.reshape(-1, 3).astype(np.float32), n=N.reshape(-1, 3).astype(np.float32),
                c=C.reshape(-1, 3).astype(np.float32), ao=np.ones(nx * nz, np.float32), f=faces.astype(np.uint32))

def blob_mesh(spheres, col, step=0.05, k=0.25):
    def f(P):
        d = None
        for (c, r) in spheres:
            s = ellipsoid(P, c, r) if np.ndim(r) else sphere(P, c, r)
            d = s if d is None else smin(d, s, k)
        return d
    cs = np.array([c for c, _ in spheres]); rs = np.array([np.max(r) for _, r in spheres])
    lo = (cs - rs[:, None]).min(0) - 0.4; hi = (cs + rs[:, None]).max(0) + 0.4
    return mesh_sdf(f, col if callable(col) else solid(col), lo, hi, step=step)

def scenery():
    out = {}
    # clouds (in front of a painted sky)
    out["cloud"] = blob_mesh([((0, 0, 0), (1.1, 0.7, 0.7)), ((1.1, -0.15, 0), (0.8, 0.55, 0.6)), ((-1.1, -0.2, 0), (0.75, 0.5, 0.55)),
                              ((0.4, 0.45, 0.1), (0.7, 0.6, 0.5))], hexc("#FFFFFF"), step=0.09)
    # volcano
    def volc_f(P):
        r = np.sqrt(P[..., 0] ** 2 + P[..., 2] ** 2)
        cone = np.maximum(r * 0.75 + P[..., 1] * 0.66 - 2.6, -P[..., 1])
        cone = smax(cone, P[..., 1] - 3.3, 0.3)
        crater = sphere(P, (0, 3.75, 0), 0.9)
        return smax(cone, -crater, 0.15)
    def volc_col(P, N):
        c = mixc(np.broadcast_to(hexc("#C9A48A"), P.shape), hexc("#B08A74"), 0.5 + 0.5 * np.sin(np.arctan2(P[..., 2], P[..., 0]) * 7))
        lava = sstep(2.9, 3.2, P[..., 1]) + sstep(0.3, 0.0, np.abs(np.arctan2(P[..., 2], P[..., 0]) - 1.5) - 0.12 * (3.3 - P[..., 1])) * sstep(1.8, 2.6, P[..., 1])
        return mixc(c, hexc("#FF9A5C"), np.clip(lava, 0, 1))
    out["volcano"] = mesh_sdf(volc_f, volc_col, (-4, -0.2, -4), (4, 3.6, 4), step=0.12)
    out["smoke"] = blob_mesh([((0, 0, 0), 0.5), ((0.4, 0.5, 0), 0.45), ((0.1, 1.0, 0), 0.4)], hexc("#F2EEF2"), step=0.08, k=0.2)
    # rounded tree
    def tree_col(P, N):
        return np.where((P[..., 1] < 1.3)[..., None], hexc("#B98A6A"), mixc(np.broadcast_to(hexc("#7CC27A"), P.shape), hexc("#A8DC8C"), sstep(0, 0.8, N[..., 1])))
    out["tree"] = blob_mesh([((0, 0.7, 0), (0.18, 0.75, 0.18)), ((0, 1.9, 0), (0.75, 0.68, 0.7)), ((0.45, 1.6, 0.2), (0.5, 0.45, 0.45)),
                             ((-0.45, 1.65, -0.1), (0.5, 0.45, 0.45)), ((0.05, 2.4, 0), (0.5, 0.42, 0.45))], tree_col, step=0.07, k=0.12)
    # flowers: stem nub, five petals, centre (petal colour via instance tint; centre yellow)
    def flower_f(P):
        d = capsule(P, (0, 0, 0), (0, 0.18, 0), 0.025)
        for i in range(5):
            a = i * 2 * np.pi / 5
            d = smin(d, ellipsoid(P, (0.075 * np.cos(a), 0.2, 0.075 * np.sin(a)), (0.06, 0.025, 0.06)), 0.02)
        return smin(d, sphere(P, (0, 0.215, 0), 0.04), 0.01)
    def flower_col(P, N):
        r = np.sqrt(P[..., 0] ** 2 + P[..., 2] ** 2)
        c = np.where((r < 0.042)[..., None] & (P[..., 1] > 0.19)[..., None], hexc("#FFD45C"), np.ones(3))
        return np.where((P[..., 1] < 0.17)[..., None], hexc("#6BAF5B"), c)
    out["flower"] = mesh_sdf(flower_f, flower_col, (-0.2, -0.05, -0.2), (0.2, 0.3, 0.2), step=0.013, ao=False)
    out["rock"] = blob_mesh([((0, 0.1, 0), (0.32, 0.22, 0.28)), ((0.2, 0.08, 0.1), (0.2, 0.15, 0.18))], hexc("#C9C2D6"), step=0.045, k=0.1)
    out["sun"] = blob_mesh([((0, 0, 0), (1.0, 1.0, 0.35))] + [((1.45 * np.cos(a), 1.45 * np.sin(a), 0), (0.22, 0.22, 0.18)) for a in np.linspace(0, 2 * np.pi, 11)[:-1]],
                           hexc("#FFE07A"), step=0.08, k=0.12)
    out["ball"] = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(np.ones(3)), (-1.2,) * 3, (1.2,) * 3, step=0.12, ao=False)
    out["disc"] = mesh_sdf(lambda P: ellipsoid(P, (0, 0, 0), (1.0, 0.25, 1.0)), solid(np.ones(3)), (-1.2,) * 3, (1.2,) * 3, step=0.25, ao=False)
    out["ground"] = ground_mesh()
    return out

DINOS = [("stego", "pink"), ("longneck", "peach"), ("rex", "sky"), ("trike", "butter"), ("ankylo", "lavender")]

if __name__ == "__main__":
    import pickle, time
    t0 = time.time()
    data = dict(dinos=[make_dino(k, c) for k, c in DINOS])
    print("dinos", round(time.time() - t0, 1))
    data["eye_w"], data["eye_p"] = eye_meshes()
    data["digits"] = {str(i): digit_meshes("assets/Fredoka.ttf", str(i)) for i in range(1, 6)}
    data["scene"] = scenery()
    tris = sum(p["mesh"]["f"].shape[0] for d in data["dinos"] for p in d["parts"].values() if "mesh" in p)
    print("dino tris", tris, "total time", round(time.time() - t0, 1))
    pickle.dump(data, open("out/meshes.pkl", "wb"))
