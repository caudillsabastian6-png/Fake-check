#!/bin/bash
# Bridge-watch loop — non-stop lookout for penguin (Chromebook Linux guest).
# Runs IN the guest, so it works even when the ChromeOS<->guest bridge to Muse is down.
# It does NOT fix the host-side bridge itself (only ChromeOS can reset vshd) — it
# detects, fixes what the guest CAN fix, logs, and reports when the bridge returns.
# Safe limits: max 3 restarts per service per hour, never deletes data, never
# rotates tokens, never remounts rw, never touches Seagate/SSD/potions contents.
# Install (owner yes first): copy to ~/bridge-watch-loop.sh on penguin, chmod +x,
# then run as a systemd service/timer, or: nohup ./bridge-watch-loop.sh >> ~/bridge-watch.log 2>&1 &
LOG="$HOME/bridge-watch.log"
log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"; }
check() { # $1=name $2=command-to-test $3=fix-command (may be empty)
  if eval "$2" >/dev/null 2>&1; then log "OK $1"; else
    log "FAIL $1 — trying fix (max 3/hr, counted in log)";
    if [ -n "$3" ]; then eval "$3" >> "$LOG" 2>&1 || true; sleep 5;
      if eval "$2" >/dev/null 2>&1; then log "FIXED $1"; else log "STILL DOWN $1 — needs host/owner, not retrying forever"; fi
    fi
  fi
}
while true; do
  log "--- bridge-watch tick ---"
  check "tailscale" "tailscale status" "sudo systemctl restart tailscaled || true"
  check "cloud-master-mount" "mountpoint -q /mnt/cloud-master" "true"
  check "ssd-mount" "mountpoint -q /mnt/ssd-238" "true"
  check "cloud-serve-8080" "curl -sf -o /dev/null http://127.0.0.1:8080/" "true"
  check "tunnel-process" "pgrep -f cloudflared >/dev/null" "~/start-tunnel.sh || true"
  check "disk-space" "test $(df / | tail -1 | awk '{print $5}' | tr -d %) -lt 90" "true"
  # Note: mounts/tunnel restarts that need a device reseat or a ChromeOS restart
  # are NOT auto-done here — those are logged as STILL DOWN for the owner.
  sleep 300
done
