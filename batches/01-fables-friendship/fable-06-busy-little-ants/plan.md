# Tumble & Pip Fables 6: Busy Little Ants

- **job:** batch 01, fable 06 (`fable-06-busy-little-ants`)
- **status:** plan written; animatic in progress.
- **series:** Tumble & Pip (Fables About Friendship). Batch plan: [../plan.md](../plan.md)
- **source:** Aesop's fable *The Ant and the Grasshopper* (public domain), retold with our cast, gags and song
- **lesson (SEL):** helping a little every day; sharing with a friend who didn't plan ahead
- **length:** 48.0 s (20 bars at 100 BPM). Episode cut: 41.2 s (drops the sting and the button)
- **aspects:** 9:16 Short (`render.py`) and 16:9 episode framing (`render.py --wide`), same scene and timing

## Prompt

A 48-second claymation fable for children aged 3 to 5, on an autumn afternoon in the Picnic Meadow. Tumble the clay
fox cub lies on his tummy in the fallen leaves while a line of tiny, friendly clay ants marches past his nose, each
carrying a seed to the little door in their anthill. Tumble jumps into the leaves and calls "Come and play!". Pip
answers for the ants, "Work first, play later!", and hops along the line carrying one seed in his beak. Tumble pretends
to be an ant with a big seed balanced on his head; he wobbles in a wide-legged stance and the whole ant line marches
neatly underneath him. The wind turns chilly, the first snowflake of the year lands on Tumble's nose, he shivers and
his tummy rumbles. Pip knocks on the ants' tiny door, it swings open, and the ants carry out seeds to share with
Tumble on a big leaf. The next morning Tumble carries the biggest seed of all to their door. With Pip on his paw he
sings the moral, "Help a little every day!", and they do the series dance. Gentle storybook folk at 100 BPM in D major
with acoustic guitar, glockenspiel, bassoon for Tumble and tin whistle for Pip.

## Softening (ages 3 to 5)

- Aesop's ending (the ants refuse the hungry grasshopper) becomes sharing: the ants open their door and share.
- Tumble is only a little cold and hungry: a shiver and a tummy rumble, nothing more. Snow is one gentle flake, then a
  light flurry.
- Nobody is told off. The fix is Tumble choosing to help the next day.

## Lyrics (sung by the ElevenLabs Music model's own singers)

| Section | Bars | Time (s) | Singer | Line | Syll. | Syll/s |
|---|---|---|---|---|---|---|
| Hook | 1.5 | 0.0-3.6 | Tumble | Little ants, where do you go? | 7 | 1.9 |
| Sting | 1 | 3.6-6.0 | duet (stored) | Tumble and Pip! | | |
| Setup A | 2 | 6.0-10.8 | Tumble | Crunchy leaves! Come and play! | 6 | 1.3 |
| Setup B | 2 | 10.8-15.6 | Pip | Work first, play later, okay? | 8 | 1.7 |
| Problem A | 2 | 15.6-20.4 | Tumble | Look at me, I'm an ant! | 6 | 1.3 |
| Problem B | 3 | 20.4-27.6 | Tumble | Brr, a snowflake! My tummy rumbles... (+ instrumental gag break) | 9 | 1.3 |
| Twist | 3 | 27.6-34.8 | Pip | Knock, knock! The ants share their snack! (+ instrumental break) | 7 | 1.0 |
| Moral | 1.5 | 34.8-38.4 | Tumble | Help a little every day! (moral card) | 7 | 1.9 |
| Chorus | 3 | 38.4-45.6 | duet (stored) | Big or small, short or tall, / friends help friends, that's best of all! | | |
| Button | 1 | 45.6-48.0 | instrumental | happy ending | | |

Every line is one idea and well under 3 syllables per second. No lyric line repeats (copyright-filter rule).

Story events follow the sung words (`word_times`): the leaf burst on "leaves", the jump on "play", the seed onto his
head on "ant", the flake landing on "snowflake", the tummy hug on "rumbles", Pip's two pecks on the door on "knock".

Spoken gags in the fixed cast voices (`eleven_v3`, audio tags, stability 0.0):
- Tumble "Wibble-wobble!" (about 18.6 s, the seed wobbling on his head)
- Tumble "Brrr!" (about 24.4 s, shivering in the first snow)
- Tumble "Mmm, crunchy!" (about 31.8 s, the shared seed snack)
- both "Bye-bye!" (about 46.3 s)

## Shot list

| # | Time (s) | Shot | Camera | What happens |
|---|---|---|---|---|
| 1 | 0.0-3.6 | `hook_ants` | macro at ant height | Tumble lies on his tummy in the leaves, chin up; the ant line marches past right in front of his nose, each ant with a seed; his eyes follow them |
| 2 | 3.6-6.0 | `title_wide` | wide establishing, high | the autumn corner: orange trees, the anthill with its little door, the ant line, the leaf pile; Tumble up on his feet, Pip on the anthill; title card |
| 3 | 6.0-10.8 | `leaf_play` | medium, front three-quarter | Tumble jumps into the leaf pile on "leaves" (burst), and again on "play", waving to the ants |
| 4 | 10.8-13.8 | `pip_work` | macro side-on | Pip beside the marching line sings "Work first, play later"; nods to the beat |
| 5 | 13.8-15.6 | `pip_carry` | low tracking | Pip picks up a seed in his beak and hops along at the end of the ant line |
| 6 | 15.6-20.4 | `ant_hat` | low angle from ant height | Tumble balances a big seed on his head, legs wide; he wobbles ("Wibble-wobble!") while the ant line marches neatly between his feet; the seed tips off into the leaves |
| 7 | 20.4-24.0 | `snowflake` | face close-up | the sky cools; one snowflake drifts down and lands on his nose on "snowflake"; he goes cross-eyed at it |
| 8 | 24.0-27.6 | `chilly` | wide, slightly high | a light flurry; Tumble shivers ("Brrr!") and hugs his rumbling tummy; the last ants go in at their door; Pip flies to the anthill |
| 9 | 27.6-30.4 | `knock` | side-on medium at the door | Pip pecks the tiny door on each "knock", it swings open, ants march out with seeds |
| 10 | 30.4-32.6 | `snack` | overhead three-quarter | Tumble on his tummy in front of the door; the ants set seeds on a big leaf by his nose; "Mmm, crunchy!" |
| 11 | 32.6-34.8 | `next_day` | tracking, low | next morning (brighter sky, a little frost): Tumble carries the biggest seed in both paws to the ants' door and sets it down; the ants wave their feelers |
| 12 | 34.8-38.4 | `moral` | push-in two-shot | Pip hops onto Tumble's paw; moral card |
| 13 | 38.4-45.6 | `chorus` | medium front | the series dance and high-five; the ants sway in their line behind |
| 14 | 45.6-48.0 | `button_crane` | crane up | a snowflake lands on Pip's head, he shakes it off with a wiggle; "Bye-bye!" as the camera rises over the anthill |

Camera types: macro, wide establishing, medium, side-on macro, low tracking, low angle, close-up, wide high, overhead,
push-in, crane. 13 hard cuts. Shortest shot 1.8 s.

## How it differs from the rest of the batch

- **Set corner:** the anthill corner by the meadow's oak, with Tumble's cottage in the distance. No apple tree, stump
  or stream in frame (Fables 1 and 2 use those).
- **Season:** the first autumn grade of the batch (orange trees, golden grass, cooler sky as the wind turns), and the
  first snow.
- **Gag:** a balancing gag with a crowd passing under him; Fables 1 and 2 have a wrap-up and a dive.
- **Camera plan:** opens at ant height (macro) rather than a low tracking shot or a reach; the hook is a close-up with
  Tumble lying down, not standing.
- **Cast:** the first group of extra characters (the ant line), reused in Fable 10.

## New assets (all built from existing primitives, no `meshes.py` change)

- **Ant** (`draw_ant` in `render.py`, marked block for Fable 10): three low-poly clay balls (head, thorax, abdomen),
  six stick legs with a walking tripod gait, two stick feelers with ball tips, big kit eyes. Drawn instanced along a
  path (`ant_line`) with per-ant phase, carrying a seed.
- **Seeds:** tan clay ellipsoids (ball mesh), one big "biggest seed".
- **Anthill:** a squashed clay mound (ball mesh) with a dark arched doorway and a little wooden door on a hinge.
- **Snowflakes:** three crossed sticks with a ball centre, drifting with a gentle sway.
- **Autumn grade:** sky colours and tints on the trees and ground (multiply tints, no shader change).
- **Leaf pile:** scattered kit leaves, laid out differently from Fable 2's.
