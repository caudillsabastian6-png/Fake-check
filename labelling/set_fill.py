"""Set-fill for incomplete-set Pool A pairs — $0, local only, Oct 29, 2026.

Method (labelling guide, Oct 28): a set is filled ONLY from evidence on the
card itself + the local catalogue, never guessed:
  1. Owner-confirmed name + printed number (numerator/denominator). The
     denominator is the set's printed total, read off the card by the owner
     during the Oct 28 review — it is photo evidence, not a guess.
  2. Catalogue candidates = TCGdex EN/JA detail rows with the same
     (normalised) name and the same numerator.
  3. A candidate survives only if its set's official card count (TCGdex
     repo set files, cardCount.official) equals the printed denominator.
  4. Exactly one survivor -> SET FILLED (Potion authority, Oct 28 ~5:51 PM
     + ~6:43 PM delegation). The set-symbol visual second pass is still
     recorded as owed (symbol_check=pending_visual).
  5. Zero or multiple survivors -> set stays UNKNOWN, reason + candidates
     are listed. A name/number conflict with the catalogue (the printed
     number belongs to a different card in every candidate set) is flagged
     CONFLICT, never silently corrected.

Output: set_fill_results.csv (one row per input pair) in this folder.
The source labelled_dataset.csv is NOT modified.
"""
import csv, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
# Standalone fix (Oct 29, 2026): inputs resolve pack-relative first
# (source dataset + EN/JA detail CSVs ship in this pack), with the
# builder's workspace as fallback. The TCGdex repo clone (set totals)
# is upstream and 224 MB — it does NOT ship; without it main() SKIPs.
_PACK = os.path.normpath(os.path.join(HERE, ".."))
FAKE = os.path.normpath(os.path.join(HERE, "..", ".."))  # builder-workspace fallback root (fake-check/)
SRC = os.path.join(HERE, "labelled_dataset.csv")
if not os.path.exists(SRC):
    SRC = os.path.join(FAKE, "playground", "labelled-cards-2026-10-28", "labelled_dataset.csv")
EN = os.path.join(_PACK, "data", "tcgdex-details", "en-details.csv")
JA = os.path.join(_PACK, "data", "tcgdex-details", "ja-details.csv")
if not os.path.exists(EN):
    EN = os.path.join(FAKE, "sourcing", "tcgdex-details", "en-details.csv")
    JA = os.path.join(FAKE, "sourcing", "tcgdex-details", "ja-details.csv")
_REPO_CANDIDATES = [
    os.environ.get("TCGDEX_REPO") or "",
    os.path.join(HERE, "..", "..", "sourcing", "tcgdex-details", "repo"),
    os.path.join(HERE, "..", "..", "..", "..", "sourcing", "tcgdex-details", "repo"),
]
REPO = next((c for c in _REPO_CANDIDATES if c and os.path.isdir(c)),
            _REPO_CANDIDATES[1])
OUT = os.path.join(HERE, "set_fill_results.csv")


def norm_name(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("’", "'").replace("‘", "'").lower().strip()
    s = re.sub(r"\s*\(jp\)\s*$", "", s)
    return re.sub(r"\s+", " ", s)


def base_name(s):
    """Name without a trailing parenthetical, e.g. Professor's Research."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", norm_name(s)).strip()


def num_norm(s):
    s = str(s).strip()
    return s.lstrip("0") or "0" if s.isdigit() else s.lower()


def load_set_totals():
    totals = {}
    for sub in ("data", "data-asia"):
        for dp, _dirs, files in os.walk(os.path.join(REPO, sub)):
            for fn in files:
                if not fn.endswith(".ts"):
                    continue
                try:
                    txt = open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                mid = re.search(r'\bid:\s*"([^"]+)"', txt)
                mcc = re.search(r"cardCount:\s*\{[^}]*?official:\s*(\d+)", txt)
                if mid and mcc:
                    totals.setdefault(mid.group(1).lower(), int(mcc.group(1)))
    return totals


def load_details():
    rows = []
    for lang, path in (("en", EN), ("ja", JA)):
        with open(path, encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                r = dict(r)
                r["language"] = lang
                rows.append(r)
    return rows


def main():
    if not os.path.isdir(REPO):
        print("SKIPPED: set totals come from the TCGdex repo clone "
              "(cardCount.official in its .ts set files), which is upstream "
              "and not shipped in this pack. The generated output ships "
              "instead: set_fill_results.csv in this folder, verified by "
              "test_set_fill.py. Set $TCGDEX_REPO to a local clone to "
              "regenerate.")
        return
    totals = load_set_totals()
    details = load_details()
    by_name_num = {}
    by_set_num = {}
    for r in details:
        key = (norm_name(r["name"]), num_norm(r["localId"]))
        by_name_num.setdefault(key, []).append(r)
        by_set_num[(r["set_id"].lower(), num_norm(r["localId"]))] = r

    with open(SRC, encoding="utf-8") as f:
        dataset = list(csv.DictReader(f))
    pool_want = sys.argv[1] if len(sys.argv) > 1 else "A"
    out_path = sys.argv[2] if len(sys.argv) > 2 else OUT
    targets = [r for r in dataset if r["pool"] == pool_want and r["label_status"] == "incomplete-set"]
    print(f"targets (Pool {pool_want}, incomplete-set): {len(targets)}")

    out_rows = []
    counts = {}
    for r in targets:
        name, printed = r["card_name"], r["printed_number"]
        rec = {
            "item_id": r["item_id"], "v2_tier": r["v2_tier"], "card_name": name,
            "printed_number": printed, "front_file": r["front_file"],
            "back_file": r["back_file"], "filled_set_id": "", "filled_set_name": "",
            "result": "", "evidence": "", "candidates": "", "symbol_check": "",
        }
        m = re.fullmatch(r"\s*(\d+)\s*/\s*(\d+)\s*", printed or "")
        if not m:
            rec["result"] = "UNPARSED_NUMBER"
            rec["evidence"] = f"printed number {printed!r} is not numerator/denominator form; no fill attempted"
            out_rows.append(rec); counts[rec["result"]] = counts.get(rec["result"], 0) + 1
            continue
        numer, denom = num_norm(m.group(1)), int(m.group(2))
        cands = list(by_name_num.get((norm_name(name), numer), []))
        variant_note = ""
        if not cands:
            cands = [c for c in details
                     if base_name(c["name"]) == base_name(name) and num_norm(c["localId"]) == numer]
            if cands:
                variant_note = "name matched after dropping catalogue parenthetical suffix; "
        # denominator filter
        survivors, rejected = [], []
        for c in cands:
            total = totals.get(c["set_id"].lower())
            if total == denom:
                survivors.append(c)
            else:
                rejected.append(f"{c['id']} ({c['set_name']}, official={total})")
        cand_str = "; ".join(
            f"{c['id']} ({c['set_name']}, {c['language']}, official={totals.get(c['set_id'].lower())})"
            for c in cands)
        rec["candidates"] = cand_str
        if len(survivors) == 1:
            s = survivors[0]
            rec["result"] = "SET_FILLED"
            rec["filled_set_id"] = s["set_id"]
            rec["filled_set_name"] = s["set_name"]
            rec["evidence"] = (variant_note +
                f"name+number unique after printed-total filter: {s['id']} in {s['set_name']} "
                f"(official {denom} = printed denominator {denom}); rejected: "
                + ("; ".join(rejected) if rejected else "none"))
            rec["symbol_check"] = "pending_visual"
        elif len(survivors) > 1:
            rec["result"] = "AMBIGUOUS"
            rec["evidence"] = f"{len(survivors)} catalogue rows survive name+number+printed-total; set stays UNKNOWN"
        else:
            # conflict check: does the printed number in a denominator-sized
            # set belong to a different card?
            conflict = []
            for sid, total in totals.items():
                if total == denom and (sid, numer) in by_set_num:
                    other = by_set_num[(sid, numer)]
                    if norm_name(other["name"]) != norm_name(name) and base_name(other["name"]) != base_name(name):
                        conflict.append(f"{other['id']} is {other['name']} in {other['set_name']}")
            if cands:
                rec["result"] = "TOTAL_MISMATCH"
                rec["evidence"] = ("catalogue name+number rows exist but none has official total "
                                   f"{denom}; set stays UNKNOWN. Rejected: " + "; ".join(rejected))
            elif conflict:
                rec["result"] = "CONFLICT_NAME_VS_NUMBER"
                if "(jp)" in name.lower():
                    rec["evidence"] = ("card is marked (JP) in the owner review, so the EN rows at "
                                       "this number in total-100 sets do NOT apply. The local JA "
                                       "detail index has no row for this identity (the S4 set file "
                                       "lists official 100, but S4 cards are absent from ja-details), "
                                       "so the set cannot be confirmed locally. Set stays UNKNOWN — "
                                       "listed for owner/photo re-check, NOT corrected.")
                else:
                    rec["evidence"] = ("no catalogue row with this name+number; in a set of printed "
                                       f"total {denom} that number is: " + "; ".join(conflict[:3])
                                       + ". Name/number conflict — listed for owner/photo re-check, NOT corrected.")
            else:
                rec["result"] = "NO_CATALOGUE_MATCH"
                rec["evidence"] = ("no EN/JA catalogue row with this name+number and no "
                                   f"denominator-{denom} set row at that number in the local index; set stays UNKNOWN")
        out_rows.append(rec)
        counts[rec["result"]] = counts.get(rec["result"], 0) + 1

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader(); w.writerows(out_rows)
    print("counts:", counts)
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
