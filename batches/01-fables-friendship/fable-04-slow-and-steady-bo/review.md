# Review log: Tumble & Pip Fables 4, Slow and Steady Bo

An independent reviewer (Opus, general-purpose subagent, `tools/REVIEWER.md`) worked from contact sheets with one frame
every 0.5 s in both aspects (9:16 Short, 16:9 episode framing), `qa_geom.py` output, and about 150 extra stills it
rendered itself. It also ran its own stricter collision check (every frame at 30 fps, 4000 sample points per mesh, 5 mm
tolerance). Round 1 ran on the planned timing; from the moment the real song existed, all later rounds ran on the real
word times (song seed 2, see `audio/fable-04/`).

## Geometry QA

0 issues at every stage after the first restaging (the early nap and finish layouts produced tail and arm
penetrations, fixed by moving Tumble's nap and arrival spots).

## Round 1: FAIL (6 HIGH, 6 MED)

The reviewer found two classes of problems.

- **The real song broke the cut (HIGH).** The music model sings the Twist line at the END of its section (31.8 s), not
  the start, so the shot splits derived from it ran past the section and the finish shot got a negative length. Fixed:
  the story order was rebuilt around the song. Bo reaches the stump in the instrumental race break (29.6 s), Pip calls,
  Tumble jolts on his name (32.2 s), cut to the spin, cut to the finish with Tumble skidding in and "Well done, Bo!",
  then the moral. Every split is clamped.
- **The race did not read.** Tumble barely left the line (no speed), Bo was not tiny and far in the show-off, Bo never
  passed the sleeper, the leg spin was invisible, Bo's face was inside the stump. Fixed:
  - The course is now 15 units long: Tumble dashes about 11 units with dust puffs every 0.1 s, and the tracking camera
    lags so he surges across the frame; Bo's pace curve keeps him far back in the show-off.
  - The nap moved under the giant mushroom, and Bo passes him in the foreground (cameras raised so Bo reads clearly in
    front, never behind his head).
  - Wake: higher hop with hang-time, legs pump, longer shot, camera moved to the side.
  - The stump shot is side-on; Bo's nose rests on the stump's side.
- **MED, fixed:** Pip hidden behind Bo at the start line (pebble moved), small snore bubbles (bigger), cap bob
  (bigger, plus a breathing bob), Bo's profile mouth (smaller), hand over mouth on "Bye-bye" (a raised wave).

## Round 2: FAIL (0 HIGH, 6 MED)

Remaining: show-off distance, nap close to the stump, leg spin from behind, nose touch hidden, high-five missing,
bye-bye paw. Fixed: Bo's pace curve (exponent 1.4) and a closer shoulder camera; the side-on stump shot; the 16:9
lie-down camera pushed away from the stump; a longer wake shot (1.4 s, spin window 0.8 s) from the side with a larger
leg pump; the bye-bye paw moved off the mouth.

## Round 3: PASS (0 HIGH, 1 MED)

The only MED left is that the chorus shows no high-five. That choreography belongs to the series dance in
`common/fablekit.py` (`dance_tumble` / `dance_pip`, `HIGH_FIVE`), which the brief says not to change, and it behaves
the same in Fables 1 and 2. LOW notes left as they are:
- the bye-bye wave is small (paw at cheek height) in the far crane shot;
- the leg pump reads as a hop-run from a three-quarter view rather than a full cartoon wheel;
- Bo touches the stump about 4.4 s before Tumble arrives (the touch falls in the instrumental break);
- the sleeping fox peeks over Bo's shell at the left edge of the 16:9 stump shot, and the stump sits at the right edge
  of the 16:9 lie-down shot (the nap is only 4.2 units from the stump);
- the title shot is hazy; the flag's base is hidden behind Tumble in the moral and chorus.
