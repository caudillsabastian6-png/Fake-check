#!/usr/bin/env python3
"""Self-test of the halftone channel on SYNTHETIC prints (not real cards).
Builds an AM-screened CMYK print (offset-style, rotated screens -> rosette) and an
FM/error-diffusion print (inkjet-style) from the same source image at 24 px/mm,
then checks the periodicity score separates them. Proves the metric reads what it
claims; says nothing about real fakes."""
import sys, os, numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__)); import cardfeat as cf
src = cf.load(sys.argv[1]); H, W = 2112, 1512  # 88x63 mm @ 24 px/mm
src = cv2.resize(src, (W, H)).astype(np.float32) / 255
rgb = src[..., ::-1]; K = 1 - rgb.max(2); C = (1 - rgb[..., 0] - K) / (1 - K + 1e-6); M = (1 - rgb[..., 1] - K) / (1 - K + 1e-6); Y = (1 - rgb[..., 2] - K) / (1 - K + 1e-6)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); period = 24 / 6.0  # 6 lines/mm ~ 150 lpi
def am(ch, ang):
    a = np.radians(ang); u = xx * np.cos(a) + yy * np.sin(a); v = -xx * np.sin(a) + yy * np.cos(a)
    spot = (np.cos(2 * np.pi * u / period) + np.cos(2 * np.pi * v / period)) / 4 + 0.5
    return (ch > 1 - spot).astype(np.float32)
def fm(ch):
    rng = np.random.default_rng(0); return (rng.random(ch.shape) < ch).astype(np.float32)
def compose(c, m, y, k):
    r = (1 - c) * (1 - k); g = (1 - m) * (1 - k); b = (1 - y) * (1 - k)
    return (np.dstack([b, g, r]) * 255).astype(np.uint8)
amimg = compose(am(C, 15), am(M, 75), am(Y, 0), am(K, 45)); fmimg = compose(fm(C), fm(M), fm(Y), fm(K))
amimg = cv2.GaussianBlur(amimg, (3, 3), 0.7); fmimg = cv2.GaussianBlur(fmimg, (3, 3), 0.7)  # mild optics
q = np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], np.float32)
for name, im in [("AM offset-style", amimg), ("FM inkjet-style", fmimg)]:
    print(name, cf.ch_halftone(im, q))
    small = cv2.resize(im, (330, 462), interpolation=cv2.INTER_AREA)  # what a 520px web/phone copy keeps
    print("  same print at 5 px/mm:", cf.ch_halftone(small, np.array([[0,0],[329,0],[329,461],[0,461]], np.float32))["status"])
cv2.imwrite(os.path.join(sys.argv[2], "synthetic_AM_patch.png"), amimg[900:1100, 600:800]); cv2.imwrite(os.path.join(sys.argv[2], "synthetic_FM_patch.png"), fmimg[900:1100, 600:800])
