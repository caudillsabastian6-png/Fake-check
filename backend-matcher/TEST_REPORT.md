# Test report — matcher prototype — Oct 28, 2026, playground only

## Verdict: matcher built and tested, but it does NOT pass as a verdict tool

The code works. The separation does not. That distinction is the
whole report, and it is why the threshold proposal is "proposed, not
approved" rather than a green light.

## What passed

- Same file vs itself: 0 on aHash, dHash, pHash, full and centre. PASS.
- Robustness (50% resize + JPEG q70): 0–1 on all hashes. PASS.
  Perceptual hashes survive ordinary re-encoding, as they should.
- All pool files needed for the test resolved on disk: 73 A1 fronts
  + backs, 40 fake fronts, 7 anchor fronts (from fake-samples/).
- pHash DCT implemented in numpy, no cv2, no model calls, $0.
  (One fix during testing: the DCT matrix was recomputed per image;
  it is now cached. Hashing time for the full test dropped from
  ~48 s to ~33 s for 120 images — still slow in pure Python, and
  irrelevant to the verdict question.)

## What failed (as a verdict tool)

- Genuine same-identity hand photos score centre-pHash 10, 16, 16 —
  outside every textbook near-duplicate threshold (≤5, ≤8, ≤10
  would reject 2 of 3). The matcher cannot use published thresholds.
- One fake front's nearest genuine front scores 16 — inside the
  genuine range. A threshold that accepts all 3 genuine pairs
  (≤16) already falsely accepts 1/47 fake-nearest cases, and ≤20
  collapses to 38% fake-nearest accept.
- Nearest-neighbour overlap: a different A1 card sits at distance 10
  from another card, so top-1 hash ranking misidentifies. Ranking
  is a shortlist, never an identification.
- Genuine backs score median 6 against each other: back hashes
  cannot prove identity, by design of the card back itself.
- Sample size: n = 3 genuine pairs is far too small to approve
  anything, and there are no same-identity fake-vs-genuine pairs
  and no card-only crops in pool v2.

## Files in this folder

- `matcher.py` — aHash/dHash/pHash, full + centre variants,
  Hamming comparison, candidate ranking.
- `test_matcher.py` — the test that produced these numbers.
- `test_results.json` — full per-test statistics.
- `threshold_raw.json` — raw centre-pHash lists (same / impostor /
  fake-nearest) used for the threshold table.
- `THRESHOLD_PROPOSAL.md` — candidate thresholds, false-accept /
  false-reject table, two-gate verdict rule, approval blockers.
- `SIGNIN_DESIGN.md` — server sign-in design (scrypt, tokens,
  account-bound coins/referrals, reset fallback needing owner approval).
- `MULTIBACKEND_ROLES.md` — SSD / Seagate / Workers roles, one live
  writer rule, G1 re-evaluation Oct 30.

## Untouched, by design

- Live Penguin backend: not edited. `~/card-cauldron-backend/`
  and its backend.db were not read for writing and not modified.
- Demo: not edited. No demo file changed in this task.
- No push, no deployment, no spend. All work is in
  `~/workspace/fake-check/playground/backend-matcher-2026-10-28/`.

## Still missing before any real verdict ships

1. Card-only crops before hashing (background is in the score today).
2. Same-physical-card re-photographs, n in the hundreds.
3. Same-identity fake vs genuine pairs (the true false-accept test).
4. Held-out calibration re-run on the enlarged set.
5. Owner approval of a named final threshold (currently NONE SET
   for verdicts — this task proposes a candidate ranking band only).
6. Latch review of the threshold proposal, the sign-in design, and
   the multi-backend roles doc.
7. A deployment host for the matcher: Penguin stdlib cannot run
   Pillow/numpy as-is (see MULTIBACKEND_ROLES.md §3 and the G1
   re-evaluation point). Until a host is chosen, the matcher is a
   playground prototype, not a live capability.
