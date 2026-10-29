#!/usr/bin/env python3
"""Score a cropped back against the persisted $0 back-pool crops.

PLAYGROUND ONLY, Oct 28, 2026. Q12 (Audit #25) wiring step.

What this is: the diagnostic successor to playground/back-pool-score.py,
which scored RAW pool photos. This scorer scores against the PERSISTED
$0 crops in playground/back-pool-crops-2026-10-28/ (175/175 crop_v2,
Oct 28 keeper run), measured with the same tells_v2 code path as the
calibration. A cropped-vs-cropped comparison only — a raw hand/carpet
photo must NEVER be scored here; the caller attests the input is a
card-only crop, and an input that is not one of the persisted crops
is flagged as such in the output.

What this is NOT (hard limits, per the back-pool skills):
  - NOT a shipped verdict engine. The output field is pool_diagnostic,
    never "verdict". Back-pool calibration is still OPEN: the pool has
    exactly ONE fake back, unmatched, so no fake boundary is calibrated
    and no threshold was retuned in this run.
  - NOT wired into app_check_v2.py. The checker still scores a back
    against a single supplied back reference only. Wiring this pool
    diagnostic into a real check needs a separate Latch re-exam and a
    calibration gate — it is not claimed here.
  - NOT a per-identity median. The pool mixes identities (backs are
    mostly uniform); this is a back-design/print diagnostic across
    the genuine pool, never identity proof, never a median-ready claim
    for any identity (median-ready identities remain 0 per the
    Oct 27 other-copies search).
  - NOT best-of. The reported diff per tell is the MEDIAN across the
    genuine pool, and the median per-pair match/strong counts are
    reported alongside it so a single outlier cannot hide.

Histogram decision (Oct 28, from the Oct 28 calibration over 15,051
genuine-vs-genuine cropped pairs — NOT a retune on a new threshold):
  colour_histogram is reported as INFORMATIONAL ONLY and is excluded
  from the back-rule match/strong counts. Evidence: genuine match rate
  55.1% at the generic 0.15 threshold, median genuine diff 0.129,
  p90 0.311 — lighting and framing move back histograms far more than
  the other tells, so letting it drive a Counterfeit diagnostic would
  flag genuine backs. No new histogram threshold is set here; the
  generic threshold is still shown for transparency, and the single
  fake sample's histogram diff (1.0907 vs the genuine median) is
  reported, not treated as a boundary. The back rule therefore uses
  the 4 remaining tells: aspect_ratio, mean_rgb, border_rgb,
  edge_density. Genuine requires strong_back == 0 and matches_back
  >= 3 of those 4; Counterfeit requires strong_back >= 2; else
  Inconclusive. Aspect gate (back-pool-scoring skill): if the median
  aspect diff exceeds 0.15, the diagnostic is Inconclusive regardless
  of the other tells, because the input is probably not a card-only
  crop.

Leave-one-out: if the input file is itself one of the persisted
genuine crops (same basename / same resolved path), that crop is
excluded from its own pool, so an in-pool test cannot self-match.
The exclusion is reported; pool_scored is the count after exclusion.

Usage:
  python3 back_pool_score_crops.py <back_crop.png>
      [--crops DIR] [--out FILE]
"""
import argparse
import csv
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tells_v2  # noqa: E402

DEFAULT_CROPS = os.path.expanduser(
    "~/workspace/fake-check/playground/back-pool-crops-2026-10-28")
CALIBRATED_TELLS = ["aspect_ratio", "mean_rgb", "border_rgb", "edge_density"]
ALL_TELLS = CALIBRATED_TELLS + ["colour_histogram"]
ASPECT_GATE = 0.15


def diffs(u, v):
    return {
        "aspect_ratio": abs(u["aspect_ratio"] - v["aspect_ratio"]),
        "mean_rgb": tells_v2.rgb_diff(u["mean_rgb"], v["mean_rgb"]),
        "border_rgb": tells_v2.rgb_diff(u["border_rgb"], v["border_rgb"]),
        "edge_density": abs(u["edge_density"] - v["edge_density"]),
        "colour_histogram": 1 - tells_v2.hist_corr(u["histogram"], v["histogram"]),
    }


def counts_from_diffs(d):
    """(matches, strong) under the generic tells_v2 thresholds."""
    th = tells_v2.THRESHOLDS
    matches = sum(1 for k, v in d.items() if v <= th[k])
    strong = sum(1 for k, v in d.items() if v > th[k] * 2)
    return matches, strong


def rule_from_median_diffs(median_diffs):
    """Back rule from per-tell median diffs; histogram excluded.

    Returns (diagnostic, matches_back, strong_back, aspect_gate_hit).
    """
    th = tells_v2.THRESHOLDS
    matches_back = sum(1 for k in CALIBRATED_TELLS
                       if median_diffs[k] <= th[k])
    strong_back = sum(1 for k in CALIBRATED_TELLS
                      if median_diffs[k] > th[k] * 2)
    aspect_gate_hit = median_diffs["aspect_ratio"] > ASPECT_GATE
    if aspect_gate_hit:
        return "Inconclusive", matches_back, strong_back, True
    if strong_back >= 2:
        return "Likely Counterfeit", matches_back, strong_back, False
    if strong_back == 0 and matches_back >= 3:
        return "Likely Genuine", matches_back, strong_back, False
    return "Inconclusive", matches_back, strong_back, False


def score_from_measures(user_measure, pool_measures):
    """Core scoring over already-measured images (unit-testable, no I/O).

    pool_measures: list of (label, measure) for genuine crops.
    Returns the diagnostic dict (without file paths).
    """
    per_pair = []
    per_tell = {k: [] for k in ALL_TELLS}
    for _label, ref in pool_measures:
        d = diffs(user_measure, ref)
        per_pair.append(d)
        for k in ALL_TELLS:
            per_tell[k].append(d[k])
    if not per_pair:
        return {"genuine_pool_scored": 0, "pool_diagnostic": "Inconclusive",
                "note": "Empty genuine pool — nothing scored."}
    median_diffs = {k: round(statistics.median(v), 4)
                    for k, v in per_tell.items()}
    pair_matches = [counts_from_diffs(d)[0] for d in per_pair]
    pair_strong = [counts_from_diffs(d)[1] for d in per_pair]
    diagnostic, matches_back, strong_back, gate = rule_from_median_diffs(
        median_diffs)
    generic_matches, generic_strong = counts_from_diffs(median_diffs)
    th = tells_v2.THRESHOLDS
    hist = median_diffs["colour_histogram"]
    return {
        "genuine_pool_scored": len(per_pair),
        "median_diffs": median_diffs,
        "median_pair_matches": statistics.median(pair_matches),
        "median_pair_strong": statistics.median(pair_strong),
        "back_rule_matches_of_4": matches_back,
        "back_rule_strong_of_4": strong_back,
        "aspect_gate_hit": gate,
        "colour_histogram_informational": {
            "median_diff": hist,
            "generic_threshold": th["colour_histogram"],
            "match_at_generic_threshold": hist <= th["colour_histogram"],
            "strong_at_generic_threshold": hist > th["colour_histogram"] * 2,
            "excluded_from_back_counts": True,
            "reason": "Oct 28 calibration: genuine match rate 55.1%, "
                      "median diff 0.129, p90 0.311 — lighting/framing "
                      "dominate this tell on backs; it must not drive "
                      "a Counterfeit diagnostic. No new threshold set.",
        },
        "generic_rule_for_comparison": {
            "matches_of_5": generic_matches,
            "strong_of_5": generic_strong,
            "diagnostic_if_all_5_counted":
                ("Likely Counterfeit" if generic_strong >= 2 else
                 "Likely Genuine" if generic_strong == 0
                 and generic_matches >= 3 else "Inconclusive"),
        },
        "pool_diagnostic": diagnostic,
        "diagnostic_note": "Back-design/print diagnostic only, NOT a "
                           "verdict, NOT identity proof, NOT wired into "
                           "the checker. Median across the genuine pool, "
                           "not best-of. Calibration still open: exactly "
                           "one unmatched fake back in the pool, so no "
                           "fake boundary is claimed.",
    }


def load_genuine_crops(crops_dir):
    manifest = list(csv.DictReader(
        open(os.path.join(crops_dir, "manifest.csv"))))
    pool = []
    for m in manifest:
        if m["authenticity"] == "fake" or m["error"]:
            continue
        p = os.path.join(crops_dir, m["crop_file"])
        if os.path.exists(p):
            pool.append((m["crop_file"], p))
    return pool


def score(user_path, crops_dir=DEFAULT_CROPS):
    user_abs = os.path.realpath(user_path)
    user_base = os.path.basename(user_path)
    pool = load_genuine_crops(crops_dir)
    excluded_self = 0
    pool_measures = []
    for crop_file, p in pool:
        if crop_file == user_base or os.path.realpath(p) == user_abs:
            excluded_self += 1
            continue
        pool_measures.append((crop_file, tells_v2.measure(p)))
    result = score_from_measures(tells_v2.measure(user_path), pool_measures)
    result.update({
        "user_back": user_path,
        "input_is_persisted_pool_crop": excluded_self > 0,
        "input_attestation": "Caller attests the input is a card-only "
                             "crop. Raw hand/carpet photos must not be "
                             "scored; an input that is not a persisted "
                             "pool crop is flagged by "
                             "input_is_persisted_pool_crop=false.",
        "excluded_self_crop": excluded_self,
        "crops_dir": crops_dir,
    })
    # Keep file fields first for readability.
    ordered = {"user_back": result["user_back"],
               "crops_dir": result["crops_dir"],
               "input_is_persisted_pool_crop":
                   result["input_is_persisted_pool_crop"],
               "excluded_self_crop": result["excluded_self_crop"]}
    ordered.update({k: v for k, v in result.items() if k not in ordered})
    ordered["input_attestation"] = result["input_attestation"]
    return ordered


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("back_crop")
    ap.add_argument("--crops", default=DEFAULT_CROPS)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    result = score(a.back_crop, a.crops)
    text = json.dumps(result, indent=2)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
