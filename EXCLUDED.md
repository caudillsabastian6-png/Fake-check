# GitHub pack — EXCLUDED
Everything below was deliberately left OUT of this staging pack, and why.
Nothing here was pushed, deleted, or moved — exclusions are staging decisions only.

## Pre-Oct 26, 2026 work — do not claim as hackathon work
- All of ~/workspace/fake-check/ outside the files in MANIFEST.md, except where a file
  is dated Oct 26–27 and listed there. In particular: the Oct 24–25 site/demo work,
  the original Real or Replica app idea, and any pre-hackathon code/docs.
  Reason: hackathon compliance — claim ONLY Oct 26–Nov 4 work, with dates.
- ~/workspace/cloudflare-pages/demo-website-v1/demo/index.html — the OLD public web demo
  (Oct 24). It is the live demo's source, not Oct 26–Nov 4 checker code, and it is
  already served separately. Do not overwrite the public demo with this pack.

## Workshop files — different repo, not Fake-check
- ~/workspace/fake-check/playground/legal-agent-workshop/ in full — loop.py,
  verify_memo.py, verify_checklist.py, and the whole Meta legal-agent-workshop clone.
  Reason: that is Meta's workshop repo, not Sabastian's Fake-check repo. Its Session 1+2
  changes are uncommitted locally in that clone. Pushing them to Fake-check would be
  wrong; pushing them upstream to Meta's repo would also be wrong without instruction.
  Owner decision needed if any workshop summary (not code) is ever wanted in Fake-check.

## Third-party code — jnaapakam
- ~/workspace/fake-check/playground/jnaapakam-audit/ and
  ~/workspace/fake-check/playground/jnaapakam-prototype/ in full.
  Reason: third-party open-source memory-server code, audited Oct 27 as Alpha with an
  MCP auth exemption and external-LLM egress. Not app code, not hackathon-built, and
  the prototype verdict was "does not help beyond what already exists." Never include
  third-party code in a submission repo without a separate owner decision and licence note.

## Potion playbooks — not app code (owner decision pending)
- ~/workspace/custom-skills/ in full, including real-or-replica-agents101 and the 12 new
  skills built Oct 27 (tell-calibration, back-pool-scoring, slab-cert-card-inside,
  identity-lookup, card-identification, phone-demo-test, demo-video-beats,
  hackathon-compliance, final-examiner-gate, listing-wave-publish,
  ebay-inbox-feedback-recovery, penguin-health).
  Reason: these are Potion's operating playbooks, not Real or Replica app code.
  They are useful and grounded, but the task instruction was to exclude them unless
  the owner later says otherwise. If the owner wants a "skills" folder in the public
  repo, that is a separate approval — do not add silently.

## Data that is too large, binary, cached, or non-portable
- ~/workspace/fake-check/sourcing/tcgdex-details/repo/ — 224–236 MB TCGdex cards-database
  TypeScript clone. Only the generated JSON/CSV/SUMMARY are included. The clone is
  upstream source, not hackathon output, and would bloat the repo.
- ~/workspace/fake-check/sourcing/en-tcgdex/ and ja-tcgdex-*/ image downloads — ~2.1 GB
  of TCGdex card images. Not included; the detail index (names/sets/numbers) is
  included instead. Image licensing/redistribution for a public repo needs its own check.
- __pycache__/ everywhere, playground/app-v2-demo/out/, v1-backup/ (old loop/crop code),
  and test binary cropped.png — caches, outputs, and superseded code. JSON test results
  are included; the PNG is not.
- All other ~/workspace/fake-check/playground/ experiments (agent-loop, watchdog, SAM
  implementation packs, bridge/dual-boot packs, etc.) — not in MANIFEST.md, not in scope
  for this pack, and several contain infrastructure notes that must not go public.

## Secrets / credentials / private material — never include, none found in the pack
- Any .env file, any populated .env value, any API key/token/password, any Tailscale
  tunnel token, any Tailscale IP (100.x), any email address, any phone number.
  Scan results are in SCAN-REPORT.md: zero hits for all of these in the pack.
  The one prior public push (Oct 27 ~1:14 AM) was flagged in memory as containing
  internal Tailscale IPs in bridge-pack/watchdog audit files — those files are NOT
  in this pack, and must not be re-added.

## Oct 28, 2026 refresh — deliberately NOT added
- ~/workspace/fake-check/playground/merged-demo-2026-10-28/ and
  ~/workspace/fake-check/playground/old-plus-2026-10-28/ single-file demos —
  playground phone builds, not the V2 demo category in this pack; merged demo was
  parked Oct 28 (owner: roll back to the old demo) and old-plus is playground-only,
  not live-verified. Do not add without a fresh owner decision.
- ~/workspace/fake-check/playground/old-look-v2-upgrades-merge-plan-2026-10-28.md —
  merge plan superseded the same day by the rollback decision; stale if published now.
- ~/workspace/fake-check/playground/app-v2-merged/ Oct 27 afternoon additions
  (agreement_guard.py, inline_classifier.py, sam_multiregion.py, snapclaim.py,
  preship_reviewer.py, quality_gate.py, fix_verification.py, identity_lookup.py,
  and their tests) — not in the pack's listed V2 checker file set; adding them is a
  scope change, not a refresh. Left out, not deleted.
- ~/workspace/fake-check/playground/agent-loop/agent_loop_v2.py (Oct 27 21:16) —
  a different, larger loop file, not the app-v2-merged checker loop already in the
  pack (identical hash, unchanged). Not swapped in.

## Ambiguous — needs owner decision, NOT included
- checker/meta_pipeline.py — INCLUDED in this pack with a qualification (see MANIFEST.md):
  it references Muse surrogate connectors but contains no secret values. If the owner
  wants a fully standalone public repo, drop this file before push.
- data/databases/backs-pool-2026-10-27.csv source_path column — INCLUDED as-is with a
  qualification: it points to workspace paths for photos that are not in the pack.
  Owner decision: strip source_path to filename only before push, or accept as-is.
- Any file whose date or hackathon qualification could not be confirmed from its
  filename/mtime/content was left out rather than included. When in doubt, this pack
  excluded it.

## Oct 28, 2026 afternoon refresh — deliberately NOT added
- playground/backend-matcher-2026-10-28/__pycache__/ and
  playground/backend-tie-impl-2026-10-28/uploads/ (empty) — cache / empty output dir.
- Other Oct 28 playground work not named in the afternoon extra-push trigger
  (e.g. condition-grading-guide-2026-10-28.md, verifiable-agent-card-translation,
  ground-truth-from-hand-photos, camera fixes, site pages) — left playground-only
  for this run; not deleted, not pushed. Adding them is a separate scope decision.
- demo/index.html re-refresh — source file absent from playground/app-v2-demo/
  at refresh time; morning-pushed copy left untouched rather than re-sourced.
- The GitHub sweep report's evaluated third-party repos themselves — only the
  evaluation report is included; no third-party code was copied in.

## Oct 29, 2026 refresh — deliberately NOT added
- playground/tonight-labelling-2026-10-29/ intermediates: labelled_dataset_v2.csv
  (superseded by v3), scan_inventory.csv, rename_pilot_mapping.csv,
  set_fill_results.csv, set_fill_pending_results.csv — working intermediates,
  not the final dataset; the final v3 + code + progress ledger are included.
- playground/github-tests-2026-10-28/ code and .npz/.metadata files — third-party
  evaluation binaries/code; only its TEST-REPORT.md is included as a doc.
- playground/app-v2-merged/ other afternoon additions (identity_lookup.py,
  agreement_guard.py, inline_classifier.py, sam_multiregion.py, snapclaim.py,
  preship_reviewer.py, quality_gate.py, fix_verification.py, and their tests) —
  still a scope change, not a refresh of the pack's named file set; left out.
  The two back-pool crop helpers WERE added this run because the daily task
  names "crop helpers" explicitly.
- playground/agent-loop/ earlier keeper runs (Oct 28 0316/0916/1516) and
  agent_loop_v2.py (a different, larger loop file) — not added; only the two
  newest keeper reports since the Oct 28 afternoon push are included.
- All Oct 28 evening site/demo playground work (old-plus, site-chrome,
  avatar, rewards, chat-room, etc.) — not in this pack's categories
  (V2 checker / V2 demo / indexes / docs / tests for the checker).
- Back-pool crop PNGs in playground/back-pool-crops-2026-10-28/ — card photos,
  always excluded.

## Oct 29, 2026 daily refresh — deliberately NOT added
- playground/set-symbol-guide-2026-10-29/symbols/ — the 159 "symbol" files are
  295-byte HTML 404 stubs, not images; the guide's CSV/JSON carry the URLs instead.
- playground/tonight-labelling-2026-10-29/ new overnight intermediates:
  scan_label_batch*.py, scan_labels_batch*.csv, make_contact_batch*.py,
  scan_rename_mapping.csv (Oct 29 07:46), and all contact-sheets/ JPGs (card
  photos, always excluded). Dataset v3 is unchanged, so no new final dataset.
- Other Oct 29 morning playground folders (async-pipeline, recall-eval,
  judging-freeze, burn-down-plan, ideas-sweep, calder-training, model-probe,
  model-unlocks, digital-copies, meta-credit-burn, muse-image-pack, asset-batch,
  sam-precrop, wonder-holds, promo-x-draft) — separate experiments outside this
  pack's categories (V2 checker / V2 demo / indexes / checker docs+tests);
  left playground-only, adding them is a separate scope decision. Several
  contain card-photo crops and spend logs, which are excluded in any case.

## Oct 29, 2026 — standalone port: six modules now INCLUDED (owner-ratified)
Dated note, Oct 29, 2026 ~9:35 AM ET: the six checker modules that earlier
sections of this file record as left out by deliberate scope decision —
quality_gate.py, multi_reference.py, identity_lookup.py,
reference_registry.py, owner_scan_registry.py (playground/app-v2-merged/,
Oct 27–28) and on_device_crop.py (pip-ondevice-prototype/, Oct 26) — are now
INCLUDED in checker/, ported from the verified scratch copy
playground/standalone-fix-2026-10-29/pack-fixed/. The owner ratified this
scope change in chat Oct 29, 2026 ("Yes — port the fixes into the live
pack"), after the standalone setup test showed the pack could not measure
tells without them. The earlier "deliberately NOT added" / "still a scope
change" entries above are superseded for these six modules ONLY; the other
app-v2-merged afternoon additions named there (agreement_guard.py,
inline_classifier.py, sam_multiregion.py, snapclaim.py, preship_reviewer.py,
fix_verification.py, and their tests) remain excluded.
STILL EXCLUDED, unchanged by the port: the registries' data manifests
(verified_references_batch1.json, owner_scan_references.json — owner scan
data), ALL card photos and user photos (including demo/matcher fixture
photos), and every other exclusion in this file.

## Oct 29, 2026 — compressed EN details copy INCLUDED (API-route copy)
Dated note, Oct 29, 2026 ~9:48 AM ET: data/tcgdex-details/en-details.json.gz
is INCLUDED in the pack as the API-route copy of the TCGdex EN details index —
the plain en-details.json (5.79 MB) exceeds the GitHub push-files request
limit (HTTP 413) and is uploaded via the browser route tonight instead; the
.gz is not a replacement, both copies carry identical data (decompressed MD5
matches). checker/identity_lookup.py prefers the plain .json when present and
falls back to the compressed copy only when it is absent — .json.gz, or the
same gzip base64-encoded as text (en-details.json.gz.b64), which is the form
the UTF-8-only API push route carries; the raw .gz file itself goes up with
the plain .json on tonight's browser route.
