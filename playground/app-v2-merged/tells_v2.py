#!/usr/bin/env python3
"""
Tells v2 — PLAYGROUND ONLY, Oct 26, 2026.
Image-to-image comparison, not manifest lookup.

What it does:
  Takes a user card crop and a reference card image, measures both the SAME way,
  and scores independent tells. No SAM call here (crop is supplied), no API call,
  $0, no verdict is ever guaranteed or official.

Tells measured (all from pixels, all reproducible):
  - aspect_ratio: width / height of the crop
  - mean_rgb: average colour of the whole card
  - border_rgb: colour sampled from the top border band (print frame area)
  - edge_density: fraction of pixels with a strong left/right brightness step
    (a rough print-texture / line-work signal, NOT a font or holo proof)
  - colour_histogram: 16-bin per-channel histogram, correlation 0..1

Verdict rule (documented, not tuned to pass a test):
  - strong_mismatch = a tell far outside its threshold (see THRESHOLDS)
  - >=2 strong mismatches            -> Likely Counterfeit
  - 0 strong mismatches AND >=3 tells match -> Likely Genuine
  - anything else                     -> Inconclusive
  A Likely verdict here is still an ESTIMATE, never official, never guaranteed.
  A manifest name match alone never produces a Genuine verdict in this script.

Usage:
  python3 tells_v2.py <user_crop.png> <reference.png> <output.json>
"""
import json, math, sys
from PIL import Image

W, H = 300, 412  # normalised size for comparison; aspect is measured BEFORE resize
THRESHOLDS = {
    "aspect_ratio": 0.05,      # absolute difference
    "mean_rgb": 30.0,          # mean per-channel absolute difference
    "border_rgb": 40.0,        # mean per-channel absolute difference
    "edge_density": 0.08,      # absolute difference
    "colour_histogram": 0.15,  # 1 - correlation must be <= this to count as match
}

def measure(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    aspect = w / h
    # border: top 6% band, middle 60% of width (avoids corners)
    band = im.crop((int(w*0.2), 0, int(w*0.8), max(1, int(h*0.06))))
    def mean_rgb(img):
        px = list(img.getdata())
        n = len(px)
        return tuple(sum(p[i] for p in px)/n for i in range(3))
    small = im.resize((W, H))
    px = list(small.getdata())
    grey = [0.299*p[0]+0.587*p[1]+0.114*p[2] for p in px]
    steps = 0
    for y in range(H):
        row = grey[y*W:(y+1)*W]
        for x in range(W-1):
            if abs(row[x+1]-row[x]) > 40:
                steps += 1
    edge_density = steps / max(1, (W-1)*H)
    # 16-bin histogram per channel, normalised
    hist = []
    for ch in range(3):
        bins = [0]*16
        for p in px:
            bins[min(15, p[ch]//16)] += 1
        total = sum(bins) or 1
        hist.extend([b/total for b in bins])
    return {
        "size": [w, h],
        "aspect_ratio": round(aspect, 4),
        "mean_rgb": [round(v, 1) for v in mean_rgb(small)],
        "border_rgb": [round(v, 1) for v in mean_rgb(band)],
        "edge_density": round(edge_density, 4),
        "histogram": hist,
    }

def rgb_diff(a, b):
    return sum(abs(x-y) for x, y in zip(a, b)) / 3.0

def hist_corr(a, b):
    ma = sum(a)/len(a); mb = sum(b)/len(b)
    num = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    den = math.sqrt(sum((x-ma)**2 for x in a) * sum((y-mb)**2 for y in b)) or 1
    return num/den

def main():
    if len(sys.argv) != 4:
        print("usage: tells_v2.py <user_crop.png> <reference.png> <output.json>")
        return 2
    user_path, ref_path, out_path = sys.argv[1:]
    u = measure(user_path); r = measure(ref_path)
    tells = {}
    def tell(name, user_v, ref_v, diff, threshold, lower_is_better=True):
        match = diff <= threshold
        strong = diff > threshold * 2
        tells[name] = {"user": user_v, "reference": ref_v, "difference": round(diff, 4),
                       "threshold": threshold, "match": match, "strong_mismatch": strong}
    tell("aspect_ratio", u["aspect_ratio"], r["aspect_ratio"],
         abs(u["aspect_ratio"]-r["aspect_ratio"]), THRESHOLDS["aspect_ratio"])
    tell("mean_rgb", u["mean_rgb"], r["mean_rgb"],
         rgb_diff(u["mean_rgb"], r["mean_rgb"]), THRESHOLDS["mean_rgb"])
    tell("border_rgb", u["border_rgb"], r["border_rgb"],
         rgb_diff(u["border_rgb"], r["border_rgb"]), THRESHOLDS["border_rgb"])
    tell("edge_density", u["edge_density"], r["edge_density"],
         abs(u["edge_density"]-r["edge_density"]), THRESHOLDS["edge_density"])
    corr = hist_corr(u["histogram"], r["histogram"])
    tells["colour_histogram"] = {"user_correlation": round(corr, 4), "reference": 1.0,
        "difference": round(1-corr, 4), "threshold": THRESHOLDS["colour_histogram"],
        "match": (1-corr) <= THRESHOLDS["colour_histogram"],
        "strong_mismatch": (1-corr) > THRESHOLDS["colour_histogram"]*2}
    matches = sum(1 for t in tells.values() if t["match"])
    strong = sum(1 for t in tells.values() if t["strong_mismatch"])
    if strong >= 2:
        verdict = "Likely Counterfeit"
    elif strong == 0 and matches >= 3:
        verdict = "Likely Genuine"
    else:
        verdict = "Inconclusive"
    result = {"user_image": user_path, "reference_image": ref_path,
              "user_size": u["size"], "reference_size": r["size"],
              "tells": tells, "matches": matches, "strong_mismatches": strong,
              "verdict": verdict,
              "verdict_note": "Estimate only, never official, never guaranteed. "
                              "A manifest name match alone never produces a Genuine verdict."}
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps({k: result[k] for k in ("verdict", "matches", "strong_mismatches")}))
    for name, t in tells.items():
        print(f"  {name}: diff={t['difference']} match={t['match']} strong={t['strong_mismatch']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
