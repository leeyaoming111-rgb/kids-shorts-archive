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
                ao=a.astype(np.float32), f=faces.astype(np.uint32), sdf=(vol.astype(np.float16), lo, step))

def solid(c):
    return lambda P, N: np.broadcast_to(c, P.shape).copy()


CREAM = hexc("#FFF3E2"); PLUM = hexc("#4A2B45"); BLUSH = hexc("#FF8FA8")
EYE_W = hexc("#FFFFFF"); EYE_P = hexc("#2A1E2C")

# ---------------- Tumble the fox cub (faces +z, y up) ----------------
FOX = hexc("#F2A877"); FOX_DK = hexc("#C98663"); SOCK = hexc("#A9806F")
def make_fox():
    parts = {}
    body_c, body_r = (0.0, 0.66, 0.0), (0.42, 0.5, 0.37)
    def body_f(P):
        return ellipsoid(P, body_c, body_r)
    def body_col(P, N):
        q = ((P[..., 0]) / 0.26) ** 2 + ((P[..., 1] - 0.6) / 0.36) ** 2
        return mixc(np.broadcast_to(FOX, P.shape).copy(), CREAM, sstep(1.1, 0.85, q) * sstep(0.0, 0.18, P[..., 2]))
    parts["body"] = dict(mesh=mesh_sdf(body_f, body_col, (-0.7, 0.0, -0.65), (0.7, 1.35, 0.65)), pivot=body_c)
    for li, s in enumerate((1, -1)):
        def leg_f(P, s=s):
            d = capsule(P, (0.18 * s, 0.34, 0.0), (0.19 * s, 0.12, 0.02), 0.11)
            d = smin(d, ellipsoid(P, (0.19 * s, 0.07, 0.08), (0.13, 0.08, 0.18)), 0.05)
            return smax(d, -P[..., 1], 0.015)
        parts[f"leg{li}"] = dict(mesh=mesh_sdf(leg_f, solid(SOCK), (0.19 * s - 0.35, -0.02, -0.3), (0.19 * s + 0.35, 0.55, 0.4)), pivot=(0.18 * s, 0.34, 0.0))
    for ai, s in enumerate((1, -1)):
        def arm_f(P, s=s):
            d = capsule(P, (0.33 * s, 0.9, 0.0), (0.47 * s, 0.56, 0.05), 0.085)
            return smin(d, sphere(P, (0.49 * s, 0.5, 0.06), 0.1), 0.04)
        def arm_col(P, N, s=s):
            return mixc(np.broadcast_to(FOX, P.shape).copy(), SOCK, sstep(0.72, 0.62, P[..., 1]))
        parts[f"arm{ai}"] = dict(mesh=mesh_sdf(arm_f, arm_col, (0.4 * s - 0.4, 0.25, -0.3), (0.4 * s + 0.4, 1.15, 0.35)), pivot=(0.33 * s, 0.9, 0.0),
                                hand=(0.5 * s, 0.48, 0.07))
    head_c, head_r = (0.0, 1.45, 0.0), (0.5, 0.43, 0.43)
    snout_c, snout_r = (0.0, 1.33, 0.36), (0.18, 0.13, 0.17)
    nose = (0.0, 1.37, 0.53)
    def head_f(P):
        d = ellipsoid(P, head_c, head_r)
        d = smin(d, ellipsoid(P, snout_c, snout_r), 0.08)
        d = smin(d, sphere(P, nose, 0.06), 0.02)
        for s in (1, -1):
            d = smin(d, round_cone(P, (0.27 * s, 1.72, -0.02), (0.44 * s, 2.15, -0.06), 0.17, 0.035), 0.06)
            d = smin(d, ellipsoid(P, (0.38 * s, 1.32, 0.08), (0.14, 0.11, 0.12)), 0.08)       # cheek fluff
        q_y = P[..., 1] - 1.255; q_x = P[..., 0]
        ring = np.abs(np.sqrt(q_y ** 2 + q_x ** 2) - 0.07); ang = np.arctan2(q_y, q_x)
        arcd = np.where((ang < -0.4) & (ang > -2.75), ring, 9.0)
        groove = np.maximum(arcd - 0.016, np.maximum(-(P[..., 2] - 0.38), -(d + 0.03)))
        return np.maximum(d, -groove)
    def head_col(P, N):
        c = np.broadcast_to(FOX, P.shape).copy()
        muzzle = sstep(0.55, 0.3, length((P - V(0, 1.27, 0.3)) * V(1.0, 1.4, 1.0))) * sstep(0.1, 0.25, P[..., 2])
        c = mixc(c, CREAM, muzzle)
        for s in (1, -1):
            c = mixc(c, CREAM, sstep(0.12, 0.05, length((P - V(0.38 * s, 1.30, 0.12)) * V(1, 1, 0.8))))
            inner = sstep(0.1, 0.05, length((P - V(0.36 * s, 1.92, 0.04)) * V(1.3, 0.55, 1))) * sstep(-0.05, 0.05, P[..., 2])
            c = mixc(c, hexc("#FBD9C4"), inner)
            c = mixc(c, FOX_DK, sstep(2.0, 2.1, P[..., 1]))
            c = mixc(c, BLUSH, 0.7 * sstep(0.085, 0.035, length(P - V(0.27 * s, 1.36, 0.35))))
        c = mixc(c, PLUM, sstep(0.075, 0.06, length(P - V(*nose))))
        q_y = P[..., 1] - 1.255; q_x = P[..., 0]
        ring = np.abs(np.sqrt(q_y ** 2 + q_x ** 2) - 0.07); ang = np.arctan2(q_y, q_x)
        arcd = np.where((ang < -0.4) & (ang > -2.75), ring, 9.0)
        return mixc(c, PLUM, sstep(0.03, 0.018, arcd) * (P[..., 2] > 0.38))
    parts["head"] = dict(mesh=mesh_sdf(head_f, head_col, (-0.75, 0.9, -0.6), (0.75, 2.3, 0.75), step=0.018), pivot=(0.0, 1.1, 0.0))
    parts["eyes"] = dict(centers=[(0.17, 1.52, 0.37), (-0.17, 1.52, 0.37)], r=0.085, pivot=(0.0, 1.1, 0.0))
    parts["mouth"] = dict(c=(0.0, 1.235, 0.43), pivot=(0.0, 1.1, 0.0))
    pts = [(0.0, 0.42, -0.3), (0.12, 0.42, -0.62), (0.26, 0.7, -0.82), (0.3, 1.05, -0.84)]
    rad = [0.1, 0.19, 0.22, 0.15]
    def tail_f(P):
        d = None
        for i in range(3):
            s_ = round_cone(P, pts[i], pts[i + 1], rad[i], rad[i + 1])
            d = s_ if d is None else smin(d, s_, 0.08)
        return smin(d, sphere(P, (0.3, 1.18, -0.82), 0.1), 0.08)
    def tail_col(P, N):
        return mixc(np.broadcast_to(FOX, P.shape).copy(), CREAM, sstep(0.88, 1.0, P[..., 1]))
    parts["tail"] = dict(mesh=mesh_sdf(tail_f, tail_col, (-0.4, 0.15, -1.2), (0.7, 1.45, -0.05)), pivot=pts[0])
    return dict(parts=parts, head_top=2.18)

# ---------------- Pip the bird (faces +z), about 0.4 tall ----------------
PIPC = hexc("#8EC5F0"); PIP_DK = hexc("#6AA6DB")
def make_pip():
    parts = {}
    def body_f(P):
        d = ellipsoid(P, (0, 0.17, -0.02), (0.15, 0.15, 0.17))
        d = smin(d, sphere(P, (0, 0.33, 0.04), 0.12), 0.06)
        d = smin(d, round_cone(P, (0, 0.33, 0.15), (0, 0.31, 0.25), 0.04, 0.01), 0.01)
        d = smin(d, round_cone(P, (0, 0.14, -0.16), (0, 0.2, -0.3), 0.06, 0.03), 0.03)
        for s in (1, -1):
            d = smin(d, capsule(P, (0.05 * s, 0.03, 0.0), (0.05 * s, -0.04, 0.03), 0.018), 0.01)
        d = smin(d, round_cone(P, (0, 0.44, 0.02), (0.0, 0.5, -0.04), 0.025, 0.012), 0.015)
        return d
    def body_col(P, N):
        c = np.broadcast_to(PIPC, P.shape).copy()
        c = mixc(c, CREAM, sstep(0.0, 0.08, P[..., 2]) * sstep(0.28, 0.2, P[..., 1]) * sstep(0.02, 0.08, P[..., 1]))
        c = mixc(c, hexc("#FFB347"), sstep(0.15, 0.17, P[..., 2]) * sstep(0.26, 0.28, P[..., 1]) * sstep(0.37, 0.35, P[..., 1]))
        c = mixc(c, hexc("#FFB347"), sstep(0.06, 0.0, P[..., 1]))
        for s in (1, -1):
            c = mixc(c, BLUSH, 0.7 * sstep(0.035, 0.015, length(P - V(0.08 * s, 0.3, 0.11))))
        return c
    parts["body"] = dict(mesh=mesh_sdf(body_f, body_col, (-0.3, -0.12, -0.45), (0.3, 0.6, 0.4), step=0.008), pivot=(0, 0.17, 0))
    for wi, s in enumerate((1, -1)):
        def wing_f(P, s=s):
            Q = rot_z(P, -0.3 * s, (0.13 * s, 0.22, 0))
            return ellipsoid(Q, (0.2 * s, 0.18, -0.02), (0.1, 0.035, 0.1))
        parts[f"wing{wi}"] = dict(mesh=mesh_sdf(wing_f, solid(PIP_DK), (0.2 * s - 0.2, 0.0, -0.2), (0.2 * s + 0.2, 0.35, 0.2), step=0.008), pivot=(0.13 * s, 0.22, 0))
    parts["eyes"] = dict(centers=[(0.055, 0.37, 0.12), (-0.055, 0.37, 0.12)], r=0.028, pivot=(0, 0.17, 0))
    return dict(parts=parts)

# ---------------- props ----------------
def props():
    out = {}
    HAT_T, HAT_RX, HAT_S = (0.0, 1.86, -0.02), -0.12, 0.95
    def hat_f(P):
        d = ellipsoid(P, (0, 0.0, 0), (0.55, 0.035, 0.55))
        d = smin(d, ellipsoid(P, (0, 0.1, 0), (0.3, 0.2, 0.3)), 0.06)
        return d
    def hat_c(P, N):
        c = np.broadcast_to(hexc("#F2D58A"), P.shape).copy()
        return mixc(c, hexc("#F58FB0"), sstep(0.035, 0.06, P[..., 1]) * sstep(0.15, 0.12, P[..., 1]))
    out["hat"] = mesh_sdf(hat_f, hat_c, (-0.7, -0.15, -0.7), (0.7, 0.4, 0.7), step=0.02)
    def umb_f(P):
        r = length(P - V(0, 0, 0))
        shell = np.abs(r - 0.85) - 0.03
        a = np.arctan2(P[..., 2], P[..., 0])
        cut = P[..., 1] - (0.32 + 0.05 * np.cos(a * 8))
        d = smax(shell, -cut, 0.02)
        d = smin(d, capsule(P, (0, 0.9, 0), (0, -0.2, 0), 0.03), 0.01)
        d = smin(d, sphere(P, (0, 0.9, 0), 0.05), 0.01)
        return d
    def umb_c(P, N):
        a = np.arctan2(P[..., 2], P[..., 0]); stripe = (np.floor((a + np.pi) / (np.pi / 4)) % 2)
        c = mixc(np.broadcast_to(hexc("#FFC23D"), P.shape), hexc("#FFE08A"), stripe * 0.0 + stripe)
        return np.where((length(P[..., [0, 2]]) < 0.05)[..., None], hexc("#9A6B4F"), c)
    out["umbrella"] = mesh_sdf(umb_f, umb_c, (-1.0, -0.3, -1.0), (1.0, 1.0, 1.0), step=0.022)
    def kite_f(P):
        d = np.abs(P[..., 0]) / 0.42 + np.abs(P[..., 1]) / 0.58 - 1.0
        d = np.maximum(d * 0.25, np.abs(P[..., 2]) - 0.03) - 0.02
        return d
    def kite_c(P, N):
        q = (P[..., 0] > 0) ^ (P[..., 1] > 0)
        return np.where(q[..., None], hexc("#FF8FA8"), hexc("#7FD1C7"))
    out["kite"] = mesh_sdf(kite_f, kite_c, (-0.6, -0.8, -0.15), (0.6, 0.8, 0.15), step=0.015, ao=False)
    out["ball"] = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(np.ones(3)), (-1.2,) * 3, (1.2,) * 3, step=0.12, ao=False)
    out["stick"] = mesh_sdf(lambda P: capsule(P, (0, 0, 0), (0, 1, 0), 0.05), solid(np.ones(3)), (-0.1, -0.1, -0.1), (0.1, 1.1, 0.1), step=0.02, ao=False)
    out["mouth"] = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(hexc("#7A2E45")), (-1.2,) * 3, (1.2,) * 3, step=0.2, ao=False)
    return out

# ---------------- set: cottage garden ----------------
def ground_h(x, z):
    return 0.06 * np.sin(x * 0.7 + 0.4) * np.cos(z * 0.5) + 0.25 * np.exp(-((x + 2.8) ** 2 + (z + 3.2) ** 2) / 6.0) - 0.02 * np.exp(-((x - 0.0) ** 2 + (z - 0.9) ** 2) / 0.6)

def ground_mesh():
    nx, nz = 170, 150
    xs = np.linspace(-16, 16, nx); zs = np.linspace(-22, 12, nz)
    X, Z = np.meshgrid(xs, zs, indexing="ij"); Y = ground_h(X, Z)
    P = np.stack([X, Y, Z], -1); e = 0.01
    dx = (ground_h(X + e, Z) - ground_h(X - e, Z)) / (2 * e); dz = (ground_h(X, Z + e) - ground_h(X, Z - e)) / (2 * e)
    N = np.stack([-dx, np.ones_like(dx), -dz], -1); N /= np.linalg.norm(N, axis=-1, keepdims=True)
    g1, g2, g3 = hexc("#9CD07E"), hexc("#86C26F"), hexc("#BFE29A")
    n1 = 0.5 + 0.5 * np.sin(X * 1.3 + np.sin(Z * 1.1) * 2) * np.sin(Z * 1.6 + np.sin(X * 0.6) * 1.5)
    C = mixc(np.broadcast_to(g1, P.shape), g2, n1 * 0.7)
    C = mixc(C, g3, sstep(-6, -14, Z) * 0.6)
    idx = np.arange(nx * nz).reshape(nx, nz)
    a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
    faces = np.concatenate([np.stack([a, d, c], -1).reshape(-1, 3), np.stack([a, c, b], -1).reshape(-1, 3)])
    return dict(v=P.reshape(-1, 3).astype(np.float32), n=N.reshape(-1, 3).astype(np.float32),
                c=C.reshape(-1, 3).astype(np.float32), ao=np.ones(nx * nz, np.float32), f=faces.astype(np.uint32))

def cottage():
    def f(P):
        r = length(P[..., [0, 2]])
        wall = np.maximum(r - 1.35, np.maximum(-P[..., 1], P[..., 1] - 1.7))
        wall = wall - 0.03
        roof = np.maximum(r * 0.95 + (P[..., 1] - 1.55) * 0.62 - 1.55, -(P[..., 1] - 1.45))
        d = smin(wall, roof - 0.04, 0.08)
        d = smin(d, round_cone(P, (0, 3.6, 0), (0.05, 3.85, 0), 0.08, 0.05), 0.08)
        door = length(np.maximum(np.abs(P - V(0, 0.55, 1.35)) - V(0.32, 0.55, 0.1), 0)) - 0.12
        d = smax(d, -door, 0.03) if False else d
        d = smin(d, ellipsoid(P, (0, 0.62, 1.33), (0.42, 0.66, 0.08)), 0.02)          # door slab
        d = smin(d, ellipsoid(P, (-0.78, 1.05, 1.1), (0.28, 0.28, 0.07)), 0.02)        # round window
        d = smin(d, length(np.maximum(np.abs(P - V(-0.78, 0.68, 1.18)) - V(0.34, 0.07, 0.1), 0)) - 0.04, 0.02)   # window box
        return d
    def c(P, N):
        col = np.broadcast_to(hexc("#F7E6CF"), P.shape).copy()
        col = mixc(col, hexc("#B9A3E3"), sstep(1.5, 1.62, P[..., 1]))
        col = mixc(col, hexc("#9A84D3"), sstep(1.5, 1.62, P[..., 1]) * (0.5 + 0.5 * np.sin(P[..., 1] * 14)) * 0.35)
        door = sstep(0.06, 0.0, length((P - V(0, 0.62, 1.4)) * V(1 / 0.42, 1 / 0.66, 4)) - 1.0)
        col = mixc(col, hexc("#7CC49A"), door)
        col = mixc(col, hexc("#F2C94C"), sstep(0.05, 0.03, length(P - V(0.24, 0.6, 1.42))))
        win = sstep(0.04, 0.0, length((P - V(-0.78, 1.05, 1.17)) * V(1 / 0.28, 1 / 0.28, 4)) - 1.0)
        col = mixc(col, hexc("#BFE3F7"), win)
        col = mixc(col, hexc("#7CC49A"), sstep(0.05, 0.02, np.abs(length((P[..., [0, 1]] - np.array([-0.78, 1.05]))) - 0.26)) * (P[..., 2] > 1.1))
        box = (np.abs(P[..., 1] - 0.68) < 0.12) & (np.abs(P[..., 0] + 0.78) < 0.4) & (P[..., 2] > 1.1)
        col[box] = hexc("#C99A7A")
        col = mixc(col, hexc("#9A84D3"), sstep(3.5, 3.6, P[..., 1]))
        return col
    return mesh_sdf(f, c, (-1.8, -0.2, -1.8), (1.8, 4.0, 1.8), step=0.04)

def scenery():
    out = {}
    out["ground"] = ground_mesh()
    out["cottage"] = cottage()
    out["cloud"] = blob_mesh([((0, 0, 0), (1.1, 0.7, 0.7)), ((1.1, -0.15, 0), (0.8, 0.55, 0.6)), ((-1.1, -0.2, 0), (0.75, 0.5, 0.55)),
                              ((0.4, 0.45, 0.1), (0.7, 0.6, 0.5))], hexc("#FFFFFF"), step=0.09)
    out["sun"] = blob_mesh([((0, 0, 0), (1.0, 1.0, 0.35))] + [((1.45 * np.cos(a), 1.45 * np.sin(a), 0), (0.22, 0.22, 0.18)) for a in np.linspace(0, 2 * np.pi, 11)[:-1]],
                           hexc("#FFD45A"), step=0.08, k=0.12)
    def tree_col(P, N):
        return np.where((P[..., 1] < 1.3)[..., None], hexc("#B98A6A"), mixc(np.broadcast_to(hexc("#6FBF7A"), P.shape), hexc("#A5DC8C"), sstep(0, 0.8, N[..., 1])))
    out["tree"] = blob_mesh([((0, 0.7, 0), (0.2, 0.8, 0.2)), ((0, 2.0, 0), (0.85, 0.75, 0.8)), ((0.55, 1.7, 0.2), (0.55, 0.5, 0.5)),
                             ((-0.55, 1.75, -0.1), (0.55, 0.5, 0.5)), ((0.05, 2.55, 0), (0.55, 0.45, 0.5))], tree_col, step=0.07, k=0.12)
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
    out["stone"] = blob_mesh([((0, 0.0, 0), (0.32, 0.07, 0.26))], hexc("#D8D0E2"), step=0.03, k=0.05)
    out["leaf"] = mesh_sdf(lambda P: ellipsoid(P, (0, 0, 0), (0.12, 0.015, 0.07)), solid(np.ones(3)), (-0.2, -0.05, -0.12), (0.2, 0.05, 0.12), step=0.01, ao=False)
    def rb_f(P):
        rr = length(P[..., [0, 1]])
        a = np.abs(rr - 4.1) - 0.62; b = np.abs(P[..., 2]) - 0.08
        d = np.sqrt(np.maximum(a, 0) ** 2 + np.maximum(b, 0) ** 2) + np.minimum(np.maximum(a, b), 0) - 0.05
        return np.maximum(d, -P[..., 1])
    RB = [hexc(c) for c in ("#FF4D5E", "#FF9A2E", "#FFD93B", "#42C96B", "#3D8BFF", "#9B5CF0")]
    def rb_c(P, N):
        rr = length(P[..., [0, 1]]); i = np.clip(((4.72 - rr) / 1.24 * 6).astype(int), 0, 5)
        return np.stack(RB)[i]
    out["rainbow"] = mesh_sdf(rb_f, rb_c, (-4.9, -0.1, -0.25), (4.9, 4.9, 0.25), step=0.045, ao=False)
    out["puddle"] = mesh_sdf(lambda P: ellipsoid(P, (0, 0, 0), (1.0, 0.03, 0.7)), solid(hexc("#9CC8EE")), (-1.2, -0.1, -0.9), (1.2, 0.1, 0.9), step=0.03, ao=False)
    return out

def eye_meshes():
    w = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(EYE_W), (-1.2,) * 3, (1.2,) * 3, step=0.2, ao=False)
    p = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(EYE_P), (-1.2,) * 3, (1.2,) * 3, step=0.22, ao=False)
    return w, p

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


if __name__ == "__main__":
    import pickle, time
    t0 = time.time()
    data = dict(fox=make_fox(), pip=make_pip(), props=props(), scene=scenery())
    data["eye_w"], data["eye_p"] = eye_meshes()
    store = {}
    def walk(o, path):
        if isinstance(o, dict):
            if "v" in o and "f" in o:
                o["name"] = path
                if "sdf" in o: store[path] = o.pop("sdf")
                return
            for k, v in o.items(): walk(v, f"{path}/{k}" if path else str(k))
    walk(data, "")
    pickle.dump(store, open("out/sdf.pkl", "wb"))
    print("built in", round(time.time() - t0, 1), "s")
    pickle.dump(data, open("out/meshes.pkl", "wb"))

