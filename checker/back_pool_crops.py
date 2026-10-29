#!/usr/bin/env python3
"""Back-pool $0 crops + back-tells calibration — PLAYGROUND ONLY, Oct 28, 2026.

Q12 (Audit #25) next step: persist $0 crops for the pool backs and
calibrate back tells. SAM crops are NOT used here (no spend, no new
SAM call); the 10 SAM pilot crops stay a separate, labelled set.

Crop method, in order per pool row:
  1. crop_v2.detect (smoothed-colour mask + 10% inset, $0 on-device,
     measured on fronts in Pip Job B). On PASS, that box is the crop.
  2. On REFUSE, a geometric centre crop (central 85% width x 80%
     height — the proportion of the SAM pilot crops against their
     1536x2048 sources). Labelled "centre-fallback" in the manifest,
     NEVER claimed to be a verified card-only crop.
  3. On any error, the row is recorded as failed and skipped, never
     silently filled with another row's crop.

A back score is a back-design/print score, NEVER identity proof
(backs are mostly uniform; the pool CSV says so per row).

Calibration (run with --calibrate after cropping):
  Measures tells_v2 on every persisted GENUINE crop, then reports the
  genuine-vs-genuine pairwise difference distribution per tell
  (median, p90, match rate under tells_v2.THRESHOLDS) and the rule
  outcome distribution (Likely Genuine / Inconclusive /
  Likely Counterfeit) if those thresholds were applied to
  genuine-vs-genuine pairs. This shows whether the generic front
  thresholds fit cropped backs at all — it does NOT retune thresholds
  to pass a test, and it does NOT set a fake threshold: the pool has
  exactly ONE fake back, so fake separation is reported as a single
  sample against the genuine median, never as a calibrated boundary.

Usage:
  python3 back_pool_crops.py --crop [--out DIR] [--limit N]
  python3 back_pool_crops.py --calibrate [--crops DIR] [--out FILE]
"""
import argparse
import csv
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

POOL = os.path.expanduser("~/workspace/fake-check/databases/backs-pool-2026-10-27.csv")
DEFAULT_OUT = os.path.expanduser(
    "~/workspace/fake-check/playground/back-pool-crops-2026-10-28")

from PIL import Image  # noqa: E402

import crop_v2  # noqa: E402
import tells_v2  # noqa: E402


def centre_box(w, h):
    """Central 85% width x 80% height, matching SAM pilot proportions."""
    cw, ch = int(w * 0.85), int(h * 0.80)
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    return [x0, y0, x0 + cw, y0 + ch]


def crop_pool(out_dir, limit=None):
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, "manifest.csv")
    rows = list(csv.DictReader(open(POOL)))
    if limit:
        rows = rows[:limit]
    manifest = []
    for r in rows:
        src = os.path.expanduser(r["source_path"])
        stem = os.path.splitext(r["back_file"])[0]
        dst = os.path.join(out_dir, stem + ".png")
        entry = {"back_file": r["back_file"], "authenticity": r["authenticity"],
                 "front_card_name": r["front_card_name"],
                 "front_pair_file": r["front_pair_file"],
                 "crop_file": os.path.basename(dst), "branch": None,
                 "box": None, "crop_size": None, "aspect": None, "error": None}
        try:
            with Image.open(src) as im:
                w, h = im.size
                det = crop_v2.detect(src)
            if det.get("status") == "PASS" and det.get("box"):
                box, branch = det["box"], "crop_v2"
            else:
                box, branch = centre_box(w, h), "centre-fallback"
            with Image.open(src).convert("RGB") as im:
                crop = im.crop(box)
                crop.save(dst)
                cw, ch = crop.size
            entry.update({"branch": branch, "box": "|".join(map(str, box)),
                          "crop_size": f"{cw}x{ch}",
                          "aspect": round(cw / ch, 4)})
        except Exception as e:  # recorded, never silently substituted
            entry["error"] = f"{type(e).__name__}: {e}"
        manifest.append(entry)
        print(f"{r['back_file']}: {entry['branch']} {entry['crop_size']} "
              f"{entry['error'] or ''}".rstrip())
    with open(manifest_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0].keys()))
        w.writeheader()
        w.writerows(manifest)
    ok = sum(1 for m in manifest if not m["error"])
    print(f"cropped {ok}/{len(manifest)} -> {out_dir}")
    print(f"manifest: {manifest_path}")
    return 0 if ok == len(manifest) else 1


def _diffs(u, v):
    return {
        "aspect_ratio": abs(u["aspect_ratio"] - v["aspect_ratio"]),
        "mean_rgb": tells_v2.rgb_diff(u["mean_rgb"], v["mean_rgb"]),
        "border_rgb": tells_v2.rgb_diff(u["border_rgb"], v["border_rgb"]),
        "edge_density": abs(u["edge_density"] - v["edge_density"]),
        "colour_histogram": 1 - tells_v2.hist_corr(u["histogram"], v["histogram"]),
    }


def _rule(diffs):
    th = tells_v2.THRESHOLDS
    matches = sum(1 for k, d in diffs.items() if d <= th[k])
    strong = sum(1 for k, d in diffs.items() if d > th[k] * 2)
    if strong >= 2:
        return "Likely Counterfeit"
    if strong == 0 and matches >= 3:
        return "Likely Genuine"
    return "Inconclusive"


def _pct(values, q):
    s = sorted(values)
    if not s:
        return None
    i = min(len(s) - 1, max(0, int(math.ceil(q * len(s))) - 1))
    return round(s[i], 4)


def calibrate(crops_dir, out_path):
    manifest = list(csv.DictReader(
        open(os.path.join(crops_dir, "manifest.csv"))))
    genuine, fake = [], []
    for m in manifest:
        if m["error"]:
            continue
        p = os.path.join(crops_dir, m["crop_file"])
        if not os.path.exists(p):
            continue
        (genuine if m["authenticity"] != "fake" else fake).append((m, p))
    print(f"measuring {len(genuine)} genuine + {len(fake)} fake crops ...")
    g_measures = []
    for m, p in genuine:
        g_measures.append((m, tells_v2.measure(p)))
    # Pairwise genuine-vs-genuine diffs (measures cached, pairs are cheap).
    per_tell = {k: [] for k in tells_v2.THRESHOLDS}
    rule_counts = {"Likely Genuine": 0, "Inconclusive": 0, "Likely Counterfeit": 0}
    pairs = 0
    for i in range(len(g_measures)):
        for j in range(i + 1, len(g_measures)):
            d = _diffs(g_measures[i][1], g_measures[j][1])
            for k, v in d.items():
                per_tell[k].append(v)
            rule_counts[_rule(d)] += 1
            pairs += 1
    th = tells_v2.THRESHOLDS
    tell_stats = {}
    for k, vals in per_tell.items():
        tell_stats[k] = {
            "pairs": len(vals),
            "median_diff": round(statistics.median(vals), 4) if vals else None,
            "p90_diff": _pct(vals, 0.90),
            "threshold": th[k],
            "match_rate": round(
                sum(1 for v in vals if v <= th[k]) / len(vals), 4) if vals else None,
            "strong_rate": round(
                sum(1 for v in vals if v > th[k] * 2) / len(vals), 4) if vals else None,
        }
    # The single fake back vs the genuine median measure (one sample only).
    fake_report = []
    if fake and g_measures:
        med = {}
        for k in ("aspect_ratio", "edge_density"):
            med[k] = statistics.median(m[1][k] for m in g_measures)
        for k in ("mean_rgb", "border_rgb"):
            med[k] = [statistics.median(m[1][k][c] for m in g_measures)
                      for c in range(3)]
        med["histogram"] = [statistics.median(m[1]["histogram"][c]
                                              for m in g_measures)
                            for c in range(len(g_measures[0][1]["histogram"]))]
        for m, p in fake:
            d = _diffs(tells_v2.measure(p), med)
            fake_report.append({"back_file": m["back_file"],
                                "vs_genuine_median_diffs":
                                    {k: round(v, 4) for k, v in d.items()},
                                "rule_vs_median": _rule(d),
                                "note": "Single fake sample only — NOT a calibrated "
                                        "fake boundary."})
    report = {
        "crops_dir": crops_dir,
        "genuine_crops_measured": len(g_measures),
        "fake_crops_measured": len(fake),
        "genuine_pairs": pairs,
        "tell_stats": tell_stats,
        "genuine_pair_rule_outcomes": rule_counts,
        "genuine_pair_rule_rates": {
            k: round(v / pairs, 4) if pairs else None
            for k, v in rule_counts.items()},
        "fake_vs_genuine_median": fake_report,
        "interpretation": "Genuine-vs-genuine pairs show how much cropped "
                          "genuine backs vary among themselves (lighting, "
                          "framing, phone). A tell whose genuine match rate "
                          "is low is NOT calibrated for backs at the generic "
                          "threshold — it must not be used to call a back "
                          "Counterfeit. Back scores remain design/print "
                          "scores, never identity proof.",
    }
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crop", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--crops", default=None)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    if a.crop:
        return crop_pool(a.out or DEFAULT_OUT, a.limit)
    if a.calibrate:
        return calibrate(a.crops or DEFAULT_OUT,
                         a.out or os.path.join(
                             a.crops or DEFAULT_OUT,
                             "back-tells-calibration-2026-10-28.json"))
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
