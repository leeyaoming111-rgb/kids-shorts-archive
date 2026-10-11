# Tumble & Pip, Episode 1: What's the Weather?

- **job_id:** 2026-10-10-pm-tumble-pip-weather
- **status:** done. r1 rendered in 86 s; r2 = glitch-fix revision (see Revisions)
- **format:** series episode 1 (starts the series "Tumble & Pip")
- **series:** Tumble & Pip. Recurring cast, same cottage and garden, theme hook "Peek out, what do you see? Sun or rain, come sing with me!"
- **lesson:** weather: sunny, cloudy, windy, rainy, rainbow
- **characters:** Tumble, a cheerful pastel-orange clay fox cub with big ears and a fluffy cream-tipped tail who loves playing outside. Pip, a tiny sky-blue clay bird, his best friend, who perches wherever Tumble goes.
- **setting:** Tumble's round clay cottage (lavender roof, green round door, window box) and front garden: stepping-stone path, a leafy tree, flowers, a spot where a puddle forms.
- **voice:** am_eric (previous video used af_heart)

## Prompt

A 45-second vertical (9:16) cartoon episode for children aged 3 to 5. Tumble, a little clay fox cub, slides into his front garden to play with his tiny bird friend Pip. Every time he looks up at the sky, the weather changes, and he picks the right thing: a sunhat for sunshine, cloud-watching for clouds, a kite for wind, an umbrella and yellow boots for rain, and a happy dance when a rainbow appears. Gentle waltz song with marimba and music box, clear male voice. Each verse asks "What's the weather?", pauses so children can answer, then names it. Claymation style, soft lighting that changes with the weather, thumbprint textures, real camera shots: crane, close-up tilting to the sky, over-the-shoulder, low-angle wide, push-in.

## Shot list

| # | Time (s) | Camera | What happens |
|---|---|---|---|
| 1 | 0.0-5.5 | crane down from the sky | Cottage and garden come into view; Tumble slides in from the right on his tummy-skid, stops and waves. Title card. |
| 2 | 5.5-10.9 | medium tracking arc | Chorus. Tumble sways to the waltz on the path; Pip flies in and circles his head. |
| 3 | 10.9-13.2 | low close-up, tilts up to the sky | "What's the weather?" Tumble looks up; camera tilts; the sun slides out from behind a cloud (guessing pause). |
| 4 | 13.2-16.4 | medium front | "It's sunny! Hat on, let's play!" A small straw sunhat drops onto his head between his ears, he spins, Pip lands on the hat. |
| 5 | 16.4-18.6 | low close-up, tilts up to the sky | Big fluffy clouds slide across the sun. |
| 6 | 18.6-21.8 | over-the-shoulder | "It's cloudy! Clouds float away!" Tumble (hat on, Pip on the hat) turns and points at the drifting clouds. |
| 7 | 21.8-24.1 | low close-up, tilts up to the sky | Gag: the wind blows Tumble's hat off and it spins away into the sky; Pip flies off; clouds race, leaves blow. |
| 8 | 24.1-27.3 | wide low angle | "It's windy! Whoosh, fly my kite!" Kite dances on its string, ears and tail blow. |
| 9 | 27.3-29.5 | low close-up, tilts up to the sky | Grey clouds, first raindrops. |
| 10 | 29.5-32.7 | push-in | "It's rainy! Boots on, splash, splash!" Umbrella pops open, boots turn yellow, he hops in a puddle; Pip sits on the umbrella. |
| 11 | 32.7-35.0 | low close-up, tilts up to the sky | Rain stops, the umbrella folds shut, Pip flies to the tree top, a rainbow grows across the sky. |
| 12 | 35.0-38.2 | wide | "A rainbow! Colours so bright!" Tumble and Pip jump and cheer under the rainbow. |
| 13 | 38.2-44.9 | pull-back crane up | "Every weather, we can play! Bye-bye, friends!" Tumble waves goodbye, Pip on his head. |

## Music fingerprint (see music.json)

132 BPM waltz in 3/4, written in C and sung in B, I-vi-IV-V chorus. Marimba oom-pah-pah, plucked bass, music box doubling the melody, warm pad in the guessing pauses, shaker and triangle, no drum kit. Form: spoken intro, chorus, 5 x (question, guessing pause, answer, action line), outro.

## Different from the archive

- Format: story episode with a named cast. Dino Count and Penguin Shapes were song-and-reveal.
- Camera: 13 shots, 7 camera types, 12 hard cuts. The archive videos used one locked wide shot.
- Set: a cottage garden at eye level. The archive videos used a big round hill with five fixed spots.
- Music: 3/4 waltz at 132 BPM, marimba lead, I-vi-IV-V. The archive videos used 4/4 at 120 BPM, ukulele, C-C-F-G.
- Lyrics: question, pause, answer. The archive videos used the "X, X, here comes Y" chant.

## Lyrics

- Spoken: "Hi! I'm Tumble, and this is Pip!"
- Chorus: "Peek out, what do you see? Sun or rain, come sing with me!"
- Each verse: "What's the weather?" (guessing pause) then the answer and action:
  - "It's sunny! Hat on, let's play!"
  - "It's cloudy! Clouds float away!"
  - "It's windy! Whoosh, fly my kite!"
  - "It's rainy! Boots on, splash, splash!"
  - "A rainbow! Colours so bright!"
- Outro: "Every weather, we can play! Bye-bye, friends!"

## Checks

- Tuning: median 3.0 cents, 94% of frames within 30 cents
- HNR: 15.9 dB tuned vs 13.7 dB raw TTS
- Energy above 12 kHz: 0.00%
- Loudness: -14.5 LUFS (final MP4)
- Trim: 0 of 19 phrases trimmed (max cut 0.000 s); syllable rate 2.6 to 3.5 per second
- Contact sheet: 3 passes (fixed over-the-shoulder framing, umbrella size, rain streaks, Pip flying into the lens, caption weight)

## Series notes for Episode 2

Keep: Tumble (pastel-orange fox cub, cream muzzle and tail tip), Pip (sky-blue bird, perches on Tumble), the round cottage with lavender roof and green door, the garden, the hook "Peek out, what do you see?", the "Episode N" title pill. Change: the lesson, the adventure, the shots and the music fingerprint.

## Revisions

- **r2 (glitch fixes).** Owner feedback: Pip glitched through Tumble, the hat clipped through his ears. Geometry QA (tools/qa_geom.py) measured Pip 0.36 deep in Tumble's head, perches floating 0.2 high, the brim through the ears, feet 0.07 below ground. Reviewer agent round 1: FAIL (2 HIGH, 7 MED: hat and umbrella vanishing mid-shot, captions on the face, Pip overlapping the kite, framing). Fixes: SDF-measured perches; a small hat between the ears that the wind blows away (new gag); umbrella folds shut and leaves at a cut; answer cut half a beat before the answer; reframed cloudy and rainy shots; leaves kept off the lens; answer words moved off faces. Reviewer round 2: PASS (2 MED fixed after). Geometry QA: 0 issues incl. pop check.
- Story change in r2: the hat now stays on through the cloudy shot and blows away in the windy tilt shot; Pip sits on the hat, not the shoulder.
