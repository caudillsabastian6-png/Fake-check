#!/usr/bin/env python3
"""One-Go Check v1 — hackathon-period wiring, Oct 26, 2026.

Flow, in order:
  1. SAM 3.1 crops the card (short noun phrase "trading card", Responses API).
  2. Database comparison, v1: manifest lookup by filename only.
     If the input file is not a known pool file, the comparison is
     honestly Inconclusive — v1 does NOT measure tells yet, so it must
     NOT return Likely Genuine or Likely Counterfeit from a crop alone.
     Tells measurement is the next step after this v1.
  3. Muse Spark 1.3 explains the result in plain words.
  4. Muse Image 1.0 draws a cauldron illustration (art only, never a card photo).

Auth: reads META_MODEL_API_KEY from the environment in public use.
In Muse's own workspace it falls back to the stored Meta Model API
connection via the surrogate exchange. The key is never logged,
never written to output files, and never committed to a repo.

Usage:
  python3 one_go_check.py <image_path> <out_dir> [--manifest <manifest.csv>]

Output in <out_dir>:
  cropped.png, illustration.png, result.json (box, comparison, Spark text, verdict)
"""
import base64
import csv
import json
import os
import re
import sys
import urllib.request
import urllib.error


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def make_request(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    key = os.environ.get("META_MODEL_API_KEY")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    else:
        # Muse workspace only: stored connection via surrogate exchange.
        sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
        from dynamic_credentials import add_surrogate_to_request

        add_surrogate_to_request(
            req, "custom.meta-model-api", allowed_hosts=["api.meta.ai"]
        )
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=180) as resp:
        return json.loads(resp.read().decode())


def collect_text(obj, out):
    """Collect visible text from Meta API response shapes, skipping thinking."""
    if isinstance(obj, dict):
        if obj.get("type") in ("thinking", "redacted_thinking"):
            return
        for k in ("output_text", "text"):
            if isinstance(obj.get(k), str) and obj[k].strip():
                out.append(obj[k])
        for v in obj.values():
            collect_text(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_text(v, out)


def parse_box(text, img_w, img_h):
    m = re.search(r"<\|box;(\d+),(\d+),(\d+),(\d+)\|>", text)
    if not m:
        m = re.search(r"x1\s*=\s*(\d+).*?y1\s*=\s*(\d+).*?x2\s*=\s*(\d+).*?y2\s*=\s*(\d+)", text, re.S)
    if not m:
        return None
    x1, y1, x2, y2 = (int(v) for v in m.groups())
    x1 = max(0, min(x1, img_w - 1))
    y1 = max(0, min(y1, img_h - 1))
    x2 = max(x1 + 1, min(x2, img_w))
    y2 = max(y1 + 1, min(y2, img_h))
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "w": img_w, "h": img_h}


def main():
    if len(sys.argv) < 3:
        print("usage: one_go_check.py <image_path> <out_dir> [--manifest <csv>]")
        return 2
    image_path, out_dir = sys.argv[1], sys.argv[2]
    manifest = None
    if "--manifest" in sys.argv:
        manifest = sys.argv[sys.argv.index("--manifest") + 1]
    os.makedirs(out_dir, exist_ok=True)

    from PIL import Image

    with open(image_path, "rb") as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode()
    with Image.open(image_path) as im:
        img_w, img_h = im.size

    # 1. SAM crop — verified working form: short noun phrase only.
    sam = make_request(
        "https://api.meta.ai/v1/responses",
        {
            "model": "sam-3.1",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "trading card"},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
                    ],
                }
            ],
        },
    )
    sam_texts = []
    collect_text(sam, sam_texts)
    sam_text = "\n".join(sam_texts)
    box = parse_box(sam_text, img_w, img_h)
    if not box:
        print("SAM returned no usable box; refusing to fake a crop.")
        print(sam_text[:1000])
        return 1
    with Image.open(image_path) as im:
        cropped = im.crop((box["x1"], box["y1"], box["x2"], box["y2"]))
        cropped_path = os.path.join(out_dir, "cropped.png")
        cropped.save(cropped_path)
        cropped_size = cropped.size

    # 2. Comparison v1: manifest lookup by filename only.
    comparison = {"method": "manifest_lookup_v1", "match": None, "note": ""}
    basename = os.path.basename(image_path)
    if manifest and os.path.exists(manifest):
        with open(manifest, newline="") as f:
            for row in csv.DictReader(f):
                if row.get("file") == basename:
                    comparison["match"] = row
                    break
    if comparison["match"]:
        comparison["note"] = (
            "Input file is a known pool file; identity comes from the manifest, "
            "not from a photo tells measurement."
        )
    else:
        comparison["note"] = (
            "Input file is not a known pool file and v1 does not measure tells yet, "
            "so the comparison cannot resolve a genuine/counterfeit call."
        )

    # 3. Spark verdict explanation — generous max_tokens, parse content by type.
    prompt = (
        "You are explaining a One-Go Check result in plain words for a collector. "
        "Crop box: {box}, original image {w}x{h}, cropped image {cw}x{ch}. "
        "Manifest match: {match}. Comparison note: {note}. "
        "Rules: verdict must be exactly one of Likely Genuine, Likely Counterfeit, "
        "or Inconclusive. If no tells were measured, the verdict MUST be Inconclusive, "
        "never a guarantee, and you must say why in plain words. "
        "Do not invent tells, measurements, or a card identity that is not in the input."
    ).format(
        box=box, w=img_w, h=img_h, cw=cropped_size[0], ch=cropped_size[1],
        match=comparison["match"], note=comparison["note"],
    )
    spark = make_request(
        "https://api.meta.ai/v1/messages",
        {
            "model": "muse-spark-1.3",
            "messages": [{"role": "user", "content": prompt}],
            # Spark thinking can consume ~1500 tokens before any visible text;
            # 1200 was not enough in the Oct 26 test and returned no text.
            "max_tokens": 4000,
        },
    )
    spark_texts = []
    collect_text(spark, spark_texts)
    spark_text = "\n".join(spark_texts).strip()
    verdict = "Inconclusive"
    for candidate in ("Likely Genuine", "Likely Counterfeit", "Inconclusive"):
        if candidate in spark_text:
            verdict = candidate
            break
    # v1 guardrail: without a tells measurement, never upgrade past Inconclusive.
    # Manifest identity alone is not a tells measurement, so v1 stays Inconclusive.
    verdict = "Inconclusive"

    # 4. Muse Image cauldron illustration, art only, no text, no card.
    image_resp = make_request(
        "https://api.meta.ai/v1/images/generations",
        {
            "model": "muse-image-1.0",
            "prompt": "A small gold cauldron icon, flat simple illustration, on a plain white background, no text",
            "n": 1,
            "size": "1024x1024",
            "output_format": "png",
            "response_format": "b64_json",
        },
    )
    items = image_resp.get("data", [])
    illustration_path = os.path.join(out_dir, "illustration.png")
    if items and items[0].get("b64_json"):
        with open(illustration_path, "wb") as f:
            f.write(base64.b64decode(items[0]["b64_json"]))
    else:
        illustration_path = ""

    result = {
        "one_go_check_version": "v1",
        "date": "2026-10-26",
        "models": {
            "sam": "sam-3.1",
            "spark": "muse-spark-1.3",
            "image": "muse-image-1.0",
        },
        "input": {"file": basename, "size": [img_w, img_h]},
        "sam_box": box,
        "cropped_size": list(cropped_size),
        "comparison": comparison,
        "spark_text": spark_text,
        "verdict": verdict,
        "verdict_disclaimer": "Photo-based opinion only, never a guarantee. "
        "v1 comparison is manifest lookup only; tells measurement is the next step.",
        "illustration": os.path.basename(illustration_path) if illustration_path else "",
        "illustration_note": "Art only, never a fake card photo.",
    }
    with open(os.path.join(out_dir, "result.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(f"verdict: {verdict}")
    print(f"box: {box}")
    print(f"cropped: {cropped_size}")
    print(f"spark chars: {len(spark_text)}")
    print(f"illustration: {illustration_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
