# Bridge + Dual-Boot Loop Pack — PREPARATION ONLY
**Date:** Oct 26, 2026, late evening ET
**Status:** BUILD PACK ONLY. No change was made to penguin in this pack.
No firmware change, no dd, no format, no deletion, no uninstall, no
Tailscale/Tunnel token rotation, no penguin file was touched by this pack.
**Owner order, in sequence — do not reorder without Sabastian's yes:**
1. Delete a lot first (safe list already done Oct 26 ~11:21 PM ET; see §5).
2. Windows crew computer arrives Oct 30 and takes over.
3. THEN the Chromebook (penguin) Linux switch.
**Focus order, as the owner set it Oct 26 ~11:24 PM ET:**
Bridge FIRST, mainly. Dual-boot / solid Linux SECOND, built by the crew
working together in the loop. This pack is the loop's shared plan, not
the install itself.

---

## 0. Which "bridge" this pack is about — do not confuse the three

| Bridge | What it is | This pack? |
|---|---|---|
| **ChromeOS ↔ Crostini guest bridge (vshd)** | The host-side channel that lets ChromeOS talk to the Linux container, and lets Muse's Tailscale/SSH road reach the guest. When it wedges, the guest can be alive while Muse cannot reach it at all. | **YES — the main subject.** |
| Tailscale tailnet | The VPN road Muse uses to reach penguin (100.71.87.4) and muse (100.106.178.76). It rides *over* the guest being reachable; it does not replace vshd. A green dot in the Tailscale admin page is not proof the guest's SSH road is alive. | Context only. |
| App ↔ Office bridge (Real or Replica) | The in-app checker → office case flow. It is in TEST MODE on file and is a separate, platform-limited problem. | NO — out of scope here. Do not mix the two bridges in any later report. |

Home Wi-Fi is also not the bridge. Penguin is wired Ethernet, and past
outages showed the guest ticking while the outside path was dead.

---

## 1. Bridge failure analysis — from the logs on file, nothing invented

### 1.1 Facts on file (verified, not inferred)

- **Machine:** Chromebook, Linux guest "penguin", Tailscale 100.71.87.4,
  SSH via `~/workspace/laptop-control/ts-proxy.py`, user
  `caudillsabastian6`. Guest RAM 2.7 Gi total, **Swap 0**.
- **Oct 23 ~2:36 PM ET outage:** SSH failed three straight times
  ("CONNECT failed: connection closed"), board/CDP via the tunnel proxy
  were dark too, minutes after working cleanly at 2:26–2:30 PM.
  Later that day the guest's own journal showed its vitals writer ticking
  every minute during the outage — **the guest was alive; the
  ChromeOS↔guest bridge (vshd, broken-pipe errors) and the outside path
  were what broke.** Lesson recorded in AGENTS.md: road-dead ≠ guest-dead.
- **Oct 23 port lesson:** in-guest server healthy (HTTP 200) while Chrome
  got ERR_CONNECTION_REFUSED on a stale port. Full restarts and even a
  Linux-only restart did NOT heal port 8791's forwarding registration.
  Moving the same server to a fresh port (8792) healed it. Lesson: a
  wedged forwarding registration is per-port, and a restart is not a
  guaranteed bridge cure.
- **Oct 26 ~10:32 PM ET:** SSH down again (bridge/vshd flap).
- **Oct 26 ~11:08 PM ET:** owner restarted the Chromebook because it
  "seemed froze up". SSH right after restart still failed with the same
  "CONNECT failed: connection closed".
- **Oct 26 ~11:10 PM ET, back on:** SSH verified back — penguin,
  100.71.87.4, uptime 0 min, tailscaled active, Mem 2.7 Gi,
  2.0 Gi available fresh. Fresh-boot numbers then fell fast:
  1.8 Gi available at 11:11 PM, 1.5 Gi available at 11:21–11:22 PM
  with only ~1.2–1.3 Gi used. The guest starts light and gets tight
  quickly; there is no swap to spill into.
- **Previous-boot log check, Oct 26 ~11:10 PM ET:**
  `journalctl -b -1` last entry 22:06, `pkill -f BookwormPup32`, then
  NOTHING. Grep for OOM / killed process / out of memory / kernel panic /
  hung task / tailscaled fail / vshd broken-pipe returned only one
  unrelated line (vshd failing to open `/dev/kmsg`, permission denied,
  from the 20:15 boot). **No crash log was left. Cause is NOT proven.**
- **Drive-name shift after that reboot (safety-critical):**
  Vaio SD card moved from sdb to **sdc (7.5 G, sdc1 3.7 G vfat,
  UUID 9624-EA0B)**; sdb became Potion's Files 1.9 T. Never format sdb
  on the strength of an old name. Re-confirm name + size + UUID at
  every write. `/tmp/vaio-build` was wiped by the reboot (tmpfs) —
  future staging must be in a persistent home folder, never `/tmp`.
- **What is already in place, Oct 26 late evening:**
  - `ts-watchdog` v3 timer in the guest (see §2.2).
  - `bridge-watch-loop.sh` — ready in
    `~/workspace/laptop-control/bridge-watch-loop.sh`, being installed
    on penguin by a separate staging job at pack-writing time.
    Do not claim it is installed until its first tick is seen in
    `~/bridge-watch.log` on penguin.
  - `penguin-ping-check` cron, every 5 min, America/New_York,
    state in `~/workspace/laptop-control/ping-check-state.json`,
    owner preference Oct 26 ~11:20 PM ET: **FIX, DO NOT ALERT**
    (see §2.3). Its saved body is the authority; do not paraphrase it
    into a different rule.
  - Safe deletion done Oct 26 ~11:21 PM ET: journal
    1020 M → 57 M, apt cache 650 M → 0, disk 5.2 G used / 4.5 G avail
    (54%) → 3.8 G used / 6.0 G avail (39%), Docker + containerd
    active/enabled → inactive/disabled (not uninstalled),
    apt-daily timers disabled. Docker.socket remains active as a
    trigger socket. Chrome, Settings, Terminal, tailscaled, sshd,
    Python, tunnel scripts, guest chromium, gcc/nodejs kept.

### 1.2 What the logs do NOT prove

- They do **not** prove the freeze was an out-of-memory kill. No OOM
  line was found in the previous boot.
- They do **not** prove tailscaled itself died. Tailscaled was active
  on the fresh boot, and the previous boot's grep found no tailscaled
  error.
- They do **not** prove the guest crashed. A guest that stops logging
  and a bridge that stops delivering logs look the same from Muse's
  side. The Oct 23 vitals evidence is the reason "guest alive, bridge
  dead" is the leading hypothesis, not a proven fact for Oct 26.
- They do **not** prove a single cause. Treat the next outage as a
  discrimination test (§1.4), not as a repeat of a known cause.

### 1.3 Ranked hypotheses (most likely first, all still hypotheses)

1. **Host-side vshd / ChromeOS↔guest bridge wedge.** Fits Oct 23
   (guest ticking, all roads dead at once) and Oct 26 (quiet log end,
   no crash). Fixed only by ChromeOS-side action: restart Linux,
   restart the Chromebook, or a fresh port registration. Not fixable
   from inside the guest, and not fixable from Muse when SSH is down.
2. **Guest RAM pressure / hang without an OOM log.** Fits 2.7 Gi,
   Swap 0, available falling 2.0 → 1.5 Gi within minutes of boot,
   and a freeze that leaves no log. A hang (not a kill) would also
   leave a quiet log end. Needs memory-trend data, not a single
   snapshot, to confirm or rule out.
3. **Tailscaled / vshd flap inside the guest.** Fits the "CONNECT
   failed: connection closed" SSH error and the Oct 23 pattern of
   one brief recovery (~2:34–2:35 PM) inside a longer outage.
   This is the one the guest *can* fix itself (§2.1).
4. **USB / hub power starvation (contributory, not the bridge itself).**
   On file: a USB fan on laptop USB power starved the hub and dropped
   all drives Oct 26. Rule for penguin, already set: fan on wall
   power only, 1–2 drives at a time, never fan + hub + 3 drives.
   This can drop drives and confuse jobs; it does not by itself
   explain a clean bridge wedge, so do not use it as a blanket
   explanation.
5. **ChromeOS update / sleep / power event.** Not evidenced in the
   logs on file. Do not claim it without a ChromeOS-side log or
   owner report of an update/restart prompt.

### 1.4 How to tell them apart at the next outage (owner + crew checklist)

Ask, in order, and record the answers before restarting anything if
it is safe to do so:

1. **Is ChromeOS itself alive?** Can the owner open Chrome, Settings,
   Files? If ChromeOS is frozen too, it is not a vshd-only wedge.
2. **Is the Linux Terminal alive locally?** If Terminal opens and
   `tailscale status` + `free -h` work locally, the guest is alive
   and the bridge is the suspect. If Terminal will not open or keeps
   losing access, the container itself is down.
3. **What does the guest log say when it comes back?**
   `journalctl -b -1` tail, plus grep for `oom`, `killed process`,
   `vshd`, `tailscaled`, `hung task`. A vitals line ticking through
   the outage window = guest alive, bridge dead. A gap with no
   vitals = guest down or hung.
4. **What was running just before?** Big copy, crew browser with
   16 extensions, cloud-serve + tunnel + a job at once, 3 drives
   mounted? One job at a time is the penguin rule for a reason.
5. **What was the last thing in `~/bridge-watch.log` and in
   `~/bridge-vitals.json` (§2.4) before the gap?** That is the
   reconstruction record the new design exists to create.

Do not restart twice in a row and then claim the second restart
"fixed" the bridge — the Oct 23 port lesson shows a restart can
look like a fix while a stale registration is the real problem.
Record what changed, port included, every time.

---

## 2. Watchdog / heartbeat design — fix what the guest can, log the rest

Design principle, in the owner's words: **fix it, do not just alert
about it.** That principle has a hard limit, stated plainly in every
later section: a fix that needs the host cannot be done from the
guest or from Muse. The design therefore has three layers, and no
layer pretends to do another layer's job.

### 2.1 What the guest CAN fix itself (and only these, automatically)

| Problem | Guest-side fix | Limit / guardrail |
|---|---|---|
| tailscaled service dead | `systemctl restart tailscaled`, re-check once | ts-watchdog v3 rules (§2.2). Max 3 restarts/hour for any one service in bridge-watch. Never loop forever. |
| tailscaled alive but `tailscale status` slow/failing | Count strikes, restart only on 3 consecutive failures (20 s probe each) | A healthy tailscaled on a loaded 2.7 Gi guest can miss one 8 s probe — v2's single-miss restart was a bug, v3 fixed it. Do not regress to v2. |
| cloud-serve / tunnel process dead, mounts still present | Restart that process from its own start script (`~/start-tunnel.sh` for the tunnel) | Only if the mount/device it serves is still present. A dead process with a missing drive is STILL DOWN, not a restart loop. |
| Journal / apt cache growth | Vacuum / clean on a schedule or a size cap (already done once: journal to ~100 M cap, apt cache to 0) | Cache only. Never delete user data, pool files, tunnel config, `~/.ssh`, or `~/vaio-build` to "free space". |
| A non-essential job eating RAM | Shed it in a fixed order (crew browser first, then cloud-serve pause, then any batch job) — see §2.4 thresholds | Shedding is a stop, not a deletion. Jobs resume only on a fresh owner/crew decision, never auto-resumed in the same tick. |

### 2.2 What already exists — keep, do not reinvent

- **`ts-watchdog` v3** (`~/workspace/laptop-control/ts-watchdog.sh`,
  timer `ts-watchdog.timer` — KEEP, do not disable):
  restart tailscaled at once only if the service is not active;
  otherwise count failed 20 s `tailscale status` probes, restart on
  3 consecutive failures; strike counter in `/run` (tmpfs, resets on
  boot/success). It also restarts `crew-window.service` only when
  inactive — that service is currently parked/disabled on file, so
  do not let the watchdog silently resurrect a parked service without
  an owner yes. If crew-window stays parked, remove that one check
  from a future watchdog revision and note the change.
- **`bridge-watch-loop.sh`** (existing script, 5 min tick):
  checks tailscale, cloud-master mount, SSD mount, cloud-serve :8080,
  tunnel process, disk < 90%. Each check logs OK / FAIL / FIXED /
  STILL DOWN. Safe limits in its header: max 3 restarts per service
  per hour, never deletes data, never rotates tokens, never remounts
  rw, never touches Seagate/SSD/potions contents. **Gaps in the
  existing script, to be fixed in the v2 revision (§2.4), not by
  hand-editing on penguin without a reviewed copy in the workspace:**
  it has no memory/load check, no vshd/journal-error check, no
  vitals file, no log cap (`~/bridge-watch.log` grows unbounded),
  no flock (two copies could run at once after a reboot + nohup),
  and its mount/tunnel "fixes" are placeholders (`true`) that log
  STILL DOWN rather than fixing anything.

### 2.3 What Muse's side CAN and CANNOT do — the ping check, honestly

- **Cron `penguin-ping-check`, every 5 min** (saved body in
  `~/workspace/cron.d/minutely/penguin-ping-check__interval@5m.md`,
  state in `~/workspace/laptop-control/ping-check-state.json`):
  SSH-checks penguin, restarts tailscaled via SSH if reachable and
  inactive, records low-memory state, and — by owner preference
  Oct 26 ~11:20 PM ET — **sends no alert, warning, or recovery
  message, even after 2, 12, or more failures.** It keeps checking.
- **What it cannot do:** fix a bridge that is already down (SSH is
  the road it uses to fix things), fix a frozen guest, or restart
  ChromeOS/Linux from outside. If the bridge is the broken part,
  the ping check's job is to keep a faithful failure count in its
  state file so the *next* time anyone looks, the gap is measured
  in ticks, not guessed.
- **Consequence the owner accepted with "fix, don't alert":**
  a host-side break will not produce a message. The owner must
  check status himself, or re-enable alerts as a last resort.
  Do not silently re-enable alerts to "help". If the owner asks
  for alerts back, that is a new cron update with its own yes.
- **The outbound-ping idea, correctly understood:** a script on
  penguin cannot *alert* Muse when the bridge is down, because the
  bridge is the path the alert would travel on. What it *can* do
  is write a local vitals record every tick (§2.4). When the bridge
  returns, Muse reads the vitals + the gap and reconstructs what
  happened. The Muse-side 5 min checker is the receiver that
  notices a missing ping; the guest-side writer is the sender that
  proves the guest was alive during the gap. Both halves are needed.
  Neither half alone is a "cure" for vshd.

### 2.4 Watchdog v2 — the revision to build next (spec, not an install)

Build this in the workspace first, review it with Nickel/Latch
(§4), and install it only on a fresh owner yes for that exact file.
Do not edit the running copy on penguin in place.

**New checks, in tick order, every 5 minutes, one tick at a time:**

1. `flock` the run — if a previous tick is still running, exit
   quietly. No overlapping ticks, no double restarts.
2. **Vitals write (always, first):** append one JSON line to
   `~/bridge-vitals.jsonl` (not a single overwritten file, so a
   gap is visible): timestamp, `free -m` available MB, load
   average, `systemctl is-active tailscaled`, `tailscale status`
   exit code only (never keys, never addresses in the log beyond
   what `tailscale status` already shows locally), disk % for `/`,
   and the last vshd-related journal line count. Rotate the file
   at 5 MB (keep the newest 5 MB, archive nothing sensitive).
3. **tailscaled** — ts-watchdog v3 rules, unchanged. Bridge-watch
   must not add a second, faster restart that fights it.
4. **Memory pressure (predictive, the "spot it before it happens"
   part):**
   - Available ≥ 500 MB: log OK only.
   - Available 300–499 MB: log WARNING in vitals + bridge-watch log,
     shed the crew browser if running, do not start any new job.
     No chat alert under the current fix-not-alert preference.
   - Available < 300 MB: log CRITICAL, shed cloud-serve pause +
     any batch job, keep only tailscaled, sshd, watchdog, and the
     terminal plumbing. Do not kill tailscaled, sshd, or the
     watchdog itself. Do not delete files to free RAM — RAM is not
     freed by deleting disk files.
   - Trend rule: three consecutive ticks with available falling
     by ≥ 200 MB each is a WARNING even if the absolute number is
     still above 500 MB. Trend is the early warning; absolute
     number is the late warning.
5. **Journal-error scan (last 5 min only, cheap):**
   `journalctl --since "5 minutes ago"` grep for
   `vshd.*(broken pipe|error|fail)`, `tailscaled.*(error|disconnect)`,
   `oom`, `killed process`, `hung task`. Log counts only, not
   full journal dumps. Three ticks in a row with a vshd error
   count > 0 = bridge-distress pattern: log it, do not restart
   anything host-side, and let the next successful Muse read
   reconstruct it.
6. **Mounts / tunnel / cloud-serve** — existing checks, but with
   honest fixes: a mount that is not present is STILL DOWN (owner
   reseat needed), never auto-remounted rw, never auto-mounted
   from a guessed device name. A tunnel process that is dead with
   its mount present may be restarted from `~/start-tunnel.sh`
   once per hour, max.
7. **Log cap:** `~/bridge-watch.log` truncated/rotated at 5 MB.
   An unbounded log on a 10 Gi guest root is itself a future
   disk-full freeze.

**What v2 must never do:** delete user data, format or dd any
drive, rotate any token, uninstall PackageKit/tailscaled/sshd/
Python, disable `ts-watchdog.timer`, resurrect a parked service,
or claim in its log that it "fixed the bridge" when all it did
was restart tailscaled. Log wording: FIXED = the named service
passed its re-check. BRIDGE = host-side, owner action, never
claimed as fixed by the guest.

**Testing v2 before it is trusted:**

1. Playground test in the workspace: run the script with mocked
   `tailscale`, `systemctl`, and `free` commands and confirm it
   logs OK / WARNING / CRITICAL at the right thresholds and
   never calls a real restart in mock mode.
2. Latch review (§4): read the script, check every restart path
   has a rate limit, every deletion path is absent, and the log
   wording cannot be misread as a bridge fix.
3. Live test, owner-approved, one step only: stop tailscaled once
   (owner yes for that exact test), watch ts-watchdog + bridge-watch
   restore it, verify SSH from Muse, then stop. Do not test by
   breaking the bridge on purpose — there is no safe way to wedge
   vshd on demand, and a forced wedge could require a full
   Chromebook restart to recover.
4. Soak test: 24 hours of ticks with no STILL DOWN storm, no log
   growth beyond the cap, no double-run from flock failures.

### 2.5 If the bridge still breaks after v2 — the honest escalation ladder

1. Guest watchdog + Muse ping check keep trying, silently,
   per the fix-not-alert preference.
2. Owner, at the machine: open Terminal locally. If it opens,
   run `tailscale status`, `free -h`, `journalctl -b -1 | tail`,
   and read the vitals gap. If Terminal will not open, shut
   down Linux (Terminal menu / Settings) and reopen it.
3. If Linux will not come back: restart the Chromebook.
4. If a port registration is stale (in-guest 200, Chrome
   ERR_CONNECTION_REFUSED): move that service to a fresh port
   before asking for another restart — see Oct 23 port lesson.
5. If breaks repeat after deletion + watchdog + a fresh port:
   that is the evidence for the §3 Linux switch, not another
   round of the same restart. Do not grind restarts as a cure.

---

## 3. Dual-boot vs full Linux for this Chromebook — comparison and recommendation

### 3.1 The question, precisely

"Dual boot" on a Chromebook can mean three different things, and
the crew must not use the phrase loosely:

- **A. Keep ChromeOS, add Linux alongside it (true dual boot).**
  ChromeOS stays, a second OS boots from a separate partition /
  firmware path.
- **B. Replace ChromeOS with Linux (full Linux, single boot).**
  ChromeOS goes, Linux is the only OS. This is what the owner
  described Oct 26 ~11:14 PM ET: wait for Windows, migrate, then
  "switching this Chromebook over to Linux".
- **C. Keep ChromeOS, boot Linux from USB (live / persistent USB).**
  No install, no partition change. The Vaio Puppy USB is the
  pattern for this, on a different machine.

This pack recommends **B, after the Windows migration**, with C
as the trial / fallback. A is possible but is not recommended
first for this machine — see the table.

### 3.2 Comparison

| Criterion | A. True dual boot | B. Full Linux (RECOMMENDED, after migration) | C. Linux from USB (trial) |
|---|---|---|---|
| Keeps ChromeOS + Android apps? | Yes, if it works | No — ChromeOS is gone | Yes, untouched |
| Firmware work needed | Most: developer mode + MrChromebox UEFI firmware (or legacy boot), partition resize, boot menu | Most if UEFI, but only one OS to maintain after | Least: developer mode + USB boot only, no install |
| Risk of losing ChromeOS recovery | Highest — a bad firmware/partition step can leave recovery as the only way back | High at install time, but a clean break: one OS, one recovery path (the installer USB) | Lowest — pull the USB out, ChromeOS is still there |
| RAM available to Linux | Full host RAM, minus whatever the boot firmware reserves | Full host RAM — **this is the point**: no more 2.7 Gi Crostini guest cap, no vshd bridge at all | Host RAM while booted, but USB speed + no persistence unless a persistent partition is made |
| Does it kill the vshd bridge problem? | Only when booted into Linux; ChromeOS boots still have it | Yes — there is no ChromeOS↔guest bridge left to wedge | Yes while booted from USB; ChromeOS boots still have it |
| Driver risk (Wi-Fi, sound, touchpad, power) | Same as B, plus ChromeOS driver expectations | Same driver risk, single OS to debug | Same driver risk, but a failed trial costs nothing — just reboot to ChromeOS |
| Day-to-day maintenance | Two OSes to update, two sets of settings, partition space split | One OS to update | USB wear, updates need a persistent setup |
| Time / owner taps at the machine | Most | Medium (install taps, but once) | Least (plug USB, boot select) |
| Fits "don't break again"? | Partially — ChromeOS side can still break the same way | Best — removes the breaking layer entirely | Partially — only helps while booted from USB |

### 3.3 Recommendation, with reasons

**Recommend B: full Linux, after the Oct 30 Windows migration, and
only after the backup checklist in §3.5 is complete.**

Reasons, in order:

1. It removes the actual breaking layer (vshd + Crostini guest
   cap) instead of keeping it alongside a second OS that can
   still break the same way.
2. It is simpler to maintain than a dual boot on a small,
   firmware-locked machine: one OS, one update path, one
   Tailscale/SSH setup, full host RAM.
3. It matches the owner's own sequence: Windows takes over as
   the main machine, the Chromebook becomes a dedicated Linux
   box, not a second Windows box and not a ChromeOS box with a
   Linux sidecar.
4. Dual boot is not ruled out forever — if, after trying full
   Linux from USB (option C), the owner finds he still needs a
   ChromeOS-only app, dual boot can be revisited with that
   concrete need as the justification, not as a guess.

**What would change the recommendation:** a concrete, named
ChromeOS-only app or Android app the owner must keep on this
exact machine, or a MrChromebox support check that says this
board cannot run full Linux reliably while ChromeOS can. Both
are open questions (§3.6), not assumptions.

### 3.4 A note on "Windows on this Chromebook"

The owner also floated putting Windows on this Chromebook.
Do not pursue that as the main plan. Chromebooks are
firmware-locked and driver-thin for Windows: Wi-Fi, sound,
touchpad, and power drivers are commonly missing or
community-only, activation and updates are a separate fight,
and the same firmware work as Linux is needed for a worse
driver outcome. The Windows machine arriving Oct 30 is the
Windows machine. The Chromebook's sensible second life is
Linux, not Windows. If the owner insists on Windows-on-
Chromebook, that needs its own research pack and a named
reason — do not fold it into this pack as a silent option.

### 3.5 Backup / migration checklist — Windows Oct 30 move, before any Linux switch

Do not start the Chromebook Linux switch until every row below
is either DONE or explicitly waived by the owner. This checklist
is preparation; ticking a row requires evidence, not a guess.

| # | Item | Owner / crew | Evidence to record |
|---|---|---|---|
| 1 | Windows crew computer arrives, boots, Wi-Fi/Ethernet works | Owner at machine | Model photo, Windows version, RAM as-shipped (1×8 GB or 2×4 GB — decides the 16 GB upgrade) |
| 2 | Tailscale installed on Windows, joined the same tailnet, SSH reachable from Muse | Crew, owner signs in | Windows Tailscale IP, SSH test from Muse, no key in chat |
| 3 | Python + Pillow + agent-loop v2 test on Windows (one card, same as the workspace test) | Crew | One-card result, verdict, Latch checks |
| 4 | Pool index + laptop-control scripts copied to Windows | Crew | `pool-merged-2026-10-26.json` (8,658 distinct) present, `laptop-control/` scripts listed |
| 5 | Tunnel / cloud-serve decision: does cloud-serve move to Windows, stay on penguin until the switch, or pause? | Owner decision | Named decision, not assumed |
| 6 | Penguin home inventory: `~/`, `~/.ssh`, `~/.cloudflared`, `~/start-tunnel.sh`, `~/bridge-watch-loop.sh`, `~/vaio-build/` (if still present), `~/crew-work`, `~/Downloads` | Crew via SSH, read-only | File list + sizes, no deletions in this step |
| 7 | Drives verified, not formatted: Seagate 1.8 T "Cauldron" (master), Samsung SSD 238 G, Potion's Files 1.9 T, Vaio SD sdc 7.5 G (separate job — do not use Vaio SD for the Chromebook install) | Crew via SSH, owner confirms names | `lsblk` + `blkid` at migration time, names re-confirmed that day |
| 8 | Penguin ping-check cron: keep, repoint, or remove? | Owner decision | If penguin becomes Linux, the cron's SSH target changes; if penguin is retired, remove the cron. Do not leave a cron pinging a dead host. |
| 9 | What, if anything, on penguin must survive that is NOT on a drive or in the workspace? | Owner | Named list, or "nothing" in writing |
| 10 | Chromebook model / board / host RAM / eMMC recorded (§3.6) | Owner at machine | Settings > About ChromeOS screenshot or sticker photo, board name if shown |

**Drives are never the backup for the Chromebook switch.**
The drives hold the pool and backups; they are not to be
formatted, partitioned, or used as the Linux installer target
unless the owner names that exact drive for that exact purpose.
The Linux installer USB is a separate, named USB stick.

### 3.6 Model / driver checks still needed (open questions, not guesses)

The crew cannot answer these from inside the Crostini guest
alone. The owner must supply them at the machine, or the crew
must check them from a live USB boot (option C) before any
install:

1. **Exact Chromebook model + board name.** Settings > About
   ChromeOS, or the sticker on the bottom, or `chrome://system`
   board field. Without the board name, MrChromebox support
   cannot be checked.
2. **Host RAM and storage.** Guest RAM (2.7 Gi) is not host RAM.
   Host RAM decides whether full Linux will feel roomy or
   still tight, and eMMC size decides whether a dual-boot
   partition is even feasible.
3. **Wi-Fi chip, sound, touchpad.** These are the three
   Chromebook drivers that most often break on full Linux.
   A live-USB trial (option C) that tests Wi-Fi + sound +
   touchpad + suspend/resume for a day is the cheap proof
   before any install.
4. **Is developer mode already on?** If it is, the path is
   shorter. If it is not, turning it on wipes local ChromeOS
   data — another reason the Windows migration comes first.
5. **MrChromebox support for this board.** Check the
   MrChromebox device list for this exact board before
   promising UEFI dual boot or full Linux. If the board is
   not listed, do not promise either; the live-USB trial is
   still the safe test.
6. **Does the owner need any ChromeOS-only app on this
   machine after the switch?** If yes, name it. If no, the
   full-Linux recommendation stands.
7. **What Linux distribution?** Default proposal, to be
   confirmed after the model check: Debian Bookworm-based
   (matches the Vaio Puppy lineage and the crew's Debian
   tooling) or Ubuntu LTS (broader Chromebook driver
   coverage). Do not pick a distribution until the board
   check is done — the board, not preference, decides it.

### 3.7 Owner-at-machine steps, in order (full-Linux path, after migration)

**Stop points are real stops.** Do not proceed past a stop
point without the owner's yes for that step, even if the
previous step went well.

1. **Confirm the migration is done** (§3.5 rows 1–5, 8).
   Windows is reachable from Muse, the pool index is on
   Windows, and penguin is no longer the only copy of anything
   that matters.
2. **Record the model** (§3.6, items 1–4). Photo/screenshot,
   board name, host RAM/eMMC.
3. **Trial boot from USB (option C, no install).** Crew prepares
   the installer/live USB in the workspace; owner plugs it in,
   boots from USB, tests Wi-Fi, sound, touchpad, suspend.
   If the trial fails on Wi-Fi or touchpad, STOP — do not
   install, report the failure, and revisit the distribution
   or the board check.
4. **Backup confirmation.** Owner confirms in writing: "nothing
   on penguin that is not already on Windows / a drive / the
   workspace needs saving", or names what does.
5. **Developer mode on** (owner taps at the machine, ChromeOS
   recovery screen, Ctrl+D or the on-screen equivalent for
   this model). This wipes local ChromeOS data — that is why
   steps 1 and 4 come first. Record the exact key sequence
   for this model; do not copy another model's sequence.
6. **Firmware, only if needed for the chosen install path.**
   If the installer boots from USB without a firmware flash,
   do not flash. If UEFI is needed, run the MrChromebox
   firmware script from the official source, owner typing,
   and record the before/after firmware version. Never flash
   from a copied script in chat, never flash a different
   board's firmware.
7. **Install.** Owner boots the installer USB, selects the
   target disk (the Chromebook's internal storage — name it
   from the installer's disk list, never a plugged-in drive
   by guess), chooses full-disk Linux (recommended path) or,
   only if dual boot was re-chosen with a named reason, the
   partitioned layout from the reviewed plan. No other drive
   is plugged in during install, to remove the wrong-disk
   risk entirely.
8. **First-boot checks (owner + crew together).**
   Wi-Fi, `python3 --version`, `free -m`, `df -h`, `lsblk`,
   Tailscale install + `tailscale up --ssh` (owner signs in),
   SSH test from Muse to the new Linux IP, bridge-watch v2
   install (now as a native service, not a Crostini guest
   loop — the vshd checks become moot and should be removed
   or replaced with native equivalents).
9. **Restore.** Laptop-control scripts, tunnel config (new
   tunnel token only if the old one is retired — never rotate
   a working tunnel token to "clean up"), pool index, and
   the Vaio SD job's status (separate — the Vaio SD is not
   touched by the Chromebook install).
10. **Retire the old checks.** Remove or repoint
    `penguin-ping-check` to the new host, remove the Crostini
    bridge-watch loop, and record the new host's SSH/Tailscale
    details in memory. Do not leave two ping checks running
    against the same name.

**Dual-boot variant, only if re-chosen:** insert, after step 6,
a reviewed partition plan (ChromeOS partition size kept,
Linux partition size, shared data partition or none), and a
recovery plan (ChromeOS recovery USB made *before* resizing,
kept by the owner). If the recovery USB is not made, do not
resize. This variant is not the recommended path (§3.3).

---

## 4. Crew lanes working together in the loop — who does what

One loop, one queue, one writer at a time. No lane deletes,
formats, flashes, or installs anything in this pack.
Preparation only. Every lane's output is a file or a log the
next lane can read, never a live change to penguin.

| Lane | Owns in this loop | Must NOT do in this pack |
|---|---|---|
| **Potion — orchestrator** | Holds the plan, the owner order, and the stop points. Spawns lanes, folds their reports into this pack, talks to the owner, and is the only lane that asks the owner for a yes. | Never claim a bridge fix, a dual-boot install, or a deletion that did not happen. Never re-enable alerts silently. |
| **Index — research / logs** | Reads the logs on file, the previous-boot journal, the ping-check state, and the model/driver sources once the model is known. Keeps the facts table in §1 current. | Never invent a log line, a model, or a driver result. Every fact cites its file or command. |
| **Pip — scripts / test harness** | Writes watchdog v2 (§2.4) in the workspace, writes the mock test harness, and writes the installer-USB preparation checklist. Tests in mock mode first. | Never install a script on penguin, never run a live tailscaled-kill test without an owner yes for that exact test. |
| **Nickel — flaw / safety gate** | Reads every script and every owner-step for a flaw: a restart without a rate limit, a deletion path, a guessed device name, a token in a log, a claim that the guest fixed the bridge. Nickel's dissent is a stop, not a comment. | Never approve its own script. Nickel examines; Pip writes; Latch examines again. |
| **Noor — plain-words owner steps** | Turns §3.7 into the exact taps the owner will do at the machine, in plain words, one tap per line, with a stop point after each risky step. | Never write a tap sequence for a model that has not been identified. "Ctrl+D" for one board is not a universal instruction. |
| **Wick — docs / pack** | Keeps this pack, the migration checklist (§3.5), and the installer guide in one place, with dates, so the next lane does not work from a stale copy. | Never publish a doc as a live change. Docs are preparation until the owner says "go". |
| **Latch — final examiner, edits nothing** | Reads the finished pack and the finished watchdog v2 script against §1–§3, checks every restart path, every device name, and every claim, and either passes it or sends it back with the exact failing line. Latch never edits the script or the pack. | Never fix a flaw by editing it in place. A Latch pass with edits is not a pass. |
| **Lens / Gauge — measurement** | Measures before/after for any live test that is later approved: RAM available, load, disk %, tick counts, gap length in minutes. Numbers only, no verdicts from numbers alone. | Never measure by guessing. If a number was not read from a command, it is not in the report. |
| **Juno / Milo / Ziggy / Penny — not in this loop** | No art, game, or store work in the bridge/dual-boot loop. Their lanes stay in the app/pool work and do not touch penguin. | — |

**Loop rules, carried from the distributed crew map:**

- One queue file, one lane writes at a time; a job is claimed
  (name + time in the log) before work starts and released when
  done or after a timeout. No two lanes work the same job.
- If a device goes offline, its claimed jobs sit. They are not
  re-claimed until the timeout, and no lane invents a result
  for them.
- No lane counts as done until Latch checks it, then the owner
  checks it. Same gate as every other lane, every time.
- The loop's shared state for *this* pack is this file plus
  `~/workspace/laptop-control/ping-check-state.json` and
  `~/bridge-watch.log` / `~/bridge-vitals.jsonl` on penguin
  (once v2 exists). Do not duplicate state into a second file
  that can drift.
- **Fix-not-alert is the loop's reporting rule for penguin.**
  A lane that "alerts" the owner about penguin being down
  instead of fixing what it can, or logging what it cannot,
  has broken the loop's rule. The owner can change that rule
  with a new yes; no lane changes it alone.

---

## 5. What is already done, what is next, and what is NOT next

**Already done (evidence on file, Oct 26 late evening):**

- AI loop v2 test, workspace only: Inconclusive (honest guardrail),
  Alakazam BS 1, SAM box 19/16–584/813, Baseten failed this run
  (empty response) with Meta Spark 1.3 fallback, art checked OK,
  Latch checks all true. Output in
  `playground/agent-loop/run-v2-2026-10-26-night/`.
- Penguin safe deletion: journal + apt cache + Docker disable +
  apt timers (see §1.1). SSH verified still OK after.
- Penguin ping check: created, then updated to fix-not-alert,
  verified by reading its saved body back.
- Vaio SD staging (separate job, running at pack-writing time):
  ISO copying to a persistent `~/vaio-build/` on penguin, package
  copied, checksum + sdc re-confirmation + watchdog install still
  to be reported by that job. **Do not touch that job from this
  pack, and do not use the Vaio SD for the Chromebook install.**

**Next, in owner order:**

1. Watchdog v2 spec → workspace script → Nickel review →
   Latch review → owner yes for that exact file → install.
2. SD staging job reports; SD write only on a fresh owner yes
   naming sdc (name changed since the original sdb approval).
3. Windows computer arrives Oct 30 → migration checklist §3.5.
4. Chromebook model recorded → driver/board check → live-USB
   trial → owner decision: full Linux (recommended) vs dual
   boot (only with a named reason) vs stay on stripped Crostini.
5. Only then: owner-at-machine steps §3.7.

**NOT next (do not start, even if a lane finishes early):**

- No dual-boot install, no firmware flash, no full-Linux install
  before deletion + Windows migration + model check.
- No Windows-on-Chromebook work.
- No deletion beyond the safe list already done, except on a
  fresh owner yes naming the exact item.
- No re-enabling of penguin alerts, no rotation of the tunnel
  token, no formatting of any drive.
- No claim that the bridge is "fixed" — v2 + ping check make it
  *managed and measurable*, with a host-side limit that only
  the owner at the machine can clear.

---

## 6. Open questions — need the owner, or the Chromebook model

1. **Chromebook model / board name?** (see §3.6.1) — blocks the
   distribution and MrChromebox checks.
2. **Host RAM / eMMC size?** — blocks the dual-boot feasibility
   call.
3. **Is developer mode already on?** — changes the step count,
   not the order.
4. **Any ChromeOS-only app that must survive on this machine?**
   — the only thing that would flip the recommendation from
   full Linux back to dual boot.
5. **Distribution preference, once the board is known?**
   Debian Bookworm-based vs Ubuntu LTS — crew proposes, owner
   decides, board decides the tie-break.
6. **Tunnel / cloud-serve home after migration?** Windows,
   penguin-until-switch, or paused — owner decision (§3.5.5).
7. **Is the crew browser route dead?** Guest chromium profile
   and `~/crew-extensions/` were not present at inventory time.
   If dead, guest chromium becomes a removal candidate in a
   later, separately-approved pass — not in this pack.
8. **What to do with the failing `cauldron-keepawake` service?**
   Fix or disable — small, not a RAM win, but a broken loop
   should not be carried into a new install unexamined.
9. **Is Docker needed again on penguin / Windows?** It is
   disabled, not uninstalled, on penguin. If Docker is planned
   for the Windows migration, say so before any uninstall
   discussion.
10. **Vaio SD write — owner yes naming sdc?** Separate job,
    but it shares penguin's SSH road and the owner's attention.
    Do not let the Chromebook switch and the Vaio write
    compete for the same evening without the owner choosing
    which goes first.

---

## Sources on file (this pack cites only these, plus the task brief)

- `~/workspace/laptop-control/bridge-watch-loop.sh`
- `~/workspace/laptop-control/ts-watchdog.sh`
- `~/workspace/cron.d/minutely/penguin-ping-check__interval@5m.md`
- `~/workspace/laptop-control/ping-check-state.json`
- `~/workspace/fake-check/distributed-crew-map-2026-10-26.md`
- `~/workspace/fake-check/vaio-puppy-setup-2026-10-26.md`
- `~/workspace/fake-check/vaio-usb/README-vaio-usb-2026-10-26.md`
- AGENTS.md lessons: Oct 23 road-dead ≠ guest-dead, Oct 23
  per-port forwarding, Oct 26 fan/hub power, Oct 26 /tmp wipe.
- Oct 26 late-evening SSH-verified facts in §1.1 (penguin
  100.71.87.4, RAM, disk, journal/apt/Docker results, sdc shift).

*End of pack. Preparation only. No penguin change, no firmware
change, no dd/format, no deletion was made by writing this pack.*
