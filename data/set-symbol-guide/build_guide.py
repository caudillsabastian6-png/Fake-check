import json, urllib.request, csv, os, sys

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"CardCauldronSetSymbolGuide/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

rows = []
for lang in ["en","ja"]:
    try:
        sets = fetch(f"https://api.tcgdex.net/v2/{lang}/sets")
    except Exception as e:
        print(f"{lang} sets fetch FAILED: {e}"); sys.exit(1)
    print(f"{lang}: {len(sets)} sets")
    for s in sets:
        rows.append({
            "lang": lang,
            "set_id": s.get("id",""),
            "set_name": s.get("name",""),
            "serie_id": (s.get("serie") or {}).get("id","") if isinstance(s.get("serie"), dict) else "",
            "official_count": (s.get("cardCount") or {}).get("official",""),
            "total_count": (s.get("cardCount") or {}).get("total",""),
            "symbol_url": s.get("symbol","") or "",
            "logo_url": s.get("logo","") or "",
            "symbol_on_card": "yes" if s.get("symbol") else "NO_SYMBOL (e.g. Base Set era: identify by number/era, never force a symbol)",
            "release_date": s.get("releaseDate","") or "",
        })

with open("set_symbol_guide.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

en = [r for r in rows if r["lang"]=="en"]; ja = [r for r in rows if r["lang"]=="ja"]
nosym_en = [r for r in en if not r["symbol_url"]]
print(f"TOTAL rows: {len(rows)} (EN {len(en)}, JA {len(ja)}); EN sets without symbol: {len(nosym_en)}")
json.dump(rows, open("set_symbol_guide.json","w"), indent=1)
