# V3 vs V3.1 — Comparison — DRAFT ONLY, Oct 27, 2026

**Status: DRAFT ONLY. Neither V3 nor V3.1 is installed on penguin.
Neither replaces V1 or V2. Both are audit/report only in this draft:
no auto-editing, no auto-restarting, no publishing.**

Owner order: Oct 27, 00:35 ET — make a V3 and a V3.1, one to watch
over V1 and one to watch over V2, instead of a single V3 watching both.
This file is the comparison the owner asked for implicitly in that
split: what each watcher watches, what each adds, and where they
deliberately do NOT overlap.

Files in this folder:
- `v3-spec.md` — V3 spec (watcher for V1)
- `v3.1-spec.md` — V3.1 spec (watcher for V2)
- `v3-watch-v1-draft.sh` — V3 draft script, header DRAFT-NOT-INSTALLED
- `v3-1-watch-v2-draft.sh` — V3.1 draft script, header DRAFT-NOT-INSTALLED
- `v3-vs-v3.1.md` — this file

## Comparison table

| | V3 — watcher for V1 | V3.1 — watcher for V2 |
|---|---|---|
| **Watches** | V1 (`~/bridge-watch-loop.sh`, PID 1640 at last check) | V2 (`~/bridge-watch-v2.sh`, PID 29431 at last check) |
| **Focus** | Bridge: is V1 alive, fresh, and telling the truth about bridge-adjacent services? | Host health: are V2's vitals complete, fresh, trending, and honest? |
| **Primary input** | V1's lines in `~/bridge-watch.log`, V1 process state | V2's `~/bridge-watch-vitals.jsonl` lines, V2 process state, V2's log lines |
| **Own output** | `~/watchdog-v3.log` + `~/watchdog-v3-history.jsonl` (proposed paths, not live) | `~/watchdog-v3-1.log` + `~/watchdog-v3-1-history.jsonl` (proposed paths, not live) |
| **Tick** | 300 s, matching V1 | 300 s, matching V2 |
| **Single-instance** | Own flock `/tmp/watchdog-v3.lock` | Own flock `/tmp/watchdog-v3-1.lock` |
| **Log rotation** | Own log + history at 5 MB | Own log + history at 5 MB |
| **Memory / load** | Adds its own vitals + trend (V1 has none) | Validates + re-derives V2's vitals, adds trend V2 lacks |
| **Trend rule** | 3 ticks falling ≥200 MB each = TREND-WARNING, report only | Same rule, report only |
| **Absolute memory states** | ≥500 OK, 300–499 WARNING, <300 CRITICAL, report only | Same, re-derived from vitals, report only |
| **Journal / vshd scan** | **Yes — core feature.** Last-5-min counts only: vshd broken-pipe/error/fail, tailscaled error/disconnect, OOM, hung task, USB disconnect. 3 ticks vshd > 0 = BRIDGE-DISTRESS (owner action, never "fixed"). | **No — deliberately not duplicated.** Records only `JOURNAL-NOT-IN-VITALS` as a known V2 gap. Journal scanning is V3's bridge job; duplicating it in V3.1 would blur the split. |
| **Mount checks** | Corrected paths, read-only, + stale-path audit of V1's `/mnt/cloud-master` and `/mnt/ssd-238`. Rate-limited repeat STILL DOWN reporting (once/hour with count). | Corrected paths, read-only, as **missing-check probes**: reports `V2-MISSING-CHECK mounts` + probe result. Does not mount. |
| **Tunnel check** | Read-only probe vs V1's last tunnel line; `V1-STALE` / `V1-MISMATCH` if stale or disagreeing. Never runs start-tunnel.sh. | Read-only probe as **missing-check probe**: reports `V2-MISSING-CHECK tunnel` + probe result. Never runs start-tunnel.sh. Does not decide tunnel home. |
| **Cloud-serve :8080** | Read-only probe vs V1's last cloud-serve line; `V1-STALE` / `V1-MISMATCH`. | Read-only probe as **missing-check probe**: reports `V2-MISSING-CHECK cloud-serve` + probe result. |
| **Tailscale** | V1's tailscale line age + independent read-only probe; mismatch reported. | V2's tailscaled state from vitals, re-derived; restart-line counting (see below). |
| **Restart-rate counter** | Reports V1's header claim-vs-code gap (claims max 3/hr, no counter in code). Does not count V1 restarts as its tick job — that counting is V3.1's pattern for V2, cross-referenced by the AI Loop audit. | **Implements the counter as an audit counter.** Counts V2 restart lines per hour; >3 = `RESTART-RATE-VIOLATION`, reported, **not enforced** in this draft. Gating block is commented out. Future non-audit build could gate; that needs its own owner yes. Alternative: remove the claim from V2's header — owner picks, V3.1 does not edit. |
| **<300 MB pause claim** | Reports V2's claim only by cross-reference; V3's own <300 MB state is report-only, no shed. | **Audits the claim directly:** below 300 MB with no shed record = `V2-CLAIM-UNIMPLEMENTED pause-below-300MB`. Shed order is a proposal, not performed. |
| **Claim-vs-code gaps reported** | V1: stale mount paths, mount fix = `true` (no-op), max-3/hr claim with no counter, no memory/load/journal/vitals/flock/log-cap. | V2: header claims tunnel/cloud-serve it does not check; max-3/hr claim with no counter; <300 MB pause claim with no shed; vitals have no sequence number (`VITALS-NO-SEQUENCE`, gaps measured by timestamp). |
| **Shared-log handling** | Stats `~/bridge-watch.log`, reports size >5 MB as `LOG-CAP-WARNING` and V1/V2 line counts. Writes to its **own** log, never the shared log. Does not rotate/truncate the shared log in this draft. | Same principle: writes to its **own** log, never the shared log. Does not rotate/truncate V2's files in this draft. |
| **What it NEVER does** | Edit/kill/restart/start V1, V2, or any service; mount/remount/format/dd/delete; rotate tokens; alert on routine recovery; claim a bridge wedge is fixed. | Edit/kill/restart/start V2, V1, or any service; mount/remount/format/dd/delete; rotate tokens; alert on routine recovery; claim V2 is healthy because vitals are well-formed. |
| **Mock mode** | `WATCHDOG_V3_MOCK=1`, `WATCHDOG_V3_MOCK_DIR`; one tick, then exit, for inspection. | `WATCHDOG_V3_1_MOCK=1`, `WATCHDOG_V3_1_MOCK_DIR`; one tick, then exit, for inspection. |
| **Mock tests** | v3-spec.md §6 (7 tests: stale V1, stale-path noise, mismatch, trend, journal distress, log cap, mock isolation). | v3.1-spec.md §6 (8 tests: stale V2, malformed vitals, claim-gap, restart-rate, missing-check probes, below-300, trend+gap, mock isolation). |
| **Design target** | Current Crostini guest (where vshd is the main failure). | V2 as written, which targets the future full-Linux host — V3.1 audits V2 on the current guest without pretending V2's design target has changed. |

## Key difference, in one paragraph

**V3 asks: "Is V1 telling the truth about the bridge?"**
**V3.1 asks: "Is V2 telling the truth about the host?"**

V3 is outward-facing (bridge, tunnel, cloud-serve, mounts, journal
distress) because V1's job is bridge coverage and V1's blindness is
everything numeric and predictive. V3.1 is inward-facing (vitals
validity, freshness, trend, claim honesty, restart counting) because
V2's job is host-health numbers and V2's blindness is everything
bridge-adjacent plus its own unimplemented claims. A single V3
watching both would have to do both jobs in one tick, with one
report, and a failure in one half would hide in the other half's
OK lines — the exact false-healthy pattern the AI Loop audit
warned about. Two watchers, two reports, one comparison (this
file, plus the AI Loop audit) is the owner's split, and it is
the right split for exactly that reason.

## What V3 and V3.1 share (and why that is not duplication)

- 300-second ticks, `set -u`, own flock, own log/history at
  5 MB rotation, fix-not-alert, never delete / never rotate /
  never guess a device name, drive identity by share name (never
  sd letter), trend rule (3 × ≥200 MB fall = TREND-WARNING),
  memory states (500/300 MB), mock mode with one-tick exit.
- Shared runtime shape is intentional: one tick pattern, two
  different audit subjects. The shared shape makes the two
  reports comparable (same timestamps, same trend rule, same
  rotation), while the audit subjects stay separate.
- Deliberate non-overlap: only V3 scans the journal; only
  V3.1 counts V2 restarts and audits the pause claim. If a
  future build merges them, it must say so explicitly and
  re-prove both mock suites — it must not silently merge by
  copying one script into the other.

## AI Loop oversight of V3/V3.1

**Owner update, Oct 27, 00:35 ET — this section is the top
layer of the design, and it replaces any reading of the old
§7 as "the AI Loop reads the reports." The AI Loop watches
over the PROCESS of V3 and V3.1, not just their output.**

### The full chain

1. V1 watches the bridge/host services (Crostini guest).
2. V2 watches host health (numbers, vitals).
3. V3 watches V1. V3.1 watches V2.
4. **The AI Loop watches over the processes of V3 and
   V3.1** — their specs, their tick logs once live, their
   upgrade proposals, and their compliance with the hard
   rules below.
5. **The owner is the final gate.** The owner reads the AI
   Loop's audit and the V3/V3.1 reports on status checks,
   and approves or rejects each proposed addition one by
   one. No one else approves.

There is **no V4**. See "Why NOT a V4" below for why the
chain stops here.

### What "watches over the process" means (not just output)

Reading V3/V3.1 tick lines and saying "they look OK" is
output review. Process oversight is wider, and the AI Loop
audit must check all of it, for each watcher separately:

1. **Spec audit — does the watcher do what its spec says?**
   Compare `v3-spec.md` / `v3.1-spec.md` against the draft
   scripts and, once live, against actual behaviour. Spec
   drift is a finding: a watcher that starts doing something
   its spec does not say, or stops doing something its spec
   promises, fails the audit even if its tick lines look
   healthy. Example: V3.1 silently activating its
   commented-out restart-gating block would be spec drift
   and a failed audit, not an improvement.
2. **Tick-log audit — are the watchers alive, fresh, and
   complete?** For V3: last tick age, V1-STALE / V1-MISSING
   states, TREND-WARNING / CRITICAL states, BRIDGE-DISTRESS
   patterns, shared-log cap warnings. For V3.1: last vitals
   age, V2-STALE / V2-MISSING states, VITALS-MALFORMED lines,
   TREND-WARNING / CRITICAL states, RESTART-RATE-VIOLATION
   counts, V2-CLAIM-GAP / V2-CLAIM-UNIMPLEMENTED lines. A
   watcher whose history stops advancing while its subject
   keeps ticking is itself stale, and that staleness is a
   finding, not a blank in the report.
3. **Upgrade-proposal audit — are proposals honest and
   gated?** Every upgrade V3 or V3.1 proposes must be
   marked NEEDS-OWNER-YES, must state what it changes, what
   test proves it (mock first), and what rule it touches.
   A proposal that would break audit-only, fix-not-alert,
   never-delete, or never-rotate-tokens must be flagged as
   a rule-breaking proposal, not passed through as a routine
   upgrade. A proposal that re-words a claim to hide a gap
   (e.g. quietly dropping the tunnel claim from V2's header
   instead of adding the check or correcting the header
   openly) is a failed audit.
4. **Compliance audit — did the watchers stay audit-only in
   fact?** Check, from logs and file timestamps, that
   neither watcher edited V1 or V2, killed or restarted any
   watchdog or service, mounted or remounted anything,
   deleted anything, rotated any token, or put any secret
   in any log, vitals, history, or report line. A watcher
   that acted while claiming to audit has broken the rule
   that justifies its existence, regardless of whether the
   action "worked."
5. **Gap reporting — what is still missing?** The AI Loop
   reports, per watcher, which checks are still missing
   (V3: is journal distress still unproven? V3.1: are
   tunnel/cloud-serve still probe-only, not V2 checks?),
   which claim-vs-code gaps are still open, and which
   owner decisions are still owed. A gap that is reported
   every audit and never acted on is itself escalated (see
   below) — it is not allowed to become permanent noise
   like V1's STILL DOWN storm.

### Audit cadence

- **After the next 20 ticks of each watcher** (i.e. after
  ~100 minutes of ticking at 300-second ticks, once live),
  and after every subsequent 20 ticks: a full process audit
  covering items 1–5 above, for V3 and V3.1 separately, in
  one audit file with a per-watcher section. This cadence
  is proposed, not auto-set — it takes effect when the
  owner approves the first install, and it is audit-only
  (it does not start, stop, or edit anything by itself).
- **After any FAIL / WARNING / CRITICAL state**, in
  either watcher or either subject: an event audit, in
  addition to the 20-tick cadence, covering the event
  window (the ticks before, during, and after the state),
  whether the watcher reported it correctly, and whether
  any rule was broken in response. Trigger states include,
  at minimum: V1-STALE, V2-STALE, V1-MISSING, V2-MISSING,
  BRIDGE-DISTRESS, TREND-WARNING, CRITICAL (memory),
  RESTART-RATE-VIOLATION, VITALS-MALFORMED, V2-CLAIM-GAP,
  V2-CLAIM-UNIMPLEMENTED, LOG-CAP-WARNING, and any
  tailscale / tunnel / cloud-serve FAIL in V1 or V2.
- **Before any install or upgrade:** a spec audit of the
  exact draft file(s) to be installed, plus mock-test
  results and a Latch/Nickel review. No install audit is
  skipped because a previous audit passed — each exact
  file gets its own audit.
- **Draft phase (now):** the AI Loop audits the drafts
  themselves — these specs and scripts — against the prior
  research and the V2 audit, for spec drift, claim honesty,
  and rule compliance, before either draft is installed.
  That draft-phase audit is part of this same oversight
  layer, not a separate one.

### What the AI Loop escalates vs what it just logs

**Escalate to the owner (in the next status report, as a
named item requiring a decision — not as a silent log line,
and not as an alert that re-enables alerts):**
- Any compliance break: a watcher edited, restarted,
  mounted, deleted, rotated, or leaked a secret; a
  commented-out acting block was activated without owner
  approval; a spec was drifted from without an approved
  change.
- Any watcher staleness: V3 or V3.1 stops ticking while its
  subject keeps ticking, or stops ticking while SSH is up.
- Any BRIDGE-DISTRESS pattern, CRITICAL memory state, or
  RESTART-RATE-VIOLATION — with the window, the counts,
  and the owner's host-side options (restart Linux, then
  Chromebook, then fresh port), never with a claim that
  the guest fixed it.
- Any claim-vs-code gap that has survived two consecutive
  audits unaddressed (e.g. V2's tunnel/cloud-serve header
  claim, the max-3/hour counter, the <300 MB pause claim).
  Two audits of silence turn a logged gap into an
  escalated decision: correct the claim, add the check, or
  remove the claim — picked by the owner, not by the
  watcher or the auditor.
- Any upgrade proposal that would break audit-only,
  fix-not-alert, never-delete, or never-rotate-tokens, or
  that would turn an audit watcher into an acting watcher
  without a separate owner yes for that acting behaviour.

**Just log (in the audit file, for the next 20-tick review,
not escalated as a decision item):**
- Routine OK ticks, routine WARNING states that clear on
  the next tick, and routine trend warnings that do not
  reach CRITICAL and do not repeat across audits.
- Single-tick mismatches (V1-MISMATCH / V2-MISMATCH) that
  resolve on the next tick, with both timestamps recorded.
- Repeat STILL DOWN / repeat claim-gap lines with no state
  change, counted once per audit window, not once per tick
  — the same rate-limiting discipline V3 applies to V1's
  STILL DOWN storm, applied to the audit itself.
- Vitals gaps measured by timestamp (VITALS-NO-SEQUENCE)
  that are shorter than one audit window and do not recur.
- Proposals that are correctly marked NEEDS-OWNER-YES and
  break no rule: logged as pending proposals, not escalated
  until the owner asks for a proposal review or the
  proposal has waited through two audits (at which point
  it escalates as a stale proposal, per the two-audit rule
  above).

**What the AI Loop NEVER does in this layer:**
- Auto-edit V3 or V3.1, or their specs.
- Restart, start, or stop V3, V3.1, V1, V2, or any service.
- Approve its own upgrades, or approve an upgrade V3/V3.1
  proposed. Owner approval remains the final gate, for
  every change to a watcher and for every upgrade a watcher
  proposes to its subject.
- Re-enable owner alerts, rotate a token, delete data, or
  claim a bridge wedge is fixed. Fix-not-alert stands
  unless the owner re-enables alerts as a separate decision.

## 7. Who watches V3 and V3.1 — why NOT a V4

**Answer: the AI Loop audit + owner review, as specified
in "AI Loop oversight of V3/V3.1" above. NOT a V4.**

The chain, as it stands after this draft:
1. V1 watches the bridge/host services (Crostini guest).
2. V2 watches host health (numbers, vitals).
3. V3 watches V1. V3.1 watches V2.
4. The AI Loop (audit-only, Latch-style: read, check, report,
   edit nothing) watches V3 and V3.1.
5. The owner reads the AI Loop's audit and the V3/V3.1 reports
   on status checks, and approves or rejects each proposed
   addition one by one.

Step 4 is not a ticking watchdog, and that is the point. A V4
would be another ticking script, which would need a V5 to watch
it, which would need a V6, and so on — an infinite regress
that proves nothing, because a ticking script cannot judge
whether its own report is being acted on. The AI Loop audit
can, because it is periodic, not continuous: it runs after
20 ticks of each watcher, and after any V1-STALE /
V2-STALE / BRIDGE-DISTRESS / TREND-WARNING / CRITICAL /
RESTART-RATE-VIOLATION, under the same hard rules as the
prior audit (read-only, edit nothing, propose only, every
addition NEEDS-OWNER-YES). The owner is the final level,
because only the owner can do the host-side actions (restart
Linux, restart Chromebook, fresh port, tunnel-home decision,
firmware/migration decisions) that no guest script can do.

Failure mode if V3/V3.1 themselves go stale: the AI Loop
audit notices their reports stop advancing (no new V3/V3.1
history lines while V1/V2 keep ticking, or no new lines at
all while SSH is up), and the Muse-side ping check notices
the same staleness in its state file. That staleness is
reported, not auto-fixed by a V4, because auto-restarting a
watcher-of-a-watcher without a human reading why it died
would hide the very failure the watcher exists to surface.

In short: the chain stops at a human plus a periodic
examiner, because a report that no one reads is the failure
mode, and another daemon does not fix unread reports.

## What still needs owner approval before EITHER is installed

Applies to both V3 and V3.1, item by item — approval of one
is not approval of the other:

1. **The exact draft files**, after their mock suites pass
   and a Latch/Nickel review passes: `v3-watch-v1-draft.sh`
   and `v3-1-watch-v2-draft.sh`, separately.
2. **Own log/history paths and rotation sizes** (proposed:
   `~/watchdog-v3.log`, `~/watchdog-v3-history.jsonl`,
   `~/watchdog-v3-1.log`, `~/watchdog-v3-1-history.jsonl`,
   all at 5 MB) — proposed, not approved, not live.
3. **Corrected mount share names**, re-confirmed at install
   time (share names can change; neither watcher asserts a
   stale name).
4. **Claim resolutions, picked by the owner, not by the
   watchers:** (a) V2 tunnel/cloud-serve header claim —
   correct the header, or add the checks; (b) max-3/hour
   claim — enforce with V3.1's counter in a future non-audit
   build, or remove the claim; (c) <300 MB pause claim —
   implement the shed order, or change the log line to
   warning-only.
5. **Shared-log rotation** for `~/bridge-watch.log` —
   proposed as a future action, not approved, not done.
6. **Tunnel-home decision**, if either watcher is ever to do
   more than report tunnel state (neither decides it here).
7. **Install order:** each watcher starts while its subject
   keeps running (V3 while V1 runs, V3.1 while V2 runs).
   Neither subject is stopped to "make room" for its watcher.
8. **Future non-audit build, if ever wanted:** any version
   of V3/V3.1 that restarts, sheds, mounts, or edits anything
   needs a fresh, separate owner yes naming that exact
   behaviour — this audit draft's approval, if given, does
   NOT carry over to an acting version.
9. **Audit cadence** (proposed, not auto-set): AI Loop
   re-audit after 20 ticks of each watcher, and after any
   STALE / DISTRESS / WARNING / CRITICAL / VIOLATION state.
