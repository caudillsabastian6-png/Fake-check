#!/usr/bin/env python3
"""eval_web.py - measure the prototype channels on the OUTSIDE web test set.

Results on web images are NOT accuracy claims: tiny n, re-compressed images, labels
taken from forum/blog captions, crops cut by hand. Denominators are written to
OUT/denominators-locked.json BEFORE any measurement runs.
Usage: python3 eval_web.py WEB_SET_DIR OUT_DIR
"""
import sys, os, json
import numpy as np
import cv2
sys.path.insert(0, os.path.dirname(__file__))
import cardfeat as cf
from eval_harness import wilson, auc, loo

MACRO_TYPES = {"microscope", "lab_macro", "loupe_phone", "phone_closeup", "composite_graphic", "edge_macro"}
PAIR_KINDS = ("same_photo", "same_photo_genuine_control", "composite_two_photos", "same_session_not_same_photo")


def W(x, n):
    lo, hi = wilson(x, n)
    return f"{x}/{n} [{lo*100:.1f}-{hi*100:.1f}%]" if n else "0/0"


def num(chs):
    d = {}
    for ch in chs:
        if ch["status"] == "ran":
            for k, v in ch["values"].items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    d[f"{ch['channel']}.{k}"] = v
    return d


def mean_L(canon):
    return float(cv2.cvtColor(canon, cv2.COLOR_BGR2LAB)[60:-60, 50:-50, 0].mean())


def main():
    web, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    rows = json.load(open(os.path.join(web, "manifest.json")))["rows"]
    lab = [r for r in rows if r["label"] in ("GENUINE", "FAKE")]
    sp = {}
    for r in lab:
        if r["pair_kind"] in PAIR_KINDS:
            sp.setdefault((r["pair_kind"], r["pair_id"]), []).append(r)
    for (kind, pid), lst in list(sp.items()):  # genuine controls: GG crop + the genuine crop of the same photo
        if kind == "same_photo_genuine_control":
            src = lst[0]["crop_of"]
            g2 = next(r for r in lab if r["crop_of"] == src and r["pair_kind"] == "same_photo" and r["label"] == "GENUINE")
            sp[(kind, pid)] = [g2, lst[0]]
    cards = [r for r in lab if r["photo_type"] not in MACRO_TYPES]
    ros = [r for r in lab if r["est_px_per_mm"] not in ("", None) and float(r["est_px_per_mm"]) >= 15]
    den = {"locked_before_measurement": True,
           "pairs": {k: sum(1 for (kk, _) in sp if kk == k) for k in PAIR_KINDS},
           "pair_ids": {f"{k}|{p}": [r["image_id"] for r in v] for (k, p), v in sp.items()},
           "single_card_images_by_photo_type": {},
           "rosette_lane_candidates_ge15ppm": {"GENUINE": sum(r["label"] == "GENUINE" for r in ros),
                                               "FAKE": sum(r["label"] == "FAKE" for r in ros),
                                               "ids": [r["image_id"] for r in ros]}}
    for r in cards:
        k = f"{r['photo_type']}|{r['side']}"
        den["single_card_images_by_photo_type"].setdefault(k, {"GENUINE": 0, "FAKE": 0})[r["label"]] += 1
    json.dump(den, open(os.path.join(out, "denominators-locked.json"), "w"), indent=1)

    meas = {}

    def M(r):
        if r["image_id"] not in meas:
            meas[r["image_id"]] = cf.measure(os.path.join(web, r["file"]), "back" if r["side"] == "back" else "front")
        return meas[r["image_id"]]

    lines = ["# Web test set - measurements (NOT accuracy claims)", "",
             "Denominators locked first (`denominators-locked.json`). Labels = source captions. Hand-cut crops. Tiny n.", ""]
    # 1. paired comparisons -------------------------------------------------
    pair_res = []
    for (kind, pid), lst in sorted(sp.items()):
        if kind == "composite_two_photos" or len(lst) != 2 or any(r["photo_type"] in MACRO_TYPES for r in lst):
            continue
        g = next(r for r in lst if r["label"] == "GENUINE")
        c = [r for r in lst if r is not g][0]
        (gc, gcan), (cc, ccan) = M(g), M(c)
        same, why = cf.capture_match(gc[0]["values"], cc[0]["values"])
        gv, cv = num(gc), num(cc)
        flags = []
        te = "small_text_edges.edge_p99_over_contrast"
        if te in gv and te in cv and cv[te] < 0.7 * gv[te]:
            flags.append("softer_small_print")
        if g["side"] == "back":
            k = "back_blue.shade_spread_L"
            if k in gv and k in cv and cv[k] < 0.7 * gv[k]:
                flags.append("flatter_back_blue")
            k = "back_blue.hue_deg"
            if k in gv and k in cv and abs(cv[k] - gv[k]) > 12:
                flags.append("back_hue_shift")
        hp = "halftone_periodicity.peak_to_median"
        if hp in gv and hp in cv and cv[hp] < 0.6 * gv[hp]:
            flags.append("less_periodic_screen")
        pair_res.append({"kind": kind, "pair": pid, "ref": g["image_id"], "cand": c["image_id"], "cand_label": c["label"],
                         "side": g["side"], "capture_same": same, "capture_why": why, "flags": flags,
                         "lightness_delta_L": round(mean_L(ccan) - mean_L(gcan), 2), "values_ref": gv, "values_cand": cv})
    lines += ["## 1. Paired look-closer flags (reference = genuine from the same photo / session)", "",
              "| set | pairs | capture judged SAME | any look-closer flag |", "|---|---|---|---|"]
    for kind in ("same_photo", "same_photo_genuine_control", "same_session_not_same_photo"):
        sel = [p for p in pair_res if p["kind"] == kind]
        lines.append(f"| {kind} | {len(sel)} | {W(sum(p['capture_same'] for p in sel), len(sel))} | {W(sum(bool(p['flags']) for p in sel), len(sel))} |")
    lines += ["", "Same-photo G->F: a flag = catch. Genuine controls (two real copies in one photo): a flag = false flag.", "",
              "| pair | ref | cand | cand label | capture same? | flags | dL cand-ref |", "|---|---|---|---|---|---|---|"]
    for p in pair_res:
        cs = "yes" if p["capture_same"] else "NO: " + "; ".join(p["capture_why"])[:100]
        lines.append(f"| {p['pair']} | {p['ref']} | {p['cand']} | {p['cand_label']} | {cs} | {', '.join(p['flags']) or '-'} | {p['lightness_delta_L']} |")
    spf = [p for p in pair_res if p["kind"] == "same_photo" and p["side"] == "front"]
    ctrl = [p for p in pair_res if p["kind"] == "same_photo_genuine_control"]
    lines += ["", "### Paired direction per feature (same-photo G->F fronts): how often the fake reads LOWER than its genuine twin", "",
              "50% = coin flip. Genuine controls show the same count for 2nd real copy vs 1st.", "",
              "| feature | fake lower than twin | controls: 2nd genuine lower |", "|---|---|---|"]
    skip = ("capture_profile.width", "capture_profile.height", "capture_profile.card_fill", "capture_profile.px_per_mm")
    feats = sorted({k for p in spf for k in p["values_ref"] if k in p["values_cand"] and k not in skip})
    for k in feats + ["lightness_delta_L"]:
        if k == "lightness_delta_L":
            x, n = sum(p[k] < 0 for p in spf), len(spf)
            xc, nc = sum(p[k] < 0 for p in ctrl), len(ctrl)
        else:
            v = [p for p in spf if k in p["values_cand"] and k in p["values_ref"]]
            vc = [p for p in ctrl if k in p["values_cand"] and k in p["values_ref"]]
            x, n = sum(p["values_cand"][k] < p["values_ref"][k] for p in v), len(v)
            xc, nc = sum(p["values_cand"][k] < p["values_ref"][k] for p in vc), len(vc)
        lines.append(f"| {k} | {W(x, n)} | {W(xc, nc)} |")
    # 2. unpaired by photo type --------------------------------------------
    lines += ["", "## 2. Unpaired single-image features, split by photo type (top 6 by separation)", ""]
    groups = {}
    for r in cards:
        groups.setdefault(f"{r['photo_type']}|{r['side']}", []).append(r)
    for gk, lst in sorted(groups.items()):
        ng = sum(r["label"] == "GENUINE" for r in lst); nf = len(lst) - ng
        lines.append(f"**{gk}**: genuine {ng}, fake {nf}")
        if ng < 3 or nf < 3:
            lines.append("  - too few in a class to compute anything"); continue
        vals = [num(M(r)[0]) for r in lst]
        labels = [1 if r["label"] == "FAKE" else 0 for r in lst]
        res = []
        for k in sorted({k for v in vals for k in v}):
            ok = [i for i, v in enumerate(vals) if k in v]
            g = [vals[i][k] for i in ok if labels[i] == 0]; f = [vals[i][k] for i in ok if labels[i] == 1]
            if len(g) < 3 or len(f) < 3:
                continue
            A = auc(g, f); cx, nf2, fx, ng2 = loo([vals[i][k] for i in ok], [labels[i] for i in ok])
            res.append((max(A, 1 - A), k, cx, nf2, fx, ng2))
        for sep, k, cx, nf2, fx, ng2 in sorted(res, reverse=True)[:6]:
            cap = " (CAPTURE descriptor - confound, not a tell)" if k.startswith("capture_profile") else ""
            lines.append(f"  - {k}{cap}: sep {sep:.2f}; LOO catch {W(cx, nf2)}; false-flag {W(fx, ng2)}")
    # 3. rosette lane ---------------------------------------------------------
    lines += ["", "## 3. Screen-periodicity (rosette) lane on images at >= 15 px/mm (estimated scale)", "",
              "| image | label | photo type | est px/mm | status | peak_to_median | band_power_frac |", "|---|---|---|---|---|---|---|"]
    ros_res = []
    for r in ros:
        img = cf.load(os.path.join(web, r["file"]))
        if r["photo_type"] in MACRO_TYPES:
            ch = cf.ch_halftone_known_scale(img, float(r["est_px_per_mm"]))
        else:
            q, _ = cf.find_card(img, r["side"]); ch = cf.ch_halftone(img, q)
        v = ch.get("values", {})
        ros_res.append((r, ch))
        st = ch["status"] if ch["status"] == "ran" else f"could_not_run ({ch.get('reason_code')})"
        lines.append(f"| {r['image_id']} | {r['label']} | {r['photo_type']} | {r['est_px_per_mm']} | {st} | {v.get('peak_to_median', '')} | {v.get('band_power_frac', '')} |")
    ran = [(r, ch) for r, ch in ros_res if ch["status"] == "ran"]
    g = [ch["values"]["peak_to_median"] for r, ch in ran if r["label"] == "GENUINE"]
    f = [ch["values"]["peak_to_median"] for r, ch in ran if r["label"] == "FAKE"]
    lines += ["", f"Ran on {len(ran)}/{len(ros_res)}. Genuine n={len(g)}, fake n={len(f)}."]
    if len(g) >= 2 and len(f) >= 2:
        t = min(g)
        lines.append(f"AUC (fake reads LESS periodic) = {1 - auc(g, f):.2f}. Fakes below the lowest genuine ({t}): {W(sum(x < t for x in f), len(f))}.")
    open(os.path.join(out, "results.md"), "w").write("\n".join(lines) + "\n")
    json.dump({"denominators": den, "pairs": pair_res,
               "rosette": [{"id": r["image_id"], "label": r["label"], "ch": ch} for r, ch in ros_res]},
              open(os.path.join(out, "results.json"), "w"), indent=1, default=str)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
