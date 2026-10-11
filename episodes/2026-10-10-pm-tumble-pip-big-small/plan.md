# Tumble & Pip, Episode 2: Big and Small!

- **job_id:** 2026-10-10-pm-tumble-pip-big-small
- **status:** done (rendered on the Mac in 83 s, 2026-10-10 23:41 local)
- **format:** series episode 2 (series: Tumble & Pip). Previous video was a one-off story (Lulu & Bo).
- **lesson:** big and small (not in the last 4: counting, shapes, weather, taking turns)
- **characters:** Tumble (pastel-orange clay fox cub) and Pip (tiny sky-blue clay bird), who speaks and sings for the first time.
- **setting:** a new place in the series world: Picnic Meadow by the stream (checked picnic blanket, wicker basket, apple tree, big tree stump, mushroom ring, stream, Tumble's cottage tiny in the distance). Archive settings: mossy hill, snowy hill, cottage garden, lily pond.
- **voice:** song by the ElevenLabs Music API (music_v2_5, take 33 of 3): a friendly male lead, a deep booming male BIG voice and a high tiny female voice for Pip. Spoken lines by ElevenLabs TTS: Liam (Tumble), Jessica (Pip).

## Prompt

A 45-second vertical (9:16) cartoon episode for children aged 3 to 5. Tumble the clay fox cub and his tiny bird friend Pip go on a picnic in a sunny meadow and play "big and small". Tumble sings every BIG thing in a deep, slow voice; Pip sings every tiny thing in a high, quick voice. Four rounds, each with a slapstick gag: a big apple rolls away with Pip running on top; Tumble's big leaf fan blows Pip head over tail into the picnic basket; Tumble sits on a tiny mushroom and it squashes and boings him into the air; Pip's tiny stomp goes "tap" while Tumble's big hop shakes the whole meadow. Bouncy 6/8 jig with tuba and tin whistle. The word BIG appears huge on screen and the word "tiny" appears tiny. Finale in split screen, BIG on top and small below, then a crane up over the meadow as they wave goodbye.

## Shot list

| # | Time (s) | Shot | What happens |
|---|---|---|---|
| 1 | 0.0-4.1 | flyover | drone flyover descending: meadow, stream, far cottage; Tumble walks in carrying the basket in his arms, Pip flies beside. Title card. Spoken: 'Picnic time, Pip!' / 'Let's find BIG and small!' |
| 2 | 4.1-9.5 | overhead | overhead top-down: Tumble sets the basket on the checked blanket, sways; Pip hops around the blanket. |
| 3 | 9.5-12.9 | big0 | low-angle push-in: Tumble hugs a huge red apple in front of his belly. 'A BIG red apple!' |
| 4 | 12.9-14.4 | small0 | macro: Pip points his raised wing at a tiny berry on the blanket. 'Tiny berry!' |
| 5 | 14.4-16.4 | gag0 | wide tracking: the apple rolls away on its side with Pip running on top ('Wheee!'), Tumble chases right behind. |
| 6 | 16.4-19.8 | big1 | medium: Tumble swings a giant leaf. 'A BIG leaf fan, whoosh!' |
| 7 | 19.8-21.0 | gag1 | wide side: the gust tumbles Pip head over tail into the picnic basket ('Whoa!'). |
| 8 | 21.0-23.2 | small1 | macro: Pip pops up in the basket fanning himself with a tiny leaf (same leaf model as Tumble's, 1/9 the size). 'Tiny leaf fan!' |
| 9 | 23.2-26.6 | big2 | low angle: Tumble walks round and hops up to sit on the big stump. 'A BIG tree stump seat!' |
| 10 | 26.6-28.1 | small2 | macro: Pip flutters onto a tiny red mushroom. 'Tiny mushroom!' |
| 11 | 28.1-30.0 | gag2 | side two-shot: Pip hops off, Tumble hops onto the mushroom, it squashes flat and boings him into the air; he lands on his bottom ('Oops!'). |
| 12 | 30.0-33.4 | big3 | ground-level wide, small camera shake: Tumble stomps twice, puffs, Pip bounces. 'BIG feet go stomp, stomp!' |
| 13 | 33.4-34.7 | small3 | macro: Pip hops. 'Small feet go hop!' |
| 14 | 34.7-36.8 | gag3 | wide: Pip's tiny stomp (tap, nothing happens); Tumble's giant hop ('Boing!'), the landing shakes the meadow and flips Pip. |
| 15 | 36.8-40.2 | split | split screen: top BIG (Tumble close-up), bottom small (Pip close-up). 'BIG and small, BIG and small!' |
| 16 | 40.2-42.2 | together | medium two-shot: Pip flies up onto Tumble's forehead. 'Best friends, BIG and small!' |
| 17 | 42.2-44.9 | crane_out | crane up and away over the meadow, Tumble waves. 'Bye-bye, friends!' |

## Music fingerprint (music.json)

6/8 jig, dotted-quarter 88 BPM, G major, I-V-vi-IV style (G-Em-C-D chorus, G-C-D-Em-D rounds). Tuba oom-pah bass, toy-piano and pizzicato chords, tin whistle doubling Pip, bassoon-like low reed doubling Tumble, woodblock, triangle, slide whistle and boing gag SFX. Form: spoken intro, chorus, 4 x (BIG line, tiny line, gag), finale duet, bye.

## Different from the archive

- Format: series episode 2 after a one-off story; first episode with spoken lines from Pip and a two-voice duet.
- Music vs each archive entry: 6/8 (vs 4/4, 3/4, 4/4 swing); 88 BPM (vs 120, 132, 104: 16+ apart); key G (vs C, C, F); G-Em-C-D progression (vs C-C-F-G, I-vi-IV-V, I-IV-ii-V); tuba + tin whistle lead (vs ukulele, marimba, kalimba); BIG/tiny contrast form (vs reveal chant, weather question loop, story with questions). Differs on all 6 attributes.
- Visual: new meadow picnic set; first overhead shot, first macro shots, first split screen; captions size-coded (BIG huge, tiny tiny).
- Gags as setup, anticipation, payoff in each round (inspiration principles from Oddbods and Monica Toy).

## Checks

- Song: ElevenLabs Music v2.5, best of 3 seeded takes. Speech-to-text lyric recall 100%, every line inside its section, forced-alignment loss 1.17. Diarization: 3 voices (lead, deep BIG, high tiny).
- Final mix: -14.6 LUFS, minimum gap between voice lines 0.36 s, full-mix lyric recall 97% (65/67; only "Wheee" and "Boing" misheard).
- Geometry QA: 0 issues (penetration, floating, below-ground, pops) at 15 fps.
- Reviewer agent: FAIL, FAIL, PASS (3 rounds). See review.md.
