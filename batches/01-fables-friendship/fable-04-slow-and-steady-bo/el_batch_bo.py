"""Fable 4 wrapper around ../el_batch.py: adds Bo's sung style (a warm, gentle low baritone with a soft cello doubling
the melody, Bo's leitmotif) so the Setup B and Moral lines are sung by the music model's own singer, not left
instrumental. Same commands as el_batch.py:  python3 el_batch_bo.py verse . <seed>  |  check  |  assemble  |  plan.
The ElevenLabs key comes from ELEVENLABS_API_KEY only."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))
import el_batch as E
E.VOICE["bo"] = ["warm gentle low male baritone lead vocal", "one solo singer", "soft cello doubling the melody",
                 "sung melodically, legato singing, clear diction, sung exactly as written"]
sys.argv[0] = "el_batch_bo.py"
cmd = sys.argv[1] if len(sys.argv) > 1 else ""
if cmd == "verse":
    secs, _ = E.fable_sections(sys.argv[2]); out = os.path.join(sys.argv[2], "code", "out", f"verse_{sys.argv[3]}.mp3")
    E.compose(secs, out, sys.argv[3]); E.check(out, secs)
elif cmd == "check":
    part = sys.argv[3]
    secs = E.STING if part == "sting" else E.CHORUS if part == "chorus" else E.fable_sections(sys.argv[4])[0]
    E.check(sys.argv[2], secs)
elif cmd == "assemble": E.assemble(*sys.argv[2:6])
elif cmd == "plan":
    for s in E.fable_sections(sys.argv[2])[0]: print(s)
else: sys.exit(__doc__)
