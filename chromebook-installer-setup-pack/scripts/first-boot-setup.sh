#!/bin/bash
# first-boot-setup.sh — Chromebook Linux first boot, ONE script.
# Run ONCE, on the already-installed Linux host (Debian 12 XFCE, HP 11A G8 EE / BARLA).
# This script does NOT install the OS, does NOT wipe, partition, flash, or format anything.
# It does NOT contain any token, API key, password, or private key.
# Secrets are entered separately by the owner at first boot (see CHECKLIST.md, step 4).
# Stops on first error. Prints each step. Safe to re-run the non-secret parts; it will
# skip steps that are already done.
set -e
echo "=== Chromebook Linux first-boot setup ==="
echo "Host: $(hostname)  Date: $(date)"
echo "[1/10] Checking system (no changes yet)"
free -h
df -h /
lsblk -o NAME,SIZE,LABEL
python3 --version || true
echo "[2/10] Timezone: America/New_York"
sudo timedatectl set-timezone America/New_York || sudo ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime || true
timedatectl 2>/dev/null | head -5 || date
echo "[3/10] Base tools: git curl rsync htop, Python3 + Pillow"
sudo apt update
sudo apt install -y git curl rsync htop python3 python3-pip python3-pil || sudo apt install -y git curl rsync htop python3 python3-pip
python3 --version
python3 -c "import PIL; print('Pillow', PIL.__version__)" || echo "Pillow check: install via pip/venv if needed (see README)"
echo "[4/10] AMD Stoneyridge non-free firmware (Wi-Fi/GPU on BARLA)"
# Debian non-free-firmware must be enabled for this board's Wi-Fi/GPU firmware.
# If this step changes firmware, reboot and re-check Wi-Fi before continuing to step 9.
sudo apt install -y firmware-linux firmware-linux-nonfree 2>/dev/null || echo "NOTE: firmware-linux not available in this repo set — enable non-free-firmware in /etc/apt/sources.list, apt update, retry. Wi-Fi re-check required after install."
echo "[5/10] Tailscale + SSH, auto-start on boot"
# Install Tailscale from the official Debian package if not present.
if ! command -v tailscale >/dev/null 2>&1; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi
sudo systemctl enable --now tailscaled || true
sudo apt install -y openssh-server || true
sudo systemctl enable --now ssh || sudo systemctl enable --now sshd || true
echo "NOTE: Tailscale LOGIN is NOT done by this script. Owner must run, at first boot:"
echo "  sudo tailscale up --ssh"
echo "Then test SSH to this host from Muse and record the new tailnet IP (it will NOT be the old Crostini IP)."
echo "[6/10] Cloudflared (binary only, NO token in this pack)"
if ! command -v cloudflared >/dev/null 2>&1; then
  echo "Install cloudflared from the official Cloudflare Debian package, then stop here for tunnel setup."
  echo "Tunnel token/config are entered by the owner via secure login at first boot — never baked into this pack."
  echo "See start-tunnel.sh in this pack: it reads ~/.cloudflared/tunnel-token ONLY if the owner created it, and exits cleanly if not."
else
  echo "cloudflared already present: $(cloudflared --version 2>/dev/null | head -1)"
fi
echo "[7/10] Agent loop v2 + pool + tells v2 (copied from this setup pack)"
mkdir -p ~/agent-loop
cp -u ./agent_loop_v2.py ./agent_loop.py ./tells_v2.py ./pool-merged-2026-10-26.json ~/agent-loop/ 2>/dev/null || cp ./agent_loop_v2.py ./agent_loop.py ./tells_v2.py ./pool-merged-2026-10-26.json ~/agent-loop/
ls -lh ~/agent-loop/
echo "[8/10] Bridge-watch v2 (host health, NOT the old Crostini bridge watcher)"
cp ./bridge-watch-v2.sh ~/bridge-watch-v2.sh
chmod +x ~/bridge-watch-v2.sh
echo "Start it with: nohup ~/bridge-watch-v2.sh >> ~/bridge-watch.log 2>&1 &"
echo "Or install it as a systemd service/timer — see README. Verify its first vitals tick in ~/bridge-watch.log."
echo "[9/10] Journal + apt cleanup for 32 GB eMMC"
sudo journalctl --vacuum-size=100M || true
sudo apt-get clean || true
df -h /
echo "[10/10] Firewall: Tailscale-only SSH (written, enabled, and to be tested)"
echo "If ufw is available, run (owner / sudo at first boot, after Tailscale is up):"
echo "  sudo ufw allow in on tailscale0 to any port 22"
echo "  sudo ufw enable"
echo "Do NOT open SSH to the whole internet. Test SSH from Muse via Tailscale before considering this step done."
echo ""
echo "=== First-boot setup script finished (non-secret parts) ==="
echo "STILL NEEDS THE OWNER (see CHECKLIST.md):"
echo "  1. sudo tailscale up --ssh  (login/auth — cannot be pre-done)"
echo "  2. Tunnel token/config via secure login, ONLY if tunnel home is this host (cannot be pre-done)"
echo "  3. Reboot after firmware step if firmware was installed, then re-check Wi-Fi, sound, touchpad"
echo "  4. Start bridge-watch v2 and verify its first tick"
echo "  5. SSH test from Muse, then Latch-style first-boot checks (loop pack §7)"
