# TCGdex EN + JA detail index — SUMMARY

Built 2026-10-27 from the already-cloned repo only. $0, no API calls, no network,
no spending, repo files not moved or edited. Card `.ts` files were parsed with
regex/text parsing only — never executed.

Source: `~/workspace/fake-check/sourcing/tcgdex-details/repo/`
- EN: `repo/data/<Serie>/<Set>/<LocalId>.ts`
- JA: `repo/data-asia/<Serie>/<Set>/<LocalId>.ts`
- Set id/name: the matching `repo/data/<Serie>/<Set>.ts` /
  `repo/data-asia/<Serie>/<Set>.ts` file. If a set id could not be parsed it
  would be left blank and the folder name used as set_name — in this run every
  output row has a set_id, so no id was invented and none was left blank.

## Counts (reconciled to files on disk)

| Language | Card files scanned | Rows in output | Skipped | Set files mapped | JSON rows | CSV data rows |
|---|---|---|---|---|---|---|
| EN | 23,873 | 23,771 | 102 | 223 | 23,771 | 23,771 |
| JA | 18,522 | 13,598 | 4,924 | 346 | 13,598 | 13,598 |
| Total | 42,395 | 37,369 | 5,026 | 569 | 37,369 | 37,369 |

Duplicate `id` values: 0 in both languages. CSV row counts match JSON row counts.

## Files produced

- `~/workspace/fake-check/sourcing/tcgdex-details/en-details.json` (5.6 MB)
- `~/workspace/fake-check/sourcing/tcgdex-details/en-details.csv` (1.9 MB)
- `~/workspace/fake-check/sourcing/tcgdex-details/ja-details.json` (3.4 MB)
- `~/workspace/fake-check/sourcing/tcgdex-details/ja-details.csv` (1.3 MB)

Fields (JSON and CSV alike): `id` (set_id-localId), `set_id`, `set_name`,
`localId`, `name`, `rarity`, `category`, `hp`, `types` (JSON list; CSV joined
with `;`), `illustrator`. Empty `hp` in CSV = no hp in source.

## Skipped files — reason

Language matching is strict: a card is EN only if its source has an `en` name,
JA only if it has a `ja` name. No other language's name was ever filed under
EN or JA.

- EN skipped, 102: all fr-only cards, e.g. `data/McDonald's Collection/
  Collection McDonald's 2013/1.ts` (name langs: fr). They have no `en` name.
- JA skipped, 4,924, by name languages present in the source:
  - zh-tw only: 3,090
  - id only: 834
  - id+th: 704
  - th only: 57
  - th+zh-tw: 70
  - id+th+zh-tw: 121
  - zh-cn: 48

Important finding: `data-asia/` is NOT Japanese-only. It also holds zh-tw, ko,
th, id and zh-cn cards. Those 4,924 non-JA Asian cards are excluded from
`ja-details.*`, not filed as Japanese. They could be indexed separately later
if a zh-tw / th / id / ko index is wanted — that was outside this task.

## Parsing gaps (in the output rows, not in the source index)

These are fields absent (or empty) in the source card files themselves —
Trainer/Energy cards legitimately have no hp/types, for example. They are not
parser failures; the row is still present with that field empty.

| Gap | EN (of 23,771) | JA (of 13,598) |
|---|---|---|
| missing hp | 3,547 | 2,725 |
| missing types | 3,538 | 2,729 |
| missing illustrator (absent or `""` in source) | 720 | 2,265 |
| missing rarity (field absent) | 0 | 810 |
| missing category | 0 | 0 |
| missing set_id | 0 | 0 |

Note on rarity: a further 591 EN rows and 2,260 JA rows carry the literal
source value `rarity: "None"` — that is the source's own value, preserved
as-is, not a missing field.

## Sample entries verified against source .ts files

EN — `base4-1` in `en-details.json`:
`{"id": "base4-1", "set_id": "base4", "set_name": "Base Set 2", "localId": "1",
"name": "Alakazam", "rarity": "Rare", "category": "Pokemon", "hp": 80,
"types": ["Psychic"], "illustrator": "Ken Sugimori"}`
Source `repo/data/Base/Base Set 2/1.ts` shows exactly: name en "Alakazam",
illustrator "Ken Sugimori", rarity "Rare", category "Pokemon", hp 80,
types ["Psychic"]; set file `repo/data/Base/Base Set 2.ts` gives id "base4"
and name en "Base Set 2". Match on every field.

JA — `BW8a-001` in `ja-details.json`:
`{"id": "BW8a-001", "set_id": "BW8a", "set_name": "ラセンフォース",
"localId": "001", "name": "タマタマ", "rarity": "Common", "category": "Pokemon",
"hp": 30, "types": ["Grass"], "illustrator": "Shigenori Negishi"}`
Source `repo/data-asia/BW/BW8a/001.ts` shows exactly: name ja "タマタマ",
illustrator "Shigenori Negishi", rarity "Common", category "Pokemon", hp 30,
types ["Grass"]; set file `repo/data-asia/BW/BW8a.ts` gives id "BW8a" and
name ja "ラセンフォース". Match on every field.

## What was NOT done

- No network or TCGdex API calls of any kind.
- No touching of `~/workspace/fake-check/sourcing/ja-tcgdex-rest/` or its
  running slow detail-check.
- No deploy, publish, or message to anyone. This is a background index only.
- No repo files edited, moved, or committed.
