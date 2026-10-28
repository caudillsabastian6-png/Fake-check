# Backend-tie impl — Steps 1–3 test only, Step 4a calibration (Oct 28, 2026)

Playground only. Localhost only. No Modal deploy, no live push, no spend, no training.

Run (from this folder):
```
/tmp/backend-tie-venv/bin/uvicorn app:app --host 127.0.0.1 --port 8765
```
Then open `demo-test-upload.html` in Chrome on the same machine.
Stop the server when testing ends, then run `python3 delete_test_uploads.py`.

Retention default: test photos live only in `uploads/` here, deleted after the test run.
No shipped verdict: every response carries TEST ONLY labelling and shipped_verdict null.

Full results, tests, gaps, and the Step 4a gate verdict: see REPORT.md in this folder.
Step 4a gate verdict is FAIL — no real verdict is enabled by this work.
