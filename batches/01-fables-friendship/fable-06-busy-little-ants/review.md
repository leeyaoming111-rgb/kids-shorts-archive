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
