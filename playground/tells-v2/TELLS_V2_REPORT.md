# Tells v2 — playground build, Oct 26, 2026
Built on owner yes Oct 26 ~10:30 PM ET. Playground only, $0, no SAM/API calls,
no live change, no demo change.

## What it is
`playground/tells-v2/tells_v2.py` — image-to-image comparison, not manifest lookup.
Measures user crop and reference image the SAME way, scores 5 independent tells:
aspect ratio, mean RGB, border RGB, edge density, colour histogram correlation.
Verdict rule: >=2 strong mismatches -> Likely Counterfeit; 0 strong + >=3 matches
-> Likely Genuine; else Inconclusive. Verdicts are estimates only, never official,
never guaranteed. A manifest name match alone never produces Genuine here.

## Test 1 — self-test (PIPELINE test, NOT authentication proof)
User crop: agent-loop v2 cropped Alakazam (565x797, SAM box 19/16/584/813)
Reference: sourced-reals/sr-0001-BS-1.png, Alakazam, Base, BS 1, Rare Holo
Result: Likely Genuine, 5/5 tells match, 0 strong mismatches.
  aspect diff 0.0184, mean RGB diff 8.23, border diff 28.43,
  edge density diff 0.0055, histogram diff 0.0787.
Honest label: this crop was DERIVED from this same source image, so a match is
expected. It proves the comparison pipeline runs and scores, it does NOT prove
a real user photo would pass, and it does NOT authenticate a physical card.

## Test 2 — negative test (different card, not a fake)
User crop: same Alakazam crop
Reference: sr-0004-BS-4.png, Charizard, Base, BS 4, Rare Holo
Result: Inconclusive, 2/5 match, 1 strong mismatch (histogram diff 1.0514).
Honest label: a Charizard is NOT a fake Alakazam — it is a different identity.
Inconclusive here is correct behaviour, not a failure: identity must be
confirmed first (name/set/number), THEN tells are scored against the RIGHT
reference. A Counterfeit verdict must only come from tells mismatching the
correct card's reference, not from comparing to the wrong card.

## What is still missing for a real check
- Front AND back user photos (this test is front only, and self-derived).
- A real, independent user photo (phone photo, not a crop of the reference).
- Holo/font/edge tells beyond these 5 pixel tells, and thresholds calibrated
  on real genuine vs known-fake pairs, not on one self-test.
- Back-side tells, and the second-photo reference (owner's second-photo idea)
  so a user photo is compared to official + real-world references.
Next step, when owner says so: run tells v2 on a real owner phone photo vs its
correct reference, and on a known fake vs its correct reference, and report
both before any live use.
