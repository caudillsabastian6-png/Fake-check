"""Tests for set_fill_results.csv — run after set_fill.py. $0, local."""
import csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
res = list(csv.DictReader(open(os.path.join(HERE, "set_fill_results.csv"), encoding="utf-8")))
# Standalone fix (Oct 29, 2026): the pre-fill source dataset ships in
# this folder (labelled_dataset.csv — the Oct 28 dataset set_fill.py ran
# on; labelled_dataset_v3.csv in this pack is its post-fill state).
src = list(csv.DictReader(open(os.path.join(
    HERE, "labelled_dataset.csv"), encoding="utf-8")))

checks = []
def check(name, ok):
    checks.append((name, bool(ok)))
    print(("PASS" if ok else "FAIL"), name)

targets = [r for r in src if r["pool"] == "A" and r["label_status"] == "incomplete-set"]
check("one result row per target (118 = 103 A2 + 7 test + 8 reshoot)", len(res) == len(targets) == 118)
check("item_ids match targets exactly", {r["item_id"] for r in res} == {r["item_id"] for r in targets})
filled = [r for r in res if r["result"] == "SET_FILLED"]
check("every SET_FILLED row has set_id + set_name", all(r["filled_set_id"] and r["filled_set_name"] for r in filled))
check("no unfilled row carries a filled set", all(not r["filled_set_id"] for r in res if r["result"] != "SET_FILLED"))
check("every row has evidence text", all(r["evidence"] for r in res))
check("every filled row records symbol_check pending_visual", all(r["symbol_check"] == "pending_visual" for r in filled))
# known anchors
by_id = {r["item_id"]: r for r in res}
check("Rolycoly 078/163 fills Battle Styles (swsh5)",
      by_id["GEN-001"]["filled_set_id"] == "swsh5")
prof = [r for r in res if r["card_name"] == "Professor's Research"]
check("Professor's Research 178/202 fills Sword & Shield (swsh1) x2",
      len(prof) == 2 and all(r["filled_set_id"] == "swsh1" for r in prof))
fan = [r for r in res if "Fan Club" in r["card_name"]]
check("Pokemon Fan Club 133/156 fills Ultra Prism (sm5) — both copies",
      len(fan) == 2 and all(r["filled_set_id"] == "sm5" for r in fan))
fletch = [r for r in res if r["card_name"] in ("Fletchling", "Fletchinder")
          and r["printed_number"].endswith("/203")]
check("Fletchling/Fletchinder Evolving Skies rows are NOT filled (name/number conflict)",
      len(fletch) == 2 and all(r["result"] != "SET_FILLED" for r in fletch))
chill = [r for r in res if r["printed_number"].endswith("/198")]
check("all /198 rows fill Chilling Reign (swsh6)",
      len(chill) > 0 and all(r["filled_set_id"] == "swsh6" for r in chill))
sir = [r for r in res if "Sirfetch" in r["card_name"]]
check("Galarian Sirfetch'd V (JP) is NOT filled (JA detail row absent locally)",
      len(sir) == 1 and sir[0]["result"] != "SET_FILLED")

failed = [n for n, ok in checks if not ok]
print(f"\n{len(checks) - len(failed)}/{len(checks)} PASS")
sys.exit(1 if failed else 0)
