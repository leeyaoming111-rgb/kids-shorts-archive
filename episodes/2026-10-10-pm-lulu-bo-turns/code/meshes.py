"""Clay models for 'My Turn, Your Turn!': Lulu the frog, Bo the turtle, the golden-hour lily pond set.
SDF primitives and the marching-cubes mesher come from the engine toolkit (clay.py)."""
import numpy as np
from clay import *

CREAM = hexc("#FFF4DC"); PLUM = hexc("#3B2340"); BLUSH = hexc("#FF8FA3")
EYE_W = hexc("#FFFFFF"); EYE_P = hexc("#24182A")

# ---------------- world layout (shared with render.py) ----------------
POND_C = (-1.4, -3.4); POND_R = (3.6, 2.6)
ROCK_C = (1.95, -1.9); ROCK_R = (1.5, 1.6, 1.1); ROCK_TOP = 1.25
# ride curve: where a rider's base sits while sliding (cubic bezier)
RIDE = np.array([(1.05, 1.28, -1.85), (0.35, 1.22, -1.75), (-0.25, 0.42, -2.05), (-0.95, 0.14, -2.65)])
TUBE_R = 0.36
STEPS = [(3.45, 0.40, -1.45), (3.28, 0.84, -1.55)]       # stone slab centres on the rock's right side

def pond_q(x, z):
    return ((x - POND_C[0]) / POND_R[0]) ** 2 + ((z - POND_C[1]) / POND_R[1]) ** 2

def ground_h(x, z):
    q = pond_q(x, z)
    h = 0.12 + 0.05 * np.sin(x * 0.8 + 0.3) * np.cos(z * 0.6) - 0.75 * sstep(1.18, 0.86, q)
    h = h + 1.4 * sstep(-9.0, -15.0, z) * (0.6 + 0.4 * np.sin(x * 0.35))
    return h

def bez(s):
    s = np.asarray(s, float)[..., None]; P = RIDE
    return ((1 - s) ** 3) * P[0] + 3 * ((1 - s) ** 2) * s * P[1] + 3 * (1 - s) * s * s * P[2] + s ** 3 * P[3]
def bez_d(s):
    s = np.asarray(s, float)[..., None]; P = RIDE
    return 3 * (1 - s) ** 2 * (P[1] - P[0]) + 6 * (1 - s) * s * (P[2] - P[1]) + 3 * s * s * (P[3] - P[2])
def ride(s):
    """rider base position and unit tangent at curve parameter s"""
    p = bez(s); d = bez_d(s); return p, d / np.linalg.norm(d, axis=-1, keepdims=True)

# ---------------- Lulu the frog (faces +z, y up), about 1.3 tall ----------------
LIME = hexc("#7BD84A"); LIME_DK = hexc("#4FAE2E"); BELLY = hexc("#F3F7B8")
def make_frog():
    parts = {}
    def body_f(P):
        d = ellipsoid(P, (0, 0.42, -0.02), (0.44, 0.40, 0.40))
        d = smin(d, ellipsoid(P, (0, 0.80, 0.05), (0.47, 0.32, 0.40)), 0.16)
        for s in (1, -1):
            d = smin(d, sphere(P, (0.21 * s, 1.06, 0.12), 0.16), 0.08)
        # wide smile groove
        x = P[..., 0]; yc = 0.625 + 0.8 * x ** 2
        groove = np.sqrt((P[..., 1] - yc) ** 2 + 0.0 * x) - 0.016
        groove = np.maximum(groove, np.abs(x) - 0.22)
        groove = np.maximum(groove, -(P[..., 2] - 0.3))
        d = np.maximum(d, -groove)
        # flower behind the right eye bump
        fc = np.array([0.36, 1.12, -0.04])
        for i in range(5):
            a = i * 2 * np.pi / 5
            d = smin(d, ellipsoid(P, tuple(fc + np.array([0.075 * np.cos(a), 0.075 * np.sin(a), 0.02])), (0.065, 0.065, 0.03)), 0.015)
        return d
    def body_col(P, N):
        c = np.broadcast_to(LIME, P.shape).copy()
        belly = sstep(1.0, 0.7, length((P - V(0, 0.38, 0.32)) * V(1 / 0.3, 1 / 0.34, 1 / 0.3))) * sstep(0.05, 0.2, P[..., 2])
        c = mixc(c, BELLY, belly)
        # back spots
        for (x, y, z, r) in [(0.18, 0.62, -0.32, 0.07), (-0.2, 0.5, -0.34, 0.06), (0.0, 0.85, -0.3, 0.06), (0.32, 0.35, -0.25, 0.05), (-0.3, 0.8, -0.2, 0.05)]:
            c = mixc(c, LIME_DK, sstep(r, r - 0.02, length(P - V(x, y, z))))
        for s in (1, -1):
            c = mixc(c, BLUSH, 0.75 * sstep(0.09, 0.04, length(P - V(0.3 * s, 0.76, 0.33))))
        x = P[..., 0]; yc = 0.625 + 0.8 * x ** 2
        c = mixc(c, PLUM, sstep(0.017, 0.008, np.abs(P[..., 1] - yc)) * (np.abs(x) < 0.22) * (P[..., 2] > 0.25))
        fl = sstep(0.12, 0.10, length(P - V(0.36, 1.12, -0.02)))
        c = mixc(c, hexc("#FF7FB0"), fl)
        c = mixc(c, hexc("#FFD43B"), sstep(0.04, 0.025, length(P - V(0.36, 1.12, 0.0))))
        return c
    parts["body"] = dict(mesh=mesh_sdf(body_f, body_col, (-0.65, 0.0, -0.6), (0.65, 1.38, 0.6), step=0.017), pivot=(0, 0.45, 0))
    for li, s in enumerate((1, -1)):
        def leg_f(P, s=s):
            Q = rot_y(P, 0.35 * s, (0.36 * s, 0.2, -0.05))
            d = ellipsoid(Q, (0.36 * s, 0.22, -0.06), (0.17, 0.16, 0.3))
            d = smin(d, ellipsoid(P, (0.43 * s, 0.04, 0.2), (0.15, 0.045, 0.22)), 0.06)
            for k in (-1, 0, 1):
                d = smin(d, sphere(P, (0.43 * s + 0.09 * k, 0.04, 0.42 - 0.03 * abs(k)), 0.045), 0.02)
            return smax(d, -P[..., 1] - 0.005, 0.01)
        parts[f"leg{li}"] = dict(mesh=mesh_sdf(leg_f, solid(LIME), (0.4 * s - 0.4, -0.05, -0.45), (0.4 * s + 0.4, 0.45, 0.55), step=0.016), pivot=(0.32 * s, 0.3, -0.1))
    for ai, s in enumerate((1, -1)):
        def arm_f(P, s=s):
            d = capsule(P, (0.3 * s, 0.55, 0.22), (0.33 * s, 0.1, 0.33), 0.07)
            d = smin(d, ellipsoid(P, (0.34 * s, 0.03, 0.38), (0.09, 0.035, 0.1)), 0.04)
            return smax(d, -P[..., 1] - 0.005, 0.01)
        parts[f"arm{ai}"] = dict(mesh=mesh_sdf(arm_f, solid(LIME), (0.33 * s - 0.25, -0.05, 0.05), (0.33 * s + 0.25, 0.7, 0.55), step=0.014),
                                 pivot=(0.3 * s, 0.58, 0.2), hand=(0.34 * s, 0.05, 0.38))
    parts["eyes"] = dict(centers=[(0.21, 1.09, 0.235), (-0.21, 1.09, 0.235)], r=0.12, pivot=(0, 0.45, 0))
    parts["mouth"] = dict(c=(0.0, 0.64, 0.43), pivot=(0, 0.45, 0))
    return dict(parts=parts, top=1.32)

# ---------------- Bo the turtle (faces +z), about 0.85 tall ----------------
SKIN = hexc("#8ED8BE"); SHELL = hexc("#F49A46"); PLATE = hexc("#FFC266"); SHELL_DK = hexc("#C46A2C"); RIM = hexc("#F2D28C")
def make_turtle():
    parts = {}
    def shell_f(P):
        d = ellipsoid(P, (0, 0.40, -0.02), (0.56, 0.40, 0.62))
        d = smax(d, -(P[..., 1] - 0.2), 0.03)
        d = smin(d, ellipsoid(P, (0, 0.24, -0.02), (0.63, 0.085, 0.69)), 0.05)
        d = smin(d, ellipsoid(P, (0, 0.19, -0.02), (0.5, 0.08, 0.56)), 0.03)
        return d
    def shell_col(P, N):
        c = np.broadcast_to(SHELL, P.shape).copy()
        # plates: hex-ish cells from a projected grid
        u = P[..., 0] / 0.2; v = P[..., 2] / 0.2 + 0.5 * (np.floor(u) % 2)
        cu = (np.floor(u) + 0.5) * 0.2; cv = (np.floor(v) + 0.5 - 0.5 * (np.floor(u) % 2)) * 0.2
        dcell = np.maximum(np.abs(P[..., 0] - cu) / 0.1, np.abs(P[..., 2] - cv) / 0.1)
        c = mixc(c, PLATE, sstep(0.75, 0.55, dcell) * 0.85)
        c = mixc(c, SHELL_DK, sstep(0.9, 1.0, dcell) * 0.6)
        c = mixc(c, RIM, sstep(0.3, 0.26, P[..., 1]))
        return c
    parts["shell"] = dict(mesh=mesh_sdf(shell_f, shell_col, (-0.8, 0.0, -0.85), (0.8, 0.9, 0.85), step=0.018), pivot=(0, 0.3, 0))
    def head_f(P):
        d = capsule(P, (0, 0.32, 0.42), (0, 0.52, 0.72), 0.13)
        d = smin(d, ellipsoid(P, (0, 0.62, 0.84), (0.25, 0.22, 0.24)), 0.08)
        x = P[..., 0]; yc = 0.535 + 1.0 * x ** 2
        groove = np.maximum(np.abs(P[..., 1] - yc) - 0.012, np.maximum(np.abs(x) - 0.13, -(P[..., 2] - 0.95)))
        return np.maximum(d, -groove)
    def head_col(P, N):
        c = np.broadcast_to(SKIN, P.shape).copy()
        for s in (1, -1):
            c = mixc(c, BLUSH, 0.75 * sstep(0.065, 0.025, length(P - V(0.17 * s, 0.56, 0.97))))
        x = P[..., 0]; yc = 0.535 + 1.0 * x ** 2
        c = mixc(c, PLUM, sstep(0.018, 0.009, np.abs(P[..., 1] - yc)) * (np.abs(x) < 0.13) * (P[..., 2] > 0.95))
        c = mixc(c, hexc("#6CC3A6"), sstep(0.8, 0.86, P[..., 1]) * 0.5)
        return c
    parts["head"] = dict(mesh=mesh_sdf(head_f, head_col, (-0.35, 0.15, 0.2), (0.35, 0.9, 1.15), step=0.014), pivot=(0, 0.38, 0.45))
    parts["eyes"] = dict(centers=[(0.105, 0.69, 1.0), (-0.105, 0.69, 1.0)], r=0.075, pivot=(0, 0.38, 0.45))
    parts["mouth"] = dict(c=(0.0, 0.55, 1.05), pivot=(0, 0.38, 0.45))
    for li, (sx, sz) in enumerate([(1, 1), (-1, 1), (1, -1), (-1, -1)]):
        def leg_f(P, sx=sx, sz=sz):
            d = capsule(P, (0.4 * sx, 0.25, 0.38 * sz), (0.44 * sx, 0.06, 0.42 * sz), 0.11)
            d = smin(d, ellipsoid(P, (0.45 * sx, 0.04, 0.45 * sz + 0.04), (0.13, 0.05, 0.14)), 0.04)
            return smax(d, -P[..., 1] - 0.005, 0.01)
        parts[f"leg{li}"] = dict(mesh=mesh_sdf(leg_f, solid(SKIN), (0.42 * sx - 0.25, -0.05, 0.4 * sz - 0.3), (0.42 * sx + 0.25, 0.42, 0.4 * sz + 0.3), step=0.016),
                                 pivot=(0.4 * sx, 0.25, 0.38 * sz))
    def tail_f(P): return round_cone(P, (0, 0.2, -0.6), (0, 0.16, -0.8), 0.07, 0.025)
    parts["tail"] = dict(mesh=mesh_sdf(tail_f, solid(SKIN), (-0.15, 0.05, -0.95), (0.15, 0.32, -0.45), step=0.014), pivot=(0, 0.2, -0.6))
    return dict(parts=parts, top=0.92)

# ---------------- props ----------------
def star_sdf(P, r_out=1.0, r_in=0.48, th=0.22):
    a = np.arctan2(P[..., 0], P[..., 1]); r = np.sqrt(P[..., 0] ** 2 + P[..., 1] ** 2)
    seg = 2 * np.pi / 5; a2 = np.abs(((a + seg / 2) % seg) - seg / 2)
    q = np.stack([r * np.cos(a2), r * np.sin(a2)], -1)
    A = np.array([r_out, 0.0]); B = np.array([r_in * np.cos(seg / 2), r_in * np.sin(seg / 2)])
    pa = q - A; ba = B - A; h = np.clip((pa @ ba) / (ba @ ba), 0, 1)
    d2 = np.sqrt(np.sum((pa - h[..., None] * ba) ** 2, -1))
    inside = (pa[..., 0] * ba[1] - pa[..., 1] * ba[0]) < 0
    d2 = np.where(inside, -d2, d2)
    return np.maximum(d2, np.abs(P[..., 2]) - th) - 0.12
def props():
    out = {}
    out["star"] = mesh_sdf(lambda P: star_sdf(P), lambda P, N: mixc(np.broadcast_to(hexc("#FFD21F"), P.shape), hexc("#FFE98A"), sstep(0.2, 0.5, N[..., 2]) * 0.5),
                           (-1.3, -1.3, -0.5), (1.3, 1.3, 0.5), step=0.04)
    out["ball"] = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(np.ones(3)), (-1.2,) * 3, (1.2,) * 3, step=0.12, ao=False)
    out["ring"] = mesh_sdf(lambda P: length(np.stack([length(P[..., [0, 2]]) - 1.0, P[..., 1]], -1)) - 0.06, solid(np.ones(3)),
                           (-1.2, -0.2, -1.2), (1.2, 0.2, 1.2), step=0.04, ao=False)
    out["stick"] = mesh_sdf(lambda P: capsule(P, (0, 0, 0), (0, 1, 0), 0.05), solid(np.ones(3)), (-0.1, -0.1, -0.1), (0.1, 1.1, 0.1), step=0.02, ao=False)
    out["mouth"] = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(hexc("#6E2343")), (-1.2,) * 3, (1.2,) * 3, step=0.2, ao=False)
    return out

# ---------------- set ----------------
def ground_mesh():
    nx, nz = 190, 170
    xs = np.linspace(-14, 14, nx); zs = np.linspace(-24, 10, nz)
    X, Z = np.meshgrid(xs, zs, indexing="ij"); Y = ground_h(X, Z)
    P = np.stack([X, Y, Z], -1); e = 0.01
    dx = (ground_h(X + e, Z) - ground_h(X - e, Z)) / (2 * e); dz = (ground_h(X, Z + e) - ground_h(X, Z - e)) / (2 * e)
    N = np.stack([-dx, np.ones_like(dx), -dz], -1); N /= np.linalg.norm(N, axis=-1, keepdims=True)
    g1, g2, g3 = hexc("#A8C27A"), hexc("#93B46C"), hexc("#C9C98E")
    n1 = 0.5 + 0.5 * np.sin(X * 1.3 + np.sin(Z * 1.1) * 2) * np.sin(Z * 1.6 + np.sin(X * 0.6) * 1.5)
    C = mixc(np.broadcast_to(g1, P.shape), g2, n1 * 0.7)
    q = pond_q(X, Z)
    C = mixc(C, hexc("#E7CF9E"), sstep(1.35, 1.12, q))          # sandy shore
    C = mixc(C, hexc("#9C8A72"), sstep(1.08, 0.98, q))          # wet mud under the waterline
    C = mixc(C, g3, sstep(-8, -14, Z) * 0.5)
    idx = np.arange(nx * nz).reshape(nx, nz)
    a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
    faces = np.concatenate([np.stack([a, d, c], -1).reshape(-1, 3), np.stack([a, c, b], -1).reshape(-1, 3)])
    return dict(v=P.reshape(-1, 3).astype(np.float32), n=N.reshape(-1, 3).astype(np.float32),
                c=C.reshape(-1, 3).astype(np.float32), ao=np.ones(nx * nz, np.float32), f=faces.astype(np.uint32))

def water_mesh():
    nx, nz = 120, 100
    xs = np.linspace(-6.0, 3.2, nx); zs = np.linspace(-6.8, 0.2, nz)
    X, Z = np.meshgrid(xs, zs, indexing="ij"); Y = np.zeros_like(X)
    P = np.stack([X, Y, Z], -1); N = np.zeros_like(P); N[..., 1] = 1
    C = np.broadcast_to(hexc("#5FB8C4"), P.shape)
    idx = np.arange(nx * nz).reshape(nx, nz)
    a, b, c, d = idx[:-1, :-1], idx[1:, :-1], idx[1:, 1:], idx[:-1, 1:]
    faces = np.concatenate([np.stack([a, d, c], -1).reshape(-1, 3), np.stack([a, c, b], -1).reshape(-1, 3)])
    return dict(v=P.reshape(-1, 3).astype(np.float32), n=N.reshape(-1, 3).astype(np.float32), c=C.reshape(-1, 3).astype(np.float32),
                ao=np.ones(nx * nz, np.float32), f=faces.astype(np.uint32))

def rock():
    cx, cz = ROCK_C
    def f(P):
        d = ellipsoid(P, (cx, 0.0, cz), ROCK_R)
        d = smin(d, ellipsoid(P, (cx - 0.55, 0.0, cz + 0.45), (0.6, 0.55, 0.5)), 0.2)
        d = smax(d, P[..., 1] - ROCK_TOP, 0.12)
        for (x, y, z) in STEPS:
            slab = length(np.maximum(np.abs(P - V(x, y, z)) - V(0.22, 0.03, 0.24), 0)) - 0.04
            d = smin(d, slab, 0.05)
        d = d + 0.015 * np.sin(P[..., 0] * 9) * np.sin(P[..., 2] * 8) * np.sin(P[..., 1] * 7)
        return d
    def c(P, N):
        col = mixc(np.broadcast_to(hexc("#C7B8CC"), P.shape), hexc("#B3A3BC"), sstep(0.3, 0.8, np.sin(P[..., 1] * 5 + P[..., 0] * 3) * 0.5 + 0.5) * 0.6)
        col = mixc(col, hexc("#A3BE79"), sstep(0.8, 0.95, N[..., 1]) * sstep(ROCK_TOP - 0.15, ROCK_TOP - 0.02, P[..., 1]))   # moss cap
        for (x, y, z) in STEPS:
            col = mixc(col, hexc("#E1D6E6"), sstep(0.06, 0.0, length(np.maximum(np.abs(P - V(x, y, z)) - V(0.24, 0.05, 0.26), 0))))
        return col
    return mesh_sdf(f, c, (cx - 2.1, -0.4, cz - 1.4), (cx + 2.0, ROCK_TOP + 0.2, cz + 1.4), step=0.035)

def slide():
    ss = np.linspace(-0.04, 1.03, 80)
    C = bez(ss) + np.array([0, TUBE_R, 0])
    def closest(P):
        best = np.full(P.shape[:-1], 1e9); by = np.zeros(P.shape[:-1]); bs = np.zeros(P.shape[:-1])
        for i in range(len(C) - 1):
            a, b = C[i], C[i + 1]; pa = P - a; ba = b - a
            h = np.clip(np.sum(pa * ba, -1) / np.dot(ba, ba), 0, 1)
            q = pa - ba * h[..., None]; d = length(q)
            m = d < best
            best = np.where(m, d, best); by = np.where(m, a[1] + ba[1] * h, by); bs = np.where(m, ss[i] + (ss[i + 1] - ss[i]) * h, bs)
        return best, by, bs
    def f(P):
        d, cy, s = closest(P)
        shell = np.abs(d - TUBE_R) - 0.045
        shell = smax(shell, P[..., 1] - (cy + 0.02), 0.03)
        shell = np.maximum(shell, np.maximum(s - 1.02, -0.03 - s))
        return shell
    def col(P, N):
        d, cy, s = closest(P)
        base = mixc(np.broadcast_to(hexc("#F6A9C2"), P.shape), hexc("#FFE3EC"), sstep(0.0, 1.0, s) * 0.7)
        inner = (d < TUBE_R)
        vein = sstep(0.025, 0.008, np.abs(P[..., 0] * 0.0 + (d - TUBE_R * 0.6)))
        base = mixc(base, hexc("#FFFFFF"), sstep(0.6, 1.0, np.sin(s * 40) * 0.5 + 0.5) * 0.18 * inner)
        return mixc(base, hexc("#E47FA2"), sstep(0.02, 0.0, cy + 0.02 - P[..., 1]) * 0.6)
    lo = RIDE.min(0) - 0.6; hi = RIDE.max(0) + np.array([0.6, 1.1, 0.6])
    return mesh_sdf(f, col, lo, hi, step=0.026)

def scenery():
    out = {}
    out["ground"] = ground_mesh()
    out["water"] = water_mesh()
    out["rock"] = rock()
    out["slide"] = slide()
    def pad_f(P):
        r = length(P[..., [0, 2]]); a = np.arctan2(P[..., 2], P[..., 0])
        d = np.maximum(r - 1.0, np.abs(P[..., 1]) - 0.035) - 0.02
        notch = np.maximum(np.abs(a) - 0.22, -(r - 0.05))
        return np.maximum(d, -notch)
    def pad_c(P, N):
        r = length(P[..., [0, 2]]); a = np.arctan2(P[..., 2], P[..., 0])
        c = mixc(np.broadcast_to(hexc("#6FB46A"), P.shape), hexc("#8CCB79"), sstep(0.2, 0.9, r) * 0.6)
        c = mixc(c, hexc("#5A9E58"), sstep(0.05, 0.0, np.abs(np.sin(a * 5))) * sstep(0.1, 0.3, r) * 0.6)
        return c
    out["pad"] = mesh_sdf(pad_f, pad_c, (-1.15, -0.12, -1.15), (1.15, 0.12, 1.15), step=0.025, ao=False)
    def lily_f(P):
        d = sphere(P, (0, 0.08, 0), 0.07)
        for ring, (n, rr, tilt, ln) in enumerate([(6, 0.1, 0.9, 0.16), (6, 0.06, 0.4, 0.14)]):
            for i in range(n):
                a = i * 2 * np.pi / n + ring * 0.5
                Q = rot_y(P, -a); Q = rot_z(Q, -tilt, (0, 0.05, 0))
                d = smin(d, ellipsoid(Q, (rr + ln * 0.6, 0.08, 0), (ln, 0.03, 0.06)), 0.02)
        return d
    def lily_c(P, N):
        r = length(P[..., [0, 2]])
        c = mixc(np.broadcast_to(hexc("#FF9EC4"), P.shape), hexc("#FFF0F5"), sstep(0.3, 0.05, r))
        return mixc(c, hexc("#FFD43B"), sstep(0.06, 0.03, length(P - V(0, 0.12, 0))))
    out["lily"] = mesh_sdf(lily_f, lily_c, (-0.4, -0.05, -0.4), (0.4, 0.35, 0.4), step=0.012, ao=False)
    def cat_f(P):
        d = capsule(P, (0, 0, 0), (0, 1.25, 0), 0.025)
        d = smin(d, capsule(P, (0, 0.9, 0), (0, 1.15, 0), 0.06), 0.02)
        for a in (0.4, 2.6, 4.3):
            d = smin(d, round_cone(P, (0, 0.0, 0), (0.18 * np.cos(a), 0.8, 0.18 * np.sin(a)), 0.035, 0.008), 0.02)
        return d
    def cat_c(P, N):
        return np.where(((P[..., 1] > 0.86) & (P[..., 1] < 1.2) & (length(P[..., [0, 2]]) > 0.035))[..., None], hexc("#9A6440"), hexc("#88AE5E"))
    out["cattail"] = mesh_sdf(cat_f, cat_c, (-0.3, -0.05, -0.3), (0.3, 1.35, 0.3), step=0.014, ao=False)
    def bush_col(P, N):
        return mixc(np.broadcast_to(hexc("#86A866"), P.shape), hexc("#B5C98A"), sstep(0, 0.9, N[..., 1]))
    out["bush"] = blob_mesh([((0, 0.35, 0), (0.7, 0.5, 0.6)), ((0.55, 0.25, 0.1), (0.45, 0.35, 0.4)), ((-0.5, 0.28, -0.1), (0.5, 0.38, 0.45)),
                             ((0.1, 0.7, 0), (0.45, 0.35, 0.4))], bush_col, step=0.06, k=0.15)
    def tree_col(P, N):
        return np.where((P[..., 1] < 1.3)[..., None], hexc("#A27C68"), mixc(np.broadcast_to(hexc("#8DAF6C"), P.shape), hexc("#C4D08E"), sstep(0, 0.8, N[..., 1])))
    out["tree"] = blob_mesh([((0, 0.7, 0), (0.2, 0.8, 0.2)), ((0, 2.0, 0), (0.85, 0.75, 0.8)), ((0.55, 1.7, 0.2), (0.55, 0.5, 0.5)),
                             ((-0.55, 1.75, -0.1), (0.55, 0.5, 0.5)), ((0.05, 2.55, 0), (0.55, 0.45, 0.5))], tree_col, step=0.07, k=0.12)
    out["cloud"] = blob_mesh([((0, 0, 0), (1.3, 0.55, 0.6)), ((1.2, -0.1, 0), (0.8, 0.42, 0.5)), ((-1.2, -0.12, 0), (0.8, 0.4, 0.5)),
                              ((0.3, 0.35, 0.1), (0.7, 0.45, 0.45))], hexc("#FFFFFF"), step=0.09)
    out["reed"] = mesh_sdf(lambda P: round_cone(P, (0, 0, 0), (0, 1.0, 0), 0.06, 0.04), solid(hexc("#8BA66A")), (-0.15, -0.1, -0.15), (0.15, 1.1, 0.15), step=0.02, ao=False)
    return out

def eye_meshes():
    w = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(EYE_W), (-1.2,) * 3, (1.2,) * 3, step=0.2, ao=False)
    p = mesh_sdf(lambda P: sphere(P, (0, 0, 0), 1.0), solid(EYE_P), (-1.2,) * 3, (1.2,) * 3, step=0.22, ao=False)
    return w, p

if __name__ == "__main__":
    import pickle, time
    t0 = time.time()
    data = dict(frog=make_frog(), turtle=make_turtle(), props=props(), scene=scenery())
    data["eye_w"], data["eye_p"] = eye_meshes()
    print("built in", round(time.time() - t0, 1), "s")
    pickle.dump(data, open("out/meshes.pkl", "wb"))
