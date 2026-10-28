# Real or Replica — App V2 local demo (playground only, Oct 27, 2026)

**LOCAL ONLY. Not a release. Nothing here is deployed, published, shared,
or sent to anyone. No public link exists for this build. No Play submission.
No spend, no keys, no tokens, no secrets in code or output.**

## What this is
A simple local web demo that wires the App V2 playground checker
(`../app-v2-merged/app_check_v2.py`) into one tester flow:
upload a front photo → verdict first → Tells Explainer expandable →
front-only honesty line. It is the V2 logic, not a copy of the old
public demo, and not the full Play app.

Hard rules carried over from V2, unchanged:
- Identity-first: the reference must be for the supplied identity, or
  the verdict is Inconclusive — never Genuine.
- A name/manifest match alone never produces Likely Genuine; only a
  tells measurement can.
- Every Likely verdict is an ESTIMATE ONLY, never official, never
  guaranteed, never a grade, never a SAM authentication.
- SAM is last-resort only: a refused / bad-aspect crop stays
  Inconclusive and records SAM escalation required. This demo makes
  NO live SAM, Baseten, or Meta call ($0, api_calls=0).
- Front-only: backs are not tells-scored in V2. The UI says plainly
  a back would help if it disagreed.
- Inconclusive stays Inconclusive — it is never upgraded by the UI.
- No real card photo is shown in the demo UI. Reference images are
  used server-side only for tells measurement and are never served;
  API responses strip user/reference file paths and image fields.
  Backgrounds are CSS gradients only (crossfade spec used as a visual
  reference only): no Raian art, no official Pokémon art, no real
  card photos as backgrounds.

## Files
- `index.html` — one upload/check flow, verdict first, Tells Explainer
  `<details>`, 700ms background crossfade home→verdict, reduced-motion
  fallback (instant switch, no animation).
- `server.py` — stdlib-only local server, binds 127.0.0.1:8765 only.
  Endpoints: `GET /` (demo page), `GET /api/identities`,
  `POST /api/canned` (Test A / Test B, no photo shown),
  `POST /api/check` (multipart photo + identity).
- `run_tests.py` — re-runs canonical V2 tests into `out/`.
- `out/` — test outputs, including `demo-test-results.json`.

## Run it locally
```
cd ~/workspace/fake-check/playground/app-v2-demo
python3 server.py
# open http://127.0.0.1:8765/ in a local browser, then Ctrl+C to stop
```
Uploads stay on this computer only. Stop the server when done; it
does not stay running and does not expose anything to the network.

## Test results, Oct 27, 2026 — local, $0
Re-run through `run_tests.py` (exit 0, PASS 2/2):
- Test A — Alakazam crop vs Alakazam|Base|1: **Likely Genuine**,
  tells matches=5, strong_mismatches=0. PIPELINE TEST ONLY — the crop
  was derived from the same source image, so this is NOT
  authentication proof.
- Test B — same Alakazam crop vs Charizard|Base|4: **Inconclusive**,
  reason `identity_mismatch_reference_not_for_supplied_identity`.

Live server smoke test (started, checked, stopped, same session):
- `GET /` → HTTP 200, 6,419 bytes.
- Canned A via `/api/canned` → Likely Genuine, 5/5 matches.
- Canned B via `/api/canned` → Inconclusive, identity mismatch.
- Upload of the Test A crop via `/api/check` → Likely Genuine, 5/5,
  and the response contained no reference image field.
- Server was stopped after the smoke test; no process left running
  for testers, no public endpoint.

## Exact site-demo styles + all upgrades, Oct 27 ~11:32 AM — for owner review only, not shared yet
CORRECTION: the web demo source IS in the workspace — owner was right.
`~/workspace/cloudflare-pages/demo-website-v1/demo/index.html` (229,086
bytes, Oct 24) is the public demo Muse built, with home, picker,
capture (front/back, file picker), Light Test, Condition Grader,
sample verdict/receipt, Binders, Plan, Games, and Tells (live camera
on the Tells screen). V2 playground now uses that file's exact
styles: Cinzel headings, Georgia body, bg #0b0908, surface #1c1917,
text #fff8e7, gold #ffc53d, b-sky bubble buttons, 4px dashed sky
frame, gold corners, dock nav, demo banner. Verdict now uses the
site's verdict-pill + 5-bubble meter (bubbles = front tells matching,
labelled, not a percentage or grade). Note: the site capture screen's
"Take the photo" opens a file picker, not live camera — V2's live
camera is an upgrade over that, kept. Play app source is still NOT
in the workspace; this correction is about the web demo only.

## Site-demo look + all upgrades, Oct 27 ~11:31 AM — for owner review only, not shared yet
Look now matches the public site demo screenshot (owner, Oct 27 ~11:28 AM):
dark background, gold PUBLIC DEMO banner, "← Pick a category",
"Checking: Pokémon Card · Photo 1 of 2 · DEMO", serif uppercase
"First, the front of the card", dashed blue frame with gold corners,
"Take the front photo" / "Use a sample photo instead" pill buttons,
"Photos you pick stay on your device" line, bottom nav Check / Binders /
Games / Plan / Explore / Tells (Check only live in this preview).
Flow is Photo 1 front → Photo 2 back → Ready to check, with dots.
Upgrades kept inside that look (NOT the old site logic): V2 tells
checker, back scoring (separate, combined verdict), live camera
capture front/back, Fake-of-the-Week, Limits-first, photo guide,
slab cert field, Look-twice for Charizard, What-would-have-helped +
Re-run on Inconclusive, community report held locally, canned
Test A/B as sample photos. Old site demo logic is NOT claimed as V2;
only its visual style is matched. Verified: canned A/B PASS 2/2,
front+fake back = Counterfeit via server, all site-look strings
present (headings/buttons render uppercase via CSS, so raw HTML is
mixed case). Server stopped after smoke test. Still missing:
owner's further site screens (back screen, verdict screen, etc.) —
send them and they will be matched the same way.

## Camera + back scoring, Oct 27 ~11:25 AM — for owner review only, not shared yet
- Live camera view in the demo: Start camera, Capture front, flip card,
  Capture back, Stop camera (manual capture only; auto quick-snap NOT
  yet). Camera needs a real browser — in a file preview it may be
  blocked, then Choose File is the fallback. Captures stay local.
- Back scoring in App V2 (`app_check_v2.py --back --back-reference`):
  same 5 tells, scored separately against a card-only back reference.
  Back aspect must match within 0.15, else back stays Inconclusive.
  Combined: Counterfeit if front OR back is Counterfeit; Genuine only
  if BOTH are Genuine; otherwise Inconclusive. Front-only unchanged.
- Demo server accepts `back_photo` and scores it against the pilot
  back reference: one genuine English back crop (Disco Charizard real
  back). Backs are mostly uniform, so this is a back-design/print
  score, NOT identity-specific, and NOT a back pool yet.
- Pilot results, $0: front Genuine + fake back = Likely Counterfeit
  (back 1/5 matches, 3 strong); front Genuine + real back = Likely
  Genuine (back 5/5); front only = Likely Genuine, back None.
  Canned A/B still PASS 2/2. Server stopped after smoke test.
- NOTE: this playground demo is NOT the real app — it is a simple
  web page, so it looks different from the real app. The real app
  source is not in the workspace, so its exact screens/colours cannot
  be copied from here. A screenshot of the real app's checker screen,
  or the app source, is needed to match it.

## Polished Oct 27 ~11:22 AM — for owner review only, not shared yet
In place in `index.html` (12,062 bytes), same checker, same $0 tests:
- Fake-of-the-Week card on home (text only, labelled FAKE, one tell,
  no card photo shown) + "Try the checker" button.
- Limits-first box (3 lines) and 3-line photo guide on the camera step.
- "Add the back?" toggle + front-only line on every verdict; backs
  are still NOT scored in V2.
- Slab cert field in the same check flow; cert alone never makes a
  card genuine, cert without card-inside stays incomplete.
- "Look twice" line only for Charizard (commonly faked identity).
- "What would have helped" line + "Re-run with that" button on
  Inconclusive only (same-card reference for identity mismatch, else
  flatter photo / back photo).
- Community report line with consent checkbox; checking it only shows
  "Held for review in this local demo only — nothing sent."
- Smooth fade + gentle slide on the result card, reduced-motion
  fallback, full-width buttons on small phones, check button disabled
  while a check runs, upload errors show as Inconclusive with a plain
  reason instead of a blank screen.
- Preview fallback: if the local server is not running, canned
  Test A/B still show their canned verdicts (labelled preview
  fallback, per-tell numbers need the server). Upload checks still
  need `server.py` locally.
Verified Oct 27 ~11:22 AM: `run_tests.py` PASS 2/2, local server
GET / 200, canned A Likely Genuine 5/5, canned B Inconclusive
identity mismatch, all new UI strings present in served HTML,
server stopped after smoke test.

## What is still missing before this could be shared with a few testers
Do NOT share this yet — owner review is required first, and per the
Oct 27 ~9:58 AM owner order, the Discord tester reply + link go out
together only after the owner reviews this demo build.
This polish is for review, NOT a public deploy and NOT a tester message.
1. Owner review of this build and its verdict wording.
2. A shareable host for it: this build binds localhost only. A tester
   link would need a separate, owner-approved deploy (not done here),
   and the current public demo link still serves the OLD version.
3. Quick-snap — NOT in V2 playground.
4. Little Office — NOT in V2 playground.
5. Top-bar fix — NOT verified in this demo (mobile nav bug list item
   is still pending on the real site/app).
6. Grade — NOT in V2 playground; no grade is ever guessed here.
7. Phone cropper as sole cropper — NOT shippable (see V2 README
   blockers; bad-aspect boxes are refused, not scored).
8. SAM escalation path for Real checks — recorded only, no live SAM
   call in this $0 build; a Real check needs an owner-approved paid
   SAM step outside this demo.
9. Full app source integration — absent from workspace; this demo is
   a playground build, NOT a merge into the full app source.
10. Tells calibration — thresholds are documented, not tuned on real
    genuine vs known-fake pairs of the same identity.
11. Back-photo scoring — front-only in V2; a disagreeing back would
    not be caught here.

## What was NOT done
No deploy, no Cloudflare Pages deploy, no public link, no Play
submission, no post, no message, no link sent to any tester or to
Discord, no spending, no key/token handling, no card-photo publishing.

## Agents 101 ideas A–D, built Oct 27, 2026 — playground only, $0
Checker (`app_check_v2.py`) now formalises the agent loop with per-step
progress, gates verdict filing on a proven checklist with tell-citing
findings, returns needs_input naming the exact missing evidence
(slab cert, back photo, well-formed identity, usable crop) instead of
guessing, and exposes a 6-row loop timeline. The demo UI renders that
timeline (Check timeline panel), a needs_input box, and a slabbed
checkbox that triggers the slab-cert needs_input path. Styles, live
camera, back scoring, and 10-idea elements are unchanged. Canned A/B
still PASS 2/2; server smoke: canned A filed Likely Genuine with a
6-row timeline, canned B Inconclusive.

## Games levels + demo rewards (Oct 27, 2026, demo only, $0)
- Tell or Tale?: Levels 1 (3 Qs), 2 (5 Qs), 3 (7 Qs), harder as levels rise; pass at 60%+ unlocks the next level; locked levels are disabled, not dead buttons.
- Bubble Beat: piano-key rhythm game, one beat pattern per level (L1 C E G E slow, L2 C D E F G F faster, L3 C E G A G E D C fastest), music on/off toggle, playable muted via the highlighted key. Music uses on-device synthesized tones, NOT verified on a real phone — the old tap-blips-only bug is not claimed fixed.
- Rewards (localStorage key cc_demo_rewards_v1, device only, never money/prizes): +10 coins per correct game answer, +50 coins per level completed, +1 star on first completion of a level, +20 coins per completed card check, +25 coins daily claim (once per day). No leaderboard in this demo — a live board needs real sign-in first.
- Other crew games remain honestly labelled "not in this demo yet" with no fake buttons. Checker/timeline untouched; canned test-a still Likely Genuine.

## Identity lookup — Oct 27, 2026 (playground only, $0)
Check screen now has "Find a real card — EN/JA index" (set + printed number,
optional name fallback, language filter). 37,369 identities searchable.
A hit shows name, set, number, language, rarity, HP, types, illustrator, and
whether a reference image exists. Only Alakazam|Base|1 and Charizard|Base|4 have
references; every other hit stays Inconclusive on a check, honestly, because
tells cannot be measured without a reference. No card images are loaded into
the demo, no card photos are used as backgrounds. Tests: ../app-v2-merged/test_identity_wiring.py.

## Reference expansion, batch 1 (Oct 27, 2026)
Demo now measures 10 identities, not 2: /api/lookup-stats reports measurable 10
(2 canned + 8 pilot batch refs), /api/lookup reports reference_status for batch
refs, and the lookup panel labels them "verified batch pilot, uncalibrated".
Searchable stays 37,369 EN/JA. Non-batch identities stay Inconclusive.
Plan: ../app-v2-merged/reference-expansion-plan-2026-10-27.md.

## Oct 27, 2026 — Scan quality gate + multi-reference (playground only, $0)
- Verdict screen meta line now shows scan quality (passed/failed) and reference mode/count.
- New endpoint GET /api/multi-reference?identity=Name|Set|Number returns count/mode only — no photo paths, no owner card photos served. Alakazam|Base|1 and Charizard|Base|4 each have 2 verified references (canned + TCGdex batch) = median mode; default demo check path is unchanged (single mode for canned tests).
