"""Geometry QA for SDF-clay videos: finds objects passing through each other, sinking into the ground, or
perched objects floating above their support. Reusable: tag each draw's uniforms with obj="<name>" (and
perch=True for a perched object); meshes must carry a "name" whose SDF grid lives in out/sdf.pkl."""
import pickle, json, math
import numpy as np
from scipy.ndimage import map_coordinates

class Bank:
    def __init__(self, sdf_path, mesh_dicts, nsample=500, seed=0):
        raw = pickle.load(open(sdf_path, "rb"))
        self.g = {k: (v.astype(np.float32), np.asarray(lo, float), float(st)) for k, (v, lo, st) in raw.items()}
        rng = np.random.default_rng(seed)
        self.v = {}
        for name, m in mesh_dicts.items():
            v = m["v"]; idx = rng.choice(len(v), min(nsample, len(v)), replace=False)
            self.v[name] = np.c_[v[idx], np.ones(len(idx))]
            c = v.mean(0); self.v[name + ":bs"] = (c, float(np.max(np.linalg.norm(v - c, axis=1))))
    def sdf(self, name, P):
        vol, lo, st = self.g[name]
        idx = ((P - lo) / st).T
        return map_coordinates(vol, idx, order=1, mode="nearest")

def _scale(M): return abs(np.linalg.det(M[:3, :3])) ** (1 / 3)

def check_frame(t, items, bank, ground=None, tol=0.012, float_tol=0.05, masks=None, ground_objs=None):
    """items: list of (obj, mesh_name, M, perch). Returns list of issue dicts."""
    out = []
    world = {}
    for i, (obj, name, M, perch) in enumerate(items):
        world[i] = (M @ bank.v[name].T).T[:, :3]
    spheres = {}
    for i, (obj, name, M, perch) in enumerate(items):
        c, r = bank.v[name + ":bs"]; spheres[i] = ((M @ np.r_[c, 1])[:3], r * _scale(M))
    for i, (oa, na, Ma, pa) in enumerate(items):
        for j, (ob, nb, Mb, pb) in enumerate(items):
            if oa == ob: continue
            (ca, ra), (cb, rb) = spheres[i], spheres[j]
            if np.linalg.norm(ca - cb) > ra + rb: continue
            W = world[i]
            if masks and (oa, ob) in masks:
                W = W[masks[(oa, ob)](bank.v[na][:, :3])]
                if not len(W): continue
            Pl = (np.linalg.inv(Mb) @ np.c_[W, np.ones(len(W))].T).T[:, :3]
            d = bank.sdf(nb, Pl) * _scale(Mb)
            depth = -float(d.min())
            if depth > tol:
                out.append(dict(t=round(t, 3), kind="penetration", a=f"{oa}:{na}", b=f"{ob}:{nb}", depth=round(depth, 3)))
    # perched objects must touch something
    for i, (oa, na, Ma, pa) in enumerate(items):
        if not pa: continue
        best = 9.0
        for j, (ob, nb, Mb, pb) in enumerate(items):
            if ob == oa: continue
            Pl = (np.linalg.inv(Mb) @ np.c_[world[i], np.ones(len(world[i]))].T).T[:, :3]
            best = min(best, float(bank.sdf(nb, Pl).min()) * _scale(Mb))
        if best > float_tol:
            out.append(dict(t=round(t, 3), kind="floating", a=f"{oa}:{na}", gap=round(best, 3)))
    if ground is not None:
        for i, (oa, na, Ma, pa) in enumerate(items):
            if ground_objs and oa not in ground_objs: continue
            P = world[i]; g = ground(P[:, 0], P[:, 2])
            sink = float((g - P[:, 1]).max())
            if sink > 0.03:
                out.append(dict(t=round(t, 3), kind="below_ground", a=f"{oa}:{na}", depth=round(sink, 3)))
    return out

def summarize(issues, fps):
    """merge per-frame issues into time intervals per (kind, a, b)"""
    groups = {}
    for e in issues:
        groups.setdefault((e["kind"], e["a"], e.get("b", "")), []).append(e)
    res = []
    for (k, a, b), es in groups.items():
        es.sort(key=lambda e: e["t"]); start = prev = es[0]["t"]; worst = 0
        for e in es + [None]:
            if e is None or e["t"] - prev > 1.5 / fps:
                res.append(dict(kind=k, a=a, b=b, t0=start, t1=prev, worst=worst))
                if e is None: break
                start = e["t"]; worst = 0
            worst = max(worst, e.get("depth", e.get("gap", 0))); prev = e["t"]
    return sorted(res, key=lambda r: r["t0"])
