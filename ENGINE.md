# Kids Shorts 3D engine: playbook for scheduled runs (v3, 2026-10-12)

Each run makes original 45-second vertical 3D claymation Shorts for children aged 3 to 5, and every Short is built so it
can also join a long-form episode. The cloud session writes the story, song, audio, models and animation. The Mac renders
it on its GPU (Apple M4, about 70 s per Short).

## v3: batch mode (owner decision 2026-10-12, overrides v2 where they differ)

Shorts are now made in **batches**: one theme, 10 to 14 Shorts, one long-form episode built from the same scenes.
The first batch is `batches/01-fables-friendship/plan.md` in the archive repo. Read the current batch plan before
anything else; it holds the fable list, song plan, episode running order, schedule and owner decisions.

What changes from v2:
1. **Variety moves inside the batch.** Within a batch, every Short needs a different story, gag, shot list and set
   corner. Across a batch, the series stays the same on purpose: same cast and voices, same world, same theme sting,
   same moral chorus, same caption style. The v2 cross-video rules (format rotation, lesson not in the last 4, world
   not in the last 6, music fingerprint 4+ differences) now apply **between batches**, not between Shorts of a batch.
   History: the owner rejected Penguin Shapes as a reskin of Dino Count (same hill, slots, camera, song). A batch must
   never turn into that: shared series elements are fine, a repeated story shape, layout or gag is not.
2. **One song sound per batch.** The theme sting and the moral chorus are generated once and stored
   (`batches/<batch>/series_audio/`). Each Short gets one verse take from ElevenLabs Music on the batch fingerprint,
   spliced on bar lines with `batches/<batch>/el_batch.py`. A join needs instrumental chroma similarity 0.9 or more.
   Leave the composition and sound to ElevenLabs (owner's choice); only check recall, sections and joins.
3. **Two cameras per shot.** Every shot frames a world-space box; `render.py` solves the camera distance for 9:16
   (`render.py out.mp4`) and 16:9 (`render.py --wide out.mp4`). Stage the action in a centre core that works in both.
   Fable 1 (`batches/01-fables-friendship/fable-01-tiny-pip-big-help/code/render.py`) is the reference.
4. **Episode-ready skeleton.** Hook, sting, setup, problem, twist, moral card, moral chorus, button. The episode cut
   drops the sting and the button and adds link scenes, a recap and an outro (see the batch plan).
5. **Cadence: at least 2 Shorts a day, from a bank.** Do not publish until the whole batch and its episode are done.
   If the pipeline cannot hold 2 a day, publish 1 a day; never lower the quality gates or pad with re-cuts of old Shorts.
6. **Sources.** Fable batches retell public-domain plots only (Aesop, Grimm, Andersen, Panchatantra, Jataka, folk tales),
   never a modern book, film or song version. Soften for ages 3 to 5. Credit the fable in every description.
7. **Timeline without audio.** `timeline.py` runs on the planned 100 BPM grid with estimated word times until
   `out/song_check.json` exists, so staging, stills, contact sheets and geometry QA can be done before the song.
   Never queue a final render until the real song is aligned and mixed.
8. **No ElevenLabs key: stop at the animatic.** Build and check the visuals, then stop and tell the owner. No Kokoro fallback.

Unchanged from v2: the quality and safety rules, geometry QA, the reviewer agent, the cast voices, the audio checks and
the queue/archive steps below. Where a v2 step says "different from the archive", read it as "different from the
other Shorts in this batch".

### Batch folder layout (in this repo)

| Path | What it holds |
|---|---|
| `batches/<nn-slug>/plan.md` | the batch plan and owner decisions |
| `batches/<nn-slug>/el_batch.py` | sting, chorus and verse generation, checks, bar-line assembly |
| `batches/<nn-slug>/series_audio/` | the chosen sting and chorus takes (audio stays out of git) |
| `batches/<nn-slug>/fable-NN-slug/plan.md` | the Short's plan, shot list, lyrics, status |
| `batches/<nn-slug>/fable-NN-slug/code/` | `timeline.py`, `meshes.py`, `render.py`, `render_base.py`, `qa_geom.py` |
| `batches/<nn-slug>/fable-NN-slug/stills/`, `review/` | 8 stills per aspect, reviewer contact sheets and report |

---

The v2 playbook follows. It still applies except where v3 above overrides it.

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
| `tools/el_song.py`, `tools/audio_el_example.py` | ElevenLabs song generator and checks; example mix with spoken lines and SFX. |
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

### Song: ElevenLabs Music first, Kokoro as fallback

When `ELEVENLABS_API_KEY` is set and `api.elevenlabs.io` is reachable, make the song with `tools/el_song.py` (Episode 2 is the
reference):
1. Write a composition plan for `music_v2_5`: one section per sung line or story beat, exact `duration_ms` per section (min 3 s),
   lyrics in `text`, the voice and instruments in each section's `positive_styles` (not inline cues), the tempo, key and genre
   in the first section, `vocals` in the intro's `negative_styles`.
2. Generate 3 takes with different seeds (the plan allows 2 requests at a time). Keep the take with the best speech-to-text
   lyric recall (target 100%, minimum 95%) whose every line sits inside its section.
3. Forced alignment on the chosen take gives word timings. Drive captions, lip sync, shot cuts and gag events from them.
4. Diarized speech-to-text confirms the voices (for example a deep BIG voice and a high tiny voice). Spoken lines use ElevenLabs
   TTS with character timestamps (Episode 2: Liam for Tumble, Jessica for Pip).
5. Mix song + spoken lines + SFX at -14 LUFS with at least 0.3 s between voice lines. Check the full lyric text against the
   transcript once more after mixing.
Without the key or network, use the Kokoro sung-TTS pipeline below.

### Cast voices (fixed for every video, from Ep 2 v2)

Recurring characters keep ONE ElevenLabs voice for speaking and gag sounds in every episode. Singing comes from the music model's own singers (owner's choice). The voice IDs are in `tools/cast_voices.json`
(Tumble `Kx0fJ79cIgKz5YbJmR0t`, Pip `tGxaydQ2FS8MHwM6syrt`). A new character gets a voice from Voice Design (`/v1/text-to-voice/design`,
model `eleven_ttv_v3`, describe an adult voice actor performing the character, 3 previews), picked by pitch contrast with the cast and
clarity, saved with `/v1/text-to-voice`, and added to `cast_voices.json`. 

Song pipeline (owner's choice 2026-10-11; Episode 2 v4 is the reference; tools: el_song2.py, build_song_v4.py):
1. Everything is SUNG, by the music model's OWN singers. No voice conversion: the owner compared native singing with Seed-VC
   (cloud CPU and Mac GPU, cleaned vocal, 50 steps) and with ElevenLabs speech-to-speech plus retune, and judged every converted
   version tinny, robotic and garbled. Native wins.
2. Use melodic lyrics and a chorus of 6 to 9 s. Put "sung melodically, legato, not spoken" in `positive_styles` and "spoken word,
   talking, rap, chant" in `negative_styles`. Describe Tumble's and Pip's singing voices the same way every episode
   (warm young male tenor; light high female soprano). The model only partly follows that, which is accepted.
3. Generate takes 2 at a time with music_v2_5. Keep a take with 95%+ recall, every line inside its section and gag breaks in the right
   places. Its copyright filter can false-flag heavily repeated lyric lines: keep repeats to two.
4. A sung line may move by a whole bar via the stems (`/v1/music/stem-separation`) only when the instrumental chroma under both spots
   matches (similarity 0.9 or more). Otherwise reorder the shots to fit the song.
5. Spoken bits and gag exclamations use `eleven_v3` TTS in the fixed cast voices (tools/cast_voices.json) with audio tags and
   stability 0.0. Make 2 takes and keep the one with the widest pitch range; give "Boing" a springy pitch bend.
6. Final checks: full-mix lyric recall 90%+, loudness -14 LUFS, and a short sample for the owner when the sound approach changes.
Seed-VC on the Mac GPU stays installed (see "Mac GPU voice jobs") for possible future use with per-character training on a CUDA
GPU service. Don't use voice conversion for singing until the owner approves a sample.
Output format: mp3_44100_128 (192 needs the Creator tier).

### Audio rules for the Kokoro fallback (from the Penguin Shapes failure)

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

### Mac GPU voice jobs (set up 2026-10-11)
- `tools/svc_env` (PyTorch with Apple MPS) and `tools/seed-vc` (patched for MPS: float32 F0, soundfile save) are installed on the Mac.
  Run voice work as a queue job whose `render.py` calls `tools/svc_env/bin/python tools/seed-vc/batch.py jobs.json 50`.
  The runner marks voice jobs FAILED because they make no video; that is expected. Results go to the job's `out/`.
- Conversion at 50 steps takes about 30 s per line (the fanless Air sometimes slows to about 3 min).
- Fine-tuning Seed-VC on MPS is impractical (about 90 s per step). Don't run it on this Mac; it needs a CUDA GPU service.
- Clean the vocal stem with `/v1/audio-isolation` (whole track, at least 4.6 s) before converting: it cuts music bleed about 15-fold.
- UTMOS naturalness scores don't separate versions of sung or high cartoon voices (Pip's own speech scores 1.3). Don't use them as a gate.
  Send the owner a short sample for approval instead.
