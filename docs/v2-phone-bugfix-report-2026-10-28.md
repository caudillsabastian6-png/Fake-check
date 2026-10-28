# V2 demo + main site phone bug-fix report — overnight, playground only
**Date:** 2026-10-28, overnight while owner asleep
**Scope:** Playground only. NOTHING was pushed to GitHub, Cloudflare, or any live site.
No send, post, spend, or deletion. Live files verified untouched at the end.
**Live site state at report time:** cardcauldrontcg.com/demo/ is still the old
V2 build (no dock/checker/profile/scroll fixes from this report are live yet).

## Summary — read this first in the morning
Two code bugs, not one, explain most of what the owner saw on his Moto phone:

1. **Profile temporal-dead-zone (TDZ) on load — CONFIRMED in code, PROVEN in a
   reduced Node reproduction.** In the old file, `renderRewards();
   renderTellLevels(); renderBb();` ran at line ~910, but `let profile` was
   not declared until line ~958. Those renders call
   `renderGameAvatars() -> avatarStr() -> profile`, so the first render
   throws `ReferenceError: Cannot access 'profile' before initialization`,
   script execution stops there, `bbKeys` / `bbLevels` / `tellLevels` are
   never populated, and the bottom init (`buildAvatarPicker();
   showScreen('home')`, old lines ~1025-1026) never runs.
2. **Home scroll sections were OUTSIDE `#screen-home` — CONFIRMED in code.**
   The five scroll cards (Our story, Checker, Index, Games, Help us test it)
   sat after the closing `</div>` of `#screen-home`, so `showScreen()` —
   which only hides `.screen` elements — never hid them. Tapping Games,
   Settings, Check, etc. unhid the target screen *below* those always-visible
   cards, below the fold. On a phone the visible screen stayed on
   "Our story", so it looked like nothing happened. This matches the
   parent's desktop browser repro exactly: buttons registered, no error,
   target appeared below the home sections, Explore (home) did change the
   visible screen, and the fixed dock covered bottom content.
   Desktop Chromium taps "worked" because the desktop agent scrolled / saw
   headings; the phone user, at the top of the page, did not.

Both are fixed in the playground file below. **Neither is claimed fixed on
a phone yet** — a full-page browser test and an owner phone retest are
still owed before any live push (see "Still needs retest").

---

## 1. Navigation — dock, top bubble, home buttons not switching on phone
- **What was verified:**
  - Old playground file: `showScreen()` itself is sound (hides all `.screen`,
    unhides `screen-<name>`, toggles nav, `scrollTop()`), and extracted
    script passes `node --check`.
  - Old file: scroll-section cards were outside `#screen-home`
    (old lines ~155-158, after home's closing div, before `#screen-picker`).
  - Old file: bottom init never ran if the line-910 render threw (see §2).
  - Parent desktop test (00:14 AM ET, taps only): Games, Settings, Check
    all "worked" on desktop Chromium. That does NOT contradict the phone
    report — it is consistent with a below-the-fold target + a phone user
    who stays at the top, plus a fixed dock covering lower content.
  - Games screen DID load once on the phone (screenshot 537, dock Games
    highlighted), so this was partial/intermittent in the owner's words,
    not a total failure. That also fits: `showScreen('games')` does not
    itself touch `profile`, so it can work even after the TDZ throw, while
    Settings (which calls profile code) and the initial home render cannot.
- **What was changed (playground only):**
  - `~/workspace/fake-check/playground/app-v2-demo/index.html`
    - Scroll-section cards moved INSIDE `#screen-home`: now lines 164-168,
      inside the home div that opens at line 135 and closes at line 169,
      before `#screen-picker` (line 171). Now `showScreen('games')` etc.
      hide home *and* its scroll cards, so the target screen is at the top.
    - Profile moved before first render (see §2), so bottom init can run
      and `showScreen('home')` actually unhides home on load.
  - No verdict, price, or demo-only label was changed.
- **What was tested:**
  - `node --check` on the extracted script: PASS (after edits).
  - Structural grep checks: all five scroll cards are inside the home block;
    profile line (914) is before first render line (917); dock has 11 buttons.
  - Reduced Node TDZ reproduction: old order throws ReferenceError;
    new order runs and returns the avatar. See §2.
  - A local headless-Chromium `--dump-dom` attempt on a local copy was
    NOT completed (video/virtual-time run hung; the run was killed, no
    result used). **Full-page navigation was therefore NOT browser-verified
    by this subagent.** A live-browser test by the parent is required.
- **Still needs owner phone retest:** Open cardcauldrontcg.com/demo/ *after*
  a live push of this playground file, tap Check, Games, Settings (dock
  and top bubble), Explore, Play the games, Customise my app, and confirm
  each replaces the visible screen at the top (not below Our story).

## 2. Bubble Beat — keys missing / "It don't work"
- **What was verified:**
  - Screenshot 537: Games screen open, Bubble Beat card visible, Music on
    checked, Show the beat / Play this level visible, but NO piano keys
    between the "Your turn" text and Show the beat.
  - Code: `renderBb()` (old line ~735) sets `bbKeys` innerHTML from
    `BB_NOTES` (C D E F G A B) and `bbLevels` from levels 1-3, but it first
    calls `renderGameAvatars() -> avatarStr() -> profile`. With `profile`
    still in TDZ at the line-910 call, `renderBb()` throws before it ever
    reaches the `bbKeys` assignment. Later calls to `renderBb()` (level
    change, beat complete) hit the same throw, because the script had
    already aborted before `let profile` ever executed — so keys stay
    empty for the whole session. `bbShowPattern()` then flashes keys
    that do not exist (`if(!el) return` before tone/beat text), which
    matches "Show the beat does nothing, no keys to tap, no sound".
  - `bbTone()` itself is sound code (AudioContext oscillator, gated by
    the Music checkbox), but it is never reached when the key element
    is missing, and on a phone AudioContext also needs a user tap first.
- **What was changed (playground only):**
  - Same file, lines 914-917: `let profile = {...}` + saved-profile load
    moved to just before `renderRewards(); renderTellLevels(); renderBb();`.
    The old duplicate definition at ~958 was removed (only one
    `let profile=` remains, line 914).
  - Line 922: `avatarStr()` guarded with try/catch, returning '🫧' if
    profile is ever uninitialised, so a future reorder cannot blank
    the games again.
  - No beat patterns, tempos, levels, unlock rules, or coin rules changed.
- **What was tested:** Same as §1 — `node --check` PASS; reduced TDZ
  reproduction before (throws) / after (runs); structural checks.
  **Bubble Beat play itself was NOT browser-tested by this subagent.**
- **Still needs retest:** After live push, on the phone: Games → Bubble
  Beat keys C-G visible, Show the beat highlights keys in order,
  Play this level → tap keys in order works, Music on produces tones
  (tap-gated), Music off is visual only, Level 1 → 2 unlock at 60%+ /
  beat-complete rules unchanged.

## 3. Dock layout — lonely Settings on a third row
- **What was verified:** Playground change from the parent session is
  still in place. Dock now has **11 buttons**, lines 486-496:
  Check, Binders, Games, Plan, Explore, Tells, Light, Grade, Receipt,
  Camera, Help. `data-nav="settings"` is NOT in the dock.
  Settings remains reachable from the top Guest / Profile / Settings
  bubble and from the home "All screens" list.
- **What was changed in this session:** Nothing — verified only.
- **Still needs retest:** After live push, dock should show no lonely
  single button on a third row on a ~390px phone width (expected wrap
  6 + 5 with the current 16.666% flex basis, not 5 + 6 + 1).

## 4. Checker prominence — brighter, more defined checker card
- **What was verified:** CSS exists (twice, lines 31 and 48 — the later
  definition wins, so the brighter one applies) and the card markup
  exists at line 165:
  `.checker-hero` — 3px gold border, gold-tinted gradient, gold glow
  shadow; `.checker-tag` — gold pill "★ START HERE — THIS IS THE CHECKER";
  heading "🔍 The Checker — How a check works"; gold button
  "🔍 GO TO THE CHECKER — START A CHECK".
  The duplicate CSS block is harmless but untidy; it was left alone
  rather than risking an edit for cosmetics alone.
- **What was changed in this session:** Nothing — verified only.
  The checker card is now also inside `#screen-home` (line 165) as part
  of the §1 move, so it hides correctly when another screen opens.
- **Still needs retest:** After live push, on the phone the checker card
  should read as the obvious start-here hero, not a plain card.

## 5. Main site homepage — top banner hiding bubbles, hero cards long/stretched
- **Source reviewed (NOT edited):**
  `~/workspace/fake-check/playground/live-push-2026-10-27/index.html`
  (live-push copy timestamps unchanged, `checker-hero` count 0 there —
  this session did not touch the live source).
- **What was verified / diagnosed (code only, NOT phone-verified):**
  - `.ref-banner` is `position:relative; z-index:60`, in flow ABOVE a
    `position:fixed; top:0; z-index:50` nav. On mobile the nav wraps to
    brand + store-btn + a full-width `.mnav` row, so banner + nav
    together are taller than the mobile hero `padding-top:8.6rem`.
    Hero content therefore starts under the fixed stack — consistent
    with "top banner hiding bubbles".
  - `.hero-bg img` is `height:118%; object-fit:cover;
    object-position:center 30%` — on a portrait phone a wide hero is
    cropped to a central slice.
  - `.flycard` imgs have width only (`clamp(84px,13vw,150px)`, mobile
    62px/54px) and no explicit `aspect-ratio`/`height` guard in the
    mobile query. In the playground copy alone the stretch was NOT
    reproduced (parallax JS only does `translate3d` Y), so the
    "long and stretched" appearance on the phone is NOT proven to be
    this rule alone — it may be live-build, parallax, or screenshot
    timing. The aspect-ratio guard below is therefore a proposal,
    not a proven fix.
- **What was changed:** NOTHING in the live-push source. A proposal
  file was written instead:
  `~/workspace/fake-check/playground/main-site-phone-fix-2026-10-28.css`
  — mobile hero padding-top 11.5rem, flycard `aspect-ratio:498/689;
  height:auto; object-fit:contain`, hero-bg height 100%.
- **Still needs:** Owner review of that snippet, apply to the main-site
  source only with his yes, then phone retest on cardcauldrontcg.com
  (not /demo): banner no longer covers hero bubbles, flycards keep
  card proportions, hero top content is fully below nav + banner.

## 6. Phone background characters — only fire, no cute characters
- **What was verified:**
  - Demo hero poster: `hero-poster.webp`, 2352×1008 (ratio 2.33).
    Video: 1440×608 (ratio 2.37), 10.0s.
  - Poster content (read directly): Mallow (mint cub) at left
    (~15-45% of width), Ember (fire drake) at right (~65-95%), golden
    cauldron + fire at centre (~50%).
  - Demo CSS: `.bg-layer video, .bg-layer img.hero-poster
    {width:100%; height:100%; object-fit:cover}` on a fixed full-viewport
    layer. On a 390×844 portrait phone, cover scales the 2.37-ratio art
    to fill height, showing only ~390 / (844×2.37) ≈ 19% of the width —
    the central cauldron/fire slice. Both characters are cropped out.
    That exactly matches the owner's report.
- **What was changed (playground demo only):**
  - Same demo file, line 90: `@media (max-width:640px){
    .bg-layer.hero-layer video, .bg-layer.hero-layer img.hero-poster
    {object-fit:contain; object-position:center top; background:#0b0908}}`
  - Trade-off, stated plainly: on a phone the full hero art (both
    characters) will now be visible, but as a top-anchored strip with
    dark background below, NOT as a full-screen fire background.
    A true portrait hero (new video/poster framed for portrait) would
    be needed to keep both characters AND a full-screen background
    on a phone; that asset does not exist in the playground and was
    not created here.
- **Still needs retest:** After live push, on the phone the demo hero
  should show Mallow and Ember, not fire alone. If the owner dislikes
  the letterboxed strip, the next step is a portrait hero asset, not
  reverting to cover.

## Files changed in this session (playground only)
- `~/workspace/fake-check/playground/app-v2-demo/index.html`
  - Profile moved to line 914, first renders at 917, `avatarStr` guard
    at 922, scroll sections moved inside `#screen-home` (lines 164-168),
    mobile hero `object-fit:contain` at line 90.
  - MD5 after edits: `6002c38eaa0a8cc857d74a39c3a261ca` (102K, 1033 lines).
  - `node --check` on extracted script: PASS.
- `~/workspace/fake-check/playground/main-site-phone-fix-2026-10-28.css`
  - Proposal only, 1.8K.
- `~/workspace/fake-check/playground/v2-phone-bugfix-report-2026-10-28.md`
  - This report.
- **NOT changed:** `live-push-2026-10-27/` (demo + main-site sources),
  GitHub, Cloudflare, any live URL, any verdict/price/label, any
  account, any other playground pack.

## What is NOT fixed / NOT verified — do not over-claim in the morning
- No full-page browser test of the fixed playground file passed in
  this session (subagent has no live-browser task; local headless
  `--dump-dom` run hung on the looping hero video and was killed).
  Parent must run a desktop + phone-width browser test of the
  playground file (Check, Games, Settings, Explore, Bubble Beat keys)
  BEFORE any live push.
- No owner phone retest has happened for any item above.
- Main-site stretch cause is not proven; its fix is a proposal only.
- Bubble Beat sound on a real phone is still unproven (AudioContext
  is tap-gated; keys/flash are the primary fix here).
- The duplicate `.checker-hero` CSS block (lines 31 and 48) was left
  in place; harmless, but could be tidied in a later cosmetic pass.

## Morning checklist for the parent (in order)
1. Browser-test the playground demo file: home hero visible on load,
   dock taps replace the visible screen at the top, Settings opens,
   Bubble Beat keys render and play, checker hero is prominent.
2. If that passes, push ONLY the demo file to the live Git route with
   owner review, then verify cardcauldrontcg.com/demo/ live.
3. Owner phone retest on /demo/ (nav + Bubble Beat + characters).
4. Separately, owner review of the main-site CSS proposal, then
   main-site phone retest on cardcauldrontcg.com (banner + flycards).
5. Only after phone retests pass, call any of these bugs "fixed".

---

## Addendum — second overnight session, 2026-10-28 ~00:46 AM ET
**Owner order at 00:46 AM ET: "Keep working on the app overnight the
website please." Scope stayed playground only. Nothing was pushed live,
nothing sent/posted/spent, nothing deleted. `live-push-2026-10-27/` was
not edited (its demo MD5 is still `d3b326958f482663fa14cf2a9c9989f2`).**

### New owner clue — "stays at home but the background changes"
At 00:44 AM ET the owner answered the nav question: tapping a button
stays at home, but the background changes. That is exactly what the OLD
code would do, and it strengthens — not weakens — the home-nesting
diagnosis: `showScreen()` always calls `setSectionBg()` (so the
background layer changes and the hero video pauses for non-hero
screens), while the old scroll cards, outside `#screen-home`, stayed
visible at the top and the target screen sat below them, below the
fold. Tap registered, background changed, visible content looked like
home. The fix for that is the home-nesting move verified below, and
the morning retest must check this exact symptom, not just "does the
button do something".

### Verification — all earlier playground fixes intact
Structural parse of `app-v2-demo/index.html` (after this session's
cleanup, 1,029 lines, 103,151 bytes):
- 13 screens; home opens line 132, next screen (picker) line 168.
- All 5 scroll sections are descendants of `#screen-home`:
  story 161, checker 162, index 163, games 164, close 165.
- Single `let profile` at line 911; first renders at line 914;
  `avatarStr()` try/catch guard at line 919. (The `profile={...}`
  reassignment at line ~1020 is inside `clearSession()`, after the
  declaration, and is not a second declaration.)
- Dock: 11 buttons (check, binders, games, plan, home, tells, light,
  grader, receipt, camera, help); no `settings` in the dock.
- Checker hero markup at line 162, with tag, gold heading, gold button.
- Mobile hero `object-fit:contain` at line 87.
- `showScreen()` still hides every `.screen` and calls
  `setSectionBg(screenToSection(name))`, then scrolls to top.
- Extracted-script `node --check`: PASS.
- Diff vs `live-push-2026-10-27/demo/index.html` contains only the
  known hunks (checker hero, mobile hero, scroll-card move, dock
  Settings removal, profile move, avatarStr guard). No verdict, price,
  tier, or demo-only label lines appear in the diff.

### Cleanup done in this session — duplicate checker CSS merged safely
The duplicate `.checker-hero` blocks (old lines 31 and 48) are now ONE
block at line 45, with `.checker-tag` at line 47 and the button rule
at line 48. The merge keeps the later block's border, gradient
(including the blue `.12` tail), shadow (`.45`), letter-spacing
(`.04em`), margin (`0 0 8px`) and button size (19px / 64px), plus the
earlier block's `.9rem` tag font-size, which the later block had
omitted. Computed appearance is therefore unchanged by the cleanup.
MD5 after cleanup: `a2197191806f31b51c664766d643389b` (was
`6002c38eaa0a8cc857d74a39c3a261ca` before this cleanup — the change
is the CSS merge only).

### Push-ready package (playground only, NOT pushed)
- `~/workspace/fake-check/playground/live-push-ready-2026-10-28/demo/index.html`
  — byte-identical copy of the cleaned playground file (MD5 above).
- `~/workspace/fake-check/playground/live-push-ready-2026-10-28/PUSH-CHECKLIST.md`
  — what changed, what was tested, what still needs a browser test and
  an owner phone retest, companion files that must already be live
  (hero-poster.webp, hero-video.mp4, icons, manifest, sw.js), and a
  cache warning: `sw.js` caches `index.html` under `ror-demo-v1` and
  was not changed, so a phone that still shows the old build after a
  push should be checked for service-worker cache before the fix is
  called failed.
- Main-site CSS (`main-site-phone-fix-2026-10-28.css`) remains a
  SEPARATE proposal and must NOT be pushed with the demo.

### Still NOT verified — do not over-claim
- No browser test of the fixed file has passed in either overnight
  session (this session, as a subagent, has no live-browser task).
  Parent browser test in the morning is still required before any push.
- No owner phone retest has happened. Bubble Beat sound on a real
  phone is still unproven. Main-site stretch cause is still unproven.
- Nothing in this addendum makes any bug "fixed on a phone" yet.

---

## Addendum 2 — PAUSED, 2026-10-28 ~00:49 AM ET (owner correction)
**Owner corrected at 00:49 AM ET: the ENTIRE website needs to roll
back, not just the demo. "Our website needs roll back none of it
works until we fix it. The website is completely broken right now."**
This supersedes the 00:47–00:48 AM demo-only plan.

**What this session did in response: PAUSED V2 push-ready work.**
- Nothing was pushed to GitHub, Cloudflare, or any live site, by
  either overnight session. The push-ready folder below stays
  playground only.
- The V2 fix is **NOT for tonight as live**. It remains for AFTER
  the rollback, to be browser-tested and re-pushed later.
- The live rollback itself (apex back to the old Cloudflare project)
  is the priority and is handled separately by the parent — it is
  NOT done by this session, which has no live-browser task and must
  not push anything.
- **Important distinction:** the demo-rollback folder prepared in
  this session (`demo-rollback-2026-10-28/`, Oct 24 Public Demo
  `demo/index.html` only) is a DEMO-only fallback. It is NOT the
  entire-website rollback. The entire-website rollback, per the
  parent's record, is moving the apex custom domain
  `cardcauldrontcg.com` from the new Cloudflare project back to the
  old Cloudflare project in the dashboard, without deleting the new
  project — because the GitHub site repo only contains the new site,
  a GitHub push is not the rollback route. Do not substitute the
  demo-only file for that whole-site rollback.
- Main-site CSS proposal (`main-site-phone-fix-2026-10-28.css`)
  remains a separate, unapplied proposal, and is also parked with
  the V2 work until after the rollback.

### Correction to the rollback identification (filesystem search completed)
The demo-rollback folder's source was first listed only as
`demo-deploy-v1/demo/index.html`, with a note that the original
`demo-website-v1` folder no longer existed. That note was wrong: a
completed filesystem search found
`~/workspace/cloudflare-pages/demo-website-v1/demo/index.html` intact,
229,086 bytes, MD5 `1ad0b980776c7349f774f2e3fbbea18a` — identical to
both the `demo-deploy-v1` copy and the rollback copy. The rollback
file's identity is therefore stronger, not weaker: it is the original
Oct 24 demo source itself, not just a surviving copy. Nothing else
in this report changes; the V2 work remains parked and nothing was
pushed.
