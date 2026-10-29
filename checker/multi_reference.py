"""Multi-reference median tells — playground only, $0, Oct 27, 2026.

Where an identity has more than one VERIFIED genuine reference, compare
the submitted scan against the MEDIAN tells across those references
(up to 5 per identity, first 5 in the order supplied), not just a
single photo. Where only 1 reference exists, use it singly and label
it single-reference. Where 0 exist, stay Inconclusive — this module
never invents a reference.

Median is taken per tell, using the same measurement as tells_v2:
  aspect_ratio: median of reference aspects
  mean_rgb / border_rgb: median per channel
  edge_density: median
  colour_histogram: median per bin (48 bins)
The verdict rule is tells_v2's rule, unchanged:
  >=2 strong mismatches -> Likely Counterfeit
  0 strong + >=3 matches -> Likely Genuine
  else -> Inconclusive
A median result is labelled pilot/uncalibrated until per-identity
calibration is shown, exactly like a single pilot reference. Median
does NOT make a verdict calibrated, official, or authentication.

References must already be verified by their own registry (canned
sourced-reals, verified TCGdex batch-1, verified owner-scan batch).
This module only opens the files it is given; it does not verify
provenance itself, and a caller that passes an unverified file is
misusing it — the checker passes only registry-verified files.
"""
import statistics
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tells_v2


def median_tells(user_path, reference_paths):
    """Return a tells_v2-compatible result dict, plus reference_count,
    reference_files, and reference_mode='median'|'single'."""
    refs = list(reference_paths or [])[:5]
    if not refs:
        raise ValueError("multi_reference: no reference paths supplied")
    user = tells_v2.measure(user_path)
    measures = [tells_v2.measure(p) for p in refs]
    # Median reference, per tell.
    med = {
        "aspect_ratio": statistics.median([m["aspect_ratio"] for m in measures]),
        "mean_rgb": [statistics.median([m["mean_rgb"][i] for m in measures]) for i in range(3)],
        "border_rgb": [statistics.median([m["border_rgb"][i] for m in measures]) for i in range(3)],
        "edge_density": statistics.median([m["edge_density"] for m in measures]),
        "histogram": [statistics.median([m["histogram"][i] for m in measures]) for i in range(len(measures[0]["histogram"]))],
    }
    tells = {}
    def tell(name, user_v, ref_v, diff, threshold):
        tells[name] = {"user": user_v, "reference": ref_v, "difference": round(diff, 4),
                       "threshold": threshold, "match": diff <= threshold,
                       "strong_mismatch": diff > threshold * 2}
    tell("aspect_ratio", user["aspect_ratio"], round(med["aspect_ratio"], 4),
         abs(user["aspect_ratio"] - med["aspect_ratio"]), tells_v2.THRESHOLDS["aspect_ratio"])
    tell("mean_rgb", user["mean_rgb"], [round(v, 1) for v in med["mean_rgb"]],
         tells_v2.rgb_diff(user["mean_rgb"], med["mean_rgb"]), tells_v2.THRESHOLDS["mean_rgb"])
    tell("border_rgb", user["border_rgb"], [round(v, 1) for v in med["border_rgb"]],
         tells_v2.rgb_diff(user["border_rgb"], med["border_rgb"]), tells_v2.THRESHOLDS["border_rgb"])
    tell("edge_density", user["edge_density"], round(med["edge_density"], 4),
         abs(user["edge_density"] - med["edge_density"]), tells_v2.THRESHOLDS["edge_density"])
    corr = tells_v2.hist_corr(user["histogram"], med["histogram"])
    tells["colour_histogram"] = {"user_correlation": round(corr, 4), "reference": 1.0,
        "difference": round(1 - corr, 4), "threshold": tells_v2.THRESHOLDS["colour_histogram"],
        "match": (1 - corr) <= tells_v2.THRESHOLDS["colour_histogram"],
        "strong_mismatch": (1 - corr) > tells_v2.THRESHOLDS["colour_histogram"] * 2}
    matches = sum(1 for t in tells.values() if t["match"])
    strong = sum(1 for t in tells.values() if t["strong_mismatch"])
    if strong >= 2:
        verdict = "Likely Counterfeit"
    elif strong == 0 and matches >= 3:
        verdict = "Likely Genuine"
    else:
        verdict = "Inconclusive"
    return {"user_image": user_path, "reference_image": refs[0] if len(refs) == 1 else "median_of_references",
            "reference_files": refs, "reference_count": len(refs),
            "reference_mode": "median" if len(refs) > 1 else "single",
            "reference_status": "pilot_uncalibrated",
            "user_size": user["size"],
            "tells": tells, "matches": matches, "strong_mismatches": strong,
            "verdict": verdict,
            "verdict_note": "Estimate only, never official, never guaranteed. "
                            "Median across verified references only; pilot/uncalibrated until per-identity calibration is shown."}
