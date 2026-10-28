# Backend-tie Steps 1–3 implemented + Step 4a calibration — TEST ONLY, Oct 28, 2026

**Status: PLAYGROUND / TEST ONLY. No live push, no Modal deploy, no endpoint left running,
no spend ($0), no training, no GPU, no model calls, no real verdict shipped.**

Owner approval on file: Steps 1–5 approved Oct 28 ~09:14 AM, corrected to Step 5 max (no Step 6).
Later update Oct 28 ~09:15–09:16 AM: Step 4b (accept report) and 4c (enable a real verdict) approved
IN PRINCIPLE, and Step 5 "do everything else" approved as preparation — BUT both are gated:
a report must first exist, pass, and get a Final Examiner (Latch role) eyeball review, and any
enabled verdict is PARTIAL ONLY (passing identities/conditions only). **This report does NOT pass
(see Step 4a below), so NO real verdict is enabled by this work, regardless of that advance
approval. Step 5's actual G1 move is NOT done (G1 has not arrived; arrives by Oct 30) and a live
push is NOT approved by this work.**

## Retention (default, owner did not name a different note in the approval)
Test photos live ONLY in `uploads/` inside this impl folder, deleted after the test run
(`delete_test_uploads.py`, and POST /v1/test-session/{id}/delete). They are never retained as a
product store, never sent anywhere else, never used to file a back as fake. The test server was
stopped after testing; nothing is left running. The owner may change this default by naming a
new retention note — until then, this default stands.

## What was built, where
All in `~/workspace/fake-check/playground/backend-tie-impl-2026-10-28/`:
- `app.py` — FastAPI prototype (localhost 127.0.0.1:8765 only). Endpoints: GET /health,
  POST /v1/test-upload (receipt only), POST /v1/test-match, POST /v1/test-tells,
  GET /v1/test-session/{id}, POST /v1/test-session/{id}/delete. Run with the venv in /tmp
  (fastapi/uvicorn/pillow installed there, $0, not a system change). **Not deployed to Modal:**
  the Oct 27 Modal test token was not captured and is effectively unrecoverable, and Modal
  Shared billing is unresolved — per the brief, no Modal endpoint was created, scaled, or left live.
- `matcher.py` — Step 2 wrapper around the existing `app-v2-merged/identity_lookup.py`
  (37,369 EN+JA identities verified: EN 23,771 + JA 13,598). No new pool, no merge.
- `tells_engine.py` — Step 3 wrapper around the existing `app-v2-merged/tells_v2.py`
  (5 pixel tells, same thresholds). Front and back measured separately, each against its own
  reference only. Missing back = not_measurable, never borrowed.
- `demo-test-upload.html` — Chrome-only test page (same machine as the server). Labelled
  "TEST UPLOAD ONLY — NOT A REAL CHECK" throughout. **Deviation, stated plainly:** the brief
  said "demo-side upload path in the old-plus playground copy only". This test page is the
  demo-side upload path for playground testing, and the old-plus file itself was NOT modified
  for upload, so its pending Chrome test is not disturbed by a localhost endpoint. If the
  owner wants the upload card merged into old-plus itself, that is a separate, small step.
- `calibration.py` + `calibration-report-2026-10-28.json` — Step 4a, $0 local run.
- `run_tests.py` — re-runs the server tests (health + match cases), stops the server,
  deletes test uploads. Result on Oct 28: PASS (4/4).
- `delete_test_uploads.py` — retention cleanup.

## Step 1 tests (plan §3, Step 1) — PASS
1. Front photo uploads and back photo uploads both return a receipt for the same session — PASS
   (front-only session reported back missing; front+back session reported both present).
2. Missing front/back reported as missing, never paired with a generic/wrong-side image — PASS
   (receipt `missing: ["back"]`, note says so explicitly).
3. Failed upload shows plain-language failure, never a fake verdict — PASS (non-image file
   returned HTTP 400 "front photo is not a readable image — upload failed, no verdict…").
4. Demo still shows SAMPLE labelling on non-real screens — PASS for this impl (every response
   carries "TEST ONLY — NOT A REAL CHECK, NOT A VERDICT"; old-plus itself was not changed).

## Step 2 tests (plan §3, Step 2) — PARTIAL, not fully passed
1. Named test set, correct identity or needs_input, never a confident wrong identity — PASS
   for set+number: exact `base1` + `1` resolves Alakazam base1-1; loose `Base` + `1` + Alakazam
   returns needs_input listing base1-1, base4-1, ecard1-1 (never picks).
2. Out-of-pool / too-blurry returns needs_input, not a nearest guess — PASS for out-of-pool
   (`Nonexistent Set` + `999` → needs_input). A blurry-photo image test was not run as a
   separate case because image-only matching does not exist (see gap).
3. Exact-set disambiguation preserved — PASS (see loose-Base case above, and the Oct 28
   exact-set regression test already on file).
4. Demo still SAMPLE; only the identity line may change, labelled test match — PASS in this
   impl (every match response is labelled TEST MATCH ONLY).
**GAP — Step 2 is partial:** there is NO image-to-identity matcher on file at $0.
`inline_classifier` takes tell numbers, not pixels, and needs model calls this step does not
use. An image supplied without set/number correctly returns needs_input. **Proposed threshold:
NONE SET.** A future image matcher must have a threshold named and approved by the owner
before image-only matching can count as passed. Do not quote a threshold from this work.

Named test set for Step 2 (existing ground truth only, no invented cards):
- Alakazam, Base Set, 1 (base1-1) — user crop + sr-0001 reference, from the Oct 28 exact-set
  regression test. Blastoise, Base Set, 2 (base1-2, sr-0002) as the wrong-reference control.
- FAKE-001..009 / anchor set: NOT used as named identities — the Oct 26 fake-fronts manifest
  records those photos as owner-confirmed fakes but states card-by-card identification was
  NOT yet verified, so no name/set/number is quoted for them here.
- Chatot: NOT used as a test identity — it has 2 distinct verified phone copies and needs
  1 more; it is NOT median-ready, and no Chatot photo pair was in this run.

## Step 3 tests (plan §3, Step 3) — PASS as test evidence only
1. Each named test card lists all 5 tells, fired / not fired / not measurable, front and back
   separate — PASS for front (same-card front: 5/5 matches; wrong-ref front: 4/5 matches,
   1 strong). Back was not_measurable in every case here because no verified paired back
   reference for these identities was supplied — that is the correct behaviour, not a pass
   for back scoring.
2. Front-only check does not borrow back evidence — PASS (back = not_measurable, reason stated).
3. Known fake and known genuine both produce readable tell evidence — PARTIAL: the known
   genuine same-card case produces readable evidence (5/5). The owner-confirmed fake front
   (5280_324_7kcl.jpg, identity unknown) vs the Alakazam reference produced a test-only
   Counterfeit outcome, but that is a MISMATCH signal against a non-own reference, NOT
   credited as fake detection, because its own card's reference was not used.
4. Demo still SAMPLE / test-evidence labelling; no tester sees a Likely from this step — PASS
   (shipped_verdict is always null; test outcomes are labelled "test-only … NOT shipped").

## Step 4a calibration — RUN LOCALLY, $0 — GATE VERDICT: FAIL, NO REAL VERDICT SHIPS
Set recorded in `calibration.py` before scoring (8 cases, see the JSON for per-case values):
- C1 same-card front (Alakazam crop vs sr-0001): test-only Likely Genuine, 5/5 tells — agree.
- C2 wrong-reference control (Alakazam crop vs Blastoise sr-0002): test-only Inconclusive
  (4/5 matches, 1 strong — histogram only). Safe (no confident wrong verdict), but it proves
  tells do NOT distinguish a different Base Set card: discrimination fails for this control.
- C3 fake front, identity unknown, vs Alakazam reference: test-only Likely Counterfeit —
  mismatch signal only, EXCLUDED from fake-detection credit (reference is not its own card).
- C4 loose Base/Alakazam 1: needs_input — agree. C5 image-only: needs_input — agree as a
  safety outcome, not as an image-matching pass. C6 front-only: back not_measurable — agree.
  C7 out-of-pool: needs_input — agree. C8 exact base1-1: resolved — agree.
- Safety agreement: 7/7 safe outcomes (no confident wrong verdict). False-Likely rate: 0
  confident wrong verdicts in 8 cases. Inconclusive rate: 1 of 3 tells cases (the
  wrong-reference control). These safety numbers do NOT make the gate pass, because:
  - Median-ready identities: **0** (Chatot 2/3 needed, not ready).
  - Paired front+back same-physical-card test set for a named identity: **NONE in this run**
    (backs-pool pairs are "possible" hand triage, not verified same-card pairs; tonight
    centre crops are backs without paired fronts here).
  - Image-only identity matching: **not available** (see Step 2 gap).
  - Tells discrimination on wrong-reference controls: **not proven**.
- **Conditions a Likely would require (all unmet today):** a median-ready identity;
  a verified paired front+back genuine+fake set with ground truth recorded before the run;
  tells discrimination proven on wrong-reference and near-identical controls; an
  image-to-identity matcher with a named, owner-approved threshold (or an explicit
  set+number-only scope); Latch Final Examiner eyeball review of this report and of
  tester-facing wording.
- **Therefore: Step 4b (accept report) and 4c (enable a real verdict) are NOT satisfied by
  this report, even though the owner approved them in principle.** That advance approval
  was expressly gated on a passing report + Latch review + partial scope only. This report
  fails, so the plan stops here for real verdicts: demo stays SAMPLE, backend stays test-only.

## What is NOT done
- Step 4b: report acceptance — NOT done; this report is submitted for owner + Latch review,
  and it recommends NON-acceptance as a basis for any real verdict.
- Step 4c: enable any real verdict — NOT done, and must not be done on this report.
- Step 5: G1 move — NOT done; G1 has not arrived (by Oct 30). Preparation only: this impl is
  portable (FastAPI + local files, no Modal dependency) and can be re-tested on G1 when it
  arrives. Modal prototype: retired by default per Step 5 direction; no Modal endpoint was
  created or left live in this work, and the old prototype URL was not touched.
- Live push — NOT done, NOT approved by this work.
- Any spend, training, GPU, model call, or Modal scaling — NONE. Cost: $0.
- Owner phone test in Chrome — STILL OWED (see below).

## Owner phone test in Chrome still owed (before anything counts as passed beyond this local run)
1. Start the local test server (instructions in this folder's README — to be added by parent
   if wanted; server command is in app.py's docstring), open `demo-test-upload.html` in Chrome
   on the same machine, upload a front photo and a back photo, confirm the receipt shows
   both present and no verdict.
2. Upload front only, confirm the receipt reports back as missing (never a paired image).
3. Upload a non-image file, confirm the plain-language failure (no verdict).
4. In the old-plus demo in Chrome (unchanged by this work), confirm the live camera
   see-through and music loop from the Oct 28 morning fixes still work — those were not
   re-tested in this impl run.
5. Review this calibration report + Latch eyeball review before ANY discussion of enabling
   a real verdict. The recommendation from this run is: do not enable one yet.
