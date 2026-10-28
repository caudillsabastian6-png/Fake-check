"""Step 2 matcher wrapper — PLAYGROUND / TEST ONLY, Oct 28, 2026.
Uses ONLY the identity index already on file (37,369 EN+JA rows) via
playground/app-v2-merged/identity_lookup.py. No new pool, no merge.

Honest limit, stated in code so it cannot be mistaken for image recognition:
  - There is NO image-to-identity matcher on file that can name a card
    from pixels alone at $0 (inline_classifier takes tell numbers, not
    pixels, and needs model calls which this step does not use).
  - Therefore: set + printed number (or name + number with an exact set)
    resolves via identity_lookup.resolve(). An image supplied WITHOUT
    set/number returns needs_input naming what is missing — never a guess.
  - Proposed image-match threshold: NONE SET in this impl. A future
    image matcher must have a threshold named and approved by the owner
    before image-only matching can count as passed. Do not quote one.
"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.expanduser("~/workspace/fake-check/playground/app-v2-merged")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
import identity_lookup  # noqa: E402

def counts():
    return identity_lookup.counts()

def match(set_query=None, local_id=None, name=None, language=None, image_supplied=False):
    """Returns resolve() result plus a test label and an image_note.
    Never guesses. Image-only (no set/number) is needs_input."""
    r = identity_lookup.resolve(set_query=set_query, local_id=local_id, name=name, language=language)
    out = {
        "status": r["status"],
        "row": ({"id": r["row"].get("id"), "name": r["row"].get("name"),
                 "set_name": r["row"].get("set_name"), "set_id": r["row"].get("set_id"),
                 "localId": r["row"].get("localId"), "language": r["row"].get("language")}
                if r["row"] else None),
        "method": r["method"],
        "matches": [{"id": m.get("id"), "name": m.get("name"), "set_name": m.get("set_name"),
                     "localId": m.get("localId"), "language": m.get("language")} for m in r["matches"][:10]],
        "name_candidates": [{"id": m.get("id"), "name": m.get("name"), "set_name": m.get("set_name"),
                             "localId": m.get("localId")} for m in r["name_candidates"][:10]],
        "needs_input": list(r["needs_input"]),
        "label": "TEST MATCH ONLY — NOT A REAL CHECK, NOT A VERDICT",
        "image_match_threshold": None,
        "image_match_note": ("No image-to-identity matcher is on file at $0; "
                             "an image alone cannot resolve an identity in this impl. "
                             "Supply set + printed number.") if image_supplied and not (set_query and local_id) else None,
    }
    if image_supplied and not (set_query and local_id) and not out["needs_input"]:
        out["needs_input"].append("test-match: image alone cannot resolve an identity in this prototype — supply set + printed number; nothing was guessed")
    return out
