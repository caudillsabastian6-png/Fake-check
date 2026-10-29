#!/usr/bin/env python3
"""Tests for back_pool_score_crops — PLAYGROUND ONLY, Oct 28, 2026.

Synthetic measures only (no image I/O), so the suite stays fast;
real-crop integration is exercised via the CLI in the keeper run
report, not here. Rules under test:
  - histogram is informational only: a strong histogram diff alone
    (or with one calibrated strong) must NOT make Counterfeit, and
    with all 4 calibrated tells matching the back rule is Genuine
    even when histogram is strong (generic all-5 rule would say
    Inconclusive on that 1 strong).
  - 2 calibrated strong diffs -> Counterfeit, histogram irrelevant.
  - aspect median diff > 0.15 -> Inconclusive via the aspect gate,
    even with 2 calibrated strong diffs (crop probably not card-only).
  - leave-one-out is a caller-side exclusion: score_from_measures
    scores exactly the pool it is given, so a test pool of 3 measures
    reports genuine_pool_scored == 3.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Standalone fix (Oct 29, 2026): the modules under test live in ../checker.
sys.path.insert(0, os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "checker")))

import back_pool_score_crops as bpc  # noqa: E402


def measure(aspect=0.80, mean=(100, 100, 100), border=(90, 90, 90),
            edge=0.05, hist=None):
    # A flat histogram (all bins equal) correlates 1.0 with itself and
    # ~0 with a single-spike histogram; tests build hist explicitly
    # where the histogram diff matters, via hist_corr behaviour.
    return {"aspect_ratio": aspect, "mean_rgb": list(mean),
            "border_rgb": list(border), "edge_density": edge,
            "histogram": hist if hist is not None else [1 / 48.0] * 48}


def pool_of(ref):
    return [("ref%d" % i, ref) for i in range(3)]


class TestBackPoolScoreCrops(unittest.TestCase):
    def test_histogram_strong_alone_does_not_block_genuine(self):
        # User histogram is a single spike; refs are flat -> hist diff
        # ~1.0 (strong). All calibrated tells identical -> back Genuine,
        # generic all-5 rule Inconclusive (1 strong).
        user = measure(hist=[1.0] + [0.0] * 47)
        ref = measure()
        out = bpc.score_from_measures(user, pool_of(ref))
        self.assertEqual(out["pool_diagnostic"], "Likely Genuine")
        self.assertEqual(out["back_rule_matches_of_4"], 4)
        self.assertEqual(out["back_rule_strong_of_4"], 0)
        self.assertTrue(out["colour_histogram_informational"]
                        ["excluded_from_back_counts"])
        self.assertEqual(out["generic_rule_for_comparison"]
                         ["diagnostic_if_all_5_counted"], "Inconclusive")

    def test_two_calibrated_strong_is_counterfeit(self):
        user = measure(aspect=0.95, mean=(200, 200, 200))  # aspect + mean strong
        ref = measure()
        out = bpc.score_from_measures(user, pool_of(ref))
        self.assertEqual(out["pool_diagnostic"], "Likely Counterfeit")
        self.assertEqual(out["back_rule_strong_of_4"], 2)

    def test_aspect_gate_overrides_counterfeit(self):
        user = measure(aspect=1.05, mean=(200, 200, 200))  # aspect diff 0.25
        ref = measure()
        out = bpc.score_from_measures(user, pool_of(ref))
        self.assertTrue(out["aspect_gate_hit"])
        self.assertEqual(out["pool_diagnostic"], "Inconclusive")

    def test_one_calibrated_strong_is_inconclusive(self):
        user = measure(mean=(200, 200, 200))  # mean diff 100 > 60 = strong
        ref = measure()
        out = bpc.score_from_measures(user, pool_of(ref))
        self.assertEqual(out["back_rule_strong_of_4"], 1)
        self.assertEqual(out["pool_diagnostic"], "Inconclusive")

    def test_median_not_best_of(self):
        # Two refs identical to the user, one far away: median diff is
        # still 0 (majority match), which is the point of the median —
        # but the per-pair median counts are also reported, and the
        # pool size is exactly what was given (no hidden exclusion).
        user = measure()
        pool = [("a", measure()), ("b", measure()),
                ("c", measure(aspect=0.95, mean=(200, 200, 200)))]
        out = bpc.score_from_measures(user, pool)
        self.assertEqual(out["genuine_pool_scored"], 3)
        self.assertEqual(out["median_diffs"]["aspect_ratio"], 0.0)
        self.assertEqual(out["pool_diagnostic"], "Likely Genuine")

    def test_empty_pool_is_inconclusive(self):
        out = bpc.score_from_measures(measure(), [])
        self.assertEqual(out["pool_diagnostic"], "Inconclusive")
        self.assertEqual(out["genuine_pool_scored"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
