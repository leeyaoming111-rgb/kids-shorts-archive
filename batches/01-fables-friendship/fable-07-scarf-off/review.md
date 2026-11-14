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

## Polish pass (2026-10-20)

Work list: `scratchpad/rev/issues/07.md` (2 HIGH, 5 MED, 7 LOW). New song: take_11 (one continuous take, recall 0.967,
voice sim 0.803). Hook is now 2.32 s, the sting 3.68 s, the button 4.8 s, `T.DURATION` 50.4 s. Spoken lines are v2
(el_voice2, stability 0.5, anchor-closest take). Mix (el_mix2): -14.0 LUFS, 0 problems; final STT recall below.

### Timing (timeline.py)

- Shot cuts follow the real line ends: wind_puff starts after "...snug and warm!" (14.91), so Wind blows in his own
  close-up and "Huff and puff!" starts on Tumble (cut 16.76); the spin shot holds the whole "Round and round... it won't
  come off!" line (to 24.2); pip_cling (24.2-26.2) holds all of "Whoa-whoa!" (24.06, 1.9 s); wind_tired 26.2-27.6.
- "Ahh... scarf off!" moved off the sung Twist line to 33.81 (after "kind..." ends 33.66); the sunbathe holds to 35.76
  and the moral shot starts 0.3 s before "Gentle".
- HIGH_FIVE lands on the sung "all!" (42.86). The hook whistle peep moved to the title shot after "Tumble and Pip!"
  (4.48), since the 2.32 s hook is all singing. "Bye-bye!" at 46.3 (ends 46.97). Every action settles at
  `END_HOLD = DURATION - 0.8` (49.6) and the frame holds still under the kit's end fade.

### Issue by issue

- **HIGH ending.** One song take rings out to silence (-27 dB at 47.8, -63 dB at 49.0, no slam, no cut). The crane runs
  47.15-48.7 and settles; Wind waves a puffy cloud arm out of his side and rocks, the Sun rocks and winks (48.1-49.45);
  the frame holds 49.6-50.4. Final framing fits both faces whole in both aspects.
- **HIGH sunbathe head.** The head roll now counters the body tip: `head[2] = -(pi/2 - 0.3) * lie`. He lies on his side
  with his head upright, ears up, eyes closed. The overhead shot also gets a lower key light (-0.14) against the haze.
- **MED scarf through the tail.** The scarf ends are pushed out of five measured tail spheres (they follow the tail
  swing). The tail is tagged `obj="tail"` so QA now checks scarf against tail (tail-fox is ignored, it is one body).
- **MED scarf end on the post.** hold_tight films from his right (yaw 25, pitch 6): the streaming end clears Pip's post
  in both aspects.
- **MED Pip's wing on Tumble's cheek (moral, chorus).** Camera from his right (moral -20 to -30, chorus -32), Pip sits
  0.08 out from the paw ball's centre (eased in over his hop), turns 0.3 rad to the camera, folds his wings, and folds
  the near wing low on the high-five. Full-resolution crops at 36.4, 36.5, 38.0, 39.0, 40.0, 41.0, 42.0, 42.6, 42.9 and
  44.0 in both aspects show a clear gap between Pip and the cheek. QA stays at 0 (no penetration, no floating).
- **MED title placement.** 9:16: a low wide camera puts Wind and Sun below the title and Tumble and Pip at the bottom.
  16:9: the post lands right of "Scarf Off!", so the landing reads.
- **MED star puff.** render.py's big puff (the yellow doughnut) is gone; the kit's small puff at the wing-paw contact stays.
- **LOW captions on the wrong shot.** Fixed by the timing changes above.
- **LOW scarf on the grass.** It lies in soft S-waves (heading wobble along its length); the dropped part falls into a
  curl from its hanging shape (no straight runs, no corner).
- **LOW crops.** Spin [short] now frames Pip on the flower; pip_blown [wide] shows Tumble whole; hook, sky_faces [wide]
  and wind_tired keep Wind's cloud in frame.
- **LOW bug eye in the spin.** Eyes are not drawn while his face points away from the camera (dot < -0.15).
- **LOW hug.** The paws clutch the scarf at the collar (`HUG = [0.8, 1.3, 0.7]`).
- Not changed: the hanging scarf end still hangs beside his left paw; the Sun's top edge touches the frame in the short
  pip_blown insert, and the scarf's end pokes in at its left edge (both LOW).

### Checks

- `python3 render.py qa` (30 fps, penetration plus screen_contact): **0 issues** (`out/qa_report.json`).
- Contact sheets rebuilt in both aspects (`code/review/`, 18 sheets); every tile read by the fixer.
- Independent reviewer: the fixer session had no Agent tool, so the coordinator ran the REVIEWER.md round on these
  sheets (`rev/issues/07_polish_r1.md`).

### Polish round 1: PASS (0 HIGH, 0 MED, 9 LOW)

All 14 items of the old list read FIXED or reduced to LOW. Mouths match captions, no level slams, the end holds still,
Pip's near wing keeps a 20-40 px gap from the cheek at full resolution. Cheap LOWs fixed after the verdict:

- **Scarf vs tail tip at 22.92-23.00 (camera-only overlap).** The tail now swings to the upwind side during the gust
  (`st["tail"] = -0.6 * gusty(t)`), so the white tip stays below the streaming ends. Full-res wide 22.9/22.95/23.0 are clear.
- **"Whoa-whoa!" caption 0.14 s early.** `s00_pip` t0 = PB_SPLIT1 + 0.05 (24.25): the caption starts on the pip_cling cut.
- **[short] sunbathe Pip half cut.** The 9:16 fit box moves right and widens (target x 0.05, fit 2.15): Pip and his post
  sit inside the frame at 33.5 and 35.5. The shot's key light drops another 0.06 against the haze.
- **Dropped scarf.** Wider S-waves (amp 1.05, k 2.6) pack the run closer to the foot, and the dropped end lies in a gentle
  wave (amp 0.45) instead of a tight curl, so no candy-cane hook by the fence.
- **Not fixed: the high-five wing.** Pip's far wing sits hidden behind his body at this yaw, and the only wing that reaches
  the paw on screen sits against Tumble's cheek, the owner-priority problem. Both wings stay folded; the beat reads as the
  paw bump, Pip's hop and the kit's star dots on "all!".
- Left as LOW: Wind touching the left edge in the [short] hook and sky_faces, the Sun in the [short] pip_blown, two ray
  balls above the [wide] title, the small [short] spin composition, Pip off-screen in [wide] sky_faces while he sings.

Checks after these fixes: QA 0 issues (30 fps). `el_mix2.py` with STT: -14.0 LUFS, peak 0.908, lyric recall 0.967,
0 problems (spoken at 24.25, 33.81, 46.3).
