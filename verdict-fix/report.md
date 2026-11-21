# Verdict engine — what's wrong, what to do, what I built
Hark, Sat Nov 21 2026. Read-only review + standalone prototype. Live verdict switch untouched (OFF). Nothing in the app, labels, thresholds, registry, Rapid Fire, Play Console, signing, Modal or the frozen demos was changed.

## Bottom line (blunt)
The engine isn't mainly short on clever features. **It's short on fair test data.** Nearly every labelled set I could see mixes up *how the photo was taken* with *whether the card is real*:
- App demo pool: genuine cards are clean scans/renders; fakes are phone photos with background slivers. My measurements: the best "separator" on that set is a capture descriptor (edge-ring texture, LOO catch 13/20) — i.e. it detects the camera, not the fake.
- Site same-card pairs (3): genuine = official digital render, fake = phone photo on carpet.
- The packet itself says the same thing about the house sets: phone darkness features flip sign across domains; genuine-hand and fake-hand were shot in different sessions (§4.5 T6); P-core thresholds don't travel to phone (§4.5 T1); camera lane answered Inconclusive on 687/688 hand photos (§5.7).
- Every lane that "passes" passes on **one fake family** (pair-sheet prints, or 5 battery fakes from one source). That's why numbers look great in-family (399/400) and collapse everywhere else (Run 4 physical-only catch 14.29%).

Second blunt point: **a normal phone full-card photo cannot see the strongest tell.** The print screen on a card is ~6–8 lines/mm; you need ~15 px/mm on the card to read it. The app's photos measure ~8 px/mm (demo pool: 8.25), web copies ~5. So the rosette family — the house's best lane — is physically blind on the app's current input. That isn't a tuning problem. The fix is the capture flow (a close-up shot), not more thresholds.

## Top 5 fixes, ranked (impact vs effort)
1. **Build matched pairs before anything else (high impact, low effort, $0).** Same card, same camera, same session, same light: one genuine copy + one fake copy, front and back. Do it on the phone *and* the scanner. Also two genuine copies of the same card (genuine-vs-genuine controls — the house has none, §5.1). The Evolving Skies fake box (P6, landing Nov 21–27) is the perfect first batch: photograph each fake beside a genuine copy of the same card in one sitting. Without this, every number measures the camera.
2. **Guided capture flow that feeds the strong tells (highest catch upside, medium effort).** After front + back: (a) **back close-up** — fill the frame with the logo/"P" from ~3–5 cm (or a $5 clip-on macro), which puts that region in scanner territory (≥15 px/mm) so P-core / halftone checks can actually run on phones; (b) **edge shot** for the core line; (c) **tilt clip** for holo-and-above (T9); (d) optional light test logged as data only. This is the existing fix items 55/56 — I'm saying they matter more than any new model. Coaching text speaks about framing only.
3. **One manifest + one comparison index, keyed by card + side + capture class (low effort).** Built: `scripts/build_index.py`. Run it on Potion's machine over the real pools (pair library, bank-451, pair-sheet 800, labeled-fake lane). It records sha256, stated label + where the label came from, capture class, px/mm, duplicates, and for every candidate which reference it should be compared to and whether the capture matches. Spec: `folder-spec.md`.
4. **Evaluation harness that splits by capture class and fake family (low effort).** Built: `scripts/eval_harness.py` — writes denominators before measuring, reports x/n + 95% Wilson, flags capture descriptors. Rule to adopt: any feature that separates *only* across capture classes is a confound, not a tell; every lane reports per family and per capture class, never blended.
5. **New lane: screen-type read on the back close-up (medium effort).** Offset = regular AM screen (sharp spectral peaks); inkjet = stochastic spray; laser = toner scatter / weak rosette (sources in comparison-table.md). Built as the `halftone_periodicity` channel. It generalises P-core's idea to any coloured region and to phone macro shots, and targets home-printed fakes (INK/LAS) that Lane D misses. It refuses to run below 15 px/mm. Not validated on real fakes — there are none at that resolution on this machine.

Honourable mention (cheapest untested experiment, packet Idea 5): back-blue hue with a white card in frame to cancel phone white balance.

## Why catch / false-flag stall (from the packet, mapped)
| Cause | Evidence in record | What fixes it |
|---|---|---|
| One fake family per lane | P-core, back lane, one-shot pass all pair-sheet only; scanner battery 5 fakes one family (§4.5, P9) | Fix 1 + per-family reporting (Fix 4) |
| Scanner → phone domain shift | P-core silent on phone; camera lane 0 coverage; Lane C phone AUC rides on illuminant feature that flips on scanner | Fix 2 (macro shot brings phone into scanner domain for the key region) |
| Capture/label confound | genuine-hand vs fake-hand different sessions (T6); my demo-pool measurement | Fix 1 |
| Tiny fake denominators | physical core 29 fakes — one card = 3.4 points; Run 5 short 62 physical fakes | Fix 1 (fake box), lock denominators (Fix 4) |
| Thin margins | P-core genuine max 19.2 vs fake median 18.9; all 6 FFs within 0.35 | Higher-res input (Fix 2) widens dot separation |
| Ceiling | loop+residual voices capped at 22/29 = 75.9% even in theory (§5.4); 26/101 pair-sheet fakes pass both checks | New channels that read different physics: tilt, texture, edge, screen type |
| Reference integrity | 3 designated fakes sitting as genuine `master.ref`; bank-451 burned (§7.3) | Manifest with label_source + registry_check column (Fix 3) |

## Which strong photo tells the engine already uses vs ignores
- **Uses:** dot energy inside back "P" (scanner), back dappling (pair-sheet scanner only), fonts/centering (Lane D), identity/catalogue checks, designated-registry hash match.
- **Ignores or can't yet see:** screen type (AM vs FM) on phone close-ups; back-blue hue/dappling on *phone* input; holo masking/dynamics (no tilt capture); edge/core line as its own shot; corner radius from a straight-on photo; small-print sharpness compared like-for-like.
- **Correctly kept out:** light test as a verdict, price/popularity priors, model judges.

## Real vs fake table
Full table with sources: `comparison-table.md`. Short version — **phone photo (A):** back blue/dappling (white-balance sensitive), text facts (é, HP, typos, set number), fonts/symbols vs same-card reference, holo in wrong places. **Scanner or macro (B):** rosette vs inkjet/laser screen, dots inside solid black, small-print sharpness, edge core line. **Physical only (C):** texture by fingertip, weight, light test, thickness, tilt behaviour (unless video).

## What I built (all in `/workspace/work/verdict-fix/`)
- `scripts/cardfeat.py` — deterministic channels in the house output shape (ran / could_not_run + reason): capture profile, halftone periodicity, small-text edges, centering, back blue, HS-histogram distance (labelled capture-match only).
- `scripts/compare_cards.py REF CAND [--side back]` — side-by-side report + optional sheet PNG + JSON. Never prints a verdict word; flags "look closer" and a CAPTURE MISMATCH warning.
- `scripts/build_index.py` — non-destructive manifest, duplicates, comparison index, denominators.
- `scripts/eval_harness.py` — locked denominators, AUC, leave-one-out catch/false-flag x/n with Wilson 95%.
- `scripts/selftest_halftone.py` — proves the halftone metric reads what it claims, on synthetic prints.
- `index/` — manifest over the images on this machine: 204 files, 98 unique, 53 duplicate groups (the same demo images live in 3 folders), 0 identity-matched genuine/fake pairs with stated labels.

## Tiny-sample results (honest, not accuracy claims)
- **Demo pool fronts, n = 25 genuine / 20 fake** (`sample-output/eval-front.txt`):
  - Halftone: could_not_run on 45/45 (below resolution). Expected.
  - Best non-capture feature, overall lightness: LOO catch **3/20 = 15% [Wilson 5.2–36.0%]** at false-flag **2/25 = 8% [2.2–25.0%]**. Weak; fakes run a bit darker, matching the owner's "prints darker", but nowhere near usable.
  - Small-text edges: catch 0/20 [0–16.1%].
  - Capture descriptor edge-ring texture: catch 13/20 [43.3–81.9%] at FF 2/25 — **this is the confound, not a tell.** It's why this set must not be used to grade anything.
- **Genuine scans (sample A front/back):** halftone ran on 2/2, strong periodic peaks (178, 1005).
- **Synthetic self-test:** offset-style AM print peak score 2990 vs inkjet-style FM 51 at 24 px/mm; both refuse at 5 px/mm. Synthetic only.
- **Sample A (genuine) vs sample B (known fake) backs:** halftone couldn't run on B (5.2 px/mm web copy). Back-blue hue differs by 14° (B more purple — a known fake trait), but the capture differs, so white balance could explain it. **Bug found in my own tool:** on A's back the card finder locked onto the inner swirl instead of the navy frame, so the frame-vs-swirl numbers for A are invalid.
- **3 same-card web pairs (genuine render vs fake carpet photo):** card localisation failed on the carpet photos (3/3 read as full frame), and the automatic capture-mismatch check flagged only 1/3. Lesson: the capture gate has to make the card fill the frame; don't trust localisation on textured backgrounds.

## What won't work (said plainly)
- More threshold tuning on the existing sets. The record already shows the ceiling (75.9%) and the domain collapse.
- Grading the app on demo-pool or site images — they're confounded by capture.
- Rosette/P-core on ordinary phone full-card photos — not enough pixels on the card.
- Light test as a verdict input.

## Data that's missing
1. Same-card, same-capture genuine + fake pairs (phone and scanner). **Zero on this machine.**
2. Any fake image at ≥15 px/mm on this machine (the only high-res images are one genuine pair).
3. Genuine-vs-genuine controls (two copies of the same card).
4. Phone close-ups of backs (genuine and fake) — needed to calibrate a phone P-core / screen-type lane.
5. Holo pile scans for the capture gate (packet §6.7 gap); tilt clips of genuine vs fake holos.
6. The real pools (pair library, bank-451, pair-sheet, labeled-fake lane, designated registry) aren't on this machine — the manifest needs to run on Potion's.

## Note on the workspace
While I worked, `/workspace/work/rorapp/www/index.html` and `hark-extras.js` were changed by another process. Not by me — I wrote nothing outside `verdict-fix/` (plus a read-only clone in `work/gh_ro/`).

---

## HANDOFF FOR POTION
**What I did (Nov 21, 2026, ~5:45–7:30 PM ET):** Read deepdive.md in full. Searched the workspace (rorapp, ccrepo, demo pools, samples, assets) and GitHub (read-only clone of `Fake-check`, `rosette-loop-lens`). Researched genuine manufacture vs fake methods (5 fetched sources, in comparison-table.md). Built a standalone comparison prototype, a non-destructive manifest/index generator, a locked-denominator eval harness, and a halftone self-test. Pushed those files only to new branch `hark/verdict-fix-nov21` on `caudillsabastian6-png/Fake-check` (a new `verdict-fix/` folder; no existing file touched; main untouched).
**What I decided and why:**
- Ranked "matched pairs" and "guided capture with a back close-up" above any new feature: the record and my measurements both show capture domain and single-family fakes, not missing features, are what's stalling catch/false-flag.
- The halftone channel refuses below 15 px/mm instead of guessing (house law: couldn't look = Inconclusive).
- Labels taken only from files that state them; the 3 site pairs labelled only by filename are kept UNKNOWN (filename_hint column), per Book Law 6.
- Conflict flagged: the Nov 19 packet says "Hark never pushes"; Sabastian's live word today asked me to push a branch (never main). I followed his live word, branch only, additive files only.
**Fences kept:** switch OFF; card check advisory; no labels, weights, thresholds, registry, Rapid Fire, Play Console, signing, Modal, or demo/ demo-1/ changes. No accuracy claims beyond the tiny-sample numbers above.
**Open items:**
- Run `build_index.py` + `eval_harness.py` on your machine over the real pools; add capture_class + physical_copy_id stamps.
- Evolving Skies fake box (Nov 21–27): owner designates in hand, then photograph each fake beside a genuine copy of the same card, same session, phone + scanner, plus back close-ups. Keep a slice sealed as blind exam supply (Latch decides the split before anyone measures).
- Latch: rule on whether "separates only across capture classes = confound" becomes a standing test rule; set the px/mm floor for any rosette-family read on phones.
- Owner's word needed before any capture-flow change ships in the app (back close-up, edge shot, tilt clip).
- My tool bugs to fix next: card finder on textured backgrounds; inner-frame lock on some backs.
**Dates:** Fake box lands Nov 21–27. Run 5 window Dec 1–4 (unchanged; nothing here moves it). HF prepaid credits expire Dec 3.
