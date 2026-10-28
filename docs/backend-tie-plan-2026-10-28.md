# Backend-Tie Plan — Real or Replica demo to backend, so testers can really take photos of cards

**Status: PLAN ONLY — Oct 28, 2026**

- This document is a plan. Nothing in it is approved to build yet, and nothing in it has been built.
- Owner approval on Oct 28, 2026 was for drawing up this plan step by step, with what gets tested first, before any code goes live.
- **A fresh, explicit owner yes is required for each build step below, after the owner reviews this plan.** No step moves on a plan approval alone.
- No code changes, no backend deploy, no live push, no spend, no training, no data upload, nothing sent or posted as part of this plan.

---

## 1. Current state, honestly

### 1.1 The demo today is SAMPLE only

- The current playground build is the old-plus demo, based on the old Public Demo (Upscale Build, staged), with upgraded games, avatar, sign-ins, menu fix, live scrolling background, and related fixes.
- Its checks are canned SAMPLE verdicts. A photo picker / Choose File flow exists, but the verdict shown is not read from the photo the tester provides.
- Camera behaviour depends on where the demo is opened:
  - **In Chrome on a phone:** `getUserMedia` camera and Choose File (which opens the phone camera / gallery picker) can work.
  - **In the Muse file viewer:** camera does not turn on, the keyboard does not pop for text inputs, and gate button taps have been observed not to get through. Viewer limits are not demo-code bugs, and viewer testing cannot prove camera, keyboard, or gate behaviour.
- Until a gate in §3 passes, the demo must stay SAMPLE-labelled. No tester-facing wording may imply a photo taken in the demo has been really verified.

### 1.2 The backend today is identity-only

- Modal backend prototype: https://caudillsabastian6--real-or-replica-backend-fastapi-app.us-east.modal.run
- Verified state: health endpoint has returned HTTP 200 with an identity-only, prototype, non-deploy status. It has:
  - **No photo upload endpoint.**
  - **No tells scoring wired in.**
  - **No real-verdict path.**
- It is a prototype, not a product backend. It must not be presented to testers as a live verification service.

### 1.3 The data and calibration position today

- Identity pool: **37,369 identities** in the whole-app playground build (English and Japanese rows combined, as recorded in playground work).
- Tells v2 (`playground/app-v2-merged/tells_v2.py` in prior work): **5 pixel tells**, with a rule of ≥2 strong = Likely Counterfeit, 0 strong + ≥3 matches = Likely Genuine, otherwise Inconclusive.
  - **That rule is NOT calibrated cross-source. Never ship a cross-source Likely verdict from it as it stands.**
- Median-ready identities: **0**.
  - Per-identity median rule on file: 3–5 distinct phone copies of verified-genuine cards; separate copies count, the same SHA counts as one copy.
  - Chatot is the closest example on file: 2 distinct verified phone copies, needs 1 more for a median set. It is not median-ready yet.
- Genuine backs and owner-printed help-text backs are **never** to be filed as fake backs. That rule survives every step below.

### 1.4 Hosting position today

- Modal is temporary. The owner has said he does not plan to keep paying for Modal.
- The long-term home in this plan is the G1 machine after its arrival (arrives by Fri Oct 30, 2026), not Modal forever.
- Any Modal work in this plan is therefore a stepping stone for testing, not the final home, and any step that would leave a Modal endpoint live, scaled, or public needs its own owner decision (see §4, Step 5).

---

## 2. Proposed architecture, in order

The order matters. Do not skip ahead to a real verdict because a photo upload works, and do not move hosting before the verdict path is proven in a test environment.

```
Phone (Chrome) — old-plus demo, SAMPLE-labelled
        │  front + back photos, only after owner approval for that step
        ▼
Photo upload endpoint (new, test-only at first)
        │
        ▼
Identity matching from the image (name / set / number, with needs_input
when the image cannot be matched confidently — never a guessed identity)
        │
        ▼
Tells engine, front + back (5 pixel tells, plus back-pool reference work
only when that work itself is approved and calibrated)
        │
        ▼
Calibration gate (§3, Step 4) — NO real verdict ships before this passes
        │
        ▼
Real verdict path, only for identities / conditions that passed calibration,
otherwise Inconclusive / needs_input, with SAMPLE labelling kept everywhere else
        │
        ▼
Hosting move to G1 (Step 5), Modal prototype retired or left as a test stub
only if the owner explicitly says so
```

Key design constraints for every step:

- **No forced Likely.** If identity, tells, or back evidence is insufficient, the answer is Inconclusive or needs_input naming what is missing. Never a guessed Likely.
- **No silent downgrade of honesty.** A SAMPLE screen, a real-check screen, and an Inconclusive screen must be visibly different to the tester.
- **Photos are not kept longer than the step requires.** Each build step must state, before it is approved, where photos go, how long they are kept, and how they are deleted. This plan does not authorise any retention policy by itself.
- **Demo-first safety.** If any step fails its test, the demo stays SAMPLE and the backend stays identity-only. That is the rollback for every step (see §4).

---

## 3. Steps, in order

### Step 1 — Photo upload endpoint (front + back), test-only

**What it changes:**
- Adds one new backend endpoint that accepts a front photo and a back photo from the demo, returns a receipt (upload received, image sizes / hashes for logging, no verdict), and stores the photos only as the approved retention note for that step states.
- Adds a demo-side upload path in Chrome only (Choose File / camera picker), clearly labelled as a test upload, not a real check.

**What it does NOT change:**
- No identity matching, no tells scoring, no verdict of any kind. The demo still shows SAMPLE verdicts, and any uploaded photo gets a receipt only.
- No change to the live site, the live demo, or the Modal prototype's identity-only behaviour for other callers.
- No change to the 37,369-identity pool, the tells code, or any calibration claim.

**Test to pass before moving on:**
1. In Chrome on the owner's phone, front photo uploads and back photo uploads both return a receipt, for the same check session.
2. A missing front or missing back is reported as missing, not silently paired with a generic or wrong-side image.
3. An upload that fails (network, size, format) shows a plain-language failure, not a fake verdict.
4. The demo still shows its SAMPLE label on every screen that is not yet a real-check screen.

**Owner tap required:** Fresh explicit yes for Step 1, after reviewing this plan, including the retention note for that step (where photos go, how long, how deleted).

**Cost:** Must be $0 for the step itself, or a named cost approved separately before the step starts. No spend is authorised by this plan. Modal grant limits on file ($130 total Modal grant: $100 + $30 Starter) are noted, but this plan does not authorise drawing on them, scaling a Shared Endpoint, running a Dedicated Endpoint, or leaving an endpoint live.

**Rollback:** Remove / disable the upload path in the demo; backend returns to identity-only. Demo stays SAMPLE.

### Step 2 — Identity matching from the image

**What it changes:**
- The backend, given front (and, where useful, back) photos, returns a ranked identity match: name, set, card number, and a confidence / needs_input state.
- The demo can display "this looks like X" only when the match passes the threshold set in the step approval; otherwise it shows needs_input with candidate identities or a request for a clearer photo, never a guessed card.

**What it does NOT change:**
- No tells verdict, no Likely Genuine / Likely Counterfeit, no grade guess, no market price guess.
- No change to the identity pool itself in this step (no new identities added, no pool re-merge) unless a separate pool step is approved.
- No change to Step 1's retention note except as explicitly re-approved.

**Test to pass before moving on:**
1. On a small, named test set (owner-approved cards, including at least one card that is easy to confuse with a near-identical set / number), the matcher returns the correct identity or needs_input — never a confident wrong identity.
2. A photo of a card outside the pool, or too blurry / cropped to match, returns needs_input, not a nearest-guess presented as a match.
3. Exact-set disambiguation behaviour is preserved: where set is ambiguous, the matcher asks, it does not pick.
4. The demo still shows SAMPLE for any verdict; only the identity line may change, and it must be labelled as a test match until Step 4 passes.

**Owner tap required:** Fresh explicit yes for Step 2, including the named test set and the match threshold.

**Cost:** $0 or named and approved separately. No training run is part of this step. The $30 training cap on file is noted here only to make clear it is **not** spent by Step 2.

**Rollback:** Disable image matching in the demo; identity lookup returns to the existing identity-only behaviour. Demo stays SAMPLE.

### Step 3 — Tells engine wiring, front + back

**What it changes:**
- Wires the existing 5 pixel tells into the backend path, for front and back, so a test check can produce tell-by-tell evidence (which tells fired, which did not, and what was missing), without yet producing a shipped Likely verdict.
- Adds back-side handling only on the terms approved for that step: paired front/back for the same physical card, never a generic back paired to a specific card.

**What it does NOT change:**
- No shipped Likely verdict. Tell evidence in this step is for calibration and review only.
- No filing of genuine or help-text backs as fake backs, under any circumstance.
- No change to the tells rule itself in this step unless a separate tells-change step is approved and re-tested.
- No grade guess for slabs, and no slab-cert claim beyond what the slab checker skill already allows (never grader-verified on its own).

**Test to pass before moving on:**
1. For each named test card, the tell output lists each of the 5 tells, fired / not fired / not measurable, with the front and back evidence kept separate.
2. A front-only check does not silently borrow back evidence from another card.
3. A known fake in the test set and a known genuine in the test set both produce tell evidence that a reviewer can read without the code having to be trusted blindly.
4. The demo still shows SAMPLE / test-evidence labelling; no tester sees a Likely verdict from this step.

**Owner tap required:** Fresh explicit yes for Step 3, including the named test cards and the back-pairing rule for that step.

**Cost:** $0 or named and approved separately. No training, no GPU run, no Modal scaling is part of this step.

**Rollback:** Unwire the tells path; backend returns to identity-only plus Step 1–2 test behaviour, or to identity-only if the owner prefers. Demo stays SAMPLE.

### Step 4 — Calibration gate (the hard gate before any real verdict ships)

**What it changes:**
- Nothing ships. This step is measurement and review only: the Step 2 + Step 3 path is run over a calibration set, and the results are compared against ground truth (owner-verified genuine and owner-declared fake cards, with physical-card / photo ground truth winning over any database check).
- It produces a calibration report: per-identity and overall agreement, false-Likely rate, Inconclusive rate, and the exact conditions under which a Likely would be allowed.

**What it does NOT change:**
- No tester-facing real verdict is enabled by this step alone. Enabling one is a further, separate owner decision after the report is reviewed.
- No change to the median rule: 3–5 distinct phone copies of verified-genuine cards per identity, separate copies count, same SHA counts once. An identity is not median-ready until that rule is met.
- No quoting of a product accuracy figure (for example, never quote 29% or 100% as product accuracy) unless the calibration report itself supports it and the owner approves that wording.

**Test to pass before moving on (all must pass):**
1. Calibration set is named, with genuine and fake ground truth recorded before the run, not chosen after seeing results.
2. No cross-source Likely is produced by the test path during calibration except in the report, labelled as a test outcome.
3. The report states, plainly, which identities / conditions pass and which do not. A partial pass means a partial rollout only (only passing identities / conditions get a real verdict, everything else stays Inconclusive / SAMPLE).
4. A final examiner review (Latch role on file: verifier, never actor) has eyeballed the calibration report and the tester-facing wording before any real verdict is enabled.
5. If the gate fails, the plan stops here. No real verdict ships, no matter how good the upload or matching felt in Steps 1–3.

**Owner tap required:** Fresh explicit yes to (a) run calibration, (b) accept the calibration report, and (c) separately, enable any real verdict at all — and, if partial, exactly which identities / conditions. Those are three separate yeses, not one.

**Cost:** $0 or named and approved separately. Any model / compute cost for the calibration run must be named before the run, with the batch-by-batch approval rule on file: present identities, model, cost, cap, and artifact, and get approval before a large run. No training run is authorised by this step; the $30 training cap is a hard stop if training is ever proposed separately.

**Rollback:** No rollout. Demo stays SAMPLE, backend stays test-only. The calibration report is kept as a playground record, not as a shipped claim.

### Step 5 — Hosting move to G1, Modal prototype retired or stubbed

**What it changes:**
- Moves the proven backend path (only the steps that passed their tests, and only the real-verdict scope that passed Step 4, if any) from the temporary Modal prototype to the G1 machine after its arrival, with the same gates, logging, and retention notes re-applied on the new host.
- Retires the Modal prototype, or leaves it as a clearly-labelled test stub only if the owner explicitly says so. The default in this plan is retirement, not keeping two live backends.

**What it does NOT change:**
- No new verdict scope, no new identity pool, no new tells rule, and no new retention policy are introduced by the move itself. A move is not an excuse to widen scope.
- No change to the live site or live demo except through the normal, separately-approved live-push path. The demo in this plan stays playground until a live push is separately approved.
- No change to the owner's stated position on Modal: he does not plan to keep paying for it. If G1 is not ready, the backend stays test-only on Modal (or is shut down) — it does not become a permanent Modal product by drift.

**Test to pass before moving on:**
1. Health, upload, match, and (if enabled) verdict paths all pass the same Step 1–4 tests on G1, from Chrome on the owner's phone, before Modal is retired.
2. Modal shutdown (or stubbing) is verified: the old prototype URL no longer serves a live verdict path, or serves only the stub the owner approved.
3. The demo's backend URL / host setting is changed in one place, in playground first, and re-tested, before any live-push discussion.
4. A rollback host is named: if G1 fails, the demo reverts to SAMPLE and the backend reverts to test-only, not to a half-moved live service.

**Owner tap required:** Fresh explicit yes for Step 5, including the hosting choice (G1 as the home, Modal retired vs. stubbed), and a separate yes for any live push that follows it.

**Cost:** $0 or named and approved separately. No Modal overage, no Dedicated Endpoint, no scaled Shared usage is authorised by this plan. The Modal $130 grant limits are noted, not drawn on, by this plan.

**Rollback:** Keep the demo SAMPLE and the backend test-only on its previous host until G1 passes its tests. Do not leave a half-moved backend serving testers.

---

## 4. Risks and hard stops

These are not warnings to skim. Each one stops the step it applies to.

1. **No real Likely verdicts before calibration proof (Step 4).** Upload working, matching working, and tells firing are not calibration. A Likely that ships early is a dishonest verdict to a tester, even if it happens to be right once.
2. **No shipping cross-source Likely from the current 5 tells.** The tells are uncalibrated. That rule stands until Step 4 proves otherwise, for the specific identities / conditions in the report.
3. **No genuine or help-text backs filed as fake.** Back-pairing mistakes are a data-poisoning risk: one wrongly filed back can corrupt later calibration. Paired backs must be for the same physical card, verified, never guessed.
4. **No backend expansion code until a fresh explicit yes for that step.** This plan is not that yes. Plan approval ≠ Step 1 approval ≠ calibration approval ≠ rollout approval ≠ live-push approval.
5. **No spend without a separate ask.** This plan authorises $0. Any cost — Modal usage, compute, training, hosting, storage — must be named, capped, and approved before the step that would incur it. The $30 training cap and the Modal $130 grant limits are ceilings to respect, not budgets to spend.
6. **No leaving an endpoint live by accident.** Modal endpoints, test uploads, and G1 services must each have a named shutdown / stub decision in their step approval. "Temporary" does not mean "leave it running."
7. **No viewer-based proof.** Camera, keyboard, gate, and animation behaviour cannot be proven in the Muse viewer. Steps 1–5 must be tested in Chrome on the owner's phone (or another real browser the owner names) before they count as passed.
8. **No live-site change by drift.** Playground success does not move anything to cardcauldrontcg.com, to the live demo, or to any store. A live push needs its own explicit go-ahead, naming exactly what is pushed.
9. **No personal data or photo retention by default.** Each step approval must include where photos go, how long they are kept, and how they are deleted. If that note is missing, the step is not approved.
10. **No accuracy or "biggest database" claims.** Do not advertise the 37,369 identities, the 25,868 stock fronts, the 8,658 pool, or the 175 backs as a product claim, and do not quote an accuracy figure the calibration report does not support.

---

## 5. What success looks like, in plain language

If all gates pass, a tester in Chrome on a phone can:

1. Open the demo, sign in (gate + Guest fallback, local demo only), and go to Check.
2. Take a front photo and a back photo of a real card they hold.
3. Get either (a) a real, calibrated verdict for that identity / condition, with the evidence shown, or (b) a plain Inconclusive / needs_input naming what is missing — never a guessed Likely and never a SAMPLE verdict dressed up as real.
4. Know, from the screen itself, whether what they just saw was a real check or a sample.

If any gate fails, success is narrower: the demo stays SAMPLE, the backend stays test-only, and the failure is recorded honestly instead of being papered over with a verdict.

---

## 6. Owner decision checklist

Owner: please answer each line separately. A yes to one line is not a yes to another.

- [ ] **Plan reviewed?** — I have read this plan and understand it is plan-only, not a build approval.
- [ ] **Plan approved as a direction?** — Yes, this order (upload → match → tells → calibration gate → G1 move) is the direction, or: No / changes needed (list them).
- [ ] **Step 1 approved?** — Yes, build the photo upload endpoint (front + back, test-only, receipt only, no verdict), with the retention note: ___________. Or: No, not yet.
- [ ] **Step 2 approved?** — Yes, build identity matching from the image, with the named test set and threshold: ___________. Or: No, not yet.
- [ ] **Step 3 approved?** — Yes, wire the tells engine (front + back, test-evidence only, no shipped Likely). Or: No, not yet.
- [ ] **Step 4 approved?** — (a) Run calibration: Yes / No. (b) Accept the calibration report (after it exists): Yes / No. (c) Enable a real verdict, and exactly which identities / conditions: ___________. Or: No real verdict yet.
- [ ] **Step 5 / hosting choice?** — G1 as the long-term home: Yes / No. Modal prototype after the move: Retire / Leave as a test stub only / Decide later.
- [ ] **Live push?** — No live push is approved by this plan. A live push, if ever wanted, needs a separate yes naming exactly what is pushed: ___________.
- [ ] **Anything to change in this plan first?** — List it here, before any build step is approved.

**Do not present this plan as approved or built.** Until the checklist above is answered, the state remains: demo SAMPLE only, backend identity-only, no real verdict path, no backend expansion code.
