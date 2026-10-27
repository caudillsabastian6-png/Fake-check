#!/usr/bin/env python3
"""Pip Job B crop v1: background-colour mask detector, fallback to v0.

v0 failure (Job A): on phone carpet photos, Sobel texture inside the
card and on carpet is almost identical, so the largest edge component
is often background or an art fragment (phone IoU mean 0.243, 1/26).
v1 hypothesis: the card's COLOUR differs from the carpet background
even when texture does not. Background = median RGB of corner patches
(8% each, same idea as multi_detect). Mask = colour distance > 40
from background, closing, largest component whose bbox aspect is in
the card bands and area 0.25-0.95. If v1 yields no gate-passing box,
fall back to v0 (detect()) and report which branch was used.
No SAM calls; SAM boxes are the answer key only in the harness.
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.expanduser("~/workspace/fake-check/pip-ondevice-prototype"))
from on_device_crop import detect as v0_detect, validate_box, PORTRAIT, LANDSCAPE  # noqa

def detect_v1(path):
    img = Image.open(path).convert("RGB")
    W, H = img.size
    scale = min(1.0, 640.0 / max(W, H))
    small = img.resize((max(1, int(W * scale)), max(1, int(H * scale))), Image.LANCZOS)
    a = np.asarray(small, dtype=np.float64)
    h, w, _ = a.shape
    ph, pw = int(h * 0.08), int(w * 0.08)
    patches = []
    for (y0, x0) in [(0, 0), (0, w - pw), (h - ph, 0), (h - ph, w - pw)]:
        patches.append(a[y0:y0 + ph, x0:x0 + pw].reshape(-1, 3))
    bg = np.median(np.concatenate(patches, axis=0), axis=0)
    dist = np.sqrt(((a - bg) ** 2).sum(axis=2))
    mask = dist > 40
    closed = ndimage.binary_closing(mask, structure=np.ones((3, 3)), iterations=2)
    lab, n = ndimage.label(closed)
    if n == 0:
        return {"branch": "v1_none", "status": "REFUSE", "reason": "no_colour_component", "box": None}
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    objs = ndimage.find_objects(lab)
    for idx in np.argsort(sizes[1:])[::-1][:10] + 1:
        sl = objs[idx - 1]
        if sl is None: continue
        y1, y2 = sl[0].start, sl[0].stop - 1
        x1, x2 = sl[1].start, sl[1].stop - 1
        bw, bh = x2 - x1, y2 - y1
        if bw <= 0 or bh <= 0: continue
        aspect = bw / bh; area = (bw * bh) / (w * h)
        if not (PORTRAIT[0] <= aspect <= PORTRAIT[1] or LANDSCAPE[0] <= aspect <= LANDSCAPE[1]): continue
        if not (0.25 <= area <= 0.95): continue
        box = [int(x1 / scale), int(y1 / scale), int(x2 / scale), int(y2 / scale)]
        gates = validate_box(box, [W, H], img)
        out = {"branch": "v1", "box": box}
        out.update(gates)
        if gates["gate_reasons"]:
            out.update({"status": "REFUSE", "reason": ";".join(gates["gate_reasons"])})
        else:
            out.update({"status": "PASS", "reason": None})
        return out
    return {"branch": "v1_none", "status": "REFUSE", "reason": "no_card_band_component", "box": None}

def detect(path):
    """v1 first, v0 fallback. Returns dict with branch used."""
    r = detect_v1(path)
    if r["status"] == "PASS":
        return r
    v0 = v0_detect(path)
    v0["branch"] = "v0_fallback"
    # Prefer v1 REFUSE reason if v0 also refuses? No: report both, caller
    # counts PASS only. Keep v0 result as the fallback result.
    return v0
