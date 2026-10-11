import re
"""Single source of truth for 'Tumble & Pip, Episode 1: What's the Weather?'. Audio and video both import this."""
BPM = 132.0
BEAT = 60.0 / BPM          # 0.4545 s
BAR = 3                    # 3/4 waltz
TOTAL_BEATS = 96           # 32 bars
DURATION = 44.9
FPS = 30
W, H = 1080, 1920
TRANSPOSE = -11            # melody written around C4..C5 (centre ~E4), sung in B (centre ~F3, +3.7 st over am_eric)
VOICE = "am_eric"
TITLE = "Tumble & Pip"
SUBTITLE = "What's the Weather?"

def t(beat):
    return beat * BEAT

INTRO = (0, 12)
CHORUS = (12, 24)
def seg_start(k):           # weather segment k = 0..4, 12 beats each
    return 24 + 12 * k
OUTRO = (84, 96)

WEATHER = ["sunny", "cloudy", "windy", "rainy", "rainbow"]
WORD = ["SUNNY", "CLOUDY", "WINDY", "RAINY", "RAINBOW"]
WORD_COL = ["#FFB000", "#6F86B8", "#14B8A6", "#2F7BEB", None]   # None = rainbow letters

PHRASES = []
def sung(text, caption, notes, tag=None):
    words = caption.split()
    nsyl = sum(len(re.split("[-~]", w)) for w in words)
    assert nsyl == len(notes), (caption, nsyl, len(notes))
    PHRASES.append(dict(text=text, caption=caption, notes=notes, tag=tag))

# ---- chorus (theme hook): 2 lines x 2 bars ----
sung("Peek out, what do you see!", "Peek out, what do you see?",
     [(12, 1, 60), (13, 1, 64), (15, .5, 72), (15.5, .5, 71), (16, .5, 69), (16.5, .6, 67)], "chorus")
sung("Sun or rain, come sing with me!", "Sun or rain, come sing with me!",
     [(18, 1, 62), (19, 1, 65), (20, 1, 69), (21, .5, 67), (21.5, .5, 65), (22, .5, 62), (22.5, .6, 60)], "chorus")

# ---- weather verses: question | guessing pause | answer | action ----
ANSWER = [("It's sunny!", "It's sun-ny!", [60, 64, 67]),
          ("It's cloudy!", "It's cloud-y!", [60, 64, 65]),
          ("It's windy!", "It's wind-y!", [62, 65, 69]),
          ("It's rainy!", "It's rain-y!", [64, 62, 60]),
          ("A rainbow!", "A rain-bow!", [60, 64, 72])]
ACTION = [("Hat on, let's play!", "Hat on, let's play!", [67, 65, 64, 62]),
          ("Clouds float away!", "Clouds float a-way!", [65, 64, 62, 59]),
          ("Whoosh, fly my kite!", "Whoosh, fly my kite!", [69, 67, 65, 62]),
          ("Boots on, splash, splash!", "Boots on, splash, splash!", [64, 64, 62, 62]),
          ("Colours so bright!", "Col-ours so bright!", [67, 69, 71, 72])]
for k in range(5):
    s = seg_start(k)
    sung("What's the weather!", "What's the wea-ther?", [(s, .75, 67), (s + .75, .5, 69), (s + 1.25, .5, 67), (s + 1.75, .8, 64)], f"q{k}")
    tx, cap, nn = ANSWER[k]
    sung(tx, cap, [(s + 5.5, .5, nn[0]), (s + 6, .75, nn[1]), (s + 6.75, .75, nn[2])], f"a{k}")
    tx, cap, nn = ACTION[k]
    sung(tx, cap, [(s + 8.5, .5, nn[0]), (s + 9, .75, nn[1]), (s + 9.75, .5, nn[2]), (s + 10.25, .8, nn[3])], f"act{k}")
QUESTION_PAUSE = [(t(seg_start(k) + 2.5), t(seg_start(k) + 5.5)) for k in range(5)]

# ---- outro ----
sung("Every weather, we can play!", "Ev-ery wea-ther, we can play!",
     [(84, .5, 64), (84.5, .5, 65), (85, 1, 67), (86, .5, 64), (87, .5, 65), (87.5, .5, 62), (88, .65, 60)], "outro")
sung("Bye bye, friends!", "Bye~bye, friends!", [(90, 1, 67), (91, 1, 64), (92, 2.4, 60)], "bye")

SPOKEN = [dict(text="Hi! I'm Tumble, and this is Pip!", t0=2.2, speed=0.95, caption="Hi! I'm Tumble, and this is Pip!")]

# ---- chords: one per bar (beat of bar start) ----
_C, _Am, _F, _G, _Dm = (48, "M"), (45, "m"), (53, "M"), (55, "M"), (50, "m")
CHORDS = {}
for i, c in enumerate([_C, _F, _C, _G]):
    CHORDS[3 * i] = c
for i, c in enumerate([_C, _Am, _F, _G]):
    CHORDS[12 + 3 * i] = c
ANS_CHORD = [_C, _F, _Dm, _Am, _C]
for k in range(5):
    s = seg_start(k)
    CHORDS[s] = _C; CHORDS[s + 3] = _F; CHORDS[s + 6] = ANS_CHORD[k]; CHORDS[s + 9] = _C if k == 4 else _G
for i, c in enumerate([_C, _G, _F, _C]):
    CHORDS[84 + 3 * i] = c
def chord_at(beat):
    b = int(beat // 3) * 3
    while b not in CHORDS and b > 0:
        b -= 3
    return CHORDS.get(b, _C)

# ---- shot table: (t0, t1, name) ----
SHOTS = [(0.0, t(12), "crane_in"), (t(12), t(24), "track_arc")]
for k in range(5):
    s = seg_start(k)
    SHOTS.append((t(s), t(s + 5), f"tilt{k}"))          # cut to the answer shot half a beat before it is sung
    SHOTS.append((t(s + 5), t(s + 12), WEATHER[k]))
SHOTS.append((t(84), DURATION + 0.1, "pullback"))
def shot_at(sec):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= sec < b:
            return i, n, (sec - a) / (b - a), sec - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, sec - SHOTS[-1][0]

# weather change happens during the guessing pause of segment k
def weather_weights(sec):
    """returns list of 6 weights: [clear-start, sunny, cloudy, windy, rainy, rainbow]"""
    w = [1.0, 0, 0, 0, 0, 0]
    cur = 0
    for k in range(5):
        a, b = t(seg_start(k) + 2.2), t(seg_start(k) + 5.2)
        if sec >= b:
            cur = k + 1
        elif sec > a:
            u = (sec - a) / (b - a); u = u * u * (3 - 2 * u)
            w = [0.0] * 6; w[cur] = 1 - u; w[k + 1] = u
            return w
    w = [0.0] * 6; w[cur] = 1.0
    return w

# SFX / animation events
HOPS_RAIN = [seg_start(3) + x for x in (9.75, 10.25, 11.0)]     # splash hops on "boots on splash splash"
HAT_DROP = seg_start(0) + 6.0
UMBRELLA_POP = seg_start(3) + 6.0
SLIDE_IN = (2.0 / BEAT, 3.3 / BEAT)
