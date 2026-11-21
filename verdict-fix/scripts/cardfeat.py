"""cardfeat.py - shared, deterministic photo measurements for card comparison.

Advisory measurements only. Nothing here produces a verdict word.
Each channel answers in the house contract shape:
  {"channel", "status": "ran"|"could_not_run", "value"/"values", "reason_code", "detail"}

Card size: 63 x 88 mm (Bulbapedia production article). Offset screens on cards
are fine (~150-200 lpi, i.e. ~6-8 lines/mm), so a halftone read needs roughly
>= 15 px/mm on the card (about 380 dpi). Below that the channel says
could_not_run / below_resolution instead of guessing.
"""
import numpy as np
import cv2

CARD_W_MM, CARD_H_MM = 63.0, 88.0
MIN_PX_PER_MM_HALFTONE = 15.0
CANON_W, CANON_H = 630, 880  # 10 px/mm canonical view for layout measurements


def load(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:  # webp etc. via PIL fallback
        from PIL import Image
        im = Image.open(path).convert("RGB")
        img = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    return img


def _order(pts):
    pts = pts.reshape(4, 2).astype(np.float32)
    s, d = pts.sum(1), np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)], pts[np.argmax(s)], pts[np.argmax(d)]], np.float32)


def find_card(img):
    """Return (quad or None, info). Looks for the largest 4-sided contour.
    If the card fills the frame (scan / tight crop), returns the full frame."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 100)
    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), 1)
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:5]:
        area = cv2.contourArea(c)
        if area < 0.25 * w * h:
            break
        peri = cv2.arcLength(c, True)
        ap = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(ap) == 4:
            best = ap
            break
    if best is not None and cv2.contourArea(_order(best)) / float(w * h) > 0.92:
        best = None  # "card" = whole frame: could be a scan, or a carpet edge field; check smooth region first
    if best is None:
        # textured backgrounds (carpet, wood) defeat edge contours: segment the card as the
        # large smooth region instead (low local variance), then take its rotated box.
        lv = cv2.blur((blur.astype(np.float32) - cv2.blur(blur.astype(np.float32), (9, 9))) ** 2, (15, 15))
        smooth = (lv < np.percentile(lv, 45)).astype(np.uint8) * 255
        smooth = cv2.morphologyEx(smooth, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
        c2, _ = cv2.findContours(smooth, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if c2:
            c = max(c2, key=cv2.contourArea)
            rect = cv2.minAreaRect(c); (rw, rh) = rect[1]
            ar = max(rw, rh) / (min(rw, rh) + 1e-6)
            if 0.1 * w * h < rw * rh < 0.9 * w * h and 1.2 < ar < 1.6:
                box = _order(cv2.boxPoints(rect))
                if np.linalg.norm(box[1] - box[0]) > np.linalg.norm(box[3] - box[0]):  # keep portrait
                    box = np.roll(box, -1, axis=0)
                return box, {"crop": "smooth_region", "card_fill": round(rw * rh / (w * h), 3)}
    if best is None:
        quad = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
        return quad, {"crop": "full_frame", "card_fill": 1.0}
    quad = _order(best)
    fill = cv2.contourArea(quad) / float(w * h)
    if fill > 0.92:
        quad = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
        return quad, {"crop": "full_frame", "card_fill": round(fill, 3)}
    return quad, {"crop": "contour", "card_fill": round(fill, 3)}


def warp(img, quad, W=CANON_W, H=CANON_H):
    dst = np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], np.float32)
    M = cv2.getPerspectiveTransform(quad, dst)
    return cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_AREA)


def px_per_mm(quad):
    top = np.linalg.norm(quad[1] - quad[0]); left = np.linalg.norm(quad[3] - quad[0])
    return float((top / CARD_W_MM + left / CARD_H_MM) / 2)


# ---------------------------------------------------------------- channels
def ch_capture(img, quad, info):
    """Capture-domain descriptors. NOT tells. Reported so nobody mistakes a
    capture difference (scan vs phone vs web image) for a print difference."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sharp = float(cv2.Laplacian(gray, cv2.CV_32F).var())
    blown = float((gray >= 250).mean())
    m = max(4, int(min(h, w) * 0.05)); ring = np.ones_like(gray, bool); ring[m:-m, m:-m] = False
    hp = np.abs(gray - cv2.GaussianBlur(gray, (0, 0), 2))
    edge_tex = float(hp[ring].mean())  # textured surroundings (carpet/table) or card border?
    return {"channel": "capture_profile", "status": "ran",
            "values": {"width": w, "height": h, "px_per_mm": round(px_per_mm(quad), 2),
                       "crop": info["crop"], "card_fill": info["card_fill"],
                       "laplacian_var": round(sharp, 1), "blown_share": round(blown, 4), "edge_ring_texture": round(edge_tex, 2)}}


def ch_halftone(img, quad):
    """Periodic-screen score. Offset print = AM halftone at fixed screen angles ->
    sharp periodic peaks in the 2D spectrum (rosette). Inkjet = FM/stochastic
    spray -> broadband noise, no peaks. Laser = screens often without the classic
    rosette plus toner scatter. Measured on native-resolution patches."""
    ppm = px_per_mm(quad)
    if ppm < MIN_PX_PER_MM_HALFTONE:
        return {"channel": "halftone_periodicity", "status": "could_not_run",
                "reason_code": "below_resolution",
                "detail": f"{ppm:.1f} px/mm on card; need >= {MIN_PX_PER_MM_HALFTONE} (about 380 dpi) to resolve a print screen"}
    # sample patches inside the card (avoid edges), native resolution
    xs = np.linspace(quad[:, 0].min(), quad[:, 0].max(), 7)[1:-1]
    ys = np.linspace(quad[:, 1].min(), quad[:, 1].max(), 9)[1:-1]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    P = 128
    win = np.outer(np.hanning(P), np.hanning(P))
    fy, fx = np.meshgrid(np.fft.fftfreq(P), np.fft.fftfreq(P), indexing="ij")
    fr = np.sqrt(fx ** 2 + fy ** 2)  # cycles/pixel
    # screen band in cycles/pixel from cycles/mm (4..12 lines/mm covers 100-300 lpi)
    lo, hi = 4.0 / ppm, min(12.0 / ppm, 0.49)
    band = (fr >= lo) & (fr <= hi)
    peak_scores, band_fracs = [], []
    for y in ys:
        for x in xs:
            y0, x0 = int(y - P / 2), int(x - P / 2)
            if y0 < 0 or x0 < 0 or y0 + P > img.shape[0] or x0 + P > img.shape[1]:
                continue
            patch_s = hsv[y0:y0 + P, x0:x0 + P, 1]
            if patch_s.mean() < 40:  # skip near-neutral areas (white/black solids show no screen)
                continue
            p = gray[y0:y0 + P, x0:x0 + P]
            p = (p - cv2.GaussianBlur(p, (0, 0), 6)) * win  # high-pass + window
            S = np.abs(np.fft.fft2(p)) ** 2
            S[0, 0] = 0
            tot = S[fr > 1.5 / P].sum() + 1e-9
            b = S[band]
            band_fracs.append(float(b.sum() / tot))
            peak_scores.append(float(np.sort(b)[-8:].mean() / (np.median(b) + 1e-9)))
    if len(peak_scores) < 4:
        return {"channel": "halftone_periodicity", "status": "could_not_run",
                "reason_code": "region_unreadable", "detail": "fewer than 4 coloured patches"}
    return {"channel": "halftone_periodicity", "status": "ran",
            "values": {"peak_to_median": round(float(np.median(peak_scores)), 2),
                       "band_power_frac": round(float(np.median(band_fracs)), 4),
                       "patches": len(peak_scores), "px_per_mm": round(ppm, 2)}}


def ch_text_edges(canon):
    """Sharpness of small dark print in the bottom strip (copyright / illustrator line).
    Scan-rebuilt fakes blur the smallest print. Normalised by local contrast so
    exposure does not dominate. Capture blur also lowers it - compare only
    like-for-like captures."""
    strip = cv2.cvtColor(canon[int(CANON_H * 0.93):int(CANON_H * 0.985), int(CANON_W * 0.05):int(CANON_W * 0.95)], cv2.COLOR_BGR2GRAY).astype(np.float32)
    if strip.std() < 8:
        return {"channel": "small_text_edges", "status": "could_not_run", "reason_code": "region_unreadable", "detail": "bottom strip has no contrast"}
    gx = cv2.Sobel(strip, cv2.CV_32F, 1, 0); gy = cv2.Sobel(strip, cv2.CV_32F, 0, 1)
    g = np.sqrt(gx ** 2 + gy ** 2)
    top = np.percentile(g, 99)
    return {"channel": "small_text_edges", "status": "ran",
            "values": {"edge_p99_over_contrast": round(float(top / (np.percentile(strip, 95) - np.percentile(strip, 5) + 1e-6)), 3)}}


def ch_back_blue(canon):
    """Back blue: genuine English backs show several blue shades (dappling) and a
    navy frame distinct from the swirl (TCGplayer: back comparison is its most
    reliable test). Measures blue-pixel Lab stats + low-frequency shade spread."""
    lab = cv2.cvtColor(canon, cv2.COLOR_BGR2LAB).astype(np.float32)
    hsv = cv2.cvtColor(canon, cv2.COLOR_BGR2HSV)
    blue = (hsv[..., 0] >= 95) & (hsv[..., 0] <= 135) & (hsv[..., 1] >= 60) & (hsv[..., 2] >= 30)
    frac = float(blue.mean())
    if frac < 0.2:
        return {"channel": "back_blue", "status": "could_not_run", "reason_code": "family_not_applicable",
                "detail": f"only {frac:.0%} blue pixels - not an English-style back, or wrong side"}
    L, a, b = lab[..., 0][blue], lab[..., 1][blue] - 128, lab[..., 2][blue] - 128
    Lblur = cv2.GaussianBlur(lab[..., 0], (0, 0), 6)[blue]
    # frame vs swirl: outer 6% ring vs interior
    ring = np.zeros(blue.shape, bool); m = int(CANON_W * 0.06)
    ring[:m, :] = ring[-m:, :] = ring[:, :m] = ring[:, -m:] = True
    fr_L = float(lab[..., 0][ring & blue].mean()) if (ring & blue).any() else float("nan")
    in_L = float(lab[..., 0][(~ring) & blue].mean())
    return {"channel": "back_blue", "status": "ran",
            "values": {"blue_frac": round(frac, 3), "L_mean": round(float(L.mean()) * 100 / 255, 2),
                       "a_mean": round(float(a.mean()), 2), "b_mean": round(float(b.mean()), 2),
                       "hue_deg": round(float(np.degrees(np.arctan2(b.mean(), a.mean())) % 360), 1),
                       "shade_spread_L": round(float(np.percentile(Lblur, 90) - np.percentile(Lblur, 10)) * 100 / 255, 2),
                       "frame_minus_swirl_L": round((fr_L - in_L) * 100 / 255, 2)}}


def ch_centering(canon):
    """Border centering from the inner frame line. Real cards are often off-centre,
    so this is a layout descriptor and a crop sanity check, never a tell alone."""
    gray = cv2.GaussianBlur(cv2.cvtColor(canon, cv2.COLOR_BGR2GRAY).astype(np.float32), (3, 3), 0)
    def edge_pos(profile, rev=False):
        p = profile[::-1] if rev else profile
        d = np.abs(np.diff(p[: int(len(p) * 0.15)]))
        d[:3] = 0  # ignore the physical edge
        i = int(np.argmax(d)); return i if d[i] > 6 else None
    vals = {k: [] for k in "LRTB"}
    for y in np.linspace(CANON_H * 0.3, CANON_H * 0.7, 9).astype(int):
        r = gray[y, :]; vals["L"].append(edge_pos(r)); vals["R"].append(edge_pos(r, True))
    for x in np.linspace(CANON_W * 0.3, CANON_W * 0.7, 9).astype(int):
        c = gray[:, x]; vals["T"].append(edge_pos(c)); vals["B"].append(edge_pos(c, True))
    med = {}
    for k, v in vals.items():
        v = [q for q in v if q is not None]
        if len(v) < 5:
            return {"channel": "centering", "status": "could_not_run", "reason_code": "region_unreadable", "detail": f"frame line not found on side {k}"}
        med[k] = float(np.median(v))
    lr = med["L"] / (med["L"] + med["R"] + 1e-6); tb = med["T"] / (med["T"] + med["B"] + 1e-6)
    return {"channel": "centering", "status": "ran",
            "values": {"left_right": f"{lr*100:.0f}/{(1-lr)*100:.0f}", "top_bottom": f"{tb*100:.0f}/{(1-tb)*100:.0f}",
                       "border_mm": {k: round(v / 10, 2) for k, v in med.items()}}}


def ch_color_hist(canon_a, canon_b):
    """Hue/saturation histogram distance. WARNING (house record, Tells v2 calibration
    Oct 27): this fired strong on 16/17 pairs because it separates scanner scans
    from seller photos. Treat as a capture-match check, not a print tell."""
    def h(c):
        hsv = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)
        H = cv2.calcHist([hsv], [0, 1], None, [30, 16], [0, 180, 0, 256]); return cv2.normalize(H, H).flatten()
    return {"channel": "hs_histogram_distance", "status": "ran",
            "values": {"bhattacharyya": round(float(cv2.compareHist(h(canon_a), h(canon_b), cv2.HISTCMP_BHATTACHARYYA)), 3)}}


def measure(path, side="front"):
    img = load(path)
    quad, info = find_card(img)
    canon = warp(img, quad)
    out = [ch_capture(img, quad, info), ch_halftone(img, quad), ch_text_edges(canon), ch_centering(canon)]
    if side == "back":
        out.append(ch_back_blue(canon))
    return out, canon
