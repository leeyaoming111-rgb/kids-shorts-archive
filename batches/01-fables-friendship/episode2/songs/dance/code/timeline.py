"""Episode v2 dance-break song (el_song2.py reads PLAN_SECTIONS / PLAN_LINES like a fable). 100 BPM, 22 bars, 52.8 s."""
STYLE_EXTRA = ["bouncy dance-along", "energetic but gentle", "call and response"]
PLAN_SECTIONS = [("Intro", 0, 2, "verse"), ("Stretch", 2, 6, "verse"), ("Flap", 6, 10, "verse"), ("Chorus", 10, 13, "chorus"),
                 ("Stomp", 13, 17, "verse"), ("Chorus 2", 17, 20, "chorus"), ("Button", 20, 22, "verse")]
PLAN_LINES = [
    ("Stretch", "tumble", "Stretch up high, and touch the sky!"),
    ("Stretch", "tumble", "Wiggle, wiggle, wiggle, my, oh my!"),
    ("Flap", "pip", "Flap your arms like a little bird!"),
    ("Flap", "pip", "Tweet, tweet, tweet is the magic word!"),
    ("Chorus", "both", "Big or small, short or tall,"),
    ("Chorus", "both", "friends help friends, that's best of all!"),
    ("Stomp", "both", "Stomp, stomp, stomp, and turn around!"),
    ("Stomp", "both", "Jump up high, and land on the ground!"),
    ("Chorus 2", "both", "Big or small, short or tall,"),
    ("Chorus 2", "both", "friends help friends, that's best of all!"),
]
