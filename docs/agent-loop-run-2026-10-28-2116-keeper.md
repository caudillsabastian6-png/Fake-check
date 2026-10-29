# AI loop keeper run — Wed Oct 28, 2026 ~9:16 PM ET

Job: ai-loop-keeper (every 6h until Nov 4, 2026 9:00 PM ET; still in window).
Mode: playground/local only, $0. No deploy, no publish, no post, no send,
no train, no spend beyond existing hackathon credits — and this run spent $0.

## Item worked: Q12 (Audit #25) — Score backs; wire persisted crops into back-pool scoring

Next buildable Tier 1 item in queue order: Q1/Q4/Q5/Q20/Q21 are owner-phone
gates, Q9 is gate-only, Q10/Q11 blocked steps were built in earlier Oct 28
keeper runs and sit on phone/Latch gates, Tier 5 waves and Q59's remaining
SAM crops are NOT started without a separate owner yes. The Q12 step built
in the 3:16 PM run (persisted $0 crops + calibration) named this wiring
and the histogram decision as its next step; this run does exactly that.

Skills checked first: back-pool-scoring, back-pool-median, tell-calibration
(custom skills). Their gates shaped the scope below: the scorer is a
diagnostic, not a shipped verdict engine; it is not wired into the checker;
no per-identity median is claimed (median-ready identities remain 0);
no threshold was retuned on the calibration data.

## Built (playground only)

- `playground/app-v2-merged/back_pool_score_crops.py` (new) — scores a
  card-only back crop against the PERSISTED $0 crops in
  `playground/back-pool-crops-2026-10-28/` (174 genuine; the 1 fake crop
  is never in the reference pool), with tells_v2:
  - Per-tell MEDIAN diff across the genuine pool, never best-of. The
    median per-pair match/strong counts are reported alongside, so the
    two median views are both visible (they differ on the fake — see below).
  - Leave-one-out: an input that is itself a persisted genuine crop is
    excluded from its own pool (reported as excluded_self_crop).
  - Input attestation: raw hand/carpet photos must not be scored; an
    input that is not a persisted pool crop is flagged
    (input_is_persisted_pool_crop=false).
  - Aspect gate: median aspect diff > 0.15 forces Inconclusive, because
    the input is probably not a card-only crop.
- Histogram decision (decided, not retuned): colour_histogram is
  INFORMATIONAL ONLY, excluded from the back-rule match/strong counts.
  Evidence from the Oct 28 calibration (15,051 genuine pairs): match
  55.1% at the generic 0.15 threshold, median diff 0.129, p90 0.311 —
  lighting/framing dominate this tell on backs. No new histogram
  threshold is set; the generic threshold is still shown for
  transparency. The back rule therefore uses 4 tells (aspect, mean_rgb,
  border_rgb, edge_density): Counterfeit if strong >= 2, Genuine if
  strong == 0 and matches >= 3 of 4, else Inconclusive.
- `playground/app-v2-merged/test_back_pool_score_crops.py` (new, 6 checks,
  synthetic measures only, no image I/O): histogram-strong-alone does not
  block Genuine, 2 calibrated strong = Counterfeit, aspect gate overrides
  Counterfeit to Inconclusive, 1 calibrated strong = Inconclusive,
  median-not-best-of, empty pool = Inconclusive.
- Integration outputs (saved, not just printed):
  `playground/agent-loop/back-pool-score-genuine-2026-10-28.json` and
  `.../back-pool-score-fake-2026-10-28.json`.

## Verification (all $0, all PASS)

- Unit tests: `test_back_pool_score_crops.py` 6/6 PASS.
- Regressions: `test_back_pool_crops.py` 14/14 PASS,
  `test_why_measured_2026-10-28.py` PASS,
  `test_identity_exact_set_2026-10-28.py` PASS,
  `test_identity_wiring.py` PASS (canned Alakazam Genuine, Alakazam vs
  Charizard Inconclusive), `test_quality_median.py` ALL PASS.
  py_compile on the new files OK. Checker code untouched; verdict logic
  unchanged; no existing scorer edited (back-pool-score.py, which scores
  raw pool photos, is left as-is — the new crop scorer supersedes it for
  cropped backs only).
- Integration, genuine (Rolycoly crop 3640_350_c1d2.png, leave-one-out):
  173 scored, median diffs aspect 0.007, mean_rgb 5.3, border_rgb 11.5,
  edge_density 0.0066, histogram 0.065 — back rule 4/4 matches, 0 strong
  — pool diagnostic Likely Genuine. Runtime ~45s (174 tells_v2 measures).
- Integration, single fake (slab-framed Disco Charizard fake back crop):
  174 scored, median diffs aspect 0.1057 (strong), mean_rgb 27.1 (match),
  border_rgb 17.8 (match), edge_density 0.0191 (match), histogram 1.0733
  (strong, informational only) — back rule 3/4 matches, 1 strong —
  pool diagnostic Inconclusive. Under the generic all-5 rule the same
  median diffs would read Counterfeit (2 strong: aspect + histogram).
  The median per-pair counts tell a different story again (median
  matches 3.0, median strong 2.0) — the counts-of-median vs median-of-
  counts gap is reported in the output, not hidden.

## What this run did NOT do — and why the fake result is reported as-is

- No verdict was forced and none shipped: the fake back reads
  Inconclusive under the back rule, NOT Counterfeit. Forcing it to
  Counterfeit by counting the histogram would have contradicted the
  calibration evidence that decided the histogram's exclusion, and the
  fake is a single slab-framed sample whose aspect diff may reflect
  framing, not print fakery. One unmatched fake sample is NOT a fake
  boundary. This is evidence that back calibration is still OPEN, not a
  failure to be papered over.
- No new card verdict at all: the only "Likely Genuine" in this run is
  a pool diagnostic on an already-indexed genuine crop, and the fake
  result above. No cross-source Likely verdict shipped.
- No Baseten, Meta Spark, SAM, or Modal call: $0 local work only, so no
  cost log change. Baseten usage log remains spent ~$0.037 / remaining
  ~$99.96 (Oct 26 state, unchanged); Meta balance still not claimed exactly.
- No deploy, publish, post, send, train, or GitHub push from the loop.
- No demo link sent to the owner (loop hold stands).
- NOT wired into app_check_v2.py: the checker still scores a back
  against a single supplied back reference only. Wiring the pool
  diagnostic into a real check needs Latch re-exam plus a calibration
  gate, and is a separate decision — it is not claimed here.

## Queue status after this run

- Q12 stays P (partial) in the queue file, NOT promoted to I: the crop
  scorer is built and code-verified, but Latch re-exam is owed, the
  checker still uses its single back reference, and back calibration is
  still open (1 fake). Next step: Latch re-exam of the crop-pool scorer,
  then a decision on opt-in checker wiring (never default, never a
  shipped verdict). Queue file updated with this run's evidence.
- Next keeper run: take the next unbuilt in-scope item in queue order
  (Tier 1 first), or a fresh source-matched agent_loop_v2 check if the
  queue item is not runnable — do not start Tier 5 category waves
  without a separate owner yes, and do not start Q59's remaining SAM
  crops without owner spend yes.

## Cost / blocker for Sabastian

- Cost: $0. Blocker: none from this run. Item needing Sabastian: none —
  Latch re-exam and the checker-wiring decision are crew gates, not
  owner taps. Per the body's reporting rule this run stays quiet unless
  the main agent judges the completed queue step worth surfacing: it is
  a completed queue step (Q12 wiring + histogram decision), not a new
  verdict.
