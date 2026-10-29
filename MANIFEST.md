# GitHub pack — MANIFEST
Refreshed Oct 28, 2026, for the daily GitHub push (owner-approved Oct 27, 2026,
daily through Nov 4, 2026 only) to the existing public repo
github.com/caudillsabastian6-png/Fake-check.

Last known public push (separate clone, not this workspace): Oct 27, 2026 ~1:14 AM ET,
commit 2ba7bc49, 46 files, under different paths (playground/app-v2-merged/, etc.).
This pack's paths (checker/, demo/, data/, docs/, tests/) were verified absent from
that remote head on Oct 28, 2026, so pushing this pack ADDS these paths; it does not
overwrite the remote root README.md (no root README.md is in this pack).
There is currently NO git repo in ~/workspace/fake-check/;
this pack is a staging folder, not a commit, not a repo, not an upstream.

Rule applied: include ONLY Oct 26–Nov 4, 2026 hackathon-period code/work, or data/indexes
built in that window. File dates below are source-file mtimes (UTC, as shown by the
workspace; ET is UTC−4, so all Oct 27 UTC dates below are still Oct 26–27 ET and
inside the window). SHA-256 hashes are in SCAN-REPORT.md.

## checker/ — V2 checker, Oct 26–27, 2026
- checker/app_check_v2.py — Agents 101 loop, verification gate, needs_input, timeline
  (refreshed Oct 28 from playground/app-v2-merged/app_check_v2.py, Oct 27 13:47)
- checker/agents101_leftovers.py — plan, exact-evidence facts, flag do-not-use, real slab check, saved/resumable/branch checks (Oct 27)
- checker/tells_v2.py — 5 pixel tells, thresholds in code (Oct 27 04:34 UTC = Oct 26 evening ET)
- checker/crop_v2.py — card-only crop helpers (Oct 27 04:34 UTC)
- checker/agent_loop_v2.py — agent loop v2 (Oct 27 04:34 UTC)
- checker/run_demo.py — demo runner (Oct 27)
- checker/README.md — merged V2 README, Agents 101 A–D + leftovers sections
  (refreshed Oct 28 from playground/app-v2-merged/README.md, Oct 27 13:49)
- checker/meta_pipeline.py — Meta/Baseten/SAM pipeline code (Oct 27). QUALIFICATION: it
  references Muse's dynamic_credentials surrogate mechanism and connector names
  (custom.meta-model-api, custom.baseten). It contains NO secret values (see scan),
  but it is NOT standalone-runnable in a public repo without that Muse infrastructure.
  Owner decision: include as reference code, or drop before push — see EXCLUDED.md note.

## demo/ — V2 demo playground, Oct 27–28, 2026
- demo/index.html — demo UI, site styles, live camera, timeline, needs_input, slab checkbox
  (refreshed Oct 28 from playground/app-v2-demo/index.html, Oct 28 08:17)
- demo/server.py — local demo server, passes slab/back flags to the checker
  (refreshed Oct 28 from playground/app-v2-demo/server.py, Oct 27 17:30)
- demo/run_tests.py — canned-test runner (Oct 27, unchanged)
- demo/README.md — demo README, Agents 101 section
  (refreshed Oct 28 from playground/app-v2-demo/README.md, Oct 27 13:49)

## data/tcgdex-details/ — TCGdex detail index, built Oct 27, 2026
- data/tcgdex-details/en-details.json (5.6 MB, 23,771 rows) + en-details.csv (1.9 MB)
- data/tcgdex-details/en-details.json.gz (480 KB, Oct 29, 2026) — gzip copy of
  en-details.json (decompressed MD5 identical), added because the plain .json
  exceeds the GitHub push-files request limit (HTTP 413) and ships via browser
  upload instead; checker/identity_lookup.py now falls back to the compressed
  copy when the plain .json is absent (plain file still preferred when
  present, Oct 29, 2026). The API push route accepts UTF-8 text only, so the
  same gzip also travels as en-details.json.gz.b64 (base64 text, decodes to
  the identical .gz); the loader accepts .json, then .json.gz, then
  .json.gz.b64, in that order.
- data/tcgdex-details/ja-details.json (3.4 MB, 13,598 rows) + ja-details.csv (1.3 MB)
- data/tcgdex-details/SUMMARY.md — build notes, including that data-asia/ is not Japanese-only
  and 4,924 non-JA Asian rows were excluded, not filed as JA.
  Qualifies as a data index built Oct 27, not pre-hackathon app code. The 224 MB source
  TypeScript repo clone is EXCLUDED (see EXCLUDED.md).

## data/databases/ — backs/fronts indexes, Oct 26–27, 2026
- data/databases/backs-pool-2026-10-27.csv — 175 rows: 174 genuine + 1 fake back, indexed only, not cropped (Oct 27)
- data/databases/backs-index-2026-10-26.csv — backs index (Oct 26)
- data/databases/fake-fronts-intake-2026-10-26.csv — fake fronts intake (Oct 26)
- data/databases/README.md — databases README, backs-pool section (Oct 27)
  QUALIFICATION: backs-pool source_path column points to ~/workspace/user/files/…
  and to fake-samples/reference-db paths. The photos themselves are NOT in this pack.
  That path column reveals workspace layout and is useless publicly without the images.
  Recommendation before push: strip source_path to the filename only, or accept it as-is.
  No secret, IP, email, or phone was found in these files (see SCAN-REPORT.md).

## docs/ — Oct 27–28, 2026 reports and plans
- docs/tells-calibration-accuracy-2026-10-27.md — calibration report; its 29.4% figure is
  a matched-pairs diagnostic (n=17), NOT product accuracy, and is labelled as such in the file.
- docs/agents101-build-order-2026-10-27.md — Agents 101 ideas → app build order.
- docs/DEMO-CHECKLIST-2026-10-27.md — demo checklist: fully functional, no dead screens,
  no canned verdict presented as real, no SAM-authenticates claim, no grade guess.
- docs/v2-phone-bugfix-report-2026-10-28.md — V2 demo phone-bug fixes, Oct 28 (added Oct 28).
- docs/backend-tie-plan-2026-10-28.md — backend-tie PLAN ONLY, Oct 28 (added Oct 28).
  The plan itself states no build step moves without a fresh explicit owner yes;
  publishing the plan does not build, deploy, or spend anything.

## tests/ — canned-test JSON results, Oct 27, 2026
- tests/test-A-result.json, test-A-tells.json — Alakazam vs itself, Likely Genuine
- tests/test-B-result.json, test-B-tells-only.json — Alakazam vs Charizard, Inconclusive
- tests/test-C-fixed-result.json — on-device fixed case
- tests/test-D-result.json — missing-reference case
- tests/test-results-2026-10-27.json — test summary
  Binary test image (cropped.png in test-C) is EXCLUDED — JSON only.

Total pack after Oct 28 afternoon refresh: 56 content files, ~13.2 MB (12 MB of it
is the TCGdex detail JSON/CSV), plus MANIFEST.md, EXCLUDED.md, and SCAN-REPORT.md
(59 files on disk). The morning Oct 28 push already put the original 33 content
files live (remote head e7eb7ac52e64e3ff9eb62ad43f5b8d78a6d661fa); this afternoon
run pushes only the 23 new files + 1 modified file listed below.
Unchanged since Oct 27 staging: TCGdex details (hashes match sourcing/ originals),
databases indexes, checker files other than app_check_v2.py/README.md, and all tests/.

## Oct 28, 2026 afternoon refresh (extra push, owner-approved Oct 28)
Source folders are playground/backend-matcher-2026-10-28/,
playground/backend-tie-impl-2026-10-28/, playground/verification-pool-2026-10-28/,
playground/github-sweep-2026-10-28/, and playground/app-v2-merged/ (checker only).
All dated Oct 28, 2026, inside the Oct 26–Nov 4 window. No card photos are in
any of these files: the pool CSV lists filenames only, and the backend-tie
uploads/ folder was empty (test photos deleted after the run).

## backend-matcher/ — image-to-identity matcher proposal, Oct 28, 2026
- backend-matcher/matcher.py — matcher implementation (Oct 28 12:59)
- backend-matcher/test_matcher.py — matcher tests (Oct 28 12:58)
- backend-matcher/test_results.json — matcher test results (Oct 28 12:59)
- backend-matcher/threshold_raw.json — raw threshold data (Oct 28 13:00)
- backend-matcher/THRESHOLD_PROPOSAL.md — threshold proposal; NO threshold is
  approved/set for a real verdict (Oct 28 13:01)
- backend-matcher/MULTIBACKEND_ROLES.md — multi-backend roles (Oct 28 13:01)
- backend-matcher/SIGNIN_DESIGN.md — sign-in design, no credentials (Oct 28 13:01)
- backend-matcher/TEST_REPORT.md — matcher test report (Oct 28 13:01)
  Excluded from this folder: __pycache__/ (cache, not code).

## backend-tie-impl/ — backend-tie Steps 1–3 test impl + Step 4a calibration, Oct 28, 2026
- backend-tie-impl/README.md — localhost-only, TEST ONLY labelling, no deploy/spend
- backend-tie-impl/REPORT.md — full results; Step 4a gate verdict is FAIL, no real
  verdict is enabled by this work (Oct 28 09:19)
- backend-tie-impl/app.py, calibration.py, matcher.py, tells_engine.py — test impl
- backend-tie-impl/run_tests.py, delete_test_uploads.py, demo-test-upload.html
- backend-tie-impl/calibration-report-2026-10-28.json — calibration data
  This is the implementation behind docs/backend-tie-plan-2026-10-28.md (already
  pushed in the morning run); the plan alone was pushed first, this is the code.
  Excluded: uploads/ (empty at copy time).

## data/verification-pool-v2/ — verification pool v2 index, Oct 28, 2026
- data/verification-pool-v2/README.md — tier rules, owner decisions Oct 28 12:37 PM ET
- data/verification-pool-v2/verification_pool_v2.csv — 229 rows + header (76,426 bytes):
  A1 genuine identity-confirmed 73, A2 genuine pairing-confirmed 103, B fake 47
  (40 owner-confirmed fronts + 7 Sammy anchor), C reference/web 6. Filenames only;
  no photos in this file or folder. Pool v2 does NOT by itself ship a verdict.

## docs/ addition — Oct 28, 2026
- docs/github-sweep-report-2026-10-28.md — GitHub sweep, research/evaluation ONLY:
  12 repos evaluated (Skewtle, card-centering-studio, CollectorVision, imagehash,
  Tesseract, EasyOCR, TCGdex cards-database + python-sdk, Pokemon-Card-CSV,
  pokepc/dataset, Pokemon-TCGP-Card-Scanner, pokemon-tcg-companion), gaps noted
  (no dedicated fake-tell repo, no verified Penguin-stdlib backend repo), top-3
  next-test list. No third-party code is copied into this pack.

## checker/ + tests/ refresh — Oct 28, 2026
- checker/app_check_v2.py — MODIFIED since the morning push: Oct 28 09:18 source
  adds the Q10 plain-words why explainer (why_measured) to the verdict output.
- checker/why_measured.py — NEW, required by the updated app_check_v2.py import
  (Oct 28, app-v2-merged). Pushed together so the checker stays runnable.
- tests/test_why_measured_2026-10-28.py — NEW test for the why explainer.
  NOT refreshed this run: demo/index.html — its morning source
  (playground/app-v2-demo/index.html, Oct 28 08:17 per the morning manifest) is no
  longer present in playground/app-v2-demo/, so the morning-pushed copy stands
  unchanged; it was not re-copied from an unverified location.

## Oct 29, 2026 refresh (owner-requested upload, ~1:12 AM ET)
Source folders: playground/app-v2-merged/, playground/agent-loop/,
playground/tonight-labelling-2026-10-29/, playground/github-tests-2026-10-28/.
All dated Oct 28–29, 2026, inside the Oct 26–Nov 4 window. No card photos:
the labelled dataset CSV lists filenames only. Existing pack files were
re-checked against their playground sources — all unchanged (hash-identical),
so this push is additions only (15 files). Pack now: 71 content files +
MANIFEST.md + EXCLUDED.md + SCAN-REPORT.md (74 files on disk, ~13.6 MB).
Pack control files (MANIFEST/EXCLUDED/SCAN-REPORT) are NOT pushed, matching
the Oct 28 pushes.

- checker/back_pool_crops.py — back-pool crop helper (Oct 28 15:21 ET)
- checker/back_pool_score_crops.py — back-pool scoring crops (Oct 28 21:19 ET)
- tests/test_back_pool_crops.py, tests/test_back_pool_score_crops.py — their tests
- data/back-pool-scores/back-pool-score-genuine-2026-10-28.json +
  back-pool-score-fake-2026-10-28.json — back-pool scoring results (Oct 28 21:21 ET)
- docs/agent-loop-run-2026-10-28-2116-keeper.md,
  docs/agent-loop-run-2026-10-29-0055-keeper.md — agent-loop keeper run reports
- docs/labelling-guide-2026-10-28.md — labelling guide (Oct 28 22:36 ET)
- docs/github-tests-report-2026-10-28.md — GitHub-tests report ONLY (Oct 28);
  no third-party code, no .npz binaries (see EXCLUDED.md)
- labelling/PROGRESS-2026-10-29.md — tonight's labelling progress ledger
- labelling/set_fill.py, labelling/apply_set_fill.py, labelling/test_set_fill.py
  — set-fill code + test (Oct 29 ~1:05 AM ET)
- labelling/labelled_dataset_v3.csv — labelled dataset v3, 339,843 bytes,
  filenames only, no photos (Oct 29 01:06 ET; v3 supersedes v2, v2 not packed)

## Oct 29, 2026 daily refresh (09:10 AM ET scheduled run)
Remote head before this run: 63f2a97784714cdaacd429d1ae107d1eb52ccb0f (the Oct 29
~1:12 AM owner-requested upload). All existing pack sources re-checked against
playground — checker/, demo/, TCGdex details, databases, labelled dataset v3 all
hash-identical, unchanged. This run is 15 additions + 1 modification. Pack now:
86 content files + MANIFEST.md + EXCLUDED.md + SCAN-REPORT.md (89 files on disk,
13,889,471 bytes). Control files are NOT pushed, matching prior runs.

- docs/agent-loop-run-2026-10-29-{0117,0127,0137,0158,0207,0218,0238,0257,0307,0316,0328}-keeper.md
  — 11 new agent-loop keeper run reports, Oct 29 01:17–03:42 ET, since the 0055
  keeper report pushed in the 1:12 AM run.
- labelling/PROGRESS-2026-10-29.md — MODIFIED: updated to the Oct 29 09:07 ET
  source (34,104 bytes, was 2,129 bytes at the 1:12 AM push); the labelling
  ledger kept growing overnight (scan batches 1–11).
- data/set-symbol-guide/ — NEW index built Oct 29, 2026 ~1:21 AM ET from TCGdex
  set records: README.md (the symbol-match gate: a set label counts only when the
  card's own symbol visually matches; all 271 Oct 29 set-fills are PROVISIONAL),
  build_guide.py, set_symbol_guide.csv (49,772 bytes) + set_symbol_guide.json
  (128,677 bytes) — 404 rows, EN 220 + JA 184 sets, symbol/logo URLs only, no images.

## Oct 29, 2026 — standalone fix port (~9:35 AM ET, owner-ratified)
Source: playground/standalone-fix-2026-10-29/pack-fixed/ (FIX-LOG.md + RESULTS.md
there are the evidence; the scratch copy was verified standalone under a clean
HOME: PASS 10 / SKIP-WITH-REASON 4 / HONEST-DEGRADE 2 / FAIL 0, secret scan
0 hits). Owner ratified the scope change in chat Oct 29, 2026 ~9:35 AM ET
("Yes — port the fixes into the live pack"). This port REPLACES the pack's
earlier statements above where they conflict: a root README.md IS now in the
pack, and the six checker modules previously left out by scope decision (see
EXCLUDED.md) are now INCLUDED. Pack now: 97 content files + MANIFEST.md +
EXCLUDED.md + SCAN-REPORT.md (100 files on disk, 14,260,998 bytes before this
control-file update). The evening push (Oct 29, 9:10 PM ET job) carries this
pack; nothing was pushed by the port itself.

- README.md — NEW at pack root: Noor's judge's-map README (drafted Oct 29 in
  playground/hackathon-ideas-execution-2026-10-29/01-noor-readme/), ported in
  as the repo README. Earlier pushes did not touch the remote README because
  no root README was in the pack; this one ships as a new file at repo root.
- requirements.txt — NEW at pack root (Pillow/numpy/scipy; backend-tie deps
  commented with pointers) + backend-tie-impl/requirements.txt — NEW.
- checker/ — six modules NEW, bundled real (Oct 26–28 hackathon work, no stubs):
  quality_gate.py (Oct 27, was the standalone blocker: without it every
  pack-only check degraded to Inconclusive before measuring tells),
  multi_reference.py (Oct 27), identity_lookup.py (Oct 28, PATCHED to prefer
  the pack's own data/tcgdex-details/), on_device_crop.py (Oct 26),
  reference_registry.py (Oct 27), owner_scan_registry.py (Oct 27).
  NOT bundled: the registries' data manifests and all reference/card photos —
  the registries degrade to empty → Inconclusive, never a guess (see EXCLUDED.md).
- checker/crop_v2.py — MODIFIED: no longer sys.path-points at the workspace
  prototype folder; uses its own folder (unbreaks tests/test_back_pool_crops.py).
- tests/ — MODIFIED: test_why_measured_2026-10-28.py, test_back_pool_crops.py,
  test_back_pool_score_crops.py now insert ../checker pack-relative in sys.path;
  T1 + T2 pass as shipped from the pack root, no PYTHONPATH.
- demo/server.py — MODIFIED: resolves the checker pack-relative; verified
  starting standalone and answering /api/lookup from pack data (37,369 counts).
  demo/run_tests.py — MODIFIED: pack-relative; prints SKIP-with-reason naming
  the three missing fixture photos (card photos, still excluded) + the
  committed A/B evidence, exit 0. No synthetic fixtures were fabricated.
- backend-matcher/matcher.py + test_matcher.py — MODIFIED: test repointed at
  the pack's verification-pool CSV, searches fixtures/$FAKECHECK_POOL_DIRS
  first; standalone it SKIPs cleanly and leaves test_results.json byte-identical.
- labelling/set_fill.py + test_set_fill.py — MODIFIED: inputs pack-relative,
  test passes 12/12 against the shipped fixtures below; the generator SKIPs
  with reason when the upstream TCGdex clone is absent, without overwriting
  shipped results. NEW fixtures: labelling/set_fill_results.csv (real generated
  results) + labelling/labelled_dataset.csv (PRE-fill dataset, metadata +
  filenames only, no photos — the test's assertions are defined on the pre-fill
  source: 118 Pool-A targets; v3 is the post-fill state and stays as packed).
- backend-tie-impl/matcher.py, tells_engine.py, run_tests.py — MODIFIED:
  repointed to the bundled ../checker; run_tests.py resolves uvicorn via
  env/PATH/-m and SKIPs with the install instruction when absent (no more
  /tmp/backend-tie-venv path). backend-tie-impl/README.md — MODIFIED (relative
  venv instructions).
- Smoke-verified in place after the port (pack root, clean HOME):
  tests/test_why_measured_2026-10-28.py → PASS; tests/test_back_pool_score_crops.py
  → 6/6 OK; checker/app_check_v2.py synthetic run → Inconclusive
  (identity_found_but_no_reference_image_for_identity, base1-1 resolved from
  pack data), api_calls 0, spend_usd 0.0 — honest result, never a guess.
