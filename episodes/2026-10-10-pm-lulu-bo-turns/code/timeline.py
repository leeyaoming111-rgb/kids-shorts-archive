"""Single source of truth for 'My Turn, Your Turn!' (Lulu & Bo at the Pond). Audio and video both import this."""
BPM = 104.0
BEAT = 60.0 / BPM          # 0.5769 s
BAR = 4                    # 4/4 swing
DURATION = 45.3
FPS = 30
W, H = 1080, 1920
TRANSPOSE = -9             # written in F around A4 (centre ~68.5), sung in Ab (centre ~59.5 = +3.6 st over af_heart)
VOICE = "af_heart"
BO_VOICE = "am_eric"
TITLE = "My Turn, Your Turn!"
SUBTITLE = "Lulu & Bo at the Pond"
SWING = 2.0 / 3.0          # off-beat eighth lands at 2/3 of the beat

def t(beat):
    return beat * BEAT

PHRASES = []
def sung(text, caption, notes, tag=None, who="lulu"):
    words = caption.split()
    nsyl = sum(len(w.split("-")) for w in words)
    assert nsyl == len(notes), (caption, nsyl, len(notes))
    PHRASES.append(dict(text=text, caption=caption, notes=notes, tag=tag, who=who))

# notes: (beat, duration in beats, written MIDI)
sung("Down the slide we love to go!", "Down the slide we love to go!",
     [(8, .5, 72), (8.5, .5, 69), (9, 1, 72), (10, .5, 69), (10.5, .5, 65), (11, 1, 67), (12, 1.25, 70)], "verse1")
sung("Splash into the pond below!", "Splash in-to the pond be-low!",
     [(14, .5, 74), (14.5, .5, 72), (15, .5, 70), (15.5, .5, 69), (16, 1, 67), (17, .5, 69), (17.5, 1.5, 67)], "verse2")
sung("Bump! Oh no, no one can go!", "Bump! Oh no, no one can go!",
     [(25.5, .75, 69), (26.5, .5, 65), (27, .5, 62), (27.5, .5, 65), (28, .5, 69), (28.5, .5, 67), (29, 1.5, 65)], "problem")
sung("My turn, your turn, wait and see!", "My turn, your turn, wait and see!",
     [(36, .5, 72), (36.5, 1, 69), (37.5, .5, 72), (38, 1, 69), (39, .5, 69), (39.5, .5, 70), (40, 1.25, 74)], "chorus1", "both")
sung("One for you and one for me!", "One for you and one for me!",
     [(42, .5, 74), (42.5, .5, 72), (43, 1, 70), (44, .5, 67), (44.5, .5, 64), (45, .5, 67), (45.5, 1.5, 72)], "chorus2", "both")
sung("Whose turn is it now!", "Whose turn is it now?",
     [(48, .5, 72), (48.5, .5, 72), (49, .5, 69), (49.5, .5, 65), (50, 1, 67)], "q1")
sung("It's Lulu's turn!", "It's Lu-lu's turn!",
     [(53, .5, 65), (53.5, .5, 70), (54, .5, 72), (54.5, 1.25, 74)], "a1")
sung("Whose turn is it now!", "Whose turn is it now?",
     [(57, .5, 72), (57.5, .5, 72), (58, .5, 69), (58.5, .5, 65), (59, 1, 67)], "q2")
sung("It's Bo's turn, hooray!", "It's Bo's turn, hoo-ray!",
     [(62, .5, 67), (62.5, .5, 67), (63, .5, 72), (63.5, .5, 70), (64, 1.25, 69)], "a2")
sung("Taking turns is fun to do!", "Ta-king turns is fun to do!",
     [(66, .5, 72), (66.5, .5, 74), (67, 1, 72), (68, .5, 69), (68.5, 1, 70), (69.5, .5, 69), (70, 1.25, 65)], "outro", "both")
sung("Bye bye, from Lulu and Bo!", "Bye-bye, from Lu-lu and Bo!",
     [(72, .5, 72), (72.5, 1, 67), (73.5, .5, 64), (74, .5, 67), (74.5, .5, 67), (75, .5, 70), (75.5, 1.6, 69)], "bye", "both")

SPOKEN = [
    dict(text="Hi! I'm Lulu!", t0=1.05, speed=1.0, voice=VOICE, who="lulu", caption="Hi! I'm Lulu!"),
    dict(text="And I'm Bo.", t0=2.75, speed=0.9, voice=BO_VOICE, who="bo", caption="And I'm Bo."),
    dict(text="Me first!", t0=t(19.6), speed=1.05, voice=VOICE, who="lulu", caption="Me first!"),
    dict(text="No, me first!", t0=t(21.8), speed=1.0, voice=BO_VOICE, who="bo", caption="No, me first!"),
    dict(text="Let's take turns!", t0=t(31.2), speed=0.92, voice=BO_VOICE, who="bo", caption="Let's take turns!"),
    dict(text="Okay!", t0=t(34.05), speed=1.05, voice=VOICE, who="lulu", caption="Okay!"),
]
GUESS_PAUSES = [(t(51.2), t(53.0)), (t(60.2), t(62.0))]

# ---- chords keyed by beat (root MIDI, quality) ----
F_, Bb, Gm, C_, Dm = (53, "M"), (46, "M"), (43, "m"), (48, "M"), (50, "m")
CHORDS = {0: F_, 4: C_, 8: F_, 12: Bb, 16: Gm, 20: C_, 24: Dm, 28: Bb, 32: C_,
          36: F_, 40: Bb, 44: C_, 48: F_, 52: Bb, 56: F_, 60: C_, 64: F_, 68: Bb, 72: C_, 76: F_}
_KEYS = sorted(CHORDS)
def chord_at(beat):
    k = 0
    for b in _KEYS:
        if b <= beat + 1e-6: k = b
    return CHORDS[k]

# ---- story events (beats) ----
BUMP = 24.5
LULU_LEAP = (34.4, 35.4)            # bank -> rock top
SLIDES = dict(lulu1=(36.6, 39.0), bo1=(42.6, 45.0), lulu2=(54.2, 56.5), bo2=(63.6, 65.9))
SPLASH = {k: v[1] for k, v in SLIDES.items()}
HOPS_INTRO = [0.9, 2.1, 3.3, 4.5, 5.7, 6.9]  # Lulu hop starts (seconds)

# ---- badges (2D lesson words): (t0, t1, text, colour) ----
BADGES = [(t(31.2), t(35.8), "TAKE TURNS", "#FF7A1A"),
          (t(36.0), t(41.6), "MY TURN", "#FF3D6E"),
          (t(42.0), t(47.6), "YOUR TURN", "#00A8E8"),
          (t(53.0), t(56.8), "LULU'S TURN!", "#3CC42A"),
          (t(62.0), t(65.9), "BO'S TURN!", "#FF8A00")]

# ---- shot table: (t0, t1, name) ----
SHOTS = [(0.0, t(8), "crane_down"), (t(8), t(14), "track_side"), (t(14), t(19), "low_water"),
         (t(19), t(21.5), "cu_lulu"), (t(21.5), t(24), "cu_bo"), (t(24), t(30.5), "wide_bump"),
         (t(30.5), t(36), "two_shot"), (t(36), t(42), "track_slide"), (t(42), t(48), "overhead"),
         (t(48), t(54), "ots_bo"), (t(54), t(57), "ride_along"), (t(57), t(66), "low_up_slide"),
         (t(66), t(71), "pad_push"), (t(71), DURATION + 0.1, "crane_up")]
def shot_at(sec):
    for i, (a, b, n) in enumerate(SHOTS):
        if a <= sec < b:
            return i, n, (sec - a) / (b - a), sec - a
    return len(SHOTS) - 1, SHOTS[-1][2], 1.0, sec - SHOTS[-1][0]
