# Set Symbol Guide — built Oct 29, 2026 (owner order ~1:20 AM ET)

Owner's rule: "Make a guide and make sure the symbols match that guide before they say it's in that set."

## What this is
A reference guide of every Pokémon TCG set's identity marks, built from TCGdex's own set records (fetched live Oct 29, 2026):
- `set_symbol_guide.csv` / `.json` — 404 rows: EN 220 sets + JA 184 sets. Each row: language, set id/code (the acronym), set name, series, official printed total, total count, release date, symbol image URL, logo URL.
- `symbols/` — the actual symbol images downloaded from TCGdex assets: **159 of 169 unique symbol URLs on disk**.

## Coverage notes (honest gaps)
- 51 EN sets have NO symbol URL in TCGdex. Some never printed a symbol at all (Base Set era — identified by number + era, never by forcing a symbol). Others may have a symbol TCGdex doesn't host; those rows are marked NO_SYMBOL and a set claim for them needs a visual check against a verified card photo, not this guide alone.
- 10 symbol URLs returned 404 (listed in the build log): all ".5" special sets — me02.5, sv03.5, sv04.5, sv06.5, sv10.5b, sv10.5w, swsh10.5, swsh12.5, swsh3.5, swsh4.5. TCGdex names a symbol asset that isn't there. Fallback for those sets: crop the symbol from an owner-verified card photo of that set when one exists in the confirmed pool; until then, set claims for those 10 sets stay provisional.

## The gate (how this guide is used)
A set label counts ONLY when the set symbol visible at the bottom of the card's own front photo visually matches this guide's symbol image for the claimed set (recorded as symbol_check=match). Mismatch or unreadable symbol = set held (UNKNOWN-pending), never filled from catalogue name+number alone. All 271 set-fills from Oct 29, 2026 carry symbol_check=pending_visual and are PROVISIONAL until this gate passes them.
