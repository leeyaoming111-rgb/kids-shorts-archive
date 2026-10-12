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

## Round 2

See below once it has run.
