# Two comparison databases — fronts and backs (started Oct 26, 2026, ~11 PM ET)

Owner decision Oct 26, 2026: start TWO separate databases, not one paired set.
- `fronts/` — every real front compared to fronts, every fake front compared to fronts.
- `backs/` — every real back compared to backs, every fake back compared to backs.
- No front is required to match its own back. A front-only photo is fully usable in the fronts database.

## Rules (standing)
- Authenticity labels come only from the owner or documented provenance. Never label a photo by guess.
- Genuine backs must NEVER be filed as fake backs, and owner-printed fake backs (printed help text, Oct 24) must NEVER be filed as fake-back examples — they would teach the wrong back pattern.
- A fake back enters `backs/` only with same-print front+back evidence, or the owner scanning a physical fake's back himself.
- Raw hand/carpet photos never go in public display; SAM card-only crops only.
- No SAM/API spend on these files until the owner says so. Intake only for now.

## Fronts database — first fake calibration intake (Oct 26, 2026 evening)
- 40 files, indices 324–363, all owner-declared FAKES, fronts only, no backs.
- Source files live in `~/workspace/user/files/` (do not move originals); this index points at them.
- Several photos are multi-card group shots — card appearances total ~71, distinct cards fewer (repeats noted). Multi-card photos must be split/cropped per card before counting distinct cards or running tells.
- Full per-file intake: `fake-fronts-intake-2026-10-26.csv` in this folder.
- Status: INTAKE ONLY. Not yet SAM-cropped, not yet tells-scored, not yet merged into any live pool.
- Classification authority: `~/workspace/fake-check/fakes-fronts-batch-2026-10-26-2251.md` (owner-confirmed: all fakes, fronts only). Names in the intake CSV are provisional reads from the chat-rendered photos, NOT full-resolution verified — do not quote them as final until each photo is eyeballed at full size.

## Backs database — status
- EMPTY for fakes. Genuine backs already on file (from the earlier real-photo batches) belong here once indexed, but fake backs still need sourcing — owner decision Oct 26, 2026: "we are going to have to source some fake back."
- Until fake backs exist, the checker must be able to give a front-only verdict, and say so honestly when a back would have helped.

## What this unlocks
- Tells v2 finally has a real known-fake front set to calibrate against, instead of only genuine-vs-genuine pipeline tests. Calibration (genuine front vs fake front, same identity where possible) is still owed — intake is not calibration.

## Backs pool — indexed Oct 27, 2026 (~11:36 AM ET)
- File: `backs-pool-2026-10-27.csv` — 175 rows total: 174 genuine + 1 fake.
  - 169 genuine paired backs from hand triage (`possible_back_pair`,
    all verified present in `~/workspace/user/files/`, all PIL-openable,
    front pair identity from the triage row — back alone does NOT prove
    that identity, backs are mostly uniform).
  - 1 genuine unidentified back: 3798_682_af6t.jpg (Tier 1 sample;
    front identity NOT established, do not invent it).
  - 3 genuine reference designs: English, Japanese, Japanese 1996 red
    deck back (reference-db/backs/).
  - 1 genuine Disco Charizard back (fake-samples/pairs, duplicate in
    shelf-staging counted once).
  - 1 FAKE back: web-05 Disco Charizard fake back, filed as fake only.
  - Excluded: PSA slab backs (slab labels, not card backs) and the
    op-fake-vs-real comparison image (not a single back).
- Status: INDEXED ONLY, NOT CROPPED, NOT CALIBRATED. Originals were
  NOT moved, renamed, or published. Raw hand photos must NOT be used
  as public display images, and must NOT be used as a verdict source
  until card-only cropped + calibrated.
- Diagnostic, Oct 27: `playground/back-pool-score.py` (median tells
  vs first 20 genuine pool backs, $0) gave fake back = Inconclusive
  (median 3 matches, 1 strong) and genuine real back = Likely
  Counterfeit (median 1 match, 2 strong) — INVERTED / UNRELIABLE on
  raw photos. Do NOT ship pool-median as a verdict. Next step needs
  owner yes: SAM card-only crops for the genuine pool (174 × $0.0025
  ≈ $0.44 estimate) or an improved on-device crop, then calibration,
  before back-pool scoring can decide anything.
