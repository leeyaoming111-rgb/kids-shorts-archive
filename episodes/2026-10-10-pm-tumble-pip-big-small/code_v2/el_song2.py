"""Episode 2 v2 song: every line SUNG (no spoken lines), same section grid as v1 so the approved animation keeps its timing.
Voices in the raw take are placeholders: each line is converted afterwards to the character's fixed voice (cast_voices.json)."""
import sys, el_song_base as B
SING = ["sung melodically", "legato singing", "sustained sung notes", "clear diction", "sung exactly as written"]
TUM = ["warm bright male tenor lead vocal"] + SING
PIP = ["high light female soprano vocal", "cute and bubbly"] + SING
BOTH = ["male tenor and high female soprano singing together in unison"] + SING
B.BASE = ["children's sing-along song", "bouncy 6/8 jig", "88 BPM", "G major", "tuba oom-pah bass", "tin whistle", "toy piano",
          "pizzicato strings", "glockenspiel", "playful cartoon", "catchy melodic chorus"]
B.NEG = ["spoken word", "talking", "rap", "chant", "shouting", "drum kit", "electric guitar", "autotune", "sad", "dark", "heavy reverb", "choir", "whisper"]
R = [("A big red apple, big and round!", "A tiny berry!", "after"), ("A big leaf fan goes whoosh, whoosh!", "Tiny leaf fan!", "before"),
     ("A big tree stump, what a seat!", "Tiny mushroom!", "after"), ("Big feet go stomp, stomp!", "Small feet hop!", "after")]
S = [("Intro", 4090, "[Chorus]\nBig and small, big and small,", ["tumble"], BOTH),
     ("Chorus", 5450, "[Chorus]\nLet's go find them, find them all!\nBig and small!", ["pip", "tumble"], BOTH + ["catchy hook", "joyful"])]
for k, (big, small, br) in enumerate(R):
    S.append((f"Round {k + 1} big", 3410, f"[Verse]\n{big}", ["tumble"], TUM + ["bouncy, slightly lower and bigger sounding"]))
    if br == "after":
        txt = f"[Verse]\n{small}\n\n[Instrumental break]"; how = ["the short line is sung right at the start", "then a long playful instrumental break with slide whistle"]
    else:
        txt = f"[Instrumental break]\n\n[Verse]\n{small}"; how = ["starts with a long playful instrumental break with a whoosh", "the short line is sung only at the very end"]
    S.append((f"Round {k + 1} small", 3410, txt, ["pip"], PIP + how))
S += [("Finale A", 3410, "[Chorus]\nBig and small, big and small!", ["tumble"], BOTH),
      ("Finale B", 4770, "[Outro]\nBest friends, big and small!\nBye-bye, friends!", ["pip", "tumble"], BOTH + ["warm happy ending", "final held note"])]
B.SECTIONS = S
B.OUT = sys.argv[2] if len(sys.argv) > 2 else "song.mp3"
if sys.argv[1] == "compose": print("song-id", B.compose(int(sys.argv[3]) if len(sys.argv) > 3 else None))
B.check()
