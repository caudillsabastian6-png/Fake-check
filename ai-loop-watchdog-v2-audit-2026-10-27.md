# AI Loop Audit of Watchdog V2 — 2026-10-27, 00:32–00:33 ET

**Auditor role:** AI Loop v2, Latch-style only — read, check, report, edit nothing.
This audit watched and proposed. It did **not** edit, kill, restart, start, or
install any watchdog, and it did **not** auto-add any upgrade.

**Hard-rule compliance, verified in this audit:**
- No edit to `~/bridge-watch-loop.sh` (V1) or `~/bridge-watch-v2.sh` (V2).
- No watchdog killed, restarted, or started by this audit.
- Nothing installed on penguin by this audit.
- Every proposed addition below is marked **NEEDS-OWNER-YES** before it is
  added to any watchdog script.

## 1. What was checked, and when

- Host: penguin, 100.71.87.4, via SSH, read-only checks.
- Audit window: log lines 2026-10-26 23:53 through 2026-10-27 00:31 ET, plus
  the full vitals file at audit time.
- Both watchdogs confirmed running at audit time:
  - V1: `~/bridge-watch-loop.sh`, PID 1640, started 00:00, ticks every 300 s.
  - V2: `~/bridge-watch-v2.sh`, PID 29431, started 00:31 ET Oct 27, ticks
    every 300 s.
- Files at audit time (penguin home):
  - V1 script: 1.9K, Oct 26 23:18
  - V2 script: 2.9K, Oct 27 00:30
  - `~/bridge-watch.log`: 7.4K, shared by both watchdogs
  - `~/bridge-watch-vitals.jsonl`: 192 bytes, 2 lines, V2 only
- AI Loop v2 reference: `~/workspace/fake-check/playground/agent-loop/agent_loop_v2.py`
  — only its examiner pattern was used here (read → check → report, edit
  nothing). No card-checking steps were run in this audit.

## 2. What the logs actually show

### V1 ticks in the window (pattern, every tick, no change)
Every V1 tick in the window reads the same way:
- `OK tailscale`
- `FAIL cloud-master-mount — trying fix` → `STILL DOWN cloud-master-mount`
- `FAIL ssd-mount — trying fix` → `STILL DOWN ssd-mount`
- `OK cloud-serve-8080`
- `OK tunnel-process`
- `OK disk-space`

Ticks seen: 23:53, 00:00, 00:05, 00:11, 00:16, 00:21, 00:26, 00:31 ET.
No tailscale, tunnel, cloud-serve, or disk failure in this window.

Important context for those two FAIL lines: V1 checks
`mountpoint -q /mnt/cloud-master` and `mountpoint -q /mnt/ssd-238`.
Those guest mountpoints are empty in the current guest; the real shared
drives are under `/mnt/shared/removable/` (Cauldron, SSD, potions fil).
So those two FAIL lines are, at present, stale-path noise — they do not
prove a drive is unplugged, and they do not prove a mount is broken.
They also never clear, so a reader skimming the log learns to ignore FAIL
lines, which is itself a weakness.

### V2 ticks in the window (only 2 ticks at audit time)
Vitals file, complete at audit time:
```json
{"ts":"2026-10-27T04:30:49Z","avail_mb":1376,"load":"0.06","disk_pct":73,"tailscaled":"active"}
{"ts":"2026-10-27T04:31:47Z","avail_mb":1376,"load":"0.26","disk_pct":73,"tailscaled":"active"}
```
Log lines for those ticks:
- `--- bridge-watch-v2 tick --- avail=1376MB load=0.06 disk=73% tailscaled=active`
- `OK tailscaled`, `OK disk-space`, `OK vitals written`
- Second tick, same, load 0.26.

No WARNING, no CRITICAL, no tailscaled restart in this window — correctly,
because available memory (1,376 MB) is far above both V2 thresholds, disk
73% is below 90%, and tailscaled is active.

### Side-by-side observation
Both watchdogs write to the **same** `~/bridge-watch.log`, with no shared
lock between them. V2 holds a flock on `/tmp/bridge-watch-v2.lock`, which
only stops a second V2 — it does not stop V1. In the sample the lines did
not interleave mid-line (V2 tick 00:31:47, V1 tick 00:31:48), but
interleaving of tick blocks is not prevented by either script.
If tailscaled ever dies, both watchdogs could restart it in the same
minute, with no coordination.

## 3. Check-by-check comparison

| Check | V1 (Crostini bridge watcher) | V2 (full-Linux host-health script) |
|---|---|---|
| Tailscale | `tailscale status` probe; restart on probe failure | `systemctl is-active tailscaled`; restart only if service is not `active` |
| Memory (available MB) | None | Yes, `free -m`, thresholds 500 / 300 MB |
| Load | None | Yes, 1-min load from `/proc/loadavg` |
| Disk | Binary: OK only if use < 90% | Numeric % in log + vitals; WARNING at >= 90%, never auto-delete |
| Mounts | `/mnt/cloud-master`, `/mnt/ssd-238` — fix command is `true` (no-op) | None |
| Cloud-serve :8080 | `curl` check, fix is `true` (no-op) | None — comment only |
| Tunnel process | `pgrep cloudflared`; fix is `~/start-tunnel.sh` | None — explicitly OFF by default, pending a tunnel-home decision |
| Journal / vshd scan | None | None |
| Memory trend | None | None (single-tick thresholds only) |
| Vitals file | None | JSONL, one line per tick, rotated at ~5 MB |
| Main log rotation | None | None (vitals rotate; `bridge-watch.log` does not) |
| Single-instance guard | None | flock on `/tmp/bridge-watch-v2.lock` (V2 only) |
| Restart rate limit | Header claims max 3/hr, but the `check()` code has no counter — not enforced | Header claims max 3/hr, but the code has no counter — not enforced |
| Design target | Crostini guest, where the vshd bridge is the main failure | Full-Linux host, where the header says there is no vshd bridge to watch |

Two claim-vs-code mismatches, Latch-style, recorded plainly:
1. V2's header says it watches "Tailscale, tunnel, cloud-serve." The code
   watches Tailscale only; tunnel/cloud-serve are comments, OFF by default.
   Do not present V2 as watching tunnel/cloud-serve until that code exists.
2. Both scripts' headers claim a max-3-restarts-per-hour limit. Neither
   script implements a counter. A dead service would be restarted every
   5-minute tick, by both watchdogs, until it stays up.

## 4. (1) Upgrades / additions V2 still needs

Each item below is a proposal only. **NEEDS-OWNER-YES** before it is added
to any watchdog script, and each needs a mock/workspace test first —
never a live tailscaled-kill, dd, or format test without a separate
owner yes for that exact test.

1. **Mount checks, with corrected paths — NEEDS-OWNER-YES.**
   Add mount checks for the paths that actually exist in the current
   guest (`/mnt/shared/removable/` shares), or, on full Linux, for the
   real mountpoints chosen at first boot. Do not keep checking
   `/mnt/cloud-master` and `/mnt/ssd-238` as if they were live.
   Test: mock a missing mountpoint, confirm FAIL, not STILL DOWN forever
   without a useful next step.
2. **Tunnel-process check and restart, with a tunnel-home decision — NEEDS-OWNER-YES.**
   Add `pgrep cloudflared` + a restart path, but only after the owner
   decides tunnel home: Windows, penguin-until-switch, or paused.
   Do not enable it by guessing the home.
3. **Cloud-serve :8080 check — NEEDS-OWNER-YES.**
   Add the V1 curl check, or its full-Linux equivalent, so a dead
   cloud-serve is not invisible under V2.
4. **Journal / vshd scan, last 5 minutes — NEEDS-OWNER-YES.**
   Scan for `vshd.*(broken pipe|error|fail)`, `tailscaled.*(error|disconnect)`,
   OOM, and hung-task lines, and log a count per tick. This is the only
   V2 addition that can even hint at a bridge wedge from inside the guest;
   it still cannot fix a host-side wedge.
5. **Memory trend warning — NEEDS-OWNER-YES.**
   Add: 3 consecutive ticks falling >= 200 MB each = WARNING, even if
   still above 500 MB. Single-tick thresholds alone will not spot a slow
   leak before it hits 300 MB.
6. **Make the critical-memory action real, or remove the claim — NEEDS-OWNER-YES.**
   V2 currently logs "pause non-essential jobs" below 300 MB but pauses
   nothing. Either implement a defined shed order (crew browser first,
   then cloud-serve pause, then batch jobs — never tailscaled/sshd/watchdog),
   or change the log line to warning-only. Do not leave a claimed action
   unimplemented.
7. **Separate log file and main-log rotation — NEEDS-OWNER-YES.**
   Give V2 its own log file, or a shared log with a writer lock, and
   rotate `bridge-watch.log` at a stated size. Vitals rotation alone does
   not stop the main log growing, and two writers to one file is not a
   safe long-term pattern.
8. **Enforce the restart rate limit, or remove the claim — NEEDS-OWNER-YES.**
   Implement a per-service counter (max 3 restarts/hour, then STILL DOWN
   until the next hour), in both V1 and V2, or delete the max-3/hr claim
   from both headers. Test in mock mode with a fake dead service.
9. **Extend vitals fields when checks are added — NEEDS-OWNER-YES.**
   When mounts, tunnel, and cloud-serve are added, add them to the JSONL
   vitals line too, so a reader does not have to grep two logs to see
   one tick.
10. **Systemd service/timer instead of nohup, at full-Linux time — NEEDS-OWNER-YES.**
    Do not convert the current Crostini guest to systemd management
    without a separate plan; this item belongs to the full-Linux host
    first boot, with a service file, a timer, and a restart policy that
    matches the rate limit in item 8.

## 5. (2) What V2 does better than V1

- **Vitals JSONL:** machine-readable, one line per tick, with timestamp,
  available MB, load, disk %, and tailscaled state. V1 has no equivalent;
  its log must be grepped by eye.
- **Memory thresholds:** >= 500 MB OK, 300–499 MB WARNING, < 300 MB
  CRITICAL (log-only today, see item 6 above). V1 has no memory check at all.
- **Load + numeric disk:** load is logged every tick; disk is a number,
  not just a pass/fail under 90%.
- **Cleaner tailscaled check:** `systemctl is-active` + restart only when
  the service is dead, rather than restarting on any `tailscale status`
  probe failure, which can be transient.
- **Flock single-instance guard:** a second V2 exits instead of doubling
  ticks. V1 has no guard.
- **Vitals rotation:** at ~5 MB, the vitals file rotates to `.1`. V1 has
  no rotation anywhere.
- **No false "trying fix" for mounts:** V2 does not pretend to fix mounts
  it cannot fix. V1 logs "trying fix" for mounts, then runs `true`.
- **Explicit never-kill list:** V2 states it never kills
  tailscaled/sshd/watchdog. V1's never-list is in its header but is less
  specific about the watchdog itself.
- **`set -u`:** V2 fails on unset variables rather than silently using
  empty values. V1 has no equivalent.

## 6. (3) What would break if V2 replaced V1 today

Do **not** replace V1 with V2 on the current Crostini guest. The following
would break or go silent on day one:

1. **Tunnel death goes silent.** V1 detects a dead `cloudflared` process
   and restarts it via `start-tunnel.sh`. V2 has no tunnel check. A dead
   tunnel under V2-only would still log `OK vitals written`, which looks
   healthy.
2. **Cloud-serve death goes silent.** V1 curl-checks :8080. V2 does not.
3. **Mount signal is lost.** Even though V1's mount lines are currently
   stale-path noise, removing them removes the only mount signal in the
   log. A future mount change would have no log line at all.
4. **False-healthy log.** Removing V1's FAIL lines while tunnel/cloud-serve
   are unchecked makes the log look cleaner without the system being
   healthier. That is worse than a noisy log.
5. **Bridge wedge stays invisible.** V2 was written for a host with no
   vshd bridge. On the current guest, the vshd bridge is the main failure
   mode, and V2 has no vshd/journal check for it. Neither script can fix
   a host-side wedge, but V1 at least keeps the bridge-adjacent checks
   (tunnel, cloud-serve, mounts) that V2 drops.
6. **Unbounded restart risk, doubled.** If tailscaled stays dead, V2
   restarts it every 5 minutes with no counter. If V1 is also still
   running during a transition, both restart it. The side-by-side run
   mitigates this only while both are watched; a cutover must stop one
   first, with a stated order.
7. **Design-target mismatch.** V2's own header says it is NOT the old
   Crostini bridge watcher. Installing it as a drop-in replacement on
   Crostini contradicts its design. The correct home for V2-as-written
   is the full-Linux host after migration, with the additions in §4
   applied first if it must also cover the current guest.

## 7. AI Loop watchdog role, as set by the owner

- V1 remains the watchdog for the current guest.
- V2 runs side by side, and its vitals are the audit signal for V1's
  weaknesses (memory, load, trend, journal — the things V1 cannot see).
- The AI Loop is the watchdog for V2: it reads V2's ticks and vitals,
  compares them against V1, and proposes upgrades — it does not edit,
  restart, or replace either watchdog on its own.
- Proposed audit cadence, for owner approval (not auto-set):
  re-audit after the next 20 ticks of each watchdog, and after any
  tailscale/tunnel/cloud-serve FAIL, or any memory WARNING/CRITICAL.
  Each re-audit is audit-only, same hard rules as this one.
- V3 is the hybrid that keeps both check sets: V1's bridge/tunnel/
  cloud-serve/mount checks + V2's vitals, thresholds, trend, journal
  scan, flock, and rotation — built only after the owner approves the
  items in §4, one by one.

## 8. Verdict

**Do not replace V1 with V2 today. Keep them side by side.**
V2 is better at host health numbers and worse at bridge coverage; V1 is
better at bridge coverage and blind to memory, load, and trends.
The upgrade path is not V1 → V2, it is V1 + V2 → V3, with the §4 items
approved first.

**Nothing was changed by this audit.** Both watchdogs were still running
at the end of it, V1 PID 1640 and V2 PID 29431, and no watchdog script,
log, or vitals file was edited by this job — log and vitals growth seen
here is the watchdogs' own ticking, not this audit.
