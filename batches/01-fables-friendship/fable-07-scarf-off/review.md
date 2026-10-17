# Review log: Tumble & Pip Fables 7, Scarf Off!

The independent reviewer subagent (Opus) followed `tools/REVIEWER.md`. It worked from contact sheets with one frame
every 0.5 s in both aspects (9:16 Short and 16:9 episode framing), plus geometry QA (`qa_geom.py`, 15 fps). The review
is at the animatic stage: there is no audio yet and word times are estimated on the 100 BPM grid.

## Geometry QA before the reviewer

- After merging the kit update (third arm angle) the hug pose became the two-paw hold `[0.3, 1.25, 0.62]`.
- First runs: 16 issues. Causes: Pip floated 0.03 above the post, and Pip's flight from the post to the flower
  passed through the stem and petals. Fixed by lowering the perch and routing the flight over the flower head.
- Then **0**.

## Round 1: FAIL (4 HIGH, 7 MED)

- **HIGH (both), whistle.** It hung in mid-air beside Pip's beak. Fixed: it lies on his chest on a red cord and swings
  up into his beak to blow (cord stays attached).
- **HIGH (both), pip_cling.** Pip floated beside the stem with his feet in the air. Fixed: he is blown onto the
  petals of the big flower and rides its sway; his seat is measured from the flower mesh and follows the bend.
- **HIGH (both), wind_puff.** A tree sat under the Wind's mouth like a beard, and no gust was visible. Fixed: trees are
  hidden in the four sky-face shots, a fan of streaks pours from the round mouth, and the Sun is moved out of the wide
  frame for that shot.
- **HIGH (both), sunbathe.** He looked collapsed with his head upside down. Fixed: the lie-down is a cosy nap on his
  side with his head kept upright, eyes closed, filmed from a lower camera.
- **MED, hold_tight camera.** Pulled out too far, Tumble cropped. Fixed: it follows Pip's flight to the flower with
  both in frame and no ground edge.
- **MED, wind_tired / sky_faces framing.** The Sun and the Wind were cut by the frame edge. Fixed: wider fit, the
  trees removed, the Sun's mouth is now a curved smile.
- **MED, button crane.** Characters left the frame during "Bye-bye!". Fixed: the crane starts after the line.
- **MED, spin.** Pip lay under the petals. Fixed by the new flower-head perch.
- **MED, moral/chorus.** A tree crowned Tumble's head. Fixed: that tree is hidden in those shots.
- **MED, scarf_off.** The hanging scarf looked like a rod. Fixed: a draped, swaying curve.

## Round 2: FAIL (1 HIGH, 5 MED)

- **HIGH, sunbathe.** He still looked like he fell. Fixed over rounds 3 to 5: a crouch first, then a slow lie-down onto
  his side with his head rolled upright to the camera, eyes closed and smiling.
- **MED, hold_tight short.** The camera was too far back and showed the ground edge. Fixed: hold_tight now ends as the
  gust hits and a separate insert shot, `pip_blown`, films Pip's flight from the post onto the flower head.
- **MED, Wind's mouth and streaks.** The mouth became an open "O" with a lip ring, and the gust streaks start in front of
  it and follow the face direction. The wide camera is raised so the mouth clears the caption.
- **MED, tree behind Tumble in moral/chorus.** Three trees are hidden in those shots.
- **MED, scarf.** The hanging part is a draped curve with a rounded corner (Chaikin smoothing).
- **MED, sky_faces short.** Tumble sat under the caption. The shot is now sky only (he and his scarf are not drawn).

## Rounds 3 and 4: FAIL, then PASS (spot check)

- Round 3 found a grey blob (the camera was beyond the ground disc in the short hold_tight) and streaks that
  did not start at the mouth. Both fixed as above.
- Round 4: PASS with one MED, the forward lean as he lies down.

## Final pass (real song timing): FAIL, then PASS

- With the real song the Twist line landed 3 s late, so the Sun shot was silent and the spoken "Ahh... scarf off!" was
  hidden by the sung caption. Fixed by a new verse take (seed 5) whose Twist line starts 1.2 s into its section, and by
  moving the spoken gags clear of the sung lines ("Whoa-whoa!" at 24.2, "Ahh... scarf off!" at 31.79).
- Last pass: **PASS**, all 18 sheets read tile by tile, no HIGH, 1 MED left (the lie-down still tips forward a little
  before he settles on his side), the rest LOW polish (a cropped cloud edge, the star puff reads as a ring of dots).
