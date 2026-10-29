"""TCGdex EN/JA identity lookup — wired into the V2 checker/demo Oct 27, 2026.

$0, local files only, no API calls, no network, no spend, no images loaded.
Source: ~/workspace/fake-check/sourcing/tcgdex-details/en-details.json
        (23,771 rows) and ja-details.json (13,598 rows), built Oct 27, 2026.
Total searchable identities: 37,369 rows (EN 23,771 + JA 13,598).

This module does NOT change any checker verdict and a lookup hit is NOT
authentication. It only answers: "Does this set + printed number exist,
and what card is it?" The checker still decides Genuine / Counterfeit /
Inconclusive from tells, and a Likely verdict still needs a reference
image for that exact identity plus the verification gate. Most indexed
identities have NO reference image in the playground (only 2 canned
references exist), so a lookup hit without a reference stays
Inconclusive — it never becomes Genuine on lookup alone.

Lookup order (never guess):
  1. Set + printed number first. Printed number beats name/rarity.
     Set query matches set_id exactly (case-insensitive) or is a
     substring of set_name (case-insensitive). Numbers are normalised
     (leading zeros stripped: "016" == "16"), because EN prints "16"
     and JA prints "016" for the same slot.
  2. Name + number as fallback search only. If set+number finds
     nothing, name+number candidates are returned for the user to pick
     the correct set from — the checker never auto-picks one of them.
  3. Name substring search (search_by_name) is a finding aid only.

Ambiguity is a stop, not a guess: the same set_id+number exists in
both EN and JA for 1,254 keys (e.g. neo1-1 is Ampharos in EN and a
different card in JA). If set+number matches more than one distinct
card name, the result is needs_input listing the candidates, and the
caller must ask for language/name — never pick the first row.
Same-name multi-set is the same stop (fixed Oct 28, 2026): a loose
set hint such as "Base" matches Alakazam #1 in Base Set, Base Set 2
and Expedition Base Set — same name, three different identities.
If set+number matches more than one distinct row id, the result is
needs_input listing the sets, and the caller must ask for the exact
set (set_id or exact set_name) — never pick the first row.
"""

import json
import os

_BASE = os.path.dirname(os.path.abspath(__file__))
# Standalone fix (Oct 29, 2026): prefer the pack's own data folder
# (data/tcgdex-details at the pack root); fall back to the playground
# sourcing folder when running inside the builder's workspace.
_PACK_DETAILS_DIR = os.path.normpath(
    os.path.join(_BASE, "..", "data", "tcgdex-details"))
_DETAILS_DIR = _PACK_DETAILS_DIR if os.path.isdir(_PACK_DETAILS_DIR) else \
    os.path.normpath(
        os.path.join(_BASE, "..", "..", "sourcing", "tcgdex-details"))

_cache = None


def _load():
    global _cache
    if _cache is not None:
        return _cache
    rows = []
    for lang, path in (
        ("en", os.path.join(_DETAILS_DIR, "en-details.json")),
        ("ja", os.path.join(_DETAILS_DIR, "ja-details.json")),
    ):
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for row in json.load(f):
                row = dict(row)
                row["language"] = lang
                rows.append(row)
    _cache = rows
    return rows


def counts():
    rows = _load()
    return {"en": sum(1 for r in rows if r["language"] == "en"),
            "ja": sum(1 for r in rows if r["language"] == "ja"),
            "total": len(rows)}


def norm_number(local_id):
    """'016' -> '16', '1' -> '1', '' -> ''."""
    s = str(local_id).strip()
    if not s:
        return ""
    digits = s.lstrip("0")
    return digits if digits else "0"


def _set_matches(row, set_query):
    if not set_query:
        return True
    q = str(set_query).strip().lower()
    if not q:
        return True
    return (q == str(row.get("set_id", "")).strip().lower()
            or q in str(row.get("set_name", "")).strip().lower())


def _language_matches(row, language):
    if not language or str(language).strip().lower() in ("all", ""):
        return True
    return row["language"] == str(language).strip().lower()


def lookup_by_set_number(set_query, local_id, language=None):
    """Step 1: set + printed number. Returns dict with:
    matches (rows), distinct_names, set_known, number_known_in_set,
    ambiguous (True if >1 distinct name), needs_input (list of strings).
    """
    if not set_query or not local_id:
        return {"matches": [], "distinct_names": [], "set_known": False,
                "number_known_in_set": False, "ambiguous": False,
                "needs_input": ["identity_lookup: supply both a set and a printed card number"]}
    num = norm_number(local_id)
    # Exact set_id / exact set_name beats substring: "Base Set" must not
    # also match "Base Set 2". Substring is only a fallback when no
    # exact set exists (e.g. a user typing "Base" is ambiguous, and
    # correctly returns needs_input, not a first-row pick).
    q = str(set_query).strip().lower()
    all_rows = [r for r in _load() if _language_matches(r, language)]
    exact_rows = [r for r in all_rows
                  if q == str(r.get("set_id", "")).strip().lower()
                  or q == str(r.get("set_name", "")).strip().lower()]
    set_rows = exact_rows if exact_rows else [
        r for r in all_rows if _set_matches(r, set_query)]
    set_known = bool(set_rows)
    matches = [r for r in set_rows if norm_number(r.get("localId", "")) == num]
    names = sorted({r["name"] for r in matches})
    # Distinct identities, not just distinct names: the same name in
    # two sets (e.g. Alakazam #1 in Base Set vs Base Set 2) is still
    # two identities, and picking the first row would be a guess.
    distinct_ids = sorted({str(r.get("id", "")) for r in matches if r.get("id")})
    ambiguous = len(names) > 1 or len(distinct_ids) > 1
    needs = []
    if not set_known:
        needs.append(f"identity_lookup: no set found for '{set_query}' in the EN/JA index — "
                     "check the printed set, or search by card name to find the set")
    elif not matches:
        needs.append(f"identity_lookup: no card found for set '{set_query}' number '{local_id}' "
                     "in the EN/JA index — check the printed set and number; nothing was guessed")
    elif ambiguous:
        cands = "; ".join(f"{r['name']} ({r.get('id', '?')}, {r['language']}, {r['set_name']})" for r in matches[:10])
        needs.append(f"identity_lookup: set '{set_query}' number '{local_id}' matches more than one card "
                     f"({cands}) — supply the exact set (set_id or exact set_name, e.g. base1) "
                     f"and/or a language; nothing was picked")
    return {"matches": matches, "distinct_names": names, "distinct_ids": distinct_ids,
            "set_known": set_known,
            "number_known_in_set": bool(matches), "ambiguous": ambiguous,
            "needs_input": needs}


def lookup(name, local_id, set_hint=None):
    """Legacy name+number lookup, kept compatible. Numbers normalised.

    `matches` = name + localId match, and set_hint matches (or no hint).
    """
    if not name or not local_id:
        return {"matches": [], "set_mismatch_candidates": []}
    name_norm = str(name).strip().lower()
    num = norm_number(local_id)
    hint = str(set_hint).strip().lower() if set_hint else ""
    matches, mismatches = [], []
    for row in _load():
        if str(row.get("name", "")).strip().lower() != name_norm:
            continue
        if norm_number(row.get("localId", "")) != num:
            continue
        if not hint:
            matches.append(row)
            continue
        if hint == str(row.get("set_id", "")).strip().lower() or (
            hint in str(row.get("set_name", "")).strip().lower()
        ):
            matches.append(row)
        else:
            mismatches.append(row)
    return {"matches": matches, "set_mismatch_candidates": mismatches}


def search_by_name(name, language=None, limit=50):
    """Step 2/3 fallback: substring name search, finding aid only.
    Returns rows (capped), never a single resolved identity."""
    if not name or not str(name).strip():
        return []
    q = str(name).strip().lower()
    out = []
    for row in _load():
        if not _language_matches(row, language):
            continue
        if q in str(row.get("name", "")).strip().lower():
            out.append(row)
    out.sort(key=lambda r: (r["set_id"], norm_number(r.get("localId", "")).zfill(4)))
    return out[:limit]


def resolve(set_query=None, local_id=None, name=None, language=None):
    """Full resolution for the checker, in order, never guessing.

    Returns {"status": "resolved"|"needs_input", "row": row|None,
    "method": "set_number"|"name_number"|None, "matches": [...],
    "name_candidates": [...], "needs_input": [...]}.
    - resolved: exactly one distinct row for set+number (one id,
      so same-name multi-set matches do NOT resolve).
    - needs_input: not found, or ambiguous — with candidates if a
      name+number search found rows for the user to pick from.
    """
    if set_query and local_id:
        r = lookup_by_set_number(set_query, local_id, language)
        if r["matches"] and not r["ambiguous"]:
            return {"status": "resolved", "row": r["matches"][0], "method": "set_number",
                    "matches": r["matches"], "name_candidates": [], "needs_input": []}
        needs = list(r["needs_input"])
        cands = []
        if name and local_id:
            # Fallback search only: show name+number rows so the user
            # can pick the correct set; do NOT auto-resolve from them.
            by_name = lookup(name, local_id)
            cands = by_name["matches"] + by_name["set_mismatch_candidates"]
            if cands:
                needs.append("identity_lookup: name+number candidates found — pick the correct set "
                             "and re-run with that set + printed number")
        return {"status": "needs_input", "row": None, "method": None,
                "matches": r["matches"], "name_candidates": cands[:10], "needs_input": needs}
    if name and local_id:
        # Name+number without a set: only resolves if it is unambiguous
        # across the whole index (rare); otherwise it is a candidate list.
        by_name = lookup(name, local_id)
        names = sorted({r["name"] for r in by_name["matches"]})
        if len(by_name["matches"]) == 1:
            return {"status": "resolved", "row": by_name["matches"][0], "method": "name_number",
                    "matches": by_name["matches"], "name_candidates": [], "needs_input": []}
        return {"status": "needs_input", "row": None, "method": None,
                "matches": by_name["matches"], "name_candidates": by_name["matches"][:10],
                "needs_input": [f"identity_lookup: name '{name}' number '{local_id}' is not enough on its own — "
                                "supply the set + printed number; candidates are listed, nothing was picked"]}
    return {"status": "needs_input", "row": None, "method": None, "matches": [],
            "name_candidates": [],
            "needs_input": ["identity_lookup: supply a set + printed card number, or a card name + number"]}


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3 and sys.argv[1] != "--name":
        result = lookup_by_set_number(sys.argv[1], sys.argv[2],
                                      sys.argv[3] if len(sys.argv) > 3 else None)
        print(f"matches={len(result['matches'])} set_known={result['set_known']} "
              f"ambiguous={result['ambiguous']} needs_input={result['needs_input']}")
        for row in result["matches"][:10]:
            print(row)
    elif len(sys.argv) >= 3:
        result = lookup(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
        print(f"matches={len(result['matches'])} "
              f"set_mismatch_candidates={len(result['set_mismatch_candidates'])}")
        for row in result["matches"][:10]:
            print(row)
    else:
        print("usage: identity_lookup.py <set> <number> [language]  OR  identity_lookup.py --name <name> <number>")
        raise SystemExit(2)
