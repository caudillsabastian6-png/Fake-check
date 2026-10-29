#!/usr/bin/env python3
"""Q10 (Audit #15) tests — plain-words 'why this verdict' explainer.
AI loop keeper Oct 28 2026. $0 local only, no network, no SAM/Baseten/Meta.
Run: python3 test_why_measured_2026-10-28.py
Exits non-zero on any failure.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# Standalone fix (Oct 29, 2026): why_measured lives in ../checker.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "checker")))
import why_measured

fails = []

def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        fails.append(name)

def mk_tell(match, strong, diff=0.01, thr=0.05):
    return {"difference": diff, "threshold": thr, "match": match, "strong_mismatch": strong}

ALL_MATCH = {"tells": {k: mk_tell(True, False) for k in why_measured.KNOWN_ORDER},
             "matches": 5, "strong_mismatches": 0, "verdict": "Likely Genuine"}
TWO_STRONG = {"tells": dict(ALL_MATCH["tells"],
                            aspect_ratio=mk_tell(False, True, 0.2, 0.05),
                            mean_rgb=mk_tell(False, True, 80.0, 30.0)),
              "matches": 3, "strong_mismatches": 2, "verdict": "Likely Counterfeit"}
BACK_MATCH = {"tells": {k: mk_tell(True, False) for k in why_measured.KNOWN_ORDER},
              "matches": 5, "strong_mismatches": 0, "verdict": "Likely Genuine"}

# 1. All matched: 5 plain sentences, front sentence names 5 of 5.
w = why_measured.explain(ALL_MATCH, None, "Likely Genuine")
check("all-match 5 measured", len(w["front"]["measured"]) == 5,
      str(len(w["front"]["measured"])))
check("all-match plain words present",
      all(m["plain"] and m["finding"] for m in w["front"]["measured"])
      and "matched the reference closely" in w["front"]["measured"][0]["finding"])
check("all-match front sentence 5 of 5", "5 of 5" in w["front"]["sentence"],
      w["front"]["sentence"])
check("all-match combined genuine", "Likely Genuine" in w["combined_sentence"])
check("all-match no missing front", w["front"]["missing"] == [])
check("all-match edge text not font/holo proof",
      "not proof of a font or holo pattern" in w["front"]["measured"][3]["plain"])

# 2. Two strong mismatches: flags named, counterfeit sentence.
w = why_measured.explain(TWO_STRONG, None, "Likely Counterfeit")
check("counterfeit flags named",
      sum(1 for m in w["front"]["measured"] if "differed a lot" in m["finding"]) == 2)
check("counterfeit combined", "Likely Counterfeit" in w["combined_sentence"])

# 3. Front-only: back lands in not-measured with the exact reason.
w = why_measured.explain(ALL_MATCH, None, "Likely Genuine")
check("front-only back not measured",
      any("no back photo was supplied" in x for x in w["not_measured"]),
      str(w["not_measured"]))
check("back supplied no ref names reason",
      any("no back reference was given" in x
          for x in why_measured.explain(ALL_MATCH, None, "Likely Genuine",
                                        back_supplied=True)["not_measured"]))

# 4. Back measured: back sentences present, back NOT in not-measured.
w = why_measured.explain(ALL_MATCH, BACK_MATCH, "Likely Genuine")
check("back measured present", w["back"] is not None and len(w["back"]["measured"]) == 5)
check("back measured not in not-measured",
      not any("no back photo" in x or "no back reference" in x for x in w["not_measured"]))

# 5. Always-not-measured: grader, grade, SAM, price — never claimed measured.
w = why_measured.explain(ALL_MATCH, BACK_MATCH, "Likely Genuine")
for needle in ("grader", "grade", "SAM", "Market price"):
    check(f"always not measured: {needle}",
          any(needle in x for x in w["not_measured"]))
check("measured never claims grader",
      not any("grader" in m["plain"].lower() for m in w["front"]["measured"]))

# 6. Partial tells: only present keys listed; absent keys in not-measured.
partial = {"tells": {"aspect_ratio": mk_tell(True, False), "mean_rgb": mk_tell(True, False)},
           "matches": 2, "strong_mismatches": 0, "verdict": "Inconclusive"}
w = why_measured.explain(partial, None, "Inconclusive")
check("partial only 2 measured", len(w["front"]["measured"]) == 2)
check("partial absent 3 in not-measured", len(w["front"]["missing"]) == 3,
      str(w["front"]["missing"]))
check("partial combined inconclusive", "stays Inconclusive" in w["combined_sentence"])

# 7. No tells at all: honest empty explainer, no Likely support.
w = why_measured.explain(None, None, "Inconclusive")
check("no tells measured_total 0", w["measured_total"] == 0)
check("no tells sentence honest", "No tells were measured" in w["combined_sentence"])
check("unknown tell key still listed",
      len(why_measured.explain(
          {"tells": {"some_new_tell": mk_tell(True, False)}, "matches": 1,
           "strong_mismatches": 0, "verdict": "Inconclusive"},
          None, "Inconclusive")["front"]["measured"]) == 1)

# 8. Checker integration: canned pipeline run carries why_measured, and
#    Agents 101 canned verdicts are unchanged by the wiring.
CROP = os.path.expanduser("~/workspace/fake-check/playground/agent-loop/run-v2-2026-10-26-night/cropped.png")
REF_ALA = os.path.expanduser("~/workspace/fake-check/sourced-reals/sr-0001-BS-1.png")
if os.path.exists(CROP) and os.path.exists(REF_ALA):
    r = subprocess.run([sys.executable, os.path.join(HERE, "app_check_v2.py"),
                        "--user", CROP, "--crop-mode", "supplied",
                        "--reference", REF_ALA, "--reference-identity", "Alakazam|Base|1",
                        "--lookup-set", "base1", "--lookup-number", "1",
                        "--out", "/tmp/out-why-measured"],
                       capture_output=True, text=True, timeout=120)
    d = json.load(open("/tmp/out-why-measured/result.json"))
    check("checker verdict unchanged Genuine", d["verdict"] == "Likely Genuine",
          d["verdict"])
    check("checker why_measured present", "why_measured" in d)
    check("checker why measured_total 5", d["why_measured"]["measured_total"] == 5,
          str(d["why_measured"]["measured_total"]))
    check("checker why combined mentions Genuine",
          "Likely Genuine" in d["why_measured"]["combined_sentence"])
    check("checker why front-only back line",
          any("no back photo" in x for x in d["why_measured"]["not_measured"]))
else:
    print("SKIP checker integration (crop/ref files absent)")

print("PASS" if not fails else f"FAIL {fails}")
sys.exit(1 if fails else 0)
