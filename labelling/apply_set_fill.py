"""Apply set_fill_results.csv to a COPY of labelled_dataset.csv.

Writes labelled_dataset_v2.csv in this folder. The original dataset is
never modified. A row moves to label_status=complete ONLY when its set was
filled AND its name + printed number were already present (they are, for
all Pool A targets). Filled set_code stores the TCGdex set_id; the set
name + evidence go in notes. Authenticity, pairing, condition are copied
unchanged — a set-fill is an identity completion, not a verdict.
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "labelled-cards-2026-10-28", "labelled_dataset.csv"))
RES = os.path.join(HERE, "set_fill_results.csv")
OUT = os.path.join(HERE, "labelled_dataset_v2.csv")

import sys
res_files = sys.argv[1:-1] if len(sys.argv) > 2 else [RES]
out_path = sys.argv[-1] if len(sys.argv) > 2 else OUT
fills = {}
for rf in res_files:
    for r in csv.DictReader(open(rf, encoding="utf-8")):
        if r["result"] == "SET_FILLED":
            fills[r["item_id"]] = r
rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
changed = 0
for r in rows:
    f = fills.get(r["item_id"])
    if not f:
        continue
    assert r["label_status"] == "incomplete-set" and not r["set_code"], r["item_id"]
    r["set_code"] = f["filled_set_id"]
    r["label_status"] = "complete"
    r["notes"] = (r["notes"] + f" | Set filled Oct 29, 2026 (AI loop keeper, Potion authority Oct 28): "
                   f"{f['filled_set_name']} ({f['filled_set_id']}) — {f['evidence']} "
                   f"Set-symbol visual second pass still owed.").strip()
    changed += 1

fields = list(rows[0].keys())
with open(out_path, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader(); w.writerows(rows)
print(f"rows {len(rows)}, set-filled applied {changed}, wrote {out_path}")
