"""Fable 10 verse tool: el_batch.py plus a voice for the ant ("small, bright, cheerful voice") without editing the shared file.
Usage (same as el_batch.py): python3 el_verse.py verse|check|assemble|plan ...  (run from this folder; the key comes from the environment)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BATCH)
import el_batch as E
E.VOICE["ant"] = ["small bright cheerful young voice, tiny and sweet", "one solo singer", "pizzicato strings doubling the melody",
                  "sung melodically, legato singing, clear diction, sung exactly as written"]
E.SERIES = os.path.join(BATCH, "audio", "series")
if __name__ == "__main__":
    cmd = sys.argv[1]
    fd = os.path.abspath(os.path.join(HERE, ".."))
    if cmd == "verse":
        secs, _ = E.fable_sections(fd); out = os.path.join(fd, "code", "out", f"verse_{sys.argv[2]}.mp3")
        E.compose(secs, out, sys.argv[2]); E.check(out, secs)
    elif cmd == "check": E.check(sys.argv[2], E.fable_sections(fd)[0])
    elif cmd == "assemble": E.assemble(fd, *sys.argv[2:4])
    elif cmd == "plan":
        for s in E.fable_sections(fd)[0]: print(s)
