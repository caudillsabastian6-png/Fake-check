#!/usr/bin/env python3
"""Re-run the canonical V2 tests through app_check_v2.py into out/ (local, $0)."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.expanduser("~/workspace/fake-check/playground/app-v2-merged")
CROP = os.path.expanduser("~/workspace/fake-check/playground/agent-loop/run-v2-2026-10-26-night/cropped.png")
REFS = {"Alakazam|Base|1": "~/workspace/fake-check/sourced-reals/sr-0001-BS-1.png",
        "Charizard|Base|4": "~/workspace/fake-check/sourced-reals/sr-0004-BS-4.png"}
CASES = [("test-a", "Alakazam|Base|1", "Alakazam|Base|1", "Likely Genuine"),
         ("test-b", "Alakazam|Base|1", "Charizard|Base|4", "Inconclusive")]
results = []
for name, ident, refid, expected in CASES:
    out = os.path.join(HERE, "out", name)
    r = subprocess.run([sys.executable, os.path.join(V2, "app_check_v2.py"), "--user", CROP,
                        "--reference", os.path.expanduser(REFS[refid]), "--identity", ident,
                        "--reference-identity", refid, "--crop-mode", "supplied", "--out", out],
                       capture_output=True, text=True, timeout=120)
    d = json.load(open(os.path.join(out, "result.json")))
    ok = d["verdict"] == expected
    results.append({"test": name, "expected": expected, "verdict": d["verdict"],
                    "reason": d["verdict_reason"], "matches": (d.get("tells") or {}).get("matches"),
                    "strong": (d.get("tells") or {}).get("strong_mismatches"),
                    "api_calls": d["api_calls"], "spend_usd": d["spend_usd"], "pass": ok})
    print(f"{name}: {d['verdict']} (expected {expected}) pass={ok} reason={d['verdict_reason']}")
json.dump(results, open(os.path.join(HERE, "out", "demo-test-results.json"), "w"), indent=2)
print("PASS" if all(x["pass"] for x in results) else "FAIL", f"{sum(x['pass'] for x in results)}/{len(results)}")
sys.exit(0 if all(x["pass"] for x in results) else 1)
