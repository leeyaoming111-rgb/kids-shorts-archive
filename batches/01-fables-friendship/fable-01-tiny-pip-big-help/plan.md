# Tumble & Pip Fables 1: Tiny Pip, Big Help!

- **job:** batch 01, fable 01 (`fable-01-tiny-pip-big-help`)
- **status:** animatic done. Visuals built in both aspects on the planned grid; geometry QA 0; reviewer PASS (round 6).
  Waiting for the ElevenLabs song (the build session had no key and no network access to ElevenLabs), then the final
  render on the Mac.
- **series:** Tumble & Pip (Fables About Friendship). Batch plan: [../plan.md](../plan.md)
- **source:** Aesop's fable *The Lion and the Mouse* (public domain), retold with our cast, gags and song
- **lesson (SEL):** small friends can be big helpers; don't judge help by size
- **length:** 48.0 s (20 bars at 100 BPM). Episode cut: 41.2 s (drops the sting and the button)
- **aspects:** 9:16 Short (`render.py`) and 16:9 episode framing (`render.py --wide`), same scene and timing

## Prompt

A 48-second claymation fable for children aged 3 to 5. Tumble the clay fox cub flies a big pink-and-teal kite in the
Picnic Meadow, and the wind tugs him off his feet. His tiny bird friend Pip, perched on the old tree stump, asks to help,
and Tumble kindly says the kite is too big for tiny wings. A gust swings the kite round and round him until he is wrapped
up like a parcel and topples over in the grass. Pip flies down and pecks the knot, peck, peck, peck, and Tumble spins
free like a top, dizzy and laughing. With Pip sitting on his paw, Tumble sings the moral: tiny friends can be big
helpers. They do the series dance (Pip rides Tumble's paw, they sway, then a paw-to-wing high-five), and Pip flies the kite back up into the sky.
Gentle storybook folk at 100 BPM in D major with acoustic guitar, glockenspiel, bassoon for Tumble and tin whistle for Pip.

## Change from the batch plan

The batch plan opened on the tangled image as a teaser. Preschoolers follow straight-through stories better than
flash-forwards, so the hook is now the kite tugging Tumble off his feet in the first 3 seconds (action in the first
second, the problem set up by the end of the hook).

## Lyrics (sung by the ElevenLabs Music model's own singers)

| Section | Time (s) | Singer | Line |
|---|---|---|---|
| Hook | 0.0-3.6 | Tumble | Up, up, up goes my big kite! |
| Sting | 3.6-6.0 | duet (stored) | Tumble and Pip! |
| Setup A | 6.0-10.8 | Pip | Can I help? I'm good at things! |
| Setup B | 10.8-15.6 | Tumble | This kite's too big for tiny wings! |
| Problem A | 15.6-20.4 | Tumble | Whoosh! The wind goes round and round, |
| Problem B | 20.4-27.6 | Tumble | now Tumble's tangled on the ground! (+ instrumental gag break) |
| Twist | 27.6-34.8 | Pip | I can help! Peck, peck, peck! (+ instrumental spin-out break) |
| Moral | 34.8-38.4 | Tumble | Tiny friends can be BIG helpers! (moral card) |
| Chorus | 38.4-45.6 | duet (stored) | Big or small, short or tall, / friends help friends, that's best of all! |
| Button | 45.6-48.0 | instrumental | happy ending |

Spoken gags in the fixed cast voices (`eleven_v3`, audio tags, stability 0.0): Tumble "Uh-oh! Help!" (about 24.1 s,
lying tangled), Tumble "Wheee!" (about 31.9 s, the spin-out), both "Bye-bye!" (about 46.3 s).
Syllable budget: every line at or under 3 syllables per second.

## Shot list

| # | Time (s) | Camera | What happens |
|---|---|---|---|
| 1 | 0.0-3.6 | low tracking, front three-quarter | Tumble runs in with the kite rising behind; Pip flies beside; on "kite!" the kite tugs him into the air |
| 2 | 3.6-6.0 | wide establishing | meadow, stump and stream; Tumble waves, Pip lands on the stump; title card "Tumble & Pip / Fables / Tiny Pip, BIG Help!" |
| 3 | 6.0-10.8 | macro close-up | Pip on the stump hops on "help", "good", "things", wing up |
| 4 | 10.8-15.6 | over Pip's shoulder | Tumble turns to Pip, chuckles and shakes his head; Pip droops |
| 5 | 15.6-20.4 | wide low angle, push-in | leaves blow, the kite swoops and circles him 2.3 times, the string coils round him, arms pinned |
| 6 | 20.4-24.0 | medium side | wrapped hops, wobble, tips over on "tangled", bump, rocks like a log, feet kicking |
| 7 | 24.0-27.6 | overhead | wrapped like a parcel in the grass, kite beside him; "Uh-oh! Help!"; Pip flies down to his chest |
| 8 | 27.6-31.2 | macro, side-on | Pip pecks the knot on each sung "peck"; the knot pops open with a puff |
| 9 | 31.2-34.8 | wide | Tumble rises and spins three times as the string unwinds onto the grass ("Wheee!"), dizzy, laughs; Pip cheers |
| 10 | 34.8-38.4 | push-in two-shot | Pip hops onto Tumble's raised paw; the moral card |
| 11 | 38.4-45.6 | medium front | the series dance: Pip rides Tumble's outstretched paw, they sway on every second beat, then a paw-to-wing high-five with a star puff |
| 12 | 45.6-48.0 | crane up | Pip takes off from the paw with the string in his beak and flies the kite back up; Tumble cheers |

Camera types: tracking, wide, macro, over-the-shoulder, low angle push-in, medium, overhead, crane. 11 hard cuts.
Shortest shot 2.4 s.

## How it differs from the rest of the batch and the archive

- First fable and first kite-wrap gag in the archive; the kite from Episode 1 returns as a story prop.
- First moral card, first series dance, first 16:9 framing.
- Set: a new corner of the Picnic Meadow (stump, stream, apple tree) with no picnic blanket or basket.
- Music: the batch fingerprint (100 BPM, 4/4, D major, guitar and glockenspiel, storybook folk) differs from every
  archive song on tempo (vs 120, 132, 104, 88), key (vs C, C/B, F/Ab, G), lead instrument and form.

## Checks so far (animatic, planned grid)

- Stills and contact sheets in both aspects looked at; fixes made: a camera below the ground in the gust shot, Tumble
  falling into the stump, Pip seen from behind in two shots, the string crossing Pip, overhead framing, coil readability.
- Geometry QA: 0 issues at 15 fps (started at 45).
- Reviewer agent: PASS in round 6, after 5 FAIL rounds (see `review.md`).
- Stills: 8 per aspect in `stills/`, plus contact sheets.
- Still to do once the song exists: take recall 95%+ with lines inside sections, diarization (Tumble, Pip, duet),
  tempo within 2 BPM of 100, bar-line joins at chroma 0.9+, full-mix recall 90%+, -14 LUFS, final Mac render, 2 frames
  from the MP4.
