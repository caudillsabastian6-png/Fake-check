#!/bin/bash
# Chromebook first-boot setup — Debian 12 Bookworm XFCE, BARLA 4GB / 32GB eMMC
# SAFE: no tokens, keys, or passwords are stored in this pack. Anything secret
# is entered by the owner at first boot, never written into these files.
# Usage (after installing Debian to the internal eMMC, as a normal user with sudo):
#   sudo bash /path/to/setup-pack/scripts/first-boot.sh
# Steps are idempotent where possible; re-running is safe except the
# Tailscale login step, which only needs to run once.
set -e
echo "=== Chromebook first-boot setup ==="
echo "Timezone: America/New_York"
sudo timedatectl set-timezone America/New_York || true
echo "--- apt update + base tools ---"
sudo apt-get update
sudo apt-get install -y git curl wget rsync htop python3 python3-pip python3-pil \
  openssh-server firmware-linux-nonfree 2>/dev/null || \
  sudo apt-get install -y git curl wget rsync htop python3 python3-pip python3-pil openssh-server
echo "--- Python packages (system pip, no secrets) ---"
python3 -c "import PIL; print('Pillow OK:', PIL.__version__)" || echo "Pillow check: install python3-pil above, or pip install Pillow in a venv"
echo "--- 32GB disk hygiene ---"
sudo journalctl --vacuum-size=100M || true
sudo apt-get clean || true
echo "--- SSH: Tailscale-only is set in tailscale-ssh-setup.sh (run next) ---"
echo "Next steps, in order:"
echo "  1. bash scripts/tailscale-ssh-setup.sh   # owner runs: sudo tailscale up --ssh, then approves the login URL"
echo "  2. bash scripts/backup-to-seagate.sh     # only after Seagate is mounted by LABEL, never by sd letter"
echo "  3. Copy agent-loop/, tells-v2/, pool/, bridge-watch/ to ~/ and start bridge-watch"
echo "  4. Cloudflared: install cloudflared, then enter the tunnel token AT FIRST BOOT ONLY"
echo "     (token is NOT in this pack; restore it from the owner's secure copy, never paste it here)"
echo "Done. No secrets were written by this script."
