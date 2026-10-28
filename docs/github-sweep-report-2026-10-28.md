# GitHub sweep for Real or Replica — research and evaluation ONLY

Date: Oct 28, 2026. Swept by subagent, at the owner's Oct 28 order to look on GitHub
for anything the app may need: backend, data, machine learning, centering, fake
tells, card identification, image matching, grading.

**What this report is NOT:** it is not an approval, not a licence ruling, not a
test result on the owner's cards, and not a shipment. No repo code was copied
into the live demo, into old-plus, or into any other workspace file. No
training ran, no GPU ran, no money was spent, no verdict, threshold, or grade
was taken from any repo below. Every repo still needs a real test on the
owner's own hand-photo pairs, plus a licence check, before anyone talks about
using it.

**Headline finding, plain words:** GitHub has good pieces for the *steps*
around a check — flatten a photo, measure centering, find which card a photo
looks like, read the printed text, compare two photos by hash — but it does
**not** have a ready-made, open-source "is this Pokémon card fake?" checker.
No repo found in this sweep does font + print-dot rosette + back colour +
spelling/name checks as a tested fake-tell engine. That part stays ours:
our own tells engine, checked against our own verified pairs, with
Inconclusive when the evidence is not enough. Do not let a repo's marketing
("AI grading", "instant check") turn into a product claim for Real or Replica.

## Summary table

| Repo | What it does, in one line | Licence found | Fit for Real or Replica? | $0 test on owner pairs? |
|---|---|---|---|---|
| owengenge/Skewtle | Flatten an angled card photo in the browser, by dragging 4 corner handles | MIT (repo page) | YES, as a manual flatten step before centering | YES — flatten an angled owner front, then measure |
| ElitePete/card-centering-studio | Measure centering (left/right, top/bottom) from scans, with manual guides | MIT (repo page) | YES, for the centering math + measurement habit only | YES — use its formula on flattened owner fronts/backs |
| HanClinto/CollectorVision | Find a card's identity from a photo: corner detect, dewarp, 128-d embedding, nearest-neighbour search | AGPL-3.0 (repo page), commercial licence also offered | TEST FIRST — the closest thing to our missing image-to-identity matcher, but Pokémon is experimental and AGPL needs a licence decision before any use in the app | YES — CPU test on A1 pairs (see §3) |
| JohannesBuchner/imagehash | aHash / dHash / pHash / wHash / colour hash for "do these two photos look nearly identical?" | BSD-2-Clause, per DeepWiki + Guix secondary sources — licence file NOT directly read in this sweep, verify before use | YES, as a hash library only — it already matches the Oct 28 matcher idea, it is not a card identifier and not a fake detector | YES — already the same family as the Oct 28 matcher prototype; re-run on cropped owner pairs |
| tesseract-ocr/tesseract | Read printed text out of a photo (OCR) | Apache 2.0 (project docs) | YES, as a text reader only — read name + printed number, then check them against the set list ourselves | YES — OCR 10 owner fronts, count exact name/number reads |
| JaidedAI/EasyOCR | Read text out of photos with a PyTorch model, 80+ languages | Apache 2.0 (setup.py / package pages) | MAYBE, later — heavier than Tesseract (PyTorch), and not needed until Tesseract is proven too weak on card fonts | YES on CPU, but only after the Tesseract test |
| tcgdex/cards-database | Pokémon TCG card database behind the TCGdex API (data the app already uses) | UNKNOWN from this sweep — do not claim a licence | DATA ONLY, already in use as identity data — not new code, and its card images are Pokémon Company art, not ours to re-claim | N/A — already the source of the 37,369 identities |
| tcgdex/python-sdk | Python wrapper for the TCGdex API | UNKNOWN from this sweep | LOW — an API wrapper, not a checker; only useful if a future backend wants TCGdex over HTTP | NO new test needed |
| tradingcarddex/Pokemon-Card-CSV | Pokémon card data as CSV | UNKNOWN from this sweep; README snippet requires attribution to TradingCardDex.com | LOW — duplicate of identity data we already have, attribution strings attached | NO — do not add a second identity source without a reason |
| pokepc/dataset | Pokémon species / game data (Pokédex, moves, games), static JSON | MIT (repo page) | NO for card checking — this is species data, not card set/number data | NO |
| 1vcian/Pokemon-TCGP-Card-Scanner | TCG *Pocket* screenshot scanner: YOLO11 Nano oriented boxes + RGB perceptual hash, in the browser | UNKNOWN — only DeepWiki pages were returned, licence file not read | PATTERN ONLY — Pocket screenshots are not physical cards; the YOLO-box + pHash pattern is the interesting part, not the app | NO direct test on physical pairs; pattern may inform a future detector test |
| dsouza95/pokemon-tcg-companion | "AI-powered Pokémon TCG companion — upload a card image to look up its info" (API description only) | UNKNOWN — only a GitHub API snippet was returned, repo README not verified | UNVERIFIED — do not rely on it until its README, licence, and method are actually read | NO — not until verified |
| (gap) Fake-tell engine | — | — | NONE FOUND | — |
| (gap) Penguin-stdlib leaderboard / referral / auth example | — | — | NONE VERIFIED — the live Penguin backend already does leaderboard + referral; do not import a generic auth tutorial | — |

## 1. owengenge/Skewtle — flatten angled photos

- Source: https://github.com/owengenge/Skewtle
- What it actually does, in plain words: a browser tool. Upload a card photo
  taken at an angle, drag four corner handles onto the card's corners, and it
  applies a perspective transform and gives back a flat, correctly proportioned
  (default 5:7) crop. No upload to a third-party service, no desktop software.
- Licence: **MIT** — shown on the repo page ("License: MIT License (MIT)"),
  and the README ends with "License: MIT".
- Fit: the owner's angled hand photos are the exact problem this solves.
  Flatten first, *then* measure centering. Without flattening, an angled
  photo makes borders look uneven even when they are not.
- What it does NOT do: it does not find the corners by itself (the user drags
  them), it does not measure centering, it does not grade, it does not check
  real vs fake, and it does not work well on warped/bent cards or on photos
  where the card fills only a small part of the frame. The repo says this
  itself.
- $0 test that would prove it: take 5 angled owner fronts (Manectric and
  Diglett first, since their owner notes differ), flatten each by hand in the
  tool, then measure left/right and top/bottom on the flattened crop. Pass
  = the flattened crop looks square and the measured ratios are stable when
  the corners are re-placed a second time. Fail = ratios swing wildly with
  small corner moves — then flattening is not reliable enough to trust.
- Red flag: none on licence or method. Small project (3 stars, 49 commits,
  created Jun 2026, React + TypeScript + Konva). It is a *manual* step, not
  an automatic pipeline — anyone who sells it as "automatic centering" is
  overstating it.

## 2. ElitePete/card-centering-studio — centering measurement

- Source: https://github.com/ElitePete/card-centering-studio
- What it actually does, in plain words: a Windows desktop app (Python,
  PySide6, OpenCV, Pillow, SQLite) for repeatable centering measurements from
  flatbed scans. Import a front scan and a back scan, place 8 guides per side
  (4 outer card edges, 4 inner printed-image edges), and it reports
  left/right and top/bottom ratios to one decimal place, e.g. 49.2/50.8,
  with plain-English severity bands and a saved PNG report.
- Licence: **MIT** — shown on the repo page, and the README says "Card
  Centering Studio is released under the MIT License. Copyright © 2026
  Lambda Core Engineering LLC."
- Fit: this is the centering *math* and the measurement habit to copy as a
  method, not necessarily the app itself. Its formula is simple pixel
  arithmetic: left = inner_left − outer_left, right = outer_right −
  inner_right, and so on; horizontal = 100 × left/(left+right).
- What it does NOT do: V1 has **no automatic edge detector** — the README
  says "No automatic detector is implemented in V1" and a future detector
  could implement a reserved `CardEdgeDetector` protocol. It also
  deliberately "does not predict grades or make grading-company claims" and
  its severity bands "are not grading predictions". It is scan-first
  (Windows, PNG scans), not phone-photo-first, and not Penguin-stdlib
  (it needs PySide6/OpenCV, which Penguin does not have).
- $0 test that would prove it: use only its formula (not the whole app) on
  the Skewtle-flattened owner fronts/backs, and compare the ratios against
  the owner's own in-hand centering notes (e.g. Cottonee "off-centered",
  Bisharp "off-center", Dialga "off-center"). Pass = the measured ratios
  move in the same direction as the owner's notes. Fail = they do not, and
  the formula is not the problem — the flattening or the guide placement is.
- Red flag: very new and tiny (0 stars, 5 commits, created Oct 15, 2026).
  Treat it as a formula + workflow reference, not as a battle-tested tool.
  Never present its severity bands as PSA/CGC grades.

## 3. HanClinto/CollectorVision — card identification from a photo

- Source: https://github.com/HanClinto/CollectorVision
- What it actually does, in plain words: feed it a photo of a card, it finds
  the four corners, dewarps the card to a standard crop, turns that crop into
  a short 128-number fingerprint (embedding), and searches a catalog of
  reference fingerprints for the nearest match. The full pipeline is claimed
  to run in under 100 ms on a laptop CPU. It can also build a custom catalog
  from your own images: put reference images in a folder, name each file with
  the ID you want back, and it builds a searchable catalog file from them.
- Licence: **AGPL-3.0** — shown on the repo page, and the README says
  "AGPL-3.0. Commercial licenses available". This is the one licence in this
  sweep that needs a real decision before any use *inside* the app: AGPL
  is a strong copyleft licence, very different from MIT/Apache. Testing it
  and reading it is fine; shipping it inside Real or Replica without a
  licence decision is not.
- Fit: this is the closest thing found to the app's missing piece — an
  image-to-identity matcher. It directly answers "which card is in this
  photo?" without the user typing the set and number first. It is also the
  only repo here whose method (corner detect + dewarp + embedding +
  nearest neighbour) is a step beyond plain hashing.
- What it does NOT do: it does **not** check real vs fake, it does not
  grade, and its Pokémon catalog is explicitly experimental. The README
  says Magic: The Gathering is the primary supported catalog and "the
  others are previews", and an earlier search snippet says non-MTG catalogs
  are "highly experimental and need user feedback from real-world scans".
  Its Pokémon catalog returns TCGplayer product IDs, not the set + printed
  number the app uses, so a mapping step would still be needed. It is also
  sensitive to 180-degree rotation (the repo gives a rotation-invariant
  workaround: embed upright and rotated, keep the stronger result).
  It needs Python 3.10+ and ONNX Runtime — not Penguin stdlib, so it would
  run on the Muse VM / G1, not on Penguin as-is.
- $0 test that would prove it: (a) run its Pokémon catalog on 10 owner A1
  fronts and record top-1 and top-5 hit rate against the known identity;
  (b) separately, build a *custom* catalog from owner A1 fronts only and
  test held-out re-photographs of the same cards against it. Pass = top-1
  is right most of the time *and* a wrong-identity card is not confidently
  matched to a different identity. Fail on either = it is not a matcher
  for this app yet, however good it is on Magic cards.
- Red flag: AGPL (see above), Pokémon experimental, TCGplayer-ID mapping
  gap, rotation sensitivity, and a catalog built from TCGplayer reference
  images — those reference images are not the owner's, and their licence
  for re-use inside a product is a separate question from the code licence.
  Do not ship the catalog as if it were the app's own verified pool.

## 4. JohannesBuchner/imagehash — perceptual hashing library

- Source: https://github.com/JohannesBuchner/imagehash
  (URL surfaced in the PyPI / DeepWiki / Guix pages returned by search; the
  PyPI page states "Source hosted at GitHub" with this URL.)
- What it actually does, in plain words: a small Python library that turns a
  photo into a short hash that stays similar when the photo is slightly
  changed — average hash, perceptual hash, difference hash, wavelet hash,
  colour hash, and a crop-resistant hash. Two hashes can then be compared by
  Hamming distance: small distance = photos look nearly identical.
- Licence: **BSD-2-Clause, per secondary sources** (DeepWiki's dependency
  page lists "License: BSD-2-Clause"; Guix lists "Licenses: FreeBSD").
  The licence *file* itself was not directly read in this sweep — verify
  it from the repo before any use. Do not quote it as confirmed until then.
- Fit: this is the same family of method as the Oct 28 matcher prototype
  (aHash/dHash/pHash + Hamming distance, centre-crop variant). It would
  replace hand-written hash code with a tested library, nothing more.
- What it does NOT do: it does not identify a card, it does not know sets
  or numbers, it does not detect fakes, and a hash distance is not a
  verdict. The Oct 28 results already showed why: genuine same-identity
  pairs scored 10–16, random impostors median 30, but one fake front scored
  16 against its nearest genuine — inside the genuine range. A library
  does not fix that; only a larger same-card test set and a two-gate rule
  (identity first, tells second) do.
- $0 test that would prove it: re-run the Oct 28 matcher numbers using
  this library on *cropped* owner pairs (crop first, hash second), and
  check whether the genuine/impostor/fake separation improves or not.
  Pass = separation improves on crops. Fail = it does not, and hashing
  stays a shortlist tool only, never a pass/fail.
- Red flag: none on method, but do not let "perceptual hash" be sold as
  "AI identification" — it is a similarity number, not an identity.

## 5. tesseract-ocr/tesseract — read the printed text

- Source: https://github.com/tesseract-ocr/tesseract
  (URL surfaced as the project repository in the Tesseract docs returned
  by search; docs at https://tesseract-ocr.github.io/tessdoc/Installation.html)
- What it actually does, in plain words: an OCR engine — it reads printed
  text out of a photo and returns it as text. No built-in GUI; it is a
  command-line / library tool, with language packs for 100+ languages.
- Licence: **Apache 2.0** — stated in the project docs ("available under
  the Apache 2.0 license") and in the Wikipedia summary.
- Fit: read the card name and the printed number off the front, then check
  those two strings against the set list *ourselves*. That is a real
  fake tell in the owner's own words: if the name is wrong, or the number
  does not exist in that set, the card is suspect. OCR is also the cheapest
  way to get an identity candidate without a neural embedding model.
- What it does NOT do: it does not know card fonts, it does not check
  spelling against a set list by itself, it does not read foil or back
  colour, and its accuracy falls on small, shiny, or angled text — which
  is exactly what card photos are. It needs preprocessing (grayscale,
  threshold, deskew — which is where Skewtle-style flattening helps again).
- $0 test that would prove it: run it on 10 owner fronts (cropped, flat)
  and count how many times it reads the name exactly right and the
  printed number exactly right. Pass = most names and numbers exact.
  Fail = it mangles card fonts, and EasyOCR or a card-specific reader
  would need to be tested instead — but that failure itself is useful
  evidence, not a reason to keep OCR-ing badly.
- Red flag: none on licence. The risk is accuracy, not legality: a
  misread name must never become a "fake" verdict on its own. OCR output
  is a candidate to check, not a finding.

## 6. JaidedAI/EasyOCR — heavier OCR, test only if Tesseract fails

- Source: https://github.com/JaidedAI/EasyOCR
  (URL surfaced in the EasyOCR setup.py pages and package pages returned
  by search.)
- What it actually does, in plain words: a Python OCR package built on
  PyTorch, for reading text in photos, including natural scene text, in
  80+ languages. Two lines of Python turn a photo into text with boxes.
- Licence: **Apache 2.0** — stated in its setup.py ("license='Apache
  License 2.0'") and in its README badge.
- Fit: a fallback if Tesseract proves too weak on card fonts. It is better
  on wild, non-document text; it is worse in one practical way — it needs
  PyTorch, which Penguin does not have, and it is heavier to run.
- What it does NOT do: same limits as Tesseract, plus weight. It does not
  identify cards, check sets, or detect fakes by itself.
- $0 test that would prove it: only if the Tesseract test fails — run
  EasyOCR on the *same* 10 fronts and compare exact name/number reads.
  Pass = clearly better than Tesseract on the same photos. Fail = stick
  with the lighter tool.
- Red flag: a fork named EasyOCR2 (cyberiums/EasyOCR) exists in search
  results — do not confuse the two. Use only the JaidedAI original if
  this is ever tested, and check which one is actually maintained.

## 7. tcgdex/cards-database — identity data, not code

- Source: https://github.com/tcgdex/cards-database
  (URL surfaced as the repo html_url in the GitHub API snippets returned
  by search; description: "Pokémon Trading Card Game Card (TCG) Database
  for the TCGdex API".)
- What it actually does, in plain words: the card database behind the
  TCGdex API — sets, cards, numbers, names, and the reference data the
  app's 37,369 identities already come from.
- Licence: **UNKNOWN from this sweep.** No licence field was shown in the
  snippets returned. Do not claim MIT, Apache, or any other licence for
  it until the repo's LICENCE file is actually read.
- Fit: data only, and already in use. There is no new capability here —
  it is the source the app already trusts for identities.
- What it does NOT do: it does not identify a photo, check a fake, grade,
  or give any authenticity signal. And a critical distinction: even if
  the *database code* were openly licensed, the *card images* inside it
  are Pokémon Company art. A repo licence never turns official card art
  into art the app owns or can re-publish as its own.
- $0 test: none needed — this is already the identity source. Any future
  change here is a data-refresh question, not a test question.
- Red flag: licence unknown + official art inside. Keep the existing
  use (identity lookup) and do not expand it into shipping reference
  images as app content without a separate art-licence check.

## 8. tcgdex/python-sdk — API wrapper only

- Source: https://github.com/tcgdex/python-sdk
  (URL surfaced in the TCGdex documentation pages returned by search.)
- What it actually does, in plain words: a Python SDK that wraps the
  TCGdex REST API — query cards, sets, series, prices — so a Python
  program does not have to hand-write the HTTP calls.
- Licence: **UNKNOWN from this sweep.** No licence field was shown.
- Fit: LOW. The app already has identity data locally; an API wrapper
  adds a network dependency for data it already holds. It would only
  matter if a future backend wanted live TCGdex lookups over HTTP.
- What it does NOT do: everything in §7, plus it is not a checker.
- $0 test: none. Do not test what the app does not need.
- Red flag: none, beyond licence unknown. Do not adopt a wrapper to
  solve a problem the app does not have.

## 9. tradingcarddex/Pokemon-Card-CSV — duplicate identity data

- Source: https://github.com/tradingcarddex/Pokemon-Card-CSV
  (URL surfaced in the README commit snippet returned by search, which
  links to this repo.)
- What it actually does, in plain words: Pokémon card data as CSV files,
  with a database site behind it.
- Licence: **UNKNOWN from this sweep.** The only terms seen were in a
  README snippet: "If you use this data in a project, attribution to
  TradingCardDex.com" — attribution is required by that snippet, and no
  licence (MIT/Apache/other) was shown. Do not claim it is freely
  reusable until the repo's own terms are read.
- Fit: LOW. It duplicates identity data the app already has from TCGdex.
  Adding a second identity source without a reason would create the
  exact cross-source confusion the app's rules forbid (never ship a
  cross-source Likely).
- What it does NOT do: identification, fake checks, grading.
- $0 test: none.
- Red flag: attribution requirement + unknown licence + duplicate source.
  Skip unless a specific gap in TCGdex data is ever proven.

## 10. pokepc/dataset — species data, not card data

- Source: https://github.com/pokepc/dataset
- What it actually does, in plain words: static JSON data for Pokémon
  species, games, Pokédexes, abilities, moves, and related game metadata,
  with TypeScript helpers and an OpenAPI description for serving it as a
  static API.
- Licence: **MIT** — shown on the repo page ("License: MIT License (MIT)").
- Fit: NO for card checking. Knowing that Bulbasaur is a Grass Pokémon
  does not tell you whether a Bulbasaur *card* is 001/151, which set it
  is from, or whether its print is genuine. Species data and card data
  are different things, and confusing them would be a real bug.
- What it does NOT do: card sets, card numbers, card images, fake tells.
- $0 test: none.
- Red flag: none on licence, but a fit trap — a clean MIT licence does
  not make irrelevant data relevant.

## 11. 1vcian/Pokemon-TCGP-Card-Scanner — pattern only, Pocket only

- Source: DeepWiki pages for 1vcian/Pokemon-TCGP-Card-Scanner
  (https://deepwiki.com/1vcian/Pokemon-TCGP-Card-Scanner and its
  sub-pages; the GitHub repo itself was not directly opened in this
  sweep, so treat everything here as DeepWiki-reported, not repo-verified.)
- What it actually does, in plain words, per DeepWiki: a browser app for
  Pokémon TCG *Pocket* (the phone game, not physical cards). Upload a
  screenshot of an in-game collection, a YOLO11 Nano oriented-box model
  finds each card in the screenshot, then a 24-bit RGB perceptual hash
  of each cropped card is compared by Hamming distance against a
  precomputed hash database to identify it. All computation runs in the
  browser with TensorFlow.js.
- Licence: **UNKNOWN** — no licence file was read in this sweep.
- Fit: PATTERN ONLY. Pocket screenshots are clean, flat, digital renders
  — the opposite of angled, sleeved, foil-glared physical photos. The
  *pattern* is interesting (detect box → crop → hash → nearest match,
  with the printed number as the tie-breaker for twin printings, as
  described in a related offline-scanner write-up), but the app itself
  does not check physical cards.
- What it does NOT do: physical cards, fakes, grading, centering, backs.
  Its hash database is for Pocket cards, not for the 37,369 physical
  identities.
- $0 test: none on physical pairs. If the pattern is ever pursued, the
  test is the CollectorVision test in §3, not this app.
- Red flag: Pocket vs physical confusion is the trap here. Do not cite
  this as "a card scanner that works" for Real or Replica — it scans a
  game screen, not a card in hand.

## 12. dsouza95/pokemon-tcg-companion — unverified, do not rely on it

- Source: https://github.com/dsouza95/pokemon-tcg-companion
  (URL surfaced as the repo html_url in the GitHub API snippet returned
  by search; the repo README itself was not opened in this sweep.)
- What it actually does, in plain words, per the API description only:
  "AI-powered Pokémon TCG companion — upload a card image to look up its
  info", built with Pydantic AI and FastAPI.
- Licence: **UNKNOWN.**
- Fit: UNVERIFIED. "Look up its info" is identification, not
  authentication, and without reading the README it is impossible to say
  whether it uses a model, an API, a database, or something else — or
  whether it costs money, sends photos to a third party, or works at all.
- What it does NOT do: unknown, for the same reason. Do not assume it
  checks fakes or grades.
- $0 test: none until the README and licence are actually read. If that
  reading shows a real, $0, local method, it can be re-swept then.
- Red flag: unverified + "AI-powered" + photo upload = the exact
  combination that needs a privacy and cost check before any test.
  Photos must never be sent to an unknown third-party service.

## 13. Gap: no dedicated fake-tell repo was found

Searches for "trading card fake / counterfeit detection" on GitHub
returned policy documents, unrelated fraud projects, and guides — not a
code repo that detects Pokémon fakes. Searches for font / rosette /
back-colour tell detection likewise returned guides, not code.

What the guides agree on (and what the owner's own words already said):
the tells are font and spacing, print-dot rosette, back blue swirl and
border, colour saturation, spelling/name errors, absurd HP/damage, and
the light test. Those are *checks to build and test against verified
pairs*, not a library to import. Any future sweep that claims to have
found "the fake detector repo" should be asked for the repo URL, the
licence, and a test on the owner's known fake fronts (the 40 owner-
confirmed fake fronts, plus the Caterpie EX fake front) before it is
believed.

## 14. Gap: no verified Penguin-stdlib backend repo

Searches for a Python-stdlib leaderboard / referral / auth example
returned generic login tutorials, not a small, auditable, stdlib-only
auth + leaderboard + referral module. That is fine: the live Penguin
backend already implements leaderboard and referral tables, and the
sign-in design already written for this app (scrypt, hashed session
tokens, 30-day expiry) is the design to test, not a tutorial to import.
Do not import a generic "login example" — most of them store passwords
badly, skip lockout, or assume Flask/Django, which Penguin does not have.

## Recommended next-test list (top 3, in order)

These are *tests*, not adoptions. Each one ends with a pass/fail report
and a Latch review before anything is used in the app. No training, no
spend, no demo change in any of them.

### Test 1 — CollectorVision, image-to-identity matcher (the biggest blocker)

- Why first: the app's missing piece is an image-to-identity matcher.
  Hashing alone (Oct 28: genuine 10–16, one fake at 16) cannot carry a
  verdict, and the owner still has to type set + number by hand. This is
  the only repo in the sweep that tries to solve that step directly, on
  CPU, for $0.
- How: (a) Pokémon catalog, 10 owner A1 fronts, top-1/top-5 hit rate vs
  known identity; (b) custom catalog built from owner A1 fronts only,
  held-out re-photographs tested against it; (c) one known fake front
  run through both, to see whether it is confidently misidentified.
- Pass bar: top-1 right most of the time, AND wrong-identity / fake
  cards are not confidently matched. Anything less = not a matcher yet.
- Licence gate before any use in the app: AGPL-3.0. Test and read freely;
  do not integrate until the AGPL question is decided and the owner
  approves it. Also map TCGplayer IDs to set + printed number before
  any result is shown to a user.

### Test 2 — Skewtle flatten + card-centering-studio formula, centering protocol

- Why second: both are MIT, both are $0, both are manual and honest
  about their limits, and together they give a centering measurement
  the app currently cannot make from angled photos at all.
- How: flatten 5 angled owner fronts in Skewtle by hand, measure
  left/right and top/bottom with the centering-studio formula, compare
  against the owner's in-hand centering notes (Cottonee, Bisharp,
  Dialga "off-center"; Rockruff/Deoxys "centering fine").
- Pass bar: measured ratios move in the same direction as the owner's
  notes, and re-placing the corners a second time does not swing the
  ratios wildly.
- What it proves: centering *measurement* only. It never proves a full
  grade — corners, edges, and surface still cap the grade, and the
  weakest pillar still rules.

### Test 3 — ImageHash (cropped) + Tesseract OCR, tell-support pair

- Why third: both are small, $0, CPU, permissively licensed (BSD /
  Apache, subject to the licence-file check in §4), and they support
  two different tells the owner named: "does this photo look like the
  reference?" (hash) and "is the name / number right?" (OCR).
- How: (a) re-run the Oct 28 hash test on *cropped* owner pairs with
  ImageHash and check whether genuine/impostor/fake separation
  improves; (b) run Tesseract on the same 10 fronts and count exact
  name reads and exact printed-number reads.
- Pass bar: hash separation improves on crops, AND OCR reads most
  names and numbers exactly. If OCR mangles card fonts, record that as
  a failed test and only then consider EasyOCR on the same photos.
- What it proves: support for two tells, not a verdict. A hash distance
  is not an identity, and an OCR misread is never, on its own, a
  "fake" finding.

## What was NOT verified in this sweep

- Licence files for ImageHash, TCGdex repos, TradingCardDex, EasyOCR's
  current repo state, and the TCGP scanner were not directly read from
  their LICENCE files — only secondary pages / snippets were returned.
  Those licences are marked UNKNOWN or "per secondary sources" above
  for exactly that reason.
- No repo was run against the owner's pairs in this sweep. That is the
  next step, and it is a separate job from this report.
- No paid app, paid API, or closed-source "AI grader" was evaluated as
  a candidate, because the owner direction is $0 and open, and because
  a closed grader cannot be audited against the owner's verified pairs.
- Search was by web search over GitHub, not by cloning repos. A repo
  that search did not surface is not proven to not exist — it is only
  not found here.
