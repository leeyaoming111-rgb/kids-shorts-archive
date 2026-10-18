# Review log: Tumble & Pip Fables 8, Pip Who Cried Help

The independent reviewer (Opus subagent, `tools/REVIEWER.md`) worked from the 18 contact sheets (9 per aspect,
one frame every 0.5 s) plus `qa_report.json`, and rendered extra stills. Animatic stage: no audio yet, word times
estimated on the 100 BPM grid.

## Geometry QA before the reviewer

- Handoff run: 33 issues. After merging the coordinator kit (third arm angle, shadow-VAO override "3f 28x" in
  `render.py`) and fixing causes: 0.
- Causes fixed: the skid path brushed the giant flower (path and spin spot moved out), Pip inside the basket
  sat on the wall (re-seated and lowered 0.033 so the basket's rock neither floats nor sinks him), Pip's exit
  path clipped the rim and lid (route front-over-rim with a forward dive), the hug put Pip's wings into Tumble's
  head (Pip lands on the moral's paw pose, flies in low in front of the belly).

## Round 1: FAIL (4 HIGH, 5 MED)
- HIGH: lid lifts without Tumble touching it (he could not reach: lid raised too high). Fixed: lift angle 0.55,
  Tumble stands at the lid's right end, both paws IK-solved onto the lid's end face (measured distance about 0.1).
- HIGH: no hug / Pip across Tumble's face at 33.9. Fixed: Pip flies low in front of the belly onto the paw.
- HIGH [short]: two-shot cropped at 20.5-23.5. Fixed: wider fit.
- MED: splash read as beads (now a radial droplet burst), giggle shot hid Tumble behind the flower cap (camera
  moved), Pip on Tumble's ear at 18.5, lid straps looked like posts (removed), thinking pose (paws-to-mouth arm).

## Round 2: FAIL (2 HIGH, 4 MED)
- HIGH [short]: Pip perched on Tumble's head at 19.0-19.5 (camera yaw +28 fixes it). HIGH: no hug (the kit's
  arm reach is about 0.55 in front of the belly, so a chest hug puts Pip inside Tumble; replaced by Pip on the paw
  plus the other paw reaching round and a head tip). MED: lid set-down pop (now 0.45 s, hug starts after),
  Tumble's face behind the lid (camera).

## Round 3: FAIL (0 HIGH, 5 MED; limit is 2)
- Pip hovering across Tumble's muzzle at 33.7 (hover moved well left), wide rescue camera hid his face (own wide
  camera), wide splash framing (own wide camera).

## Round 4: PASS (0 HIGH, 2 MED accepted)
- MED accepted: the hold reads as a perch, not a hug (kit arm reach; a cheek nuzzle is a possible later polish).
- MED accepted: the open lid disc reads as a halo behind Tumble's head in some framings.
- LOW (not fixed): Pip's hover shadow on the basket, Pip at the top edge in the wide splash, small faces in the
  short giggle and two-shot, no shake-off spray, weak wave, no clear star puff on the high-five, wide specks 28-29.5.
