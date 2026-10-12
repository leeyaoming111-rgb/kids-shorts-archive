# Tumble & Pip Fables 9: Stronger Together!

- **job:** batch 01, fable 09 (`fable-09-stronger-together`), built on the shared kit (`common/fablekit.py`)
- **status:** plan written; animatic in progress.
- **source:** Aesop's fable *The Bundle of Sticks* (public domain), retold with our cast
- **lesson (SEL, social-emotional learning):** one alone is easy to break; together we are strong
- **length:** 48.0 s (20 bars at 100 BPM). Episode cut: 41.2 s

## Prompt

A 48-second claymation fable for children aged 3 to 5:
- On the stream bank of the Picnic Meadow, a big bundle of twigs tied with grass lies like a little bench across the
  old stump and a round rock. Tumble the fox cub holds up one little twig and snaps it in two: "So easy!"
- Pip hops along the bundle: "Can you snap the whole big bundle?" "Easy peasy!" says Tumble.
- He pulls it up and pushes it down until his face goes red. It only bends and springs back.
- He hops up and sits on the middle, as hard as he can. The bundle bows down... and springs back, BOING, and throws
  him up into the air. He lands on his bottom in the grass, dizzy: "It went BOING!"
- Pip pats the bundle: one stick snaps, but lots of sticks together stay strong. Tumble stands the bundle up on the
  bank and tips it over the stream. It lands on the far bank and makes a little bridge, and Tumble walks across with
  his arms out like a tightrope walker while Pip flies ahead.
- On the far bank Pip sings the moral, "Together we're strong!", from Tumble's paw. They do the series dance, then Pip
  hops onto the bridge, and it bounces him, boing, as they wave goodbye.

## Lyrics

| Section | Time (s) | Singer | Line |
|---|---|---|---|
| Hook | 0.0-3.6 | Tumble | One little twig? Snap! So easy! |
| Sting | 3.6-6.0 | duet (stored) | Tumble and Pip! |
| Setup A | 6.0-10.8 | Pip | Can you snap the whole big bundle? |
| Setup B | 10.8-15.6 | Tumble | Easy peasy! Watch me go! |
| Problem A | 15.6-20.4 | Tumble | Pull and push... it will not snap! |
| Problem B | 20.4-27.6 | Tumble | I'll sit on it, as hard as I can! (+ instrumental gag break: the boing) |
| Twist | 27.6-34.8 | Pip | One stick snaps, but lots stay strong! / Make a bridge and hop along! |
| Moral | 34.8-38.4 | Pip | Together we're strong! (moral card) |
| Chorus | 38.4-45.6 | duet (stored) | Big or small, short or tall, / friends help friends, that's best of all! |
| Button | 45.6-48.0 | instrumental | |

Syllables: every line is 5 to 9 syllables in its section, at most 3 per second.

Spoken gags (cast voices, `eleven_v3`, audio tags, stability 0.0):
- Tumble "Whoa-oa!" (launched into the air, about 24.8 s)
- Tumble "It went BOING!" (sitting dizzy in the grass, about 26.4 s)
- both "Bye-bye!" (about 46.5 s)

## Shot list

| # | Time (s) | Camera | What happens |
|---|---|---|---|
| 1 | 0.0-3.6 | medium front, slow push-in | Tumble holds one twig in both paws; on the sung "Snap!" it breaks in two with a puff of crumbs; he drops the halves. The bundle lies behind him across the stump and the rock, Pip on it. |
| 2 | 3.6-6.0 | wide establishing, from the far side of the stream | the bench of sticks, the stream, the far bank; title card |
| 3 | 6.0-10.8 | low macro along the bundle | Pip on the bundle, wing pointing along it, sings the question; Tumble listens behind |
| 4 | 10.8-15.6 | medium three-quarter | Tumble rubs his paws, struts up to the bundle and grips its middle |
| 5 | 15.6-20.4 | reverse angle from the stream side | pull (it bows up), push (it bows down), it springs back; his face goes red |
| 6 | 20.4-25.3 | side-on low angle, tilting up | he hops up and sits on the middle, bounces as he sings, sits down HARD: it bows... BOING, he flies up out of frame-top |
| 7 | 25.3-27.6 | medium, high | he drops into frame and lands on his bottom in the grass, dizzy; "It went BOING!" |
| 8 | 27.6-30.8 | two-shot | Pip on the bundle pats it and sings; Tumble nods and jumps up |
| 9 | 30.8-34.8 | high-angle wide, side-on to the stream | he tips the upright bundle over the stream (thump, puff on the far bank) and walks across, arms out; Pip flies ahead |
| 10 | 34.8-38.4 | push-in two-shot | far bank: Pip on Tumble's paw; the moral card |
| 11 | 38.4-45.6 | medium front | the series dance and high-five, the bridge behind |
| 12 | 45.6-48.0 | crane up | Pip hops onto the bridge, it boings him up; "Bye-bye!" |

Camera types: medium, wide, macro, three-quarter, reverse angle, low angle tilt, high two-shot, high-angle wide,
push-in, crane. 11 hard cuts. Shortest shot 2.3 s.

## How it differs from the other fables in the batch

- **Set corner:** the stream bank by a stump and a round rock. Fable 1 had the stump with the stream far behind;
  Fable 2 was under the apple tree. Here the stream is part of the story, and the camera crosses it.
- **Gag:** a springboard launch (he is thrown UP), against Fable 1's wrap-and-spin and Fable 2's dive into leaves.
- **Fix:** a thing they build together (a bridge), not a rescue (Fable 1) or a pull (Fable 2).
- **Cameras:** first reverse angle from the stream side and first high-angle side-on crossing shot. The wide
  establishing shot looks back from the far bank.
- **Button:** Pip on the bridge's springy middle, a callback to the gag.

## New assets (built from kit primitives, no `meshes.py` change)

- **Twig bundle:** 7 `stick` capsules in a hexagonal bundle (radius 0.15, length 2.6). Each stick is drawn as 8
  segments along a bent curve, so the bundle can bow under Tumble, bow up when he pulls, and spring back.
- **Grass ties:** two rings of small green `ball`s, with a two-`leaf` bow on top.
- **One twig:** a thin stick that snaps into two halves; the halves stay in the grass for the rest of the film.
- **Rock:** the `stone` mesh scaled up to stump height, the second support of the "bench".
