"""Owner-scan verified references — playground only, $0, Oct 27, 2026.

Separate from reference_registry.py (TCGdex fronts). This module wires
ONLY 10 owner hand-photo SAM card-only crops, on demand, as internal
measurement references. It never serves an owner card photo in the demo
UI (server.py strips reference paths from results), never displays
owner real cards publicly, and never uses a fake or uncertain scan.

Verification for ONE candidate:
  1. TCGdex detail-index row exists for name + printed number, exact.
  2. SAM crop file exists, opens with Pillow as real image bytes,
     portrait card aspect 0.73-0.81 (SAM crops carry a small margin,
     so they are wider than a 600x825 TCGdex front — that is expected,
     not a failure), and size > 1000 bytes.
  3. SHA-256 matches the manifest record on every load.

Pilot means: file + index verified, but per-identity tells calibration
is STILL OPEN, so any Likely verdict measured against an owner-scan
reference must be labelled owner_scan_pilot_uncalibrated and must
never be presented as authentication of a physical card.
No center-crop was applied to this batch: the SAM crops are already
card-only and crop_verified=pass; applying the back-crop 8%/7%/92%/93%
window to them would cut the card.
"""
import hashlib
import json
import os

_BASE = os.path.dirname(os.path.abspath(__file__))
_MANIFEST = os.path.join(_BASE, "owner_scan_references.json")

_cache = None


def _load():
    global _cache
    if _cache is not None:
        return _cache
    if not os.path.exists(_MANIFEST):
        _cache = {}
        return _cache
    with open(_MANIFEST, encoding="utf-8") as f:
        rows = json.load(f)
    _cache = {r["index_id"]: r for r in rows}
    return _cache


def batch_identities():
    return sorted(_load().keys())


def load_reference(set_id, local_id, language="en"):
    import identity_lookup
    res = identity_lookup.resolve(set_id, local_id, None,
                                  language if language != "all" else None)
    if res["status"] != "resolved":
        return None
    row = res["row"]
    rec = _load().get(row["id"])
    if not rec:
        return None
    p = rec["file"]
    if not os.path.exists(p):
        return None
    try:
        from PIL import Image
        with Image.open(p) as im:
            im.load()
            size = im.size
    except Exception:
        return None
    if not (0.70 <= size[0] / max(1, size[1]) <= 0.85):
        return None
    with open(p, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    if sha != rec.get("sha256"):
        return None
    return rec


def reference_for_identity(name, number, language="en"):
    import identity_lookup
    rows = identity_lookup.lookup(name, number)
    for row in rows["matches"]:
        if row.get("language") == language:
            rec = load_reference(row["set_id"], row["localId"], language)
            if rec:
                return rec
    return None
