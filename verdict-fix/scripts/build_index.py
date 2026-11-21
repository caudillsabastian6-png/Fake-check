#!/usr/bin/env python3
"""build_index.py - NON-DESTRUCTIVE manifest + comparison index over card images.

Reads image folders, never moves/renames/deletes anything. Writes only:
  OUT/manifest.csv, OUT/manifest.json      one row per image file (path, sha256, size, label, provenance)
  OUT/duplicates.csv                       byte-identical files living in more than one place
  OUT/comparison-index.csv                 for every candidate: which reference(s) to compare it to, and why
  OUT/denominators.json                    counts per label/capture class, written BEFORE any evaluation

Labels come only from files that already state them (game-images.json, the app's
isReal list, the demo SAMPLES block). Nothing is inferred from pixels; an
image with no stated label is UNKNOWN. The designated-fakes registry is not on
this machine, so registry_check = "not_run".

Usage: python3 build_index.py OUT_DIR ROOT [ROOT ...]
"""
import sys, os, re, json, csv, hashlib
from PIL import Image

EXT = {".jpg", ".jpeg", ".png", ".webp"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stated_labels(root):
    """Collect labels stated in sibling data files. Returns {basename: dict}."""
    lab = {}
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs]
    parent = os.path.dirname(os.path.abspath(root))  # the app/demo page that names these images usually sits one level up
    files += [os.path.join(parent, f) for f in os.listdir(parent) if os.path.isfile(os.path.join(parent, f))]
    # pass 1: json, pass 2: html (the live page list wins over the older json list)
    files = sorted(files, key=lambda p: 0 if p.endswith(".json") else 1)
    for p in files:
            f = os.path.basename(p)
            if f == "game-images.json":
                try:
                    d = json.load(open(p))
                except Exception:
                    continue
                for e in d.get("rapidReal", []):
                    lab[e["img"]] = {"label": "GENUINE", "name": e.get("name"), "number": e.get("number"), "set": e.get("set"), "label_source": p}
                for e in d.get("rapidFake", []):
                    lab[e["img"]] = {"label": "FAKE", "name": e.get("name"), "note": e.get("note"), "label_source": p}
                for e in d.get("zoom", []):
                    lab.setdefault(e["img"], {"label": "UNKNOWN_STATED_ZOOM", "name": e.get("name"), "number": e.get("number"), "set": e.get("set"), "finish": e.get("kind"), "label_source": p})
            elif f in ("index.html",):
                try:
                    s = open(p, encoding="utf8", errors="ignore").read()
                except Exception:
                    continue
                for m in re.finditer(r'\{\s*name:"([^"]*)",\s*set:"([^"]*)",\s*img:"[^"]*/([^"/]+)",\s*isReal:(true|false)\s*\}', s):
                    name, st, img, real = m.groups()
                    lab[img] = {"label": "GENUINE" if real == "true" else "FAKE", "name": name, "set_or_note": st, "label_source": p}
                for m in re.finditer(r'id:"(genuine|fake)",[^}]*?front:"[^"]*/([^"/]+)",\s*back:"[^"]*/([^"/]+)",\s*read:\{name:"([^"]*)",\s*number:"([^"]*)",\s*set:"([^"]*)"', s):
                    kind, fr, bk, name, num, st = m.groups()
                    L = "GENUINE" if kind == "genuine" else "FAKE"
                    lab[fr] = {"label": L, "name": name, "number": num, "set": st, "side": "front", "pair": bk, "label_source": p}
                    lab[bk] = {"label": L, "name": name, "number": num, "set": st, "side": "back", "pair": fr, "label_source": p}
    return lab


def main():
    out, roots = sys.argv[1], sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    rows = []
    for root in roots:
        labels = stated_labels(root)
        for dp, _, fs in os.walk(root):
            for f in sorted(fs):
                if os.path.splitext(f)[1].lower() not in EXT:
                    continue
                p = os.path.join(dp, f)
                try:
                    w, h = Image.open(p).size
                except Exception:
                    continue
                if min(w, h) < 200:  # icons / UI art, not card photos
                    continue
                L = labels.get(f, {})
                ppm = round(((min(w, h) / 63.0) + (max(w, h) / 88.0)) / 2, 2)  # upper bound: assumes card fills frame
                rows.append({"path": p, "file": f, "root": root, "sha256": sha(p), "bytes": os.path.getsize(p),
                             "width": w, "height": h, "px_per_mm_max": ppm,
                             "capture_class_guess": "scan_or_hires" if ppm >= 15 else "photo_or_web_lowres",
                             "label": L.get("label", "UNKNOWN"), "name": L.get("name", ""),
                             "number": L.get("number", ""), "set": L.get("set", L.get("set_or_note", "")),
                             "note": L.get("note", ""), "side": L.get("side", "front" if "back" not in f else "back"),
                             "pair_file": L.get("pair", ""), "label_source": L.get("label_source", ""),
                             "registry_check": "not_run (registry not on this machine)",
                             "filename_hint": ("fake" if f.lower().startswith("fake") else "genuine" if f.lower().startswith("genuine") else "") if not L else "",
                             "domain_note": ""})
    # duplicates
    by = {}
    for r in rows:
        by.setdefault(r["sha256"], []).append(r)
    dups = [(k, len(v), " | ".join(x["path"] for x in v)) for k, v in by.items() if len(v) > 1]
    for r in rows:
        r["copies"] = len(by[r["sha256"]])
        r["canonical_copy"] = by[r["sha256"]][0]["path"]
    cols = list(rows[0].keys())
    with open(os.path.join(out, "manifest.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(rows)
    json.dump(rows, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    with open(os.path.join(out, "duplicates.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["sha256", "copies", "paths"]); w.writerows(dups)
    # comparison index: one canonical copy per sha
    uniq = [v[0] for v in by.values()]
    genu = [r for r in uniq if r["label"] == "GENUINE"]
    idx = []
    for c in uniq:
        if c["label"] not in ("FAKE", "UNKNOWN", "UNKNOWN_STATED_ZOOM", "GENUINE"):
            continue
        same_id = [g for g in genu if g is not c and c["name"] and g["name"] == c["name"] and g["side"] == c["side"]]
        if same_id:
            ref, why = same_id[0], "same identity, same side"
        elif c["side"] == "back":
            backs = sorted([g for g in genu if g["side"] == "back" and g is not c], key=lambda g: -g["px_per_mm_max"])
            ref, why = (backs[0], "English back is the same design on every card since 1999 - any verified genuine back is a valid reference") if backs else (None, "no genuine back reference on file")
        else:
            same_dom = sorted([g for g in genu if g is not c and g["capture_class_guess"] == c["capture_class_guess"]], key=lambda g: -g["px_per_mm_max"])
            ref, why = (same_dom[0], "NO same-identity reference - nearest same-capture genuine front, layout/print checks only") if same_dom else (None, "no genuine reference on file")
        idx.append({"candidate": c["canonical_copy"], "cand_label": c["label"], "cand_name": c["name"], "side": c["side"],
                    "reference": ref["canonical_copy"] if ref else "", "ref_name": ref["name"] if ref else "",
                    "pairing": why, "identity_matched": bool(same_id),
                    "same_capture_class": bool(ref and ref["capture_class_guess"] == c["capture_class_guess"])})
    with open(os.path.join(out, "comparison-index.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, list(idx[0].keys())); w.writeheader(); w.writerows(idx)
    den = {}
    for r in uniq:
        k = f"{r['label']}|{r['side']}|{r['capture_class_guess']}"
        den[k] = den.get(k, 0) + 1
    json.dump({"unique_images": len(uniq), "files_total": len(rows), "by_label_side_capture": den,
               "identity_matched_pairs": sum(i["identity_matched"] for i in idx)}, open(os.path.join(out, "denominators.json"), "w"), indent=1)
    print(f"files {len(rows)}  unique {len(uniq)}  duplicate groups {len(dups)}  index rows {len(idx)}")
    print(json.dumps(den, indent=1))


if __name__ == "__main__":
    main()
