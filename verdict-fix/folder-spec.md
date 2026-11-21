# Verdict data layout — one place to find "card X vs its reference"

Goal: anyone can answer "what do we compare this card to, and how was each photo taken?" in one lookup.
Rule: **never move originals.** The layout below is built from *pointers* (manifest rows) plus optional hard-link/copy views. Originals stay where they are; the manifest says where.

## 1. One manifest row per physical image file (the "one home per fact")
`manifest.csv` columns (build_index.py writes the first set today; the rest are to be filled by Latch/owner stamps):

| column | meaning | who sets it |
|---|---|---|
| image_id | `sha256` of the bytes (stable, dedupes copies) | script |
| path, canonical_copy, copies | where it lives; the first copy; how many byte-identical copies exist | script |
| card_key | `LANG-SETCODE-NUMBER-FINISH` e.g. `EN-DRI-016/182-REG` | identity read + owner |
| side | front / back / edge / macro / tilt / raking / light | capture app |
| capture_class | `scan600` / `scan300` / `phone_still` / `phone_macro` / `web_render` / `web_photo` | capture app or script |
| px_per_mm | measured on the card, not the file | script |
| label | GENUINE / FAKE / UNKNOWN (only from a stamping authority) | owner / Latch |
| label_source | file + line or stamp record | script / Latch |
| fake_class | STK / TXT / INK / LAS / CPX / MAN / unknown | owner |
| physical_copy_id | which physical card (two photos of one card share this) | owner (box number works) |
| registry_check | pass / hit / not_run | registry screen |
| exam_status | train / tune / sealed_exam / burned | Latch |

## 2. Pair key = card_key + side + capture_class
`comparison-index.csv` = for each candidate, its reference, chosen in this order:
1. same `card_key`, same side, same `capture_class`, label GENUINE (best: a true twin)
2. same `card_key`, same side, different capture (flag CAPTURE MISMATCH)
3. back side only: any GENUINE English back in the same capture_class (the back is one design since 1999)
4. none → the comparison channel answers `could_not_run: no_reference`

## 3. Optional browse view (hard links or copies, never moves)
```
by-card/<card_key>/
   genuine/<capture_class>/<side>__<image_id8>.jpg
   fake/<fake_class>/<capture_class>/<side>__<image_id8>.jpg
   unknown/...
   INDEX.md   <- generated: every photo of this card, its label source, and the compare command
```
`exam_status = sealed_exam` files are **never** placed in the browse view (keeps blind supply blind).

## 4. What exists on this machine today
Only the app/demo game images: 24 genuine fronts, 19 fake fronts (demo pool) + one genuine front/back pair and one fake front/back pair (demo samples) + 3 genuine/fake same-card web pairs (site assets, labelled only by filename). The real pools (pair library, bank-451, pair-sheet 800, labeled-fake lane, designated registry) live on Potion's machine; run `build_index.py` there.
