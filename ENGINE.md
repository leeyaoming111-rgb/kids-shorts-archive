# Kids Shorts 3D engine: playbook for scheduled runs (v2, 2026-10-10)

Each scheduled run makes ONE new, original 45-second vertical 3D claymation Short for children aged 3 to 5.
The cloud session writes the story, song, audio, models and animation. The Mac renders it on its GPU (Apple M4, about 70 s).

**v2 changes the goal.** v1 made every video a reskin of "Dino Count" (same hill, five arrival spots, locked camera, same
120 BPM C-F-G bouncy song, same "X, X, here comes Y" chant). The owner rejected that. Every video must now look, move
and sound new. The dino code supplies tools only (SDF clay modelling, GPU renderer, sung-TTS tuning, mixing). It never
supplies the look, the layout, the camera or the song. This playbook overrides any instruction elsewhere to copy the
Dino Count shape.

## Folder map (on the Mac: ~/Movies/kids-shorts)

| Path | What it holds |
|---|---|
| `engine/` | Toolkit from "Dino Count": sing.py (phrase autotune), audio.py (mix chain), check_audio.py, meshes.py (SDF primitives, mesher), render.py (moderngl renderer, shader, captions). Read-only. Copy what you need. |
| `archive/<job_id>/` | One folder per video: `plan.md`, `music.json`, `stills/` (8 frames). THE variety memory. Read all of it before inventing. |
| `queue/<job_id>/` | Jobs waiting for the Mac helper. Renders when `READY` exists. Helper writes `RUNNING`, then `DONE` (JSON) or `FAILED` (log tail). |
| `videos/<job_id>.mp4` | Finished full-quality videos. |
| `history.json` | One line per finished video: job_id, date, title, format, lesson, characters, setting, voice, hook. |
| `tools/qa_geom.py` | Geometry QA: penetration, floating perches, below-ground. Copy into the job. |
| `tools/REVIEWER.md` | Brief for the independent reviewer subagent. |
| `runner.sh`, `install_helper.command` | The Mac helper. Do not modify. |

`job_id` format: `YYYY-MM-DD-am-slug` or `YYYY-MM-DD-pm-slug` (local Mexico City time; am = before 13:00).

## Step 1. Set up the cloud workspace

1. `device_stage_files` the files in `engine/`, `history.json`, and every `archive/*/plan.md` and `archive/*/music.json`.
2. `pip install --break-system-packages kokoro-onnx soundfile skia-python praat-parselmouth moderngl scikit-image`
3. Download Kokoro from GitHub into `assets/`: `kokoro-v1.0.onnx` and `voices-v1.0.bin`
   (`https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/`).

## Step 2. Invent something new (read the archive first)

Pick and write down, before any code:

1. **Format.** Rotate between:
   - *Song-and-reveal*: things or characters slide into frame one at a time and the song names them.
   - *Story*: one character wants something, tries, has a small problem, solves it. Beginning, middle, end.
   - *Series episode*: recurring characters from an earlier archive entry marked `series:`, new adventure, same look and theme song hook. Start a new series when no series exists or the last 3 videos had none.
   Do not use the format of the previous video.
2. **Lesson.** Not used in the last 4 videos. Ideas: counting, colours, shapes, big and small, animal sounds, opposites, weather, fruit and veg, vehicles, body parts, feelings, bedtime and routines, sea creatures, bugs, farm animals, sharing, taking turns, days of the week, letters, rhyming.
3. **World.** Setting and character species not used in the last 6 videos. Original characters only. Never a licensed character, never a real person's voice or likeness. Give the main character a name and a personality.
4. **Shot list.** 6 to 12 shots. Each shot: time range, camera type (wide, medium, close-up, low angle, overhead, tracking, slide-in, push-in, cutaway), and one sentence on what happens. Use at least 4 camera types and at least 2 hard cuts. Hold each shot at least 1.3 s.
5. **Music fingerprint** (write `music.json`): tempo, time signature, key, chord progression, instruments, song form, hook line. It must differ from EACH of the last 10 archive entries on at least 4 of: tempo by 12+ BPM, time signature, key, progression, lead instrument, song form. Reuse no melody and no chant pattern.
6. **Prompt.** One paragraph in plain words (the shape of a text-to-video prompt) that describes this video.

Then create `archive/<job_id>/plan.md` (format, lesson, world, characters, prompt, shot list, lyrics, status: in progress) on the Mac
straight away, so a parallel run sees it and avoids it.

## Step 3. Build it

Write new `timeline.py`, `meshes.py`, `render.py`, `audio.py` for this video. Copy toolkit functions freely; design the rest from the plan.
Freedom: camera, lighting mood, sky, set, layout, caption position, title style and props all follow the plan.
Fixed for quality and safety only:
- Ages 3 to 5: slow readable motion, no flashing (no full-frame brightness change faster than 0.5 s), nothing scary, big friendly captions, one idea per segment, repetition of the hook.
- The lesson items are the most saturated things on screen. Backgrounds stay softer.
- Claymation look: SDF clay, thumbprint shader, soft shadows. Keep it.
- Style inspiration (principles only, never their characters): Monica Toy, Too Too Boy, Oddbods, Pinkfong. Hook in the first
  3 seconds, gags as setup, anticipation, payoff, big expressive faces, squash and stretch, sound-effect timing, a copyable dance move.
- Contacts: place anything that rests on something (a bird on a head, a hat, feet) from SDF-measured surface heights.
- Output: 1080x1920, 30 fps, about 45 s. `render.py out/video.mp4` must run on the Mac with only numpy, scipy, skimage, PIL, skia, moderngl. Nothing else is installed there.

### Audio rules (from the Penguin Shapes failure)

Penguin Shapes cut 8 of 18 sung lines short by up to 0.36 s, often on the lesson word. Prevent it:
- Budget syllables: at most 3.5 sung syllables per second. Leave at least 0.5 beat of rest after every sung line.
- The last note of a line ends at least 0.35 s before the next line starts.
- Log, for every phrase, how much the cap trimmed (`cut` seconds) in `out/vocal_log.json`.
- Voices: `am_eric` (speaks near MIDI 51.3) and `af_heart` (near MIDI 55.9). Alternate. Set TRANSPOSE so the melody centre sits 3 to 4 semitones above speaking pitch.

## Step 4. Check in the cloud before queueing

1. Audio: tuning median under 5 cents, 90%+ frames within 30 cents, HNR at or above raw TTS, energy above 12 kHz under 1%, loudness -14 LUFS plus or minus 1.
2. **Trim check: every phrase `cut` at most 0.03 s.** Fix lyrics or timing until true. Listen-proxy: also confirm the last word of every line is present in `word_times.json` before its next line.
3. Variety check: compare `music.json` and the plan with the last 10 archive entries; write the differences into `plan.md`.
4. Render 8 stills across the shots, build a contact sheet and LOOK at it. Check: characters in frame, props where the story needs them, captions readable, nothing intersecting, and the stills look different from the archive stills of the last 3 videos.
5. **Geometry QA:** tag draws with `obj=` (and `perch=True` for perched objects), export `out/sdf.pkl`, run `tools/qa_geom.py`
   over every frame at 15 fps, plus a pop check (objects appearing or vanishing on screen away from a cut). Target 0 issues.
   Props change only at a cut or through a visible action.
6. **Reviewer agent:** render a frame every 0.5 s into labelled contact sheets (12 per sheet). Spawn a separate subagent with
   `tools/REVIEWER.md`, the sheets, `plan.md` and `qa_report.json`. Fix every HIGH and MED issue; repeat until it returns PASS.
   Save its final report as `archive/<job_id>/review.md`.
7. Fix and re-check until clean. Do not queue a job that fails a check.

## Step 5. Queue the job on the Mac

1. Stage everything `render.py` needs under `/mnt/user-data/outputs/<job_id>/` (code, assets, out/meshes.pkl, out/audio.wav, out/word_times.json, job.json). Files must be 30 MB or less each.
2. `device_commit_files` them to `~/Movies/kids-shorts/queue/<job_id>/`.
3. Commit an empty `READY` file LAST, in its own call.
4. Poll with `device_bash` for `DONE` or `FAILED`, up to 15 minutes.

## Step 6. Verify, archive, deliver

1. On DONE: extract 2 frames (one mid-video, one in the finale) and look at them.
2. Stage `queue/<job_id>/out/video_share.mp4` and send it with SendUserFile.
3. Finish `archive/<job_id>/`: final `plan.md` (status: done, render time, check numbers), `music.json`, `stills/` with 8 frames (JPEG, 540x960).
4. Append the entry to `history.json` (with `format`).
5. If GitHub push access works (`git ls-remote` succeeds with credentials), commit `archive/<job_id>/` (plan, music.json,
   review.md, stills, job code; no audio or video files) to https://github.com/leeyaoming111-rgb/kids-shorts-archive.
6. Report in the owner's house voice: title, format, lesson, prompt, what is new versus the archive, check numbers, render time, timestamps worth watching.

## Fallbacks

- FAILED: read the log tail, fix, re-queue as `<job_id>-r2`.
- Mac unreachable or no DONE after 15 minutes: leave the job queued AND render in the cloud: `python3 render.py seg <f0> <f1> <out>` in parallel halves, concat, mux audio, re-encode under 30 MB, send.
- Never modify `engine/`, `runner.sh` or `install_helper.command`, and never delete anything on the Mac.
