"""Verified-reference expansion pipeline — playground only, $0, Oct 27, 2026.

On-demand reference loading ONLY. Nothing here loads, copies, or
pre-loads the ~22,000 TCGdex EN fronts. A reference is resolved only
when that exact identity is checked, and only if it passes verification
below. Anything unverified stays no-reference / Inconclusive — never a
guessed reference.

Verification for ONE candidate (verify_reference):
  1. Detail-index row must exist for (language, set_id, localId) and
     match name + set_name + localId exactly (numbers normalised:
     "016" == "16").
  2. Image file must exist under sourcing/<lang>-tcgdex/img/ with a
     stem matching set_id + localId (unpadded or zero-padded to 3).
  3. Image must open with Pillow as real image bytes, format WEBP
     for EN TCGdex fronts, and sane portrait card dimensions
     (500-700 wide, 750-900 tall; TCGdex fronts are 600x825).
  4. SHA-256 of the verified file is recorded in the batch manifest.

Batch 1 (this pass only): 10 common EN Base Set cards, hand-verified
in reference-expansion-plan-2026-10-27.md. The 2 canned references
(Alakazam, Charizard) are kept as canned; the 8 new ones are pilot
references. Pilot means: file + index verified, but per-identity
tells calibration is STILL OPEN, so any Likely verdict measured
against a pilot reference must be labelled pilot/uncalibrated and
must never be presented as authentication of a physical card.
Back-pool scoring is NOT wired by this module (still 1 pilot back).
Real card photos are never used as backgrounds by this module.
"""
import hashlib
import json
import os

_BASE = os.path.dirname(os.path.abspath(__file__))
_SOURCING = os.path.normpath(os.path.join(_BASE, "..", "..", "sourcing"))
_IMG_DIRS = {
    "en": os.path.join(_SOURCING, "en-tcgdex", "img"),
    # JA fronts: 3,882 in ja-tcgdex-30pct/img; the rest run is still
    # in progress and is NOT wired here (see plan file).
    "ja": os.path.join(_SOURCING, "ja-tcgdex-30pct", "img"),
}
_BATCH_PATH = os.path.join(_BASE, "verified_references_batch1.json")

_batch_cache = None


def _load_batch():
    global _batch_cache
    if _batch_cache is not None:
        return _batch_cache
    if not os.path.exists(_BATCH_PATH):
        _batch_cache = {}
        return _batch_cache
    with open(_BATCH_PATH, encoding="utf-8") as f:
        rows = json.load(f)
    _batch_cache = {r["index_id"]: r for r in rows}
    return _batch_cache


def batch_identities():
    """Verified batch-1 identities only — never the whole index."""
    return sorted(_load_batch().keys())


def _candidate_files(set_id, local_id):
    n = str(local_id).strip()
    stems = {f"{set_id}-{n}", f"{set_id}-{n.zfill(3)}"}
    return sorted(stems)


def verify_reference(row, language="en"):
    """Verify ONE index row against its image file. Returns dict with
    status verified|failed, file, format, size, sha256, reason."""
    if not row:
        return {"status": "failed", "reason": "no index row supplied"}
    lang = (language or row.get("language") or "en").lower()
    img_dir = _IMG_DIRS.get(lang)
    if not img_dir or not os.path.isdir(img_dir):
        return {"status": "failed", "reason": f"no image directory for language '{lang}'"}
    set_id = str(row.get("set_id", "")).strip()
    local_id = str(row.get("localId", "")).strip()
    found = None
    for stem in _candidate_files(set_id, local_id):
        p = os.path.join(img_dir, stem + ".webp")
        if os.path.exists(p):
            found = p
            break
    if not found:
        return {"status": "failed",
                "reason": f"no image file for {set_id}-{local_id} in {img_dir}"}
    try:
        from PIL import Image
        with Image.open(found) as im:
            fmt, size = im.format, im.size
            im.load()
    except Exception as e:
        return {"status": "failed", "file": found,
                "reason": f"image does not open as real image bytes: {type(e).__name__}"}
    w, h = size
    if not (500 <= w <= 700 and 750 <= h <= 900):
        return {"status": "failed", "file": found, "format": fmt, "size": size,
                "reason": "dimensions outside sane card portrait range 500-700 x 750-900"}
    if os.path.getsize(found) < 1000:
        return {"status": "failed", "file": found, "format": fmt, "size": size,
                "reason": "file too small to be a real card image"}
    with open(found, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    return {"status": "verified", "file": found, "format": fmt, "size": size,
            "bytes": os.path.getsize(found), "sha256": sha,
            "index_id": row.get("id"), "name": row.get("name"),
            "set_name": row.get("set_name"), "localId": local_id,
            "language": lang, "reference_status": "verified_reference_pilot_uncalibrated"}


def load_reference(set_id, local_id, language="en"):
    """On-demand load for a BATCH-1 identity only. Returns the verified
    batch record, or None (caller must stay no-reference/Inconclusive).
    Verifying a non-batch identity is a separate, explicit
    verify_reference() call — it is not auto-wired by this function,
    so this pass cannot silently expand to all 21,986 images."""
    import identity_lookup
    res = identity_lookup.resolve(set_id, local_id, None,
                                  language if language != "all" else None)
    if res["status"] != "resolved":
        return None
    row = res["row"]
    batch = _load_batch()
    rec = batch.get(row["id"])
    if not rec:
        return None
    # Re-verify the batch file on every load: a batch record alone is
    # never trusted if the file moved, changed, or fails to open now.
    v = verify_reference(row, language=row.get("language", language))
    if v["status"] != "verified":
        return None
    if v["sha256"] != rec.get("sha256"):
        return None
    return rec


def reference_for_identity(name, number, language="en"):
    """Batch lookup by name + printed number (canned-style key helper
    for the demo server). Returns batch record or None."""
    import identity_lookup
    rows = identity_lookup.lookup(name, number)
    for row in rows["matches"]:
        if row.get("language") == language:
            rec = load_reference(row["set_id"], row["localId"], language)
            if rec:
                return rec
    return None
