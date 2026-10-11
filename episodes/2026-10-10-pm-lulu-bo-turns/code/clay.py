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


