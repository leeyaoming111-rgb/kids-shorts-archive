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

# ---------------- penguins ----------------
PALETTE = {  # base pastel, accent (flippers/back), feet+beak
    "pink":     ("#F4B3CB", "#E592B2", "#FFB27A"),
    "mint":     ("#A9DEC6", "#84C7AA", "#FFB27A"),
    "sky":      ("#AFCFF2", "#8CB4E3", "#FFB27A"),
    "lavender": ("#CDBDF0", "#AE9BDF", "#FFB27A"),
    "peach":    ("#FFCBA6", "#F2AE84", "#F59A7A"),
}
CREAM = hexc("#F4E8DA"); PLUM = hexc("#4A2B45"); BLUSH = hexc("#FF8FA8")
EYE_W = hexc("#FFFFFF"); EYE_P = hexc("#2A1E2C")

def make_penguin(colname, tuft=False, bow=False):
    base, accent, feetc = (hexc(c) for c in PALETTE[colname])
    parts = {}
    body_c, body_r = (0.0, 0.78, 0.0), (0.50, 0.66, 0.48)
    head_c, head_r = (0.06, 1.50, 0.0), (0.40, 0.37, 0.40)

    def body_f(P):
        return ellipsoid(P, body_c, body_r)
    def body_col(P, N):
        c = np.broadcast_to(base, P.shape).copy()
        q = ((P[..., 1] - 0.72) / 0.52) ** 2 + (P[..., 2] / 0.34) ** 2
        bel = sstep(1.05, 0.85, q) * sstep(-0.05, 0.2, P[..., 0])
        c = mixc(c, CREAM, bel)
        c = mixc(c, accent, sstep(-0.1, -0.45, P[..., 0]) * 0.55)
        return c
    lo = np.array(body_c) - np.array(body_r) - 0.3; hi = np.array(body_c) + np.array(body_r) + 0.3
    parts["body"] = dict(mesh=mesh_sdf(body_f, body_col, lo, hi), pivot=body_c)

    # feet (2) as legs
    for li, sz in enumerate((1, -1)):
        hx, hy, hz = 0.12, 0.15, 0.2 * sz
        def leg_f(P, hz=hz):
            d = ellipsoid(P, (0.2, 0.06, hz), (0.22, 0.07, 0.14))
            for dz in (-0.075, 0.0, 0.075):
                d = smin(d, sphere(P, (0.38, 0.05, hz + dz), 0.05), 0.03)
            d = smin(d, capsule(P, (0.05, 0.08, hz), (0.05, 0.22, hz), 0.07), 0.05)
            return smax(d, -(P[..., 1] - 0.0), 0.02)
        lo = (hx - 0.4, -0.02, hz - 0.35); hi = (hx + 0.45, 0.4, hz + 0.35)
        parts[f"leg{li}"] = dict(mesh=mesh_sdf(leg_f, solid(feetc), lo, hi), pivot=(hx, hy, hz))

    # flippers (2)
    for fi, sz in enumerate((1, -1)):
        sh = (0.0, 1.15, 0.42 * sz)
        def flip_f(P, sz=sz):
            Q = rot_x(P, 0.22 * sz, (0.0, 1.15, 0.42 * sz))
            return ellipsoid(Q, (-0.02, 0.82, 0.47 * sz), (0.15, 0.36, 0.075))
        def flip_col(P, N):
            return mixc(np.broadcast_to(accent, P.shape).copy(), base, sstep(0.6, 1.1, P[..., 1]) * 0.5)
        lo = (-0.4, 0.3, 0.42 * sz - 0.35); hi = (0.4, 1.4, 0.42 * sz + 0.35)
        parts[f"flip{fi}"] = dict(mesh=mesh_sdf(flip_f, flip_col, lo, hi), pivot=sh)

    # head (+ beak, cheeks, optional tuft / bow)
    beak_a, beak_b = (head_c[0] + 0.34, head_c[1] - 0.07, 0), (head_c[0] + 0.58, head_c[1] - 0.10, 0)
    def head_f(P):
        d = round_cone(P, (0.0, 1.12, 0), (0.04, 1.40, 0), 0.40, 0.37)
        d = smin(d, ellipsoid(P, head_c, head_r), 0.1)
        d = smin(d, round_cone(P, beak_a, beak_b, 0.10, 0.035), 0.04)
        if tuft:
            for k, a in enumerate((-0.35, 0.0, 0.35)):
                tip = (head_c[0] - 0.05 + 0.12 * a, head_c[1] + head_r[1] + 0.22 - 0.06 * abs(a) * 2, 0.12 * a)
                d = smin(d, round_cone(P, (head_c[0] - 0.02, head_c[1] + head_r[1] - 0.06, 0.05 * a), tip, 0.06, 0.02), 0.04)
        if bow:
            for s_ in (1, -1):
                d = smin(d, ellipsoid(P, (head_c[0] - 0.05, head_c[1] + head_r[1] - 0.02, 0.13 * s_), (0.07, 0.07, 0.12)), 0.02)
            d = smin(d, sphere(P, (head_c[0] - 0.05, head_c[1] + head_r[1] - 0.01, 0), 0.06), 0.02)
        return d
    def head_col(P, N):
        c = np.broadcast_to(base, P.shape).copy()
        face = sstep(0.12, 0.26, P[..., 0] - head_c[0]) * sstep(head_c[1] + 0.02, head_c[1] - 0.06, P[..., 1]) * 0.85
        c = mixc(c, CREAM, face)
        c = mixc(c, feetc, sstep(0.025, 0.0, round_cone(P, beak_a, beak_b, 0.10, 0.035)))
        for s_ in (1, -1):
            cheek = V(head_c[0] + 0.24, head_c[1] - 0.07, s_ * 0.27)
            c = mixc(c, BLUSH, 0.75 * sstep(0.09, 0.03, length(P - cheek)))
        if tuft:
            c = mixc(c, accent, sstep(head_c[1] + head_r[1] - 0.04, head_c[1] + head_r[1] + 0.02, P[..., 1]))
        if bow:
            bc = V(head_c[0] - 0.05, head_c[1] + head_r[1] - 0.02, 0)
            c = mixc(c, hexc("#FFFFFF"), sstep(0.2, 0.15, length((P - bc) * V(1, 1, 0.6))))
        return c
    parts["head"] = dict(mesh=mesh_sdf(head_f, head_col, (-0.55, 0.85, -0.6), (0.85, 2.25, 0.6), step=0.019), pivot=(0.0, 1.15, 0.0))

    er = 0.085
    ex = head_c[0] + head_r[0] * 0.70; ey = head_c[1] + head_r[1] * 0.30; ez = 0.17
    parts["eyes"] = dict(centers=[(ex, ey, ez), (ex, ey, -ez)], r=er, pivot=(0.0, 1.15, 0.0))

    def tail_f(P):
        return round_cone(P, (-0.38, 0.32, 0), (-0.62, 0.12, 0), 0.13, 0.05)
    parts["tail"] = dict(mesh=mesh_sdf(tail_f, solid(accent), (-0.9, -0.1, -0.35), (-0.1, 0.6, 0.35)), pivot=(-0.38, 0.32, 0))
    return dict(parts=parts, kind="penguin", color=colname, base=base, legs=2,
                head_top=head_c[1] + head_r[1] + (0.2 if tuft else 0.05), body_c=body_c)

def eye_meshes():
    w = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(EYE_W), (-1.2,) * 3, (1.2,) * 3, step=0.2, ao=False)
    p = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(EYE_P), (-1.2,) * 3, (1.2,) * 3, step=0.22, ao=False)
    return w, p

# ---------------- shapes (puffy clay shapes with white sticker backing) ----------------
def shape_mask(name, S=400):
    img = Image.new("L", (S, S), 0); d = ImageDraw.Draw(img); c = S / 2; R = 150
    if name == "circle":
        d.ellipse((c - R, c - R, c + R, c + R), fill=255)
    elif name == "square":
        d.rounded_rectangle((c - 135, c - 135, c + 135, c + 135), radius=34, fill=255)
    elif name == "triangle":
        pts = [(c + 165 * np.cos(np.pi / 2 + k * 2 * np.pi / 3), c - 165 * np.sin(np.pi / 2 + k * 2 * np.pi / 3) + 30) for k in range(3)]
        d.polygon(pts, fill=255)
        img = img.filter(__import__("PIL.ImageFilter", fromlist=["x"]).MinFilter(15)).filter(__import__("PIL.ImageFilter", fromlist=["x"]).MaxFilter(15))
        img = img.point(lambda v: 255 if v > 127 else 0)
    elif name == "star":
        pts = []
        for k in range(10):
            r = 170 if k % 2 == 0 else 74
            a = np.pi / 2 + k * np.pi / 5
            pts.append((c + r * np.cos(a), c - r * np.sin(a) + 12))
        d.polygon(pts, fill=255)
    elif name == "heart":
        t = np.linspace(0, 2 * np.pi, 400)
        x = 16 * np.sin(t) ** 3; y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        d.polygon(list(zip(c + x * 9.5, c - y * 9.5 - 10)), fill=255)
    return np.array(img) > 127

def shape_meshes(name):
    S = 400
    m = shape_mask(name, S)
    dist = np.where(m, -ndimage.distance_transform_edt(m), ndimage.distance_transform_edt(~m))
    ys, xs = np.where(m); hgt = max(ys.max() - ys.min(), xs.max() - xs.min())
    cy, cx = (ys.max() + ys.min()) / 2, (xs.max() + xs.min()) / 2
    sc = 1.0 / hgt
    dist = dist * sc
    def d2(P, grow=0.0):
        u = (P[..., 0] / sc + cx); v = (cy - P[..., 1] / sc)
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
    moss1, moss2, moss3 = hexc("#E6EEF8"), hexc("#D3E0F2"), hexc("#F4F8FD")
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
    # igloo
    def igloo_f(P):
        dome = smax(sphere(P, (0, 0, 0), 2.0), -P[..., 1], 0.05)
        tun = smax(capsule(P, (1.6, 0.0, 0), (2.6, 0.0, 0), 0.85), -P[..., 1], 0.05)
        d = smin(dome, tun, 0.15)
        door = capsule(P, (2.0, 0.0, 0), (2.9, 0.0, 0), 0.55)
        return smax(d, -door, 0.05)
    def igloo_col(P, N):
        c = np.broadcast_to(hexc("#CFE0F6"), P.shape).copy()
        r = np.sqrt(np.sum(P ** 2, -1)); el = np.arcsin(np.clip(P[..., 1] / np.maximum(r, 1e-6), -1, 1))
        row = el / 0.26; az = np.arctan2(P[..., 2], P[..., 0])
        rowi = np.floor(row); col = az / 0.42 + 0.5 * (rowi % 2)
        line = np.minimum(np.abs(row - np.round(row)), np.abs(col - np.round(col)) * np.cos(el) * 1.6)
        c = mixc(c, hexc("#8FA9D6"), sstep(0.07, 0.02, line) * sstep(0.3, 1.2, r))
        c = mixc(c, hexc("#7E8FB8"), sstep(0.62, 0.5, np.sqrt((P[..., 1]) ** 2 + P[..., 2] ** 2)) * sstep(2.4, 2.6, P[..., 0]))
        return c
    out["volcano"] = mesh_sdf(igloo_f, igloo_col, (-2.3, -0.2, -2.3), (3.0, 2.3, 2.3), step=0.06)
    # snowy pine tree
    def pine_f(P):
        d = capsule(P, (0, 0, 0), (0, 0.6, 0), 0.13)
        for k, (y, r) in enumerate([(0.45, 0.85), (1.15, 0.68), (1.8, 0.48)]):
            cone = round_cone(P, (0, y, 0), (0, y + 0.95 - 0.12 * k, 0), r, 0.06)
            d = smin(d, cone, 0.08)
        return d
    def pine_col(P, N):
        c = np.where((P[..., 1] < 0.45)[..., None], hexc("#B98A6A"), hexc("#7FBFA4"))
        snow = sstep(0.55, 0.85, N[..., 1]) * (P[..., 1] > 0.5)
        return mixc(c, hexc("#F7FAFF"), snow)
    out["tree"] = mesh_sdf(pine_f, pine_col, (-1.1, -0.1, -1.1), (1.1, 3.0, 1.1), step=0.06)
    out["smoke"] = blob_mesh([((0, 0, 0), 0.5)], hexc("#FFFFFF"), step=0.1)
    # snow tuft (replaces flowers): three soft lumps
    out["flower"] = blob_mesh([((0, 0.02, 0), (0.18, 0.09, 0.15)), ((0.13, 0.0, 0.06), (0.11, 0.07, 0.1)), ((-0.1, 0.0, -0.07), (0.1, 0.06, 0.09))],
                              hexc("#FFFFFF"), step=0.03, k=0.06)
    out["rock"] = mesh_sdf(lambda P: length(np.maximum(np.abs(P - V(0, 0.18, 0)) - V(0.2, 0.14, 0.18), 0)) - 0.07, solid(hexc("#BFE0F5")), (-0.5, -0.1, -0.5), (0.5, 0.5, 0.5), step=0.03)
    out["sun"] = blob_mesh([((0, 0, 0), (1.0, 1.0, 0.35))] + [((1.45 * np.cos(a), 1.45 * np.sin(a), 0), (0.22, 0.22, 0.18)) for a in np.linspace(0, 2 * np.pi, 11)[:-1]],
                           hexc("#FFE07A"), step=0.08, k=0.12)
    out["ball"] = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(np.ones(3)), (-1.2,) * 3, (1.2,) * 3, step=0.12, ao=False)
    out["disc"] = mesh_sdf(lambda P: ellipsoid(P, (0, 0, 0), (1.0, 0.25, 1.0)), solid(np.ones(3)), (-1.2,) * 3, (1.2,) * 3, step=0.25, ao=False)
    out["ground"] = ground_mesh()
    return out

PENGUINS = [("pink", False, True), ("mint", True, False), ("sky", False, False), ("lavender", True, False), ("peach", False, True)]
SHAPES = ["circle", "square", "triangle", "star", "heart"]

if __name__ == "__main__":
    import pickle, time
    t0 = time.time()
    data = dict(dinos=[make_penguin(c, tu, bo) for c, tu, bo in PENGUINS])
    print("penguins", round(time.time() - t0, 1))
    data["eye_w"], data["eye_p"] = eye_meshes()
    data["shapes"] = {i: shape_meshes(n) for i, n in enumerate(SHAPES)}
    data["scene"] = scenery()
    tris = sum(p["mesh"]["f"].shape[0] for d in data["dinos"] for p in d["parts"].values() if "mesh" in p)
    print("penguin tris", tris, "total time", round(time.time() - t0, 1))
    pickle.dump(data, open("out/meshes.pkl", "wb"))
