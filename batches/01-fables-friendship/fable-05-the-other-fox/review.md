# Fable 5 review log

## Round 0 (earlier worker, pre-audio)
Fixes only: berry in beak, reach, framing, reflection clear of captions, crane tree (commit 1329752).

## Round 1 (reviewer on sheets rendered with the real song timing) - FAIL (4 MED, 6 LOW, 0 HIGH)
- MED [short] 24.5: reflection forearm floated loose during the ripple wobble. Fix: ripple wavelength lengthened (3.0 per metre of depth, was 7.0), amplitude 0.12 eased in over 0.8 s.
- MED [short+wide] 0-3.5, 11.5-15.5, 46.5: reflection ears under or touching the caption box. Fix: hook, bigger, copycat, wobble, moral, chorus and crane cameras framed 0.3-0.5 units taller.
- MED [short+wide] 6.5-20: apple held across the muzzle. Fix: two-paw hold lowered (forward angle 1.25 -> 0.98), so the apple sits on his chest, in the reflection too.
- MED [short+wide] 24.5-27.5: apple stayed at the water line. Fix: drifts faster down the stream and out to the side, off frame by about 26.5 s.
- LOW fixed: share shot widened (Pip cut by the edge); moral/chorus ear tips off the top edge.
- LOW left: reach lean is modest; "Blehhh!" lands at the end of the copycat shot; high-five and star puff are short at 0.5 s sampling; one paw waggles in the silly face.

## Round 2 - PASS (0 HIGH, 0 MED)
All round 1 MEDs resolved in both aspects. LOW left as is: reflection ear tips graze the caption in the bigger shot and on "Bye-bye!", proud-shot apple passes the cheek (mouth stays visible), share-shot reflection at the bottom edge, wide share ear tips at the top, weak reach lean, "Blehhh!" timing, small high-five, one-paw waggle.

## Polish pass (2026-10-20)

New song: take_11 (one continuous take, `T.DURATION` 50.4 s; Hook 0-2.93, Sting 2.93-6.0, Button 45.6-50.4).
Spoken lines re-voiced with `el_voice2.py` (stability 0.5, anchor-matched), mixed with `el_mix2.py --nostt`:
-14.0 LUFS, 0 problems. Spoken t0: Blehhh 19.26, Whoa wobbly 24.88, Your berry is the best 31.98, Bye-bye 46.3.

### Fixes for the reviewer's issue list (rev/issues/05.md)
- MED berry take-off into the paw: the paw is out by a+0.45 before Pip lifts off; Pip turns to the paw in the air
  (no yaw snap) and flies up / across / in on the far side of the paw (offset away from Tumble). Short framing widened
  so Pip stays in frame.
- MED title fly-in collision: new path from the far bank, high, then straight down onto the log; title camera moved
  to yaw 62 so Pip lands beside Tumble on screen; head turn 0.3 (was 0.55). Wide title target lowered under the card.
- MED tongue without a mouth: the kit's single mouth is held open (FK.MOUTH track patched) whenever the silly face is
  on; the tongue is drawn only while the mouth is open.
- MED apple over the mouth: proud pose holds the apple out at arm's length at shoulder height (beside him, clear of
  the face); reach pose solved so the mouth sits 0.3 above the apple.
- MED eats his half: paw-to-mouth pose solved numerically (berry 0.06 under the mouth); mouth opens for the bite.
- MED Pip's mouth hidden on his sung line: berry delivered to the paw before "Here's" (a+1.2), Pip takes his half
  only after "you!" (PIP_TAKE = line end + 0.12), so his beak is free for the whole line.
- MED chorus to button jump cut: the crane starts on the chorus camera exactly and Tumble starts in the chorus-end
  pose; the crane finishes at a+2.0 and holds; characters settle by DURATION-0.8 (frozen pose under the fade).
- MED reach beat: restaged. High three-quarter camera from downstream (Pip clear to the side, the stream and the
  reflection visible below), Tumble turns a little towards the near-bank water, goes up on his toes, leans out and
  reaches down with both paws; the apple slips and lands just below him, then he turns back to watch it float away.
  The near tree is left out of this one shot only (it stands where this camera is).
- LOW fixed: wide share framing (ears), berry half touching the beak tip (BEAK_HALF), copycat water apple back to
  normal size (re-grows on "THAT"), "Blehhh!" now ends inside the copycat shot (shot extended, face held while it is
  heard), "Whoa, wobbly!" ends before the berry cut, "Your berry is the best!" caption ends before the moral, hook
  peering and pointing made visible, button tongue bigger with a head waggle and wings by his face, end hold.
- LOW left: share shot reflection under the log (real reflection; camera raised to 30 deg so it is smaller), Bye-bye
  caption over the reflection in the short crane, chorus high-five and star puff (kit dance, not changed).

QA (30 fps, penetration + screen_contact): 0 issues in both aspects. Fixed causes on the way: feet into the round
log during the reach lean (up on his toes), tail into Pip during the reach turn (smaller body turn, head does the
rest), falling apple through the log (lands further out).

### Polish round 1 (independent reviewer, rev/issues/05_polish_r1.md): PASS, 1 MED, 8 LOW
- MED reach 21.0-23.5, apple on his lower lip: fixed. In the reach his apple now rides the near paw, held low at hip
  height and out over the water, while the other paw stretches forward and down; chin up (head pitch 0.05).
  The held apple now sits 0.12 in front of the paws (was a fixed world offset that pushed it into chest and chin) and
  the head pitches in the hook, bigger, silly-face and copycat shots were lowered. Strict QA with the (apple, fox)
  ignore removed (`QA_STRICT=1 python3 render.py qa`) now shows no apple contact with his head or body in any frame;
  the only remaining contacts are the holding paw itself, so the normal qa_ignore stays for that.
- LOW berry take-off touch at 28.08: fixed. Pip first hops out low, away from the paw, then goes straight up, and turns
  towards the paw only at the top. Clear gap in every frame 28.0-28.7, both aspects.
- LOW proud framing [short]: camera widened (fit 1.45) and re-centred; apple, back and ears inside the frame.
- LOW share reflection strip [short]: subject framed lower (lift -0.04); the reflection now sits mostly under the
  caption band.
- LOW Bye-bye caption over the reflection face [short]: the crane finishes in 1.5 s and ends with more lift and a
  slightly wider fit, so from about 46.8 the caption sits below the reflection's face (it still overlaps at 46.4-46.7
  while the crane is moving).
- LOW left as is: hook peer/point (beat is visible as a paw swing; small at this distance), chorus high-five and star
  puff (kit dance, not changed), copycat/hook fox small in 16:9 (camera shared with the short framing), chorus wing
  touching the cheek outline (reviewer: reads as beside the head).
- QA 0 issues in both aspects. Mix with speech-to-text: -14.0 LUFS, lyric recall 1.0, 0 problems.
  STT also hears a short ad-lib in the song's instrumental around the wobble ("I share that one...") that is in the
  ElevenLabs take itself.
