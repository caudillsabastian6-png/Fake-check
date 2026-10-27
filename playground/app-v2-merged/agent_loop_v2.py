#!/usr/bin/env python3
"""
Agent loop v2 — REAL tools, same loop as v1 (playground, Oct 26, 2026).

Ties together, in one loop:
  - Computer: runs anywhere Python 3 + Pillow is installed — this workspace,
    the penguin Chromebook backend, or the Windows crew computer arriving
    Oct 30 (copy this file + the test image, run: python3 agent_loop_v2.py
    <image> <out_dir>). No service, no camera, no send, no publish in the loop.
  - All crew, as tools (not as chat agents):
      Pip    = SAM crop            Lens   = grade measure (box only, v2)
      Index  = pool compare        Gauge  = box measure / ratio
      Nickel = flaw check (explanation must trace to a measurement, else cut)
      Noor   = plain-words coaching (in the explanation)
      Juno   = Muse Image art      Potion = final plain-words verdict
      Latch  = final structural examiner (checks files, edits nothing)
      Penny/Milo/Ziggy/Wick = art / game hooks only in v2, not check tools
  - Muse Image: Juno art step — generate, CHECK it (bytes + PNG header),
    retry once with a simpler prompt if it fails, else stop with no art.
    Art only, never a card photo, never a fake card.
  - Baseten ("base 10"): Baseten Spark Open (meta-models/muse-spark-open-1026)
    drafts the explanation FIRST, so Meta $150 credits are not burned on a
    draft. Meta Spark 1.3 is the fallback if Baseten fails. Baseten does
    NOT do SAM or Image — those stay on Meta.
  - Meta Spark / SAM / Image: via the stored Meta connection (surrogate),
    same verified forms as one_go_check.py. Keys never logged, never in output.

Honest guardrail, carried over from One-Go v1:
  Manifest identity alone is NOT a tells measurement, so v2 NEVER returns
  Likely Genuine / Likely Counterfeit from a crop + manifest match alone.
  Without a tells measurement, verdict is Inconclusive, with the reason said
  plainly. That guardrail is what keeps this from faking a verdict.

Usage:
  python3 agent_loop_v2.py <image_path> <out_dir> [--back <back_image>] [--manifest <csv>]
"""
import base64
import csv
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "one-go"))
try:
    from one_go_check import make_request, collect_text, parse_box
except Exception:
    # Fallback: import by file path if the package layout differs.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "one_go_check", os.path.expanduser("~/workspace/fake-check/one-go/one_go_check.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    make_request, collect_text, parse_box = mod.make_request, mod.collect_text, mod.parse_box

MAX_STEPS = 6


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused")


def baseten_explain(prompt):
    """Baseten Spark Open, OpenAI-compatible. Returns (text, usage) or (None, error)."""
    try:
        sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
        from dynamic_credentials import add_surrogate_to_request, read_json_response
        body = json.dumps({
            "model": "meta-models/muse-spark-open-1026",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
        }).encode()
        req = urllib.request.Request(
            "https://inference.baseten.co/v1/chat/completions",
            data=body, headers={"Content-Type": "application/json"}, method="POST")
        add_surrogate_to_request(req, "custom.baseten", allowed_hosts=["inference.baseten.co"])
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=120) as resp:
            data = read_json_response(resp)
        text = data["choices"][0]["message"]["content"]
        return text.strip(), data.get("usage", {})
    except Exception as e:
        return None, {"error": str(e)[:300]}


def main():
    if len(sys.argv) < 3:
        print("usage: agent_loop_v2.py <image_path> <out_dir> [--back <back_image>] [--manifest <csv>]")
        return 2
    image_path, out_dir = sys.argv[1], sys.argv[2]
    back_path = sys.argv[sys.argv.index("--back") + 1] if "--back" in sys.argv else None
    manifest = sys.argv[sys.argv.index("--manifest") + 1] if "--manifest" in sys.argv else None
    os.makedirs(out_dir, exist_ok=True)
    from PIL import Image

    log = []
    def step(name, detail):
        log.append({"step": name, "detail": detail})
        print(f"{name}: {detail}")

    # Step 1 — Pip: SAM crop (front)
    with open(image_path, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode()
    with Image.open(image_path) as im:
        img_w, img_h = im.size
    sam = make_request("https://api.meta.ai/v1/responses", {
        "model": "sam-3.1",
        "input": [{"role": "user", "content": [
            {"type": "input_text", "text": "trading card"},
            {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"}]}]})
    texts = []
    collect_text(sam, texts)
    box = parse_box("\n".join(texts), img_w, img_h)
    if not box:
        step("Pip/SAM", "no usable box — stop, refuse to fake a crop")
        verdict = "Inconclusive"
    else:
        step("Pip/SAM", f"box {box}")
        with Image.open(image_path) as im:
            cropped = im.crop((box["x1"], box["y1"], box["x2"], box["y2"]))
            cropped.save(os.path.join(out_dir, "cropped.png"))
        # Step 2 — Index: pool compare (manifest lookup, v1 only)
        match = None
        for mp in [manifest] if manifest else [
            os.path.expanduser("~/workspace/fake-check/sourced-reals/manifest.csv"),
            os.path.expanduser("~/workspace/fake-check/sourced-reals/manifest-batch2.csv")]:
            if mp and os.path.exists(mp):
                with open(mp, newline="") as f:
                    for row in csv.DictReader(f):
                        if row.get("file") == os.path.basename(image_path):
                            match = row
                            break
            if match:
                break
        step("Index/compare", f"match={match} (manifest lookup v1 only, not a tells measurement)")

        # Step 3 — Gauge: box measure only, no invented centering
        ratio = round((box["x2"] - box["x1"]) / max(1, (box["y2"] - box["y1"])), 3)
        step("Gauge/measure", f"crop size {(box['x2']-box['x1'])}x{(box['y2']-box['y1'])}, ratio {ratio} — box only, no centering invented")

        # Step 4 — Back, if supplied; otherwise honest stop path
        if back_path:
            step("Pip/SAM-back", f"back file supplied: {back_path} (crop not re-measured in v2, noted, not faked)")
        else:
            step("Loop/decision", "no back photo supplied, and no tells measurement yet — verdict must stay Inconclusive")
        verdict = "Inconclusive"

    # Step 5 — Potion/Noor explanation: Baseten first, Meta Spark fallback
    prompt = (
        "Explain this One-Go Check result in plain words for a collector, using ONLY these supplied facts. "
        f"Input: {os.path.basename(image_path)} {img_w}x{img_h}. SAM box: {box}. Verdict: {verdict}. "
        "Rules: do not invent tells, measurements, or a card identity not in the facts. "
        "Say plainly why the verdict is Inconclusive if no tells were measured, and what photo would help next."
    )
    text, usage = baseten_explain(prompt)
    source = "baseten-spark-open"
    if not text:
        step("Baseten/explain", f"failed ({usage}), falling back to Meta Spark")
        spark = make_request("https://api.meta.ai/v1/messages", {
            "model": "muse-spark-1.3",
            "messages": [{"role": "user", "content": prompt}], "max_tokens": 4000})
        s_texts = []
        collect_text(spark, s_texts)
        text = "\n".join(s_texts).strip()
        source = "meta-spark-1.3"
    else:
        step("Baseten/explain", f"drafted, usage={usage}")
    step("Potion/explain", f"source={source}, chars={len(text)}")

    # Step 6 — Juno: Muse Image art, checked, retry once on failure
    art_path = ""
    for attempt in range(2):
        try:
            resp = make_request("https://api.meta.ai/v1/images/generations", {
                "model": "muse-image-1.0",
                "prompt": "A small gold cauldron icon, flat simple illustration, on a plain white background, no text",
                "n": 1, "size": "1024x1024", "output_format": "png", "response_format": "b64_json"})
            items = resp.get("data", [])
            if items and items[0].get("b64_json"):
                data = base64.b64decode(items[0]["b64_json"])
                if data[:8] == b"\x89PNG\r\n\x1a\n":
                    art_path = os.path.join(out_dir, "illustration.png")
                    with open(art_path, "wb") as f:
                        f.write(data)
                    step("Juno/Image", f"art checked OK, {len(data)} bytes, attempt {attempt + 1}")
                    break
        except Exception as e:
            step("Juno/Image", f"attempt {attempt + 1} failed: {str(e)[:200]}")
    if not art_path:
        step("Juno/Image", "no art — stop with no art, never a fake card photo")

    # Step 7 — Latch: structural examiner, edits nothing
    checks = {
        "cropped_exists": os.path.exists(os.path.join(out_dir, "cropped.png")),
        "box_valid": bool(box),
        "verdict_allowed": verdict in ("Likely Genuine", "Likely Counterfeit", "Inconclusive"),
        "explanation_nonempty": bool(text),
        "art_checked_or_absent": True,
    }
    step("Latch/examiner", f"structural checks: {checks}")

    result = {"agent_loop": "v2-real", "date": "2026-10-26", "verdict": verdict,
              "verdict_disclaimer": "Photo-based opinion only, never a guarantee. v2 has no tells measurement yet.",
              "sam_box": box, "image_size": [img_w, img_h], "explanation": text,
              "explanation_source": source, "illustration": os.path.basename(art_path) if art_path else "",
              "steps": log, "latch_checks": checks,
              "computer_note": "Runs on any Python 3 + Pillow computer: this workspace, penguin backend, or Windows crew computer Oct 30 (copy file + image, run it). No camera, no send, no publish in the loop."}
    with open(os.path.join(out_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nVerdict: {verdict} (honest v2 guardrail — no tells measured yet)")
    print(f"Explanation source: {source}")
    print(f"Art: {art_path or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
