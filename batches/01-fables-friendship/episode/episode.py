"""Episode 01 data shared by the scene renderer (code/timeline.py), the audio tool (el_episode.py) and assemble.py:
the running order, the fable cut grid, each scene's planned lines, and the sunset-to-night light curve.

Pure data and small helpers; no rendering imports."""
import os, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.normpath(os.path.join(HERE, ".."))
AUDIO = os.path.join(BATCH, "audio", "episode-01")
RENDERS = os.path.join(BATCH, "renders")
SCENE_RENDERS = os.path.join(RENDERS, "episode-01")

BPM = 100.0
BAR = 4 * 60.0 / BPM                     # 2.4 s

# ---- the fables (titles and morals from the batch plan; recap lines are the sung form) ----
FABLES = {
    1: dict(title="Tiny Pip, Big Help!", moral="Tiny friends can be big helpers!"),
    2: dict(title="Sour Apples?", moral="Don't say sour, ask a friend!"),
    3: dict(title="Pebble, Pebble, Plop!", moral="Think it through, try something new!"),
    4: dict(title="Slow and Steady Bo", moral="Slow and steady gets there too!"),
    5: dict(title="The Other Fox", moral="Be happy with what you've got, and share!"),
    6: dict(title="Busy Little Ants", moral="Help a little every day!"),
    7: dict(title="Scarf Off!", moral="Gentle and kind works best!"),
    8: dict(title="Pip Who Cried Help", moral="Tell the truth, so friends know!"),
    9: dict(title="Stronger Together", moral="Together we are strong!"),
    10: dict(title="One Good Turn", moral="Help a friend, and a friend helps you!"),
}
def fable_dir(n):
    """the fable's folder, whatever its slug (other workers name them); None if it does not exist yet"""
    hits = sorted(glob.glob(os.path.join(BATCH, f"fable-{n:02d}-*")))
    return hits[0] if hits else None
def fable_still(n, near):
    """the archived 16:9 still closest to `near` seconds, or None (placeholder page)"""
    d = fable_dir(n)
    if not d: return None
    best = None
    for p in glob.glob(os.path.join(d, "stills", "wide_*.jpg")):
        try: t = float(os.path.basename(p)[6:-4])
        except ValueError: continue
        if best is None or abs(t - near) < abs(best[0] - near): best = (t, p)
    return best[1] if best else None
HOOK_STILL, STORY_STILL = 2.6, 29.0

# ---- fable cut grid (the same in every fable: 100 BPM, 20 bars) ----
HOOK_END, STING_END = 1.5 * BAR, 2.5 * BAR          # 3.6, 6.0: the sting is dropped
CHORUS_START, BUTTON_START = 16 * BAR, 19 * BAR     # 38.4, 45.6
CHORUS_FABLES = {1, 5, 8}                           # first, middle and last keep the full moral chorus
XF = 0.5                                            # dissolve between segments (video and audio)
HANDLE = XF / 2                                     # a fable plays this far past its cut point, centring the dissolve on it
def fable_out(n): return (BUTTON_START if n in CHORUS_FABLES else CHORUS_START) + HANDLE
def fable_len(n): return HOOK_END + fable_out(n) - STING_END

ORDER = ["intro", 1, "link01", 2, "link02", 3, "link03", 4, "link04", 5, "break", "link05", 6, "link06", 10,
         "link07", 9, "link08", 7, "link09", 8, "recap", "outro"]
LINK_NEXT = {"link01": 2, "link02": 3, "link03": 4, "link04": 5, "link05": 6, "link06": 10, "link07": 9, "link08": 7, "link09": 8}
RECAP_ORDER = [n for n in ORDER if isinstance(n, int)]

# ---- planned lines per scene: (t, who, text, kind, tags). kind: tts | sting | chorus | recap | lullaby ----
SCENE_LEN = {"intro": 25.0, "break": 20.0, "recap": 53.4, "outro": 15.0}
SCENE_LEN.update({f"link{k:02d}": 8.0 for k in range(1, 10)})
LINES = {
    "intro": [(0.0, "both", "Tumble and Pip!", "sting", ""),
              (3.0, "pip", "Tumble? Tell me a story!", "tts", "[curious] [softly]"),
              (6.6, "tumble", "A story? I've got a whole book of them!", "tts", "[warmly]"),
              (10.2, "tumble", "Fables About Friendship!", "tts", "[proudly] [warmly]"),
              (13.0, "pip", "Ooh! Open it, open it!", "tts", "[excited] [softly]"),
              (17.2, "tumble", "Story number one...", "tts", "[warmly] [storyteller voice]"),
              (19.6, "tumble", "a big kite, and a tiny helper!", "tts", "[warmly]"),
              (22.6, "pip", "That's me!", "tts", "[giggles]")],
    "link01": [(0.6, "pip", "I'm tiny AND helpful!", "tts", "[proudly]"),
               (4.6, "tumble", "You are! Now... a red apple, way up high.", "tts", "[warmly]")],
    "link02": [(0.6, "tumble", "Asking a friend made it sweet.", "tts", "[warmly] [content]"),
               (4.6, "pip", "Next one! A thirsty bird, and a tall jug.", "tts", "[curious]")],
    "link03": [(0.5, "pip", "Count with me! One, two, three, four, five!", "tts", "[cheerful] [slowly]"),
               (5.0, "tumble", "Next... a big race!", "tts", "[warmly]")],
    "link04": [(0.6, "tumble", "Slow and steady Bo! Hooray!", "tts", "[cheerful] [softly]"),
               (4.6, "pip", "Who's that, down in the water?", "tts", "[curious] [softly]")],
    "link05": [(0.6, "tumble", "Phew! Back to our story stump.", "tts", "[relieved] [warmly]"),
               (4.6, "pip", "Look! Little ants, marching along!", "tts", "[curious] [softly]")],
    "link06": [(0.6, "pip", "The ants shared with Tumble!", "tts", "[warmly]"),
               (4.6, "tumble", "And now, the ants need a friend too.", "tts", "[softly]")],
    "link07": [(0.6, "tumble", "Friends help each other.", "tts", "[softly] [warmly]"),
               (4.6, "pip", "Next... a bundle of sticks. Snap!", "tts", "[softly] [playful]")],
    "link08": [(0.6, "pip", "Together, we're strong!", "tts", "[softly]"),
               (4.6, "tumble", "Now... the Wind and the Sun.", "tts", "[softly] [storyteller voice]")],
    "link09": [(0.5, "tumble", "Gentle and kind... like you, Pip.", "tts", "[softly] [warmly]"),
               (3.6, "pip", "One more, please?", "tts", "[sleepy] [softly]"),
               (5.4, "tumble", "The very last one.", "tts", "[whispers]")],
    "break": [(0.3, "tumble", "Story break! Everybody, stand up!", "tts", "[cheerful]"),
              (2.6, "both", "Big or small, short or tall,", "chorus", ""),
              (2.6, "both", "friends help friends, that's best of all!", "chorus", ""),
              (9.8, "both", "Big or small, short or tall,", "chorus", ""),
              (9.8, "both", "friends help friends, that's best of all!", "chorus", ""),
              (17.6, "pip", "Well done, everybody!", "tts", "[cheerful] [softly]")],
    "recap": [(2.6 + 4.8 * k, "both", FABLES[n]["moral"], "recap", "") for k, n in enumerate(RECAP_ORDER)],
    "outro": [(0.4, "both", "Big or small, short or tall,", "lullaby", ""),
              (3.9, "both", "friends help friends, that's best of all.", "lullaby", ""),
              (8.6, "both", "Goodnight, friends!", "tts", "[whispers]")],
}
# the chorus and the stored sting are placed whole: offsets of the take inside the scene
CHORUS_AT = {"break": [2.6, 9.8]}

# ---- music takes for the recap and the outro (el_batch fingerprint, same singers) ----
RECAP_SECTIONS = [("Recap A", 12000, "[Verse]\n{short instrumental intro}\n" + "\n".join(FABLES[n]["moral"] for n in RECAP_ORDER[0:2]), "both")]
for k, name in enumerate("BCDE"):
    RECAP_SECTIONS.append((f"Recap {name}", 9600, "[Chorus]\n" + "\n".join(FABLES[n]["moral"] for n in RECAP_ORDER[2 + 2 * k:4 + 2 * k]), "both"))
RECAP_SECTIONS.append(("Ring-out", 3000, "[Outro]\n{soft instrumental ending}", None))
OUTRO_SECTIONS = [("Lullaby", 7200, "[Chorus]\nBig or small, short or tall,\nfriends help friends, that's best of all.", "both"),
                  ("Lullaby end", 7800, "[Outro]\n{soft music box lullaby ending, slowing down, final chord}", None)]
BED_SECTIONS = [("Bed A", 9600, "[Intro]\n{gentle instrumental, glockenspiel melody over soft guitar}", None),
                ("Bed B", 9600, "[Verse]\n{gentle instrumental, guitar melody, calm evening}", None),
                ("Bed C", 9600, "[Outro]\n{gentle instrumental, glockenspiel and guitar, calm}", None)]
BED_AT = {"link01": 2, "link02": 3, "link03": 4, "link04": 5, "link05": 6, "link06": 7, "link07": 8, "link08": 1, "link09": 4}  # bar offset into the bed

# ---- scene lengths with the real audio, and each scene's place in the episode ----
def scene_len(name):
    p = os.path.join(AUDIO, f"{name}.json")
    if os.path.exists(p): return json.load(open(p))["duration"]
    return SCENE_LEN[name]
def seg_len(item): return fable_len(item) if isinstance(item, int) else scene_len(item)
def starts():
    out, t = {}, 0.0
    for it in ORDER:
        out[it] = t; t += seg_len(it) - XF
    return out, t + XF
LIGHT_KEYS = [("intro", 0.0), ("recap", 0.62), ("outro", 0.82), ("end", 1.0)]
def dusk(ep_t):
    """0 = golden sunset (intro) ... 0.62 = violet twilight (recap) ... 1 = starry night (end of the outro)"""
    st, total = starts()
    pts = [(st[k] if k != "end" else total, v) for k, v in LIGHT_KEYS]
    if ep_t <= pts[0][0]: return pts[0][1]
    for (a, va), (b, vb) in zip(pts[:-1], pts[1:]):
        if ep_t <= b: return va + (vb - va) * (ep_t - a) / max(b - a, 1e-6)
    return pts[-1][1]
