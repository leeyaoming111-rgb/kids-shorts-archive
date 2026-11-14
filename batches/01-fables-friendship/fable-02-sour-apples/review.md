# Review log: Tumble & Pip Fables 2, Sour Apples?

An independent reviewer subagent (Opus) followed `tools/REVIEWER.md`. It worked from contact sheets with one frame
every 0.5 s in both aspects (9:16 Short and 16:9 episode framing), plus geometry QA (`qa_geom.py`, 15 fps), and
rendered extra stills where needed. Rounds 2 to 4 ran on the real sung word times (song sync in place).

## Geometry QA

- Before round 1: 0 issues on the estimated grid.
- After the round-2 restaging: 11 issues (Pip crossing Tumble's head and the canopy on his new flight paths). Fixed
  with explicit straight-leg flights (up, across behind the stump, in from the outer side). Back to **0**.
- Final: **0** with the real word times.

## Round 1: FAIL (3 HIGH)

- Arms could not cross, catch or hold the apple; the tug staging was wrong; the hook had no reach.
- Fixed: kit inward arm swing (crossed arms, two-paw hold, paws to the mouth), the apple follows Pip's beak in the
  tug, tug camera angle solved so Tumble is out of line, Pip hovers at his face in `pip_idea`, higher jumps, bigger
  kicks in the pile.

## Round 2: FAIL (3 HIGH, 4 MED)

Found only after the real song times were applied (the events had been planned on the grid and the sung words sit
later in their sections):

- **HIGH, leap:** the leap happened after the cut to the pile, so he was never seen jumping. Fixed: the cut is now
  0.5 s after the sung "jump" of "One more big jump".
- **HIGH, catch:** the apple fell before the catch shot began and popped in. Fixed: the release is on "here it
  comes", the cut is just before it, the camera is tall, and the apple falls into his paws in view. A new `ready`
  shot has Pip wait behind the stump, then fly round behind him to the apple (cameras moved to the right side so
  the leaf pile no longer hides the stump).
- **HIGH, chorus:** the chorus was static. Fixed: bounce and sway on the beat, the apple paw lifts on the beat,
  and the "Mmm, SWEET!" bite moved to after the chorus lyric (it overlapped the sung "here it comes" before). The
  spoken lines were re-placed in the mix (Oof 14.57 s, SWEET 44.0 s).
- **MED:** sulk head pitched up and body turned to camera; Pip left Tumble's face at the climb cut; leaf-pile
  camera starts wide to keep him in; both paws reach on the jumps.

## Round 3: FAIL (5 MED)

- Sulk still read as one paw on the chest; tug showed no pull; chorus modest; bite did not read; wide leap cut the
  apple off.
- Fixed: tug swing and final strain, longer hanging stem, tug camera widened; apple paw dances on every beat; a pale
  bite mark stays on the apple after the bite (crumb puff removed); big_jump and climb cameras raised; Pip lifts off
  sideways at the end of `pip_idea`. Stronger inward arm swings were tried and rejected: Tumble's arms are too
  short, they just sink into his torso.

## Round 4: PASS (0 HIGH, 2 MED, 5 LOW)

- **MED, tug:** Pip backs off about one apple-width between tugs and the stem hides in the canopy, so the grip is
  weak. Accepted: the release, fall and catch read clearly.
- **MED, sulk:** "paws clasped at the chest, nose up, head turned" rather than crossed arms. The reviewer judged it
  not fail-worthy for ages 3 to 5.
- LOW, left as is: modest chorus dance (shared series dance); apple covers his snout mid-bite; large soft trunk in
  the wide tug frame; jump paws only to face height; Pip behind his cheek at 16.0; title text hides the apple in
  the wide title card.

## Polish pass (2026-10-20)

New song (one continuous take, `take_14.mp3`, 50.4 s), spoken lines v2 (stability 0.5, anchor-matched), mix v2
(`el_mix2.py --nostt`: -14.0 LUFS, 0 problems). Work list: the independent review of the previous final render
(`rev/issues/02.md`, FAIL: 3 HIGH, 5 MED, 8 LOW).

### Fixes

- **HIGH, Pip in Tumble's head (two-shot, 20.4-24.0):** Pip's hover was parented to the turning head. It is now a
  fixed world point beside the cheek on the camera's right (0.95 to the side of the head centre, a little towards the
  camera), with a clear gap from ear and snout. Tumble sulks with his nose turned away from Pip, then turns his head
  to Pip on "Let's try" and nods on "you and me". The two-shot camera frames both.
- **HIGH, leaves through the ears (sulk):** the two big head leaves are replaced by one small leaf resting on the
  front of the crown, placed from the head SDF and tagged `headleaf` for QA. It comes from the pile as he pops out
  and stays on to the end (a running gag), which also fixes the LOW continuity note at 20.4.
- **HIGH, the tug did not read:** the apple swing sign is fixed (it now swings out towards Pip), the pull is bigger,
  and the apple has a short side stalk; Pip's beak sits on the stalk's end, computed from the swung apple every frame.
  The tug camera yaw is now chosen by projecting the tree mesh: no trunk in frame in either aspect (also the LOW).
- **MED, jump cut into the sulk:** the pop-out now happens at the end of the leaf-pile shot, with the camera widening
  to catch it. The sulk shot opens with him standing. "Oof!" moved after the sung "whoa!" (14.34 s).
- **MED, heading pop on the leap:** the leap yaw blends from the run-up heading.
- **MED, apple into the snout at the bite:** his arms are too short to hold the apple in front of him without hitting
  chin or tummy, so the bite is a side chomp, solved against the head SDF (head turned to the apple, nose down). The
  `("apple", "fox")` QA ignore is removed for the whole film; the apple rests on the paw (offsets solved by SDF).
- **MED, button hop over the crown:** Tumble holds the apple out at his side; Pip flies off the paw, round low in
  front of his tummy and up to the apple's outer side, and pecks it there.
- **MED, mouth artefact in the sulk:** in the sulk and the bite this fable sinks the singing mouth flatter into the
  muzzle with a matte dark red (an override of the kit mouth draw in `render.py`).
- **LOW:** no one-frame flip at the climb or run-up cuts; the pile's rim leaves are smaller, none touch the stump, and
  Tumble pops out and walks clear of it (the pile is now tagged for QA outside the dive shots); the bite mark is a flat
  pale patch on the side that met his mouth; he hops down off the stump before the moral (to the side away from the
  pile); the dance spot moved clear of the pile.
- **Catch:** he now catches the apple on his right paw at his side (it used to sit between his paws, inside his chin),
  then turns to us. The ready shot is at least 1.8 s even though "tug" comes early in the new take.
- **End:** the last action settles by `DURATION - 0.8`; the scene holds a still frame with everyone's eyes open
  (t = 49.48) under the kit's fade. "Bye-bye!" is at 47.7 s, after Pip's pecks.
- Not changed: the sulk's "crossed arms" still read as paws clasped at the chest (his arms are too short to cross;
  accepted in round 4).

### Checks

- Geometry QA at 30 fps (penetration, floating, ground, pops, screen_contact): first run 70 issues (mostly the newly
  tagged pile and the un-ignored apple), then 12, 3, **0**. `qa_ignore` is only `("apple", "tree")` (the hanging
  apple's top in the leaves).
- Self-check of both aspects' sheets and full-resolution crops of the two-shot, the sulk mouth, the head leaf, the
  bite and the button flight.

### Independent review, round 1: PASS (0 HIGH, 0 MED, 7 LOW)

The coordinator ran the reviewer (`rev/issues/02_polish_r1.md`): 14 of the 16 old issues fixed, mouths match the
captions, nothing reads as one character inside another. Cheap LOWs fixed afterwards:

- Apple on his chin for 0.2 s at the catch: he now turns to us while it falls (RELEASE to CATCH), so it lands on
  his paw at his side.
- Forehead leaf read as a flat disc: deeper orange, with a darker midrib and a little stalk.
- The held apple's side-stalk leaf lay on the apple's front: while held, the stalk points back and out to his side.
- Dark corner in the [short] tug close-up: it was Tumble's own paw (catch pose) poking in from the stump; his paws
  stay down during the tug shot.
- Pip's mouth read as a berry in his beak (the kit already has it at (0, 0.305, 0.215)): `render.py` now draws it as a
  thin dark opening tucked under the beak base.
- Left as is: the "crossed arms" sulk (arms too short) and the modest chorus dance with an implied high-five (shared
  series dance; HOLD_ARM keeps the apple clear of his face).

After the fixes: QA **0** at 30 fps; targeted full-res stills in both aspects (sulk leaf, two-shot, tug, catch, moral,
bite, peck). Spoken lines are the v2 takes; mix `el_mix2.py` with speech-to-text: recall 1.0, -14.0 LUFS, 0 problems.
Final `T.DURATION` 50.4 s.
