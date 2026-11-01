# AI loop keeper run — Sat Oct 31, 2026 ~3:16 PM ET

Job: ai-loop-keeper (every 6h until Nov 4, 2026 9:00 PM ET; still in window).
Mode: playground/local only, $0. No deploy, publish, post, send, train,
no Baseten / Meta Spark / SAM / Modal call. No new card verdict issued
(the only Likely Genuine in test output is the pre-existing canned
pipeline regression test, unchanged).

## Queue state checked first

- Last run (Oct 31 ~9:16 AM) was the builder form of Q22 (Audit #58):
  `playground/app-v2-merged/home_hero.js` + the standalone hero surface
  at `playground/home-hero-2026-10-31/index.html`, built under the Q22
  spec (one hero line, then the single primary action, no banner
  stack). Its named next step: "Latch exam of home_hero.js + the hero
  surface (examiner-only); only on PASS, merge into the live demo Home
  surface by the build lane, then owner phone test."
- That Latch exam is this run's work, examiner-only: no builder code
  edited (mtimes on home_hero.js / test file / hero index.html all
  still Oct 31 ~9:18 AM), no live build touched, no module changed
  by the examiner. Q23 (stance lines) was NOT built — one item at
  a time, and this run is Q22's exam, not a builder run.

## Worked: Q22 (Audit #58) — Latch exam of the Home hero module

Subject: `playground/app-v2-merged/home_hero.js`,
`playground/app-v2-merged/test_home_hero_2026-10-31.js`,
`playground/home-hero-2026-10-31/index.html`.

### Verification (all $0, local)
- Syntax: `node --check home_hero.js` OK.
- Builder tests re-run: `test_home_hero_2026-10-31.js` **9/9 PASS**
  (TB11 hero line verbatim, hero before primary, exactly one primary
  action, no banner element, banner stack / two primaries / empty
  hero all rejected, escaping, secondary entries as links).
- Regressions, all PASS / exit 0: tonight-batch tests (incl. Q22 hero
  + Q23 stance checks, "FAILURES: none"),
  `test_identity_exact_set_2026-10-28.py` (incl. checker loose "Base"
  = Inconclusive/needs_input), `test_why_measured_2026-10-28.py`.
  Checker logic untouched.
- Not-merged re-verified: 0 references to HomeHero/home_hero in the
  live retheme build's `index.html`
  (`playground/retheme-build-2026-10-29/index.html`) and in
  `app_check_v2.py`. No network primitives and no alert in the module
  or the surface page.
- HTTP smoke (local static server, stopped after, port verified
  free): hero page 200 (2,143 B), home_hero.js 200 (5,152 B);
  "Playground only" label present on the page — matches the builder
  run's sizes exactly.

### Examiner probes (own script in /tmp, builder files unmodified) — 18/19 PASS
- Fail-closed, probed beyond the builder tests: banners as a
  non-array rejected and renders error-only; empty banners array is
  the only banner shape that passes; zero primary actions, a primary
  with an empty label, and a non-array primaryActions all rejected;
  config shapes null / array / string / number all render only the
  honest error line, never a partial hero.
- Escaping probed in attributes as well as text: a custom primary's
  id/target carrying quotes (`a"b`, `x" onmouseover="y`) and a
  secondary entry's id/target carrying quotes render escaped — no
  attribute breakout, no injected handler, primary count stays 1.
- Secondary discipline: non-array secondary, a secondary entry with
  no label, and a null entry all fail closed; a secondary LABEL whose
  text is "banner sale" still renders as a plain link only — no
  banner element, no second primary.
- Order invariant holds with secondary entries present: hero line
  before the primary button before the secondary nav, exactly one
  `<h1>`. Module exports are exactly the five documented keys
  (HERO_LINE / PRIMARY_ACTION / escapeHtml / validateHomeConfig /
  renderHomeHeroHtml) — the module creates no verdict, price, or
  account field.

### Non-blocking observation (trusted-host-code reachability only)
- Probe 19 FAILED, reported as-is: `validateHomeConfig({})` returns
  the module's own PRIMARY_ACTION object by reference, so host code
  that mutates the returned `primary.label` (or mutates the exported
  `HomeHero.PRIMARY_ACTION` directly) changes what a later
  `renderHomeHeroHtml()` renders (verified in fresh processes:
  label rendered "HACKED" / direct-export mutation also took).
  This is NOT reachable by user, stored, or network data: the hero
  surface's only feed is the page's own literal config, and any code
  able to mutate the module object is the host's own trusted script,
  which could rewrite the DOM directly anyway. No banner, second
  primary, verdict, or extra field can be smuggled in through it.
  Recommended (non-blocking) builder hardening for a future pass:
  return a copy of the primary in validateHomeConfig and freeze
  PRIMARY_ACTION. Merge invariant: the host surface renders via
  renderHomeHeroHtml with a literal config and never mutates the
  module's exports or a validate result.

### Latch verdict
- **PASS — cleared for merge by the build lane, under the invariant
  above.** The Q22 spec holds under builder tests, hostile-config
  examiner probes, and the served-page smoke: one TB11 hero line
  first, exactly one primary action (Check a card), no banner can
  render above the hero through this module, every rendered value
  is escaped in text and attributes, and invalid configs fail
  closed to an honest error line.
- **Q22 stays P.** Remaining gates, in order: (1) merge into the
  live demo Home surface by the build lane (NOT this loop — the
  loop is playground-only / no-deploy), keeping the invariant
  (one hero line, one primary action, no banners above the hero;
  no mutation of module exports), (2) owner phone test (hero
  wording sighting + no banner stack on a real phone).

## Cost / blocker for Sabastian
- Cost: $0. Blocker: none for Sabastian — no decision or spend needed.
- Reportable under the job's rule as a completed queue step (Latch
  exam PASS of the Q22 Home hero, clearing the previously reported
  builder form for merge by the build lane), not as a completed
  queue item: Q22 is not done.
