# GitHub sweep tests — TEST REPORT, Oct 28, 2026

Playground only, $0, no live demo change, no training, no spend, no endpoint
left live. Source report: `../github-sweep-2026-10-28/REPORT.md`.
Test code and raw results in this folder only. Nothing in this folder was
copied into the live demo or the old-plus playground.
Folder size at delivery: ~542 MB, almost all of it the local venv,
the cloned CollectorVision repo (test copy only) and the downloaded
Pokémon catalog cache — not app code. The venv can be deleted and
rebuilt if space matters; the report, scripts and JSON results above
are the durable part.

**Environment note (matters for reproducing these numbers):** system Python
3.12 has Pillow 10.2 + numpy only. Tests ran in a local venv in this folder
with imagehash + onnxruntime + CollectorVision installed from GitHub.
CollectorVision's Hugging Face download first failed on a proxy-environment
parsing error in this VM; it worked after simplifying the no-proxy list to
localhost only (no credentials, no proxy values are recorded here).
Tesseract could not be installed in this VM (see Test 3) — that part is
reported as blocked, not faked.

## Test 1 — CollectorVision, image-to-identity matcher — PASS, with a licence gate

Licence: AGPL-3.0, confirmed in the cloned repo's LICENSE file.
**TEST ONLY. Do NOT integrate into the app** — integration needs a separate
owner licence decision, and the Pokémon catalog returns TCGplayer product
IDs, not the app's set + printed number directly (although the record
metadata does carry `collector_number` and `set`, see below).

### Method
- Detector: `NeuralCornerDetector(provider="cpu")`, dewarp to a 448×448 crop,
  rotation-invariant search (upright + 180°, keep the stronger top hit).
- Detector confidence on the 10 A1 fronts was low in absolute terms
  (0.048–0.057) but `card_present` was True for all 10.
- (a) Hosted Pokémon catalog: 10 owner A1 fronts.
- (b) Custom catalogs built from dewarped owner crops only:
  first a 10-card catalog, then a 13-card catalog adding the first photos
  of Yveltal, Switch and Hop so their second photos could be held out.
- (c) One known fake front: Caterpie EX fake front
  `7982_150_qyzu.png` (label says Caterpie EX 12/108, art is Charizard).

### Files used
10 A1 fronts: Gligar 140/264, Chatot 139/185, Dugtrio 077/198,
Pyroar 023/203, Leavanny 011/264, Zarude 027/264, Scorbunny 030/202,
Wooloo 221/264, Minun 090/264, Sobble 055/202 (all from
`verification_pool_v2.csv`, tier A1, files in `~/workspace/user/files/`).
Held-out second photos: Yveltal 019/025 (`3839_545_63jm.jpg`),
Switch 183/202 (`4113_52_4xh4.jpg`), Hop 165/202 (`4179_118_j3dr.jpg`).
Raw results: `test1_results.json`, `test1_numbers.json`.

### Numbers
(a) Hosted Pokémon catalog, top-1, name **and** printed number from the
record metadata (`collector_number`):
10/10 exact. Scores: Gligar 0.782, Chatot 0.851, Dugtrio 0.929,
Pyroar 0.939, Leavanny 0.927, Zarude 0.890, Scorbunny 0.891,
Wooloo 0.912, Minun 0.783, Sobble 0.926. Example record: Gligar top-1
metadata = collector_number 140/264, set "SWSH08: Fusion Strike".
Top-5 always contained the correct species; second-place scores were
typically 0.58 or lower, so the top-1 margin was large.

(b) Custom catalog, held-out second photos (identity IS in the catalog):
Yveltal 0.966 (next best 0.397), Switch 0.980 (next best 0.432),
Hop 0.938 (next best 0.389). **3/3 top-1 correct, with a margin of
0.51–0.55 over the runner-up.**
Same-photo sanity checks scored 0.998–0.999 — that is trivial
self-matching and is NOT counted as evidence.
A first, mis-designed custom catalog (10 cards only, held-out identities
not in it) correctly could not return Yveltal/Switch/Hop and scored
only 0.35–0.42 on wrong cards — that run is recorded here so nobody
repeats the design error: a held-out identity must be in the catalog.

(c) Fake front:
- Hosted catalog: top-1 "Charizard EX" (score 0.789), top-2
  "Charizard EX (12)". That is NOT a confident match to the card's
  claimed identity (Caterpie EX 12/108) — it is a match to the *art*.
  In a two-gate system (image identity vs printed name/number) this
  mismatch is itself a fake tell. In a single-gate image-only system
  it would mislabel the card as Charizard.
- Custom 13-card catalog: top-1 0.345 (wrong card, Yveltal) — the fake
  was NOT confidently matched.
- Genuine cards NOT in the custom catalog scored in between:
  Manectric 0.505, Diglett 0.573 (top hit Dugtrio). A threshold at
  ~0.75–0.80 would pass all three held-out true matches (0.94+),
  reject the fake (0.345) and reject the not-in-catalog genuine cards
  (0.51–0.57) on this small set. That threshold is a test observation,
  not an approved operating point, and n=3 held-out is far too small
  to approve one.

### Pass / fail
**PASS for the matcher step, on this evidence.** CollectorVision finds
the right name + number on 10/10 hosted-catalog fronts and 3/3 held-out
custom-catalog second photos, and does not confidently match the fake
in the custom catalog. It is the strongest fitting piece in the sweep.

### What it proves and does NOT prove
Proves: an embedding + nearest-neighbour matcher can name a card from a
hand photo on CPU, $0, without the user typing set + number first.
Does NOT prove: real vs fake (it matches art, not authenticity), a
grade, a verdict, or that it works on every set, finish, or lighting.
It does not work as-is on Penguin (needs ONNX Runtime, not stdlib).
AGPL blocks integration until the owner decides the licence question.

## Test 2 — Skewtle flatten + card-centering-studio formula — MIXED: flatten PASS, centering measurement NOT PROVEN

Licences: both MIT, method only. Neither whole app was shipped or run;
flattening was done with Pillow perspective using hand-placed corners
(the Skewtle method), measurement with the centering-studio formula
(left = inner_left − outer_left, etc., ratios as percentages).

### Method
5 angled owner fronts, corners placed by viewing each photo and
recorded in `test2_flatten.py` (fractions of image size), flattened to
630×882 (5:7) in `flat/`. A second flatten with every corner shifted
by +0.01 tested stability. Inner guides were then placed on the
flattened crops by eye (art-box / printed-area edges) and ratios
computed with the formula. Guide uncertainty is about ±0.01 in
fraction, i.e. about ±6 px on a ~45 px border, i.e. about ±5–7 ratio
points — larger than the differences being claimed between cards.

### Files used
Manectric 13/30 (`7966_110_r81y.jpg`), Diglett 076/198
(`27f76783-ce69-4b23-bc46-4ec1e69e544d_112_i8h2.jpg`),
Cottonee 075/185 (`9ae81b51-a3a0-430d-a37e-fa6f2f4cc610_141_b9bk.jpg`),
Bisharp 134/202 (`880ba15d-303a-4e31-8637-1473326de55e_143_aikw.jpg`),
Dialga 020/025 (`0a9cd687-7048-40e5-b7c9-95d233845043_145_5qzs.jpg`).
Flattened crops: `flat/<Name>_flat.jpg` and `flat/<Name>_flat_shift.jpg`.

### Numbers
Left/right (L/R) and top/bottom (T/B) ratios, larger side first:
- Manectric: L/R 50/50, T/B 33/67 — owner note for *this* front:
  centering unknown (the "centering off" note belongs to the flagged
  possible re-send, `7966_137_2d8m.jpg`, not this file). No
  contradiction, no confirmation. T/B is contaminated: the flatten
  corners included the phone watermark strip below the card, so the
  bottom border is overstated.
- Diglett: L/R 50/50, T/B 42/58 — owner gave no separate centering
  note for Diglett, only that it was in better condition than
  Manectric. No comparison possible.
- Cottonee: L/R 50/50, T/B 40/60 — owner: "off-centered".
- Bisharp: L/R 50/50, T/B 40/60 — owner: "off-center".
- Dialga: L/R 50/50, T/B 40/60 — owner: "off-center".

Stability: flat vs flat-shift mean absolute pixel difference
(0–255 scale) was 22.3–28.7 across the five cards. A 0.01 corner
shift moves the flattened image substantially, so guide placement
precision matters more than the ratio differences measured here.

### Pass / fail
**Flatten: PASS. Centering measurement vs owner notes: FAIL / NOT
PROVEN.** The flattened crops look square and the card fills the
frame, so the Skewtle method works as a flatten step. But L/R
measured 50/50 on all three cards the owner called off-center
(0/3 reproduced), and T/B measured 33–42/58–67 on every card,
including ones with no off-center note — a pattern that points to
a systematic bias in my top/bottom guide definition (header/footer
edges are not the inner border) rather than to five genuinely
off-center cards. Fronts only were measured; the owner notes may
have been about the backs, which were not measured in this test.

### What it proves and does NOT prove
Proves: angled hand photos can be flattened by hand into square
crops. Does NOT prove: a centering grade, a centering ceiling that
can be trusted to ±5 points, or that these five fronts are centred
or off-centre. Do NOT build a centering number into a grader from
this test. Next step for centering, if pursued, is a proper
inner-edge detector plus a calibrated guide protocol (art-box edges
only, or scan-only), tested against backs as well as fronts.

## Test 3 — ImageHash on cropped pairs + Tesseract OCR — HASH PASS, OCR BLOCKED

### Hash method
ImageHash (venv install) phash/dhash/ahash on CollectorVision
dewarped crops — true card-only crops, not centre-crop proxies.
Genuine: duplicate-identity second photos vs first photos (Yveltal,
Switch, Hop). Impostor: the 10 A1 dewarped crops pairwise (45 pairs).
Fake-nearest: each owner-confirmed fake front vs nearest of the
10 A1 refs. Raw results: `test3_hash_results.json`.
Licence note: ImageHash's licence file was not directly read in
this test either (sweep reported BSD-2-Clause from secondary
sources) — verify it before any use, same caveat as the sweep.

### Hash numbers (phash, 0–64, lower = more similar)
- Genuine same-identity, dewarped: **0, 2, 4** (Yveltal 0, Switch 2,
  Hop 4). Compare Oct 28 centre-crop phash: 10, 16, 16.
- Impostor, dewarped: n=45, min 20, median 28, max 38, mean 27.4.
  Compare Oct 28 centre-crop: median 30, min 18.
- Fake-nearest, dewarped: n=38 (3 of 41 fake fronts failed corner
  detection and were excluded, not counted as matches),
  min 20, median 26, max 32, mean 25.8. Compare Oct 28 centre-crop:
  median 22, min 16. Caterpie EX fake front: nearest phash 24
  (nearest ref Minun).
- dhash/ahash impostor medians on dewarped crops: dhash 27,
  ahash 25 (ahash min 8 — ahash alone is weaker, as expected).

**Separation improves on dewarped crops:** genuine ≤4, impostor
≥20, fake-nearest ≥20 in this test. A threshold at, say, ≤10 would
accept all 3 genuine and reject all 45 impostors and all 38 fakes
here. That is a test observation on n=3 genuine pairs only — it is
NOT an approved threshold, and it is NOT a same-identity fake test:
the fake fronts here are unrelated identities, not fakes of the
same identity as the genuine reference, which is the true
false-accept test and is still absent from the pool.

### OCR method and result: BLOCKED, no numbers invented
Tesseract OCR was not run. The binary is not installed in this VM
and `apt-get install tesseract-ocr` failed with "Unable to locate
package" even after an apt update (the VM's apt package lists do
not expose it in this environment). No OCR name/number counts
exist from this test, and none are claimed.
EasyOCR was NOT tested: the task allows it only if Tesseract
clearly fails on card fonts, and Tesseract failed on installation,
not on fonts. Installing a PyTorch OCR stack as a workaround would
be a different, heavy test needing its own approval.
**OCR pass/fail: NOT RUN — blocked on tool availability, not on
accuracy.** The OCR question (does it read most names/numbers
exactly?) remains open and needs a machine with Tesseract installed
(or a fresh owner decision to test EasyOCR).

### Hash pass / fail
**PASS as a shortlist tool, on dewarped crops.** Cropping first
is what makes the difference: the Oct 28 centre-crop genuine range
(10–16) overlapped the fake range, the dewarped range (0–4) does
not, on this small set.
**FAIL as a verdict tool, by design.** A hash distance is not an
identity, not a fake finding, and never a pass/fail on its own.
That rule stands unchanged.

## Not fit — not put in, as instructed
- pokepc/dataset: species data, not card data — not tested, not used.
- tradingcarddex/Pokemon-Card-CSV: duplicate identity source,
  attribution, unknown licence — not tested, not used.
- tcgdex/python-sdk: wrapper for data already held locally — not used.
- 1vcian/Pokemon-TCGP-Card-Scanner: Pocket screenshots, not physical
  cards — pattern only, already noted in the sweep, not tested here.
- dsouza95/pokemon-tcg-companion: unverified README/licence/method —
  no photos were sent to it, not tested.
- Any paid/closed AI grader: none evaluated, none used.
- No fake-tell engine was found in the sweep and none was invented
  here: font, print-dot, back-colour and spelling checks remain
  ours to build and test against verified pairs.

## Summary — what is ready to build into a playground prototype next, and what is not

Ready to build into a **playground prototype** (not the live demo,
not a verdict): CollectorVision as a test-only image-to-identity
matcher — hosted catalog for naming (10/10 exact name + number,
3/3 held-out second photos with a 0.51+ margin) and a custom catalog
built from the owner's own dewarped fronts (3/3 held-out, fake at
0.345, not-in-catalog genuine at 0.51–0.57) — behind the existing
two-gate rule (image identity first, tells second, Inconclusive on
disagreement), with the AGPL licence decision still open before
anything goes inside the app; plus ImageHash on dewarped crops as
a shortlist/similarity tool (genuine 0–4 vs impostor/fake ≥20 here),
with the crop step (CollectorVision dewarp, or the Skewtle manual
flatten) done before any hash is computed. Not ready: centering
measurement (flatten works, the number does not reproduce owner
notes and is too sensitive to guide placement), OCR (not run —
Tesseract unavailable in this VM), any fake-tell engine (none
found, still to be built from the owner's own tells and verified
pairs), and any final threshold (all separations here rest on
n=3 genuine pairs; the same-identity fake-vs-genuine test set
still does not exist). The next build step, in order, is a
playground prototype that dewarps, identifies with CollectorVision,
and shows the image-vs-printed-name/number comparison — with
every result labelled test-only and every disagreement landing on
Inconclusive — and a separate OCR run on a machine where Tesseract
actually installs.
