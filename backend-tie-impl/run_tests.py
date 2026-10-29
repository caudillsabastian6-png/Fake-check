#!/usr/bin/env python3
"""Re-run Steps 1-3 server tests against a local uvicorn instance, then stop it.
$0, localhost only. Exits non-zero on any failure. Deletes test uploads at the end."""
import json, os, subprocess, sys, time, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "http://127.0.0.1:8765"
def req(method, path, data=None, headers=None):
    r = urllib.request.Request(BASE + path, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")
fails = []
def check(name, cond, detail=""):
    print(("PASS" if cond else "FAIL"), name, detail)
    if not cond: fails.append(name)
# Standalone fix (Oct 29, 2026): no absolute venv path. Use
# $BACKEND_TIE_UVICORN, else a uvicorn on PATH, else `python -m uvicorn`.
# If none is available, SKIP with the reason instead of failing.
import shutil
_uv = os.environ.get("BACKEND_TIE_UVICORN") or shutil.which("uvicorn")
if _uv:
    _UVICORN_CMD = [_uv]
else:
    try:
        import uvicorn  # noqa: F401
        _UVICORN_CMD = [sys.executable, "-m", "uvicorn"]
    except ImportError:
        print("SKIPPED: uvicorn/fastapi not installed on this machine — "
              "install the backend-tie deps first (pip install -r requirements.txt "
              "in this folder), then re-run. No server was started.")
        sys.exit(0)
proc = subprocess.Popen(_UVICORN_CMD + ["app:app", "--host", "127.0.0.1", "--port", "8765"],
                        cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(30):
        try:
            s, d = req("GET", "/health"); break
        except Exception: time.sleep(0.5)
    check("health ok, no verdict shipped", s == 200 and d.get("verdict") == "none shipped", str(d))
    s, d = req("POST", "/v1/test-match", json.dumps({"set": "base1", "number": "1"}).encode(), {"Content-Type": "application/json"})
    check("match exact base1-1 resolves", d.get("status") == "resolved" and (d.get("row") or {}).get("id") == "base1-1", str(d.get("row")))
    s, d = req("POST", "/v1/test-match", json.dumps({"set": "Base", "number": "1", "name": "Alakazam"}).encode(), {"Content-Type": "application/json"})
    check("match loose Base needs_input, never picks", d.get("status") == "needs_input" and d.get("row") is None)
    s, d = req("POST", "/v1/test-match", json.dumps({"image_supplied": True}).encode(), {"Content-Type": "application/json"})
    check("match image-only needs_input", d.get("status") == "needs_input")
finally:
    proc.terminate()
    try: proc.wait(timeout=10)
    except Exception: proc.kill()
subprocess.run([sys.executable, os.path.join(HERE, "delete_test_uploads.py")], check=False)
print("PASS" if not fails else f"FAIL {fails}")
sys.exit(1 if fails else 0)
