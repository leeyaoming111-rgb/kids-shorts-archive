
# ================= stills from the fables (book pictures and quiz pages) =================
import subprocess as _sp
BATCH_ = os.path.normpath(os.path.join(HERE_, "..", ".."))
import script as SCR
class _EP:                                                           # what the Episode 01 page art expects
    HOOK_STILL, STORY_STILL = 2.6, 29.0
    FABLES = {n: dict(title=tt) for n, tt in SCR.FABLE_TITLES.items()}
    @staticmethod
    def fable_still(n, near): return still_path(n, near)
EP = _EP
def still_path(n, t):
    """a 16:9 frame of fable n at t seconds: stills/fNN_<t>.png (shipped with the job), else cut from its wide render"""
    os.makedirs(STILLS, exist_ok=True)
    p = os.path.join(STILLS, f"f{n:02d}_{t:05.2f}.png")
    if not os.path.exists(p):
        cands = [os.path.expanduser(f"~/Movies/kids-shorts/videos/episode2/fable-{n:02d}_wide.mp4"),
                 os.path.join(BATCH_, "renders", f"fable-{n:02d}_wide.mp4")]
        src = next((c for c in cands if os.path.exists(c)), None)
        if not src: return None
        _sp.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-vf", "scale=1280:-2", p])
    return p if os.path.exists(p) else None
