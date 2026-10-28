# Tells v2 Calibration / Accuracy Run — 2026-10-27

Owner order Oct 27 00:36 ET. $0, Pillow only, NO SAM, NO Baseten, NO Meta Model API calls in this job.
Tool: ~/workspace/fake-check/playground/tells-v2/tells_v2.py — 5 tells, verdict >=2 strong mismatches = Likely Counterfeit, 0 strong + >=3 matches = Likely Genuine, else Inconclusive. Estimates only, never official, never guaranteed.

## Headline — read this before quoting any %

**Do NOT quote 29% as 'the checker's accuracy.' It is not. It is the rate at which tells v2, run on mismatched capture types (owner/web photos vs official clean renders), happened to cross 2 strong mismatches — mostly on artefacts, see Limitations.**

Identity-matched fake-vs-genuine, n=17:
- Likely Counterfeit (correct flag): 5/17 = 29.4%
- Inconclusive: 11/17 = 64.7%
- Likely Genuine (WRONG, false negative): 1/17 = 5.9%

Clean single-card subset only (excludes 3 contaminated comparison/video-still fakes web-01, web-02, web-07), n=14:
- Likely Counterfeit: 2/14 = 14.3%
- Inconclusive: 11/14 = 78.6%
- Likely Genuine (wrong): 1/14 = 7.1%

Owner-photo anchor subset only (anchor-01..07, owner hand photos vs official renders), n=7:
- Likely Counterfeit: 0/7 = 0%
- Inconclusive: 7/7 = 100%
- Likely Genuine (wrong): 0/7 = 0%

Genuine-vs-genuine controls: NOT AVAILABLE on disk. No identity has two distinct genuine card photos on file (pairs/ holds one official render per identity). A REAL-vs-itself run would trivially score 5/5 Genuine and was NOT counted. Genuine control accuracy is therefore unknown, not 100%.

Cross-identity negatives (fake of one card vs genuine of a different card, should be Inconclusive by rule), n=5:
- Inconclusive: 4/5 = 80%
- Likely Counterfeit: 1/5 = 20% (neg-04, Dark Weezing fake vs Wartortle genuine — a mismatch, not a same-identity call)

## Per-pair results (fake = user, genuine = reference)

| ID | Card | Side | Verdict | Matches | Strong | Strong tells |
|---|---|---|---|---|---|---|
| anchor-01 | Charizard GX SM60 | front | Inconclusive | 4 | 1 | colour_histogram |
| anchor-02 | Salazzle GX 132/147 | front | Inconclusive | 4 | 1 | colour_histogram |
| anchor-03 | Latias & Latios GX 113/181 | front | Inconclusive | 3 | 1 | colour_histogram |
| anchor-04 | Florges EX 67/119 | front | Inconclusive | 4 | 1 | colour_histogram |
| anchor-05 | Mewtwo EX XY106 (genuine XY107) | front | Inconclusive | 4 | 1 | colour_histogram |
| anchor-06 | Leafeon GX 13/156 | front | Inconclusive | 2 | 1 | colour_histogram |
| anchor-07 | Toxapex GX 57/145 | front | Inconclusive | 2 | 1 | colour_histogram |
| web-01 | Mega Charizard X ex 125/094 | front | Likely Counterfeit | 1 | 2 | aspect_ratio, colour_histogram |
| web-02 | Giratina V 186/196 | front | Likely Counterfeit | 1 | 2 | aspect_ratio, colour_histogram |
| web-04 | Disco Charizard front | front | Likely Counterfeit | 2 | 2 | aspect_ratio, colour_histogram |
| web-05 | Disco Charizard back | back | Likely Counterfeit | 1 | 3 | aspect_ratio, border_rgb, colour_histogram |
| web-06 | Disco Machamp front | front | Likely Genuine | 4 | 0 | — |
| web-07 | Articuno GX 171/168 | front | Likely Counterfeit | 1 | 4 | aspect_ratio, mean_rgb, border_rgb, colour_histogram |
| web-08 | Shining Steelix 112/105 | front | Inconclusive | 2 | 1 | colour_histogram |
| web-09 | Dark Weezing 14/82 | front | Inconclusive | 1 | 1 | colour_histogram |
| web-10 | Wartortle Base 42 | front | Inconclusive | 2 | 1 | colour_histogram |
| web-11 | Slurpuff 69/119 | front | Inconclusive | 2 | 1 | colour_histogram |

## Per-tell behaviour, n=17

| Tell | Match | Strong mismatch | Reading |
|---|---|---|---|
| aspect_ratio | 10/17 | 5/17 | Strong hits are mostly crop-size artefacts (e.g. web-04 genuine 330x558 vs fake 330x462; web-01/02 comparison photos 1920x1080), not card-geometry tells. Aspect must be measured on a card-only crop, not a full photo. |
| mean_rgb | 8/17 | 1/17 | Weak discriminator photo-vs-render. |
| border_rgb | 8/17 | 2/17 | Weak discriminator photo-vs-render. |
| edge_density | 14/17 | 0/17 | Never a strong mismatch in this run — threshold as set does not discriminate at all here. |
| colour_histogram | 0/17 | 16/17 | **Systematic artefact.** Every photo-vs-render pair fails histogram, fake or not. This tell is currently measuring capture type (photo lighting/background vs clean render), not counterfeit print. It alone cannot drive a Counterfeit verdict until genuine and fake are captured the same way. |

## Inventory — denominator is NOT the whole pool

- Merged pool index: ~/workspace/fake-check/pool-merged-2026-10-26.json — 8,658 distinct (8,484 base: 7,173 real + 1,311 fake in that index, + 174 truly new hand-photo entries). That index is a link index, not 8,658 image files in one folder, and it is NOT the accuracy denominator.
- Verified pool counts on record Oct 25 (different counting, do not conflate with the merged index): 927 genuine, 1,347 fake, 7 unknown.
- web-fakes-pool/: 1,292 files on disk (wf-001..). No identity manifest was matched to genuine pairs in this job, so wf files contribute 0 to the accuracy denominator here. Counting them would inflate n with unmatched cards.
- Identity-matched pairs with BOTH a verified fake image and a verified genuine image on disk: 17 (16 fronts + 1 back). Anchor 01..07 + web 01, 02, 04, 06, 07, 08, 09, 10, 11 fronts, plus web-05 Disco back. Web-03 excluded (multi-card group shot, not pairable). Anchor-08 excluded (no fake photo, genuine pair only). Web-12 excluded (linked only, no photo).
- FAKE-001..009 (owner-scanned Oct 22, ground truth by owner word, corrected crops in fake_6_epzv_corrected/): EXCLUDED — study file states no genuine counterpart in owner scans was confirmed, and no downloaded genuine render for JTG 089 / PFL 044-052 / Evolutions 11/108 was on disk in a pairable form for this run. Do not add them by downloading renders in a $0 local job without a fresh scope decision.
- Oct 26 fake fronts (40 files, indices 324-363, ~/workspace/user/files/): EXCLUDED from accuracy, reported separately. Owner-declared fakes, fronts only, provisional IDs only, group photos unsplit, 3 photos marked UNCERTAIN. They are intake, not ground-truth pairs, and no genuine pair per identity was verified for them in this job.
- Pilot: first 5 pairs (anchor-01, anchor-02, web-04, web-06, web-09) gave 1 Counterfeit, 1 wrong Genuine, 3 Inconclusive — thresholds were not broken (not all one verdict), so the full 17 were run. Pilot = 5, full = 17, because the total matched set is only 17.

## Cross-identity negatives

- neg-01: anchor-01 fake vs anchor-02 REAL — Inconclusive, matches=3, strong=1
- neg-02: anchor-02 fake vs anchor-01 REAL — Inconclusive, matches=4, strong=1
- neg-03: web-04 fake vs web-06 REAL — Inconclusive, matches=4, strong=1
- neg-04: web-09 fake vs web-10 REAL — Likely Counterfeit, matches=1, strong=2
- neg-05: web-11 fake vs anchor-06 REAL — Inconclusive, matches=2, strong=1

## Limitations — why this is not a releasable accuracy %

1. Capture-type mismatch dominates. Fake side = owner hand photos (1536x2048), web comparison photos, CGC crops, sticker/typo photos. Genuine side = official clean renders (734x1024, 600x825, 330x558). Pixel tells (especially histogram) measure photo vs render, not fake vs genuine. A real calibration needs same-capture pairs: both sides as phone photos, or both as card-cropped images, same lighting handling.
2. No SAM in this job, per owner order ($0, SAM only if necessary). That means no card-only crops were made here — full photos were fed to tells_v2.py as-is. Aspect and border tells are therefore contaminated by background/hand/frame.
3. Holo, font, texture, and print-sharpness tells are NOT measured by tells v2. The strongest documented tells for several of these fakes (e.g. Disco holo pixel size, typo text, light-test translucency) are outside the 5 pixel tells, so a miss here does not mean 'no tell exists.'
4. Front-only except web-05 back. No fake backs exist except web-05, and genuine backs were never used as fake backs, per standing rule. Owner-printed help-text backs were never used.
5. Small n. 17 pairs, 1 wrong Genuine (web-06 Disco Machamp — CGC fake photo vs CGC genuine photo scored 4 matches, 0 strong; pixel tells are too coarse for that high-end forgery class). One pair swings the wrong-rate by ~6 points. Do not publish a % from n=17 as a product accuracy claim.
6. No files moved, deleted, or merged in this job. Originals untouched; per-pair JSONs in /tmp/tells-calib/ (ephemeral, not the deliverable — this report is).

## What would make a real accuracy %

- Same-capture matched pairs (photo-vs-photo, card-cropped the same way) for at least 30-50 identities, with a held-out split (calibrate thresholds on one half, test on the other).
- A genuine-vs-genuine control set (two distinct genuine photos per identity) to measure false-Counterfeit rate.
- Recalibrated thresholds, especially histogram (photo-vs-render offset) and edge_density (currently never strong), and aspect measured on crop only.
- Then, and only then, a confusion table: fake→Counterfeit / Inconclusive / Genuine, genuine→Genuine / Inconclusive / Counterfeit, with denominators.

---

## UPDATE — Unmatched cards scored by real-card tells (owner correction Oct 27 00:37 ET)

Owner correction supersedes the matched-pair-only rule in the original brief: cards WITHOUT a matching fake or matching real on file CAN be scored, by fonts, colours, textures, and other details that only appear on real cards. The bar was NOT lowered to make the % look higher. Matched-pair accuracy above is unchanged and is reported separately from unmatched accuracy below. A Likely Genuine verdict still needs strong measured tells, not just a name match — where the evidence was not enough, the verdict stays Inconclusive.

### SAM rule (owner rule Oct 27 00:36 ET, reinforced)

SAM costs ~$0.0025 per crop on record. SAM is used ONLY if necessary. This job made **0 SAM calls, $0 SAM spend, $0 Baseten spend, $0 Meta Model API spend**. The AI Loop / Tells work is to learn from SAM and train off him, so the local system still knows what SAM knew when SAM has to go.

Places SAM would have been used, and what replaced it locally:
- Card-only cropping of full hand photos (anchor fakes, Oct 26 fronts) — replaced by: (a) reusing SAM crops already on file from Oct 26 triage ($0 reuse, no new call), (b) using already-cropped corrected FAKE files in fake_6_epzv_corrected/, (c) running full photos as-is through tells_v2.py with contamination explicitly noted in Limitations, NOT hidden.
- Splitting Oct 26 group photos into per-card crops — NOT replaced. No local crop was invented for group photos, so those cards were NOT scored (see below, 0 scored). Splitting them would be a necessary-SAM use, and needs a fresh owner yes with cost logged before it happens.
- Cropping FAKE-001..009 scans — replaced by the corrected crops already on file.
- Creating new genuine pair renders for FAKE-001..009 — NOT done. No renders were downloaded and no SAM crop was made for them, so they are excluded from pixel accuracy and appear only in the documented-tell audit below.

Hypothetical SAM cost avoided in this job (for scale only, not a saving claim): ~86 crops (17 matched pairs + 9 FAKE + 20 genuine pilot + 40 Oct 26 fronts) x ~$0.0025 ≈ $0.22, all NOT spent.

### Unmatched set A — FAKE-001..009, documented real-card-detail audit (NOT tells_v2 pixel accuracy)

These 9 are owner-scanned ground-truth fakes (Oct 22) with no genuine pair on disk. They were NOT run through tells_v2.py against a different-identity genuine render and called Counterfeit — that would be a cross-identity artefact, not a tell. Instead each was audited against the study-documented real-card details for its own identity (fake-study.md, text checked against TCGdex genuine card data):

| ID | Imitates | Documented real-card detail that the fake lacks / breaks | Strength |
|---|---|---|---|
| FAKE-001 | Toedscruel JTG 089/159 | Fine print soft/fuzzy; genuine prints razor sharp, even tiny lines | Strong, subtler — study calls it subtler, flatness alone does NOT convict a Normal printing |
| FAKE-002 | Zacian PFL 045/094 | Purple sparkle website-overlay graphic printed over attack, hiding name/text; no real card covers its own attack text | Decisive |
| FAKE-003 | Gligar PFL 049/094 | Orange refresh-icon overlay over attack, hiding name; genuine Poison Jab fully readable | Decisive |
| FAKE-004 | Alcremie PFL 044/094 | Purple circular-arrow overlay over attack, hiding name | Decisive |
| FAKE-005 | Brambleghast PFL 047/094 | Purple circular-arrow overlay across Ability + attack, hiding name | Decisive |
| FAKE-006 | Vibrava PFL 052/094 | Smallest text soft/jagged, art prints flat/smooth vs genuine brush texture; best fake in batch | Strong, subtler — study: "honest — these are subtler", in-hand stock/back/light tests not confirmable from scan |
| FAKE-007 | Zacian PFL 045/094 (twin) | Purple circular-arrow overlay over Limit Break, hiding name/cost/text | Decisive |
| FAKE-008 | Charizard EVO 11/108 (pale) | NO gold EVOLUTIONS logo across art window, NO gold starburst behind stage icon; mottled smear foil vs genuine cosmos holo; printed-in wear | Decisive |
| FAKE-009 | Charizard EVO 11/108 (saturated) | Same missing EVOLUTIONS logo + starburst; smeary foil vs cosmos holo; printed-in wear | Decisive |

Unmatched fake audit result, n=9:
- Decisively flagged by a real-card detail: 7/9 = 77.8%
- Strongly flagged but subtler (soft print only): 2/9 = 22.2%
- Missed entirely: 0/9 = 0%
- Any documented tell (decisive + strong): 9/9 = 100% — but do NOT quote 100% as pixel accuracy. It is a documented-tell audit, and the 2 soft-print cases are subjective at scan resolution and need in-hand follow-up (stock, back, light test), per the study itself.

Font note, honest limit: tells_v2.py does NOT measure font. The font/typography tells in this audit are the study's documented text checks (attack name hidden by overlay, missing logo, typo-class tells elsewhere), NOT an automated font measurement in this job. An automated font measurement was NOT invented here.

### Unmatched set B — Genuine cards with no fake counterpart, intrinsic pixel pilot (NOT name-match Genuine)

Pilot, n=20: first 20 truly-new hand-photo entries from pool-merged-2026-10-26.json, using their EXISTING Oct 26 SAM crop paths ($0 reuse, no new SAM). Cards include Alolan Exeggutor, Alolan Grimer, Baltoy, Blaine's Last Stand, Boss's Orders, Bruno, Bunnelby, Caitlin, Chandelure, Chatot, Chili & Cilan & Cress, Chimecho, Claydol, Cleffa, Coalossal V, and others in that list.

Intrinsic measurements (tells_v2 measure(), Pillow only):
- Genuine hand SAM crops: edge_density mean 0.0484, range 0.0177-0.0878; aspect mean 0.780, range 0.730-0.806
- Unmatched FAKE corrected crops (Set A, for comparison only, different capture): edge_density mean 0.0964, range 0.0658-0.1516; aspect mean 0.723, range 0.701-0.757
- Genuine official renders (pairs/): edge_density mean 0.1133, range 0.0511-0.2750; aspect mean 0.719, range 0.716-0.727

Finding: edge density and aspect OVERLAP across genuine and fake once capture type changes. Genuine hand photos are SOFTER (lower edge density) than scanned printed fakes. A threshold that called low edge density "fake" would flag genuine hand photos; a threshold that called high edge density "genuine" would pass scanned fakes. Aspect is also capture-dependent (SAM hand boxes run 0.73-0.81, renders run 0.716-0.727).

Unmatched genuine pilot result, n=20, by intrinsic pixel tells alone:
- Likely Genuine: 0/20 = 0%
- Likely Counterfeit: 0/20 = 0%
- Inconclusive: 20/20 = 100%

That 0% Genuine is NOT a failure of the cards — they are genuine by provenance (owner hand photos, pool-merged). It is proof that intrinsic pixel tells alone, without a same-identity reference, are NOT enough to earn a Likely Genuine verdict under the owner's no-lowered-bar rule. A name match in the pool index was NOT counted as a tell. To earn Genuine for an unmatched card, the job would need identity-specific real-card details checked per card (text vs TCGdex, set logo, holo pattern, font sharpness at magnification) — that per-card documented check was done for Set A fakes, and has NOT been done for this genuine pilot, so they stay Inconclusive.

### Unmatched set C — NOT scored, reported as pending (do not count as correct or incorrect)

- Oct 26 fake fronts: 40 files, indices 324-363, ~71 appearances, provisional IDs only, group photos unsplit, 3 UNCERTAIN. Scored: 0/40. Reason: splitting group photos and verifying IDs at full resolution would need SAM crops (SAM only if necessary, not approved for this in this job) and full-resolution ID verification. Owner declaration alone was NOT counted as a score — that would be circular.
- web-fakes-pool wf-001.. (1,292 files on disk): Scored: 0/1,292. Reason: no identity manifest matched to genuine pairs in this job, and no per-card documented tell audit was done for wf files here.
- FAKE-001..009 pixel accuracy: Scored by tells_v2: 0/9. Reason: no genuine pair on disk (see matched section). They appear only in Set A documented-tell audit above, not in pixel accuracy.

### Both numbers, side by side (do not merge them)

| Set | n | Correct flag / Genuine | Inconclusive | Wrong |
|---|---|---|---|---|
| Matched fake-vs-genuine, tells_v2 pixel | 17 | Counterfeit 5 (29.4%) | 11 (64.7%) | Genuine 1 (5.9%) |
| Matched clean subset (excl. 3 contaminated) | 14 | Counterfeit 2 (14.3%) | 11 (78.6%) | Genuine 1 (7.1%) |
| Unmatched fakes, documented-tell audit | 9 | Decisive 7 (77.8%), any tell 9 (100%) | 0 by audit definition | 0 missed |
| Unmatched genuine, intrinsic pixel pilot | 20 | Genuine 0 (0%) | 20 (100%) | Counterfeit 0 (0%) |
| Unmatched Oct 26 fronts + wf pool | 40 + 1,292 | NOT SCORED | — | — |

Conclusion for the owner: removing the matched-pair-only rule does NOT create a high unmatched accuracy %. It creates a split result: documented tells can flag known unmatched fakes (7/9 decisively), but intrinsic pixel tells alone cannot earn Genuine for unmatched genuine cards (0/20). Any future unmatched scoring that claims high Genuine accuracy from pixels alone, or from a name match, would be lowering the bar — and was not done here.
