#!/usr/bin/env python3
"""eval_harness.py - locked-denominator evaluation of single-image measurements.

1. Reads OUT/manifest.json (from build_index.py), keeps one copy per sha256,
   keeps only rows with a STATED label (GENUINE/FAKE) and the requested side.
2. Writes the denominators to OUT/eval-denominators.json BEFORE measuring anything.
3. Measures each image with cardfeat, then for each numeric feature reports:
   AUC, and leave-one-out threshold classification (threshold fitted on n-1 at
   the genuine 95th/5th percentile, whichever direction the n-1 split favours),
   as catch x/n and false-flag x/n with 95% Wilson intervals (house standard).
4. Flags features that are CAPTURE descriptors: if they separate, the data set is
   confounded by how the photos were taken, not by what was printed.

Usage: python3 eval_harness.py INDEX_DIR OUT_DIR [--side front]
"""
import sys, os, json, math, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import cardfeat as cf

CAPTURE_FEATS = {"capture_profile.card_fill", "capture_profile.laplacian_var", "capture_profile.blown_share",
                 "capture_profile.px_per_mm", "capture_profile.width", "capture_profile.height", "capture_profile.edge_ring_texture"}


def wilson(x, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = x / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def auc(g, f):
    g, f = np.asarray(g), np.asarray(f)
    return float(((f[:, None] > g[None, :]).sum() + 0.5 * (f[:, None] == g[None, :]).sum()) / (len(g) * len(f)))


def loo(vals, labels):
    """labels 1=fake. Returns (catch_x, n_fake, ff_x, n_gen)."""
    vals, labels = np.asarray(vals, float), np.asarray(labels)
    cx = fx = 0
    for i in range(len(vals)):
        m = np.ones(len(vals), bool); m[i] = False
        g, f = vals[m & (labels == 0)], vals[m & (labels == 1)]
        if auc(g, f) >= 0.5:
            t = np.percentile(g, 95); pred = vals[i] > t
        else:
            t = np.percentile(g, 5); pred = vals[i] < t
        if labels[i] == 1 and pred: cx += 1
        if labels[i] == 0 and pred: fx += 1
    return cx, int((labels == 1).sum()), fx, int((labels == 0).sum())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("index"); ap.add_argument("out"); ap.add_argument("--side", default="front")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rows = json.load(open(os.path.join(a.index, "manifest.json")))
    seen, items = set(), []
    for r in rows:
        if r["sha256"] in seen or r["label"] not in ("GENUINE", "FAKE") or r["side"] != a.side:
            continue
        seen.add(r["sha256"]); items.append(r)
    den = {"side": a.side, "n_genuine": sum(r["label"] == "GENUINE" for r in items),
           "n_fake": sum(r["label"] == "FAKE" for r in items),
           "files": [r["canonical_copy"] for r in items], "locked_before_measurement": True}
    json.dump(den, open(os.path.join(a.out, "eval-denominators.json"), "w"), indent=1)

    labels, per = [], []
    for r in items:
        chans, canon = cf.measure(r["canonical_copy"], a.side)
        lab = cv_lab(canon)
        rec = {"file": r["canonical_copy"], "label": r["label"], "name": r["name"]}
        for ch in chans:
            if ch["status"] != "ran":
                rec[ch["channel"]] = f"could_not_run:{ch['reason_code']}"; continue
            for k, v in ch["values"].items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    rec[f"{ch['channel']}.{k}"] = v
        rec.update(lab)
        cen = next((c for c in chans if c["channel"] == "centering" and c["status"] == "ran"), None)
        if cen:
            l, rr = [float(x) for x in cen["values"]["left_right"].split("/")]
            rec["centering.lr_offcentre"] = abs(l - 50)
        per.append(rec); labels.append(1 if r["label"] == "FAKE" else 0)
    keys = sorted({k for p in per for k, v in p.items() if isinstance(v, (int, float))})
    res = []
    for k in keys:
        ok = [i for i, p in enumerate(per) if isinstance(p.get(k), (int, float))]
        v = [per[i][k] for i in ok]; L = [labels[i] for i in ok]
        g = [x for x, y in zip(v, L) if y == 0]; f = [x for x, y in zip(v, L) if y == 1]
        if len(g) < 3 or len(f) < 3:
            continue
        A = auc(g, f); cx, nf, fx, ng = loo(v, L)
        res.append({"feature": k, "is_capture_descriptor": k in CAPTURE_FEATS, "n_gen": ng, "n_fake": nf,
                    "auc_fake_higher": round(A, 3), "separation": round(max(A, 1 - A), 3),
                    "loo_catch": f"{cx}/{nf}", "loo_catch_wilson95": [round(x, 3) for x in wilson(cx, nf)],
                    "loo_falseflag": f"{fx}/{ng}", "loo_falseflag_wilson95": [round(x, 3) for x in wilson(fx, ng)],
                    "coverage": f"{len(ok)}/{len(per)}"})
    res.sort(key=lambda r: -r["separation"])
    json.dump({"denominators": den, "results": res, "per_image": per}, open(os.path.join(a.out, "eval-results.json"), "w"), indent=1)
    print(f"TINY SAMPLE - side={a.side}  genuine n={den['n_genuine']}  fake n={den['n_fake']}  (denominators locked first)")
    print(f"{'feature':<40}{'cap?':<6}{'sep':>6}  {'LOO catch':>10} {'[95% W]':>14}  {'LOO FF':>8} {'[95% W]':>14}  cov")
    for r in res:
        print(f"{r['feature']:<40}{'CAP' if r['is_capture_descriptor'] else '':<6}{r['separation']:>6}  {r['loo_catch']:>10} {str(r['loo_catch_wilson95']):>14}  {r['loo_falseflag']:>8} {str(r['loo_falseflag_wilson95']):>14}  {r['coverage']}")


def cv_lab(canon):
    import cv2
    lab = cv2.cvtColor(canon, cv2.COLOR_BGR2LAB).astype(np.float32)
    inner = lab[60:-60, 50:-50]
    return {"color.L_mean": round(float(inner[..., 0].mean() * 100 / 255), 2),
            "color.chroma_mean": round(float(np.sqrt((inner[..., 1] - 128) ** 2 + (inner[..., 2] - 128) ** 2).mean()), 2)}


if __name__ == "__main__":
    main()
