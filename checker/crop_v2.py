#!/usr/bin/env python3
"""Pip Job B crop v2: smoothed-colour mask + 10% inset, fallback to v0.

Why v1 failed: raw colour distance from the corner-median carpet
colour flags 77% of pixels (carpet texture/shading varies by >40),
so the largest component is the whole image. v2 smooths each colour
channel with a 21px box blur first (suppresses carpet texture), then
masks distance > 35 from the corner-median background. That finds
the card region (phone IoU mean ~0.44 before inset), but the blur
bleeds card colour ~10% outward, so boxes are systematically too
large (many touch the frame). A fixed 10% inset per side is measured,
not guessed: phone 26 inset sweep 0.00->0.10->0.12->0.15->0.18 gives
good (IoU>=0.80) 0 -> 11 -> 11 -> 4 -> 2, mean 0.443 -> 0.577 -> 0.564
-> 0.516 -> 0.445. 0.10 is the peak; it is frozen here.
If v2 yields no gate-passing box, fall back to v0 and report branch.
No SAM calls; SAM boxes are the answer key only in the harness.
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
# Standalone fix (Oct 29, 2026): on_device_crop.py is bundled in this folder.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from on_device_crop import _blur, detect as v0_detect, validate_box, PORTRAIT, LANDSCAPE  # noqa

INSET = 0.10

def detect_v2(path):
    img = Image.open(path).convert("RGB"); W, H = img.size
    scale = min(1.0, 640.0 / max(W, H))
    small = img.resize((max(1, int(W * scale)), max(1, int(H * scale))), Image.LANCZOS)
    a = np.asarray(small, dtype=np.float64); h, w, _ = a.shape
    b = np.stack([_blur(a[:, :, c], k=21) for c in range(3)], axis=2)
    ph, pw = int(h * 0.08), int(w * 0.08); patches = []
    for (y0, x0) in [(0, 0), (0, w - pw), (h - ph, 0), (h - ph, w - pw)]:
        patches.append(b[y0:y0 + ph, x0:x0 + pw].reshape(-1, 3))
    bg = np.median(np.concatenate(patches, axis=0), axis=0)
    dist = np.sqrt(((b - bg) ** 2).sum(axis=2))
    mask = dist > 35
    closed = ndimage.binary_closing(mask, structure=np.ones((3, 3)), iterations=2)
    lab, n = ndimage.label(closed)
    if n == 0:
        return {"branch": "v2_none", "status": "REFUSE", "reason": "no_colour_component", "box": None}
    sizes = np.bincount(lab.ravel(), minlength=n + 1); objs = ndimage.find_objects(lab)
    for idx in np.argsort(sizes[1:])[::-1][:10] + 1:
        sl = objs[idx - 1]
        if sl is None: continue
        y1, y2 = sl[0].start, sl[0].stop - 1; x1, x2 = sl[1].start, sl[1].stop - 1
        bw, bh = x2 - x1, y2 - y1
        if bw <= 0 or bh <= 0: continue
        aspect = bw / bh; area = (bw * bh) / (w * h)
        if not (PORTRAIT[0] <= aspect <= PORTRAIT[1] or LANDSCAPE[0] <= aspect <= LANDSCAPE[1]): continue
        if not (0.25 <= area <= 0.95): continue
        box = [int(x1 / scale), int(y1 / scale), int(x2 / scale), int(y2 / scale)]
        bx1, by1, bx2, by2 = box; bw2, bh2 = bx2 - bx1, by2 - by1
        ix, iy = int(bw2 * INSET), int(bh2 * INSET)
        box = [bx1 + ix, by1 + iy, bx2 - ix, by2 - iy]
        gates = validate_box(box, [W, H], img)
        out = {"branch": "v2", "box": box}; out.update(gates)
        if gates["gate_reasons"]:
            out.update({"status": "REFUSE", "reason": ";".join(gates["gate_reasons"])})
        else:
            out.update({"status": "PASS", "reason": None})
        return out
    return {"branch": "v2_none", "status": "REFUSE", "reason": "no_card_band_component", "box": None}

def detect(path):
    r = detect_v2(path)
    if r["status"] == "PASS":
        return r
    v0 = v0_detect(path); v0["branch"] = "v0_fallback"; return v0
