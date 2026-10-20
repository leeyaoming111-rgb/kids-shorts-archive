# Polish pass fixer brief (Batch 01, Tumble & Pip Fables), 2026-10-20

You fix ONE fable so it passes an independent review. The owner watched the finished Shorts and complained about:
1. characters glitching into each other (Pip inside Tumble's head or face, props through bodies), including things that
   only LOOK inside from the camera;
2. voices not matching (now solved by a new song, see below);
3. jumpy audio and abrupt cuts into the outro and at the end.

An independent reviewer already watched your fable's final render frame by frame. Its report is your work list:
`/tmp/claude-0/-home-claude/80866f71-e121-5bdb-af5b-e747e72471cc/scratchpad/rev/issues/NN.md`
(zoom crops it made are under `.../scratchpad/rev/zoom/`). Fix every HIGH and MED issue. Fix LOW issues where the fix is
cheap and safe. Owner priority: anything that reads as one character inside another.

Paths: B = `/tmp/claude-0/-home-claude/80866f71-e121-5bdb-af5b-e747e72471cc/scratchpad/ksa/batches/01-fables-friendship`.
Your fable folder is `B/fable-NN-slug/`; its code is in `code/`. Read `B/FABLE_WORKER.md` (how the fables are built,
lessons from earlier reviews) and your fable's `plan.md` and `review.md` first.

## UPDATE 2026-10-20 12:05: ElevenLabs quota exhausted

Do NOT call `el_voice2.py` or any ElevenLabs API until the coordinator says so. Keep the spoken clips already in
`audio/fable-NN/`, re-time `SPOKEN` so no line overlaps sung words or runs past the end, and mix with
`python3 el_mix2.py <fable_dir> --nostt` (no API calls).

## What changed under you (already done by the coordinator)

- **Shared kit** `B/common/fablekit.py` is updated and already synced into your `code/` (do not edit it; put any
  override in your `render.py`): closed eyes really close; the singing mouth sits in the face surface; Pip's mouth sits
  at the beak base; small high-five star puff at the wing-paw contact; Pip sits on the outer half of the paw with wings
  tucked in the moral and chorus; a sung caption gives way to a spoken line; spoken mouths follow the real clip
  loudness (`out/spoken_env.json`); a 0.5 s fade to cream at the very end; QA at 30 fps plus a `screen_contact` check
  (Pip drawn over Tumble's head within 0.5 depth units).
  Fable 1 only: it has its own renderer and does not use the kit. Port the same fixes into its `render.py` by hand.
- **New song.** Each fable now has ONE continuous ElevenLabs Music take (no splices). Tumble is sung by a male voice and
  Pip by a high female voice, both conditioned on Fable 1's approved voices. The take is picked by `B/el_song2.py pick`
  and lands in `code/out/song.wav` + `code/out/song_check.json` (it has a `"take"` key; the old file does not).
  If your `song_check.json` has no `"take"` key yet, your song is still generating: do the non-timing fixes first and
  check again later (the coordinator runs `el_song2.py pick` for you; never generate music yourself).
  Timing differences you must handle:
  - Section boundaries come from the real phrasing (`T.sec(...)`), so Hook and Sting can be longer or shorter than
    3.6 / 2.4 s. Everything must keep deriving from `T.sec()`, `T.line()` and `word_times()`.
  - The Button is now 2 bars (about 4.8 s) and the video is about 50.4 s (`T.DURATION`). The final chord rings out.
    Make the last action settle by `DURATION - 0.8` and hold, so the kit's fade lands on a still frame.
  - `HIGH_FIVE` and every story event must still land on the real sung words. Check after the song arrives.
- **Spoken lines v2.** `python3 B/el_voice2.py B/fable-NN-slug` voices `timeline.SPOKEN` in the fixed cast voices at
  stability 0.5 and keeps the take closest to each character's anchor voice (so the voice stays on-model). Then
  `python3 B/el_mix2.py B/fable-NN-slug` mixes song + lines (ducking, no truncation, fades, -14 LUFS) and writes
  `code/out/audio.wav`, `code/out/spoken_env.json`, `audio/fable-NN/mix.mp3` and `report.json`. It prints PROBLEMS:
  a spoken line that lands on a sung word, or runs past the end. Re-time those lines in `timeline.py` (t0 in a gap
  between sung lines, never past `DURATION - 0.3`) and re-run the mix until there are no problems. The reviewer
  flagged several of these (gags over sung lines, "Bye-bye" cut off at the end).
  ElevenLabs key: put `export ELEVENLABS_API_KEY=$(tr -d '\n ' < /mnt/user-data/uploads/Movies/kids-shorts/.secrets/elevenlabs.key)`
  at the start of the same shell command. Never print it, never write it to a file. The plan allows only 2
  concurrent requests for ALL agents together; the tools retry on 429, so just be patient.

## Setup in your code folder

```
cd B/fable-NN-slug/code && python3 meshes.py      # builds out/meshes.pkl and out/sdf.pkl (~15 s); fonts are in assets/
```

## Checks (all must pass)

1. `python3 render.py qa` (30 fps, both 3D penetration and the new screen_contact check) reports 0 issues. Tag every
   character, prop and accessory draw with `obj=` so QA can see it (strings, scarf, flags, leaves, lids, ants, knots).
   Keep `qa_ignore` minimal and only for things that truly touch (a held prop in a paw). Fix causes; do not hide them.
   If a screen_contact is a false alarm (Pip clearly beside the head, not over it), say so in review.md with a still.
2. Look at stills yourself (`python3 render.py --preview x <secs...>` and `--wide`) at every fix, in BOTH aspects.
   CPU is shared with about ten other agents (2 cores): use targeted stills while iterating, full contact sheets
   (`python3 render.py --preview sheet` and `python3 render.py --preview --wide sheet`) only for review rounds.
3. Independent review: spawn a reviewer subagent (Agent tool, general-purpose) with `B/../../tools/REVIEWER.md`
   (`.../scratchpad/ksa/tools/REVIEWER.md`), your plan.md, both aspects' sheets and `out/qa_report.json`. Tell it the
   preview is half resolution, that it must check every tile of both aspects, report [short]/[wide], and that it may
   render extra stills but must not edit code. Fix every HIGH and MED it finds and send it the next round
   (SendMessage) until it returns PASS. Also tell it to check that the mouth moving matches the caption's character,
   and that nothing reads as one character inside another.
4. Log each round in `review.md` under a new heading "Polish pass (2026-10-20)".

## Rules

- Touch only your fable folder and `B/audio/fable-NN/`. Never edit `B/common/`, other fables, or anything on the Mac.
- Do NOT run any git command (the coordinator commits). Do not render final full-resolution videos; the coordinator
  renders them on the Mac GPU from your code folder.
- Keep everything the fable's plan intends (story beats, morals, the series dance). Improve staging where the reviewer
  says a beat does not read.
- Finish with a short report: what you fixed (issue by issue), QA result, the reviewer's final verdict and round
  count, any issue you chose not to fix and why, and the final `T.DURATION`.
