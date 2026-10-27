# Chromebook Linux — first-boot pack (Debian 12 Bookworm XFCE, BARLA)

This pack lives on a SECOND partition of the installer card, separate from
the Debian live ISO partitions. Do not move, resize, or delete the ISO
partitions to make room for it — this partition was created only in the
free space after them.

## What is in here — no secrets
- scripts/first-boot.sh — timezone, apt base tools, Python/Pillow check, journal/apt cleanup for 32GB
- scripts/tailscale-ssh-setup.sh — installs Tailscale, enables SSH; login URL is approved by the owner at first boot
- scripts/backup-to-seagate.sh — copies by LABEL=Cauldron (UUID EEDE-FDE7), never by /dev/sdX, never deletes
- scripts/install-list.txt — full install list
- agent-loop/agent_loop_v2.py, agent_loop.py — card-checker loop (Meta/Baseten keys are NOT here; they live in Muse Secure Vault, enter/use them only via approved flows)
- tells-v2/tells_v2.py — image-to-image tells, estimates only
- pool/pool-merged-2026-10-26.json — 8,658 distinct pool index
- bridge-watch/bridge-watch-loop.sh (Crostini v1, reference only)
- bridge-watch/bridge-watch-v2.sh — full-Linux watchdog, vitals JSONL, memory thresholds, no deletions, no token rotation
- home-configs/start-tunnel.sh — starts cloud-serve + cloudflared; it READS a token file at runtime, the token itself is NOT in this pack
- home-configs/bashrc-penguin.txt — old penguin .bashrc banner/config, reference only
- home-configs/cloud-serve-scripts.txt — old cloud-serve scripts, reference only

## What the owner still has to do at first boot
1. Trial-boot from this card first (Wi-Fi, sound, touchpad, suspend). Stop if trial fails.
2. Install Debian to the internal 32GB eMMC only, with NO external drives plugged in during install.
3. Run scripts/first-boot.sh, then scripts/tailscale-ssh-setup.sh and approve the Tailscale login URL it prints.
4. Restore secrets from the owner's own secure copy, in the terminal only:
   - Cloudflare tunnel token (for start-tunnel.sh's ~/.cloudflared/tunnel-token file)
   - Any API keys, only via approved flows — never paste them into this pack
5. Run scripts/backup-to-seagate.sh only after the Seagate is mounted by label and its files are visible.
6. Copy agent-loop / tells-v2 / pool / bridge-watch to ~/ and start bridge-watch-v2.
7. Verify: `tailscale status`, SSH from Muse, `free -m`, `df -h`, `lsblk`.

## What is NOT in this task
- No Linux install on the Chromebook was done by the installer-card build.
- No firmware flash, no developer-mode change, no ChromeOS wipe was done here.
  Those are owner-at-machine steps, after backup, in the loop pack.
- Voice/camera auto-start is EXCLUDED. Cameras/voice stay OFF until a separate
  owner-approved lane, with per-camera/mic approval.

## Vaio note
The Puppy Linux ISO itself still exists in the workspace and in penguin
~/vaio-build/ (BookwormPup32-23.12-261003.iso, 610 MB). This card is now a
Chromebook installer, NOT a Puppy card. Puppy can be re-staged on this same
card later, in owner order: Chromebook first, Sony Vaio second.
