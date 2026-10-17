# Review log: Tumble & Pip Fables 6, Busy Little Ants

Independent reviewer (Opus subagent) followed `tools/REVIEWER.md`, working from the 18 contact sheets (both aspects)
plus extra stills and `out/qa_report.json`. Animatic stage: no audio, word times estimated on the 100 BPM grid.

## Geometry QA before the reviewer

- The previous worker took QA from 13 to 2 issues. The held seed touched his body at 16.6-16.9 s.
- After merging the kit update and using the two-paw hold [0.3, 1.25, 0.62] with the seed held further out: **0 issues**.
- Kit bug overridden in `render.py`: the shadow VAO uses "3f 28x" (the kit's "3f 36x" misreads 40-byte vertices).

## Round 1: FAIL (1 HIGH, 8 MED)

- **HIGH [wide] ant_hat:** the ant line sat behind the caption band and his feet were off the bottom. Fixed: the wide
  camera frames higher and wider (fit height 1.9, lift 0.2).
- **MED [wide] title:** the title ran across his face. Fixed: camera aimed lower/left so the title clears him.
- **MED [wide] pip_work:** he was cut off at mid-face. Fixed: wider fit and a higher target.
- **MED [both] pip_carry:** the seed floated ahead of Pip's beak. Fixed: seed pulled back to the beak tip.
- **MED [both] ant_hat held seed:** one paw did not touch it. Fixed: the held seed is longer and the paws meet both ends.
- **MED [short] chilly:** the stream crossed his face. Fixed: camera pitched down (26 degrees).
- **MED [both] snack:** Pip stood on the ants on screen. Fixed: Pip moved to the side and forward.
- **MED [short] next_day:** the door was never in frame. Fixed: the camera aims between Tumble and the door; Pip's wait spot moved.
- **MED [both] chilly gag:** the sneeze did not match the plan. Fixed: it is now the "Brrrr!" shiver with a crossed-arm
  tummy hug, and the flake is shaken off and falls; caption and SPOKEN line renamed.
- LOW items fixed: button flake doubled in size. Not done (LOW): cross-eyed flake, Tumble up on his feet in title_wide.

## Round 2: FAIL (0 HIGH, 1 MED)

- **MED [wide] pip_carry:** his head was above the top edge. Fixed: higher target and wider fit.
- LOW fixed: Pip moved off the ants at the door; next_day starts further left; chilly wide fit taller.

## Round 3: PASS (0 HIGH, 0 MED)

Wide pip_carry head, Pip at the door and the chilly/next_day framings re-checked. LOW left: 9:16 chilly framing small,
cross-eyes on the flake, Tumble in the leaves in title_wide, small button flake.

## Round 4 (real song timing, a74eb9b): FAIL (1 HIGH, 1 MED)

- **HIGH [both] ant_hat:** "ant" is sung late (19.46), so the seed landed at 19.46 and tipped off at 19.6 (balance gag gone),
  and the spoken "Wibble-wobble!" fell on the next shot over the sung "Brr,". Fixed: the seed lands on "me," (17.58), toss
  at 17.03, TIP_OFF guarded to at least SEED_ON + 1.2 (19.6), and the spoken gag is dropped (the sung line carries it).
- **MED [both] chilly:** the spoken "Brrrr!" overlapped the sung "rumbles...". Fixed: it now starts at 25.08 after the
  sung line, with the shiver tied to the same time.
- LOW fixed: "Mmm, crunchy!" moved to 31.85, after the sung "snack!".

## Round 5: PASS (0 HIGH, 0 MED)

Every event lands on its sung word, the gags no longer collide with the singing, no pops or caption overlaps in either
aspect. Remaining LOW (polish only): the "Brrrr!" caption waits about 0.5 s for the sung caption to fade; the moral card
waits for "Help"; the flake touches his forehead before his nose; no cross-eyes; Tumble sits in the leaves in title_wide;
the button flake is small; 9:16 chilly framing is small.
