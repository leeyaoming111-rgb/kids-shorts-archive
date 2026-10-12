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
