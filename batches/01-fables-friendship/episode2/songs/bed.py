"""Underscore beds for the Story Stump scenes (instrumental, series sound, made to loop): python3 bed.py day|night <seed>"""
import os, sys, json, time, requests
HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.elevenlabs.io/v1"
BASE = ["children's TV underscore", "instrumental only", "gentle storybook folk", "100 BPM", "4/4", "D major", "acoustic guitar",
        "glockenspiel", "upright bass", "soft hand drum", "warm"]
MOOD = {"day": (["light and playful", "sunny afternoon"], ["{gentle instrumental, glockenspiel melody over soft guitar}",
                 "{gentle instrumental, guitar melody, light hand drum}", "{gentle instrumental, glockenspiel and guitar answer each other}",
                 "{gentle instrumental, back to the first melody}"]),
        "night": (["soft evening lullaby", "music box", "sleepy and calm", "no drums"], ["{soft instrumental, music box melody over guitar}",
                  "{soft instrumental, warm guitar and bass, calm}", "{soft instrumental, music box and glockenspiel, twinkly}",
                  "{soft instrumental, back to the first melody}"])}
NEG = ["vocals", "singing", "voice", "choir", "humming", "drum kit", "electric guitar", "fade out", "big ending"]
def main(kind, seed):
    extra, parts = MOOD[kind]
    chunks = [dict(text="[Instrumental]\n" + p, duration_ms=24000, positive_styles=(BASE + extra) if i == 0 else BASE[:7] + extra[:2],
                   negative_styles=NEG, context_adherence="high") for i, p in enumerate(parts)]
    key = {"xi-api-key": os.environ["ELEVENLABS_API_KEY"]}
    for attempt in range(8):
        r = requests.post(f"{API}/music?output_format=mp3_44100_192", headers=key, timeout=600,
                          json=dict(model_id="music_v2_5", composition_plan=dict(chunks=chunks), seed=int(seed)))
        if r.status_code == 200: break
        if r.status_code == 429: time.sleep(10 + 10 * attempt); continue
        sys.exit(f"{r.status_code} {r.text[:300]}")
    out = os.path.join(HERE, f"bed_{kind}.mp3"); open(out, "wb").write(r.content); print("wrote", out)
if __name__ == "__main__": main(sys.argv[1], sys.argv[2])
