"""Scan quality gate — playground only, $0, Oct 27, 2026.

Runs BEFORE tells are measured. A quality failure NEVER produces a
Counterfeit verdict and NEVER produces a guess: it returns
status=needs_input naming the exact quality problem and asking for a
retake. A quality pass does not prove a card genuine — it only means
the photo is good enough to measure.

Thresholds — deliberately conservative, so a borderline genuine photo
is NOT rejected. Every threshold below was checked against the canned
genuine crops (Alakazam crop 565x797, Base Set refs 600x825):
  genuine edge_density ~0.082, mean step ~10.3, white blowout 0.0,
  aspect 0.709-0.727.
  - Blur: fail ONLY if BOTH edge_density < 0.015 AND mean horizontal
    step < 5.0. A heavily blurred photo (blur radius 3 or 8 in tests)
    scores edge_density 0.0 and mean step 1.7-3.2, so it fails both.
    A genuine photo scores ~0.08 / ~10, so it passes by a wide margin.
    A single weak signal alone does NOT fail the gate.
  - Glare: fail only if >10% of pixels are pure white (>245 in all
    channels). Genuine cards score 0.0%; a white rectangle over the
    centre scores ~12%. A card with a genuinely white design area
    below 10% still passes.
  - Aspect / framing proxy: if a reference is available, fail only if
    |aspect - reference aspect| > 0.15 (the same tolerance already used
    for crop boxes). Without a reference, fail only if aspect is
    outside 0.60-0.90 (portrait card) or >1.05 (landscape/sideways).
    Aspect alone cannot prove all four corners are in frame — a crop
    that preserves portrait aspect can still cut a corner. That limit
    is stated in the result, not hidden.
  - Size: fail only if width < 200px (too small to measure reliably).
  - Sleeve: NOT detectable reliably from $0 pixels alone, so the gate
    NEVER rejects on sleeve. sleeve_detectable=False is recorded, and
    the photo guide ("out of a sleeve if you can") remains the control.
    Upside-down orientation is likewise not detectable $0 and is not
    claimed.
"""
import os

from PIL import Image


def _metrics(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    small = im.resize((300, 412))
    px = list(small.getdata())
    grey = [0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2] for p in px]
    steps = 0
    for y in range(412):
        row = grey[y * 300:(y + 1) * 300]
        for x in range(299):
            if abs(row[x + 1] - row[x]) > 40:
                steps += 1
    edge_density = steps / max(1, 299 * 412)
    diffs = []
    for y in range(412):
        row = grey[y * 300:(y + 1) * 300]
        diffs.extend(abs(row[x + 1] - row[x]) for x in range(299))
    mean_step = sum(diffs) / max(1, len(diffs))
    white = sum(1 for r, g, b in px if r > 245 and g > 245 and b > 245) / max(1, len(px))
    return {
        "size": [w, h],
        "aspect_ratio": round(w / max(1, h), 4),
        "edge_density": round(edge_density, 4),
        "mean_step": round(mean_step, 2),
        "white_blowout": round(white, 4),
    }


def check_quality(path, reference_path=None):
    """Return {passed, problems, metrics, notes}. problems are human
    retake instructions, never verdicts."""
    problems = []
    notes = []
    try:
        m = _metrics(path)
    except Exception as e:
        return {"passed": False,
                "problems": [f"scan_quality: photo could not be opened ({type(e).__name__}) — retake and re-upload a clear card photo"],
                "metrics": {}, "sleeve_detectable": False,
                "notes": ["unreadable photo cannot be measured; never a Counterfeit verdict on quality alone"]}
    w, h = m["size"]
    if w < 200:
        problems.append(f"scan_quality: photo is too small ({w}px wide) to measure reliably — retake a larger, sharper photo")
    # Blur: BOTH signals must agree, so a borderline genuine photo is not rejected.
    if m["edge_density"] < 0.015 and m["mean_step"] < 5.0:
        problems.append(f"scan_quality: photo is too blurry (edge_density {m['edge_density']}, mean step {m['mean_step']}) — retake a sharper, flatter photo with the card filling the frame")
    # Glare: severe blowout only.
    if m["white_blowout"] > 0.10:
        problems.append(f"scan_quality: severe glare / white blowout ({m['white_blowout']:.0%} of the photo is pure white) — retake with glare off the card, out of direct light")
    # Aspect / framing proxy.
    ref_aspect = None
    if reference_path and os.path.exists(reference_path):
        try:
            with Image.open(reference_path) as r:
                ref_aspect = r.size[0] / max(1, r.size[1])
        except Exception:
            ref_aspect = None
    if ref_aspect is not None:
        if abs(m["aspect_ratio"] - ref_aspect) > 0.15:
            problems.append(f"scan_quality: card is not fully in frame or is badly cropped (aspect {m['aspect_ratio']} vs reference {ref_aspect:.3f}) — retake with all four corners and edges in view")
    else:
        if m["aspect_ratio"] > 1.05:
            problems.append(f"scan_quality: photo looks sideways / landscape (aspect {m['aspect_ratio']}) — rotate to portrait and retake")
        elif not (0.60 <= m["aspect_ratio"] <= 0.90):
            problems.append(f"scan_quality: card aspect looks wrong ({m['aspect_ratio']}) — retake with the full card in frame, portrait, all corners visible")
    notes.append("Aspect is a framing proxy only: a crop that preserves portrait aspect can still cut a corner, and that case is not detectable by this gate.")
    notes.append("Sleeve is not detectable reliably from $0 pixels alone; this gate never rejects on sleeve. Upside-down orientation is likewise not claimed.")
    return {"passed": not problems, "problems": problems, "metrics": m,
            "reference_aspect": ref_aspect, "sleeve_detectable": False, "notes": notes}
