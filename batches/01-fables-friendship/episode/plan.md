# Episode 01: "Tumble & Pip: Fables About Friendship" (16:9 long-form)

- **status:** plan (2026-10-12). Episode worker builds the Story Stump material and `assemble.py`; the 10 fables come
  from the fable workers as `renders/fable-NN_wide.mp4`.
- **output:** `renders/episode-01_wide.mp4`, 1920x1080, 30 fps, about 9 min 20 s, -14 LUFS.
- **new material (this folder):** intro, 9 links, mid-point break, recap, outro (about 3 min of new scenes).
- **tone:** the bedtime end of the batch. Calm, warm, slow. Quiet voices, no shouting, no fast cuts, nothing scary.
  The light goes from sunset to starry night across the episode.

## The Story Stump framing

Sunset in Picnic Meadow. **Tumble stands on the big stump like a storyteller on a little stage**, holding a big clay
storybook open towards us, the way a teacher shows a picture book to a class. Pip sits on the stump beside his feet.
Pip asks "Tell me a story!" and Tumble opens the book. Every fable is "the story"; each link scene comes back to the
stump, where Tumble turns the page and the next fable's picture is on the spread.

- **The storybook (new prop, built from primitives):** two covers and two page blocks (scaled flat boxes from the
  blanket mesh), a spine (stick), one turning page. Teal-blue clay covers with a gold title, cream pages. Held in both
  paws at the outer cover edges; the front cover and the pages turn about the spine, always passing in front of the
  book (towards the camera), never through a paw.
- **Pictures on the pages:** each fable's archived 16:9 still (`fable-NN-*/stills/wide_*.jpg`, caption band cropped
  off) is drawn across the open spread with a perspective warp from the page corners. Links show the NEXT fable's
  hook still (the one nearest 2.6 s) with its title; the recap shows each fable's story still (nearest 29 s). A fable
  without stills yet gets a painted placeholder page (fable number and title), so everything renders today and picks
  up the real stills as they land.
- **Sky:** `HOOKS['sky']` plus a light grade that follow the scene's place in the episode: golden sunset at the intro,
  pink then violet twilight through the links (the sun sinks behind the far hills, fireflies appear from link 6),
  first stars in the recap, full night with moon and stars in the outro. Every change is far slower than 0.5 s.
- **Cast:** Tumble and Pip only. Voices: Tumble `Kx0fJ79cIgKz5YbJmR0t`, Pip `tGxaydQ2FS8MHwM6syrt` (eleven_v3 TTS,
  stability 0.0, 2 takes, widest pitch range wins, as `el_voice.py`). Tags keep them soft: `[warmly]`, `[softly]`,
  `[whispers]`, `[sleepy]`.

## Running order (episode cut)

Fable cuts follow the shared 100 BPM grid (bar 2.4 s): every fable drops the sting (3.6-6.0 s) and the button
(45.6-48.0 s). The full moral chorus stays on the first, middle and last fables (1, 5, 8); the others crossfade out
at 38.4 s, straight into the link. Joins between segments are 0.5 s video dissolves with matching audio crossfades;
the sting cut inside a fable is a hard cut on the bar line (the fable already cuts shots there) with a 0.1 s audio
crossfade, so the beat stays exact.

| # | Segment | Length | Content |
|---|---|---|---|
| 1 | Intro | 25.0 | the stored sting with the episode title card, sunset at the stump, "Tell me a story!", the book opens |
| 2 | Fable 1: Tiny Pip, Big Help | 43.2 | with the full moral chorus (teaches the song and the move) |
| 3 | Link 01 | 8.0 | tiny AND helpful, then the apple page |
| 4 | Fable 2: Sour Apples? | 36.0 | |
| 5 | Link 02 | 8.0 | sweet when you ask, then the jug page |
| 6 | Fable 3: Pebble, Pebble, Plop! | 36.0 | |
| 7 | Link 03 | 8.0 | count the pebbles again with Pip, then the race page |
| 8 | Fable 4: Slow and Steady Bo | 36.0 | |
| 9 | Link 04 | 8.0 | hooray for Bo, then the stream page |
| 10 | Fable 5: The Other Fox | 43.2 | with the full moral chorus |
| 11 | Mid-point break | 20.0 | stand-up stretch: the series dance with the chorus sung twice |
| 12 | Link 05 | 8.0 | back to the stump, then the ants page |
| 13 | Fable 6: Busy Little Ants | 36.0 | |
| 14 | Link 06 | 8.0 | the ants helped Tumble; now the ants need a friend |
| 15 | Fable 10: One Good Turn | 36.0 | follows the ants straight on from Fable 6 |
| 16 | Link 07 | 8.0 | friends help each other, then the sticks page |
| 17 | Fable 9: Stronger Together | 36.0 | |
| 18 | Link 08 | 8.0 | together we're strong; Pip yawns; the Wind and Sun page |
| 19 | Fable 7: Scarf Off! | 36.0 | |
| 20 | Link 09 | 8.0 | "One more, please?" The very last story |
| 21 | Fable 8: Pip Who Cried Help | 43.2 | with the full moral chorus |
| 22 | Recap | 53.4 | the chorus melody idea, one still and one moral line per fable |
| 23 | Outro | 15.0 | stars come out, the book closes, "Goodnight, friends!" |

Total before dissolves: 571 s; 22 dissolves of 0.5 s take off 11 s, so the episode runs about **9:20**.

**Two changes from the batch plan's table, on purpose:**
1. **9 links, not 8.** The batch table has no link between the break and Fable 6. Link 05 sits there: after the dance
   the children need a calm moment to sit back down before the next story.
2. **Recap 53.4 s, not 50.** Ten moral lines at 2 bars each (one line per 4.8 s, at most 2.1 sung syllables per
   second, easy to sing along) plus a 1-bar lead-in and a 3 s ring-out.

## Spoken lines and lyrics

Times are planned seconds inside each scene; the real TTS lengths replace them (each line starts at its planned time
or 0.3 s after the previous line ends, whichever is later). Page turns and other events are tied to the line times.
UK spellings.

### Intro (25 s)

| t | Who | Line | Picture |
|---|---|---|---|
| 0.0 | both (sung, stored sting) | Tumble and Pip! | wide sunset, the stump; title card "Tumble & Pip / Fables / Fables About Friendship" |
| 3.0 | Pip | Tumble? Tell me a story! | Pip flutters down onto the stump beside Tumble, who holds the closed book |
| 6.6 | Tumble | A story? I've got a whole book of them! | he lifts the book a little; the cover shows the gold title |
| 10.2 | Tumble | Fables About Friendship! | close on the cover |
| 13.0 | Pip | Ooh! Open it, open it! | Pip hops on the spot |
| 15.0 | | (the front cover swings open) | the first spread: Fable 1's hook picture, "1. Tiny Pip, Big Help!" |
| 17.2 | Tumble | Story number one... | |
| 19.6 | Tumble | a big kite, and a tiny helper! | close on the spread |
| 22.6 | Pip | That's me! | Pip points at himself; dissolve into Fable 1 |

### Links (8 s each)

Each link: line A at about 0.6 s bridges the moral that just ended; the page turns at about 3.9 s; line B at about
4.6 s names the next story while its picture is on the spread. Every link has its own camera and a small gag, and
the evening gets later each time.

| Link | A | B | Picture and gag |
|---|---|---|---|
| 01 (F1 to F2) | Pip: "I'm tiny AND helpful!" | Tumble: "You are! Now... a red apple, way up high." | Pip puffs up his chest; two-shot from the left |
| 02 (F2 to F3) | Tumble: "Asking a friend made it sweet." | Pip: "Next one! A thirsty bird, and a tall jug." | Tumble licks his lips; over Pip's shoulder |
| 03 (F3 to F4) | Pip: "Count with me! One, two, three, four, five!" | Tumble: "Next... a big race!" | Pip hops once per number; low front shot |
| 04 (F4 to F5) | Tumble: "Slow and steady Bo! Hooray!" | Pip: "Who's that, down in the water?" | Tumble claps softly; high three-quarter |
| 05 (break to F6) | Tumble: "Phew! Back to our story stump." | Pip: "Look! Little ants, marching along!" | they settle back on the stump; Pip marches on the spot |
| 06 (F6 to F10) | Pip: "The ants shared with Tumble!" | Tumble: "And now, the ants need a friend too." | first fireflies; side two-shot |
| 07 (F10 to F9) | Tumble: "Friends help each other." | Pip: "Next... a bundle of sticks. Snap!" | Pip claps his wings on "Snap!"; close two-shot |
| 08 (F9 to F7) | Pip: "Together, we're strong!" | Tumble: "Now... the Wind and the Sun." | Pip yawns after his line; the sun is gone, violet sky |
| 09 (F7 to F8) | Tumble: "Gentle and kind... like you, Pip." | Pip: "One more, please?" / Tumble: "The very last one." | sleepy eyes; slow push in |

### Mid-point break: stand-up stretch (20 s)

A new set-up after Fable 5's chorus (cut, not a continuous move): the book lies open on the stump, Tumble and Pip
stand on the grass in front of it, facing us, so children can mirror them.

| t | Who | Line |
|---|---|---|
| 0.3 | Tumble | Story break! Everybody, stand up! |
| 2.6-9.8 | both (stored chorus) | Big or small, short or tall, / friends help friends, that's best of all! |
| 9.8-17.0 | both (stored chorus, again) | Big or small, short or tall, / friends help friends, that's best of all! |
| 17.6 | Pip | Again tomorrow! |

The copyable move both times: Tumble's paw out, Pip riding it, the sway on every second beat, then the paw-to-wing
high-five with the star puff at the end of each chorus (the kit's series dance; the episode adds the first
high-five). Pip flies onto the paw during the opening call.

### Recap (53.4 s): one music_v2_5 take

Same fingerprint and singers as `el_batch.py` (100 BPM, 4/4 straight eighths, D major, gentle storybook folk,
acoustic guitar lead, glockenspiel, upright bass, soft hand drum; the tenor and soprano duet with bassoon and tin
whistle), on the chorus progression D-A-Bm-G-D-A-D, softer and slower in feel. Two lines per section, 2 bars each,
in episode order. Each line gets the yellow moral card and its fable's story still on the spread.

| Section | Length | Lyrics |
|---|---|---|
| Recap A | 12.0 s | {short instrumental intro} / Tiny friends can be big helpers! / Don't say sour, ask a friend! |
| Recap B | 9.6 s | Think it through, try something new! / Slow and steady gets there too! |
| Recap C | 9.6 s | Be happy with what you've got, and share! / Help a little every day! |
| Recap D | 9.6 s | Help a friend, and a friend helps you! / Together we are strong! |
| Recap E | 9.6 s | Gentle and kind works best! / Tell the truth, so friends know! |
| Ring-out | 3.0 s | {soft instrumental ending} |

(Fables 1, 2, 3, 4, 5, 6, 10, 9, 7, 8: the episode's order.)

### Outro (15 s): the lullaby

One music_v2_5 take on the same key and tempo as a lullaby: half-time feel, music-box glockenspiel, soft guitar, no
drums, both singers hushed.

| t | Who | Line | Picture |
|---|---|---|---|
| 0.4-7.2 | both (sung, lullaby) | Big or small, short or tall, / friends help friends, that's best of all. | stars come out one by one; Tumble slowly closes the book |
| 8.6 | both (spoken, whispered) | Goodnight, friends! | they wave, Pip leans on Tumble's foot |
| 10-15 | (instrumental ending) | | the camera tilts up to the moon and stars; slow fade to black |

## Shots (16:9 only)

Every scene is rendered with the shared kit from one parametrised folder (`episode/code`, `--scene <name>`): one
`timeline.py` and one `render.py` hold all 13 scenes, so the stump, the book, the light ramp and the cameras stay
identical, and each scene renders, checks and mixes on its own. Camera types used across the scenes: establishing
wide, two-shot, over-the-shoulder, low front, high three-quarter, side two-shot, cover and spread close-ups,
frontal dance wide, crane up to the sky. Every shot is 1.3 s or longer, hard cuts inside a scene.

## Audio

- **Lines:** eleven_v3 TTS in the cast voices (as `el_voice.py`), placed at the line times.
- **Intro and link bed:** one instrumental music_v2_5 take on the batch fingerprint (28.8 s, calm, no vocals). The
  intro plays the stored sting, then the bed; each link takes a different 8 s window of it on a bar line, faded at
  both ends and kept under the voices.
- **Break:** the stored chorus (`audio/series/chorus.mp3`) twice, 7.2 s apart (3 bars, so the beat carries on).
- **Recap and outro:** one music_v2_5 take each (above), checked with speech-to-text recall and forced alignment
  (word times drive captions and mouths).
- **Mix:** every scene at -14 LUFS (peak under -0.2 dBFS), full-mix recall checked; the assembled episode is
  normalised to -14 LUFS again.

## Checks

As `FABLE_WORKER.md`: geometry QA 0 issues per scene, contact sheets (one frame per 0.5 s) for every scene, an
independent reviewer subagent until PASS (log in `review.md`).
