"""Backend-tie Steps 1-3 — FastAPI prototype, PLAYGROUND / TEST ONLY.
Localhost only. No deploy, no Modal, no live endpoint, no spend, no training.
Retention (default, owner did not name a different note): test photos live
ONLY in ./uploads/ inside this impl folder, deleted after the test run
(see delete_test_uploads.py and POST /v1/test-session/{id}/delete).
Nothing here ships a verdict: shipped_verdict is always null.
Run: /tmp/backend-tie-venv/bin/uvicorn app:app --host 127.0.0.1 --port 8765
from this folder. Stop it when testing ends; do not leave it running.
"""
import hashlib, json, os, shutil, uuid
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image
import io

import matcher, tells_engine

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)
MAX_BYTES = 20 * 1024 * 1024
TEST_LABEL = "TEST ONLY — NOT A REAL CHECK, NOT A VERDICT"

app = FastAPI(title="Backend-tie Steps 1-3 test prototype (playground only)")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8765", "http://localhost:8765"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])

def _save(session_dir, side, up: UploadFile):
    data = up.file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(400, f"{side} photo too large: {len(data)} bytes, limit {MAX_BYTES} — upload failed, no verdict, try a smaller photo")
    try:
        im = Image.open(io.BytesIO(data)); im.verify()
        im = Image.open(io.BytesIO(data)); size = list(im.size)
    except Exception:
        raise HTTPException(400, f"{side} photo is not a readable image — upload failed, no verdict, try a different photo file")
    sha = hashlib.sha256(data).hexdigest()
    path = os.path.join(session_dir, f"{side}-{sha[:12]}.bin")
    with open(path, "wb") as f:
        f.write(data)
    return {"present": True, "bytes": len(data), "sha256": sha, "size_px": size, "stored_as": os.path.basename(path)}

@app.get("/health")
def health():
    return {"status": "ok", "prototype": True, "deploy": False, "steps": "1-3 test only",
            "verdict": "none shipped", "label": TEST_LABEL}

@app.post("/v1/test-upload")
def test_upload(front: UploadFile = File(None), back: UploadFile = File(None)):
    session_id = uuid.uuid4().hex[:16]
    sdir = os.path.join(UPLOADS, session_id); os.makedirs(sdir, exist_ok=True)
    receipt = {"session_id": session_id, "label": TEST_LABEL, "verdict": None,
               "front": {"present": False}, "back": {"present": False}, "missing": []}
    try:
        if front is not None and front.filename:
            receipt["front"] = _save(sdir, "front", front)
        if back is not None and back.filename:
            receipt["back"] = _save(sdir, "back", back)
    except HTTPException:
        shutil.rmtree(sdir, ignore_errors=True); raise
    if not receipt["front"]["present"]:
        receipt["missing"].append("front")
    if not receipt["back"]["present"]:
        receipt["missing"].append("back")
    receipt["note"] = ("Receipt only. No identity match, no tells, no verdict from this endpoint. "
                       + ("Missing: " + ", ".join(receipt["missing"]) + " — reported as missing, never paired with a generic image." if receipt["missing"] else "Front and back both received for this test session."))
    with open(os.path.join(sdir, "receipt.json"), "w") as f:
        json.dump(receipt, f, indent=2)
    return receipt

class MatchIn(BaseModel):
    session_id: str = ""
    set: str = ""
    number: str = ""
    name: str = ""
    language: str = ""
    image_supplied: bool = False

@app.post("/v1/test-match")
def test_match(body: MatchIn):
    return matcher.match(set_query=body.set or None, local_id=body.number or None,
                         name=body.name or None, language=body.language or None,
                         image_supplied=body.image_supplied)

@app.post("/v1/test-tells")
def test_tells(front_user: UploadFile = File(None), front_ref: UploadFile = File(None),
               back_user: UploadFile = File(None), back_ref: UploadFile = File(None)):
    import tempfile
    tmp = tempfile.mkdtemp(prefix="tells-test-")
    def _tmp(up, name):
        if up is None or not up.filename:
            return None
        p = os.path.join(tmp, name)
        with open(p, "wb") as f:
            f.write(up.file.read())
        return p
    try:
        return tells_engine.run(front_user=_tmp(front_user, "fu"), front_ref=_tmp(front_ref, "fr"),
                                back_user=_tmp(back_user, "bu"), back_ref=_tmp(back_ref, "br"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

@app.get("/v1/test-session/{session_id}")
def get_session(session_id: str):
    p = os.path.join(UPLOADS, session_id, "receipt.json")
    if not os.path.exists(p):
        raise HTTPException(404, "test session not found")
    return json.load(open(p))

@app.post("/v1/test-session/{session_id}/delete")
def delete_session(session_id: str):
    d = os.path.join(UPLOADS, session_id)
    if not os.path.isdir(d):
        raise HTTPException(404, "test session not found")
    shutil.rmtree(d, ignore_errors=True)
    return {"session_id": session_id, "deleted": True, "note": "Test photos for this session deleted from the playground workspace."}
