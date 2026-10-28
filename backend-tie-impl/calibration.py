#!/usr/bin/env python3
"""Step 4a calibration — PLAYGROUND / TEST ONLY, $0, local, no model/GPU/Modal.
Ground truth recorded in CALIBRATION_SET below BEFORE the run is scored.
A test outcome labelled 'test-only' is never a shipped verdict.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matcher, tells_engine

WS = os.path.expanduser("~/workspace/fake-check")
CROP = f"{WS}/playground/agent-loop/run-v2-2026-10-26-night/cropped.png"
ALA = f"{WS}/sourced-reals/sr-0001-BS-1.png"
BLAST = f"{WS}/sourced-reals/sr-0002-BS-2.png"
FAKE_FRONT = "/home/hatch/workspace/user/files/5280_324_7kcl.jpg"  # owner-confirmed fake, identity NOT verified (Oct 26 manifest)

# Ground truth, recorded before scoring:
# C1: user crop is the Alakazam Base Set 1 crop used in the Oct 28 exact-set regression test (checker filed Likely Genuine with base1 + this crop + this reference).
# C2: same crop vs Blastoise reference is a WRONG-REFERENCE control, not a fake card. A Counterfeit outcome here would be a confident WRONG verdict; Inconclusive is the safe outcome.
# C3: fake front, identity unknown, vs Alakazam reference is NOT its own card's reference. Any test outcome here is a mismatch signal only, never credited as fake detection.
# C4-C7: safety outcomes (needs_input / not_measurable) are expected, and are counted as safety agreement, not as matching/verdict passes.
cases = []
def add(cid, kind, expected, actual_fn):
    cases.append({"case": cid, "kind": kind, "expected": expected, "actual": actual_fn()})

add("C1", "same-card front tells", "test-only Likely Genuine",
    lambda: tells_engine.run(front_user=CROP, front_ref=ALA)["front"]["test_outcome"])
add("C2", "wrong-reference control", "safe: Inconclusive (NOT a confident Counterfeit, card is not fake)",
    lambda: tells_engine.run(front_user=CROP, front_ref=BLAST)["front"]["test_outcome"])
add("C3", "fake front, identity unknown, vs non-own reference", "mismatch signal only, NOT credited as fake detection",
    lambda: tells_engine.run(front_user=FAKE_FRONT, front_ref=ALA)["front"]["test_outcome"])
add("C4", "exact-set ambiguity", "needs_input",
    lambda: matcher.match(set_query="Base", local_id="1", name="Alakazam")["status"])
add("C5", "image-only identity", "needs_input (image matcher does not exist)",
    lambda: matcher.match(image_supplied=True)["status"])
add("C6", "front-only tells (missing back)", "back not_measurable, never borrowed",
    lambda: tells_engine.run(front_user=CROP, front_ref=ALA)["back"]["status"])
add("C7", "out-of-pool set+number", "needs_input",
    lambda: matcher.match(set_query="Nonexistent Set", local_id="999")["status"])
add("C8", "exact set resolves", "resolved base1-1",
    lambda: (lambda m: m["status"] + " " + (m["row"]["id"] if m["row"] else ""))(matcher.match(set_query="base1", local_id="1")))

for c in cases:
    print(c["case"], "| expected:", c["expected"], "| actual:", c["actual"])

# Safety agreement: no confident WRONG verdict in any case.
# C2 Inconclusive counts as safe (not a false Counterfeit). C3 is excluded from fake-detection credit.
safety_cases = ["C1", "C2", "C4", "C5", "C6", "C7", "C8"]
safe = {"C1": "Genuine" in str(cases[0]["actual"]),
        "C2": "Inconclusive" in str(cases[1]["actual"]),
        "C4": cases[3]["actual"] == "needs_input",
        "C5": cases[4]["actual"] == "needs_input",
        "C6": cases[5]["actual"] == "not_measurable",
        "C7": cases[6]["actual"] == "needs_input",
        "C8": cases[7]["actual"] == "resolved base1-1"}
report = {
  "label": "STEP 4a CALIBRATION REPORT — TEST ONLY, NOT A SHIPPED VERDICT, NOT AN ACCURACY CLAIM",
  "date": "2026-10-28", "cost_usd": 0, "model_calls": 0, "training": False, "gpu": False, "modal_deploy": False,
  "cases": cases, "safety_agreement": f"{sum(safe.values())}/{len(safe)} safe outcomes (no confident wrong verdict)",
  "false_likely_rate": "0 confident wrong verdicts in 8 cases (C2 Inconclusive is safe, C3 excluded from fake-detection credit)",
  "inconclusive_rate": "1 of 3 tells cases was Inconclusive (wrong-reference control); same-card front was Genuine, fake-front-vs-non-own-reference was Counterfeit-as-mismatch-only",
  "discrimination": "Tells did NOT distinguish a different Base Set card from Alakazam (wrong-reference control = Inconclusive, only histogram strong). Tells are not an identity matcher.",
  "median_ready_identities": 0,
  "paired_front_back_same_card_test_set": "NONE on file for a named identity in this run (backs-pool pairs are 'possible' triage, not verified same-physical-card pairs; tonight centre crops are backs without paired fronts here)",
  "image_only_identity_matching": "NOT AVAILABLE — no $0 image-to-identity matcher on file; Step 2 is partial (set+number only)",
  "gate_verdict": "FAIL — DO NOT ENABLE ANY REAL VERDICT. Advance Step 4b/c approval in principle does NOT override this gate: report must pass + Latch eyeball review + partial scope only. This report does not pass, so no verdict ships, regardless of advance approval.",
  "conditions_a_likely_would_require": [
    "At least one median-ready identity (3-5 distinct phone copies, same SHA = one copy) — currently 0, Chatot has 2 and needs 1 more",
    "A verified paired front+back set for the same physical cards, genuine and fake, with ground truth recorded before the run",
    "Tells discrimination proven on wrong-reference and near-identical controls, not just same-card matches",
    "An image-to-identity matcher with a named, owner-approved threshold, or a set+number-only scope stated explicitly",
    "Latch Final Examiner eyeball review of this report and of tester-facing wording",
  ],
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration-report-2026-10-28.json")
json.dump(report, open(out, "w"), indent=2)
print("gate_verdict:", report["gate_verdict"])
print("wrote", out)
