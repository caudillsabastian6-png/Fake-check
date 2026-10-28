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
  - Back photo (Oct 27 back-scoring update): if supplied via --back
    AND a card-only back reference via --back-reference, the back is
    tells-scored SEPARATELY with the same 5 tells, against that back
    reference only. Backs are mostly uniform, so a back score is a
    back-design/print score, NOT an identity proof. Back aspect must
    match the back reference within 0.15, else the back stays
    Inconclusive (bad crop, not a fake card). Combined verdict:
    Counterfeit if front OR back is Counterfeit; Genuine only if
    BOTH are Genuine; otherwise Inconclusive. If no back reference
    is supplied, the back is noted and NOT scored (old v2 behaviour).
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
import agents101_leftovers as leftovers  # noqa: E402  (Agents 101 ideas 5-9)

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
    ap.add_argument("--additional-references", default=None,
                    help="Comma-separated verified reference files for the SAME identity. "
                         "If supplied, tells are measured against the MEDIAN across "
                         "--reference + these files (multi_reference.py, up to 5 total). "
                         "Only registry-verified references may be passed; this flag never invents one.")
    ap.add_argument("--identity", default=None, help="Name|Set|Number, e.g. Alakazam|Base|1 (optional if --lookup-set/--lookup-number given)")
    # Identity lookup (Oct 27, 2026): TCGdex EN/JA detail index, $0, local.
    # Set + printed number first; name is a fallback search only, never
    # an auto-pick. A lookup hit is identity only, NOT authentication,
    # and most indexed cards have no reference image in the playground.
    ap.add_argument("--lookup-set", default=None, help="Set id or set name, e.g. base1 or 'Base Set'")
    ap.add_argument("--lookup-number", default=None, help="Printed card number, e.g. 4 or 016")
    ap.add_argument("--lookup-name", default=None, help="Card name, fallback search only")
    ap.add_argument("--lookup-language", default=None, choices=["en", "ja", "all"],
                    help="Disambiguate when a set+number exists in both EN and JA")
    ap.add_argument("--reference-identity", default=None,
                    help="Identity the reference is FOR; defaults to --identity. If different, Inconclusive.")
    ap.add_argument("--reference-status", default=None,
                    help="Reference provenance, e.g. verified_reference_pilot_uncalibrated for batch-1 TCGdex refs. "
                         "Pilot means file+index verified but per-identity tells calibration is still open.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--back", default=None)
    ap.add_argument("--back-reference", default=None)
    ap.add_argument("--real-check", action="store_true")
    ap.add_argument("--sam-box", default=None)
    ap.add_argument("--crop-mode", choices=["supplied", "ondevice"], default="supplied")
    ap.add_argument("--slab-claimed", action="store_true", help="Card is claimed slabbed: cert is then required")
    ap.add_argument("--slab-cert", default=None, help="Slab cert number, if slab claimed")
    ap.add_argument("--back-claimed", action="store_true", help="A back photo is claimed: one must be supplied")
    # Agents 101 leftovers 5-9 (all $0, all local, all optional):
    ap.add_argument("--source-label", default="owner photo")
    ap.add_argument("--source-permission", default="permissioned",
                    choices=["permissioned", "unpermissioned", "private", "unknown"],
                    help="7: unpermissioned/private sources are flagged and excluded")
    ap.add_argument("--slab-card-photo", default=None,
                    help="8: photo of the card inside the slab; required when slab claimed")
    ap.add_argument("--check-id", default=None, help="9: id for this saved check (generated if omitted)")
    ap.add_argument("--resume-from", default=None, help="9: out dir of a paused check to resume")
    ap.add_argument("--branch-from", default=None, help="9: out dir of a check to branch from")
    ap.add_argument("--pause-after", default=None, choices=["identity", "crop", "tells"],
                    help="9: pause after this stage, file no verdict (resume with --resume-from)")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    from PIL import Image
    steps = []
    progress_path = os.path.join(a.out, "progress.json")

    def step(name, detail):
        # A — agent loop: progress is saved after EVERY step, not only at
        # the end, so a stopped run can be inspected / resumed from its
        # last completed step. No step is invented after the fact.
        steps.append({"step": name, "detail": detail})
        try:
            with open(progress_path, "w") as _f:
                json.dump({"status": "in_progress", "steps_completed": len(steps),
                           "last_step": name, "steps": steps}, _f, indent=2)
        except Exception:
            pass
        print(f"{name}: {detail}")

    # 9 — Saved / resumable / branch checks (same out-dir progress.json
    # approach, no new store). Resume keeps prior steps; branch keeps
    # the parent id. Re-execution of the $0 measurements is deterministic.
    prior = None
    parent_check_id = None
    if a.resume_from:
        prior = leftovers.load_saved(a.resume_from)
    if a.branch_from and not a.resume_from:
        prior = leftovers.load_saved(a.branch_from)
        if prior:
            parent_check_id = prior.get("check_id")
    check_id = a.check_id or (prior.get("check_id") if a.resume_from and prior else None) or leftovers.new_check_id()
    prior_steps = (prior.get("steps") if isinstance(prior, dict) else None) or []
    if prior_steps:
        steps.extend(prior_steps)

    def pause_and_exit(stage):
        # 9 — pause files NO verdict and NO result.json; resume later.
        try:
            with open(progress_path, "w") as _f:
                json.dump({"status": "paused", "check_id": check_id,
                           "parent_check_id": parent_check_id,
                           "paused_after": stage, "steps_completed": len(steps),
                           "steps": steps}, _f, indent=2)
            leftovers.save_check(a.out, {"check_id": check_id, "parent_check_id": parent_check_id,
                                         "status": "paused", "paused_after": stage, "steps": steps})
        except Exception:
            pass
        print(f"Paused after {stage}: no verdict filed; resume with --resume-from {a.out}")
        return 0

    # Identity lookup (wired Oct 27, 2026): set+number first, name
    # fallback search only. Resolved identity is Name|SetName|Number
    # from the index row. Lookup proves identity ONLY; it never proves
    # a card genuine, and it never picks an ambiguous candidate.
    lookup_info = None
    lookup_needs_input = []
    lookup_proven = False
    lookup_row = None
    lookup_method = None
    reference_for_identity_available = False
    if a.lookup_set or a.lookup_number or a.lookup_name:
        try:
            import identity_lookup
            res = identity_lookup.resolve(a.lookup_set, a.lookup_number, a.lookup_name,
                                          a.lookup_language if a.lookup_language != "all" else None)
            lookup_info = {"method_requested": "set_number" if a.lookup_set else "name_number",
                           "set_query": a.lookup_set, "number_query": a.lookup_number,
                           "name_query": a.lookup_name, "language": a.lookup_language,
                           "status": res["status"], "method": res["method"],
                           "matches": res["matches"], "name_candidates": res["name_candidates"]}
            if res["status"] == "resolved":
                lookup_proven = True
                lookup_row = res["row"]
                lookup_method = res["method"]
                a.identity = f"{lookup_row['name']}|{lookup_row['set_name']}|{lookup_row['localId']}"
            else:
                lookup_needs_input = list(res["needs_input"])
        except Exception as e:
            lookup_needs_input = [f"identity_lookup_failed: {type(e).__name__}: {str(e)[:200]}"]
    if not a.identity:
        # No identity and no successful lookup: keep the result-file
        # contract by treating this as needs_input (the lookup message
        # already names the missing set/number; do not add a second
        # generic identity message on top of it).
        a.identity = ""
        if not lookup_needs_input:
            lookup_needs_input.append("identity: supply Name|Set|Number, or --lookup-set + --lookup-number")
    # 5 — Plan tool: steps shown BEFORE the check runs.
    plan = leftovers.build_plan(a.identity, a.back_claimed, a.slab_claimed, a.crop_mode)
    step("Plan", f"steps={plan['steps']}")
    # 7 — Flag do-not-use: explicit permission flag only, never a guess.
    source_flag = leftovers.flag_do_not_use(a.source_label, a.source_permission,
                                            "source permission is unpermissioned/private" if a.source_permission in ("unpermissioned", "private") else "owner/permissioned source")
    step("Flag/source", f"source_label={a.source_label} permission={a.source_permission} flagged={source_flag['flagged']}")

    identity = a.identity.strip()
    ref_identity = (a.reference_identity or identity).strip()
    identity_match = (identity == ref_identity)
    if lookup_proven and lookup_row and not identity_match and a.reference_identity:
        # Lookup identity uses the index set_name ("Base Set"), while a
        # canned reference uses a short label ("Base"). Match on the
        # two things that decide identity: name + printed number.
        try:
            import identity_lookup as _il
            _parts = [x.strip() for x in ref_identity.split("|")]
            if len(_parts) == 3 and _parts[0].strip().lower() == str(lookup_row["name"]).strip().lower() \
                    and _il.norm_number(_parts[2]) == _il.norm_number(lookup_row["localId"]):
                identity_match = True
                reference_for_identity_available = True
                step("Index/lookup", f"resolved {lookup_row['id']} ({lookup_row['language']}, "
                     f"{lookup_row['set_name']} {lookup_row['localId']}, rarity={lookup_row.get('rarity')}) "
                     f"— reference identity matches by name+number; lookup is identity only, not authentication")
        except Exception:
            pass
    if lookup_proven and not a.reference_identity:
        step("Index/lookup", f"resolved {lookup_row['id']} ({lookup_row['language']}, "
             f"{lookup_row['set_name']} {lookup_row['localId']}) — no reference identity supplied, "
             "so no reference image can be confirmed for this identity in the playground")
    step("Identity", f"user_identity={identity} reference_identity={ref_identity} match={identity_match}")
    if a.pause_after == "identity":
        return pause_and_exit("identity")

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

    if a.pause_after == "crop":
        return pause_and_exit("crop")

    # --- Scan quality gate (Oct 27, missing item #2): BEFORE tells ---
    # A quality failure is needs_input + retake, NEVER a Counterfeit
    # verdict and NEVER a guess. A pass only means the photo is good
    # enough to measure; it proves nothing about genuineness.
    quality = None
    quality_problems = []
    try:
        import quality_gate
        quality = quality_gate.check_quality(crop_path, a.reference if os.path.exists(a.reference) else None)
        quality_problems = list(quality.get("problems", []))
        step("Quality/gate", f"passed={quality['passed']} problems={quality_problems} metrics={quality.get('metrics', {})}")
    except Exception as e:
        quality = {"passed": False, "problems": [f"scan_quality: quality check failed ({type(e).__name__}) — retake a clear photo"],
                   "metrics": {}, "sleeve_detectable": False, "notes": []}
        quality_problems = list(quality["problems"])
        step("Quality/gate", f"check failed, treating as needs_input: {quality_problems}")

    # --- Tells stage: measurement only, never manifest ---
    tells_result = None
    verdict, reason = "Inconclusive", "not_measured_yet"
    multi_reference_info = None
    if quality_problems:
        # Quality alone never makes a card Counterfeit. Tells are NOT
        # measured on a photo that failed the gate.
        verdict, reason = "Inconclusive", "needs_input: " + "; ".join(quality_problems)
        step("Quality/needs_input", reason)
    elif lookup_needs_input:
        verdict, reason = "Inconclusive", "needs_input: " + "; ".join(lookup_needs_input)
        step("Index/lookup", reason)
    elif lookup_proven and not reference_for_identity_available and not a.reference_identity:
        verdict, reason = ("Inconclusive", "identity_found_but_no_reference_image_for_identity: "
                           f"{lookup_row['id']} ({lookup_row['language']}, {lookup_row['set_name']} "
                           f"{lookup_row['localId']}, {lookup_row['name']}) is in the EN/JA index, but no "
                           "reference image for this identity exists in the playground (only 2 canned "
                           "references) — tells cannot be measured, verdict stays Inconclusive, not Genuine")
        step("Index/reference", reason)
    elif not identity_match:
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
            extra_refs = [x.strip() for x in (a.additional_references or "").split(",") if x.strip()]
            extra_refs = [x for x in extra_refs if os.path.exists(x)]
            if extra_refs:
                # Multi-reference median (Oct 27, missing item #5):
                # median across primary + additional VERIFIED references
                # only (caller must pass registry-verified files).
                import multi_reference
                all_refs = [a.reference] + extra_refs
                tells_result = multi_reference.median_tells(crop_path, all_refs)
                with open(tells_out, "w") as f:
                    json.dump(tells_result, f, indent=2)
                multi_reference_info = {"reference_count": tells_result["reference_count"],
                                        "reference_mode": tells_result["reference_mode"],
                                        "reference_status": "pilot_uncalibrated",
                                        "reference_files": tells_result["reference_files"]}
                step("Gauge/multi-reference", f"median across {tells_result['reference_count']} verified references, "
                     f"pilot/uncalibrated — median does not make a verdict calibrated")
            else:
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
                multi_reference_info = {"reference_count": 1, "reference_mode": "single",
                                        "reference_status": a.reference_status}
            verdict = tells_result["verdict"]
            reason = f"tells measured: matches={tells_result['matches']} strong_mismatches={tells_result['strong_mismatches']}"
            step("Gauge/tells", reason)
        except Exception as e:
            verdict, reason = "Inconclusive", f"tells_failed: {type(e).__name__}: {str(e)[:200]}"
            step("Gauge/tells", reason)

    back_tells_result = None
    back_verdict, back_reason = None, "no_back_supplied"
    if a.back and a.back_reference:
        try:
            with Image.open(a.back) as _b, Image.open(a.back_reference) as _r:
                b_aspect = _b.size[0] / max(1, _b.size[1])
                r_aspect = _r.size[0] / max(1, _r.size[1])
            if abs(b_aspect - r_aspect) > 0.15:
                back_verdict, back_reason = "Inconclusive", "back_aspect_mismatch_crop_not_card_only"
                step("Back/tells", back_reason)
            else:
                back_out = os.path.join(a.out, "back_tells.json")
                old_argv = sys.argv
                sys.argv = ["tells_v2.py", a.back, a.back_reference, back_out]
                try:
                    tells_v2.main()
                finally:
                    sys.argv = old_argv
                with open(back_out) as f:
                    back_tells_result = json.load(f)
                back_verdict = back_tells_result["verdict"]
                back_reason = f"back tells measured: matches={back_tells_result['matches']} strong_mismatches={back_tells_result['strong_mismatches']}"
                step("Back/tells", back_reason)
        except Exception as e:
            back_verdict, back_reason = "Inconclusive", f"back_tells_failed: {type(e).__name__}: {str(e)[:200]}"
            step("Back/tells", back_reason)
    elif a.back:
        back_verdict, back_reason = None, "back_supplied_no_back_reference_not_scored"
        step("Back", f"back file supplied: {a.back} (no back reference — not tells-scored; front-only verdict, back would help if it disagreed)")
    else:
        step("Back", "no back photo supplied — front-only verdict")
    # Combined verdict: back can only pull a verdict down or confirm it,
    # never invent a Genuine on its own, and never upgrade Inconclusive.
    combined_verdict, combined_reason = verdict, reason
    if back_verdict == "Likely Counterfeit" or verdict == "Likely Counterfeit":
        combined_verdict = "Likely Counterfeit"
        combined_reason = f"combined: front={verdict} back={back_verdict} ({back_reason})"
    elif verdict == "Likely Genuine" and back_verdict == "Likely Genuine":
        combined_verdict = "Likely Genuine"
        combined_reason = f"combined: front Genuine + back Genuine ({reason}; {back_reason})"
    elif back_verdict is not None:
        combined_verdict = "Inconclusive"
        combined_reason = f"combined: front={verdict} back={back_verdict} — not both Genuine, stays Inconclusive"
    verdict, reason = combined_verdict, combined_reason
    step("Loop/combined", f"verdict={verdict} reason={reason}")

    if a.pause_after == "tells":
        return pause_and_exit("tells")

    # --- Agents 101 leftovers 6/7/8: recorded facts, flagged sources, slab ---
    # 6 — every tell becomes a recorded fact (measurement + threshold +
    # source + reference). A tell that cannot be recorded refuses the run.
    facts = []
    fact_error = None
    try:
        facts.extend(leftovers.record_facts(tells_result, "front", crop_path, a.reference))
        facts.extend(leftovers.record_facts(back_tells_result, "back", a.back, a.back_reference))
    except ValueError as e:
        fact_error = str(e)
        step("Record/fact", f"REFUSED: {fact_error}")
    if fact_error:
        verdict, reason = "Inconclusive", f"fact_recording_refused: {fact_error}"
    # 7 — flagged sources are excluded, never quoted as evidence.
    facts = leftovers.filter_facts(facts, [source_flag])
    if source_flag["flagged"]:
        step("Flag/source", "flagged source excluded from evidence — no finding may cite it")
    # 8 — real slab check: cert + card inside, both required; format
    # alone is NEVER grader verification (no grader DB, no network).
    slab_complete, slab_status, slab_missing = leftovers.slab_check(
        a.slab_claimed, a.slab_cert, a.slab_card_photo)
    plan = leftovers.update_plan(plan, "tells", ["slab_status=" + slab_status,
                                                 "facts_recorded=" + str(len(facts))])
    step("Plan/update", f"plan status={plan['status']} notes={plan['notes']}")
    step("Slab/check", f"claimed={a.slab_claimed} complete={slab_complete} status={slab_status}")

    # --- B/C — Verification layer + evidence request (Agents 101, Session 2) ---
    # A verdict may be FILED only if every checklist item is proven and
    # every finding cites a recorded tell. Claim text alone cannot bypass
    # this: if verification fails, a Likely verdict is downgraded to
    # Inconclusive. If the failure is an item only the user can supply,
    # the run returns needs_input naming that exact item instead of
    # guessing a verdict. This gate sits INSIDE verdict filing, not as a
    # separate tool the checker could choose to skip.
    identity_parts = [x.strip() for x in identity.split("|")]
    identity_wellformed = len(identity_parts) == 3 and all(identity_parts)
    findings = []
    if tells_result and tells_result.get("tells"):
        for _name, _v in tells_result["tells"].items():
            findings.append({"finding": f"front tell {_name}",
                             "cites": f"tells.{_name}", "match": _v.get("match"),
                             "strong_mismatch": _v.get("strong_mismatch"),
                             "difference": _v.get("difference"), "threshold": _v.get("threshold")})
    if source_flag["flagged"]:
        # 7 — a flagged source's findings are never quoted, anywhere.
        findings = []
    back_findings = []
    if source_flag["flagged"]:
        back_findings = []
    elif back_tells_result and back_tells_result.get("tells"):
        for _name, _v in back_tells_result["tells"].items():
            back_findings.append({"finding": f"back tell {_name}",
                                  "cites": f"back_tells.{_name}", "match": _v.get("match"),
                                  "strong_mismatch": _v.get("strong_mismatch"),
                                  "difference": _v.get("difference"), "threshold": _v.get("threshold")})
    # Lookup-proven identity counts as proven identity (not as a
    # genuine verdict): the gate still requires recorded tells, which
    # only exist when a reference for that identity was measured.
    checklist = {
        "identity_proven": bool((lookup_proven or identity_match) and identity_wellformed),
        "scan_quality_passed": not quality_problems,
        "front_tells_recorded": tells_result is not None,
        "back_state_honest": bool((not a.back_claimed or a.back) and (back_verdict is not None or not a.back)),
        "slab_complete": slab_complete,
        "findings_cite_recorded_tells": bool(findings) if verdict in ("Likely Genuine", "Likely Counterfeit") else True,
        # 6 — no finding without a recorded fact; a flagged source leaves
        # no facts, so a Likely verdict cannot file on it.
        "facts_recorded": bool(facts) if verdict in ("Likely Genuine", "Likely Counterfeit") else True,
        "source_not_flagged": not source_flag["flagged"],
    }
    verification_failed = [k for k, v in checklist.items() if not v]
    needs_input = list(lookup_needs_input)
    needs_input.extend(quality_problems)
    if not identity_wellformed and not lookup_needs_input:
        needs_input.append("identity: supply Name|Set|Number, e.g. Alakazam|Base|1")
    if a.back_claimed and not a.back:
        needs_input.append("back_photo: a back photo was claimed but none was supplied")
    needs_input.extend(slab_missing)
    if source_flag["flagged"]:
        needs_input.append("source_flagged_do_not_use: this photo's source is flagged unpermissioned/private — supply an owner photo with permission instead")
    if sam_escalation and box is None and a.crop_mode == "ondevice":
        needs_input.append("card_crop: on-device crop refused or invalid — supply a flatter, card-only photo or a SAM crop")
    if needs_input:
        # C — do not guess: a missing user-suppliable item stops filing.
        verdict, reason = "Inconclusive", "needs_input: " + "; ".join(needs_input)
        step("Loop/needs_input", reason)
    elif verdict in ("Likely Genuine", "Likely Counterfeit") and verification_failed:
        verdict, reason = "Inconclusive", "verification_failed: " + ", ".join(verification_failed) + " — Likely verdict cannot file without a proven checklist"
        step("Loop/verification", reason)
    verification_pass = not verification_failed and not needs_input
    status = "filed" if (verification_pass and verdict in ("Likely Genuine", "Likely Counterfeit")) else ("needs_input" if needs_input else "inconclusive")
    latch_signoff = bool(status == "filed")
    step("Loop/verification", f"checklist={checklist} verification_pass={verification_pass} status={status}")
    step("Loop/signoff", f"latch_signoff={latch_signoff} status={status} verdict={verdict}")

    # --- D — Transparency timeline: saw / decided / returned per step ---
    loop_timeline = [
        {"step": "0. Plan", "saw": f"plan steps before running: {plan['steps']}",
         "decided": f"plan status={plan['status']} notes={plan.get('notes', [])}",
         "returned": f"completed={plan.get('completed', [])}"},
        {"step": "1. Identity", "saw": f"user identity {identity}, reference identity {ref_identity}",
         "decided": "match" if identity_match else "mismatch / malformed" if not identity_wellformed else "mismatch",
         "returned": f"identity_match={identity_match} wellformed={identity_wellformed}"},
        {"step": "2. Crop", "saw": f"user file, crop_mode={a.crop_mode}",
         "decided": "supplied crop used" if a.crop_mode == "supplied" else ("on-device crop accepted" if box is not None else "crop refused — escalation"),
         "returned": f"crop_status={crop_status} box_valid={box_valid} sam_escalation_required={sam_escalation}"},
        {"step": "2b. Scan quality", "saw": f"user crop metrics={quality.get('metrics', {}) if quality else {}}",
         "decided": "pass" if not quality_problems else "fail — retake, never Counterfeit on quality alone",
         "returned": f"passed={not quality_problems} problems={quality_problems} multi_reference={multi_reference_info}"},
        {"step": "3. Front tells", "saw": "user crop vs reference for the supplied identity",
         "decided": tells_result["verdict"] if tells_result else "not measured",
         "returned": f"matches={(tells_result or {}).get('matches')} strong_mismatches={(tells_result or {}).get('strong_mismatches')}" if tells_result else reason},
        {"step": "4. Back tells", "saw": "back photo vs back reference, or no back photo",
         "decided": back_verdict if back_verdict is not None else "front-only, back not scored",
         "returned": back_reason},
        {"step": "5. Verification", "saw": f"checklist {checklist}",
         "decided": "pass" if verification_pass else "fail",
         "returned": f"failed={verification_failed} needs_input={needs_input}"},
        {"step": "6. Sign-off / filing", "saw": f"verification_pass={verification_pass} verdict before filing={verdict}",
         "decided": status,
         "returned": f"latch_signoff={latch_signoff} final_verdict={verdict}"},
    ]
    try:
        with open(progress_path, "w") as _f:
            json.dump({"status": status, "check_id": check_id, "parent_check_id": parent_check_id,
                       "resumed_from": a.resume_from, "branched_from": a.branch_from,
                       "plan": plan, "facts": facts, "source_flag": source_flag,
                       "slab_status": slab_status, "steps_completed": len(steps),
                       "last_step": "Loop/signoff", "steps": steps,
                       "loop_timeline": loop_timeline}, _f, indent=2)
        leftovers.save_check(a.out, {"check_id": check_id, "parent_check_id": parent_check_id,
                                     "resumed_from": a.resume_from, "branched_from": a.branch_from,
                                     "status": status, "verdict": verdict, "plan": plan,
                                     "facts": facts, "source_flag": source_flag,
                                     "slab_status": slab_status, "steps": steps})
    except Exception:
        pass

    # --- Latch: structural examiner, edits nothing ---
    checks = {
        "identity_supplied": bool(identity),
        "identity_matches_reference": identity_match,
        "crop_exists": os.path.exists(crop_path),
        "box_valid": box_valid,  # supplied-crop path has no invented box; ondevice box aspect-validated above
        "tells_measured": tells_result is not None,
        "verdict_allowed": verdict in ALLOWED,
        "verification_pass": verification_pass,
        "latch_signoff": latch_signoff,
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
        "identity_lookup": lookup_info,
        "lookup_proven": lookup_proven,
        "lookup_row": lookup_row,
        "lookup_method": lookup_method,
        "reference_for_identity_available": reference_for_identity_available,
        "reference": a.reference,
        "reference_identity": ref_identity,
        "reference_status": a.reference_status,
        "user_file": a.user,
        "crop_file": crop_path,
        "crop_mode": a.crop_mode,
        "crop_status": crop_status,
        "sam_escalation_required": sam_escalation,
        "back_supplied": bool(a.back),
        "back_reference_supplied": bool(a.back_reference),
        "back_verdict": back_verdict,
        "back_reason": back_reason,
        "back_tells": back_tells_result,
        "tells": tells_result,
        "scan_quality": quality,
        "scan_quality_passed": not quality_problems,
        "scan_quality_problems": quality_problems,
        "multi_reference": multi_reference_info,
        "steps": steps,
        "loop_timeline": loop_timeline,
        "checklist": checklist,
        "findings": findings,
        "back_findings": back_findings,
        "facts": facts,
        "fact_error": fact_error,
        "plan": plan,
        "source_flag": source_flag,
        "slab_status": slab_status,
        "slab_card_photo_supplied": bool(a.slab_card_photo),
        "check_id": check_id,
        "parent_check_id": parent_check_id,
        "resumed_from": a.resume_from,
        "branched_from": a.branch_from,
        "verification_pass": verification_pass,
        "verification_failed": verification_failed,
        "needs_input": needs_input,
        "status": status,
        "latch_signoff": latch_signoff,
        "slab_claimed": a.slab_claimed,
        "slab_cert_supplied": bool(a.slab_cert and a.slab_cert.strip()),
        "back_claimed": a.back_claimed,
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
