# Verdict fix — part 2 (carrying out the 5 fixes)
Hark, Sat Nov 21 2026, ~6:00–7:30 PM ET. Owner's go-ahead 5:55 PM ET. Verdict switch untouched (OFF). Nothing here is an accuracy claim.

## Bottom line (blunt)
1. **The web gave me 13 same-photo real/fake pairs, 4 real-vs-real controls and 9 same-session pairs** (63 labelled images from 11 pages). That's a useful outside test set. It is still tiny, re-compressed, and labelled by forum captions.
2. **The rosette/screen lane does NOT catch modern counterfeits on its own.** On every macro where I could read the screen, the fakes from China (1st Edition repros, the Disco test-print fake, the fake 1st Edition stamp) are **offset-printed with a regular dot screen, just like real cards.** Periodicity was as strong or stronger on the fakes (AUC 0.19 for "fake = less periodic", i.e. backwards). It only flagged the one consumer-printer fake (CGC Lucky Stadium star: 18 vs genuine 108, same session). Two forum threads (`ef64743`) also show genuine modern holos are printed FM (no rosette) on purpose. So: screen TYPE catches home-printed fakes; it can't tell a good offset fake from real. The tell for those is the **pattern geometry vs a same-card genuine** (dot size, angle, the stamp dimensions — the fake 1st Ed stamp in `ef23015` is measurably the wrong size), not "is there a rosette".
3. **The close-up capture step is built and pushed** (branch `hark/capture-closeup`, commit `f461380`). Visual only, advisory only, overlap-clean at 360 and 1280.
4. Weak hints from same-photo pairs (not claims): fakes read **darker** than their twin in 8/11 pairs (real-vs-real controls: 1/4), and **softer small print** in 8/10 (controls 2/4). Every interval overlaps a coin flip.

## 1. Web image set — `web-set/`
- Script: `scripts/build_web_set.py` (re-downloads images into `web-set/raw/`, cuts crops into `web-set/crops/`). **Images are git-ignored and not committed** (copyright). Committed: `web-set/manifest.csv` + `.json` (source image URL, page URL, label + the quoted caption it came from, same-photo pair id, photo type, estimated px/mm + how it was estimated).
- Counts: 48 source images downloaded (48/48), 66 manifest rows, **63 labelled (34 GENUINE / 29 FAKE)**, 3 rows MIXED (whole images that hold both a real and a fake; kept only as pair sources).
- **Same-photo real/fake pairs: 13** (10 from one Elite Fourum post where the author shot "real cards on the left, fake cards on the right"; 1 backs pair on a couch; 1 Dragonair pair; 1 forum graphic). Plus **4 genuine-vs-genuine controls** cut from the same photos (captions say two real copies), **9 same-session pairs** (CGC lab, Flipside, microscope thread), 1 composite pair.
- Photo types (labelled): phone photo in a scene 32, microscope 8, lab scan/photo 8, lab macro 5, loupe phone 4, composite graphic 4, phone close-up 1, flat photo 1.
- Labels: only what the page states, quoted in `label_basis`. Two rely on a stated convention rather than a per-photo caption (`ef17741_3270`, `_3292`: the post says "real cards on the left, fake cards on the right"). Everything else unstated = UNKNOWN.
- px/mm for macros are **estimates** (scale bars where present: `ef64743` 1000 µm bar ≈ 615 px/mm; `ef23015` on-image mm annotation ≈ 190 px/mm; the rest are size guesses marked "low confidence").
- What I could NOT get: Reddit (403 to scripts — r/IsMyPokemonCardFake has many more same-photo pairs), TCGplayer's article images (JS-rendered), any Evolving Skies fakes, any same-card genuine/fake pair above 15 px/mm on a full card except two (`ef13268_d`, `ef23015_68c`, ~20 px/mm).
- Fence kept: this is an outside TEST set only. Not mixed into any house data, labels, weights or thresholds. Every row says so.

## 2. My tool bugs (2 tries max each)
| Bug | Fix | Result |
|---|---|---|
| Card finder fails on carpet/busy floors | New background-model finder: learns the floor's colours from the frame's outer ring, marks what differs, keeps card-shaped blobs (convex hull, aspect 1.40 ±14%); guards so tight crops don't grab the text box (card ≥15% of frame, same orientation as frame; card-shaped frame filled ≥70% = scan) | Carpet pairs **3/3 found** (was 0/3). Demo pool + samples: 4 images changed crop; by eye the new crop is right on all 4 (the old ones covered only 41–83% of a card that fills the frame). Multi-card line-ups (`find_cards`) still merge touching cards — I cut those test crops by hand. |
| Back crop locks onto the inner swirl | On backs, reject a crop if the band just outside it is still navy frame | Sample A back now takes the full card (frame included). Fixed. |
| Capture-mismatch warning fired 1/3 | New `capture_match()`: resolution ratio >1.35, framing (card-in-scene vs fills-frame), on-card focus at a fixed 10 px/mm (content-normalised), background texture | Render-vs-carpet site pairs **3/3 flagged** (was 1/3). Scan vs phone in demo pool 90/90. **But it over-fires on truly matched photos: 7/16 same-photo pairs/controls flagged**, mostly from the framing rule reacting to how tightly I hand-cropped. In the app (whole photos) framing is meaningful; on crops it isn't. Not fixed (2-try limit). |

## 3. Eval (counts locked first: `eval-web/denominators-locked.json`)
Full tables: `eval-web/results.md`. Short version (x/n, 95% Wilson):
- **Same-photo G→F pairs, any look-closer flag:** 4/12 [13.8–60.9%]. Genuine controls, any flag: 0/4 [0–49.0%]. Same-session pairs: 1/6.
- **Paired direction (fake lower than its twin):** overall lightness 8/11 [43.4–90.3%] vs controls 1/4; small-print sharpness 8/10 [49.0–94.3%] vs controls 2/4. Hints only.
- **Unpaired, phone photos (16 G / 12 F):** best non-capture feature small-print sharpness, LOO catch 2/11 [5.1–47.7%] at false-flag 2/14 [4.0–39.9%]. Useless unpaired. Lab photos (3/3): only capture descriptors separate — confound, not tells.
- **Rosette lane (≥15 px/mm, est.):** ran 23/24. Genuine n=13, fake n=10. Fakes below the lowest genuine: 0/10 [0–27.8%]. AUC for "fake less periodic" 0.19 (backwards). See bottom line #2.
- **Demo pool (re-run with the new finder):** same as before, the top separator is still a capture descriptor (edge-ring texture, 13/19) — `eval-web/demo-pool-front.txt`. Blended web+demo run kept only to show why blending is wrong (`combined-front-BLENDED.txt`).

## 4. Capture flow — `real-or-replica-app`, branch `hark/capture-closeup` (off origin `hark/release-0.3` @ afaa22b), commit **f461380**
- Built in a separate git worktree (`/workspace/work/rorapp-capture`) so the other worker's tree on `hark/release-0.3` was never touched. Nothing committed to `hark/release-0.3`.
- Files: new `www/capture-closeup.js`; `www/index.html` +2 lines (one script tag + comment). No existing code edited.
- After the last capture step's Next: three optional steps — 🔍 **Back logo close-up** (round dashed framing guide; focus check, red frame + "Too blurry — retake" below the threshold), 📏 **Edge shot** (slot guide), ✨ **Holo tilt shot** (tilted card guide). Progress dots, Take / Retake / Next / Skip / Done. Labels 2–4 words; no tips or paragraphs. Home's plum background; the app's own frame/dots/bubble-btn classes so the retheme applies.
- Then the original Next runs unchanged (pool send, light test, gate). Light test is logged as data only (`taken`/`skipped`, `used_in_verdict:false`).
- Storage: shots stay on the phone in `window.ccCloseupShots` beside the front/back; a text-only log (focus scores, which shots, light test) in localStorage `cc_closeup_log`. **Not uploaded** — sending them needs a backend field and the owner's word.
- Focus threshold 120 is a starting value, not validated on real phones.
- Tests (`capture-test/run.py`): opens on last Next ✓, blurry → retake ✓, sharp → Next ✓, Done → light test → gate ✓, no page errors, **check.js clean on all 12 states at 360 and 1280** (top and scrolled to end). Screenshots: `/workspace/work/verdict-fix/capture-test/shots/`.
- Not added to `sw.js` shell list (file is network-first; only matters for offline web use) to avoid colliding with the other worker's `sw.js` edits.

## 5. Matched-pair guide — `matched-pair-guide.md` (one page, plain words)

## What's still missing
- Real matched pairs from the Evolving Skies box (phone + scanner + back close-ups). Nothing on the web replaces them.
- A same-card genuine reference at macro scale for each fake family, so the lane can compare dot geometry instead of "rosette yes/no".
- Phone close-up focus threshold tuned on real phones (use `cc_closeup_log`).
- Capture-match framing rule needs a crop-aware version before it's used on cut-out test images.
- Multi-card finder (touching cards) — only matters for test-set prep.
- Reddit same-photo posts (blocked to scripts; a browser pass could add dozens).

---

## HANDOFF FOR POTION
**What I did (Sat Nov 21, ~6:00–7:30 PM ET):**
- Built an outside web test set: 48 images from 11 public pages → 63 labelled images (34 genuine / 29 fake), 13 same-photo real/fake pairs, 4 real-vs-real controls, 9 same-session pairs. Images not committed; manifest + URLs committed.
- Fixed 2 of my 3 tool bugs fully (carpet card-finding 3/3; back crop inner-swirl lock). Third (capture-mismatch) now catches 3/3 real mismatches but over-fires on 7/16 matched hand-crops; stopped at 2 tries.
- Ran the index + eval over the web set and demo pool with counts locked first. Results in `verdict-fix/eval-web/`.
- Built the optional close-up capture step in the app on new branch `hark/capture-closeup` (commit f461380). Visual only, advisory only, no uploads, switch OFF.
- Wrote the one-page matched-pair shooting guide.
**What I decided and why:**
- Kept the web set test-only and uncommitted (copyright + no contamination of house data).
- Labelled only from captions; two images rely on the post's stated left/right convention (noted per row).
- Close-up shots stay on the phone; not added to the pool send, because that changes what the backend receives and needs the owner's word.
- Built the app change in a separate worktree so the retheme worker's tree and branch weren't touched.
- Did not add the new file to `sw.js` to avoid a merge clash with the retheme.
**Most important finding:** modern counterfeits are offset-printed. "Has a rosette" does not separate them from real cards (0/10 fakes read less periodic than every genuine). The rosette lane needs a same-card genuine reference and compares dot geometry, or it only catches home-printed fakes.
**Open / needs a word:**
- Owner: OK to send the close-up shots with the pool submission (needs a backend field)? Until then they stay on the phone.
- Merge `hark/capture-closeup` into release only after the retheme lands (2-line index.html change + 1 new file; should rebase cleanly).
- Latch: set the phone focus threshold from real `cc_closeup_log` scores; rule on reporting rosette lanes per fake family (offset vs home-printed).
- Evolving Skies box (Nov 21–27): shoot with `matched-pair-guide.md`; seal a blind slice first.
**Branches/commits:** Fake-check `hark/verdict-fix-nov21` (this report + tools); real-or-replica-app `hark/capture-closeup` @ f461380. Main untouched. Nothing built, signed, uploaded or deployed.
**Dates:** fake box Nov 21–27; Run 5 window Dec 1–4 (unchanged); HF credits expire Dec 3.
