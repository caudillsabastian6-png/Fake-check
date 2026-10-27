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
