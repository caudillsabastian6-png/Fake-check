# V3 — Watcher for V1 (Bridge-Focused) — SPEC, DRAFT ONLY

**Status: DRAFT ONLY, Oct 27, 2026. NOT installed on penguin. NOT running.
NOT a replacement for V1. NOT a replacement for V2.**
Owner order: Oct 27, 00:35 ET — make a V3 and a V3.1, one to watch over V1
and one to watch over V2, instead of a single V3 watching both.

**Sources read first, not duplicated blindly:**
- `~/workspace/fake-check/watchdog-app-v3-research-2026-10-27.md`
  (prior V3 research — top-4 list, side-by-side evidence Oct 27, 00:31 ET)
- `~/workspace/fake-check/ai-loop-watchdog-v2-audit-2026-10-27.md`
  (AI Loop audit of V2 — claim-vs-code mismatches, stale-path finding)
- V1: `~/workspace/laptop-control/bridge-watch-loop.sh`
- V2: `~/workspace/fake-check/chromebook-setup-pack/bridge-watch-v2.sh`

## 1. What V3 is

V3 watches **V1 only**. V1 remains the Crostini bridge watchdog
(`~/bridge-watch-loop.sh`, PID 1640 at last check, 5-minute ticks).
V3 does not watch V2 — that is V3.1's job (see `v3.1-spec.md`).
V3 does not replace V1 in this draft. If V3 were a replacement, the
bridge checks V1 alone provides would have to be re-proven first, and
the AI Loop audit says plainly: do not replace V1 with V2 today, for
the same reason — do not replace V1 with V3 until V3 is proven.

V3 is a **meta-watcher**: it reads what V1 wrote and what V1 should
have seen, compares the two, and reports the difference. It is the
watchdog-of-V1, not a second bridge watchdog competing with V1.

## 2. What V1 does, and what V3 audits about it

| V1 check (as written) | V3 audit of that check |
|---|---|
| `tailscale status` probe; restart on probe failure | V3 records V1's last tailscale line and its age. V3 does NOT restart tailscaled. If V1 says OK but an independent read-only probe fails, V3 reports `V1-MISMATCH tailscale`. If V1 has no tailscale line in 15 minutes, V3 reports `V1-STALE`. |
| `cloud-master-mount`: `mountpoint -q /mnt/cloud-master`, fix = `true` | V3 flags this as **stale-path noise**. Those guest mountpoints are empty; real shares are under `/mnt/shared/removable/` (Cauldron, SSD, `potions fil`). V3 checks the corrected paths read-only (`test -d`, `stat`), and reports: V1's FAIL count in the last hour, corrected-path presence, and whether V1's FAIL lines are noise or a real absence. V3 never mounts, never remounts rw, never guesses a device name. |
| `ssd-mount`: `mountpoint -q /mnt/ssd-238`, fix = `true` | Same as above. V3 also rate-limits its own reporting: a repeated STILL DOWN with no state change is reported once per hour as `V1-REPEAT-STILL-DOWN`, with a count, not once per tick. This is the fix for V1's STILL DOWN storm — applied to V3's reporting, not by editing V1. |
| `cloud-serve-8080`: `curl -sf http://127.0.0.1:8080/`, fix = `true` | V3 does its own read-only curl probe and compares it to V1's last cloud-serve line. Mismatch (V1 OK / probe fails, or V1 FAIL / probe succeeds) is reported as `V1-MISMATCH cloud-serve`, with both timestamps. V3 does NOT start cloud-serve. |
| `tunnel-process`: `pgrep -f cloudflared`, fix = `~/start-tunnel.sh` | V3 does a read-only `pgrep -f cloudflared` and compares it to V1's last tunnel line. V3 does NOT run `start-tunnel.sh`, because starting a tunnel is a service action, and this draft is audit/report only. If V1's tunnel line is stale (>15 min) or mismatched, V3 reports it. Tunnel-home gating is preserved: V3 reports tunnel state wherever V1 reports it; V3 does not decide tunnel home. |
| `disk-space`: OK only if root use < 90% | V3 records the numeric disk % itself (`df /`), so a binary OK from V1 is never the only disk number. V3 never auto-deletes. |
| No memory/load check | V3 adds its own vitals: available MB (`free -m`), 1-min load (`/proc/loadavg`), disk %. See §3. |
| No journal/vshd scan | V3 adds a last-5-minute journal scan, counts only. See §3. |
| No vitals file, no flock, no log cap | V3 has its own vitals file, its own flock, and its own log rotation. See §5. Header claim in V1 of "max 3 restarts/hour" is **not** enforced by V1's code (no counter) — V3 reports that claim-vs-code gap, it does not silently fix it by editing V1. |

## 3. What V3 adds that V1 lacks

### 3.1 Vitals + memory/load trend (report only)
- Every 5-minute tick, V3 appends one JSONL line to its own history
  file (`~/watchdog-v3-history.jsonl` in a future install; in this
  draft, the path is a proposal, not a live file).
- Fields: timestamp (UTC), `v1_state` (ALIVE / STALE / MISSING),
  `v1_last_tick_age_s`, `avail_mb`, `load`, `disk_pct`,
  `journal_counts` (see §3.2), `v1_fail_counts_last_hour`,
  `corrected_mounts_present` (true/false per share, by directory
  name under `/mnt/shared/removable/`, never by sd letter).
- Trend rule, borrowed from the bridge pack §2.4 and the prior
  research, as a **report state only**: 3 consecutive V3 ticks with
  available MB falling ≥200 MB each = `TREND-WARNING`, even if
  still above 500 MB. Absolute states, also report only:
  ≥500 MB OK, 300–499 MB WARNING, <300 MB CRITICAL.
  A TREND-WARNING or CRITICAL in this draft triggers **no shed,
  no kill, no restart, no deletion**. It is a line in V3's report
  for the AI Loop audit and the owner to act on. The prior V2
  claim "pause non-essential jobs below 300 MB" is log-only in
  V2's code; V3 does not repeat that claim as an action — it
  reports the state and leaves the shed order (crew browser
  first, then cloud-serve pause, then batch jobs, never
  tailscaled/sshd/watchdog) as an owner-approved future action.

### 3.2 Journal / vshd scan (counts only, last 5 minutes)
- Patterns, counts only, never full journal dumps, never keys,
  tokens, addresses, or secrets in any line:
  `vshd.*(broken pipe|error|fail)`, `tailscaled.*(error|disconnect)`,
  `oom|killed process`, `hung task`, `usb.*disconnect`
  (USB disconnects mattered in the Oct 26 SD/dd failure and the
  Oct 27 hub resets).
- 3 consecutive ticks with vshd-error count > 0 =
  `BRIDGE-DISTRESS` report state. This is a vitals state, not a
  diagnosis and not proof of cause — the Oct 26 freeze left no
  OOM, no kernel panic, and no tailscaled error in the
  previous-boot log, so V3 never claims a distress pattern
  proves a cause.
- A host-side vshd wedge is **not fixable from the guest**.
  V3's BRIDGE-DISTRESS line therefore never says "fixed" — it
  says "owner action at the machine: restart Linux, then
  Chromebook, then fresh port if a service is refused."
  Wording discipline from the prior research is carried here:
  FIXED = a named service passed its re-check. BRIDGE = host-side,
  owner action. V3 in audit mode claims neither.

### 3.3 Corrected mount paths (read-only)
- V1 paths checked: `/mnt/cloud-master`, `/mnt/ssd-238` — reported
  as stale, with the evidence (empty in the current guest).
- V3 paths checked (read-only directory presence, no mount):
  `/mnt/shared/removable/Cauldron`, `/mnt/shared/removable/SSD`,
  `/mnt/shared/removable/potions fil` — names are share names, not
  sd letters, and not guesses: these are the shares seen Oct 27,
  00:21 ET. If a share name changes, V3 reports
  `MOUNT-PATH-CHANGED` and stops asserting the old name; it does
  not guess a replacement.
- V3 never mounts, never remounts rw, never formats, never dd's,
  never touches Seagate/SSD/Potion's Files contents.

### 3.4 Tunnel + cloud-serve staleness
- For each of tunnel and cloud-serve, V3 records two ages:
  (a) age of V1's last line about that service, (b) age/result of
  V3's own read-only probe. If (a) is >15 minutes, V3 reports
  `V1-STALE <service>`. If (a) and (b) disagree, V3 reports
  `V1-MISMATCH <service>`. This is the check V2 cannot provide
  (its tunnel/cloud-serve check is OFF by default) and the check
  that makes V3 bridge-focused rather than host-health-focused.

### 3.5 Shared-log cap audit
- V3 stats `~/bridge-watch.log` (size, last V1 line, last V2 line)
  and reports: size >5 MB = `LOG-CAP-WARNING`; V1/V2 line counts
  in the last hour, to make the interleaving visible (e.g. V2
  00:31:47, V1 00:31:48 in the Oct 27 side-by-side window).
  V3 writes to its **own** log file, never to
  `~/bridge-watch.log`, so V3 does not add to the interleaving
  it audits. V3 does not rotate or truncate V1's/V2's log in
  this draft — rotation of the shared log is an owner-approved
  future action, stated as such, not done silently.

## 4. What V3 does NOT do (this draft)

- Does NOT edit `~/bridge-watch-loop.sh` (V1) or
  `~/bridge-watch-v2.sh` (V2).
- Does NOT kill, restart, or start any watchdog, service, tunnel,
  or cloud-serve.
- Does NOT auto-add any upgrade to V1 or V2. Every addition V3
  proposes is marked NEEDS-OWNER-YES, same rule as the AI Loop audit.
- Does NOT delete data, format, dd, rotate a token, or put a secret
  in a script, vitals line, log, or report.
- Does NOT alert the owner on routine recovery. Fix-not-alert
  (owner preference, Oct 26, 11:20 PM) is preserved: V3's reports
  are files the owner / AI Loop audit reads on a status check.
  A heartbeat gap or distress pattern is recorded, not alerted,
  unless the owner re-enables alerts as a separate decision.
- Does NOT claim to fix a host-side bridge wedge, predict a freeze
  with certainty, or prove the Oct 26 cause.

## 5. Draft runtime shape (proposal, not installed)

- Tick: every 300 seconds, matching V1/V2.
- Single-instance guard: `flock` on its own lock file
  (`/tmp/watchdog-v3.lock`), so a second V3 exits instead of
  doubling ticks. This flock does not coordinate with V1 or V2 —
  V3 never writes to their log, so it does not need to.
- Own log: `~/watchdog-v3.log`, rotated at 5 MB (`.1` suffix,
  same pattern as V2's vitals rotation).
- Own history: `~/watchdog-v3-history.jsonl`, rotated at 5 MB.
- `set -u`, no unset-variable silent defaults.
- Mock mode: `WATCHDOG_V3_MOCK=1` with `WATCHDOG_V3_MOCK_DIR`
  pointing at mock files (mock V1 log lines, mock `free` output,
  mock journal counts). In mock mode the script reads only those
  files and writes only to the mock output dir. Mock mode must
  never call a real restart, kill, mount, or delete — and in
  this audit draft, neither does live mode.
- Draft script: `v3-watch-v1-draft.sh` in this folder, header
  marked DRAFT-NOT-INSTALLED. It is not copied to penguin by
  this job, and it must not be run on penguin without a fresh
  owner yes naming this exact file.

## 6. Mock test plan (before any install)

1. **Stale V1 test:** mock V1 log with last tick 30 minutes old,
   V1 process absent in mock. Expect `V1-STALE`, not a restart.
2. **Stale-path noise test:** mock V1 log with repeating
   FAIL cloud-master-mount / ssd-mount, mock corrected shares
   present. Expect `STALE-PATH-NOISE` + corrected-mounts-present,
   and a single hourly `V1-REPEAT-STILL-DOWN` count, not a
   per-tick storm.
3. **Mismatch test:** mock V1 tunnel OK, mock probe no
   cloudflared. Expect `V1-MISMATCH tunnel`.
4. **Trend test:** mock available MB 1500 → 1200 → 900 → 600.
   Expect `TREND-WARNING` at the third falling tick, with no
   shed/kill/delete in mock output.
5. **Journal distress test:** mock 3 ticks with vshd-error
   count > 0. Expect `BRIDGE-DISTRESS`, with wording that says
   owner action, not "fixed".
6. **Log-cap test:** mock shared log >5 MB. Expect
   `LOG-CAP-WARNING` and V3's own log staying separate.
7. **Mock isolation test:** run in mock mode and confirm no
   file outside the mock output dir is written, and no
   `systemctl`, `pgrep` restart, `mount`, or `kill` is invoked
   on the live system. This is the Latch-style check for this
   draft: a mock run that touches the live system fails.

## 7. Who watches V3 — the AI Loop watches the PROCESS, not just the output

**The AI Loop audit + owner review — NOT a V4.** See the
section "AI Loop oversight of V3/V3.1" in `v3-vs-v3.1.md`
for the full chain-termination argument and the audit
cadence. In short: V3 is a ticking script, so it needs a
non-ticking examiner (the AI Loop, audit-only) plus the
owner's status checks. Adding a V4 to watch V3 would restart
the same chain one level up and prove nothing — the chain
stops where a human (owner) plus a periodic examiner (AI
Loop) read the report, because a report that no one reads
is the failure mode a V4 would not fix.

Owner update, Oct 27, 00:35 ET, applied here: the AI Loop
watches over the **process** of V3, not just V3's output
lines. That means, once V3 is live, the AI Loop audits:
(a) this draft spec itself, against what V3 actually does
(spec drift — did V3 start doing something its spec does
not say?); (b) V3's tick logs and history file, for
freshness, gaps, and states; (c) V3's upgrade proposals,
for whether each one is marked NEEDS-OWNER-YES and whether
any proposal would break fix-not-alert, audit-only, or the
never-delete / never-rotate-tokens rules; and (d) whether
V3 stayed audit-only in fact — no restart, no edit to V1
or V2, no mount, no delete, no token in any line. A V3
report that looks healthy but whose process broke a rule
is a failed audit, even if every tick line says OK.

The AI Loop does NOT auto-edit V3, does NOT restart V3,
and does NOT approve its own upgrades. Owner approval
remains the final gate for every change to V3, and for
every upgrade V3 proposes to V1.

## 8. What still needs owner approval before V3 is installed

1. This exact draft file (`v3-watch-v1-draft.sh`), after mock
   tests §6 pass and a Latch/Nickel review passes.
2. V3's own log/history paths and rotation sizes (proposed
   above, not yet approved).
3. Corrected mount share names, re-confirmed at install time
   (share names can change; V3 must not assert a stale name).
4. Whether V3's TREND-WARNING / CRITICAL states should ever
   trigger a shed action in a future non-audit build — in this
   draft they do not, and that change needs its own yes.
5. Shared-log rotation for `~/bridge-watch.log` — proposed
   here as a future action, not approved, not done.
6. Tunnel-home decision, if V3 is ever to do more than report
   tunnel state (it does not decide tunnel home in this draft).
7. Install order and cutover: V3 starts while V1 keeps running;
   V1 is never stopped to "make room" for V3 in this draft.
