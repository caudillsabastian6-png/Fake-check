#!/usr/bin/env python3
"""Why-this-verdict explainer — PLAYGROUND ONLY, AI loop keeper Oct 28 2026.

Q10 (Audit #15): the verdict screen had a raw tells table but no dedicated
plain-words explainer. This module builds one from the tells that were
ACTUALLY measured in a check — nothing else.

Rules (Agents 101 discipline):
- Only tells present in the tells dict are listed as measured. A tell key
  that is absent is listed under not-measured, never silently filled in.
- Unknown tell keys are still listed (they were measured); their plain
  label falls back to the key with underscores turned into spaces.
- The explainer never claims: grader verification, an official grade, SAM
  authentication, or a market price. Those are always under not-measured.
- Edge density is a rough print-texture signal only — the explainer says
  so, and never calls it a font or holo proof.
- If no tells were measured, the explainer says so plainly, and the
  combined sentence says the verdict does not rest on any measurement.
- $0 local only: no network, no model call, no spend.

Usage:
    from why_measured import explain
    why = explain(front_tells_result, back_tells_result, final_verdict,
                  back_supplied=True, back_reference_supplied=True)
"""
import os

# Plain-words meaning of each of the 5 tells_v2 tells, in check order.
PLAIN = {
    "aspect_ratio": "Card shape — how wide the card is compared with how tall it is",
    "mean_rgb": "Overall colour — the average colour across the whole card",
    "border_rgb": "Border colour — the colour of the printed frame at the top edge",
    "edge_density": "Print texture — how much sharp line work the picture contains "
                    "(a rough texture signal only, not proof of a font or holo pattern)",
    "colour_histogram": "Colour mix — how the card's colours are spread across light and dark shades",
}
KNOWN_ORDER = list(PLAIN)

# Things no V2 check ever measures. Always listed as not measured.
ALWAYS_NOT_MEASURED = [
    "Grader database check — no grader was contacted, so nothing here is grader-verified",
    "Official grade — condition wear is user-marked only, never a grade",
    "SAM authentication — SAM never authenticates a card",
    "Market price — no price was looked up or used in this verdict",
]


def _plain(tell):
    return PLAIN.get(tell, tell.replace("_", " "))


def _finding(v):
    """Plain-words finding for one measured tell entry."""
    diff = v.get("difference")
    thr = v.get("threshold")
    numbers = ""
    if isinstance(diff, (int, float)) and isinstance(thr, (int, float)):
        numbers = f" (difference {diff:.4f}, limit {thr})"
    if v.get("strong_mismatch"):
        return "differed a lot from the reference — a flag" + numbers
    if v.get("match"):
        return "matched the reference closely" + numbers
    return "differed somewhat — not a match, but not a strong flag" + numbers


def _side(tells_result, side_verdict):
    """Explainer for one side (front or back). Returns dict, never raises
    on a missing/odd tells result — it reports 'not measured' instead."""
    tells = (tells_result or {}).get("tells") or {}
    measured = []
    for key in KNOWN_ORDER + sorted(k for k in tells if k not in PLAIN):
        if key not in tells:
            continue
        v = tells[key] or {}
        measured.append({
            "tell": key,
            "plain": _plain(key),
            "finding": _finding(v),
            "difference": v.get("difference"),
            "threshold": v.get("threshold"),
            "match": bool(v.get("match")),
            "strong_mismatch": bool(v.get("strong_mismatch")),
        })
    missing = [f"{_plain(k)} ({k}) — not measured in this check"
               for k in KNOWN_ORDER if k not in tells]
    matches = sum(1 for m in measured if m["match"])
    strong = sum(1 for m in measured if m["strong_mismatch"])
    total = len(measured)
    if not tells_result or total == 0:
        sentence = ("No tells were measured on this side, so measurement alone "
                    "cannot support a Likely verdict from this side.")
    elif side_verdict == "Likely Genuine":
        sentence = (f"This side points to Likely Genuine: {matches} of {total} "
                    f"measured tells matched and none differed a lot.")
    elif side_verdict == "Likely Counterfeit":
        sentence = (f"This side points to Likely Counterfeit: {strong} of {total} "
                    f"measured tells differed a lot from the reference.")
    else:
        sentence = (f"This side alone does not settle it: {matches} of {total} "
                    f"measured tells matched and {strong} differed a lot.")
    return {"measured": measured, "missing": missing, "matches": matches,
            "strong_mismatches": strong, "total": total, "sentence": sentence}


def explain(front_tells_result, back_tells_result, final_verdict,
            back_supplied=False, back_reference_supplied=False):
    """Build the full why-measured explainer for one check.

    front_tells_result / back_tells_result: tells_v2-style result dicts
    (or None). final_verdict: the check's final combined verdict string.
    back_supplied / back_reference_supplied: whether a back photo and a
    back reference were given, so the back not-measured line names the
    exact reason instead of guessing.
    """
    front = _side(front_tells_result,
                  (front_tells_result or {}).get("verdict"))
    back = None
    back_sentence = None
    if back_tells_result and (back_tells_result.get("tells") or {}):
        back = _side(back_tells_result, back_tells_result.get("verdict"))
        back_sentence = back["sentence"]
    elif back_supplied and not back_reference_supplied:
        back_sentence = ("Back tells were not scored: a back photo was supplied "
                         "but no back reference was given, so the back was not measured.")
    elif back_supplied:
        back_sentence = ("Back tells were not scored: the back measurement did not "
                         "produce a result, so the back was not measured.")
    else:
        back_sentence = ("Back tells were not scored: no back photo was supplied, "
                         "so this is a front-only check.")

    not_measured = list(front["missing"])
    if back is None:
        not_measured.append(back_sentence)
    else:
        not_measured.extend(back["missing"])
    not_measured.extend(ALWAYS_NOT_MEASURED)

    if front["total"] == 0 and back is None:
        combined = ("No tells were measured, so this verdict does not rest on "
                    "any measurement — it stays Inconclusive rather than guessing.")
    elif final_verdict == "Likely Genuine":
        combined = ("Taken together, the measured tells above support Likely Genuine — "
                    "and only those tells support it. Anything under 'Not measured' "
                    "played no part in this verdict.")
    elif final_verdict == "Likely Counterfeit":
        combined = ("Taken together, the measured tells above support Likely Counterfeit — "
                    "and only those tells support it. Anything under 'Not measured' "
                    "played no part in this verdict.")
    else:
        combined = ("Taken together, the measured tells do not settle this check, so "
                    "the verdict stays Inconclusive rather than guessing.")

    return {"front": front, "back": back, "back_sentence": back_sentence,
            "not_measured": not_measured, "combined_sentence": combined,
            "measured_total": front["total"] + (back["total"] if back else 0)}
