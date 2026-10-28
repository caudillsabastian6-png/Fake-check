# App V2 — Merged Playground Build (Oct 27, 2026)

**PLAYGROUND ONLY. Not a release. No Play publish, no public demo link
update, no production release in this job. No keys, no card photos
committed, no SAM/Baseten/Meta calls, $0 local tests only.**

Owner order: Oct 27, 2026, 00:34 ET — "go ahead and merge the V2."

## What merged (one flow, in `app_check_v2.py`)

1. **Agent Loop v2 flow** (`agent_loop_v2.py`, copied verbatim):
   Pip crop → Index compare → Gauge measure → decision → Latch examine.
   Original v2 had no tells measurement, so it correctly stayed
   Inconclusive. This merge plugs that gap with Tells v2.
2. **Tells v2 measurement** (`tells_v2.py`, copied verbatim):
   5 pixel tells, same measurement on user crop and reference.
   Rule unchanged: ≥2 strong mismatches → Likely Counterfeit;
   0 strong + ≥3 matches → Likely Genuine; else Inconclusive.
3. **Pip on-device crop v2** (`crop_v2.py`, copied verbatim):
   DEFAULT crop path for full photos. Smoothed-colour mask + 10%
   inset, v0 fallback. See blockers — it is the default, not a proof.

## Hard rules enforced in code

- **Identity-first:** `--identity` is required. If the reference is not
  for that identity, verdict is Inconclusive — never Genuine.
- **Manifest / name match alone NEVER produces Likely Genuine.**
  Only a tells measurement can. No tells → Inconclusive.
- **Every Likely verdict is an ESTIMATE ONLY**, never official, never
  guaranteed, never a grade, never a SAM authentication.
- **SAM escalation only:** on-device REFUSE / invalid box, or an
  explicit `--real-check`, records `SAM_ESCALATION_REQUIRED` and stays
  Inconclusive in this $0 build. No live SAM call is made here. A SAM
  box may be *supplied* via `--sam-box` (logged as supplied, not live).
- **Offline fallback:** unreadable reference → Inconclusive with
  reason `reference_unreadable_offline`. No web fetch.
- **Back photo:** noted, NOT tells-scored in v2. Front-only verdict;
  the output says plainly a back would help if it disagreed.
- **Bad crop ≠ fake card (fixed Oct 27, see Test C):** an on-device
  box must roughly match the reference card's aspect (±0.15).
  A box that fails is REJECTED and escalated, never tells-scored.

## Files in this folder

- `app_check_v2.py` — NEW merged orchestrator ($0, Pillow only)
- `agent_loop_v2.py` — verbatim copy of Agent Loop v2 (Oct 26)
- `tells_v2.py` — verbatim copy of Tells v2 (Oct 26)
- `crop_v2.py` — verbatim copy of Pip crop v2 (Oct 26, Job B)
- `v1-backup/agent_loop_v1.py` — v1 loop, copied, NOT overwritten
- `v1-backup/crop_v1.py` — v1 crop, copied, NOT overwritten
- `v1-backup/TELLS_V2_REPORT.md` — Tells v2 report copy
- `tests/` — test outputs + `test-results-2026-10-27.json`

Originals were NOT modified: v1/v2 source files in
`playground/agent-loop/`, `playground/tells-v2/`, and
`playground/pip-job-b/` were copied, never moved or overwritten.

## Test results, Oct 27, 2026 — all $0, api_calls=0, spend=$0

| Test | Result | Why it matters |
|---|---|---|
| A — Alakazam crop (night run `cropped.png`) vs sr-0001 Alakazam, identity Alakazam\|Base\|1 | **Likely Genuine, 5/5 matches, 0 strong** | Merged flow works end-to-end. **PIPELINE TEST ONLY** — the crop was derived from the same source image, so this is NOT authentication proof. |
| B — Same Alakazam crop vs sr-0004 Charizard, reference identity Charizard\|Base\|4 | **Inconclusive** (`identity_mismatch`) | Identity gate blocks a cross-identity Genuine. |
| B (tells-only) — same crop vs Charizard, tells_v2 direct | **Inconclusive, 2 matches, 1 strong** (histogram diff 1.0514) | Even without the identity gate, tells alone do NOT say Genuine. Charizard is a different identity, not a fake Alakazam. |
| C (fixed) — sr-0001 full photo, on-device crop, vs sr-0001 | **Inconclusive** (`sam_escalation_required_crop_not_available`) | Correct behaviour for a bad crop: refuse, escalate, do not fake a verdict. |
| D — Alakazam crop vs missing reference | **Inconclusive** (`reference_unreadable_offline`) | Offline fallback works, no web fetch. |

### Bug found and fixed by Test C (do not hide this)

First run of Test C: on-device crop fell back to v0 and produced box
`[28, 27, 564, 475]` (aspect 1.196) for a portrait card (reference
aspect 0.727). Tells on that bad crop said **Likely Counterfeit for a
genuine card vs itself** — a false Counterfeit caused by the cropper,
not by the card. A first fix (generic landscape allowance) still
passed 1.196 as "landscape". The final fix rejects any on-device box
whose aspect differs from the reference aspect by >0.15, and the
re-run (Test C fixed) correctly returns Inconclusive + SAM escalation.
The original false result is preserved, clearly labelled, in
`tests/test-C-ondevice-sr0001-BUG-FOUND-then-fixed/` — it is evidence,
not a passing test.

## What is still v1 (NOT merged / NOT upgraded by this job)

- One-Go in the live app is still v1.
- The Public Demo artifact's public link still serves the OLD version
  (Oct 26 rebuild exists, link NOT updated — per this job's scope).
- No full app source in the workspace — so this merge is a playground
  build, NOT a merge into the full app source. That blocker stands.
- Grade SAM, Play closed test, and any live SAM/Baseten spend are
  untouched by this job.

## Still blocked (owner review must weigh these)

1. **Phone cropper not shippable as sole cropper.** Job B phone mean
   IoU ~0.58 at best; v0 fallback can produce a wrong-aspect box (Test C).
   The aspect gate in this merge stops a false Counterfeit, but it does
   not make the cropper good — it makes it refuse more often. SAM
   escalation is the real path for Real checks until the cropper improves.
2. **Full app source absent from workspace.** Nothing here proves the
   live app can take this merge without integration work.
3. **Tells v2 uncalibrated.** Thresholds are documented, not tuned on
   real genuine vs known-fake pairs of the same identity. Test A is a
   pipeline test, not calibration.
4. **SAM costs / Grade SAM / Play closed test** — all still open, all
   $0 in this job, none resolved by this merge.
5. **Front-only verdicts.** Backs are not scored in v2; a back that
   disagreed with a front verdict would not be caught here.

## Ready for owner review?

**Yes, as a playground build — for review, not for live push.**
The merged flow, identity gate, tells rule, offline fallback, SAM
escalation record, and bad-crop rejection all behave as specified on
the tests above, at $0. It is NOT ready for a live push until: the
owner reviews this README + test results, the cropper / SAM escalation
path is decided for Real checks, and the full app source integration
is done (blocker 2). No publishing was done in this job.

## Agents 101 ideas A–D, built Oct 27, 2026 — playground only, $0
- **A — Agent loop, formalised:** fixed step order identity → crop →
  front tells → back tells → verification → sign-off → filing, with
  `progress.json` rewritten after every step in the output dir and a
  6-row `loop_timeline` (saw / decided / returned per step) in
  `result.json`. A stopped run is inspectable from its last step.
- **B — Verification inside filing:** `checklist` (identity_proven,
  front_tells_recorded, back_state_honest, slab_complete,
  findings_cite_recorded_tells) + `findings`/`back_findings` citing
  recorded tells by name. A Likely verdict that fails the checklist
  is downgraded to Inconclusive; `latch_signoff` is true only for a
  filed verdict. No claim text can bypass this gate.
- **C — Evidence request / needs_input:** `--slab-claimed` without
  `--slab-cert`, `--back-claimed` without `--back`, a malformed
  identity, or a refused/invalid on-device crop returns
  `status=needs_input`, verdict Inconclusive, and `needs_input`
  naming the exact missing item — no verdict is guessed.
- **D — Transparency:** the demo UI now renders `loop_timeline`
  (Check timeline panel) and the `needs_input` box, alongside the
  existing tells tables. Bubbles remain tells matching only, never a
  percentage, grade, or authentication claim.
Verified Oct 27: canned A/B PASS 2/2 via run_tests.py, front Genuine
+ fake back = Likely Counterfeit (back 1/5, 3 strong, filed, sign-off
true), slab-claimed without cert = needs_input, back-claimed without
back = needs_input, slab-claimed with cert = filed Likely Genuine.

## Agents 101 leftovers 5-9, built Oct 27, 2026 — playground only, $0
New module `agents101_leftovers.py`, wired into `app_check_v2.py` with
small hooks only; A-D loop, verification gate, needs_input, timeline,
site styles, camera, back scoring, and 10-idea elements untouched in
behaviour (canned A/B re-verified below).
- **5. Plan tool:** plan is built and shown BEFORE the check runs
  (7 steps), updated as tells/slab land (notes + completed list).
  A plan is a description, never evidence.
- **6. Record_fact with exact evidence:** every measured tell becomes
  a fact with match, strong_mismatch, difference, threshold, source
  basename, and reference basename. A tell missing any field refuses
  the run (ValueError -> Inconclusive). No finding without a fact.
- **7. Flag do-not-use:** explicit permission flag only
  (unpermissioned/private). A flagged front photo is excluded from
  findings/facts entirely and returns needs_input, never a verdict
  and never a quote of that source.
- **8. Real slab check:** cert + card-inside photo, BOTH required.
  Format alone is not grader verification — status is always
  `cert_and_card_present_not_grader_verified` (no grader DB, no
  network). Cert alone never yields Genuine; card tells must still pass.
- **9. Saved / resumable / branch checks:** same out-dir progress.json
  + check.json approach, no new store. `--pause-after identity|crop|
  tells` files NO verdict; `--resume-from <out>` keeps the check id
  and prior steps and re-executes the deterministic $0 measurements;
  `--branch-from <out>` starts a new check id with parent_check_id set.

Measured Oct 27, 2026 ($0, api_calls=0):
- A Alakazam vs itself: Likely Genuine, filed, 5 facts, 7 plan steps.
- B Alakazam vs Charizard: Inconclusive (identity mismatch).
- Front Genuine + fake back (correct back path): Likely Counterfeit,
  back 1/5 matches, 3 strong, 10 facts (5 front + 5 back). NOTE: a
  first attempt at this test used a wrong fake-back path and returned
  Inconclusive with back_tells_failed — that was a test-path error,
  not a checker verdict; the rerun with the correct path passed.
- Slab claimed, no cert, no card photo: needs_input (slab_cert +
  slab_card_inside), Inconclusive.
- Slab claimed, cert 123456 + card-inside photo: Likely Genuine,
  slab_status cert_and_card_present_not_grader_verified.
- Flagged source (unpermissioned): needs_input source_flagged,
  Inconclusive, 0 facts, 0 quoted findings.
- Pause after tells: progress paused, NO result.json; resume from it:
  same check id, Likely Genuine, filed.
- Branch from A: new check id, parent = A's check id, Likely Genuine.
- Demo server smoke: GET / 200 (24,628 bytes), /api/identities lists
  both identities, canned A Likely Genuine (5 facts, 7 plan steps),
  canned B Inconclusive, server stopped, no process left.

## Identity wiring — Oct 27, 2026 (playground only, $0)
TCGdex EN/JA detail index is now wired into app_check_v2.py via identity_lookup.py
(--lookup-set/--lookup-number/--lookup-name/--lookup-language) and into the demo
server (/api/lookup, /api/lookup-stats). Searchable: EN 23,771 + JA 13,598 = 37,369.
Set+number first, printed number beats name/rarity, name fallback lists
candidates only and never auto-picks. Unknown or ambiguous set+number returns
needs_input naming it. A lookup hit is identity only, NOT authentication, and
most cards have no reference image in the playground (only 2 canned), so their
checks stay Inconclusive. Tests: test_identity_wiring.py (12/12 PASS).

## Reference expansion, batch 1 (Oct 27, 2026)
On-demand verified references: reference_registry.py + verified_references_batch1.json.
Measurable identities 2 -> 10 (2 canned + 8 new pilot Base Set refs, file+index verified,
600x825 WEBP, SHA-256 recorded). Pilot refs carry reference_status
verified_reference_pilot_uncalibrated — tells calibration still open, so a Likely
verdict against a pilot ref is a pipeline measurement, not authentication.
Non-batch identities stay no-reference/Inconclusive even if a TCGdex file exists.
Full plan: reference-expansion-plan-2026-10-27.md. Tests: test_reference_expansion.py ALL PASS.

## Oct 27, 2026 — Scan quality gate + multi-reference median (playground only, $0)
- quality_gate.py runs before tells: blur (edge_density <0.015 AND mean step <5.0), severe glare (>10% pure white), framing/aspect proxy (0.15 vs reference), size <200px. Failure = needs_input + retake, NEVER Counterfeit, tells not measured. Sleeve is not detectable from $0 pixels and is never rejected on sleeve.
- multi_reference.py: median tells across up to 5 verified references, checker flag --additional-references (verified files only). Single = single mode, zero = Inconclusive. Median results are pilot/uncalibrated.
- Tests: test_quality_median.py — 11/11 pass (clean pass, blur/crop/glare needs_input, canned A/B unchanged, median 2-ref Genuine).
