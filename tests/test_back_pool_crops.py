#!/usr/bin/env python3
"""Tests for back_pool_crops.py — PLAYGROUND ONLY, Oct 28, 2026. $0.

Covers: centre-fallback geometry, tells diff/rule helpers, and a
small synthetic calibration (2 identical genuine crops + 1 different
genuine + 1 fake) so the calibration report shape is proven without
waiting for the full 175-crop batch. No verdict on a real card here:
synthetic solid-colour images only.
"""
import csv
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image  # noqa: E402

import back_pool_crops as bpc  # noqa: E402
import tells_v2  # noqa: E402

PASS = []


def check(name, cond):
    PASS.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name)


def solid(path, rgb, size=(100, 140)):
    Image.new("RGB", size, rgb).save(path)


def main():
    # 1. Centre-fallback geometry: central 85% x 80%, centred.
    box = bpc.centre_box(1536, 2048)
    check("centre_box width 85%", box[2] - box[0] == int(1536 * 0.85))
    check("centre_box height 80%", box[3] - box[1] == int(2048 * 0.80))
    check("centre_box centred",
          box[0] == (1536 - int(1536 * 0.85)) // 2
          and box[1] == (2048 - int(2048 * 0.80)) // 2)

    # 2. Diff/rule helpers on synthetic measures.
    m = {"aspect_ratio": 0.8, "mean_rgb": [100, 100, 100],
         "border_rgb": [90, 90, 90], "edge_density": 0.1,
         "histogram": [0.0] * 48}
    m["histogram"][0] = 1.0
    d = bpc._diffs(m, m)
    check("identical diffs all zero", all(v == 0 for v in d.values()))
    check("identical rule Likely Genuine", bpc._rule(d) == "Likely Genuine")
    far = dict(m)
    far["mean_rgb"] = [200, 200, 200]  # diff 100 > 30*2 -> strong
    far["border_rgb"] = [200, 200, 200]  # diff 110 > 40*2 -> strong
    d2 = bpc._diffs(m, far)
    check("two strong -> Counterfeit",
          bpc._rule(d2) == "Likely Counterfeit")

    # 3. Synthetic calibration end-to-end.
    with tempfile.TemporaryDirectory() as td:
        rows = [
            ("g1.png", "genuine-owner-listing", (200, 30, 30)),
            ("g2.png", "genuine-owner-listing", (200, 30, 30)),
            ("g3.png", "genuine-owner-listing", (30, 30, 200)),
            ("f1.png", "fake", (30, 200, 30)),
        ]
        with open(os.path.join(td, "manifest.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "back_file", "authenticity", "front_card_name",
                "front_pair_file", "crop_file", "branch", "box",
                "crop_size", "aspect", "error"])
            w.writeheader()
            for name, auth, rgb in rows:
                solid(os.path.join(td, name), rgb)
                w.writerow({"back_file": name + ".jpg", "authenticity": auth,
                            "front_card_name": "synthetic",
                            "front_pair_file": "", "crop_file": name,
                            "branch": "crop_v2", "box": "0|0|100|140",
                            "crop_size": "100x140", "aspect": 0.7143,
                            "error": ""})
        out = os.path.join(td, "cal.json")
        rc = bpc.calibrate(td, out)
        rep = json.load(open(out))
        check("calibrate exit 0", rc == 0)
        check("genuine measured 3", rep["genuine_crops_measured"] == 3)
        check("fake measured 1", rep["fake_crops_measured"] == 1)
        check("genuine pairs 3", rep["genuine_pairs"] == 3)
        check("tell stats cover 5 tells",
              set(rep["tell_stats"]) == set(tells_v2.THRESHOLDS))
        check("identical genuine pair is Genuine",
              rep["genuine_pair_rule_outcomes"]["Likely Genuine"] >= 1)
        check("fake report is single-sample, labelled",
              len(rep["fake_vs_genuine_median"]) == 1
              and "Single fake sample" in
              rep["fake_vs_genuine_median"][0]["note"])
        check("rule rates sum to 1",
              abs(sum(rep["genuine_pair_rule_rates"].values()) - 1.0) < 1e-9)

    failed = [n for n, ok in PASS if not ok]
    print(f"{len(PASS) - len(failed)}/{len(PASS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
