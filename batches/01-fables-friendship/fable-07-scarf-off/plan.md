# Tumble & Pip Fables 7: Scarf Off!

- **job:** batch 01, fable 07 (`fable-07-scarf-off`)
- **status:** in progress (plan written, animatic next)
- **series:** Tumble & Pip (Fables About Friendship). Batch plan: [../plan.md](../plan.md)
- **source:** Aesop's fable *The North Wind and the Sun* (public domain), retold with our cast, gags and song
- **lesson (SEL):** gentle and kind works better than pushing hard
- **length:** 48.0 s (20 bars at 100 BPM). Episode cut: 41.2 s (drops the sting and the button)
- **aspects:** 9:16 Short (`render.py`) and 16:9 episode framing (`render.py --wide`), same scene and timing

## Prompt

A 48-second claymation fable for children aged 3 to 5. On the little hill by Tumble's cottage, Tumble the clay fox
cub wears his long red-and-cream striped scarf. Two friendly clay faces float in the sky: a puffy Wind cloud and a
smiling Sun. Pip the tiny blue bird is the referee, with a yellow whistle, perched on the garden fence post. Wind
goes first: he puffs out his cheeks and blows, whoosh. Tumble only hugs his scarf tighter while its ends stream out
and his head wobbles, Pip is blown off the post and clings to a big flower, and one gust spins Tumble round like a
weathervane. Wind runs out of puff and laughs. Then the Sun shines softly, the sky warms slowly, Tumble smiles, pulls
off his scarf, lets it fall on the grass and stretches out in the sunshine. Pip blows the whistle for the Sun. Pip
sings the moral, gentle and kind works best, and the friends do the series dance. At the end Wind blows a soft,
cool breeze and Wind and Sun wave bye-bye from the sky. Gentle storybook folk at 100 BPM in D major with acoustic
guitar, glockenspiel, bassoon for Tumble and tin whistle for Pip.

## Adaptation

- Aesop's Wind and Sun argue about who is stronger and test it on a traveller's cloak. Ours is a friendly game with
  Pip as referee; Wind and Sun smile at each other the whole time and Wind laughs when he loses.
- Nothing scary: Wind's face is a soft round cloud with rosy cheeks, his gusts are playful, Pip clings to the flower
  giggling ("Whoa-whoa!"), nobody falls or gets hurt.
- The sky goes a little cooler and paler while Wind blows and warms up when the Sun shines. Both changes ramp over
  1.2 to 1.6 s (no-flashing rule: no full-frame brightness change faster than 0.5 s).

## Lyrics (sung by the ElevenLabs Music model's own singers)

| Section | Time (s) | Singer | Line |
|---|---|---|---|
| Hook | 0.0-3.6 | Pip | Who can get the scarf off? |
| Sting | 3.6-6.0 | duet (stored) | Tumble and Pip! |
| Setup A | 6.0-10.8 | Pip | Wind and Sun, a friendly game! |
| Setup B | 10.8-15.6 | Tumble | My stripy scarf is snug and warm! |
| Problem A | 15.6-20.4 | Tumble | Huff and puff! I'll hold on tight! |
| Problem B | 20.4-27.6 | Tumble | Round and round... it won't come off! (+ instrumental gag break) |
| Twist | 27.6-34.8 | Pip | Sun's turn! Shine so soft and kind... (+ instrumental break: scarf off) |
| Moral | 34.8-38.4 | Pip | Gentle and kind works best! (moral card) |
| Chorus | 38.4-45.6 | duet (stored) | Big or small, short or tall, / friends help friends, that's best of all! |
| Button | 45.6-48.0 | instrumental | happy ending |

Spoken gags in the fixed cast voices (`eleven_v3`, audio tags, stability 0.0): Pip "Whoa-whoa!" (about 23.7 s,
clinging to the flower), Tumble "Ahh... scarf off!" (about 31.9 s, as the scarf slips free), both "Bye-bye!"
(about 46.3 s). Syllable budget: every line at or under 3 syllables per second (the densest is Setup B, 8 syllables
in 4.8 s).

## Shot list

| # | Time (s) | Camera | What happens |
|---|---|---|---|
| 1 | 0.0-3.6 | low angle, push-in | Tumble on the hill in his striped scarf; Wind (left) and Sun (right) lean down from the sky; Pip hovers beside him and sings the question, then peeps the whistle |
| 2 | 3.6-6.0 | wide establishing | the hill, the cottage, the garden fence; Pip lands on the fence post; title card "Tumble & Pip / Fables / Scarf Off!" |
| 3 | 6.0-8.6 | sky close-up (cutaway) | Wind and Sun turn to each other, nod and smile: a friendly game |
| 4 | 8.6-10.8 | macro, side-on | Pip on the post lifts the whistle and blows it, wing pointing up: go! |
| 5 | 10.8-15.6 | medium front | Tumble pats and hugs his scarf, proud and cosy, little happy bounce |
| 6 | 15.6-17.4 | sky close-up, push-in | Wind fills his cheeks (they swell) and blows, whoosh; wind streaks fly out |
| 7 | 17.4-20.4 | medium low three-quarter | Tumble hugs the scarf to his chest, leans into the wind, head wobbling, scarf ends streaming; Pip is blown backwards off the post towards the flower |
| 8 | 20.4-23.4 | high angle wide | the big gust spins Tumble round twice like a weathervane, scarf streaming straight out downwind; he wobbles to a stop, still wearing it |
| 9 | 23.4-25.2 | macro | Pip clings to the big flower stem, feathers fluttering, "Whoa-whoa!" |
| 10 | 25.2-27.6 | sky medium | Wind runs out of puff: cheeks go down, eyes squeeze in a laugh, he drifts back a little; the Sun smiles |
| 11 | 27.6-30.0 | sky close-up, slow push-in | the Sun's turn: rays turn slowly, the sky warms over 1.6 s |
| 12 | 30.0-32.6 | medium front | Tumble relaxes and fans himself, takes the scarf end and pulls it, the scarf slides round his neck and off ("Ahh... scarf off!") |
| 13 | 32.6-34.8 | overhead | he lets the scarf fall on the grass and lies down in the sunshine; Pip peeps the whistle and points at the Sun |
| 14 | 34.8-38.4 | push-in two-shot | Tumble stands; Pip hops onto his raised paw; the moral card |
| 15 | 38.4-45.6 | medium front | the series dance: Pip rides Tumble's paw, they sway on every second beat, paw-to-wing high-five with a star puff |
| 16 | 45.6-48.0 | crane up | Wind blows a soft breeze (flowers sway, Tumble's tail wags); the camera cranes up to Wind and Sun waving and winking |

Camera types: low angle, wide, sky close-up cutaway, macro side-on, medium, high angle, overhead, push-in, crane.
15 hard cuts. Shortest shot 1.8 s.

## How it differs from the rest of the batch

- **Set corner:** the hilltop by Tumble's cottage with a garden fence, the cottage close behind. Fable 1 used the
  stump-and-stream corner, Fable 2 the apple tree. No stump, apple tree or basket in this Short.
- **New characters:** Wind and Sun as soft clay faces in the sky. First Short whose antagonists are in the sky, and
  the first with sky cutaways (shots 3, 6, 10, 11 and the crane to the sky in the button).
- **Gag:** the weathervane spin with the scarf streaming straight out, and Pip clinging to a flower; nothing like the
  kite wrap (Fable 1) or the leaf-pile dive (Fable 2).
- **Light:** the first Short whose sky and key light change with the story (cool and pale in the wind, warm in the sun).
- **Camera plan:** low-angle opener looking up at the sky (Fable 1 opened tracking, Fable 2 on a low reach under the
  tree), a high-angle spin and an overhead sunbathe.
- **Pip's role:** referee with a whistle (Fable 1 helper, Fable 2 idea-giver).

## New assets (all built in `render.py` from existing meshes; `meshes.py` unchanged)

- Wind: the scene cloud mesh, soft blue-white, with clay eyes, rosy cheeks, puff cheeks (balls that swell) and a
  round blowing mouth.
- Sun: the scene sun mesh with a face; the rays turn while the face stays still.
- Scarf: a chain of 40 short capsule segments in red, cream and teal stripes. Worn as a collar plus two hanging ends;
  the ends stream downwind; taking it off slides the chain round his neck and through his paw; it then lies on the grass.
- Whistle: a tiny yellow capsule with a ball, on Pip's chest; it moves up to his beak when he blows it.
- Garden fence: posts and rails from the stick mesh. Big flower: the scene flower at 4 times its size.
- Wind streaks: thin white capsules flying across in the wind shots, kept above and behind Tumble's head.
- Sky and key light ramps through `HOOKS["sky"]` and an override of the kit's `draw_pass` (key light intensity).

## Checks

Animatic: to do.
