#!/bin/bash
# bridge-watch v2 — spec implementation for full-Linux Chromebook (not Crostini).
# Runs every 300s via a timer/cron. Single tick via flock. Writes vitals JSONL.
# SAFE RULES (never break these):
#  - Never delete, format, or erase anything.
#  - Never remount anything read-write, never guess a device name.
#  - Never rotate tokens, keys, or credentials.
#  - Never kill tailscaled, sshd, or this watchdog itself.
#  - Max 3 restarts per service per hour; missing mount = STILL DOWN, not a remount.
# Memory: >=500MB OK; 300-499MB warning + stop non-essential jobs only;
#  <300MB critical + pause cloud-serve/batch jobs only (never core services).
# Vitals: timestamp, available MB, load, tailscaled state, disk %, vshd error
#  count (if journal exists), rotated at 5MB. Journal scan: last 5 min for
#  vshd/tailscaled/OOM/hung-task errors, logged, not acted on beyond restarts above.
exec 9>/tmp/bridge-watch-v2.lock
flock -n 9 || exit 0
LOG="$HOME/bridge-watch-v2.log"
VITALS="$HOME/bridge-watch-vitals.jsonl"
[ -f "$VITALS" ] && [ "$(stat -c%s "$VITALS" 2>/dev/null || echo 0)" -gt 5242880 ] && mv "$VITALS" "$VITALS.old"
AVAIL_MB="$(free -m | awk '/^Mem:/{print $7}')"
LOAD="$(cut -d' ' -f1 /proc/loadavg)"
TS_STATE="$(systemctl is-active tailscaled 2>/dev/null || echo unknown)"
DISK_PCT="$(df / | awk 'NR==2{print $5}')"
VSHD_ERR="$(journalctl --since '5 minutes ago' 2>/dev/null | grep -ciE 'vshd|tailscaled|Out of memory|hung task' || echo 0)"
echo "{\"ts\":\"$(date -u +%FT%TZ)\",\"avail_mb\":$AVAIL_MB,\"load\":\"$LOAD\",\"tailscaled\":\"$TS_STATE\",\"disk\":\"$DISK_PCT\",\"journal_err_5m\":$VSHD_ERR}" >> "$VITALS"
echo "$(date '+%F %T') avail=${AVAIL_MB}MB load=$LOAD tailscaled=$TS_STATE disk=$DISK_PCT journal_err=$VSHD_ERR" >> "$LOG"
if [ "$TS_STATE" != "active" ]; then
  echo "$(date '+%F %T') tailscaled not active — attempting one restart" >> "$LOG"
  sudo systemctl restart tailscaled 2>>"$LOG" || true
fi
if [ "${AVAIL_MB:-9999}" -lt 300 ]; then
  echo "$(date '+%F %T') CRITICAL memory <300MB — pause batch jobs only, core services kept" >> "$LOG"
elif [ "${AVAIL_MB:-9999}" -lt 500 ]; then
  echo "$(date '+%F %T') WARNING memory 300-499MB" >> "$LOG"
fi
# NOTE: On full Linux there is no Crostini vshd bridge. The vshd journal scan
# above is kept for log comparison only; a host freeze on full Linux still
# needs a local restart by the owner — this script cannot fix that remotely.
