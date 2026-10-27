# Chromebook Linux Setup Pack — ready to go, workspace only

**For:** HP Chromebook 11A G8 EE, board BARLA, AMD Stoneyridge, 4 GB RAM, 32 GB eMMC, Debian 12 Bookworm XFCE
**Location in this workspace:** `fake-check/chromebook-setup-pack/`
**Status:** Assembled in workspace Oct 26, 2026. **NOT written to any drive by this pack.** The installer agent may place this folder as a second partition / separate folder alongside the Debian ISO on sdc AFTER the ISO write is verified — see "Placement" below. This pack does not write to sdc itself.

## What is in here

| File | What it does | Secrets? |
|---|---|---|
| `first-boot-setup.sh` | ONE script for first boot: timezone, base tools, Python/Pillow, AMD firmware, Tailscale + SSH auto-start, cloudflared binary note, agent loop restore, bridge-watch v2 copy, journal/apt cleanup, Tailscale-only SSH firewall instructions | NO — no token, key, or password in it |
| `CHECKLIST.md` | Short owner checklist: one script + the few things only the owner can do at first boot | — |
| `backup-to-seagate.sh` | Backup to Seagate by label Cauldron + UUID EEDE-FDE7, never by sd letter, never deletes a source, never formats anything | NO |
| `bridge-watch-v2.sh` | New host-health watchdog (flock, vitals JSONL, memory thresholds, Tailscale restart only if dead, never kills tailscaled/sshd/watchdog, never auto-remounts rw) | NO |
| `start-tunnel.sh` | Adapted tunnel starter: reads `~/.cloudflared/tunnel-token` ONLY if the owner created it, exits cleanly if missing, never prints a secret | NO value in the file |
| `agent_loop_v2.py`, `agent_loop.py` | Agent loop, copied from workspace/penguin vaio-build package | NO |
| `pool-merged-2026-10-26.json` | Pool index, 8,658 distinct, copied from workspace | NO |
| `tells_v2.py` | Tells v2 image comparison, copied from workspace playground | NO |
| `penguin-originals/bridge-watch-loop-v1.sh` | Old Crostini bridge-watch v1, for reference only — do NOT run as-is on full Linux; v2 replaces it | NO |
| `penguin-originals/cloud-serve.sh` | Original local file server (localhost:8080, from `/mnt/cloud-master` on penguin) — reference only; update the serve directory for the new host before use | NO |
| `penguin-originals/cloud-sync.sh` | Legacy sync script (voice/porch paths are retired — voice OFF now) — reference only, do NOT run blindly | NO |
| `penguin-originals/cloud-access-fetch.sh` | Cloudflare Access fetch script — reads `~/.cloudflared/service-token.env` ONLY if the owner created it; the script itself contains NO token value | NO value in the file |

**NOT copied, on purpose:** `~/.cloudflared/tunnel-token`, `~/.cloudflared/service-token.env`, `~/.cloudflared/cert.pem`, any `~/.ssh/` private key, any password. Those files live only on penguin (old host) and are NOT in this pack. The new host gets fresh secrets via secure login at first boot (see CHECKLIST).
**NOT copied, on purpose:** `crew-browser.sh` and crew extensions — that route is retired, extensions were absent at inventory.
**NOT in this pack:** the Debian ISO itself, any firmware, any OS install, any voice/camera service.

## Placement — coordinate with the installer agent, do not clobber the ISO write

1. Installer agent writes the Debian ISO to sdc, verifies it, and releases sdc. This pack does NOT touch sdc during that write.
2. Only after that release, the installer agent may place this `chromebook-setup-pack/` folder as:
   - (a) a second partition / free space on the same SD, ONLY if it confirms the ISO partitions are untouched and free space exists, or
   - (b) a separate folder (Seagate once §4 backup unblocks, or a second USB) copied in at first boot.
3. If (a) would resize, move, or overwrite any ISO partition, use (b). Never resize an installer partition to make room for this pack.
4. After placement, verify: ISO partitions still boot, setup pack folder is readable, and no file in the pack contains a secret (grep the pack for token/key/password values — the only matches should be the words "token" in comments explaining that no token is included).

## How first boot is supposed to go (one script, not a dozen steps)

1. Boot the new Linux host from the installer SD, trial-boot checklist first (loop pack §6.1), then install to internal 32 GB eMMC with all other drives unplugged.
2. Reboot without the SD, log in, copy `chromebook-setup-pack/` onto the new host (from the second partition/folder, or from Seagate/workspace).
3. Run ONE script: `bash first-boot-setup.sh` (or `chmod +x` then `./first-boot-setup.sh`).
4. Do the short owner steps in CHECKLIST.md — Tailscale login, tunnel secret if tunnel home is this host, firmware reboot + Wi-Fi re-check, bridge-watch start, SSH test from Muse.
5. That is it for setup. The OS install, the Tailscale login, and any secret entry are the only steps that cannot be pre-done (see CHECKLIST, "What CANNOT be pre-done and why").

## What CANNOT be pre-done — summary (full list in CHECKLIST.md)

- Tailscale login/auth (`tailscale up --ssh`) — needs the owner's account login at first boot, cannot be baked in.
- Any secret/token/key/password entry — cloudflared tunnel token, Cloudflare Access service token, any app key. Entered via secure login at first boot, never baked into the SD.
- The actual Chromebook install itself — developer mode wipe, write-protect disable, firmware flash, USB trial boot, and install all need the owner at the machine.
- Wi-Fi/GPU firmware verification — firmware can be installed by the script, but only a live reboot + Wi-Fi check on the real hardware proves it works.

## Safety rules carried from the loop pack

- One writer, one drive, one job. This pack writes no drive.
- Identify drives by label + UUID, never by sd letter.
- Never delete a source until a backup is verified by count + bytes.
- Fix-not-alert for the watchdog: log quietly, do not alert for routine recovery.
- Voice/camera auto-start is EXCLUDED. No voice listener, wake-word, webcam, or recording service is installed or auto-started by this pack.
