#!/usr/bin/env python3
"""Pip on-device crop detector prototype v0 — classical vision only.

No ML model, no SAM calls, no training on SAM outputs. SAM boxes already
on file are used ONLY as an evaluation answer key (compare, don't learn
weights from them). OpenCV is not installed in this VM, so this uses
PIL + NumPy (+ scipy.ndimage when available) only.

Pipeline (Pass-1 rules, pip-learning-pass-1-2026-10-26.md §2):
  1. Downscale, grayscale, box-blur, Sobel gradient magnitude.
  2. Largest-quadrilateral candidate: binary edge map (75th-percentile
     gradient), 3x3 binary closing x2, connected components; pick the
     largest component whose axis-aligned bounding box has an aspect
     in the card bands and an area in 25-95% of the image. Its four
     corners are the component's extremes (min/max of x+y and x-y,
     i.e. the diamond corners of a tilted rectangle), with the bbox
     corners as fallback. This is a v0 heuristic.
  3. Gates (a failed gate = REFUSE, never a guessed crop):
     - aspect: portrait 0.60-0.85, or landscape 1.18-1.67 then rotate
       to portrait. Outside both bands -> refuse.
     - area: <25% or >95% -> flag (small clean cards CAN pass per
       triage, so area alone does not refuse; it is reported).
     - corners inside frame: a box touching the image edge on any
       side means a corner may be cut -> refuse.
     - glare: fraction of pixels >= 250 inside the box, reported.
     - focus proxy: mean Sobel magnitude inside the box, reported.
     - stability: NOT measurable from a single still. Live app must
       require the rectangle to be stable ~1 s across frames.
     - hand / second card: v0 does NOT reliably detect a hand or a
       second card from one still. It refuses only when those produce
       a detectable symptom (no border component, aspect out of band,
       box touches an edge). That is a documented v0 limitation.

Gate validator (testable independently of the detector):
  validate_box(box, orig_size, image) applies the same gates to any
  candidate box — e.g. a SAM box — so the gates themselves can be
  measured against the boxes already on file.

Usage:
  python3 on_device_crop.py <image>   # print one result (JSON)
"""
import json
import sys

import numpy as np
from PIL import Image

PORTRAIT = (0.60, 0.85)
LANDSCAPE = (1.18, 1.67)
GLARE_PIXEL = 250

try:
    from scipy import ndimage
    _HAVE_SCIPY = True
except Exception:
    _HAVE_SCIPY = False


def _blur(gray, k=5):
    pad = k // 2
    p = np.pad(gray, pad, mode="edge")
    c = np.cumsum(np.concatenate([np.zeros((1, p.shape[1])), p], axis=0), axis=0)
    v = (c[k:] - c[:-k]) / k
    c = np.cumsum(np.concatenate([np.zeros((v.shape[0], 1)), v], axis=1), axis=1)
    return (c[:, k:] - c[:, :-k]) / k


def _sobel(gray):
    gy, gx = np.gradient(gray)
    return np.hypot(gx, gy)


def _candidate_box(small_gray):
    """Largest-component quadrilateral candidate, in small-image coords."""
    if not _HAVE_SCIPY:
        return None
    mag = _sobel(_blur(small_gray))
    edge = mag >= np.percentile(mag, 75)
    closed = ndimage.binary_closing(edge, structure=np.ones((3, 3)), iterations=2)
    lab, n = ndimage.label(closed)
    if n == 0:
        return None
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    slices = ndimage.find_objects(lab)
    H, W = small_gray.shape
    best = None
    for idx in np.argsort(sizes[1:])[::-1][:20] + 1:
        sl = slices[idx - 1]
        if sl is None:
            continue
        y1, y2 = sl[0].start, sl[0].stop - 1
        x1, x2 = sl[1].start, sl[1].stop - 1
        bw, bh = x2 - x1, y2 - y1
        if bw <= 0 or bh <= 0:
            continue
        aspect = bw / bh
        area = (bw * bh) / (W * H)
        if not (PORTRAIT[0] <= aspect <= PORTRAIT[1] or
                LANDSCAPE[0] <= aspect <= LANDSCAPE[1]):
            continue
        if not (0.25 <= area <= 0.95):
            continue
        # Diamond corners of this component only (tilt-aware extremes).
        sub = (lab[sl] == idx)
        ys, xs = np.where(sub)
        xs = xs + x1; ys = ys + y1
        s = xs + ys; d = xs - ys
        corners = [(int(xs[np.argmin(s)]), int(ys[np.argmin(s)])),
                   (int(xs[np.argmax(s)]), int(ys[np.argmax(s)])),
                   (int(xs[np.argmin(d)]), int(ys[np.argmin(d)])),
                   (int(xs[np.argmax(d)]), int(ys[np.argmax(d)]))]
        best = {"bbox": [x1, y1, x2, y2], "corners": corners,
                "component_pixels": int(sizes[idx])}
        break
    return best


def validate_box(box, orig_size, img):
    """Apply Pass-1 gates to any candidate box. Returns a gate dict."""
    ow, oh = orig_size
    x1, y1, x2, y2 = box
    bw, bh = x2 - x1, y2 - y1
    aspect = bw / bh if bh else 0.0
    rotated = False
    if LANDSCAPE[0] <= aspect <= LANDSCAPE[1]:
        aspect = 1.0 / aspect
        rotated = True
    in_band = PORTRAIT[0] <= aspect <= PORTRAIT[1]
    area_frac = (bw * bh) / (ow * oh) if ow * oh else 0.0
    touches_edge = (x1 <= 2 or y1 <= 2 or x2 >= ow - 3 or y2 >= oh - 3)
    crop_img = img.crop((x1, y1, x2, y2)).convert("L")
    crop = np.asarray(crop_img, dtype=np.float64)
    glare_frac = float(np.mean(crop >= GLARE_PIXEL)) if crop.size else 0.0
    # Focus proxy on a downscaled crop (full-res Sobel is slow, same signal).
    fscale = min(1.0, 640.0 / max(crop_img.size)) if crop_img.size[0] else 1.0
    fsmall = crop_img.resize((max(1, int(crop_img.size[0] * fscale)),
                              max(1, int(crop_img.size[1] * fscale))), Image.LANCZOS)
    farr = np.asarray(fsmall, dtype=np.float64)
    focus = float(np.mean(_sobel(_blur(farr)))) if farr.size else 0.0
    reasons = []
    if not in_band:
        reasons.append(f"aspect_out_of_band:{aspect:.3f}")
    if touches_edge:
        reasons.append("box_touches_frame_edge_possible_cut_corner")
    return {"aspect": round(aspect, 3), "rotated_from_landscape": rotated,
            "in_aspect_band": in_band, "area_frac": round(area_frac, 3),
            "area_flagged": not (0.25 <= area_frac <= 0.95),
            "touches_edge": touches_edge,
            "glare_frac": round(glare_frac, 4), "focus_proxy": round(focus, 2),
            "gate_reasons": reasons}


def detect(path):
    """Detect a card rectangle in one still image. Returns a dict."""
    img = Image.open(path).convert("RGB")
    orig_w, orig_h = img.size
    scale = min(1.0, 640.0 / max(orig_w, orig_h))
    small = img.resize((max(1, int(orig_w * scale)), max(1, int(orig_h * scale))),
                       Image.LANCZOS)
    cand = _candidate_box(np.asarray(small.convert("L"), dtype=np.float64))
    base = {"orig_size": [orig_w, orig_h],
            "stability": "not_measurable_single_frame"}
    if cand is None:
        base.update({"status": "REFUSE", "reason": "no_quadrilateral_candidate",
                     "box": None})
        return base
    x1, y1, x2, y2 = [int(v / scale) for v in cand["bbox"]]
    gates = validate_box([x1, y1, x2, y2], [orig_w, orig_h], img)
    out = dict(base)
    out.update({"box": [x1, y1, x2, y2],
                "corners_orig": [[int(cx / scale), int(cy / scale)]
                                 for cx, cy in cand["corners"]],
                "component_pixels": cand["component_pixels"]})
    out.update(gates)
    if gates["gate_reasons"]:
        out.update({"status": "REFUSE",
                    "reason": ";".join(gates["gate_reasons"])})
    else:
        out.update({"status": "PASS", "reason": None})
    return out


def iou(a, b):
    """Axis-aligned IoU of [x1,y1,x2,y2] boxes (SAM boxes are axis-aligned)."""
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
    x2 = min(a[2], b[2]); y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    aa = (a[2] - a[0]) * (a[3] - a[1]); bb = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (aa + bb - inter) if (aa + bb - inter) else 0.0


if __name__ == "__main__":
    print(json.dumps(detect(sys.argv[1]), indent=2))
