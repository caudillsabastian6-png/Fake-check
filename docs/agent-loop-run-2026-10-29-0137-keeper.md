# AI loop keeper run — Thu Oct 29, 2026 ~1:37–1:50 AM ET

Job: ai-loop-keeper (every 6h until Nov 4, 2026 9:00 PM ET; still in window).
Trigger: labelling night watchdog 01:36 ET kick — step 4 scan batch 3
(batch4) next in queue order, after batch 2 (19/23, batch12 gap closed).
Mode: playground/local only, $0. No deploy, publish, post, send, train,
no Baseten / Meta Spark / SAM / Modal call. No verdict issued or forced.

## Worked: tonight-labelling step 4 — scan visual labelling, batch 3

Batch: `oct12-scan-batch4`, 74 files (37 fronts + 37 back-named).
Method: same as batches 1–2 — labelled contact sheets built first
(`tonight-labelling-2026-10-29/scan-batch3-contact/`, fronts-1..7,
backs-1..4), every front read visually, disputed numbers re-read from
zoom crops (8 front zooms). A front is labelled only when the visual
read AGREES with the filename; set filled by the set_fill catalogue
method only on exactly one survivor. Script: `scan_label_batch3.py`;
output: `scan_labels_batch3.csv`.

### Fronts (37)
- **29 fronts labelled** (`labelled_visual_filename_match`, set filled,
  symbol_check=pending_visual). Includes promos Glaceon GX SM147
  (SM Black Star Promos) and Venusaur V SWSH100 (SWSH Black Star
  Promos), and Bulbasaur 1/18 (Detective Pikachu). Two labelled fronts
  carry the filename abbreviation 'cec' while their unique catalogue
  survivor is Unified Minds (Dedenne 145/236, Dragonair 150/236) —
  filled by the printed-number rule, abbreviation mismatch noted here.
- **7 fronts HELD — filename conflicts, printed value zoom-verified,
  never corrected:** Bewear file 132/264 prints **151/264**; Dhelmise
  file bst-59/163 prints **59/145**; Hoppip file fus-20/264 prints
  **002/203**; Nickit file viv-121/185 prints **112/189**; Noibat file
  evs-132/203 prints **158/236**; Rattata file evs-143/203 prints
  **143/214**; Woobat file evs-073/203 prints **073/185**.
- **1 front HELD — catalogue gap:** Pikipek 142/185 (visual == filename)
  has 0 EN detail-index survivors at total 185; set stays UNKNOWN.
  Same failure class as Scorbunny 026/163 (batch 1) and Lunala GX
  SM103a (batch 2).
- Authenticity stays **UNKNOWN** for all 74 (SCAN set only, never
  merged into the phone-photo ground truth).

### BATCH ANOMALY — batch4 has no card backs at all
- Unlike batch 1 (true standard backs), **all 37 `-back.jpg` files in
  batch4 are a different card's FRONT** — verified on every file via
  backs-1..4 sheets + zoom crops (`zoomback-*`, `zoombacks2-1..5`).
  Example: `alolan-grimer-cec-130236-back.jpg` shows a Ledian 005/198
  front. Each back-named file is recorded in the CSV as
  `held_back_file_is_different_front` with the front it actually shows
  (visual name + printed number; Skarmory 26/107, Mareep 38/114 and
  Pancham 60/111 carry their numbers bottom-right, read from the backs
  sheets; the other 34 are zoom-verified).
- **No stem pairing was made.** Every labelled front in this batch is
  front-only, back MISSING — no true back image exists in batch4.
  The batch-1 pairing rule must NOT be applied blindly to later
  batches; each batch's back-named files need a visual check first.

### Scan totals after this run
- **104 files labelled** (75 prior + 29), **63 held** (18 prior + 45:
  7 conflicts + 1 catalogue gap + 37 misnamed back files),
  **771 still inventory-only** of 938 total scan files.

## Cost / blocker for Sabastian
- Cost: $0. Blocker: none.
- For Sabastian (not urgent): batch4's "back" scans are actually
  fronts of other cards — the Oct 12 scan naming broke down for this
  batch, so these 37 cards have no back image and 37 extra fronts are
  sitting in back-named files (full list in `scan_labels_batch3.csv`).
  Plus 7 more filename number errors caught by the visual pass.
- Next keeper run: scan visual labelling batch 4 (`oct12-scan-batch5`,
  same contact-sheet method, WITH a visual check of its back-named
  files before any pairing); step 5 rename copies still wait for the
  owner spot-check of the pilot mapping; step 6 (online-sourced
  photos) stays behind the scan batches tonight.
