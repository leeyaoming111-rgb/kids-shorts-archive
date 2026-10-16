# Review log: Tumble & Pip Fables 3, Pebble, Pebble, Plop!

An independent reviewer subagent (Opus) followed `tools/REVIEWER.md`. It worked from contact sheets with one frame
every 0.5 s in both aspects (9:16 Short and 16:9 episode framing), plus geometry QA (`qa_geom.py`, 15 fps), and
rendered extra stills where needed. All rounds ran on the real sung word times (verse seed 3), because the song was
generated before the first review: events and shot splits come from the sung words, as the Fable 2 log advised.

## Geometry QA

- Before round 1: 0 on the real word times.
- Round-1 restaging (drink pose, long wall, cottage moved): 5 issues (wall vs cottage, Pip vs wall top, Pip vs head
  in the drink, head vs jug). Fixed (cottage moved back, Pip higher on the wall, Pip lifts off after his sip, drink
  distance 1.18). Back to **0**.
- Final: **0**.

## Round 1: FAIL (4 HIGH, 6 MED)

- HIGH: the paw never visibly went into the jug (camera in front, the jug hid the arm); Pip's head sank into Tumble's
  muzzle in hot_walk; Pip hovered at Tumble's face during the leaf lift so the pick-up could not be seen; the drink
  shot was 1.46 s with the tongue outside the rim and "Ahh!" after the cut.
- MED: water disc too high in the hook (beak almost touching); pebbles teleported from the leaf (Pip never picked
  one up); Tumble's face cropped in wide; static chorus.
- Fixed: new camera angles for hot_walk, paw_in and pull; a long staggered stone wall (it read as a tower); Pip waits
  at the far end of the wall; the leaf lift stays on screen to 28.6 s (cut moved to just before "Pebbles in!");
  the drink shot is 33.93 to 35.69 with the camera square on, brim water visible, Pip sipping first and then lifting
  off, Tumble lapping after, "Ahh!" inside the shot; water starts lower; Tumble stands back in pip_try; bigger
  plop splashes.

## Round 2: FAIL (5 MED)

- MED: the beak still touched the water from above in the hook; the button splash was a perfect ring of beads over
  Tumble's eye; dropped pebbles floated on the water; from every front angle the arm to the jug was hidden (the
  arm swings forward, toward the camera, and his own head and the jug cover it); Tumble's head cut in the wide count.
- Fixed: hook pov steeper with a shorter lean; a real droplet spray (uneven, gravity, small) replaces the puff ring
  for the plops, the pop and the button; pebbles slip under the surface straight after the plop; paw_in is now two
  shots, from behind and above where the arm is seen running to the jug (the pulls use the same side) and a face
  reaction on "stuck!"; wide count camera framed taller.

## Round 3: PASS (0 HIGH, 0 MED, 8 LOW)

- LOW, left as is: pale streak across the muzzle in paw_stuck (the reaching arm from above); Pip flying in two
  shots and on the grass in the next; camera flips behind/front three times in 8 s; ears touch the top edge in the
  wide paw_stuck; static 2.6 s hold on the leaf lift; jug cut by the bottom edge in the wide roll_back; the
  empty leaf already on the grass in the drink; Pip clipped by the right edge at 6.0 in the short; modest chorus
  (shared series dance) and Tumble's open mouth while Pip sings the moral.

## Audio

- Verse seed 3: recall 100%, every line in its section (seed 1: 94.8%, a line outside its section; seed 2 hit the
  two-request limit).
- Joins verse to sting, sting to verse and chorus to verse measure 0.61 to 0.67 (the a-cappella sting; the owner
  approved the sting joins by ear); verse to chorus 0.95.
- Mix: -14.4 LUFS, full-mix recall 98.4%.
