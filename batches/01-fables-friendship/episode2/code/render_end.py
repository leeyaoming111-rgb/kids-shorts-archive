
def scene_pages():
    if T.CLOSED_BOOK: return [("hook", 1)]
    if MODE == "read":
        if T.RECAP:
            import json as _j
            order = _j.load(open(os.path.join(HERE_, "..", "songs", "recap", "code", "out", "song_check.json")))["lines"]
            ns = [int(L["sec"].split()[1]) for L in order if L["sec"].startswith("Moral")]
            return [("hook", T.PAGE_FROM)] + [("story", n) for n in ns] + [("end", 0)]
        return [("hook", T.PAGE_FROM), ("hook", T.PAGE_TO)]
    return [("story", T.FABLE or 5)]
PAGES = scene_pages()

@lru_cache(maxsize=None)
def quiz_image(n, at):
    """full-frame picture insert: the fable still on a storybook page (cream paper, rounded frame, number badge)"""
    arr = np.zeros((H, W, 4), np.uint8); cv = skia.Surface(arr).getCanvas()
    cv.clear(skia.Color(250, 240, 214))
    rng = np.random.default_rng(n)
    for k in range(60):                                                 # paper speckle
        cv.drawCircle(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 3), skia.Paint(AntiAlias=True, Color=skia.Color(232, 218, 188)))
    p = still_path(n, at)
    mx, my = int(W * 0.07), int(H * 0.08); iw, ih = W - 2 * mx, H - 2 * my - int(H * 0.06)
    if p:
        im = Image.open(p).convert("RGB"); sw, sh = im.size
        ch = int(sh * 0.80); cw = min(sw, int(ch * iw / ih)); x0 = (sw - cw) // 2
        im = im.crop((x0, 0, x0 + cw, ch)).resize((iw, ih), Image.LANCZOS)
        rgba = np.dstack([np.asarray(im), np.full((ih, iw), 255, np.uint8)])
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx - 14 + 10, my - 14 + 14, iw + 28, ih + 28), 46, 46),
                     skia.Paint(AntiAlias=True, Color=skia.Color(150, 120, 90, 90)))                     # soft shadow
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx - 14, my - 14, iw + 28, ih + 28), 46, 46),
                     skia.Paint(AntiAlias=True, Color=skia.Color(255, 250, 240)))
        cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx, my, iw, ih), 34, 34), True)
        cv.drawImage(_skimg(rgba), mx, my); cv.restore()
    cv.drawCircle(mx + 40, my + 40, 62, skia.Paint(AntiAlias=True, Color=skia.Color(255, 214, 80)))
    _text(cv, "?", mx + 40, my + 72, 96, (255, 250, 240), 10)
    return arr
def page_insert(t):
    for P in T.PAGES:
        if P["t0"] <= t < P["t1"]: return P
    return None

_render_frame = FK.render_frame
def render_frame(t):
    if T.kind_at(t) == "page":                                         # a 2D picture insert: no 3D needed
        P = page_insert(t) or T.PAGES[0]
        base = quiz_image(P["fable"], float(P["still"]))
        u = clampu(t, P["t0"], P["t1"]); z = 1.0 + 0.05 * u                # slow push in
        img = np.zeros((H, W, 4), np.uint8); cv = skia.Surface(img).getCanvas()
        cv.translate(W / 2, H / 2); cv.scale(z, z); cv.translate(-W / 2, -H / 2)
        cv.drawImage(_skimg(base), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        img[..., 3] = 255
        return img
    return _render_frame(t)
FK.render_frame = render_frame

_overlay = FK.overlay
def overlay(img, t):
    if T.kind_at(t) != "page":
        eye, tgt, fov = camera(t)
        q = QUADS.get(round(t, 4))
        if q:
            surf_ = skia.Surface(img); cv = surf_.getCanvas()
            cover_q, spread_q, facing = q
            if facing < -0.995 and cover_angle(t) < 0.02:
                pq = _project(eye, tgt, fov, cover_q)
                if pq: _draw_quad(img, cv, cover_image(), pq, 1.0)
            idx, alpha = spread_index(t) if MODE == "read" else (0, 1.0)
            if PAGES and alpha > 0.01:
                pq = _project(eye, tgt, fov, spread_q)
                if pq: _draw_quad(img, cv, page_image(*PAGES[min(idx, len(PAGES) - 1)]), pq, alpha, ref=PAGE)
            del surf_
    return _overlay(img, t)
FK.overlay = overlay

# ================= draws =================
def build_draws(t):
    NOW["t"] = t
    draws, contacts = [], []
    backdrop(draws, t)
    draws.append((E2["stump"], trans(STUMP[0], ground_h(*STUMP) - 0.02, STUMP[1]) @ roty(STUMP_YAW) @ scale(STUMP_S), U(mat=0, bump=0.9, obj="stump"), True))
    for (x, z, s) in [(STUMP[0] + 1.9, STUMP[1] + 0.9, 0.2), (STUMP[0] - 2.6, STUMP[1] - 0.6, 0.17), (STUMP[0] - 1.5, STUMP[1] - 1.6, 0.22)]:
        draws.append((E2["mushroom"], trans(x, ground_h(x, z) - 0.01, z) @ scale(s), U(mat=0, bump=0.6, obj="mushroom"), True))
    draw_flowers(draws, t, FLOWERS)
    st = tumble(t); mats = fox_mats(st)
    draw_tumble(draws, contacts, t, st, mats)
    if MODE == "read":
        Mb = fox_root(dict(st, sq=0.0)) @ book_frame_local(t); turn, _ = page_turn(t)
        QUADS[round(t, 4)] = book_draws(draws, Mb, cover_angle(t), turn)
    else:
        QUADS[round(t, 4)] = book_draws(draws, BOOK_FLAT, math.pi, None)
    pip = pip_state(t, st, mats)
    draw_pip(draws, contacts, t, pip, mats[2])
    for hf in T.HIGH_FIVES[:-1]:                                        # the kit puffs the last high-five only
        puff(draws, hand_pos(mats[2]) + np.array([0.08, 0.12, 0.16]), hf, t, n=6, size=0.032, spread=0.55, dur=0.35, tint=(1.0, 0.88, 0.35), axis=(0, 0.25, 0.25))
    if len(QUADS) > 64: QUADS.pop(next(iter(QUADS)))
    return draws, contacts

HOOKS.update(build=build_draws, camera=camera, tumble=tumble, sky=sky_hook,
             ground_objs=lambda t: ("fox", "pip"),
             qa_ignore={("book", "fox"), ("fox", "book")})

def main_episode():
    os.makedirs("out", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "qa": FK.qa(out=f"out/qa_{SCENE}.json"); return
    if len(sys.argv) > 1 and sys.argv[1] == "sheet": FK.sheets(outdir=f"review/{SCENE}"); return
    if len(sys.argv) > 1 and sys.argv[1] == "x":
        for s in sys.argv[2:]:
            t0 = time.time(); fr = overlay(render_frame(float(s)), float(s))
            skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/still_{SCENE}_{float(s):05.2f}.png")
            print(s, round(time.time() - t0, 2), "s", flush=True)
        return
    FK.main()
if __name__ == "__main__":
    main_episode()
