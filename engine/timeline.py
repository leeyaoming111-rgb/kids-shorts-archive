"""Single source of truth for 'Stomp, Stomp, Dino Count!'. Audio and video both import this."""
BPM = 120.0
BEAT = 60.0 / BPM          # 0.5 s
TOTAL_BEATS = 88
TAIL = 0.9
DURATION = TOTAL_BEATS * BEAT + TAIL   # 44.9 s
FPS = 30
W, H = 1080, 1920
TRANSPOSE = -9             # melody written around C4..G4, sung in Eb (centre ~G3 for am_eric @ 158 Hz)
VOICE = "am_eric"

def t(beat):
    return beat * BEAT

# ---- sections (beats) ----
INTRO = (0, 8)
CHORUS1 = (8, 16)
ARRIVE0 = 16               # arrival k (1..5) occupies [16+8(k-1), 24+8(k-1))
def arrival_start(k):
    return ARRIVE0 + 8 * (k - 1)
CHORUS2 = (56, 64)
BACKDOWN = (64, 68)
COUNTDOWN = (68, 74)
HOORAY = 74
ENDING = (76, 88)

NUMWORDS = ["One", "two", "three", "four", "five"]

# ---- sung phrases: (tts text, caption with hyphenated syllables, [(beat, dur, midi)]) ----
PHRASES = []
def sung(text, caption, notes, tag=None):
    words = caption.split()
    nsyl = sum(len(w.split("-")) for w in words)
    assert nsyl == len(notes), (caption, nsyl, len(notes))
    PHRASES.append(dict(text=text, caption=caption, notes=notes, tag=tag))

def chorus(b0, tag):
    sung("Stomp, stomp, one more friend!", "Stomp, stomp, one more friend!",
         [(b0, .75, 67), (b0 + 1, .75, 67), (b0 + 2, .5, 69), (b0 + 2.5, .5, 67), (b0 + 3, .85, 64)], tag)
    sung("Count with me from start to end!", "Count with me from start to end!",
         [(b0 + 4, .5, 65), (b0 + 4.5, .5, 65), (b0 + 5, .5, 64), (b0 + 5.5, .5, 62),
          (b0 + 6, .5, 64), (b0 + 6.5, .5, 62), (b0 + 7, .85, 60)], tag)

chorus(8, "chorus1")
NUM_NOTE = [67, 67, 69, 69, 72]
SCALE = [60, 62, 64, 65, 67]
for k in range(1, 6):
    b0 = arrival_start(k)
    word = NUMWORDS[k - 1].lower()
    sung(f"Stomp, stomp, here comes {word}!", f"Stomp, stomp, here comes {word.upper()}!",
         [(b0, .75, 64), (b0 + 1, .75, 64), (b0 + 2, .5, 65), (b0 + 2.5, .5, 65), (b0 + 3, .85, NUM_NOTE[k - 1])],
         f"arrive{k}")
    c = b0 + 4
    if k == 1:
        sung("One dino!", "One di-no!", [(c, 1, 60), (c + 1, .5, 62), (c + 1.5, 1.6, 64)], "count1")
    elif k == 2:
        sung("One, two dinos!", "One, two di-nos!", [(c, 1, 60), (c + 1, 1, 62), (c + 2, .5, 64), (c + 2.5, 1.1, 64)], "count2")
    elif k == 3:
        sung("One, two, three!", "One, two, three!", [(c, 1, 60), (c + 1, 1, 62), (c + 2, 1.6, 64)], "count3")
    elif k == 4:
        sung("One, two, three, four!", "One, two, three, four!", [(c, 1, 60), (c + 1, 1, 62), (c + 2, 1, 64), (c + 3, .7, 65)], "count4")
    else:
        sung("One, two, three, four, five!", "One, two, three, four, five!",
             [(c, .7, 60), (c + .75, .7, 62), (c + 1.5, .7, 64), (c + 2.25, .7, 65), (c + 3, .7, 67)], "count5")
chorus(56, "chorus2")
sung("Now let's count back down!", "Now let's count back down!",
     [(64, .5, 67), (64.5, .5, 67), (65, .9, 69), (66, .9, 67), (67, .7, 62)], "backdown")
sung("Five, four, three, two, one!", "Five, four, three, two, ONE!",
     [(68, .85, 67), (69, .85, 65), (70, .85, 64), (71, .85, 62), (72, 1.5, 60)], "countdown")
sung("Hooray!", "Hoo-ray!", [(74, .5, 64), (74.5, 1.2, 67)], "hooray")
sung("Stomp, stomp, bye bye!", "Stomp, stomp, bye-bye!",
     [(76, .75, 67), (77, .75, 67), (78, .75, 64), (79, 2.4, 60)], "bye")

# ---- spoken lines: (text, start seconds, speed) ----
SPOKEN = [dict(text="Hi friends! Let's count dinosaurs!", t0=0.45, speed=0.95, caption="Hi friends! Let's count dinosaurs!")]

# ---- chords at 2-beat resolution: beat -> (root midi, quality) ----
_C, _F, _G = (48, "M"), (53, "M"), (55, "M")
CHORDS = {}
def _set(b0, seq):
    for i, c in enumerate(seq):
        CHORDS[b0 + 2 * i] = c
_set(0, [_C, _C, _F, _G])
_set(8, [_C, _C, _F, _G])
for _k in range(1, 6):
    _set(arrival_start(_k), [_C, _F, _C, _G])
_set(56, [_C, _C, _F, _G])
_set(64, [_F, _G])
_set(68, [_C, _G, _C, _C, _C, _C])
_set(80, [_C, _C, _C, _C])
def chord_at(beat):
    b = int(beat // 2) * 2
    while b not in CHORDS and b > 0:
        b -= 2
    return CHORDS.get(b, _C)

# ---- shared visual/audio events ----
STOMPS = []      # (beat, strength, who) who: dino index 0..4, -1 = offscreen, 'all' = 99
for _k in range(1, 6):
    _b = arrival_start(_k)
    STOMPS += [(_b, 1.0, _k - 1), (_b + 1, 1.0, _k - 1), (_b + 2, .45, _k - 1), (_b + 2.5, .45, _k - 1), (_b + 3, .75, _k - 1)]
STOMPS += [(8, .8, -1), (9, .8, -1), (56, 1.0, 99), (57, 1.0, 99), (76, 1.0, 99), (77, 1.0, 99)]

POPS = []        # (beat, dino index, number, big)
for _k in range(1, 6):
    _b = arrival_start(_k)
    POPS.append((_b + 3, _k - 1, _k, True))
for p in PHRASES:
    if p["tag"] and p["tag"].startswith("count") and p["tag"] != "countdown":
        k = int(p["tag"][-1])
        for j in range(k):
            POPS.append((p["notes"][j][0], j, j + 1, False))
for _i, (_b, _d, _m) in enumerate([(68, 4, 5), (69, 3, 4), (70, 2, 3), (71, 1, 2), (72, 0, 1)]):
    POPS.append((_b, _d, _m, True))
POPS.sort()
