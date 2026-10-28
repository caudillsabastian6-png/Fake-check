"""Step 3 tells engine wrapper — PLAYGROUND / TEST ONLY, Oct 28, 2026.
Wraps playground/app-v2-merged/tells_v2.py measure() + thresholds.
Front and back are measured SEPARATELY, against their OWN reference only.
A missing back is 'not_measurable', never borrowed from another card.
No shipped verdict: test_outcome is labelled test evidence only and
shipped_verdict is always None in this impl.
"""
import importlib.util, os, sys
_SRC = os.path.expanduser("~/workspace/fake-check/playground/app-v2-merged/tells_v2.py")
_spec = importlib.util.spec_from_file_location("tells_v2_impl", _SRC)
_mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
THRESHOLDS = dict(_mod.THRESHOLDS)

def _compare(user_path, ref_path):
    u = _mod.measure(user_path); r = _mod.measure(ref_path)
    tells = {}
    def tell(name, uv, rv, diff, thr):
        tells[name] = {"user": uv, "reference": rv, "difference": round(diff, 4),
                       "threshold": thr, "match": diff <= thr, "strong_mismatch": diff > thr * 2}
    tell("aspect_ratio", u["aspect_ratio"], r["aspect_ratio"],
         abs(u["aspect_ratio"] - r["aspect_ratio"]), THRESHOLDS["aspect_ratio"])
    tell("mean_rgb", u["mean_rgb"], r["mean_rgb"],
         _mod.rgb_diff(u["mean_rgb"], r["mean_rgb"]), THRESHOLDS["mean_rgb"])
    tell("border_rgb", u["border_rgb"], r["border_rgb"],
         _mod.rgb_diff(u["border_rgb"], r["border_rgb"]), THRESHOLDS["border_rgb"])
    tell("edge_density", u["edge_density"], r["edge_density"],
         abs(u["edge_density"] - r["edge_density"]), THRESHOLDS["edge_density"])
    corr = _mod.hist_corr(u["histogram"], r["histogram"])
    tells["colour_histogram"] = {"user_correlation": round(corr, 4), "reference": 1.0,
        "difference": round(1 - corr, 4), "threshold": THRESHOLDS["colour_histogram"],
        "match": (1 - corr) <= THRESHOLDS["colour_histogram"],
        "strong_mismatch": (1 - corr) > THRESHOLDS["colour_histogram"] * 2}
    matches = sum(1 for t in tells.values() if t["match"])
    strong = sum(1 for t in tells.values() if t["strong_mismatch"])
    if strong >= 2:
        test_outcome = "test-only: Likely Counterfeit (tells rule, NOT shipped)"
    elif strong == 0 and matches >= 3:
        test_outcome = "test-only: Likely Genuine (tells rule, NOT shipped)"
    else:
        test_outcome = "test-only: Inconclusive"
    return {"tells": tells, "matches": matches, "strong_mismatches": strong,
            "user_size": u["size"], "reference_size": r["size"],
            "test_outcome": test_outcome, "shipped_verdict": None}

def run(front_user=None, front_ref=None, back_user=None, back_ref=None):
    out = {"label": "TEST EVIDENCE ONLY — NOT A SHIPPED VERDICT", "shipped_verdict": None}
    if front_user and front_ref:
        out["front"] = _compare(front_user, front_ref)
    else:
        out["front"] = {"status": "not_measurable", "reason": "front user image or front reference missing — nothing measured, nothing borrowed"}
    if back_user and back_ref:
        out["back"] = _compare(back_user, back_ref)
    elif back_user and not back_ref:
        out["back"] = {"status": "not_measurable", "reason": "back user image supplied but no back reference for this card — back NOT scored, never paired with a generic back"}
    elif back_ref and not back_user:
        out["back"] = {"status": "not_measurable", "reason": "back missing — reported as missing, never paired with a generic or wrong-side image"}
    else:
        out["back"] = {"status": "not_measurable", "reason": "no back user image and no back reference"}
    # Combined test outcome is for the calibration report only.
    f = out["front"]; b = out["back"]
    if isinstance(f, dict) and "test_outcome" in f and isinstance(b, dict) and "test_outcome" in b:
        if "Counterfeit" in f["test_outcome"] or "Counterfeit" in b["test_outcome"]:
            out["combined_test_outcome"] = "test-only: Likely Counterfeit (front OR back, NOT shipped)"
        elif "Genuine" in f["test_outcome"] and "Genuine" in b["test_outcome"]:
            out["combined_test_outcome"] = "test-only: Likely Genuine (front AND back, NOT shipped)"
        else:
            out["combined_test_outcome"] = "test-only: Inconclusive"
    else:
        out["combined_test_outcome"] = "test-only: Inconclusive (a side was not measurable)"
    return out
