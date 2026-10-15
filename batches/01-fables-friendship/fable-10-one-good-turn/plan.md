# Tumble & Pip Fables 10: One Good Turn

- **job:** batch 01, fable 10 (`fable-10-one-good-turn`), built on the shared kit (`common/fablekit.py`)
- **status:** animatic done, geometry QA 0, reviewer PASS (round 2). Audio and final renders still to do (no ElevenLabs key in the session).
- **source:** Aesop's fable *The Dove and the Ant* (public domain), retold with our cast
- **lesson (SEL, social-emotional learning):** kindness comes back; help a friend and a friend helps you
- **length:** 48.0 s (20 bars at 100 BPM). Episode cut: 41.2 s (drops the sting and the button)
- **aspects:** 9:16 Short (`render.py`) and 16:9 episode framing (`render.py --wide`), same scene and timing

## Prompt

A 48-second claymation fable for children aged 3 to 5:
- On the bank of the Picnic Meadow stream, a tiny cherry-red clay ant is spinning round and round on a twig in the
  water and can't steer to the bank. Pip flutters over: "Oh no, little ant!"
- Pip picks up a big green leaf from the bank in his beak and drops it on the water right beside the twig: "Here's a
  leaf! Hop on, hop on!" The ant hops onto the leaf, which drifts gently to the bank.
- The ant hops ashore and waves its feelers at Pip: "Thank you, Pip! I won't forget!"
- Later, along the bank, a huge golden flower drips honey into a shiny puddle. Pip flies over for a sniff. Tumble
  calls "Careful, Pip! The honey's sticky!", too late: splat, Pip lands right in it.
- "Oh no! My feet are stuck!" Pip flaps, and his clay body stretches up like toffee, but his feet stay put.
  Tumble: "Uh-oh!" The little ant sees, whistles, and a whole line of ants marches up.
- The ants hold on to each other, the first one holds Pip's tail, and they pull: "Heave-ho! Heave-ho! One more...
  POP!" Each tug stretches Pip longer like clay toffee before he springs back. On "POP" his feet come loose, the ants
  sit down in a heap, and Pip somersaults backwards over them and lands on Tumble's nose ("Wheee!").
- The ant, riding Tumble's other paw, sings the moral: "Help a friend, and a friend helps you!" They do the series
  dance, and the ants dance along at Tumble's feet.
- Button: the ants march home carrying a drop of honey like a golden ball; everyone waves "Bye-bye!"

## Lyrics (sung by the ElevenLabs Music model's own singers)

| Section | Time (s) | Singer | Line |
|---|---|---|---|
| Hook | 0.0-3.6 | Pip | Oh no, little ant! |
| Sting | 3.6-6.0 | duet (stored) | Tumble and Pip! |
| Setup A | 6.0-10.8 | Pip | Here's a leaf! Hop on, hop on! |
| Setup B | 10.8-15.6 | the ant | Thank you, Pip! I won't forget! |
| Problem A | 15.6-20.4 | Tumble | Careful, Pip! The honey's sticky! |
| Problem B | 20.4-27.6 | Pip | Oh no! My feet are stuck! (+ instrumental break: the ants march in) |
| Twist | 27.6-34.8 | the ant | Heave-ho! Heave-ho! One more... POP! (+ instrumental break: the somersault) |
| Moral | 34.8-38.4 | the ant | Help a friend, and a friend helps you! (moral card) |
| Chorus | 38.4-45.6 | duet (stored) | Big or small, short or tall, / friends help friends, that's best of all! |
| Button | 45.6-48.0 | instrumental | happy ending |

- The ant's lines are sung by the music model with its own voice description ("small, bright, cheerful voice";
  `code/el_verse.py` adds it to `el_batch.py`'s voice table without editing the shared file).
- Syllables: every line is at or under 3 sung syllables per second (the densest is the moral, 9 syllables in 3.6 s).

Spoken gags in the fixed cast voices (`eleven_v3`, audio tags, stability 0.0):
- Tumble "Uh-oh!" (Problem B break, Pip stuck)
- Pip "Wheee!" (the backwards somersault)
- both "Bye-bye!" (button)

## Shot list

| # | Time (s) | Camera | What happens |
|---|---|---|---|
| 1 | 0.0-3.6 | low, at water level | the ant on a twig, spinning slowly in the stream, wobbling with its feelers up; Pip flutters in beside it: "Oh no, little ant!" |
| 2 | 3.6-6.0 | high wide establishing | the stream, the bank, the big golden flower with its honey puddle; Tumble waves from the bank; title card |
| 3 | 6.0-8.4 | medium, tracking | Pip flies down to a big leaf on the bank, takes its stem in his beak and lifts it |
| 4 | 8.4-10.8 | overhead | Pip flies over the water and drops the leaf beside the twig; the ant hops onto it on "hop" |
| 5 | 10.8-15.6 | macro, low, side-on | the leaf drifts to the bank; the ant hops ashore and waves its feelers to Pip on the grass: "Thank you, Pip!" |
| 6 | 15.6-18.0 | medium, following | Pip takes off towards the flower; Tumble points and calls after him, walking along the bank |
| 7 | 18.0-20.4 | low close | Pip lands in the honey puddle: splat, gold drops |
| 8 | 20.4-23.4 | close, side-on | Pip flaps and stretches up like toffee twice; his feet stay stuck; honey strings |
| 9 | 23.4-27.6 | wide | Tumble "Uh-oh!"; the ant whistles (little music-note puffs), and the ant line marches in and lines up, the ant holding Pip's tail |
| 10 | 27.6-~30.5 | side-on medium | heave, heave, one more: each tug stretches Pip longer; the ants lean back together |
| 11 | ~30.5-34.8 | wide, side | POP: his feet come loose, the ants sit down in a heap, Pip somersaults backwards over them and lands on Tumble's nose; Tumble goes cross-eyed and laughs |
| 12 | 34.8-38.4 | push-in two-shot | Pip hops onto Tumble's paw; the ant rides his other paw and sings the moral (moral card) |
| 13 | 38.4-45.6 | medium front | the series dance and high-five; the ant sways on Tumble's paw and the ant line sways at his feet |
| 14 | 45.6-48.0 | crane up | the ants march home carrying a honey drop like a golden ball; "Bye-bye!" |

Camera types: low water-level, high wide, tracking, overhead, macro, following, low close, side-on, wide, push-in,
medium front, crane. 13 hard cuts. Every shot is 1.3 s or longer.

## How it differs from the other fables in the batch

- **Set corner:** the stream bank with a huge golden flower and a honey puddle. The stream is a rescue place, not a
  bridge (Fable 5 has a log bridge, Fable 9 a bundle bridge).
- **Gag shape:** a stretch-and-pop. Pip is the one in trouble and the helpers are many tiny friends pulling together
  (Fable 1 is a wrap and spin, Fable 2 a dive, Fable 8 a pratfall in a puddle).
- **Story turn:** the helper and the helped swap places (one good turn comes back), and a guest sings the moral.
- **Cameras:** the overhead leaf drop and the side-on tug line are new to the batch.
- **Colour:** gold honey and cherry-red ants; Fable 8's flower is pink, this one is a golden yellow.

## New assets (all built from kit primitives in `code/render.py`, no mesh changes)

- **Ant** (clearly marked block in `render.py`): three clay balls (head, middle, bottom) on six stick legs, two
  feelers with ball tips, big eyes from the kit, a tiny mouth when it sings. The hero ant wears a leaf hat. The
  coordinator will unify it with Fable 6's ant later.
- **Twig raft:** the kit stick, lying in the water.
- **Leaf boat:** Episode 2's `bigleaf`, scaled down.
- **Big golden flower:** the kit flower, scaled 4.5 and tinted gold.
- **Honey:** glossy gold blobs (`mat=2` with a gold tint): the hanging drip, the falling drop, the puddle, strings.

## Checks

To fill in as the work goes: geometry QA, reviewer rounds, song recall, mix loudness, renders.
