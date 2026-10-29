#!/usr/bin/env python3
"""Real or Replica — App V2 LOCAL playground demo server. LOCAL ONLY.

Serves index.html on 127.0.0.1 only and runs the V2 playground checker
(app_check_v2.py, $0, Pillow only, no network, no SAM/Baseten/Meta calls)
for uploads. Never serves reference card images: the UI shows verdict +
tells numbers only, never a real card photo.

Run:  python3 server.py
Then: open http://127.0.0.1:8765/ in a local browser.
Stop:  Ctrl+C. Nothing is deployed, published, or sent anywhere.
No keys, tokens, or secrets are read or written by this server.
"""
import json, os, subprocess, sys, tempfile, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
# Standalone fix (Oct 29, 2026): the checker ships in this pack, in ../checker.
V2 = os.path.normpath(os.path.join(HERE, "..", "checker"))
sys.path.insert(0, V2)
import identity_lookup  # noqa: E402  ($0, local EN/JA detail index only)
import reference_registry  # noqa: E402  ($0, on-demand verified batch only)
import owner_scan_registry  # noqa: E402  ($0, owner SAM-crop batch only, never served as photos)
CHECKER = os.path.join(V2, "app_check_v2.py")


def _norm_number(n):
    return identity_lookup.norm_number(n)


def _canned_ref_for(name, number):
    """Canned reference key whose name + printed number match, or None.
    Only 2 canned references exist; every other indexed identity has
    no reference image in the playground."""
    for key in REFS:
        parts = [x.strip() for x in key.split("|")]
        if len(parts) == 3 and parts[0].strip().lower() == str(name).strip().lower() \
                and _norm_number(parts[2]) == _norm_number(number):
            return key
    return None


def _lookup_payload(set_q, number, name, language):
    res = identity_lookup.resolve(set_q, number, name,
                                  language if language not in (None, "", "all") else None)
    counts = identity_lookup.counts()
    row = res.get("row")
    canned = _canned_ref_for(row["name"], row["localId"]) if row else None
    batch = None
    if row and not canned:
        # On-demand batch load only: re-verifies file + sha256 on load,
        # returns None for any non-batch identity (even if a TCGdex
        # file exists for it) — this pass wires 10, not 21,986.
        batch = reference_registry.load_reference(row["set_id"], row["localId"],
                                                  row.get("language", "en"))
    owner_batch = None
    if row and not canned and not batch:
        owner_batch = owner_scan_registry.load_reference(
            row["set_id"], row["localId"], row.get("language", "en"))
    if batch:
        ref_record = batch
    elif owner_batch:
        ref_record = owner_batch
    else:
        ref_record = None
    return {"status": res["status"], "method": res["method"], "row": row,
            "matches": res["matches"], "name_candidates": res["name_candidates"],
            "needs_input": res["needs_input"],
            "reference_for_identity_available": bool(canned or batch or owner_batch),
            "canned_identity": canned,
            "batch_reference": ref_record,
            "owner_scan_reference": bool(owner_batch),
            "reference_status": ("canned" if canned else
                                 (ref_record["reference_status"] if ref_record else None)),
            "verified_batch_count": len(reference_registry.batch_identities()),
            "owner_scan_batch_count": len(owner_scan_registry.batch_identities()),
            "searchable": counts,
            "disclaimer": "Lookup is identity only, never authentication. "
                          "A lookup hit without a reference image stays Inconclusive.",
            "api_calls": 0, "spend_usd": 0.0}
# Standalone fix (Oct 29, 2026): canned reference photos are card photos
# and are never shipped in this pack. Drop local copies into demo/fixtures/
# with these names to enable the canned endpoints; absent files degrade
# honestly (the handlers below already check os.path.exists).
REFS = {
    "Alakazam|Base|1": os.path.join(HERE, "fixtures", "sr-0001-BS-1.png"),
    "Charizard|Base|4": os.path.join(HERE, "fixtures", "sr-0004-BS-4.png"),
}
# Pilot back reference ONLY: one genuine English back crop. Backs are
# mostly uniform, so this scores back design/print, NOT identity.
# It is NOT Alakazam/Charizard-specific, and NOT a back pool yet.
BACK_REF = os.path.join(HERE, "fixtures", "web-05-disco-charizard-back-REAL.jpg")  # fixtures/ — see REFS note
CANNED = {
    "test-a": (os.path.join(HERE, "fixtures", "cropped.png"),
               "Alakazam|Base|1", "Alakazam|Base|1"),
    "test-b": (os.path.join(HERE, "fixtures", "cropped.png"),
               "Alakazam|Base|1", "Charizard|Base|4"),
}

def _other_copies_phone_files(identity):
    """Second (and further) verified phone copies from the
    other-copies record (other-copies-2026-10-27.json). Only copies
    whose kind is additional_copy, whose source starts with 'phone',
    that pass the quality gate and are not blurry, are returned —
    raw hand/carpet forms and same-photo duplicates are NEVER
    returned (the JSON marks them same_photo_raw_form, not
    additional_copy, and they are excluded here by kind). Each
    file's SHA-256 is re-checked against the JSON record on load,
    exactly like the owner-scan registry does for its own files.
    In practice this adds exactly one file today: Chatot's second
    distinct phone SAM crop. Base identities add nothing (their
    additional copies are stock, not phone); other owner identities
    add nothing (their additional copy is stock)."""
    parts = [x.strip() for x in identity.split("|")]
    if len(parts) != 3:
        return []
    import hashlib
    path = os.path.join(V2, "..", "other-copies-2026-10-27.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            rows = json.load(f)
    except Exception:
        return []
    out = []
    for row in rows:
        if str(row.get("name", "")).strip().lower() != parts[0].strip().lower():
            continue
        if _norm_number(str(row.get("localId", ""))) != _norm_number(parts[2]):
            continue
        for c in row.get("copies", []):
            if c.get("kind") != "additional_copy":
                continue
            if not str(c.get("source", "")).startswith("phone"):
                continue
            if not c.get("quality_passed") or c.get("blurry_by_gate"):
                continue
            f = c.get("file")
            if not f or not os.path.exists(f):
                continue
            try:
                from PIL import Image
                with Image.open(f) as im:
                    im.load()
                    aspect = im.size[0] / max(1, im.size[1])
                if not (0.70 <= aspect <= 0.85):
                    continue
                with open(f, "rb") as fh:
                    sha = hashlib.sha256(fh.read()).hexdigest()
                if c.get("sha256") and sha != c["sha256"]:
                    continue
            except Exception:
                continue
            out.append((f, "owner-2nd"))
    return out


def _all_verified_reference_files(identity):
    """All verified reference files for one identity, in use order,
    as (file, source) pairs, deduplicated, max 5. Sources: canned,
    batch (TCGdex stock front), owner (owner-scan phone SAM crop),
    owner-2nd (second verified phone copy from other-copies).
    No file path is ever returned to the UI — callers use only the
    count, the source names, and the files as checker inputs.
    NOTE: the registry helpers below are EN-only, so a JA identity
    resolves its lookup row but finds no batch/owner file here."""
    parts = [x.strip() for x in identity.split("|")]
    if len(parts) != 3:
        return []
    files = []
    def add(f, src):
        if f and os.path.exists(f) and all(x[0] != f for x in files):
            files.append((f, src))
    if identity in REFS:
        add(REFS[identity], "canned")
    batch = reference_registry.reference_for_identity(parts[0], parts[2], "en")
    if batch and batch.get("file"):
        add(batch["file"], "batch")
    owner = owner_scan_registry.reference_for_identity(parts[0], parts[2], "en")
    if owner and owner.get("file"):
        add(owner["file"], "owner")
    for f, src in _other_copies_phone_files(identity):
        add(f, src)
    return files[:5]


def _multi_reference_for(identity):
    """Verified references for one identity, deduplicated by file.
    Canned + verified TCGdex batch + verified owner-scan batch only.
    No file path is returned to the UI — only counts and mode, so an
    owner card photo is never served as an image."""
    files = _all_verified_reference_files(identity)
    parts = [x.strip() for x in identity.split("|")]
    if len(parts) != 3:
        return {"identity": identity, "reference_count": 0, "reference_mode": "none",
                "note": "Identity must be Name|Set|Number."}
    mode = "median" if len(files) > 1 else ("single" if len(files) == 1 else "none")
    return {"identity": identity, "reference_count": len(files), "reference_mode": mode,
            "verified_reference_sources": [src for _, src in files],
            "note": ("Median across verified references, pilot/uncalibrated until per-identity "
                     "calibration is shown." if mode == "median" else
                     "Single verified reference." if mode == "single" else
                     "No verified reference — a check stays Inconclusive.")}


def _apply_cross_source_guard(d, files):
    """HONESTY GATE, /api/check uploads only (never canned pipeline tests,
    never the direct checker). Tells v2 fails fake separation
    phone-vs-stock even calibrated, so a fresh-upload Likely verdict
    against anything but an owner-scan-only (phone-vs-phone) reference
    set is NOT shipped: it stays Inconclusive, tells numbers still
    shown, reason names the block. Owner-scan-only sets keep their
    Likely verdict, still labelled pilot/uncalibrated by the checker."""
    if d.get("verdict") not in ("Likely Genuine", "Likely Counterfeit"):
        return d
    if files and all(src.startswith("owner") for _, src in files):
        return d
    original = d["verdict"]
    d["blocked_likely_verdict"] = original
    d["cross_source_blocked"] = True
    d["verdict"] = "Inconclusive"
    d["status"] = "inconclusive"
    d["latch_signoff"] = False
    d["verdict_reason"] = (
        "cross_source_likely_blocked: original Likely verdict '" + original + "' is NOT shipped — "
        "tells v2 fails fake separation phone-vs-stock even calibrated, so a fresh-upload check "
        "against a stock/canned reference stays Inconclusive. Tells numbers below are still measured "
        "and shown; a Likely verdict needs a source-matched, per-identity calibrated reference set, "
        "which this playground does not have for this identity.")
    return d


def _scrub_paths(obj):
    """Recursively replace any absolute file path in a result dict
    (notably the loop_timeline string that embeds multi_reference_info
    with its reference_files list) with a placeholder. The UI must
    never see a reference file path, so an owner card photo can never
    be located or served from a result payload."""
    import re
    if isinstance(obj, dict):
        return {k: _scrub_paths(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_scrub_paths(v) for v in obj]
    if isinstance(obj, str):
        return re.sub(r"/(?:home|tmp)/[A-Za-z0-9_./-]+", "[verified-reference-file]", obj)
    return obj


def run_check(user_path, identity, ref_identity, back_path=None, slab_claimed=False, slab_cert=None, back_claimed=False, ref_status=None, additional_refs=None, explicit_ref=None):
    if explicit_ref:
        # Caller-resolved primary (used by /api/check after SHA
        # exclusion, so the primary is never the user's own photo).
        # Caller must pass the matching ref_status; no default is
        # invented here (a batch primary is not an owner primary).
        ref = explicit_ref
    else:
        ref = REFS.get(ref_identity)
    if not ref:
        # Batch reference, resolved on demand by the caller (file +
        # sha256 re-verified in reference_registry.load_reference).
        batch = None
        parts = [x.strip() for x in ref_identity.split("|")]
        if len(parts) == 3:
            batch = reference_registry.reference_for_identity(parts[0], parts[2], "en")
        if batch:
            ref = batch["file"]
            ref_status = batch["reference_status"]
        if not batch:
            owner_batch = owner_scan_registry.reference_for_identity(parts[0], parts[2], "en")
            if owner_batch:
                ref = owner_batch["file"]
                ref_status = owner_batch["reference_status"]
    if not ref or not os.path.exists(ref):
        return {"verdict": "Inconclusive", "verdict_reason": "reference_unreadable_offline",
                "verdict_disclaimer": "Estimate only, never official, never guaranteed.",
                "identity": identity, "api_calls": 0, "spend_usd": 0.0}
    out = os.path.join(tempfile.mkdtemp(prefix="v2demo-"), "out")
    cmd = [sys.executable, CHECKER, "--user", user_path, "--reference", ref,
           "--identity", identity, "--reference-identity", ref_identity,
           "--crop-mode", "supplied", "--out", out]
    if additional_refs:
        # Multi-reference median, wired: tells are measured against the
        # median across primary + these registry-verified files, not
        # just the single primary. Caller must pass verified files only.
        cmd += ["--additional-references", ",".join(additional_refs)]
    if ref_status:
        cmd += ["--reference-status", ref_status]
    if back_path and os.path.exists(BACK_REF):
        cmd += ["--back", back_path, "--back-reference", BACK_REF]
    if slab_claimed:
        # Demo UI: the front photo IS the card-inside photo (the card
        # photographed inside its slab). Cert + that photo, every time.
        cmd += ["--slab-claimed", "--slab-card-photo", user_path]
    if slab_cert:
        cmd += ["--slab-cert", slab_cert]
    if back_claimed:
        cmd += ["--back-claimed"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    p = os.path.join(out, "result.json")
    if os.path.exists(p):
        with open(p) as f:
            d = json.load(f)
        if ref_status:
            d["reference_status"] = ref_status
            d["pilot_reference_note"] = ("Pilot reference: file + index verified, "
                "but per-identity tells calibration is still open — a Likely verdict here is a "
                "pipeline measurement, not authentication of a physical card.")
        # Strip anything that could leak a file path / image to the UI.
        d.pop("user_file", None); d.pop("crop_file", None); d.pop("reference", None)
        if d.get("tells"): d["tells"].pop("user_image", None); d["tells"].pop("reference_image", None); d["tells"].pop("reference_files", None)
        if d.get("back_tells"): d["back_tells"].pop("user_image", None); d["back_tells"].pop("reference_image", None)
        if isinstance(d.get("multi_reference"), dict): d["multi_reference"].pop("reference_files", None)
        if d.get("back_tells"): d["back_tells"].pop("user_image", None); d["back_tells"].pop("reference_image", None)
        return _scrub_paths(d)
    return {"verdict": "Inconclusive", "verdict_reason": f"checker_failed: {r.stderr[-300:]}",
            "verdict_disclaimer": "Estimate only, never official, never guaranteed.",
            "identity": identity, "api_calls": 0, "spend_usd": 0.0}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, body, ctype="application/json", code=200):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if urlparse(self.path).path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f: self._send(f.read(), "text/html")
        elif urlparse(self.path).path in ("/hero-video.mp4", "/hero-poster.webp"):
            # Local demo assets only, exact-name whitelist — the hero
            # video/poster referenced by index.html, so a served
            # playground preview actually plays instead of 404ing.
            name = urlparse(self.path).path.lstrip("/")
            ctype = "video/mp4" if name.endswith(".mp4") else "image/webp"
            with open(os.path.join(HERE, name), "rb") as f: self._send(f.read(), ctype)
        elif urlparse(self.path).path == "/api/identities":
            self._send(json.dumps(sorted(REFS)))
        elif urlparse(self.path).path == "/api/lookup-stats":
            self._send(json.dumps({"canned_identities": sorted(REFS),
                                   "verified_batch_identities": reference_registry.batch_identities(),
                                   "measurable_identities": 10,
                                   "searchable": identity_lookup.counts(),
                                   "note": "Lookup is identity only, never authentication. "
                                           "2 canned + 8 pilot batch references are measurable; "
                                           "pilot references are file+index verified but tells-uncalibrated."}))
        elif urlparse(self.path).path == "/api/multi-reference":
            q = parse_qs(urlparse(self.path).query)
            self._send(json.dumps(_multi_reference_for(q.get("identity", [""])[0] or "")))
        elif urlparse(self.path).path == "/api/lookup":
            q = parse_qs(urlparse(self.path).query)
            get = lambda k: (q.get(k, [""])[0] or "")
            self._send(json.dumps(_lookup_payload(get("set"), get("number"), get("name") or None, get("language"))))
        else:
            self._send("not found", "text/plain", 404)
    def do_POST(self):
        path = urlparse(self.path).path
        n = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(n) if n else b""
        try:
            if path == "/api/canned":
                name = json.loads(raw or b"{}").get("test")
                if name not in CANNED: return self._send(json.dumps({"error": "unknown test"}), code=400)
                user, ident, refid = CANNED[name]
                # Canned pipeline test, labelled as such everywhere it
                # is shown — never presented as a real verdict. The
                # cross-source guard is NOT applied here: this is a
                # measurement test, not a shipped verdict.
                files = _all_verified_reference_files(refid)
                d = run_check(user, ident, refid, additional_refs=[f for f, _ in files[1:]])
                d["is_canned_test"] = True
                d["canned_test"] = name
                d["canned_label"] = "SAMPLE — canned pipeline test, not a real verdict."
                d["verdict_reason"] = "SAMPLE — canned pipeline test, not a real verdict. " + str(d.get("verdict_reason", ""))
                d["verified_reference_sources"] = [src for _, src in files]
                return self._send(json.dumps(d))
            if path == "/api/check":
                # Minimal multipart parse: file field 'photo', text field 'identity'.
                import re
                ct = self.headers.get("Content-Type", "")
                m = re.search(r"boundary=(.+)", ct)
                if not m: return self._send(json.dumps({"error": "multipart required"}), code=400)
                bnd = ("--" + m.group(1).strip()).encode()
                parts = raw.split(bnd)
                photo, back_photo, identity = None, None, "Alakazam|Base|1"
                slab_claimed, slab_cert, back_claimed = False, None, False
                for part in parts:
                    if b'Content-Disposition' not in part: continue
                    head, _, body = part.partition(b"\r\n\r\n")
                    body = body.rsplit(b"\r\n", 1)[0]
                    if b'name="photo"' in head and body.strip():
                        photo = body
                    if b'name="back_photo"' in head and body.strip():
                        back_photo = body
                    if b'name="identity"' in head:
                        identity = body.decode().strip() or identity
                    if b'name="slab_claimed"' in head:
                        slab_claimed = body.decode().strip().lower() in ("on", "true", "1")
                    if b'name="slab_cert"' in head:
                        slab_cert = body.decode().strip() or None
                    if b'name="back_claimed"' in head:
                        back_claimed = body.decode().strip().lower() in ("on", "true", "1")
                if photo is None: return self._send(json.dumps({"error": "no photo uploaded"}), code=400)
                if identity not in REFS:
                    # Lookup path: an identity from the EN/JA index that
                    # is not a canned reference. Never guess, never
                    # measure tells without a reference for that card.
                    parts = [x.strip() for x in identity.split("|")]
                    if len(parts) != 3:
                        return self._send(json.dumps({"error": "unknown identity"}), code=400)
                    payload = _lookup_payload(parts[1], parts[2], parts[0], None)
                    if payload["status"] != "resolved":
                        return self._send(json.dumps({
                            "verdict": "Inconclusive", "status": "needs_input",
                            "verdict_reason": "needs_input: " + "; ".join(payload["needs_input"]),
                            "needs_input": payload["needs_input"],
                            "identity_lookup": payload,
                            "verdict_disclaimer": "Estimate only, never official, never guaranteed.",
                            "identity": identity, "api_calls": 0, "spend_usd": 0.0}))
                    if not payload["reference_for_identity_available"]:
                        return self._send(json.dumps({
                            "verdict": "Inconclusive", "status": "inconclusive",
                            "verdict_reason": "identity_found_but_no_reference_image_for_identity: "
                                f"{payload['row']['id']} ({payload['row']['language']}, "
                                f"{payload['row']['set_name']} {payload['row']['localId']}) is in the EN/JA index, "
                                "but no verified reference image for this identity exists in the playground "
                                "(2 canned + 8 pilot batch references only) — tells cannot be measured, verdict stays Inconclusive.",
                            "identity_lookup": payload,
                            "verdict_disclaimer": "Estimate only, never official, never guaranteed.",
                            "identity": identity, "api_calls": 0, "spend_usd": 0.0}))
                    # Resolved AND a reference matches: canned takes
                    # precedence; otherwise a verified batch reference
                    # (identity kept as given, run_check resolves it
                    # on demand and labels it pilot/uncalibrated).
                    if payload["canned_identity"]:
                        identity = payload["canned_identity"]
                tmp = os.path.join(tempfile.mkdtemp(prefix="v2demo-up-"), "upload.png")
                with open(tmp, "wb") as f: f.write(photo)
                back_tmp = None
                if back_photo:
                    back_tmp = os.path.join(tempfile.mkdtemp(prefix="v2demo-back-"), "back.png")
                    with open(back_tmp, "wb") as f: f.write(back_photo)
                # End-to-end wiring: all verified references for this
                # identity feed the median (step 3), not just the
                # primary. back_claimed is honoured by the checker
                # (step 4/5 gates); the cross-source guard (step 3b)
                # blocks shipped Likely verdicts on stock references.
                # SHA EXCLUSION (non-circularity): a reference file
                # whose SHA-256 equals the uploaded photo's SHA is
                # removed from this check's reference set, so a
                # tester uploading a known reference photo is
                # measured against the OTHER verified copies, never
                # against itself. If that leaves no reference, the
                # check stays Inconclusive instead of self-matching.
                import hashlib
                files = _all_verified_reference_files(identity)
                user_sha = hashlib.sha256(photo).hexdigest()
                kept = []
                for f, src in files:
                    try:
                        with open(f, "rb") as fh:
                            if hashlib.sha256(fh.read()).hexdigest() == user_sha:
                                continue
                    except Exception:
                        pass
                    kept.append((f, src))
                if files and not kept:
                    return self._send(json.dumps({
                        "verdict": "Inconclusive", "status": "needs_input",
                        "verdict_reason": "needs_input: uploaded photo matches a verified reference file by SHA — "
                            "it is that reference itself, not a new card to check; upload a different photo of the card.",
                        "needs_input": ["photo_matches_reference_itself: upload a different photo of the card"],
                        "verdict_disclaimer": "Estimate only, never official, never guaranteed.",
                        "identity": identity, "api_calls": 0, "spend_usd": 0.0}))
                if not back_photo:
                    back_claimed = False
                primary, primary_src = kept[0] if kept else (None, None)
                primary_status = None
                if primary_src in ("owner", "owner-2nd"):
                    primary_status = "owner_scan_pilot_uncalibrated"
                elif primary_src == "batch":
                    primary_status = "verified_reference_pilot_uncalibrated"
                d = run_check(tmp, identity, identity, back_tmp, slab_claimed, slab_cert, back_claimed,
                              ref_status=primary_status,
                              additional_refs=[f for f, _ in kept[1:]],
                              explicit_ref=primary)
                d["verified_reference_sources"] = [src for _, src in kept]
                d["reference_count_after_sha_exclusion"] = len(kept)
                d = _apply_cross_source_guard(d, kept)
                return self._send(json.dumps(d))
            return self._send(json.dumps({"error": "unknown endpoint"}), code=404)
        except Exception as e:
            return self._send(json.dumps({"verdict": "Inconclusive",
                "verdict_reason": f"demo_server_error: {type(e).__name__}",
                "verdict_disclaimer": "Estimate only, never official, never guaranteed.",
                "api_calls": 0, "spend_usd": 0.0}), code=500)

if __name__ == "__main__":
    print("Real or Replica V2 demo — LOCAL ONLY — http://127.0.0.1:8765/  (Ctrl+C to stop, nothing deployed)")
    ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
