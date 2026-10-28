#!/usr/bin/env python3
"""Agents 101 leftover ideas 5-9, translated to cards. Playground only, $0.

This module is deliberately separate from app_check_v2.py so the A-D
build is not rewritten: app_check_v2.py imports these helpers and calls
them at the moments that matter. None of these helpers can invent a
verdict, a tell, or a grader verification.

5. Plan tool — build_plan() lists the check steps BEFORE the check runs;
   update_plan() revises that plan when the checklist changes (e.g. a
   back or slab step is added, or an identity step fails). A plan is a
   description, never evidence.
6. Record_fact — record_fact() turns ONE measured tell into ONE fact
   carrying its measurement, threshold, reference, and source file
   (basename only, never a full path). A finding with no recorded fact
   is refused: record_fact() raises ValueError if any of match /
   difference / threshold is missing. No fact is ever created from
   claim text alone.
7. Flag do-not-use — flag_do_not_use() marks a source as excluded.
   Sources are flagged ONLY by an explicit flag: permission
   "unpermissioned" or "private", or an explicit flag label. There is
   no content sniffing, no guessing about ownership. A flagged source
   is excluded from findings entirely (filter_facts() drops its facts)
   and is never quoted as evidence. The checker treats a flagged front
   photo as needs_input, not as a verdict.
8. Real slab check — slab_check() requires BOTH a cert number AND a
   card-inside photo. Cert format alone (non-empty, plausible
   characters) is NOT grader verification: this $0 offline build has
   no grader database and makes no network call, so slab_status is
   always "..._not_grader_verified". Cert alone NEVER yields Genuine;
   the card-inside tells must still be measured and pass the normal
   verification gate. The workshop placeholder ("every signature
   consistent") is explicitly NOT used here.
9. Saved / resumable / branch checks — load_saved() / save_check()
   extend the existing progress.json approach in the check's own out
   directory. No new store, no database, no account. --pause-after
   writes a paused progress record and files NO verdict; --resume-from
   loads that record, keeps its prior steps/timeline, re-executes the
   deterministic $0 measurements, and files a verdict only if the
   verification gate passes on the resumed run; --branch-from starts
   a new check_id with parent_check_id set to the source check.
"""
import json
import os
import re
import uuid

PLAN_STEPS = [
    "1. Identity — prove Name|Set|Number and that the reference is for it",
    "2. Crop — card-only crop, aspect-checked; bad crop escalates, never verdicts",
    "3. Front tells — measure the 5 pixel tells against the reference",
    "4. Back tells — score separately if a back photo + back reference exist, else front-only honesty",
    "5. Slab check — if slabbed, cert + card inside, both required",
    "6. Verification — checklist proven, every finding cites a recorded fact",
    "7. Sign-off / filing — Latch gate; needs_input instead of a guess",
]


def build_plan(identity, back_claimed=False, slab_claimed=False, crop_mode="supplied"):
    """Plan BEFORE running. Steps are descriptions, not results."""
    steps = list(PLAN_STEPS)
    if not back_claimed:
        steps[3] = "4. Back tells — SKIPPED (no back claimed): front-only verdict, stated honestly"
    if not slab_claimed:
        steps[4] = "5. Slab check — SKIPPED (not claimed slabbed)"
    return {"identity": identity, "crop_mode": crop_mode,
            "back_claimed": bool(back_claimed), "slab_claimed": bool(slab_claimed),
            "steps": steps, "status": "planned"}


def update_plan(plan, completed_step, checklist_changes=None):
    """Revise the plan as the check progresses. Never rewrites history:
    completed steps stay listed, changes are appended as notes."""
    plan = dict(plan)
    plan["steps"] = list(plan.get("steps", []))
    plan["completed"] = list(plan.get("completed", []))
    if completed_step not in plan["completed"]:
        plan["completed"].append(completed_step)
    plan["notes"] = list(plan.get("notes", []))
    for change in (checklist_changes or []):
        note = str(change)
        if note not in plan["notes"]:
            plan["notes"].append(note)
    plan["status"] = "updated"
    return plan


def record_fact(tell_name, tell_value, side, source_file, reference_file):
    """One measured tell -> one fact. Refuses incomplete measurements."""
    if tell_value is None or not isinstance(tell_value, dict):
        raise ValueError(f"record_fact refused: tell {tell_name} has no measured value")
    for field in ("match", "strong_mismatch", "difference", "threshold"):
        if field not in tell_value:
            raise ValueError(f"record_fact refused: tell {tell_name} missing {field}")
    return {"tell": tell_name, "side": side,
            "match": bool(tell_value["match"]),
            "strong_mismatch": bool(tell_value["strong_mismatch"]),
            "difference": tell_value["difference"],
            "threshold": tell_value["threshold"],
            "source_file": os.path.basename(str(source_file)) if source_file else None,
            "reference_file": os.path.basename(str(reference_file)) if reference_file else None,
            "evidence": "measured tell, not claim text"}


def record_facts(tells_result, side, source_file, reference_file):
    """All tells in one tells result -> facts. Skips nothing silently:
    a tell that cannot be recorded raises, and the caller stays Inconclusive."""
    facts = []
    tells = (tells_result or {}).get("tells") or {}
    for name, value in tells.items():
        facts.append(record_fact(name, value, side, source_file, reference_file))
    return facts


def flag_do_not_use(source_label, permission, reason):
    """Explicit flag only. permission must be 'unpermissioned' or
    'private' to flag; anything else is recorded as not-flagged, so an
    ordinary owner photo is never excluded by accident."""
    flagged = permission in ("unpermissioned", "private")
    return {"source_label": source_label, "permission": permission,
            "reason": reason, "flagged": flagged,
            "excluded_from_evidence": flagged}


def filter_facts(facts, flags):
    """Drop facts from flagged sources. Never quote a flagged source."""
    if not any(f.get("flagged") for f in flags):
        return list(facts)
    return []  # front-photo facts are the only facts in this build; a
    # flagged front source leaves no quotable evidence at all.


def slab_check(slab_claimed, cert, card_inside_photo):
    """Real slab gate, honestly labelled. No grader DB, no network, so
    nothing here is ever 'grader verified'. Returns (complete, status,
    needs_input_items)."""
    if not slab_claimed:
        return True, "not_claimed_slabbed", []
    cert_ok = bool(cert and cert.strip() and re.fullmatch(r"[A-Za-z0-9\-]{4,40}", cert.strip()))
    card_ok = bool(card_inside_photo and os.path.exists(card_inside_photo))
    missing = []
    if not cert_ok:
        missing.append("slab_cert: card claimed slabbed but no usable cert number was supplied")
    if not card_ok:
        missing.append("slab_card_inside: card claimed slabbed but no card-inside photo was supplied (cert + card inside, every time)")
    if missing:
        return False, "incomplete_cert_or_card_inside", missing
    return True, "cert_and_card_present_not_grader_verified", []


def new_check_id():
    return "check-" + uuid.uuid4().hex[:12]


def save_check(out_dir, record):
    path = os.path.join(out_dir, "check.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2)
    return path


def load_saved(out_dir):
    """Load a prior check's progress/result from its OWN out directory.
    Returns None if there is no saved record (not an error to resume)."""
    for name in ("result.json", "progress.json"):
        path = os.path.join(out_dir, name)
        if os.path.exists(path):
            try:
                with open(path) as f:
                    return json.load(f)
            except Exception:
                continue
    return None
