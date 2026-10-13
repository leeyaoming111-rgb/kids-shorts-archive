# Coordinator handoff (session_012DiEG3BG1auD4t8c7zPpV2 → new coordinator)

The old coordinator's batch run was cut off by the weekly usage limit. This file says exactly where it stopped. Every
branch below is on origin. Nothing of the old coordinator's is uncommitted.

## Main branch `claude/laughing-tesla-ee3nna` (head before this note: 758c360)

- **Merged and done:**
  - `ENGINE.md` v3 (batch mode), `FABLE_WORKER.md` (worker brief), the shared kit `common/fablekit.py` with
    `sync_kit.sh`, the batch song tools (`el_batch.py`, `el_voice.py`, `el_mix.py`), and the series audio plus the
    Fable 1-2 audio (`audio/`) from `claude/fables-audio` up to 03af40e.
  - Fable 1 animatic (reviewer PASS in round 6).
- **Kit change at 758c360:** `fox_mats` takes an optional third arm angle `[side, fwd, inward]`. Tumble's short,
  wide-set arms can't bring the paws together without it. Solved poses:
  - crossed arms `[0.1, 1.5, 1.3]` / `[0.1, 1.35, 1.3]`
  - two-paw hold `[0.3, 1.25, 0.62]`
  - paws to the mouth `[0.2, 1.6, 0.6]`
  - a reach that reads from the front `[2.0, 0.3]`

  arm0 is Tumble's LEFT paw (screen right when he faces the camera). All workers were sent this update; check that
  each worker branch pulled it.

## Fable 2 "Sour Apples?" (`fable-02-sour-apples`): where it stopped

- Animatic built on the kit; geometry QA 0.
- **Reviewer round 1: FAIL (3 HIGH).** The arms couldn't cross, catch or hold the apple; the tug staging was wrong;
  the hook had no reach.
- **All round-1 HIGH and MED issues are fixed in 758c360:**
  - poses use the inward arm swing;
  - in the tug, the apple moves with Pip's beak, and the camera angle is solved (`_tug_cam_yaw`) so Tumble isn't lined
    up behind the apple;
  - Pip hovers at Tumble's face in `pip_idea`;
  - higher jumps, bigger kicks in the pile, the apple hung slightly lower;
  - "swapped hands" was a description error in the brief (see the arm0 note above).
- QA was rerun after the fixes: 0 issues. Fresh sheets are rendered in `code/review/`, but `review/` was never committed
  for Fable 2; re-render it.
- **Reviewer round 2 never finished:** the agent died on the usage limit. Next step: render sheets
  (`python3 render.py --preview sheet` and `--wide`), run an independent review round 2, and log the rounds in
  `fable-02-sour-apples/review.md` (not written yet, in Fable 1's format).
- **Fable 2 audio is done** (`audio/fable-02/`: verse recall 100%, mix 98% at -14.4 LUFS). Still to do: put
  `audio/fable-02/song_check.json` into `code/out/` and the mix into `code/out/audio.wav` (or run `el_mix.py`), then
  re-check QA with the real timing and render the finals.
- Stills for the archive are not made yet.

## Worker branches not merged into the main branch (state as of this note)

| Branch | Unmerged commits | Last commit |
|---|---|---|
| `claude/fables-audio` | 1 | 9d0061b the owner's by-ear approval of the Fable 1-2 song joins |
| `claude/fable-01-render` | 3 | 460759d song-sync reviewer fixes; check whether the final renders landed |
| `claude/fable-03` … `claude/fable-08`, `claude/fable-10` | 1-4 each | "WIP: handoff snapshot" from each worker |
| `claude/fable-09` | 6 | 44598eb contact sheets (in progress) |
| `claude/episode-01` | 1 | 940e7ac episode plan |

Merge order suggestion:
1. `fables-audio`, then `fable-01-render` (it touches only Fable 1 files and `renders/`).
2. Each `fable-NN` once it reaches reviewer PASS. They each touch only their own folder plus `audio/fable-NN/` and
   `renders/`; Fable 4 also changes `tools/cast_voices.json`, for Bo's new voice.
3. `episode-01`.

## Open items the owner should know about

- The ElevenLabs key was put into every worker's starting instructions (the owner asked for whatever was needed to
  make the songs). It is never in files. Rotate it after the batch.
- The audio worker opened a PR (#1) on its own. The coordinator merged its branch directly instead.
- The account-level `kids-song-shorts` skill still says "every video must look and sound new"; it needs a
  batch-mode update (the owner has to do this; sessions can't edit account skills).
- The old coordinator's check-in routine (trig_013Nr9SFvzQz3zkUAn7KusKW) was one-shot and has fired; nothing else
  is scheduled.
