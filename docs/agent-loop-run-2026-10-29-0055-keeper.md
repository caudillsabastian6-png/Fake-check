# AI loop keeper run — Thu Oct 29, 2026 ~12:55–1:06 AM ET (owner-kicked)

Job: ai-loop-keeper (every 6h until Nov 4, 2026 9:00 PM ET; still in window).
Trigger: owner ordered all scans + eBay-era pictures worked through and
labelled, kicking the loop instead of waiting for the 3:16 AM run.
Mode: playground/local only, $0. No deploy, publish, post, send, train,
no Baseten / Meta Spark / SAM / Modal call. No verdict issued or forced.

## Worked: tonight-labelling queue steps 1–3 (set-fill) + step 4/5 prep

Workspace: `playground/tonight-labelling-2026-10-29/` (PROGRESS ledger
written by the main agent at 00:56; this run is its first batch).

Method (labelling guide Oct 28, auto-label rule Oct 28 ~10:36 PM): a set
is filled only from the card's own printed evidence + the local TCGdex
catalogue — owner-confirmed name + printed number (numerator AND the
printed denominator, which is the set's printed total), filtered to the
single catalogue row whose set official card count (TCGdex repo set
files) equals that denominator. Zero/multiple survivors = set stays
UNKNOWN. Partial labels per field; nothing guessed.

### Results
- Pool A incomplete-set pairs (103 A2 + 7 test + 8 re-shoot = 118):
  **115 SET_FILLED, 3 held** — `set_fill.py`, tests `test_set_fill.py`
  **12/12 PASS** (one parser bug found + fixed mid-run: Chilling Reign's
  set file carries a comment inside cardCount, 15 rows recovered).
  Pool A is now **181/184 identity-complete**.
- PENDING front-only hand photos (step 3, 168 incomplete-set of 539
  indexed / 370 in dataset): **156 SET_FILLED, 12 held** (9 name-vs-number
  conflicts, 1 no-match, 2 special-numbered SV cards unparsed). Their
  authenticity stays **UNKNOWN** and backs stay **MISSING** — identity
  completion only, no promotion to Pool A.
- Dataset copy `labelled_dataset_v3.csv` (original untouched):
  **complete 548/617** (was 277), incomplete-set 174→**18**,
  incomplete-identity **51** (47 fake fronts whose per-card names were
  never owner-verified + 4 Tier C — correctly NOT auto-filled).
- Held for owner/photo re-check (never corrected silently):
  GEN-093 Fletchinder 138/203 (that number is Fletchling in Evolving
  Skies), GEN-094 Fletchling 135/203 (that number is Stoutland),
  GEN-086 Galarian Sirfetch'd V (JP) 065/100 (JA detail index has no S4
  cards locally), plus the 12 PENDING holds listed in
  `set_fill_pending_results.csv`.
- Every filled row records `symbol_check=pending_visual` — the guide's
  set-symbol second pass is still owed before these count as
  symbol-verified.
- Signal for the calibration bottleneck (copies per identity): inside
  Pool A complete, 12 identities now have >1 pair (Cynthia sm5 119/156
  ×5; Professor's Research swsh1 ×2; Pokémon Fan Club sm5 ×2; 9 more ×2).
  Reported as copies-in-pool only — distinct-copy/median readiness is a
  separate verification, NOT claimed here.

### Step 4/5 prep (inventory, not labelling)
- Scans: `scan_inventory.csv` — **744 files** across 10 oct12-scan-batch
  folders (+1 subdir in batch12), every row source=scan, side/name/set/
  authenticity UNKNOWN, back MISSING, `inventory_only_unlabelled`. The
  page-by-page visual labelling pass has NOT been done; scans are NOT
  merged into phone-photo ground truth.
- Rename pilot: `rename_pilot_mapping.csv` — 206 proposed names for the
  103 A2 pairs (100 set-named, 6 files held UNKNOWN-SET for the 3 held
  pairs). **Mapping only — no copies made, no originals touched**;
  copies wait for the owner spot-check per the Oct 28 rename job.

## Cost / blocker for Sabastian
- Cost: $0. Blocker: none.
- Items for Sabastian (when he's ready, not urgent tonight): the 3 Pool A
  name/number conflicts (Fletchling/Fletchinder/Sirfetch'd) need a photo
  re-check; the set-symbol visual second pass on 271 filled rows;
  dataset approval remains a separate owner decision — nothing here
  trains a model or ships a verdict.
- Next keeper run: scan page-by-page visual labelling in capped batches
  (step 4), then rename-pilot copies after owner spot-check. Tier 5
  waves and Q59 SAM remainder still NOT started (separate owner yes).
