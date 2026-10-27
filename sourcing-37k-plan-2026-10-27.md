# Sourcing the rest: ~20,000 English + ~17,000 Japanese Pokémon cards
# Plan — research and inventory only — Oct 27, 2026

**Status: PLAN ONLY. No bulk download, no bulk scraping, no SAM spend, no publishing in this job.**
Owner order Oct 27, 00:38 ET: sourcing today did not get many photos; source the rest of the
~20,000+ English cards and ~17,000 Japanese cards.

**Standing use rule, Oct 27 ~12:38 AM ET (recorded in MEMORY.md):**
Sourced card images are **comparison data only, behind a mask / private comparison layer
that only the AI crew can access. NOT for sale, NOT for public display, NOT for
redistribution. Nobody will see them but the crew/AI; not even a real human will see
the data.** This narrows the use, it does **not** by itself clear a source's terms,
rate limits, or card-art copyright. Every source below still needs a per-source
terms check before any bulk run, and sourced images must never enter a public pool,
demo, listing, post, or marketing asset. That masked, comparison-only use is the
same framing already used for the Oct 22–23 reference database ("back-end matching
library, never redistributed, never used in listings or marketing").

**Standing SAM rule, repeated Oct 27 ~12:36 AM ET:**
SAM costs money every time it is used (~$0.0025/crop). Use SAM only if necessary.
The AI Loop / Tells work exists to learn from SAM and train off him, so that by the
time SAM has to go, the local system still knows everything SAM knew. This plan is
$0 local-crop first, SAM escalation only, unless a specific necessary SAM use gets a
fresh owner yes with cost logged.

---

## 1. What we already have — inventory, verified from files on disk

### 1a. Merged pool (the checker pool)

Source: `~/workspace/fake-check/pool-merged-2026-10-26.json` (346 KB, Oct 26, 2026)

| Pool | Count |
|---|---|
| Base distinct total | 8,484 |
| — real (genuine) in base | 7,173 |
| — fake in base | 1,311 |
| Hand-photo truly new, added Oct 26 | 174 |
| Hand-photo variants attached to existing entries | 283 (not new distinct cards) |
| **Merged distinct total** | **8,658** |
| **Merged real distinct, implied** | **7,347** (7,173 + 174) — see language caveat below |
| **Merged fake distinct** | **1,311** (fakes are NOT counted toward genuine sourcing) |

Real breakdown in base: 6,000 web-official fronts + 919 older owner scans + 250 genuine
owner scans + 4 others. Hand-photo source: 457 records, 539 representative files,
670 total source files including duplicates.

**Language caveat — this is the inventory's biggest hole, and it must be fixed first:**
The merged pool index does **not** carry a language field. It carries card name,
set_code (often null — 102 of the 174 new entries have set_code null), and number.
It therefore does **not** say how many of the 7,347 real cards are English vs
Japanese vs other. Any EN/JA split of the merged pool claimed today would be a guess.
Do not quote one.

The only per-set file on record is the starter checklist:
`~/workspace/fake-check/sourcing-checklist-2026-10-26.csv` — 166 rows, one per set,
covering **only the 6,000 demo-pool official fronts**, with `total_cards_in_set`
left as `TO_BE_FETCHED_FROM_SET_LIST` and missing left as `UNKNOWN`. Top counts
in that 6,000: Evolving Skies 108, SWSH Black Star Promos 108, Paldea Evolved 101,
151 (sv03.5) 100, Crown Zenith 98, Lost Origin 94, Brilliant Stars 90, Surging
Sparks 90, Base 86, Neo Genesis 86, then 156 more sets down to 2. Those are counts
in the 6,000, **not** coverage percentages.

Other pools on file, **not** counted toward genuine sourcing (to avoid double-counting):
- Fake pools, separate: FAKE-001…009 owner scans, anchor set, web set (web-01…11),
  fake-samples-2, fake-samples-3 (out-of-scope: MTG / One Piece / plush / slab scams),
  web-fake-corpus (302 files, 80 MB), web-fake-corpus-2 (174 files, 48 MB),
  web-fake-corpus-3 (937 files, 514 MB), web-fakes-pool (1,292 files, 167 MB),
  Oct 26 fake fronts batch (40 files, indices 324–363, provisional IDs only,
  fronts only, intake only, NOT SAM-cropped, NOT tells-scored).
- Second-photo lane: **0 admitted** from the first Track B search pass (Oct 26).
  Collection / scene photos found were not close-up references, and article photos
  had not had their Flickr licence verified. The 50-card second-photo pilot in
  `second-photo-sourcing-plan-2026-10-26.md` was proposed, **pilot yes NOT yet given**,
  and was not run. That is a large part of why "today did not get many photos":
  the admit-what-passes gate, correctly, admitted almost nothing, and the pilot
  was never authorised — it is not that a bulk run failed silently.

### 1b. Reference database — identity is largely solved, images are not

Source: `~/workspace/fake-check/reference-db/index-full.csv` (33,391 rows + header),
`index-full.json` (18 MB), `index-full-stats.json`, coverage report
`coverage-full-2026-10-23.md`. Built Oct 22–23, 2026, keyless, no sign-ups, no spend.
Raw per-set cache: `raw/` (36 MB), resumable offline.

| | Rows | Sets | With image URL (small = hires) |
|---|---|---|---|
| English | 20,610 | 176 / 176 | 20,455 — **99.2%** |
| Japanese | 12,781 | 116 with rows, of 184 sets pulled | 3,882 — **30.4%** |
| **Total** | **33,391** | — | **24,337 — 72.9%** |

Details that change the plan:
- English identity: complete. All 176 EN sets present. pokemontcg.io keyless pulled
  150 sets (15,968 rows) until a persistent HTTP 500 wall (keyless volume throttle);
  the puller was stopped deliberately rather than grinding into a ban. The exact
  26 blocked sets (Crown Zenith, SV base through Ascended Heroes, Mega Evolution
  sets) were filled from TCGdex EN (4,642 rows). Crown Zenith seam verified by hand:
  TCGdex `swsh12.5` = 160 main cards, pokemontcg.io `swsh12pt5gg` = 70 Galarian
  Gallery cards, no overlap.
- Japanese identity: partial. All 184 JA sets were pulled for metadata, but **68 sets
  are metadata-only in TCGdex itself** (set exists, official card count exists, but
  `cards: []` — verified three ways). Those 68 sets account for **4,889 official JA
  cards** with no card-level records in TCGdex. Pattern: pre-SM eras (ADV/PCG splits,
  LEGEND, most of XY), SM "+" subsets, a few S-era starter subsets. pokemontcg.io
  has no Japanese data, so this gap cannot be resumed away from TCGdex.
- Japanese image coverage by era: Japanese-modern rows 34.3% have image URLs
  (SV-era sets carry TCGdex assets; SM/S-era largely do not; M-era are identity-only),
  Japanese-vintage rows **0%**. English 99.2% by contrast.
- TCGdex states **15,196 official JA cards** across all 184 sets. The 12,781 JA rows
  exceed the remaining official count (15,196 − 4,889 = 10,307) because rows include
  secret rares / variants beyond official numbering (e.g. SV4a: 320 rows vs 190 official).
- Backs: every row names a back_design (english-modern 20,610; japanese-modern
  11,319; japanese-vintage 1,462), with Bulbagarden reference images for modern
  backs. Backs are **not** the front-image gap.

### 1c. The gap — three bases, stated, not merged into one fake number

Use the owner's working totals as the order's basis, and the verified reference
database as the check. Do not pick one as fact until variants are accounted for —
the Oct 26 checklist already warned of this exact discrepancy (TCGdex index count
21,256 EN / 12,781 JA unique cards vs another catalogue's 30,332 JA cards including
printings).

**Basis A — Owner working totals (the order's numbers): ~20,000 EN + ~17,000 JA = ~37,000**
- Total real distinct on file: 7,347
- **Total gap to owner totals: 37,000 − 7,347 = 29,653 cards** (before holo / reverse
  holo / secret rare / promo variants that change the front, which would raise it).
- English bound only (not a split): if *all* 7,347 real cards were English, EN gap
  would be 20,000 − 7,347 = **12,653**, and JA gap would be the full **17,000**.
  That bound is shown only to prove why the language join in §4, step 1 is mandatory:
  the true EN and JA gaps cannot be stated until the merged pool is joined to the
  reference database on (language, set, number, name).

**Basis B — Verified reference-database identity: 33,391 rows (20,610 EN + 12,781 JA)**
- Identity gap vs real pool: 33,391 − 7,347 = **26,044 identity rows not yet in the
  real checker pool** (before dedupe on variants, and before counting owner scans
  that may already match reference rows under a different set_code).
- Plus JA metadata-only official cards with no TCGdex records: **4,889** — a separate
  source gap, not a download gap.

**Basis C — Front images, which is the actual sourcing work**
- English front images: reference DB already holds image URLs for 20,455 of 20,610
  rows. The EN problem is **download + dedupe + verify**, not discovery.
  Against the 6,000 demo-pool official fronts alone, the EN front-image gap is
  20,610 − 6,000 = **14,610** (before overlap with the 919 + 250 owner scans, which
  must be deduped first — do not subtract them twice).
- Japanese front images: only 3,882 of 12,781 JA rows have an image URL in TCGdex.
  **JA image gap in TCGdex alone: 12,781 − 3,882 = 8,899 rows**, plus the 4,889
  metadata-only official cards = **~13,788 JA cards with no image via TCGdex alone**.
  Japanese images are the bottleneck of the whole 37k plan. English images are a
  download job; Japanese images are a sourcing job.

**What "today did not get many" actually means, in numbers:**
Second-photo lane admitted 0. Checklist starter covered 6,000 already-held fronts
and left totals UNKNOWN. No 37k bulk run was authorised or attempted on Oct 26.
The gap above is therefore a backlog, not a one-day shortfall to be made up by
hammering one source tonight.

---

## 2. Sources — Tier A/B only, bulk-allowed flagged honestly

Tier definitions carried over from `second-photo-sourcing-plan-2026-10-26.md` and
`sourcing-checklist-2026-10-26.md`:
- **Tier A first:** explicit permission / CC0 / CC-BY, author + source URL + licence
  recorded per card.
- **Tier B:** Flickr CC / Wikimedia / open datasets, terms checked per source.
  A photographer's CC licence does **not** clear the underlying Pokémon card-art
  copyright, so card-art use in a distributed app still needs a per-source check.
  Under the masked, comparison-only, crew/AI-only use in this plan, the use is
  narrower than public display — that helps the comparison argument, it does not
  create a bulk-download right.
- **Tier C — DO NOT scrape by default:** marketplace listing photos, social posts,
  forum photos. A seller's eBay photo is for that listing; a Reddit / Instagram
  post is not a reuse grant, even for comparison only. Excluded from this plan.

| # | Source | Tier | Covers | Bulk download? | Notes / limits on file |
|---|---|---|---|---|---|
| 1 | Pokémon TCG API — pokemontcg.io (`api.pokemontcg.io/v2/…`, images via `images.pokemontcg.io` / Scrydex CDN in the v1 tranche) | A (API) | EN identity + images, 176 sets on file | **API-paginated, NOT bulk-scrape.** Free key from dev portal raises limits vs keyless; keyless hit a persistent HTTP 500 wall after 150 sets on Oct 22. Respect rate limits, paginate 250/page, checkpoint per set, stop on throttle — do not grind into a ban. Image use is via the API's own image URLs; card art remains Pokémon / Nintendo / Creatures copyright. | Top pick for EN identity backbone in `reference-db-wiring-plan.md`. Already the source of 15,968 EN rows. |
| 2 | TCGdex (`api.tcgdex.net/v2/{lang}/…`, assets `assets.tcgdex.net`, `/low.png` / `/high.png` / `/high.webp`) | A (API, open-source) | EN + JA identity, JA bridge | **API-paginated, NOT bulk-scrape.** Free, no key, no auth. Database code is MIT-licensed — that licence covers the *database code*, not the card art, which TCGdex itself disclaims (not produced / endorsed / affiliated with Nintendo / The Pokémon Company; images are their property, used for informational / educational purposes). | Only clean keyless JP source in scope. Already the source of 4,642 EN fallback rows + all 12,781 JA rows. JA image gap (see §1c) is a gap *in* this source, not a pull failure. |
| 3 | Pokémon official card database / pokemon.com (identity verification only) | A (reference) | EN + JP set lists, card identity | **No bulk image download proposed.** Use to verify set totals, names, and numbers; do not scrape its images in bulk. | Verification source, not a bulk image source. |
| 4 | Bulbapedia / Serebii (identity + set-list verification; Serebii Simplified Chinese 151 pattern already used on file for a different set) | B (reference) | Set lists, printed numbers, rarity | **No bulk image download proposed.** Single-card verification pages only, as already done on file. | Do not bulk-scrape wiki images. |
| 5 | Limitless TCG card database | B (reference / identity) | EN identity, HGSS and newer for card search | **No bulk image download proposed in this plan.** No public developer API documented on file; its card pages are a verification surface, not a bulk source. | Listed in the wiring plan as a corroboration surface, not a bulk image source. Flagged here so it is not mistaken for one. |
| 6 | Pokellector (set / image-URL resolution, already in wiring plan Stage B) | B (reference) | Image-URL resolution for sets already in the reference DB | **Per-set resolution only, as in the wiring plan.** Do not bulk-scrape. | Corroboration, not a new bulk lane. |
| 7 | Flickr Creative Commons / Wikimedia Commons / openly licensed datasets (Track B real-world photos only) | B, per-photo | Real-world phone photos for tells (texture / holo / print), NOT official renders | **Per-photo, admit-what-passes only.** Licence, author, source URL recorded per card. A CC photo licence does not clear card-art copyright; app-only comparison, never sold, never marketed, SAM card-only crop, strip hands / faces / backgrounds. | First Track B pass admitted **0**. That gate stays. A second official render is *not* a real-world second photo — do not count it as one. |
| 8 | Owner / family-tester phone photos (phone-stand intake, Oct 27 plan) | A (owned) | Real-world photos of cards he / family actually own, front + back | **Owner-controlled, batch intake only.** Batches of 50, WiFi only, per the Oct 27 phone-stand plan. | The only Tier A real-world source that also teaches texture / holo by era. Cannot cover cards he does not own — that is exactly why §2 sources 1–2 are needed for identity / official fronts. |
| — | Marketplace (eBay, etc.), social (Reddit / Instagram / TikTok), forums | **C — excluded** | — | **No.** | Excluded by default in both Oct 26 plans. Any single exception needs a fresh owner yes naming the source, the card, and the licence/permission — never a bulk exception. |
| — | Paid / keyed third-party card APIs (e.g. pokemonpricetracker-style, tcgapi.dev-style services found in web search) | **Not proposed** | — | **No, without owner approval + terms read.** | Web search surfaced several; their terms include anti-bulk-download / anti-competing-dataset clauses and paid plans. Do not subscribe, do not use a key, do not bulk-pull from them in this plan. If the owner wants one evaluated, that is a separate terms-read job. |

**Japanese-specific source problem, stated plainly:**
No Tier A/B source on file closes the JA image gap. TCGdex JA gives identity for
12,781 rows and images for 3,882, and nothing for the 68 metadata-only sets.
Closing JA images needs one of: (a) a new Tier A/B JP image source approved after
a terms read, (b) owner / family photos of JP cards he owns, or (c) accepting that
JA front-image comparison stays partial and the checker says so honestly for JA
cards without a reference image. Option (c) is the default until (a) or (b) is
approved — do not fill JA images by scraping official art from mirrors.

---

## 3. Scale plan — storage, SAM cost, time, dedupe

### 3a. Storage — use the documented on-file rate, not a guess

On-file rate: first official set ≈ **4.8 GB for 6,000 images = ~0.80 MB per image**
(`second-photo-sourcing-plan-2026-10-26.md`). Cross-check: web-fakes-pool
167 MB / 1,292 files ≈ 0.13 MB per file (smaller, web-compressed files), so the
0.80 MB rate is the hires / official-render end, and a low-res end is ~0.13–0.20 MB.

| Scope | At 0.80 MB/image (hires) | At 0.20 MB/image (low) |
|---|---|---|
| Owner-total gap, 29,653 cards, 1 front each | **~23.7 GB** | **~5.9 GB** |
| Full owner universe, 37,000 cards, 1 front each | **~29.6 GB** | **~7.4 GB** |
| Reference-DB identity, 33,391 rows, 1 front each | **~26.7 GB** | **~6.7 GB** |
| JA image gap alone, ~13,788 cards, 1 front each | **~11.0 GB** | **~2.8 GB** |
| Second photo (real-world) for all 8,658 merged cards, 1 each | **~6.9 GB** | **~1.7 GB** |

Crops: a SAM / local card-only crop (e.g. 565×797 PNG in the Oct 26 loop run) is
roughly 0.2–0.4 MB as PNG. Budget **+7–15 GB** if a crop is kept for every one of
the 37,000, **+~3 GB** if crops are kept only for the 8,658 merged pool.
Planning total, hires fronts + crops, worst case: **~40–45 GB**; realistic
mixed low/hires: **~15–25 GB**. That fits the Seagate (1.8 TB, label Cauldron)
and the SSD (238.5 GB) easily, and it does **not** belong in the Muse workspace.
Storage location is a blocker decision (§5): Seagate first, SSD second, workspace
never for the bulk set.

Fronts and backs are separate databases (owner decision Oct 26, 11 PM ET).
Backs are **not** included in the numbers above. A back per card would roughly
double front storage. Do not add backs to the 37k front plan without a separate
back-sourcing decision — fake backs in particular must still be sourced under
the standing rule (never file a genuine back as a fake back, never file an
owner-printed help-text back as a fake-back example).

### 3b. SAM cost — $0 first, SAM only where it earns its cost

Rate on file: **~$0.0025 per SAM crop**.

| Scope, if SAM cropped every card | Cost |
|---|---|
| Owner-total gap, 29,653 | **$74.13** |
| Full owner universe, 37,000 | **$92.50** |
| Reference-DB identity, 33,391 | **$83.48** |
| Second photo for all 8,658 merged cards | **$21.65** (already in the Oct 26 plan) |
| Pilot, 50 cards | **$0.13** if SAM cropped — but pilot step 1 is search+identify only, **$0** |

**Plan rule (SAM-only-if-necessary):** $0 local crop first (Pillow / on-device
crop v2, with the aspect gate from the Oct 27 App V2 merge — reject any on-device
box whose aspect differs from the reference aspect by >0.15, stay Inconclusive,
do not let a bad crop produce a false Counterfeit). SAM only on: invalid box,
low confidence, or an explicit Real check where the owner has approved SAM for
that card. If, say, 10% of the gap needs SAM, cost is **~$7.41** for the gap;
at 20%, **~$14.83**. Any SAM batch needs a fresh owner yes naming the batch size
and the cost cap before it runs, and every SAM call is logged (the Baseten-style
usage-tracker discipline, applied to SAM: date, card, cost, result).
No SAM spend is authorised by this plan. The learning goal is the point:
every SAM box that *is* used must be recorded as a local rule (box shape,
aspect, failure mode) so the local cropper needs SAM less next time.

### 3c. Time / bandwidth — polite, resumable, set-by-set, not one hammer run

Assumptions, stated: ~0.80 MB hires image, polite API pacing, single-threaded
unless a source's terms allow more, checkpoint after every set.

| Pace | 37,000 images | 29,653 gap images |
|---|---|---|
| 2 sec / image (polite, with verification) | ~20.5 hours elapsed | ~16.5 hours |
| 1 sec / image | ~10.3 hours | ~8.2 hours |
| 0.5 sec / image (only if terms + throttle allow) | ~5.1 hours | ~4.1 hours |
| Download alone, 10 Mbps effective, 0.80 MB/image | ~6.6 hours for 37,000 | ~5.3 hours for the gap |

Reality check from Oct 22–23: pokemontcg.io keyless throttled to persistent
500s after 150 sets, and the JP pull hit two silent worker deaths and a set-detail
404 crash before finishing under tmux with per-set checkpoints. A 37k run must
therefore be: **set-by-set, resumable from the per-set cache, with a per-set
failure guard, and a hard stop on throttle** (stop, log, resume later — never
grind into a ban). Budget in **days of background runs, not one overnight run**,
and budget verification time on top of download time: identity check (set +
number vs set list, name beats label, number beats rarity guess) is what makes
a downloaded image a reference, not the download itself.

### 3d. Dedupe — do not re-download what we already have

Join key, in order: **(language, api_set_id / set_code, number, name)**.
Reference-DB primary key is (language, id); cross-source matching uses
(language, api_set_id, number, name). Crown Zenith is split across sources —
match on number within the CRZ family, not on source.

Dedupe steps, in order:
1. Join the merged pool (8,658) to the reference DB (33,391 rows) on that key.
   This both (a) produces the missing EN/JA split of the merged pool, and
   (b) produces the true per-set missing list. Until step 1 is done, per-set
   missing counts stay UNKNOWN.
2. Dedupe the 6,000 demo-pool fronts, the 919 older owner scans, and the 250
   genuine scans against each other and against the reference DB — a scan that
   matches a reference row is a variant image for that row, not a new distinct card.
3. Dedupe hand-photo variants (283 attached, 539 representative files) the same way.
4. Exclude all fake pools from genuine dedupe. Fakes dedupe only against fakes
   (fronts vs fronts, backs vs backs).
5. Only then generate the download list: reference rows with no merged-pool match
   and no image on file, ordered by set, language EN first (images available),
   then JA sets with images, then JA sets without images (flagged as source-gap,
   not download-ready).
6. Verify each downloaded image: HTTP 200 + real image bytes + dimensions +
   identity (set + number) before it counts. A 0-byte or wrong-card file is not
   coverage, and must not be counted — the Oct 26–27 SSD backup lesson (843
   0-byte files behind an `ALL_DONE` log) applies here too: **never trust a
   completion log without a count + bytes + content check.**

---

## 4. Pilot first — 50 cards, search + identify only, no spend

Carried over from `second-photo-sourcing-plan-2026-10-26.md`, extended to the
37k universe. Pilot yes is **still not given** — this section is a proposal,
not an authorised run.

**Pilot scope (proposed):**
- 50 cards, search + identify only, **$0** in step 1 (no SAM, no API spend beyond
  keyless set-list reads already on file).
- Suggested start, for checkability: Base set cards already in the 6,000 official
  pool, including Alakazam Base / BS 1 (the loop test card), plus 10 JA cards
  from a JA set that *does* have TCGdex images (SV-era) and 10 JA cards from a
  JA set that does *not* (to measure the JA image gap honestly, not just the
  easy half).
- For each pilot card, record: language, set, number, name, official URL,
  second-photo URL if any, source, licence / terms note, why it passed / failed,
  and whether it is a real-world photo or just a second official render.
- Also record: whether the merged-pool join (step 1 in §3d) already covers it,
  and whether a $0 local crop would succeed on it (aspect gate pass / fail).

**Pilot report (required before any bulk run):**
Hit rate (admitted / 50), EN vs JA hit rate separately, JA image-availability
rate, local-crop success rate, and a sample sheet of 5 admitted + 5 rejected
with reasons. Scaling decision is **owner-only after pilot numbers are real**.
If pilot hit rate is, say, 20% for second real-world photos, expect ~1,700
second photos for the 8,658 merged pool, not 8,658 — and plan tells work around
a few clean examples per era / set / pattern, not thousands of unverified
duplicates. Admit-what-passes, not bulk-or-nothing.

**Pilot is not the 37k run.** The 37k run is the download + dedupe + verify
pipeline in §3d, run set-by-set after the pilot, after the blockers in §5 are
cleared. Do not start the 37k run on the strength of this plan alone.

---

## 5. Blockers — owner approval needed before any bulk sourcing starts

1. **Source approval, per source:** pokemontcg.io with a free API key (owner
   creates the key, it is never pasted in chat / files) vs keyless-only;
   TCGdex as the JA bridge; and a decision on the JA image gap (§2) — new
   Tier A/B JP image source, owner/family JP photos, or accept partial JA
   comparison. No bulk run until the source list in §2 is approved as written.
2. **Storage location:** Seagate (Cauldron, 1.8 TB) first, SSD second,
   workspace never for the bulk set. Confirm the Seagate backup state first —
   the Oct 26–27 SSD→Seagate re-copy was still in flight at last check, and
   no installer write is to happen until both backup gates pass. Do not mix
   the sourcing download into an unverified backup.
3. **SAM budget:** $0 local-crop first is the plan. Any SAM batch needs a fresh
   yes naming batch size + cost cap (see §3b). No SAM batch is authorised here.
4. **Language join first:** run §3d step 1 (merged pool ↔ reference DB join)
   and publish the true EN/JA split + per-set missing list before any download
   list is generated. Until then, EN/JA gaps stay as bounds in §1c, not as
   download targets.
5. **Masked comparison-only handling:** sourced images go only to the masked,
   crew/AI-only comparison layer, never to a public pool, demo, listing, post,
   or marketing asset, and never merged with owner scans or claimed as ours.
   Provenance (source, URL, licence / terms note, date) is recorded per card
   even though the image itself is not publicly shown.
6. **Pilot yes:** 50-card pilot (§4) needs an explicit yes for its scope
   (Base + SV-era JA + non-image JA) before it starts. Bulk scaling needs a
   second, separate yes after the pilot report.
7. **Rate-limit / throttle stop rule:** any source that returns persistent
   500s / throttling stops the run for that source, logs it, and resumes only
   on a fresh decision — never hammered, never circumvented with extra keys
   or accounts.

---

## 6. What this plan does NOT do

- It does not download, scrape, or publish anything. It is inventory + research.
- It does not claim the merged pool's EN/JA split, per-set completeness, or
  JA image coverage beyond what the files above prove.
- It does not count fakes toward genuine coverage, shelf-staging duplicates
  toward any count, or a second official render toward a real-world second photo.
- It does not authorise a Play publish, a public demo update, a listing, a post,
  a purchase, or a SAM batch. Each of those needs its own exact yes.
- It does not resolve the Oct 26–27 backup / installer gates. Those are separate,
  and sourcing downloads must not interfere with them.

---

## Sources on file used for this plan

- `~/workspace/fake-check/pool-merged-2026-10-26.json`
- `~/workspace/fake-check/sourcing-checklist-2026-10-26.md` + `.csv` (166 sets, 6,000)
- `~/workspace/fake-check/second-photo-sourcing-plan-2026-10-26.md`
- `~/workspace/fake-check/reference-db/index-full.csv` / `index-full-stats.json` /
  `coverage-full-2026-10-23.md` / `reference-db-wiring-plan.md`
- `~/workspace/fake-check/databases/README.md` (fronts / backs separation)
- Standing rules Oct 27, 2026: SAM-only-if-necessary (~$0.0025/crop); sourced
  images comparison-only, masked, crew/AI-only, never for sale / public display /
  redistribution.

---

## Addendum A — Owner clarification, Oct 27 00:38 ET: masked, AI-only, comparison-only use

**This addendum was added at the owner's direction after the first version of this plan.
It does not authorise any download, scrape, or SAM spend. It states the intended use
that every source in §§2 and 7 must be assessed against.**

Sourced card images are:
- **NOT for sale.**
- **NOT for public display.**
- **NOT for redistribution.**
- **Comparison data only.**
- **Nobody will see them but the crew/AI — actually, not even a real human will see
  the data.** They will be locked behind a mask / private comparison layer that
  only the AI crew can access.

What that means in practice, and what it does not mean:

**Storage — private, masked, AI-only access:**
- Store the raw sourced set in a private location only — Seagate first (see §5.2),
  never in the Muse workspace, never in a public pool, demo, artifact, or shared folder.
- Access control: AI crew processes only, through the comparison layer. No human
  browsing of the raw sourced set, no human gallery, no screenshots of raw sourced
  images for review, no forwarding of raw sourced images in chat, email, or posts.
- What a human *may* see, and only through the comparison layer, is the checker's
  output for a card they submitted (a verdict / tells summary / their own photo),
  never the raw reference set itself. If a review step would require a human to
  open the raw set, that step is redesigned or it does not happen — the mask is
  not lifted for convenience.
- Provenance is still recorded per card (source, source URL, licence / terms note,
  date, language, set, number, name) even though the image itself is not publicly
  shown. Provenance metadata is the audit trail; it is not a public display of
  the image.
- No public pool: sourced images must never be merged into `demo-pool.json`,
  never shipped in app assets, never used in a listing, store page, social post,
  video, or marketing asset, and never claimed as owner scans. The firewall in
  the Oct 26 second-photo plan (app-only comparison, never sold, never marketed)
  is extended here to: **never seen by a human outside the crew, and never seen
  raw by anyone at all.**

**How this affects a source assessment — and how it does not:**
- It *narrows* the use, which strengthens a comparison-only argument for a source
  that already permits API / reference use: the image is not being republished,
  resold, or displayed to the public, and no human is browsing a gallery of it.
- It does **not** override a source's terms, robots file, rate limit, API licence,
  or card-art copyright. If a source says "no bulk download", "no scraping",
  "no systematic download", or "no reuse without permission", the masked use does
  not turn that into a yes. The source is still flagged NO in §7, and still needs
  a per-site owner approval naming that site before any fallback run.
- It does **not** clear a photographer's copyright in a real-world photo, or
  Pokémon / Nintendo / Creatures copyright in card art. A CC licence on a photo
  still does not clear the underlying card art, and a fan site's compilation
  copyright is still that site's.
- It does **not** make a blocked or throttled source fair game. A 403, 429, 500
  throttle wall, bot check, or account ban is a hard stop for that source in
  this plan, not a prompt to route around it.
- In short: masked, AI-only, comparison-only is the *intended use to assess
  against*, not a licence. Every source below is still assessed on its own terms.

---

## Addendum B — Scraping fallback, RESEARCH ONLY, Oct 27 00:38 ET

**Owner update: website scraping for photos may become our only option because
sourcing is getting hard. This section is research only. NO scraping was started
in this job. NO bulk scraping is authorised by this section. Tier A/B first;
scraping is a clearly-marked fallback, with per-site owner approval required.**

### B1. When the fallback is even reached

The fallback is reached only if, in order, all of these have failed or been
exhausted for a given set / language:
1. Tier A API download (pokemontcg.io for EN, TCGdex for EN + JA) — paginated,
   checkpointed, throttle-respecting.
2. Owner / family-tester photos for cards actually owned.
3. Tier B per-photo admission (Flickr CC / Wikimedia / open datasets, per-photo
   licence + identity check).
4. The 50-card pilot (§4) has reported, and the pilot hit rate shows the Tier A/B
   route cannot close that set / language.

Scraping is then considered **per set, per site, per owner approval** — never as
a blanket "scrape everything" authorisation, and never as a first resort because
it is faster. If Tier A/B closes a set, the fallback for that set is closed too.

### B2. Hard rules for any fallback run (if ever approved)

- **Per-site owner yes, naming the site, the sets, and the image count cap.**
  A yes to "scraping" in general is not a yes to any particular site.
- **No bypassing a block.** 403, 429, bot check, CAPTCHA, IP ban, login wall,
  or robots disallow = stop for that site, log it, report it. No header spoofing,
  no rotating IPs / accounts, no headless-browser evasion to get around a block
  the site put up. The Oct 22–23 lesson applies: a persistent 500 wall meant
  *stop*, not *grind*.
- **No marketplace / social by default.** eBay, Facebook Marketplace, Reddit,
  Instagram, TikTok, Discord, and forums are Tier C and stay excluded unless
  a separate owner yes names that exact site *and* the permission / licence
  basis for that site's photos. See §B3 for why those are the hardest cases.
- **Rate limits to respect, minimum:** at most 1 request per 2 seconds per site
  unless the site publishes a stricter limit (then the stricter limit wins);
  stop on first 429 / 500 throttle; set-by-set, resumable, checkpointed;
  identify with a honest user-agent and a contact / project identifier if the
  site asks for one; never run two scrapers against the same site at once.
- **Provenance per image, mandatory, or the image is discarded:** source site,
  full source page URL, image URL as served, date fetched, language, set,
  printed number, card name as verified against the set list, licence / terms
  note for that site, and the masked-use flag (§A). An image without provenance
  is not coverage, even if it looks right.
- **Masked use only (§A):** any scraped image goes straight into the private,
  masked, AI-only comparison layer, never to a public pool, demo, listing,
  post, or human gallery. If a site's terms forbid even private copying, the
  masked use does not override that — the site stays NO.
- **Verification before counting:** HTTP 200 + real image bytes + dimensions +
  identity (set + number vs set list) + dedupe against the merged pool and
  reference DB (§3d). A 0-byte, wrong-card, or duplicate file is not coverage.
- **Takedown / removal:** if a source, photographer, or rights holder asks for
  removal, that image (and its crop) is removed from the masked set and the
  provenance record is marked removed, with the date. No argument about
  masked use is used to keep it.

### B3. Candidate sites — terms / robots / rate limits / provenance / masked-use effect

**Important limit on this table:** robots files and full terms pages were not
fetched as live browser visits in this research job, and a site's robots file
can change. "Not verified in this job" means exactly that — the fallback run
for that site must re-read its current terms and robots file at run time, and
if they forbid the run, the run does not happen. Do not treat this table as a
permission.

| Site / route | Bulk image download allowed? | Rate limit to respect | Provenance per image | How masked, AI-only, comparison-only use affects the assessment |
|---|---|---|---|---|
| **pokemontcg.io API + image CDN** (Tier A route, not scraping) | **API use: yes, paginated.** Bulk scraping of the website / CDN outside the API: **no — use the API.** | Official docs: keyless 1,000 requests/day, max 30/min; with a free API key 20,000/day by default (higher on request). Third-party guides cite lower hourly figures — the docs figure wins. Respect 429 (Too Many Requests) as a stop. | API card id, set id, number, name, image small/large URLs, date fetched. | Masked use fits the API's developer purpose best of any route here, because the image is not republished. It does not raise the rate limit or permit CDN scraping outside the API. |
| **TCGdex API + assets.tcgdex.net** (Tier A route, not scraping) | **API use: yes, paginated.** Bulk scraping outside the API: **no — use the API.** Database code is MIT; card art is not. | No key, no published per-day figure on file. Use the same polite floor as §B2 (≥2 sec/request, stop on 429/500), and stop on throttle. | TCGdex card id, language, set id, number, name, `/low.png` / `/high.png` URL, date fetched. | Masked use narrows the use, but TCGdex's own disclaimer (not affiliated with Pokémon / Nintendo; images are their property) means the art copyright question is unchanged. Masked use does not make TCGdex art freely redistributable — and this plan never redistributes it. |
| **Pokémon official card database / pokemon.com** | **No bulk download proposed.** Identity verification only. | Polite single-card verification only; no bulk pace is proposed because no bulk run is proposed. | Set, number, name as shown on the official page, date checked. | Masked use does not create a bulk-download right from an official site that does not offer one. Verification-only stays verification-only. |
| **Serebii.net (card pages / image script)** | **No bulk download established.** Serebii content is stated © Serebii.net, with Pokémon names/details © Nintendo. No bulk-download grant found in this research. A fan site that has itself received Nintendo copyright notices for images is a poor bulk source to rely on. | No bulk pace — do not bulk-run. Single-card verification pages only, as already done on file for Simplified Chinese 151 (verify each image against its card page, page title gives the card name). | Card page URL, image URL, date checked, set/number verified against the page title. | Masked use helps the *use* argument (no public display), but it does not override Serebii's copyright notice or Nintendo's art copyright, and it does not turn a verification page into a bulk source. **Fallback status: verification only, unless the owner gets explicit permission from Serebii — not assumed.** |
| **Bulbapedia / Bulbagarden Archives** | **No bulk download established for card images.** Original Bulbapedia text is CC-BY-NC-SA 2.5, but card images are copyrighted material allowed on Bulbapedia only under fair use / permission / open licence / public domain / own creation, per its own image-licensing page. That page's licence does not transfer to a bulk re-copy. | No bulk pace — do not bulk-run. Single-image verification only, with the Archives licensing tag checked per image. | Archives file page URL, licensing tag as shown, date checked, set/number verified. | Masked, non-commercial, AI-only comparison is *closer* to the fair-use factors Bulbapedia itself cites (purpose, amount, market) than public display would be, but fair use is per-image and per-use, not a bulk grant. **Fallback status: per-image only, with the licensing tag recorded; bulk copy is NOT cleared by this table.** |
| **Limitless TCG card database** | **No bulk download established.** No public developer API documented on file. Card search covers HGSS and newer for the main database. | No bulk pace — do not bulk-run. Single-card verification only. | Card page URL, set, number, name, date checked. | Masked use does not create an API or a bulk right where none is offered. Verification only. |
| **Pokellector** | **No bulk download established in this plan.** Per-set image-URL resolution only, as in the wiring plan. | Per-set resolution pace only, polite, stop on throttle. | Set, number, resolved image URL, date checked. | Masked use does not expand a resolution step into a bulk scrape. |
| **Flickr / Wikimedia Commons (CC photos, Track B only)** | **Per-photo only, never bulk.** Licence must be CC0 / CC-BY (or CC-BY-SA where compatible) *for that photo*, checked per photo. | Per-photo, polite, respect each site's API / download limits if an API is used. | Photographer, photo page URL, licence as shown, date checked, identity (set + number) verified, SAM / local card-only crop record. | Masked use helps (no public display, no sale), but a CC photo licence still does not clear the underlying card art. Per-photo assessment stays per-photo. |
| **eBay / Facebook Marketplace (Tier C)** | **NO by default.** eBay's own image/text policy (found in search): use only images you create yourself or from the eBay product catalogue — do not use photos or text from other eBay users or websites. Its IP policy prohibits using third-party photos without permission, and picture theft can lead to listing cancellation / account action. Marketplace terms do not grant third-party reuse. | **No bulk pace — no run.** | Would require: seller, listing URL, seller permission in writing, date — which is why this route is not a bulk route at all. | Masked, AI-only, non-public use **does not override** eBay's policy or a seller's photo copyright. A masked copy is still a copy. **Fallback status: excluded unless a separate owner yes names eBay / a specific marketplace AND a permission basis is documented for that site's photos. That yes has not been given.** |
| **Reddit / Instagram / TikTok / forums / Discord (Tier C, social)** | **NO by default.** A post is not a reuse grant, even for comparison only (Oct 26 plan). Platform terms and the poster's photo copyright both apply. | **No bulk pace — no run.** | Would require: poster, post URL, poster permission in writing, date. | Masked use does not turn a social post into a licensed reference. Same exclusion as eBay: separate owner yes naming the exact site + permission basis required, and that yes has not been given. |
| **Hugging Face openly licensed datasets** | **Per-dataset only.** Dataset licence + Pokémon copyright note must be read before any card is taken from it (Oct 26 plan). A dataset that states a CC licence for its *compilation* does not automatically clear card art. | Per-dataset, respect the dataset's own terms and download limits. | Dataset name, dataset licence, card source within the dataset, date checked. | Masked use narrows the use, but the dataset's licence must still be read and recorded per dataset. No bulk ingest from an unread dataset. |

### B4. What the fallback does NOT change

- Tier A/B order does not change. Scraping does not jump the queue because it is
  faster, and it does not replace the pilot (§4) or the language join (§3d step 1).
- The 50-card pilot is still the first step, and it is still $0 search + identify
  only. A scraping fallback run is a *later* step, after the pilot report, after
  Tier A/B exhaustion for that set, and after a per-site owner yes.
- No site in §B3 is authorised by this addendum. Every fallback row that says
  "no bulk download established" or "NO by default" stays NO until a fresh,
  site-named owner yes + a current terms/robots re-read change it — and even
  then, only for the sets and count cap named in that yes.
- If scraping becomes the only option for a set (most likely: Japanese sets
  with no TCGdex image and no metadata record), the honest alternative remains
  on the table: accept partial JA comparison and say so for those cards, rather
  than scraping a source that forbids it. "Only option" is a description of
  difficulty, not a permission.
