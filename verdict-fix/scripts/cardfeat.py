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


CARD_AR = CARD_H_MM / CARD_W_MM  # 1.397


def _rect_quad(rect):
    box = _order(cv2.boxPoints(rect))
    if np.linalg.norm(box[1] - box[0]) > np.linalg.norm(box[3] - box[0]):  # keep portrait
        box = np.roll(box, -1, axis=0)
    return box.astype(np.float32)


def _card_like(rect, frame_area, cnt_area=None, ar_tol=0.12):
    (rw, rh) = rect[1]
    if min(rw, rh) < 1:
        return False
    ar = max(rw, rh) / min(rw, rh)
    fill = rw * rh / frame_area
    sol = (cnt_area / (rw * rh)) if cnt_area is not None else 1.0
    return abs(ar - CARD_AR) <= ar_tol * CARD_AR and 0.02 <= fill <= 0.97 and sol >= 0.80


def _bg_model_candidates(img, max_side=640):
    """Busy backgrounds (carpet, wood, cloth) defeat edge contours: the texture makes
    hundreds of edges. Instead model the BACKGROUND from the outer ring of the frame
    (k-means colours in Lab after a blur that melts carpet loops), mark everything far
    from it as foreground, and keep card-shaped blobs. Returns [(quad, area_frac)] in
    full-res coordinates, largest first."""
    h, w = img.shape[:2]
    s = max_side / max(h, w)
    sm = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else img.copy()
    s = sm.shape[1] / w
    lab = cv2.cvtColor(cv2.medianBlur(cv2.GaussianBlur(sm, (0, 0), 2.5), 7), cv2.COLOR_BGR2LAB).astype(np.float32)
    H, W = lab.shape[:2]
    m = max(3, int(min(H, W) * 0.04))
    ring = np.zeros((H, W), bool); ring[:m] = ring[-m:] = True; ring[:, :m] = ring[:, -m:] = True
    px = lab[ring].reshape(-1, 3)
    K = 4
    _, _, C = cv2.kmeans(px, K, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5), 3, cv2.KMEANS_PP_CENTERS)
    d = np.min(np.linalg.norm(lab.reshape(-1, 1, 3) - C.reshape(1, K, 3), axis=2), axis=1).reshape(H, W)
    thr = max(12.0, float(np.percentile(d[ring], 97)) * 1.25)
    fg = (d > thr).astype(np.uint8) * 255
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(fg); cv2.drawContours(filled, cnts, -1, 255, -1)  # fill holes (dark art inside card)
    cnts, _ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cnts:
        a = cv2.contourArea(c)
        if a < 0.02 * H * W:
            continue
        hull = cv2.convexHull(c)  # edge bites (holo/sleeve glare matching the floor) are bridged
        rect = cv2.minAreaRect(hull)
        if _card_like(rect, H * W, cv2.contourArea(hull), ar_tol=0.14):
            q = _rect_quad(rect)
            per = cv2.arcLength(hull, True)
            for eps in (0.01, 0.02, 0.03, 0.04):  # perspective quad when the hull has 4 clear corners
                ap = cv2.approxPolyDP(hull, eps * per, True)
                if len(ap) == 4:
                    q4 = _order(ap)
                    if cv2.contourArea(q4) > 0.9 * rect[1][0] * rect[1][1]:
                        q = q4
                    break
            out.append(((q / s).astype(np.float32), rect[1][0] * rect[1][1] / (H * W)))
    return sorted(out, key=lambda t: -t[1])


def _navy_outside(img, quad):
    """Back-side guard: True when the band just OUTSIDE the quad is still the navy
    back frame, i.e. the finder locked onto the inner swirl, not the card edge."""
    h, w = img.shape[:2]
    c = quad.mean(0)
    outer = (c + (quad - c) * 1.06).astype(np.int32)
    mask = np.zeros((h, w), np.uint8)
    cv2.fillConvexPoly(mask, outer, 255); cv2.fillConvexPoly(mask, quad.astype(np.int32), 0)
    if mask.sum() == 0:
        return False
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sel = mask > 0
    H, S, V = hsv[..., 0][sel], hsv[..., 1][sel], hsv[..., 2][sel]
    navy = ((H >= 100) & (H <= 130) & (S >= 70) & (V >= 25)).mean()
    return navy > 0.5


def find_card(img, side=None):
    """Return (quad, info). Order: (1) a clean 4-sided edge contour with card shape;
    (2) background-model segmentation (busy backgrounds); (3) full frame (scan or
    tight crop). On backs, a quad whose outside band is still navy frame is rejected
    (inner-swirl lock) and the next candidate / full frame is used."""
    h, w = img.shape[:2]
    A = float(w * h)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.dilate(cv2.Canny(blur, 30, 100), np.ones((5, 5), np.uint8), 1)
    cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cands = []
    for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:5]:
        area = cv2.contourArea(c)
        if area < 0.08 * A:
            break
        ap = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
        if len(ap) == 4:
            q = _order(ap)
            rect = cv2.minAreaRect(ap)
            if _card_like(rect, A, cv2.contourArea(q)):
                cands.append((q, "contour"))
    frame_card_shaped = bool(abs(max(h, w) / min(h, w) - CARD_AR) < 0.12 * CARD_AR)
    for q, f in _bg_model_candidates(img)[:1]:
        # single-card photo guards (tight crops otherwise yield the text box or art box):
        # the card must take >= 15% of the frame and lie the same way round as the frame.
        long_axis = q[3] - q[0]  # quads are ordered so this is the card's long side
        long_is_vertical = abs(long_axis[1]) >= abs(long_axis[0])
        if f < 0.15 or (long_is_vertical != (h >= w)):
            continue
        # a card-shaped frame that the "card" already fills >= 70% of is a scan or tight
        # crop: the outer ring is card border, not floor, so the model would cut into it.
        if not (frame_card_shaped and f >= 0.70):
            cands.append((q, "bg_model"))
    rejected = []
    for q, how in cands:
        if side == "back" and _navy_outside(img, q):
            rejected.append(how + ":inner_frame_lock"); continue
        info = {"crop": how, "card_fill": round(float(cv2.contourArea(q)) / A, 3)}
        if rejected:
            info["rejected"] = rejected
        return q, info
    quad = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
    info = {"crop": "full_frame", "card_fill": 1.0, "frame_card_shaped": frame_card_shaped}
    if rejected:
        info["rejected"] = rejected
    return quad, info


def find_cards(img):
    """All card-shaped blobs (multi-card photos, e.g. forum real-vs-fake line-ups),
    left-to-right then top-to-bottom. For cropping test images only."""
    qs = [q for q, _ in _bg_model_candidates(img)]
    return qs


def warp(img, quad, W=CANON_W, H=CANON_H):
    dst = np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], np.float32)
    M = cv2.getPerspectiveTransform(quad, dst)
    return cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_AREA)


def px_per_mm(quad):
    top = np.linalg.norm(quad[1] - quad[0]); left = np.linalg.norm(quad[3] - quad[0])
    return float((top / CARD_W_MM + left / CARD_H_MM) / 2)


# ---------------------------------------------------------------- channels
def ch_capture(img, quad, info, canon=None):
    """Capture-domain descriptors. NOT tells. Reported so nobody mistakes a
    capture difference (scan vs phone vs web image) for a print difference."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sharp = float(cv2.Laplacian(gray, cv2.CV_32F).var())
    blown = float((gray >= 250).mean())
    m = max(4, int(min(h, w) * 0.05)); ring = np.ones_like(gray, bool); ring[m:-m, m:-m] = False
    hp = np.abs(gray - cv2.GaussianBlur(gray, (0, 0), 2))
    edge_tex = float(hp[ring].mean())  # textured surroundings (carpet/table) or card border?
    vals = {"width": w, "height": h, "px_per_mm": round(px_per_mm(quad), 2),
            "crop": info["crop"], "card_fill": info["card_fill"],
            "laplacian_var": round(sharp, 1), "blown_share": round(blown, 4), "edge_ring_texture": round(edge_tex, 2),
            "framing": "card_in_scene" if info["card_fill"] < 0.9 else "fills_frame"}
    if canon is not None:  # sharpness / noise ON THE CARD at a fixed 10 px/mm view, so framing can't move it
        cg = cv2.cvtColor(canon, cv2.COLOR_BGR2GRAY).astype(np.float32)
        # content-normalised focus: fine-scale vs coarse-scale detail energy. A busy card and a
        # plain card in the same capture score alike; a soft/phone capture scores lower.
        fine = float(cv2.Laplacian(cg, cv2.CV_32F).var())
        coarse = float(cv2.Laplacian(cv2.GaussianBlur(cg, (0, 0), 2.0), cv2.CV_32F).var()) + 1e-6
        vals["card_sharpness"] = round(fine / coarse, 2)
        hp2 = np.abs(cg - cv2.medianBlur(cv2.cvtColor(canon, cv2.COLOR_BGR2GRAY), 3).astype(np.float32))
        vals["card_fine_noise"] = round(float(np.median(hp2)), 3)
    return {"channel": "capture_profile", "status": "ran", "values": vals}


def capture_match(ra, rb):
    """Do two capture_profile value dicts look like the same kind of capture?
    Returns (same: bool, reasons: [str]). Any one reason = CAPTURE MISMATCH.
    v1 checked px/mm + crop + raw edge-ring texture and fired on 1/3 render-vs-carpet
    pairs; v2 adds framing (scene vs fills-frame) and on-card sharpness at a fixed scale."""
    why = []
    pa, pb = ra["px_per_mm"], rb["px_per_mm"]
    if max(pa, pb) / max(1e-6, min(pa, pb)) > 1.35:
        why.append(f"resolution on card {pa} vs {pb} px/mm")
    if ra.get("framing") != rb.get("framing"):
        why.append(f"framing {ra.get('framing')} vs {rb.get('framing')} (photo of a card in a scene vs a scan/render/tight crop)")
    sa, sb = ra.get("card_sharpness"), rb.get("card_sharpness")
    if sa and sb and max(sa, sb) / max(1e-6, min(sa, sb)) > 1.6:
        why.append(f"on-card sharpness {sa} vs {sb} (x{max(sa, sb) / max(1e-6, min(sa, sb)):.1f})")
    ea, eb = ra["edge_ring_texture"], rb["edge_ring_texture"]
    if ra.get("framing") == rb.get("framing") == "card_in_scene" and max(ea, eb) / max(1e-3, min(ea, eb)) > 2.5:
        why.append(f"background texture {ea} vs {eb}")
    return (len(why) == 0, why)


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
    return _halftone_core(img, quad, ppm)


def _halftone_core(img, quad, ppm):
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
    if len(peak_scores) < 2:
        return {"channel": "halftone_periodicity", "status": "could_not_run",
                "reason_code": "region_unreadable", "detail": "fewer than 2 coloured patches"}
    return {"channel": "halftone_periodicity", "status": "ran",
            "values": {"peak_to_median": round(float(np.median(peak_scores)), 2),
                       "band_power_frac": round(float(np.median(band_fracs)), 4),
                       "patches": len(peak_scores), "px_per_mm": round(ppm, 2)}}



def ch_halftone_known_scale(img, ppm, target_ppm=24.0):
    """Screen-periodicity read on a close-up/macro whose scale is KNOWN (scale bar, ruler
    or the capture app's fixed macro distance) instead of measured from a card outline.
    Resamples to ~24 px/mm so the 4-12 lines/mm band sits where ch_halftone expects it,
    then scores 128 px tiles over the whole frame. Same output contract."""
    if ppm is None or ppm < MIN_PX_PER_MM_HALFTONE:
        return {"channel": "halftone_periodicity", "status": "could_not_run", "reason_code": "below_resolution",
                "detail": f"{ppm} px/mm; need >= {MIN_PX_PER_MM_HALFTONE}"}
    fov_mm = min(img.shape[:2]) / ppm  # narrow microscope fields: keep >= ~300 px across
    target_ppm = max(target_ppm, 300.0 / max(fov_mm, 1e-6))
    f = target_ppm / ppm
    im = cv2.resize(img, None, fx=f, fy=f, interpolation=cv2.INTER_AREA) if f < 1 else img
    eff = ppm * min(f, 1.0)
    h, w = im.shape[:2]
    if min(h, w) < 160:
        return {"channel": "halftone_periodicity", "status": "could_not_run", "reason_code": "region_too_small",
                "detail": f"{w}x{h} px after resampling to {eff:.0f} px/mm (< 6.7 mm of card in view)"}
    quad = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
    # reuse ch_halftone's spectral core by faking a card-sized quad at the effective scale
    out = _halftone_core(im, quad, eff)
    if out["status"] == "ran":
        out["values"]["source_px_per_mm"] = round(float(ppm), 1)
    return out


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
    quad, info = find_card(img, side)
    canon = warp(img, quad)
    out = [ch_capture(img, quad, info, canon), ch_halftone(img, quad), ch_text_edges(canon), ch_centering(canon)]
    if side == "back":
        out.append(ch_back_blue(canon))
    return out, canon
