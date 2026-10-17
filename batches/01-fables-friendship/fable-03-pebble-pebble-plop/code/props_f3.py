"""Fable 3 props built from the shared SDF primitives (meshes.py is not edited): the tall clay jug.
The jug is a hollow solid of revolution (round belly, narrow neck, rolled lip, a handle on one side) with an open top,
so a paw fits in the neck, pebbles drop inside and the water disc rises inside it.
python3 props_f3.py builds out/f3_props.pkl and adds the jug's SDF grid to out/sdf.pkl for geometry QA.
render.py calls ensure() so the Mac builds it on first run (about 3 s)."""
import os, pickle
import numpy as np
from meshes import (V, length, sphere, ellipsoid, capsule, round_cone, smin, smax, hexc, mixc, sstep, mesh_sdf)

JUG_TOP = 0.845                    # top of the rolled lip
NECK_IN = 0.2                      # inner radius of the neck (Tumble's paw is 0.1)
BOTTOM_IN = 0.07                   # inside floor at the centre

def jug_outer(P):
    d = ellipsoid(P, (0, 0.34, 0), (0.33, 0.34, 0.33))
    d = smin(d, round_cone(P, (0, 0.45, 0), (0, 0.8, 0), 0.255, 0.245), 0.1)
    r = length(P[..., [0, 2]])
    lip = np.sqrt((r - 0.245) ** 2 + (P[..., 1] - 0.8) ** 2) - 0.045             # rolled lip (torus)
    d = smin(d, lip, 0.02)
    # handle: half a torus in the x-y plane on the -x side
    q = P - V(-0.3, 0.52, 0)
    rr = np.sqrt(q[..., 0] ** 2 + q[..., 1] ** 2)
    hd = np.sqrt((rr - 0.15) ** 2 + q[..., 2] ** 2) - 0.035
    hd = np.maximum(hd, q[..., 0] + 0.02)
    d = smin(d, hd, 0.03)
    return np.maximum(d, -(P[..., 1] - 0.02))                                     # flat base
def jug_inner(P):
    d = ellipsoid(P, (0, 0.36, 0), (0.285, 0.29, 0.285))
    return smin(d, capsule(P, (0, 0.45, 0), (0, 1.3, 0), NECK_IN), 0.1)
def jug_sdf(P):
    return smax(jug_outer(P), -jug_inner(P), 0.01)
def jug_col(P, N):
    c = np.broadcast_to(hexc("#C8673F"), P.shape).copy()                        # terracotta
    ang = np.arctan2(P[..., 2], P[..., 0])
    dots = sstep(0.035, 0.02, np.sqrt(((np.mod(ang * 12 / np.pi, 2) - 1) * 0.12) ** 2 + (P[..., 1] - 0.42) ** 2))
    c = mixc(c, hexc("#F6E7CC"), sstep(0.012, 0.004, np.abs(np.abs(P[..., 1] - 0.42) - 0.075)))
    c = mixc(c, hexc("#F6E7CC"), dots)
    c = mixc(c, hexc("#F3DDB8"), sstep(0.75, 0.8, P[..., 1]))                     # glazed cream lip
    inside = jug_inner(P) > -0.02
    c = np.where((inside & (P[..., 1] < 0.76))[..., None], hexc("#8E4A30"), c)    # darker clay inside
    return c

def inner_radius(y):
    """radius of the inside wall at height y (for the water disc)"""
    lo, hi = 0.0, 0.4
    for _ in range(30):
        m = (lo + hi) / 2
        if jug_sdf(np.array([[m, y, 0.0]]))[0] < 0 or jug_inner(np.array([[m, y, 0.0]]))[0] > 0: hi = m
        else: lo = m
    return lo

def build():
    jug = mesh_sdf(jug_sdf, jug_col, (-0.55, -0.05, -0.4), (0.4, 0.95, 0.4), step=0.012)
    jug["name"] = "f3/jug"
    sdf = jug.pop("sdf")
    pickle.dump(dict(jug=jug), open("out/f3_props.pkl", "wb"))
    return sdf

def ensure():
    """build the props if missing and make sure their SDF grids are in out/sdf.pkl (meshes.py rewrites that file)"""
    sdf = None
    if not os.path.exists("out/f3_props.pkl"): sdf = build()
    store = pickle.load(open("out/sdf.pkl", "rb"))
    if "f3/jug" not in store:
        if sdf is None: sdf = build()
        store["f3/jug"] = sdf; pickle.dump(store, open("out/sdf.pkl", "wb"))
    return pickle.load(open("out/f3_props.pkl", "rb"))

if __name__ == "__main__":
    import time; t0 = time.time()
    if os.path.exists("out/f3_props.pkl"): os.remove("out/f3_props.pkl")
    store = pickle.load(open("out/sdf.pkl", "rb")); store.pop("f3/jug", None); pickle.dump(store, open("out/sdf.pkl", "wb"))
    ensure(); print("built in", round(time.time() - t0, 1), "s")
