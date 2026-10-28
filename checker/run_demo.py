#!/usr/bin/env python3
"""Run every implemented use once, playground only, with a call log.
SAM calls in THIS job: 3 max (group synthetic, back reference, slab front).
The tonight's-40 SAM test is a separate job and is NOT re-run here.
Test images are playground files already on disk; no new user photos.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_pipeline as mp
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "out")
FRONT = os.path.expanduser("~/workspace/fake-check/playground/agent-loop/run-v2-2026-10-26-night/cropped.png")
SLAB_FRONT = os.path.expanduser("~/workspace/fake-check/slab-references/cgc-blissey-v-10-front.jpg")
SLAB_BACK = os.path.expanduser("~/workspace/fake-check/slab-references/psa-eevee-9-back.jpg")

# Fresh log for this run.
if os.path.exists(mp.LOG_PATH):
    os.remove(mp.LOG_PATH)

results = {}
def put(k, v):
    results[k] = v
    print(f"{k}: {str(v)[:400]}")

# A test tells result (from the merged build's own test data shape, $0 local).
tells = {"matches": 5, "strong_mismatches": 0,
         "details": {"colour": "match", "edge": "match", "aspect": "match"}}
verdict = "Likely Genuine"
identity = "Alakazam|Base|1"

put("A1-verdict-reasoning", mp.verdict_reasoning(tells, verdict, identity))
put("A2-second-opinion", mp.second_opinion(tells, verdict))
put("A3-tester-feedback", mp.tester_feedback_summary(
    ["Photo step was confusing", "I didn't know a back would help",
     "Verdict screen was clear", "Photo step was confusing"]))
put("A4-photo-coach", mp.photo_quality_coach(
    {"aspect_off": True, "card_fills_frame": False, "glare": False}))
put("A5-back-none", mp.back_consistency_note(tells, None))
put("A5-back-present", mp.back_consistency_note(
    tells, {"border": "match", "pattern": "match"}))
put("A6-community-draft", mp.community_post_draft(
    {"topic": "worst fake pulled", "app": "Real or Replica", "links": "none"}))
put("A7-identity-suggestion", mp.identity_suggestion("portrait card, yellow border, psychic type"))
put("A7-identity-check", mp.identity_check("1", "suggested: Alakazam 1"))
put("A8-triage", mp.edge_case_triage(
    [{"reason": "bad photo"}, {"reason": "back missing"}, {"reason": "bad photo"}]))
put("B9-demo-art", mp.muse_image(
    "A small gold cauldron icon, flat simple illustration, on a plain white background, no text",
    "demo-art.png", "B9-demo-art"))
put("B10-explainer-diagram", mp.muse_image(
    "A simple diagram of where to look on a trading card, flat illustration, "
    "art window at top and text box below, no real card, no brand text",
    "explainer-diagram.png", "B10-explainer-diagram"))
put("C11-voice-note", mp.transcribe_note(
    "this one feels glossy, corners look rounded — note only, not a verdict"))
put("C12-wonder-audit", mp.wonder_audit(
    "Verdict Likely Genuine from tells: colour match, edge match, aspect match."))
put("D14-batch-narration", mp.batch_calibration_narration([
    {"card": "Alakazam|Base|1", "matches": 5, "strong_mismatches": 0},
    {"card": "Charizard|Base|4", "matches": 1, "strong_mismatches": 3},
    {"card": "Test|Set|9", "matches": 2, "strong_mismatches": 1}]))
put("F25-cheap-check", mp.cheap_check(tells, verdict, identity))

# E: SAM, 3 calls only.
# E18 synthetic group: two copies of the front crop side by side, labelled
# synthetic. One SAM call returns (in the verified form) one box; this
# proves the limitation, it does NOT prove multi-appearance splitting.
with Image.open(FRONT) as im:
    w, h = im.size
    group = Image.new("RGB", (w * 2 + 20, h), "white")
    group.paste(im, (0, 0)); group.paste(im, (w + 20, 0))
    group.save(os.path.join(OUT, "synthetic-group.png"))
box_group = mp.sam_box(os.path.join(OUT, "synthetic-group.png"))
put("E18-group-split", {"box": box_group,
    "limitation": "Verified SAM form returns one box per call; splitting every "
                  "appearance needs one call per appearance or a verified "
                  "multi-box form, which is NOT proven here."})
# E19 back: code path on a slab back reference image. Result is a crop,
# NOT a back verdict, NOT filed in any backs database.
box_back = mp.sam_box(SLAB_BACK)
if box_back:
    mp.crop_to(SLAB_BACK, box_back, "back-crop-test.png")
put("E19-back-segment", {"box": box_back, "crop": "back-crop-test.png",
    "note": "Test-only crop from a slab back reference; not a back verdict."})
# E20 slab inside: SAM on a slab front. Record box aspect honestly.
box_slab = mp.sam_box(SLAB_FRONT)
if box_slab:
    mp.crop_to(SLAB_FRONT, box_slab, "slab-crop-test.png")
with Image.open(SLAB_FRONT) as im:
    slab_aspect = im.size[0] / im.size[1]
put("E20-slab-inside", {"box": box_slab, "crop": "slab-crop-test.png",
    "photo_quality": mp.photo_quality_from_box(box_slab, slab_aspect),
    "note": "SAM box may cover the slab, not just the card inside. "
            "Inside-vs-case separation is NOT proven by this box alone; "
            "cert + card-inside comparison still requires a human check."})
# E21 region split + E23, $0, on the front crop.
put("E21-region-split", mp.region_split(FRONT))
with Image.open(FRONT) as im:
    ref_aspect = im.size[0] / im.size[1]
put("E23-photo-quality", mp.photo_quality_from_box(box_group, ref_aspect))
# E24 refusals.
for fn in ("authenticate_card", "grade_card"):
    try:
        getattr(mp, fn)(FRONT)
        put("E24-" + fn, "ERROR: did not refuse")
    except NotImplementedError as e:
        put("E24-" + fn, f"refused as designed: {e}")
# F26/F27 reuse boxes already obtained (no new SAM calls).
put("F26-test-check", mp.test_check("slab-crop-test.png", tells, verdict, identity))
put("F27-demo-check", mp.demo_check("slab-crop-test.png", tells, verdict, identity))

# Call log totals.
log = []
if os.path.exists(mp.LOG_PATH):
    with open(mp.LOG_PATH) as f:
        log = [json.loads(l) for l in f if l.strip()]
sam_calls = [e for e in log if e["model"] == "sam-3.1" and "FAILED" not in e["use"]]
sam_cost = sum(e["cost_usd_estimate"] for e in log if e["model"] == "sam-3.1")
baseten_cost = sum(e["cost_usd_estimate"] for e in log if "baseten" in e["source"])
results["call_log_summary"] = {
    "total_entries": len(log), "sam_calls": len(sam_calls),
    "sam_cost_usd_estimate": round(sam_cost, 6),
    "baseten_cost_usd_estimate": round(baseten_cost, 6),
    "meta_spark_calls": len([e for e in log if e["model"] == "muse-spark-1.3"]),
    "image_calls": len([e for e in log if e["model"] == "muse-image-1.0"]),
    "sam_cap_usd": 2.0, "sam_cap_exceeded": sam_cost > 2.0}
with open(os.path.join(OUT, "result.json"), "w") as f:
    json.dump(results, f, indent=2)
print("\nCALL LOG SUMMARY:", json.dumps(results["call_log_summary"], indent=2))
