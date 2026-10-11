# Review log: Tumble & Pip, Episode 2

Independent reviewer subagent (tools/REVIEWER.md), contact sheets with one frame every 0.5 s, plus geometry QA (qa_geom.py, 15 fps).

## Round 1: FAIL
- Tumble hovering above the stump seat. Fixed: seat height from the body mesh's lowest vertex.
- Basket popping during set-down. Fixed: lowered straight down in one move.
- Apple covering Tumble's face. Fixed: hugged at chest height, camera raised.
- Tiny leaf off-frame; mushroom gag landing out of frame; berry continuity; Boing caption timing; weak split labels; captions crossing cuts. All fixed.

## Round 2: FAIL (3 HIGH)
- HIGH: no berry visible in the "Tiny berry!" macro. Fixed: the berry sits on the blanket in frame, Pip points at it.
- HIGH: Pip hovering ~2 cm above the rolling apple (run bob), Tumble out of frame. Fixed: Pip locked to the apple top with a waddle; Tumble chases right behind; camera centred between them.
- HIGH: split-screen caption across Pip's eyes and the "small" label. Fixed: caption at the bottom of the bottom panel, label larger and opaque.
- MED: caption over Pip in the apple shot; flat oval "tiny leaf" with no fanning; gag-2 landing cut by the frame edge. All fixed.
- LOW: basket half off the blanket, overhead framing, caption fade-in before cuts, Pip off-frame at the stump, tiny stomp unclear. All fixed.

## Round 3: PASS
- MED: Pip above the apple for the first 0.5 s of gag 0. Fixed after the pass: Pip starts the shot on the apple.
- LOW (left): Tumble's snout near the basket rim in the overhead; Tumble's face cut at frame top-right in the tiny-leaf macro; Pip partly behind a mushroom in the stump shot; split caption covers Pip's feet; Tumble mid-blink on the gag-2 landing frame.

Geometry QA: 108 issues at first build, 0 at queue time (penetration, floating, below-ground, pops).
Geometry QA missed what the reviewer caught (hovering 2 cm, missing prop, captions over faces), so both checks stay.
