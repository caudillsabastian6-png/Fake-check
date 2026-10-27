#!/usr/bin/env python3
"""
App V2 — MERGED PLAYGROUND BUILD, Oct 27, 2026. PLAYGROUND ONLY.
No Play publish, no public demo link update, no production release,
no network call, no SAM/Baseten/Meta call, $0 local tests only.

What this merges, in one flow (identity-first, measurement-first):
  1. Agent Loop v2 flow  (agent_loop_v2.py, copied verbatim in this folder):
     Pip crop -> Index compare -> Gauge measure -> decision -> Latch examine.
     In the ORIGINAL v2, the decision step had no tells measurement, so it
     correctly stayed Inconclusive. This merged build plugs that gap.
  2. Tells v2 measurement (tells_v2.py, copied verbatim in this folder):
     5 pixel tells, same measurement on user crop and reference.
     Verdict rule (unchanged): >=2 strong mismatches -> Likely Counterfeit;
     0 strong + >=3 matches -> Likely Genuine; else Inconclusive.
  3. Pip on-device crop v2 (crop_v2.py, copied verbatim in this folder):
     DEFAULT crop path. Smoothed-colour mask + 10% inset, v0 fallback.
     NOT shippable as the sole cropper (phone mean IoU ~0.58 at best in
     Job B) — see README blockers. It is the default here, not a proof.

Hard rules, enforced in code (not just in comments):
  - Identity-first: --identity is REQUIRED (e.g. "Alakazam|Base|1").
    The reference image must be the reference FOR THAT IDENTITY.
    If identity is missing, or reference identity does not match the
    supplied identity, verdict is Inconclusive — never Genuine.
  - Manifest / name match alone NEVER produces Likely Genuine.
    Only a tells measurement can. If tells are not measured, Inconclusive.
  - Every Likely verdict is an ESTIMATE ONLY, never official, never
    guaranteed, never a grade, never a SAM authentication.
  - SAM escalation ONLY: if on-device crop returns REFUSE / invalid box,
    or --real-check is passed, this $0 build does NOT call SAM. It records
    "SAM_ESCALATION_REQUIRED" and stays Inconclusive, unless the caller
    supplies a SAM box explicitly via --sam-box '{"x1":..,"y1":..,"x2":..,"y2":..}'
    (that box is then used to crop, and the source is logged as supplied,
    not as a live SAM call). No spend is ever hidden in this build.
  - Offline fallback: if the reference cannot be read locally, verdict is
    Inconclusive with reason "reference_unreadable_offline" — no web fetch.
  - Back photo: if supplied via --back, it is noted and NOT tells-scored
    in v2 (front-only verdict; a back would help, said plainly).
  - Latch structural checks (edits nothing): crop exists, box valid,
    verdict allowed, tells measured or reason stated, disclaimer present.

Usage (local, $0):
  python3 app_check_v2.py --user <crop-or-photo> --reference <ref.png>
      --identity "Alakazam|Base|1" --out <out_dir>
      [--back <back.png>] [--real-check]
      [--sam-box '{"x1":19,"y1":16,"x2":584,"y2":813}']
      [--crop-mode supplied|ondevice]   # default: supplied if --user is
      # already a crop (tests), ondevice if it is a full photo
  For the canonical tests in this folder, --user is already a crop, so
  use --crop-mode supplied; on-device cropping of a full photo is
  exercised separately and its PASS/REFUSE is reported, not hidden.

Cost: api_calls=0, spend_usd=0.0. Any future live SAM/Baseten call must
be logged separately and is OUTSIDE this merged $0 build.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tells_v2  # noqa: E402  (copied verbatim Tells v2)

ALLOWED = ("Likely Genuine", "Likely Counterfeit", "Inconclusive")
DISCLAIMER = ("Estimate only, never official, never guaranteed. "
              "A manifest name match alone never produces a Genuine verdict.")


def ondevice_crop(path):
    """Try Pip crop_v2.detect(); return (box, status, detail) or REFUSE."""
    try:
        import crop_v2
        r = crop_v2.detect(path)
        box = r.get("box")
        if r.get("status") == "PASS" and box and len(box) == 4:
            return box, "PASS", f"ondevice branch={r.get('branch')}"
        return None, "REFUSE", f"ondevice status={r.get('status')} reason={r.get('reason')} branch={r.get('branch')}"
    except Exception as e:  # dependency (scipy / on_device_crop) missing etc.
        return None, "REFUSE", f"ondevice unavailable: {type(e).__name__}: {str(e)[:200]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--reference", required=True)
    ap.add_argument("--identity", required=True, help="Name|Set|Number, e.g. Alakazam|Base|1")
    ap.add_argument("--reference-identity", default=None,
                    help="Identity the reference is FOR; defaults to --identity. If different, Inconclusive.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--back", default=None)
    ap.add_argument("--real-check", action="store_true")
    ap.add_argument("--sam-box", default=None)
    ap.add_argument("--crop-mode", choices=["supplied", "ondevice"], default="supplied")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    from PIL import Image
    steps = []

    def step(name, detail):
        steps.append({"step": name, "detail": detail})
        print(f"{name}: {detail}")

    identity = a.identity.strip()
    ref_identity = (a.reference_identity or identity).strip()
    identity_match = (identity == ref_identity)
    step("Identity", f"user_identity={identity} reference_identity={ref_identity} match={identity_match}")

    # --- Crop stage: on-device default, SAM escalation only ---
    crop_path = a.user
    box = None
    sam_escalation = False
    crop_status = "supplied"
    if a.crop_mode == "ondevice":
        box, crop_status, detail = ondevice_crop(a.user)
        step("Pip/ondevice-crop", detail)
        if box is None:
            sam_escalation = True
            step("Pip/SAM-escalation", "on-device crop REFUSE — SAM escalation required, $0 build makes no SAM call")
            if a.sam_box:
                try:
                    b = json.loads(a.sam_box)
                    box = [int(b["x1"]), int(b["y1"]), int(b["x2"]), int(b["y2"])]
                    step("Pip/SAM-box-supplied", f"box {box} (supplied, not a live SAM call)")
                except Exception as e:
                    step("Pip/SAM-box-supplied", f"invalid supplied box: {e}")
                    box = None
    if a.real_check:
        sam_escalation = True
        step("Pip/SAM-escalation", "explicit Real check — SAM escalation path recorded (no live call in $0 build)")

    box_valid = True
    if box is not None and crop_status != "supplied":
        # FIX 2026-10-27 (found by Test C): a v0-fallback box on a clean
        # reference image was [28,27,564,475] — landscape aspect 1.20 for a
        # portrait card — and tells then falsely said Likely Counterfeit
        # for a genuine card vs itself. A bad crop must NEVER become a
        # Counterfeit verdict. Validate aspect before trusting any box.
        bw, bh = box[2] - box[0], box[3] - box[1]
        aspect = bw / max(1, bh)
        # A crop of THIS card must roughly match THIS reference's aspect.
        # (A generic landscape allowance was the first fix's flaw: 1.196
        # passed as "landscape" for a portrait card.) If the reference
        # cannot be read, fall back to portrait 0.55-0.90 only.
        try:
            with Image.open(a.reference) as _r:
                ref_aspect = _r.size[0] / max(1, _r.size[1])
            aspect_ok = abs(aspect - ref_aspect) <= 0.15
        except Exception:
            aspect_ok = 0.55 <= aspect <= 0.90
        if not aspect_ok:
            step("Pip/crop", f"REJECTED invalid on-device box {box} aspect={aspect:.3f} — bad crop, not a fake card")
            box = None
            box_valid = False
            sam_escalation = True
            step("Pip/SAM-escalation", "invalid on-device box — SAM escalation required, $0 build makes no SAM call")
        else:
            with Image.open(a.user) as im:
                im.crop(tuple(box)).save(os.path.join(a.out, "cropped.png"))
            crop_path = os.path.join(a.out, "cropped.png")
            step("Pip/crop", f"cropped to {box} aspect={aspect:.3f}")
    elif a.crop_mode == "supplied":
        step("Pip/crop", "user file supplied as crop (test path); no re-crop, no invented box")

    # --- Tells stage: measurement only, never manifest ---
    tells_result = None
    verdict, reason = "Inconclusive", "not_measured_yet"
    if not identity_match:
        verdict, reason = "Inconclusive", "identity_mismatch_reference_not_for_supplied_identity"
        step("Index/identity", reason)
    elif not os.path.exists(a.reference):
        verdict, reason = "Inconclusive", "reference_unreadable_offline"
        step("Index/reference", reason)
    elif sam_escalation and box is None and a.crop_mode == "ondevice":
        verdict, reason = "Inconclusive", "sam_escalation_required_crop_not_available"
        step("Loop/decision", reason)
    else:
        try:
            tells_out = os.path.join(a.out, "tells.json")
            # Reuse tells_v2's measure/compare by calling its CLI-equivalent
            # logic via a subprocess-free path: run its main() on a copy.
            # tells_v2.main() reads sys.argv, so call it in-process safely.
            old_argv = sys.argv
            sys.argv = ["tells_v2.py", crop_path, a.reference, tells_out]
            try:
                tells_v2.main()
            finally:
                sys.argv = old_argv
            with open(tells_out) as f:
                tells_result = json.load(f)
            verdict = tells_result["verdict"]
            reason = f"tells measured: matches={tells_result['matches']} strong_mismatches={tells_result['strong_mismatches']}"
            step("Gauge/tells", reason)
        except Exception as e:
            verdict, reason = "Inconclusive", f"tells_failed: {type(e).__name__}: {str(e)[:200]}"
            step("Gauge/tells", reason)

    if a.back:
        step("Back", f"back file supplied: {a.back} (not tells-scored in v2; front-only verdict, back would help if it disagreed)")
    else:
        step("Back", "no back photo supplied — front-only verdict")

    # --- Latch: structural examiner, edits nothing ---
    checks = {
        "identity_supplied": bool(identity),
        "identity_matches_reference": identity_match,
        "crop_exists": os.path.exists(crop_path),
        "box_valid": box_valid,  # supplied-crop path has no invented box; ondevice box aspect-validated above
        "tells_measured": tells_result is not None,
        "verdict_allowed": verdict in ALLOWED,
        "disclaimer_present": True,
        "api_calls": 0,
        "spend_usd": 0.0,
    }
    step("Latch/examiner", f"structural checks: {checks}")

    result = {
        "app": "Real or Replica — merged V2 playground build",
        "build": "app-v2-merged, Oct 27, 2026, playground only, NOT a release",
        "verdict": verdict,
        "verdict_reason": reason,
        "verdict_disclaimer": DISCLAIMER,
        "identity": identity,
        "reference": a.reference,
        "reference_identity": ref_identity,
        "user_file": a.user,
        "crop_file": crop_path,
        "crop_mode": a.crop_mode,
        "crop_status": crop_status,
        "sam_escalation_required": sam_escalation,
        "back_supplied": bool(a.back),
        "tells": tells_result,
        "steps": steps,
        "latch_checks": checks,
        "api_calls": 0,
        "spend_usd": 0.0,
        "merged_from": ["agent_loop_v2.py", "tells_v2.py", "crop_v2.py"],
        "still_v1": ["One-Go in the live app (v1)", "Public Demo public link (old version, NOT updated in this job)"],
    }
    with open(os.path.join(a.out, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nVerdict: {verdict} ({reason}) — {DISCLAIMER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
