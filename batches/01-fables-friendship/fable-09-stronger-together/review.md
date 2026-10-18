# Review log: Tumble & Pip Fables 9, Stronger Together!

The independent reviewer subagent followed `tools/REVIEWER.md`. It worked from contact sheets with one frame every
0.5 s in both aspects (9:16 Short and 16:9 episode framing), plus geometry QA (`qa_geom.py`, 15 fps). The review is
at the animatic stage: there is no audio yet and word times are estimated on the 100 BPM grid.

## Geometry QA before the reviewer

- Handoff state: 15 issues, mostly the fox's arms and body touching the bundle sticks in the pull/push shot.
  Cause: the pull/push spot (`PULLP`) was too close to the bench. Fixed by moving him back (z -4.05 to -4.3). Result: **0**.
- Kit fix kept in `render.py`: the shadow VAO is rebuilt with "3f 28x" (vertices are 40 bytes, not 48).

## Round 1: FAIL (3 HIGH, 6 MED)

- **HIGH (both), bridge crossing.** Tumble's feet straddled the narrow deck, so one foot was in the air over the water.
  Fixed: feet in one line (one ahead of the other) while he is on the bridge.
- **HIGH (short), moral and chorus.** The bridge end poked into the foreground with a dark flat leaf bow. Fixed: the
  bow is removed and the far-bank spot moved away from the bridge.
- **HIGH (both), watch_me.** He leapt over the bundle and never gripped it. Fixed: the leap clears the bundle, and
  he lands behind it and grips the middle (the next shot starts already gripping).
- **MED:** the hook twig crossed his chin (now held in the paws and shorter); the pull/push paws floated over the
  bundle (now solved on the rig); the landing read as standing (now a profile sit); the wide button covered the bridge;
  Pip flew over Tumble's head on the crossing (now leads ahead of him); the wide camera cut his ear.

## Round 2: FAIL (0 HIGH, 5 MED)

- Remaining: feet 6 px above the deck in the short; the leap left the frame top; paws still floated in the pull pose;
  the bundle end lined up with his muzzle in the sit; stick ends poked into the wide chorus corner.
- Fixed: lower leap with a wider camera; each paw bisected onto the bundle top under it; landing spot moved; far-bank
  spot moved; bigger button boing.

## Round 3: FAIL (1 HIGH, 3 MED)

- The feet were still above the deck (height was not the problem); the paws floated in the bow-up pose and at 19.5;
  the button framing cut Pip off.
- Fixed: balancing arms (one paw ahead, one behind, because the camera looks along his arm axis); paws solved per
  paw on the real rig; head-scratch removed; button camera wider and shifted toward the bridge.

## Round 4: FAIL (1 HIGH)

- The walk line was further from the camera than the deck (measured: feet 0.03 to 0.06 above and behind the top).
- Fixed: walk line moved to x = BRX + 0.12, stand height trimmed by 0.012. Pip's hover moved clear of the head.

## Round 5: PASS (0 HIGH, 0 MED, 9 LOW)

Both feet sit on the deck in both aspects; the arms read; the paws rest on the bundle in every pose.

Remaining LOW items (not fixed):
- Lead foot hangs about 0.1 above the grass for 0.25 s as he steps off the far end (34.0 to 34.25).
- The button boing reads mostly as Pip rising and dipping at the crane distance.
- Tumble's feet overlap the rising bundle arm at the deepest bow (24.5).
- Pip and the bundle end are clipped by the left edge after the landing (25.5 to 26.0, short).
- The left arm and twig half touch the left edge after the snap (2.0 to 3.5, short).
- A sliver of Tumble at the left edge in the pip_ask macro (wide).
- Pip enters cut by the top edge (35.0, wide).
- Captions fade slightly before their sections end (19.0, 34, 37.5).
- Pip passes behind the tree at the right edge of the short for 0.5 s on the crossing (accepted).

Accepted by design: the short pip_ask has no Tumble in frame (macro on Pip); the moral and chorus use the kit's
`dance_tumble`/`dance_pip`; the bridge is not visible in the short moral and chorus.

Process note for the next fable: `qa_geom` has no foot-to-deck or paw-to-prop contact test, so floating contacts have
to be checked by measuring vertices against the prop surface.
