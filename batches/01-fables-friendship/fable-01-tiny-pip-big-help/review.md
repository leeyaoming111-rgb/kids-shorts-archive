# Review log: Tumble & Pip Fables 1, Tiny Pip, Big Help!

The independent reviewer subagent followed `tools/REVIEWER.md`. It worked from contact sheets with one frame every
0.5 s in both aspects (9:16 Short and 16:9 episode framing), plus geometry QA (`qa_geom.py`, 15 fps). The review is
at the animatic stage: there is no audio yet and word times are estimated on the 100 BPM grid.

## Geometry QA before the reviewer

- First run: 45 issues. Causes:
  - Tumble's tail swung into the stump; fixed by moving his spot.
  - The resting kite sat under his head once he fell; fixed by moving it in front of him.
  - He spun before standing up; fixed by standing him up first.
  - Pip's wing brushed his face on the paw perch; fixed by solving the paw pose numerically for clearance.
  - Pip's hops were flagged as floating; they were intentional, so the perch flag now drops during a hop.
- Then 11 issues, then 2, then **0**.

## Round 1: FAIL (4 HIGH, 10 MED)

- **HIGH (both aspects), peck shot.** Pip faced away from the knot and no knot was visible. Cause: Pip stood directly
  under the point he was meant to face, so his heading was undefined. Fixed:
  - The knot now sits low on the coil at beak height, and is bigger with a bigger pop puff.
  - Pip faces the knot.
  - The camera films the shot three-quarter front.
- **HIGH (both), chorus dance.** The paw and wing never touched, and the high-five missed. Fixed: Pip rides Tumble's
  outstretched paw through the whole chorus (no flight across the moral-to-chorus cut). They sway together, and on
  the high-five Pip hops up while the paw rises to meet his wing, with a star puff.
- **MED, hook.** Pip seemed to sit inside Tumble's head (a perspective overlap). Fixed: Pip flies at Tumble's depth,
  beside him on screen. The kite's tug is now 0.62 high instead of 0.38.
- **MED, gust.** The kite crossed his face. Fixed: it now circles above head height (radius 1.8, height 2.6 at the end).
- **MED, button.** The kite rose through his head. Fixed: it lifts straight up first.
- **MED, overhead.** Pip landed on the string, not at the chest. Fixed by the new knot target.
- **MED, spin-out start.** He was still horizontal with his face cut off. Fixed: the rise starts at the cut and the
  camera starts wider, centred on him.
- **LOW items fixed:**
  - Leaves crossing his forehead: the leaves now blow in a band behind him.
  - Foreground tail in the 16:9 Pip close-up: Tumble turns towards the kite and that camera is re-angled.
  - The mouth reading as a smear: it is a little larger and sits in front of the smile line.

## Round 2: FAIL (1 HIGH, 6 MED)

- **HIGH:** the kite still crossed his face as it fell at the end of the gust.
- **MED:**
  - the kite tail beads hung across his face;
  - the button string crossed his face;
  - the high-five had no contact.
- **Fixes:**
  - The kite falls on a curve behind him.
  - The tail follows the kite's own down axis and is shorter near him.
  - In the button, Pip and the kite take separate paths.
  - The high-five was re-choreographed: Pip hops up and lands back on the paw as it bumps up to meet him, with a star
    puff on the contact. The paw can only rise 0.11 before Pip would touch Tumble's head; that limit was solved
    numerically.

## Round 3: FAIL (3 MED)

- **MED:**
  - the gust string crossed his face from the paw;
  - the button string crossed his head;
  - Pip overlapped Tumble at the start of the spin-out.
- **Fixes:**
  - The kite flies on his paw side.
  - Pip hops clear on a high arc before Tumble rises.
  - In the button, Pip picks up the loose string end on the grass.

## Round 4: FAIL (2 MED)

- **MED:**
  - the gust string still crossed his face later in each loop;
  - the button string formed a V across his body.
- **Fixes (geometry):**
  - Tumble clutches the string low at his waist and the kite circles low, so the string always passes below his
    face. The camera is a little higher.
  - In the button, Pip flies high behind Tumble's head (three explicit legs, after a curved path cut through his head)
    and picks the string up beside the kite on Tumble's left. The slack stays on the grass round his feet.

## Round 5: FAIL (2 MED, framing)

- **MED:**
  - in 9:16, the climbing kite and Pip left the frame;
  - in 16:9, Pip landed in the caption band.
- **Fixes:**
  - The button camera follows Tumble, Pip and the kite together.
  - Tumble's head is re-meshed at twice the resolution. The jagged "mouth with teeth" was the carved smile line
    breaking up at the old mesh step.
  - The singing mouth is a single glossy shape that covers the smile line.

## Round 6: PASS

LOW items left:
- Pip half behind the "Bye-bye!" caption for about 0.2 s in 16:9.
- The kite corner passing just behind Tumble's ear at 19.8 s.
- Tumble small in the 9:16 gust.
- The kite's tail beads crossing the top edge at 16.0 s.
- Tumble's paw at the edge of the 16:9 Pip close-up.

After the pass, Pip was moved clear of the kite's tail at the end (he read as upside-down there). Geometry QA was rerun:
0 issues.

**Final checks:** geometry QA 0 issues at 15 fps; reviewer PASS (round 6) on both aspects.

Audio checks are still to do, once the ElevenLabs song exists.

## Song sync (real ElevenLabs song, aligned word times)

The real take differs from the planned grid in one place that matters. The Twist opens with an instrumental whistle
break (27.6-31.4 s), so Pip sings "I can help! Peck, peck, peck!" late (pecks at 32.42, 32.74, 33.06). On the old
shot split, Tumble was already spinning free at 31.7 s and the knot popped after the spin. Fixes (all in
`timeline.py` and `render.py`, driven by word times):

- **Twist retimed:** the peck close-up runs from 27.6 s to the first half-bar line at least 0.5 s after the last
  "peck" (33.6 s). The knot pops at 33.25 s, so the pop and puff show before the cut. The spin-out runs from 33.6 to
  36.0 s (rises at 34.05, spins until 35.5, dizzy, Pip cheers). The moral shot starts on the half-bar line at the
  sung "Tiny" (36.0 s), clamped to at least 1.9 s of spin-out and a bar before the Moral ends.
- **Whistle break:** Pip studies the knot, looking one way and then the other, with a small hop every two beats.
  From 30.8 s his wing goes up ("idea", then "I can help!") until just before the first peck.
- **Hook:** the kite's tug follows the sung "kite!" (1.86 s), not the planned 2.55 s.
- **Overhead:** Pip's flight down arcs higher (1.2 instead of 0.9), clearing a 1.2 cm wing-into-arm clip that the
  real "tangled" time caused at 25.4 s.
- **Unchanged:** captions, mouths and the spoken gags already ran from the aligned times. "Uh-oh! Help!" (24.9),
  "Wheee!" (31.9) and "Bye-bye!" (46.3) match the mix.

**Resolved after the first render (audio splice, `mix_v2.mp3`; the text below is the original problem):** the mix puts Tumble's "Wheee!" at 31.9 s, inside the peck close-up and
over Pip's "help!", while Tumble is still tied up. Its caption is hidden behind Pip's sung line. To fix it, remix with
the gag at about 34.3 s (0.25 s after Tumble starts to rise). `GAG_WHEE` in `timeline.py` would then follow.

**Independent reviewer (song sync): PASS.**
- **MED, fixed:** dead air in the whistle break; the pop shown for only 0.24 s; `KNOT_POP` and `MORAL_CUT`
  robustness (an empty `PECKS`, a moral cut not tied to "Tiny").
- **LOW, left as is:**
  - Pip's 0.42 s hop clear at 33.6 is quick.
  - The wing-up is small in the close-up.
  - The moral caption covers Tumble's legs at the end of the push-in.
  - A cropped kite corner at the 16:9 peck-shot edge.

Geometry QA after the fixes: 0 issues (15 fps).

## Moral-to-chorus cut at 38.4 s (owner: "not smooth")

The owner's 2026-10-12 listen (audio/fable-01/report.json) and a later note said the transition into the chorus at about
38 s was not smooth. Measured on the final mix: the beats stay in time across the join (onsets every 0.3 s) and there
is no click, but the chorus is much brighter (about +9 dB above 4 kHz) and the chroma match is 0.80 (target 0.90).
On the picture it was a hard cut from the tight moral push-in to the medium chorus shot, with Tumble's head tilt and
second arm jumping.

Fix (picture only, `render.py`): the moral shot now eases back out from the tight two-shot to exactly the chorus
framing (centre, yaw, pitch and size), and a 0.3 s dissolve (38.25-38.55 s) blends Tumble's small pose change.
Frames 1080-1160 re-rendered in both aspects and spliced in; the audio is unchanged (`mix_v2.mp3`).

**Open (audio):** the brightness step at the join is untouched, because it can't be judged without listening. If it
still sounds rough, ease the chorus highs in over its first second.

## Breathing space before the chorus (owner: still choppy at 38 s)

After the picture fix the owner still heard the join at about 38 s as choppy, and asked for 1-2 s of space between the
moral line and the chorus. Measured: "helpers!" ended at 38.36 s and "Big" began at 38.46 s, with nothing between.

Fix (`audio/fable-01/mix_v3.mp3`, `timeline.py`, `render.py`):
- **Audio:** 1.5 s inserted at 38.4 s, filled by a reverb ring-out of the last 0.35 s of the band, fading from -22 dB
  to about -50 dB over the gap (no digital silence). The chorus then enters on its own downbeat at 39.9 s.
  Loudness -14.5 LUFS, peak -1.1 dBFS. `mix_v2.mp3` (no gap) is kept.
- **Timeline:** everything from 38.4 s on is 1.5 s later (chorus 39.9-47.1, high-five 46.2, outro 47.1-49.5,
  "Bye-bye!" 47.8). The Moral section runs on over the gap; its card fades out as the tail rings.
- **Picture:** the moral shot eases back out to the chorus framing over its first 2.4 s and holds it through the gap,
  then the 0.3 s dissolve into the chorus. Video is now 49.5 s (1485 frames). Frames 1080-1485 re-rendered in both aspects.

Not checked by ear (the reviewer can only measure): if the ring-out sounds artificial, try a longer decay or a
shorter gap (1.0 s). `GAP` in `timeline.py` and the build in this section's script are the only things to change.
