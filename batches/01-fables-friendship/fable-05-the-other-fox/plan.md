# Tumble & Pip Fables 5: The Other Fox

- **job:** batch 01, fable 05 (`fable-05-the-other-fox`)
- **status:** plan written; animatic next.
- **series:** Tumble & Pip (Fables About Friendship). Batch plan: [../plan.md](../plan.md)
- **source:** Aesop's fable *The Dog and His Reflection* (public domain), retold with our cast, gags and song
- **lesson (SEL):** be happy with what you have, and share it
- **length:** 48.0 s (20 bars at 100 BPM). Episode cut: 41.2 s (drops the sting and the button)
- **aspects:** 9:16 Short (`render.py`) and 16:9 episode framing (`render.py --wide`), same scene and timing

## Prompt

A 48-second claymation fable for children aged 3 to 5. Tumble the clay fox cub stands in the middle of a log bridge
over the meadow stream with a shiny red apple in his paw. He looks down and sees "another fox" in the water, holding an
apple too. Pip flies in with a tiny berry and puts it down on the log. Tumble shows off his apple, then looks down
again: the other fox's apple looks BIGGER. He pulls a silly face at the other fox, and the other fox pulls exactly the
same face back. "I want THAT one!" He reaches down with both paws, his own apple slips out, splash, and it bobs away
down the stream while a ripple turns the other fox all wobbly. Pip hops over, puts his berry in Tumble's paw and pecks
it in half: one half each. Tumble laughs, eats his half and says Pip's berry is the best. With Pip on his paw, Pip
sings the moral, they do the series dance on the log while their reflections dance too, and Pip copies Tumble's
silly face for the goodbye. Gentle storybook folk at 100 BPM in D major with acoustic guitar, glockenspiel, bassoon
for Tumble and tin whistle for Pip.

## Change from the batch plan

- The hook stays in story order (as Fable 1 decided): Tumble is already on the bridge when he spots "another fox", so
  the hook image and the start of the story are the same moment, not a flash-forward.
- The moral is polished to fit the 3-syllables-a-second budget: "Love what you've got, and share it!"
  (the batch plan's "Be happy with what you've got, and share it!" is 11 syllables in a 3.6 s section).
- The reflection's apple grows a little while Tumble sings "BIGGER" (water makes it look bigger), so the want is
  readable without words.

## Lyrics (sung by the ElevenLabs Music model's own singers)

| Section | Time (s) | Singer | Line |
|---|---|---|---|
| Hook | 0.0-3.6 | Tumble | Hey! Who's that fox down there? |
| Sting | 3.6-6.0 | duet (stored) | Tumble and Pip! |
| Setup A | 6.0-10.8 | Tumble | My shiny apple, red and round! |
| Setup B | 10.8-15.6 | Tumble | That fox has a BIGGER one! |
| Problem A | 15.6-20.4 | Tumble | Silly face! He copies me! |
| Problem B | 20.4-27.6 | Tumble | I want THAT one! Oh no, SPLASH! (+ instrumental: the apple bobs away, the reflection wobbles) |
| Twist | 27.6-34.8 | Pip | Here's my berry, half for you! (+ instrumental: they share) |
| Moral | 34.8-38.4 | Pip | Love what you've got, and share it! (moral card) |
| Chorus | 38.4-45.6 | duet (stored) | Big or small, short or tall, / friends help friends, that's best of all! |
| Button | 45.6-48.0 | instrumental | happy ending |

Spoken gags in the fixed cast voices (`eleven_v3`, audio tags, stability 0.0), all in sung rests:
- Tumble "Blehhh!" (about 19.1 s, the silly face, both foxes at once)
- Tumble "Whoa, wobbly!" (about 25.0 s, the ripple wobble)
- Tumble "Your berry is the best!" (about 32.4 s, after the first bite)
- both "Bye-bye!" (about 46.3 s)

Syllable budget: every sung line is 6 to 8 syllables in a 3.6 s or longer section (at most 2.4 syllables a second).

## Shot list

| # | Time (s) | Camera | What happens |
|---|---|---|---|
| 1 | 0.0-3.6 | low, along the stream, push-in | Tumble mid-bridge, apple in paw, peers down; his mirror image ("another fox" with an apple) fills the water below; on "Hey!" he startles and points down |
| 2 | 3.6-6.0 | high wide establishing | stream, log bridge, banks; Pip flies in with a berry in his beak and sets it on the log; title card "Tumble & Pip / Fables / The Other Fox" |
| 3 | 6.0-10.8 | medium, eye level, three-quarter | Tumble turns to Pip and lifts his apple high on "shiny", "red", "round"; Pip cheers |
| 4 | 10.8-15.6 | water close-up, tilt down | the reflection's apple, Tumble's real paw and apple at the top of frame; on "BIGGER" the water apple swells with a sparkle |
| 5 | 15.6-~17.6 | close front, slight high angle | Tumble pulls a silly face at the water: paws at his ears waggling, tongue out, head wobble |
| 6 | ~17.6-20.4 | low wide, along the stream | both foxes pull the same face at the same time ("He copies me!"), then "Blehhh!" |
| 7 | 20.4-~23.6 | side-on medium from the near bank | "I want THAT one!" he leans and reaches down with both paws; on "Oh no" the apple slips; on "SPLASH" it hits the water with a splash |
| 8 | ~23.6-27.6 | low along the stream, wider | ripple rings spread, the reflection wobbles ("Whoa, wobbly!"), the apple bobs away towards the camera and out of frame; Tumble droops |
| 9 | 27.6-31.2 | macro, side-on | Pip hops over with the berry, puts it in Tumble's open paw ("Here's my berry"), pecks it in two on "half" (puff) |
| 10 | 31.2-34.8 | medium two-shot | Tumble laughs, eats his half ("Your berry is the best!"), Pip gulps the other half |
| 11 | 34.8-38.4 | low along-stream push-in two-shot | Pip hops onto Tumble's paw; the moral card; the reflections copy them |
| 12 | 38.4-45.6 | low along-stream medium | the series dance on the log (Pip rides the paw, sway every second beat, paw-to-wing high-five, star puff), mirrored in the water |
| 13 | 45.6-48.0 | crane up | both wave "Bye-bye!"; Pip copies the silly face, Tumble laughs |

Camera types: low water-level, high wide, medium three-quarter, water close-up (tilt down), close front, side-on,
macro, two-shot, crane. 12 hard cuts. Every shot is 1.3 s or longer.

## How it differs from the rest of the batch

- **Set corner:** the log bridge over the meadow stream (Fables 1 and 2 are on the grass by the stump and under the
  apple tree). First fable played over water, and the first with a mirror world.
- **Camera plan:** built round the along-the-stream view, so the frame is split by the water line: the vertical 9:16
  frame holds the fox and his reflection one above the other. No other fable uses this axis.
- **Gags:** a copycat silly face and a wobbly reflection (Fable 1: kite wrap and spin; Fable 2: leaf-pile dive).
- **Dance:** the series dance is mirrored in the stream (same move, new picture).

## New assets (all from primitives in `render.py`; `meshes.py` is untouched)

- **Reflection:** every draw near the stream is drawn again mirrored about the water line before the scene, lit with
  its unmirrored normals (so it is lit like the real thing) and without shadows; the ground is redrawn with the stream
  bed cut out, then a tinted, semi-transparent water plane (the kit shader's `fade` alpha with blending) covers it.
  No new shader. The wobble is a per-part sideways ripple applied to the mirrored copies only.
- **Stream ground:** the kit's ground re-meshed with a cleaner channel under the water line (same `ground_h` outside
  the channel, so walking and QA heights are unchanged).
- **Log bridge:** a bark-tinted stick capsule (radius 0.2), pale end-grain discs, a branch stub with a leaf.
- **Water:** flat plane, drifting flow streaks, ripple rings and a splash (tinted balls).
- **Berry halves:** the berry mesh squashed to two halves; the apple floats half under the water.
- **Silly face:** a pink tongue (tinted ball) plus paws at the ears and a head wobble; Pip gets a tiny tongue for the
  button.
