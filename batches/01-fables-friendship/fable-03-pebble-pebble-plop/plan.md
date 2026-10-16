# Tumble & Pip Fables 3: Pebble, Pebble, Plop!

- **job:** batch 01, fable 03 (`fable-03-pebble-pebble-plop`), on the shared kit (`common/fablekit.py`)
- **status:** animatic in both aspects, geometry QA 0, song and mix done (`../audio/fable-03/`: verse recall 100%,
  full-mix recall 98.4%, -14.4 LUFS). Independent review and final renders follow.
- **source:** Aesop's fable *The Crow and the Pitcher* (public domain), retold with our cast
- **lesson:** think it through and try something new (problem solving); bonus: counting 1 to 5
- **length:** 48.0 s (20 bars at 100 BPM)

## Prompt

A 48-second claymation fable for children aged 3 to 5:
- On a hot day in the Picnic Meadow, Pip peers into a tall clay jug by the cottage. The water is far down: "The
  water's way down there!"
- Tumble and Pip are thirsty. Pip's beak can't reach. Tumble pushes his paw into the neck and it gets stuck.
- He pulls, pulls, pulls and the paw comes out with a cork POP; he rolls backwards and lands on his feet.
- Pip has an idea. Tumble lifts a leaf tray of five pebbles from the old stone wall. Pip drops them in one by one,
  counting "One, two, three, four, five!" The water rises with every plop until it reaches the brim.
- Pip sips, and now the water reaches Tumble's tongue too: "Ahh!"
- Pip sings the moral from Tumble's paw, "Think it through, try something new!", then the series dance. In the
  button Pip's wing-splash lands on Tumble's nose.

## Lyrics

Real sung times from `audio/fable-03/song_check.json` (verse seed 3).

| Section | Time (s) | Singer | Line |
|---|---|---|---|
| Hook | 0.0-3.6 | Pip | The water's way down there! |
| Sting | 3.6-6.0 | duet (stored) | Tumble and Pip! |
| Setup A | 6.0-10.8 | Tumble | Hot, hot sun! We need a drink! |
| Setup B | 10.8-15.6 | Pip | My beak can't reach... let me think! |
| Problem A | 15.6-20.4 | Tumble | In goes my paw... uh-oh, it's stuck! |
| Problem B | 20.4-27.6 | Tumble | Pull, pull, pull... and POP! |
| Twist | 27.6-34.8 | Pip | Pebbles in! One, two, three, four, five! |
| Moral | 34.8-38.4 | Pip | Think it through, try something new! |
| Chorus | 38.4-45.6 | duet (stored) | Big or small, short or tall, / friends help friends, that's best of all! |
| Button | 45.6-48.0 | instrumental | |

Spoken gags (cast voices, eleven_v3): Tumble "Whoa-oh!" (the pop), both "Ahh!" (first sip), both "Bye-bye!".

## Shot list

Shot splits come from sung words (`PULLS`, `POP`, `COUNT`, `MORAL_CUT` in `timeline.py`), not from the grid.

| # | Shot | Camera | What happens |
|---|---|---|---|
| 1 | hook_peer | low side-on | Pip on the rim peers down the jug |
| 2 | hook_pov | looking down the neck | the water far below, a ripple |
| 3 | title_wide | wide | jug, wall, cottage; Pip fans himself with a wing; title card |
| 4 | hot_walk | medium side | Tumble pants and fans himself, walks to the jug |
| 5 | pip_try | close side | Pip leans in further and further, wobbles, can't reach, then "let me think" |
| 6 | paw_in | high three-quarter | paw into the neck on "in"; stuck on "stuck!" |
| 7 | pull | high three-quarter | three pulls, the jug lifts each time; cork POP on "POP!" |
| 8 | roll_back | wide, tight follow | backward somersault; Pip flies to the wall and points; Tumble lifts the pebble leaf |
| 9 | count | high three-quarter from the jug side | Pip drops a pebble on each count; plop splash; the water rises |
| 10 | drink | wide low | Pip sips, Tumble's tongue reaches the water |
| 11 | moral | push-in two-shot | Pip on his paw; moral card |
| 12 | chorus | medium front | the series dance and high-five |
| 13 | button_crane | crane up | Pip's wing-splash lands on Tumble's nose; "Bye-bye!" |

## Differences from Fables 1 and 2

- New corner: a clay jug by the cottage with a dry stone wall (no tree, no kite, no stream).
- A counting beat on the sung "one" to "five" with a rising water level; hot-day light grade.
- A cork-pop gag (stuck paw, backward roll) instead of a wrap or a dive.
- Pip solves it by thinking and dropping things, Tumble carries (Fable 1: pecking, Fable 2: tugging).

## New assets

- Hollow clay jug (`props_f3.py`, built from the shared SDF primitives) with a water disc that rises per pebble.
- Pebbles and a leaf tray built from existing meshes (`stone`, `leaf`); the stone wall is a row of stones.
- Hot-day grade wraps `fablekit.render_frame`; dynamic QA ignore for the jug only while it is stuck on his paw.
