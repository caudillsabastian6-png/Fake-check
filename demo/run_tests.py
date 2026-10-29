#!/usr/bin/env python3
"""Re-run the canonical V2 tests through app_check_v2.py into out/ (local, $0).

Standalone fix (Oct 29, 2026): this test needs three card photos — one
user crop and two reference photos. Card photos are NEVER shipped in
this pack, so on a clean clone the fixtures are absent and this script
SKIPs with the reason (exit 0) instead of failing on a workspace path.
To run it for real, drop local copies into demo/fixtures/ with the
names below (they stay out of the pack). The canned A/B results the
fixtures originally produced are committed as evidence in
tests/test-A-result.json / test-B-result.json at the pack root.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.normpath(os.path.join(HERE, "..", "checker", "app_check_v2.py"))
FIX = os.path.join(HERE, "fixtures")
CROP = os.path.join(FIX, "cropped.png")
REFS = {"Alakazam|Base|1": os.path.join(FIX, "sr-0001-BS-1.png"),
        "Charizard|Base|4": os.path.join(FIX, "sr-0004-BS-4.png")}
CASES = [("test-a", "Alakazam|Base|1", "Alakazam|Base|1", "Likely Genuine"),
         ("test-b", "Alakazam|Base|1", "Charizard|Base|4", "Inconclusive")]

needed = [CROP] + list(REFS.values())
missing = [os.path.basename(p) for p in needed if not os.path.exists(p)]
if missing:
    print("SKIPPED: canned demo test fixtures are not shipped in the pack "
          "(card photos are excluded by design). Missing in demo/fixtures/: "
          + ", ".join(missing)
          + ". Evidence from the original run: tests/test-A-result.json / "
            "tests/test-B-result.json at the pack root.")
    sys.exit(0)

results = []
for name, ident, refid, expected in CASES:
    out = os.path.join(HERE, "out", name)
    r = subprocess.run([sys.executable, CHECKER, "--user", CROP,
                        "--reference", REFS[refid], "--identity", ident,
                        "--reference-identity", refid, "--crop-mode", "supplied", "--out", out],
                       capture_output=True, text=True, timeout=120)
    d = json.load(open(os.path.join(out, "result.json")))
    ok = d["verdict"] == expected
    results.append({"test": name, "expected": expected, "verdict": d["verdict"],
                    "reason": d["verdict_reason"], "matches": (d.get("tells") or {}).get("matches"),
                    "strong": (d.get("tells") or {}).get("strong_mismatches"),
                    "api_calls": d["api_calls"], "spend_usd": d["spend_usd"], "pass": ok})
    print(f"{name}: {d['verdict']} (expected {expected}) pass={ok} reason={d['verdict_reason']}")
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
json.dump(results, open(os.path.join(HERE, "out", "demo-test-results.json"), "w"), indent=2)
print("PASS" if all(x["pass"] for x in results) else "FAIL", f"{sum(x['pass'] for x in results)}/{len(results)}")
sys.exit(0 if all(x["pass"] for x in results) else 1)
