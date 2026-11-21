#!/usr/bin/env python3
"""compare_cards.py - side-by-side photo measurements: a REFERENCE image vs a CANDIDATE.

Usage:
  python3 compare_cards.py REF.jpg CAND.jpg [--side front|back] [--json out.json] [--sheet out.png]

Prints a report. It never prints a verdict word: these are advisory measurements
for a human (or a validated lane) to read. Differences are flagged as
"look closer" only, and every flag says whether a capture difference could explain it.
"""
import argparse, json, sys, os
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import cardfeat as cf


def flat(ch):
    return {f"{ch['channel']}.{k}": v for k, v in ch.get("values", {}).items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref"); ap.add_argument("cand")
    ap.add_argument("--side", default="front", choices=["front", "back"])
    ap.add_argument("--json"); ap.add_argument("--sheet")
    a = ap.parse_args()
    R, rc = cf.measure(a.ref, a.side)
    C, cc = cf.measure(a.cand, a.side)
    hist = cf.ch_color_hist(rc, cc)
    rcap, ccap = R[0]["values"], C[0]["values"]
    notes = []
    same_domain, why = cf.capture_match(rcap, ccap)
    if not same_domain:
        notes.append("CAPTURE MISMATCH: reference and candidate were not captured the same way (" + "; ".join(why) + "). "
                     "Sharpness, colour and histogram differences below may be capture, not print.")
    print("=" * 78)
    print(f"REFERENCE : {a.ref}\nCANDIDATE : {a.cand}\nSIDE      : {a.side}")
    print("Advisory measurements only - not a verdict.")
    print("=" * 78)
    rows = []
    for r, c in zip(R, C):
        name = r["channel"]
        if r["status"] != "ran" or c["status"] != "ran":
            rs = r["status"] if r["status"] == "ran" else f"could_not_run ({r.get('reason_code')})"
            cs = c["status"] if c["status"] == "ran" else f"could_not_run ({c.get('reason_code')})"
            print(f"\n[{name}]\n  ref : {rs}\n  cand: {cs}")
            for x in (r, c):
                if x["status"] != "ran":
                    print(f"  why : {x.get('detail')}")
            rows.append({"channel": name, "ref": r, "cand": c, "compared": False})
            continue
        print(f"\n[{name}]")
        for k in r["values"]:
            rv, cv = r["values"][k], c["values"][k]
            line = f"  {k:<24} ref {str(rv):>16}   cand {str(cv):>16}"
            if isinstance(rv, (int, float)) and isinstance(cv, (int, float)) and rv:
                line += f"   ratio {cv / rv:6.2f}"
            print(line)
        rows.append({"channel": name, "ref": r, "cand": c, "compared": True})
    print(f"\n[{hist['channel']}]  bhattacharyya {hist['values']['bhattacharyya']}  (capture-match check, not a tell)")

    # simple look-closer flags (descriptive, unvalidated, no thresholds from the house)
    def v(lst, ch, key):
        for x in lst:
            if x["channel"] == ch and x["status"] == "ran":
                return x["values"].get(key)
    hp_r, hp_c = v(R, "halftone_periodicity", "peak_to_median"), v(C, "halftone_periodicity", "peak_to_median")
    if hp_r and hp_c and hp_c < 0.6 * hp_r:
        notes.append(f"Look closer: candidate's print screen is much less periodic ({hp_c} vs {hp_r}). "
                     "Offset print shows a regular screen; inkjet/laser often do not. Needs a macro photo to confirm.")
    if a.side == "back":
        sr, sc = v(R, "back_blue", "shade_spread_L"), v(C, "back_blue", "shade_spread_L")
        hr, hc = v(R, "back_blue", "hue_deg"), v(C, "back_blue", "hue_deg")
        if sr and sc and sc < 0.7 * sr:
            notes.append(f"Look closer: back blue has less shade variety (spread {sc} vs {sr}) - flat blue is a known fake trait.")
        if hr and hc and abs(hr - hc) > 12:
            notes.append(f"Look closer: back blue hue differs by {abs(hr-hc):.0f} deg (pale/purple backs are a known fake trait). "
                         + ("Capture differs, so white balance may explain it." if not same_domain else ""))
    te_r, te_c = v(R, "small_text_edges", "edge_p99_over_contrast"), v(C, "small_text_edges", "edge_p99_over_contrast")
    if te_r and te_c and te_c < 0.7 * te_r:
        notes.append(f"Look closer: small print is softer ({te_c} vs {te_r})." + (" Capture differs - may be focus." if not same_domain else ""))
    print("\nNOTES")
    for n in notes or ["No look-closer flags from these measurements (this is not a clean bill of health)."]:
        print(" - " + n)
    if a.sheet:
        h = 700; s = lambda im: cv2.resize(im, (int(im.shape[1] * h / im.shape[0]), h))
        cv2.imwrite(a.sheet, np.hstack([s(rc), np.full((h, 12, 3), 255, np.uint8), s(cc)]))
    if a.json:
        json.dump({"ref": a.ref, "cand": a.cand, "side": a.side, "channels": rows, "hist": hist,
                   "same_capture_domain": same_domain, "notes": notes, "verdict": None}, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
