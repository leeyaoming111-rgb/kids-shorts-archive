# Tumble & Pip Fables 2: Sour Apples?

- **job:** batch 01, fable 02 (`fable-02-sour-apples`), the first fable built on the shared kit (`common/fablekit.py`)
- **status:**
  - Animatic built in both aspects; geometry QA 0 issues; independent review in progress.
  - Song, voices and mix done: `../audio/fable-02/` has verse recall 100%, mix recall 98% and -14.4 LUFS.
- **source:** Aesop's fable *The Fox and the Grapes* (public domain), retold with our cast
- **lesson (SEL, social-emotional learning):** don't pretend you didn't want it ("sour grapes"); ask a friend for help
- **length:** 48.0 s (20 bars at 100 BPM). Episode cut: 41.2 s

## Prompt

A 48-second claymation fable for children aged 3 to 5:
- Under a big apple tree in the Picnic Meadow, Tumble the fox cub stretches on tiptoe for a red apple just above his
  head. He jumps three times and misses.
- He takes a run-up for one more big jump, sails past the apple and dives head-first into a pile of autumn leaves,
  with only his legs and tail sticking out.
- He pops out with leaves on his head, crosses his arms and sniffs: "Those apples are sour anyway!"
- Pip flutters up to his face: "Let's try together, you and me!" Tumble climbs onto the old stump, and Pip flies up
  and tugs the apple, tug, tug, tug, until it drops into Tumble's paws. One crunchy bite: "Mmm, SWEET!"
- Pip sings the moral, "Don't say sour, ask a friend!", from Tumble's paw. They do the series dance, and Pip hops onto
  the apple for a peck as they wave goodbye.

## Lyrics

| Section | Time (s) | Singer | Line |
|---|---|---|---|
| Hook | 0.0-3.6 | Tumble | One red apple, way up high! |
| Sting | 3.6-6.0 | duet (stored) | Tumble and Pip! |
| Setup A | 6.0-10.8 | Tumble | Jump, jump, jump! I'll reach it, I'll try! |
| Setup B | 10.8-15.6 | Tumble | One more big jump... whoa! |
| Problem A | 15.6-20.4 | Tumble | Those apples are sour anyway! |
| Problem B | 20.4-27.6 | Pip | Let's try together, you and me! |
| Twist | 27.6-34.8 | Pip | Tug, tug, tug... here it comes! |
| Moral | 34.8-38.4 | Pip | Don't say sour, ask a friend! |
| Chorus | 38.4-45.6 | duet (stored) | Big or small, short or tall, / friends help friends, that's best of all! |
| Button | 45.6-48.0 | instrumental | |

Spoken gags (cast voices, eleven_v3):
- Tumble "Oof!" (landing in the leaves)
- Tumble "Mmm, SWEET!" (the bite)
- both "Bye-bye!"

## Shot list

| # | Time (s) | Camera | What happens |
|---|---|---|---|
| 1 | 0.0-3.6 | low angle, looking up | on tiptoe under the apple, reaching |
| 2 | 3.6-6.0 | wide | tree, stump, leaf pile; Pip on the stump; title card |
| 3 | 6.0-10.8 | medium side | three jumps on the three sung "jump"s |
| 4 | 10.8-13.2 | wide, following | run-up, big leap past the apple, the dive begins |
| 5 | 13.2-15.6 | close on the pile | head-first landing, legs and tail kicking, leaves fly up |
| 6 | 15.6-20.4 | medium front | pops out with leaves on his head; arms crossed, nose up |
| 7 | 20.4-24.0 | two-shot | Pip at his face, wing up; Tumble uncrosses his arms, nods |
| 8 | 24.0-27.6 | wide | walks to the stump, hops up; Pip flies up to the apple |
| 9 | 27.6-31.2 | side-on close-up in the tree | Pip grips the apple and tugs on each "tug"; it swings and comes loose |
| 10 | 31.2-34.8 | low medium | the apple drops into his paws; the bite; Pip cheers |
| 11 | 34.8-38.4 | push-in two-shot | Pip on his paw, apple in the other paw; moral card |
| 12 | 38.4-45.6 | medium front | the series dance and high-five |
| 13 | 45.6-48.0 | crane up | Pip hops onto the apple for a peck; "Bye-bye!" |

## Differences from Fable 1

- New corner of the meadow: under a big apple tree (scale 2.2), with an autumn leaf pile. There is no kite and no
  stream in frame.
- A different gag shape: a slapstick dive and a grumpy pose, instead of a wrap and spin.
- Pip helps by pulling, not pecking a knot.
- Tumble stands on the stump (in Fable 1, Pip perched on it).

## Build notes

- The apple hangs just under the canopy (centre 2.95). Tumble's paws only reach about 1.36 high (below his own ears),
  so the apple sits just above his jumping ears, and even standing on the stump he can't quite reach it.
- Pip tugs from the outer side of the apple, below the leaves, and is filmed side-on.
- The dive uses a pitch about the middle of his body (`fox_mats_p`); geometry QA excludes the fox from the ground
  check while he dives.
- First geometry QA run: 73 issues, all layout (the stump was too close to his spot and to the trunk, and Pip's tug
  spot was inside the leaves). After rearranging the set: 0.
