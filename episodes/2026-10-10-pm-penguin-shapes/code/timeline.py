"""Single source of truth for 'Penguin Shapes!'. Audio and video both import this."""
BPM = 120.0
BEAT = 60.0 / BPM          # 0.5 s
TOTAL_BEATS = 88
TAIL = 0.9
DURATION = TOTAL_BEATS * BEAT + TAIL   # 44.9 s
FPS = 30
W, H = 1080, 1920
TRANSPOSE = -5             # melody written around C4..A4, sung in G (centre ~C4 for af_heart @ ~206 Hz, +3.5 st)
VOICE = "af_heart"
TITLE = "Penguin Shapes!"

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
COUNTDOWN = (68, 74)       # "Circle, square, triangle, star, heart!"
HOORAY = 74
ENDING = (76, 88)

SHAPES = ["circle", "square", "triangle", "star", "heart"]
# saturated lesson colours (the most saturated things on screen)
SHAPE_COL = ["#FF6A1F", "#1F86F0", "#1DB954", "#F7B500", "#F0367E"]

# ---- sung phrases: (tts text, caption with hyphenated syllables, [(beat, dur, midi)]) ----
PHRASES = []
def sung(text, caption, notes, tag=None):
    words = caption.split()
    nsyl = sum(len(w.split("-")) for w in words)
    assert nsyl == len(notes), (caption, nsyl, len(notes))
    PHRASES.append(dict(text=text, caption=caption, notes=notes, tag=tag))

def chorus(b0, tag):
    sung("Waddle, waddle, slide and play!", "Wad-dle, wad-dle, slide and play!",
         [(b0, .5, 64), (b0 + .5, .5, 62), (b0 + 1, .5, 64), (b0 + 1.5, .5, 62),
          (b0 + 2, .5, 67), (b0 + 2.5, .5, 69), (b0 + 3, .85, 67)], tag)
    sung("Find a shape with me today!", "Find a shape with me to-day!",
         [(b0 + 4, .5, 65), (b0 + 4.5, .5, 65), (b0 + 5, .5, 64), (b0 + 5.5, .5, 64),
          (b0 + 6, .5, 62), (b0 + 6.5, .5, 62), (b0 + 7, .85, 60)], tag)

chorus(8, "chorus1")
SHAPE_NOTE = [67, 67, 69, 69, 72]
ANSWERS = [
    ("Round and round and round!", "Round and round and round!",
     lambda c: [(c, 1, 64), (c + 1, .5, 62), (c + 1.5, 1, 60), (c + 2.5, .5, 62), (c + 3, .8, 67)]),
    ("Four straight sides!", "Four straight sides!",
     lambda c: [(c, 1, 64), (c + 1, 1, 62), (c + 2, 1.6, 67)]),
    ("Three pointy corners!", "Three poin-ty cor-ners!",
     lambda c: [(c, 1, 64), (c + 1, .5, 64), (c + 1.5, .5, 62), (c + 2, .5, 67), (c + 2.5, 1.1, 67)]),
    ("Five pointy tips!", "Five poin-ty tips!",
     lambda c: [(c, 1, 60), (c + 1, .5, 64), (c + 1.5, .5, 64), (c + 2, 1.6, 67)]),
    ("A heart for you!", "A heart for you!",
     lambda c: [(c, .5, 64), (c + .5, 1, 67), (c + 1.5, .5, 65), (c + 2, 1.6, 67)]),
]
for k in range(1, 6):
    b0 = arrival_start(k)
    sh = SHAPES[k - 1]; N = SHAPE_NOTE[k - 1]
    head = [(b0, .5, 60), (b0 + .5, .5, 64), (b0 + 1, .5, 60), (b0 + 1.5, .5, 64), (b0 + 2, .5, 65), (b0 + 2.5, .5, 65)]
    if sh == "circle":
        tail, cap = [(b0 + 3, .5, N), (b0 + 3.5, .45, N - 2)], "CIR-CLE"
    elif sh == "triangle":
        tail, cap = [(b0 + 3, .34, N), (b0 + 3.34, .33, N - 2), (b0 + 3.67, .4, N - 4)], "TRI-AN-GLE"
    else:
        tail, cap = [(b0 + 3, .85, N)], sh.upper()
    sung(f"Waddle, waddle, here's a {sh}!", f"Wad-dle, wad-dle, here's a {cap}!", head + tail, f"arrive{k}")
    txt, capa, fn = ANSWERS[k - 1]
    sung(txt, capa, fn(b0 + 4), f"answer{k}")
chorus(56, "chorus2")
sung("Now let's name them all!", "Now let's name them all!",
     [(64, .5, 67), (64.5, .5, 67), (65, .9, 69), (66, .9, 67), (67, .7, 62)], "backdown")
sung("Circle, square, triangle, star, heart!", "Cir-cle, square, tri-an-gle, star, HEART!",
     [(68, .5, 60), (68.5, .45, 60), (69, .85, 62), (70, .34, 64), (70.34, .33, 64), (70.67, .3, 64),
      (71, .85, 65), (72, 1.5, 67)], "countdown")
sung("Hooray!", "Hoo-ray!", [(74, .5, 64), (74.5, 1.2, 67)], "hooray")
sung("Waddle, waddle, bye bye!", "Wad-dle, wad-dle, bye-bye!",
     [(76, .5, 67), (76.5, .5, 64), (77, .5, 67), (77.5, .5, 64), (78, .75, 62), (79, 2.4, 60)], "bye")

# ---- spoken lines: (text, start seconds, speed) ----
SPOKEN = [dict(text="Hi friends! Let's find shapes with the penguins!", t0=0.45, speed=0.95,
               caption="Hi friends! Let's find shapes with the penguins!")]

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
STOMPS = []      # footfalls (beat, strength, who) who: penguin index 0..4, -1 = offscreen, 99 = all
for _k in range(1, 6):
    _b = arrival_start(_k)
    STOMPS += [(_b, 1.0, _k - 1), (_b + 1, 1.0, _k - 1), (_b + 2, .45, _k - 1), (_b + 2.5, .45, _k - 1), (_b + 3, .75, _k - 1)]
STOMPS += [(8, .8, -1), (9, .8, -1), (56, 1.0, 99), (57, 1.0, 99), (76, 1.0, 99), (77, 1.0, 99)]

POPS = []        # (beat, penguin index, shape index, finale)
for _k in range(1, 6):
    POPS.append((arrival_start(_k) + 3, _k - 1, _k - 1, False))
for _i, _b in enumerate([68, 69, 70, 71, 72]):
    POPS.append((_b, _i, _i, True))
POPS.sort()
