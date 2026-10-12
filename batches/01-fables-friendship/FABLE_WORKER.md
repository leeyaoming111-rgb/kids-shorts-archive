# Fable worker brief (Batch 01, Tumble & Pip, Fables About Friendship)

You build ONE fable of the batch end to end: plan, animatic in both aspects, geometry QA, independent review,
song and voices from ElevenLabs, mix, and final renders. The coordinator session merges your branch.

## Read first

1. `ENGINE.md`: the v3 batch-mode section, the quality and safety rules, "Cast voices" and "Song pipeline".
2. `batches/01-fables-friendship/plan.md`: series constants, adaptation rules, your fable's section, the song plan.
3. The two finished fables:
   - `fable-01-tiny-pip-big-help/`: `plan.md` and `review.md`. It predates the kit, but its review log is the best
     list of what goes wrong.
   - `fable-02-sour-apples/code/`: the reference implementation on the shared kit. Copy its structure.
4. `common/fablekit.py`: the shared renderer. Do not edit it in your branch. If you need a kit change, put it in
   your fable's `render.py` (wrap or override) and mention it in your report.

## Setup

```bash
pip install --break-system-packages moderngl skia-python scikit-image soundfile requests
apt-get install -y libegl1 libgl1-mesa-dri libegl-mesa0      # software OpenGL (llvmpipe) for headless rendering
cd batches/01-fables-friendship
mkdir -p fable-NN-slug/code/out fable-NN-slug/code/assets
cp fable-01-tiny-pip-big-help/code/assets/Fredoka.ttf fable-NN-slug/code/assets/ 2>/dev/null || \
  curl -sSL -o fable-NN-slug/code/assets/Fredoka.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf"
common/sync_kit.sh                                            # copies fablekit, render_base, meshes, qa_geom into every fable
cd fable-NN-slug/code && python3 meshes.py                    # builds out/meshes.pkl and out/sdf.pkl (about 15 s)
```

The font and the out/ files are gitignored on purpose.

## 1. Plan (write `fable-NN-slug/plan.md` before code)

Use Fable 1's `plan.md` as the template:
- prompt;
- lyrics table with sections on the same 20-bar grid at 100 BPM (Hook 1.5 bars, Sting 1, Setup A 2, Setup B 2,
  Problem A 2, Problem B 3, Twist 3, Moral 1.5, Chorus 3, Button 1);
- shot list (at least 4 camera types, hard cuts, each shot 1.3 s or longer);
- spoken gags;
- differences from the other fables in the batch;
- new assets.

Rules:
- At most 3 sung syllables per second, one idea per line.
- The moral line goes in the Moral section exactly as in the batch plan (you may polish wording).
- Chorus lyrics are fixed: "Big or small, short or tall, / friends help friends, that's best of all!"
- Retell the Aesop plot in your own words, softened for ages 3 to 5. Nobody is mean, scary or hurt.
- Every Short needs a different set corner, gag and camera plan from the other fables. Look at the other fables'
  stills before you stage.

## 2. Build the animatic

`timeline.py`:
- Copy Fable 2's and change only `JOB`, `TITLE_PARTS`, `SOURCE`, `WORD_STYLE`, `PLAN_LINES`, the `SHOTS` table, the
  story events and `SPOKEN`.
- Keep `TITLE_SHOT = "title_wide"`, the shot names `moral`, `chorus` and `button_crane`, and `HIGH_FIVE`.
- Derive story events from word times (`word_times(...)`), so they follow the real song later.

`render.py`:
- Start with `from fablekit import *`.
- Define the world constants, `tumble(t)`, `pip_state(t, st, mats)`, `camera(t)` and `build_draws(t)`, then end with
  `HOOKS.update(...)` and `main()`.
- Use `dance_tumble` / `dance_pip` for the moral and chorus (the series dance; do not change it), `fit_cam` for
  every camera, and `meadow_backdrop`, `draw_tumble`, `draw_pip` and `puff` for drawing.

Characters and props:
- Tumble: a fox cub about 2.2 tall. His paws reach only about 1.36 high, below his own ears.
- Pip: a bird about 0.6 tall.
- Existing meshes: `E2` (apple, berry, bigleaf, stump, mushroom, basket, blanket, appletree), `SC` (ground, cottage,
  cloud, sun, tree, flower, stone, leaf, rainbow, puddle), `PR` (hat, umbrella, kite, ball, stick, mouth).
- Build new props from these primitives where you can (balls, sticks, scaled leaves) rather than editing `meshes.py`.
  If you must add a mesh, add it in your fable folder's own `meshes.py` copy and say so; `sync_kit.sh` will
  overwrite that copy, so tell the coordinator.

Fast stills (about 1.5 s each on CPU):
- `python3 render.py --preview x 1.5 4.5 ...` writes `out/still_short_*.png`; add `--wide` for 16:9.
- LOOK at them, in both aspects, every time you change staging.

## 3. Checks (all must pass before audio)

1. `python3 render.py qa` must report **0 issues**:
   - Set `HOOKS["ground_objs"]` to exclude the fox while he lies down or dives.
   - Use `qa_ignore` only for held props and props tucked into foliage.
   - Fix causes; do not hide them.
2. Contact sheets: `python3 render.py --preview sheet` and `python3 render.py --preview --wide sheet`, run in
   parallel. They write `review/`.
3. Spawn an independent reviewer subagent (Agent tool, general-purpose):
   - Give it `tools/REVIEWER.md`, your `plan.md`, the 18 sheets and `out/qa_report.json`.
   - Tell it the animatic has no audio (ignore caption drift under 0.5 s and preview softness), that it must check
     every tile of both aspects and report `[short]` / `[wide]` issues, and that it may render extra stills but must
     not edit code.
   - Fix every HIGH and MED issue, rerun QA and the sheets, and send the same agent the next round (SendMessage)
     until it returns PASS.
   - Log every round in `review.md`, in Fable 1's format.

## Lessons from Fable 1's six review rounds (avoid them up front)

- **Lines (strings, ropes, tails) must never cross a face.** Check them from the camera, not in 3D. Route them
  low, behind, or on the far side.
- **Perspective overlap reads as collision.** A bird "beside" a head at a different depth looks embedded. Keep
  flyers at the same depth as what they fly beside, or clearly above it.
- **Flight paths:** use explicit straight legs (up, across, down). A curve never passes through its middle
  control point, so it cuts corners through heads.
- **Anything resting on something** (Pip on a paw, an apple in a paw, a foot on a stump) is placed from measured
  surfaces: `paw_seat()`, `hand_pos()`, mesh extents.
- **Props never appear or vanish mid-shot**, only at a cut or through a visible action.
- **Cameras:**
  - `fit_cam` keeps the eye above the grass. Use a side-on camera for beak and mouth actions
    (`side_on_yaw(a, b)`).
  - Check that the subject sits above the caption band in BOTH aspects.
  - A camera that follows several moving things should frame all of them (see Fable 1's button camera).
- **Tree canopies are low:** a bird near an apple stem is inside the leaves. Stay below the canopy on the outer side.
- **Before a shot ends,** characters must be where the next shot needs them, or the move must happen across a cut.
- **One mouth at a time.** The kit draws it; don't add your own.

## 4. Song, voices, mix (needs network access to api.elevenlabs.io)

The key is in the environment variable `ELEVENLABS_API_KEY`. The coordinator gives it to you in your first message.
Never write it to a file, log or commit, and never print it.

Steps:
- `python3 ../../el_batch.py verse <fable_dir> <seed>` for 3 seeds. Keep a take with 95%+ recall and every line
  inside its section; try more seeds if needed.
- `python3 ../../el_batch.py assemble <fable_dir> <verse.mp3> ../../audio/series/sting.mp3 ../../audio/series/chorus.mp3`.
  The owner approved the sting joins by ear; the chroma test is not meaningful for the a-cappella sting.
- Voices: `el_voice.py <fable_dir>`. Mix: `el_mix.py <fable_dir>`. Targets: -14 LUFS, full-mix recall 90%+.
  The mix writes `code/out/audio.wav` and `code/out/song_check.json`. If those tools are not in your checkout yet,
  `git pull origin claude/laughing-tesla-ee3nna`.
- Commit `audio/fable-NN/` (verse.mp3, verse_check.json, song.mp3, song_check.json, spoken mp3s, mix.mp3,
  report.json), matching `audio/fable-01/`.

## 5. Final renders

1. With `out/song_check.json` in place, the timeline uses the real word times. Rerun `qa` (must be 0), the sheets,
   and a quick look at captions against the song.
2. Render both aspects at full resolution with audio: `python3 render.py out/fableNN_short.mp4` and
   `python3 render.py --wide out/fableNN_wide.mp4`. On CPU this is slow (a few seconds per frame).
   - Split each into segments run in parallel: `python3 render.py seg <f0> <f1> out/part_k.mp4`, then concat with
     ffmpeg and mux `out/audio.wav`.
3. Copy the results to `batches/01-fables-friendship/renders/fable-NN_short.mp4` and `fable-NN_wide.mp4`,
   re-encoded with libx264 crf 23 so each is under 40 MB, and `git add -f` them (mp4 is gitignored).
4. Archive 8 stills per aspect in `fable-NN-slug/stills/`, as Fable 1 does.

## Git

- Work on your own branch (given in your first message).
- Commit and push after each milestone: plan, animatic, review pass, audio, renders. Push with
  `git push -u origin <branch>`.
- End commit messages with: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
- Do not open pull requests. Do not touch other fables' folders or `common/`.

## Report back

When done, or if blocked, finish with a short report: title, status, QA, reviewer rounds, recall and LUFS, render
paths, commit hash, and anything the coordinator must merge or fix.
