# First-boot checklist — one script + the few things only the owner can do

**Goal:** First boot into Linux needs as little owner work as possible. This checklist is short on purpose: run one script, then do the owner-only steps, then done.

## Before first boot (owner at the Chromebook, before any wipe)

- [ ] Backup verified: Seagate backup (SSD + penguin home) verified by file count + bytes — NOT just copied. See loop pack §4. If not verified, STOP before developer mode.
- [ ] ChromeOS recovery USB made for HP 11A G8 EE / BARLA, labeled, kept separate from the installer SD.
- [ ] Installer SD verified: Debian 12 Bookworm XFCE live, checksum verified, written to sdc by the installer agent, readback verified.
- [ ] All external drives unplugged except the installer SD during install.

## First boot — the one script

- [ ] Install Linux to internal 32 GB eMMC (owner at machine: developer mode, write-protect, firmware, trial boot, install — loop pack §6). This pack does NOT do this step.
- [ ] Reboot without the SD, log in.
- [ ] Copy `chromebook-setup-pack/` onto the new host (from the second partition/folder, or from Seagate/workspace).
- [ ] Run: `bash first-boot-setup.sh`
  - It installs: Python/Pillow, git, curl, rsync, htop; Tailscale + SSH auto-start; cloudflared note; timezone America/New_York; AMD firmware; agent loop restore; bridge-watch v2 copy; journal/apt cleanup; Tailscale-only SSH firewall instructions.
  - It stops on first error. If it stops, read the last step printed — do not re-run blindly past a failure.

## Owner-only steps after the script (cannot be pre-done — see below)

- [ ] **Tailscale login:** run `sudo tailscale up --ssh`, complete the login, record the new tailnet IP, tell Potion. Test SSH from Muse.
- [ ] **Tunnel secret, ONLY if tunnel home is this host:** via secure login, create `~/.cloudflared/tunnel-token` (and service-token file if needed). Never paste a token into chat, a script, or the SD. Then run `./start-tunnel.sh` if tunnel home is this host; if tunnel home is Windows/paused, skip this step entirely.
- [ ] **Firmware reboot check:** if the script installed AMD firmware, reboot, then check Wi-Fi connects, sound plays, touchpad works.
- [ ] **Bridge-watch v2 start:** `nohup ~/bridge-watch-v2.sh >> ~/bridge-watch.log 2>&1 &`, then verify its first vitals tick in `~/bridge-watch.log`.
- [ ] **First-boot checks with Potion:** free/df/lsblk, Python version, Tailscale IP, SSH test, agent loop test run, bridge-watch tick. Latch-style: no check counts until it is seen, not just run.

## What CANNOT be pre-done and why

| Cannot be pre-done | Why |
|---|---|
| Tailscale login/auth | Needs the owner's Tailscale account login in a browser at first boot. A login cannot be baked into a script or an SD without storing a credential, which this pack refuses to do. |
| Any secret/token/key/password entry | Cloudflared tunnel token, Cloudflare Access service token, any app key — entering them before first boot would mean writing them into a file on the SD, where anyone with the SD could read them. They are entered via secure login at first boot only. |
| The actual Chromebook install itself | Developer mode wipes the machine, write-protect needs a SuzyQ cable or battery disconnect at the machine, firmware flashing needs the owner present, and trial boot needs eyes on the real hardware (Wi-Fi, sound, touchpad, suspend). No script can do those from the workspace. |
| Wi-Fi/GPU firmware proof | The script can install AMD firmware, but only a reboot + live Wi-Fi check on BARLA proves it works on this exact board. |
| Backup verification | A copy is not a backup until count + bytes are checked against the source. That check needs the real source drive mounted, which was blocked (empty guest folders) until ChromeOS mounts/shares it. |

## What is NOT in this checklist, on purpose

- No voice/camera setup or auto-start (future Windows lane, cameras OFF now).
- No auto-install, auto-erase, auto-format, or auto-delete of any drive.
- No secret entry in chat, in a script, or on the SD.
- No second script to run after the first — if a step above fails, stop and report it, do not start a different script to work around it.
