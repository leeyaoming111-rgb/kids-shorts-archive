"""usage: python3 camtest.py [--wide] t cx cy cz yaw pitch fw fh [fov] [lift] ... (several cameras: repeat groups with ';')  -> out/cam_*.png"""
import sys
from render import *
a = [x for x in sys.argv[1:] if x != "--wide"]
groups = " ".join(a).split(";")
for k, g in enumerate(groups):
    v = [float(x) for x in g.split()]
    t = v[0]; tgt = np.array(v[1:4]); yaw, pit, fw, fh = v[4:8]; fov = v[8] if len(v) > 8 else 38.0; lift = v[9] if len(v) > 9 else None
    HOOKS["camera"] = lambda tt, tgt=tgt, yaw=yaw, pit=pit, fw=fw, fh=fh, fov=fov, lift=lift: fit_cam(tgt, yaw, pit, fw, fh, fov=fov, lift=lift)
    fr = overlay(fablekit.render_frame(t) if False else render_frame(t), t)
    skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/cam_{k}.png")
