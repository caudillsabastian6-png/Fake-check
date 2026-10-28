# Threshold proposal — image matcher — PLAYGROUND / TEST ONLY, Oct 28, 2026

## Status: PROPOSAL ONLY — NOT APPROVED, NOT A VERDICT THRESHOLD

No threshold in this document is approved for a real verdict. Owner
threshold approval is still owed, and the test set below is too small
to approve a final threshold on its own (see §5). Anyone quoting a
number from this file as "the approved threshold" is misquoting it.

## 1. What was actually tested

Matcher: `matcher.py` — aHash, dHash, pHash (numpy DCT), full-photo
and centre-crop (5:7, centred) variants. Primary score in this
proposal: **centre-crop pHash, Hamming distance, 0–64** (lower = more
similar). Centre crop beats full-photo here because pool photos are
hand photos on a surface, not card-only crops — full-photo hashes are
partly background (leather, rug, hand).

Test sets, all from pool v2 (`verification_pool_v2.csv`):
- Genuine same-identity: **n = 3 pairs** — the only A1 identities with
  2 distinct front files (Yveltal 019/025, Switch 183/202, Hop 165/202).
  These are distinct photos of the same identity, NOT proven
  re-photographs of the same physical card. This is the weakest leg
  of the test and it is stated as such.
- Impostors: **n = 60** random cross-identity A1 front pairs.
- Fake vs genuine: **n = 47** fake fronts (40 owner-confirmed + 7
  anchor), each scored against its NEAREST A1 genuine front. This is
  a false-accept proxy, NOT a same-identity fake test: the fake
  batch's card-by-card names are unverified, so no fake here is
  proven to be "the fake version of that genuine card".
- Backs: 20 genuine-back vs genuine-back pairs.
- Nearest-neighbour: each of 73 A1 fronts vs its nearest other A1 front.

## 2. Measured results (centre pHash)

| Test | n | min | median | max |
|---|---|---|---|---|
| Genuine same-identity | 3 | 10 | 16 | 16 |
| Impostors (random pairs) | 60 | 18 | 30 | 40 |
| Fake nearest genuine | 47 | 16 | 22 | 26 |
| Genuine back vs genuine back | 20 | 2 | 6 | 22 |
| Nearest other A1 front | 73 | 10 | 18 | 24 |

Sanity and robustness pass: same file vs itself = 0 on all hashes;
same file resized to 50% + JPEG q70 = 0–1. The hashes work as hashes.
The problem is not the code, it is what hand photos contain.

Two results that kill any naive threshold:
1. **A genuine back is a near-duplicate of every other genuine back**
   (median 6). A back hash can never prove identity — backs are a
   uniform design. Backs are a genuine/fake design check only.
2. **Nearest-neighbour overlap:** some different A1 card sits at
   centre-pHash 10 from another card. Ranking by hash alone and
   taking top-1 would misidentify. The matcher is a candidate
   shortlist, never an identification.

## 3. False-accept / false-reject at each candidate (centre pHash)

"Genuine accept" = same-identity pair at or below T.
"Impostor accept" = random impostor pair at or below T.
"Fake-nearest accept" = fake front whose nearest genuine is at or
below T (the dangerous direction: a fake looking genuine).

| T | Genuine accept | Impostor accept | Fake-nearest accept |
|---|---|---|---|
| ≤5 (literature near-duplicate) | 0/3 (0%) | 0/60 (0%) | 0/47 (0%) |
| ≤8 | 0/3 (0%) | 0/60 (0%) | 0/47 (0%) |
| ≤10 | 1/3 (33%) | 0/60 (0%) | 0/47 (0%) |
| ≤12 | 1/3 (33%) | 0/60 (0%) | 0/47 (0%) |
| ≤16 | 3/3 (100%) | 0/60 (0%) | 1/47 (2%) |
| ≤18 | 3/3 (100%) | 1/60 (2%) | 4/47 (9%) |
| ≤20 | 3/3 (100%) | 2/60 (3%) | 18/47 (38%) |

Read this honestly: at the textbook ≤5, the matcher rejects every
genuine hand-photo pair in our set. At ≤16 it accepts all 3 genuine
pairs and 0 random impostors, but also 1 fake-nearest. At ≤20 it
collapses (38% fake-nearest accept). The window 16–17 is real in
this tiny sample and fragile because n = 3.

## 4. Comparison with published practice (Oct 28 web literature)

| Method | Published rule of thumb | Fits our hand photos? |
|---|---|---|
| 64-bit pHash | 0–5 near-duplicate, 6–10 gray, >10–12 different; most production systems ≤5 | NO — our genuine same-identity hand photos are 10–16. Copying ≤5 would reject real cards. |
| dHash | ≤8 near-duplicate | NO — our same-identity centre dHash values are 16, 8, 11. |
| aHash | ≤10 near-duplicate | Mixed — same-identity centre aHash 4, 3, 4 passes, but aHash is the weakest hash and impostor aHash goes as low as 4 in our set. |
| SSIM | >0.95 identical, 0.80–0.95 highly similar | Not tested here (needs aligned crops); do not quote it as our threshold. |
| CLIP cosine | >0.90 identical, 0.70–0.90 similar | Not tested here (needs a model call); do not quote it as our threshold. |
| Face-verification cosine (e.g. FaceNet >0.7) | Model-specific | NOT transferable to cards at all. Never cite a face threshold for a card matcher. |

Lesson, stated plainly: **a threshold must be calibrated on OUR
labeled pairs for false-accept rate, not copied from another domain.**
The literature numbers above describe near-duplicate detection on
aligned, cropped, near-identical images. Our inputs are angled hand
photos of (possibly different physical copies of) a card. Different
problem, different numbers.

## 5. Recommended operating point — FOR CANDIDATE RANKING ONLY

Proposed, pending owner approval AND a bigger test set:

- **Strong candidate (shortlist only): centre pHash ≤10.** Conservative;
  it will miss most genuine hand photos (only 1/3 in our set), so it
  can prioritise candidates, never pass or fail a card.
- **Gray zone: centre pHash 11–17 — ALWAYS Inconclusive on image
  alone, never Likely (either way).** This replaces the literature
  6–10 gray zone for our input type: our genuine pairs live at
  10–16, and a fake-nearest already appears at 16. Anything in gray
  must be decided by set + number + tells, not by the hash.
- **No image match: centre pHash ≥18.** Do not call this "fake" —
  angle, lighting, sleeve glare, or a different physical copy can
  all push a genuine card here. It means: needs a better photo or a
  different check, verdict Inconclusive.
- **dHash as a second opinion only:** report centre dHash alongside
  pHash; do not set a standalone dHash pass/fail in this proposal
  (same-identity values 8–16 overlap impostors).

## 6. The two-gate verdict rule (non-negotiable in this proposal)

A false accept (calling a fake genuine) is worse than a false
reject (calling a genuine card Inconclusive), because a false accept
ships a fake into the market with our name on it. So:

1. **Gate 1 — identity, first, always:** set + printed number must
   resolve exactly via the identity index. The matcher never names a
   card. Image-only (no set/number) = needs_input, never a guess.
2. **Gate 2 — tells + image check:** the tells engine must pass AND
   the image candidate must be in the strong/gray band with no
   fake-side tell match. A gray-band image result alone never
   upgrades a card to Likely Genuine, and a high-distance image
   result alone never downgrades a card to Likely Counterfeit.
3. **Any gate fails, or any input is gray → Inconclusive.** No
   cross-source Likely, no Likely from a single signal.

## 7. What is still missing before ANY threshold can be approved

- Same-physical-card re-photographs (front, twice, different days/
  lighting) — n in the hundreds, not 3.
- Card-only crops (SAM or equivalent) before hashing — background is
  currently part of the score.
- Same-identity fake vs genuine pairs (a fake of a specific card vs
  the genuine of that same card) — the true false-accept test, which
  pool v2 does not contain.
- A larger impostor set and a held-out test set (calibrate on one
  half, test on the other — never report accuracy on the set the
  threshold was tuned on).
- Calibration re-run on the enlarged set, Latch review, and a named
  owner approval of the final operating point. Until then, threshold
  status remains: **PROPOSED, NOT APPROVED.**
