#!/bin/bash
# DRAFT-NOT-INSTALLED — V3, watcher for V1 (bridge-focused).
# DO NOT COPY TO PENGUIN. DO NOT RUN ON PENGUIN WITHOUT A FRESH OWNER YES
# NAMING THIS EXACT FILE, AFTER THE MOCK TESTS IN v3-spec.md §6 PASS.
#
# What this draft does: AUDIT / REPORT ONLY.
#   Reads V1's log lines and V1's process state, reads its own memory/load/
#   disk numbers, scans the last 5 minutes of journal for counts only,
#   checks corrected mount paths read-only, probes tunnel and cloud-serve
#   read-only, and writes its OWN report log + history file.
# What this draft NEVER does:
#   - edit, kill, restart, or start V1, V2, tailscaled, cloudflared,
#     cloud-serve, or any service
#   - mount, remount, format, dd, delete, or touch drive contents
#   - rotate a token, or put a secret in any log, vitals, or report line
#   - alert the owner (fix-not-alert: reports are files for the AI Loop
#     audit and the owner to read on a status check)
#   - claim a host-side bridge wedge is fixed (it cannot be fixed from
#     the guest; BRIDGE-DISTRESS means owner action at the machine)
#
# TOP LAYER (owner update, Oct 27, 00:35 ET): the AI Loop watches over
#   the PROCESS of this script, not just its output lines — its spec,
#   its tick logs once live, its upgrade proposals, and whether it
#   stayed audit-only / fix-not-alert / never-delete /
#   never-rotate-tokens. The AI Loop does NOT auto-edit this script,
#   does NOT restart it, and does NOT approve its own upgrades.
#   Owner approval is the final gate. There is NO V4.
#
# Paths below are PROPOSALS for a future install, not live paths.
# In mock mode (WATCHDOG_V3_MOCK=1, WATCHDOG_V3_MOCK_DIR set), every read
# comes from the mock dir and every write goes to the mock output dir.
# Mock mode must never touch the live system.
set -u
V3_LOG="${V3_LOG:-$HOME/watchdog-v3.log}"
V3_HIST="${V3_HIST:-$HOME/watchdog-v3-history.jsonl}"
V3_LOCK="${V3_LOCK:-/tmp/watchdog-v3.lock}"
V1_LOG="${V1_LOG:-$HOME/bridge-watch.log}"
SHARED_LOG="${SHARED_LOG:-$HOME/bridge-watch.log}"
MOCK="${WATCHDOG_V3_MOCK:-0}"
MOCK_DIR="${WATCHDOG_V3_MOCK_DIR:-}"

# --- single-instance guard (own lock only; never locks V1/V2's files) ---
if [ "$MOCK" != "1" ]; then
  exec 9>"$V3_LOCK" || exit 1
  flock -n 9 || { echo "watchdog-v3 already running, exiting"; exit 0; }
fi

rotate_if_big() { # $1=file, 5 MB cap, same pattern as V2 vitals rotation
  if [ -f "$1" ] && [ "$(stat -c%s "$1" 2>/dev/null || echo 0)" -gt 5242880 ]; then
    mv "$1" "$1.1" 2>/dev/null || true
  fi
}

v3_log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$V3_LOG"; }

# --- mock-aware readers: in mock mode, read mock files only ---
read_avail_mb() {
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/avail_mb.txt" 2>/dev/null || echo 0
  else free -m | awk '/^Mem:/ {print $7}'; fi
}
read_load() {
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/load.txt" 2>/dev/null || echo 0
  else cut -d' ' -f1 /proc/loadavg; fi
}
read_disk_pct() {
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/disk_pct.txt" 2>/dev/null || echo 0
  else df / | tail -1 | awk '{print $5}' | tr -d %; fi
}
v1_alive() { # read-only process check; never kills or starts anything
  if [ "$MOCK" = "1" ]; then [ -f "$MOCK_DIR/v1_alive" ]
  else pgrep -f bridge-watch-loop.sh >/dev/null; fi
}
v1_last_tick_age_s() {
  # Age of the newest V1 tick line in the log, in seconds; 999999 if none.
  local last line_ts now
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/v1_last_tick_age_s.txt" 2>/dev/null || echo 999999; return; fi
  last="$(grep 'bridge-watch tick' "$V1_LOG" 2>/dev/null | tail -1)"
  [ -z "$last" ] && { echo 999999; return; }
  line_ts="$(date -d "${last%% *} ${last#* }" +%s 2>/dev/null || echo 0)"
  now="$(date +%s)"
  echo $(( now - line_ts ))
}
journal_counts() { # counts only, last 5 min, never a full dump
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/journal_counts.json" 2>/dev/null || echo '{"vshd":0,"tailscaled":0,"oom":0,"hung":0,"usb":0}'; return; fi
  local v t o h u
  v="$(journalctl --since '-5 min' 2>/dev/null | grep -ciE 'vshd.*(broken pipe|error|fail)' || true)"
  t="$(journalctl --since '-5 min' 2>/dev/null | grep -ciE 'tailscaled.*(error|disconnect)' || true)"
  o="$(journalctl --since '-5 min' 2>/dev/null | grep -ciE 'oom|killed process' || true)"
  h="$(journalctl --since '-5 min' 2>/dev/null | grep -ciE 'hung task' || true)"
  u="$(journalctl --since '-5 min' 2>/dev/null | grep -ciE 'usb.*disconnect' || true)"
  printf '{"vshd":%s,"tailscaled":%s,"oom":%s,"hung":%s,"usb":%s}' "${v:-0}" "${t:-0}" "${o:-0}" "${h:-0}" "${u:-0}"
}
corrected_mounts() { # read-only directory presence, corrected share paths only
  local out="" p
  for p in "/mnt/shared/removable/Cauldron" "/mnt/shared/removable/SSD" "/mnt/shared/removable/potions fil"; do
    if [ "$MOCK" = "1" ]; then
      # mock: a file named after the share basename, under mock dir
      [ -f "$MOCK_DIR/mount_$(basename "$p" | tr ' ' '_')" ] && out="$out present" || out="$out absent"
    else
      [ -d "$p" ] && out="$out present" || out="$out absent"
    fi
  done
  echo "$out" | sed 's/^ //'
}
probe_tunnel() { # read-only pgrep; never runs start-tunnel.sh
  if [ "$MOCK" = "1" ]; then [ -f "$MOCK_DIR/tunnel_present" ] && echo present || echo absent; return; fi
  pgrep -f cloudflared >/dev/null && echo present || echo absent
}
probe_cloud_serve() { # read-only curl; never starts cloud-serve
  if [ "$MOCK" = "1" ]; then [ -f "$MOCK_DIR/cloud_serve_ok" ] && echo ok || echo fail; return; fi
  curl -sf -o /dev/null http://127.0.0.1:8080/ && echo ok || echo fail
}
v1_fail_count_last_hour() {
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/v1_fail_count.txt" 2>/dev/null || echo 0; return; fi
  grep 'FAIL' "$V1_LOG" 2>/dev/null | tail -100 | wc -l
}

# --- history for the trend rule: last 2 avail values, kept in the history file ---
trend_state() { # $1=current avail; echoes OK | TREND-WARNING based on last 2 lines
  local a1 a2 cur="$1"
  a1="$(tail -2 "$V3_HIST" 2>/dev/null | head -1 | grep -o '"avail_mb":[0-9]*' | cut -d: -f2 || echo "")"
  a2="$(tail -1 "$V3_HIST" 2>/dev/null | grep -o '"avail_mb":[0-9]*' | cut -d: -f2 || echo "")"
  if [ -n "$a1" ] && [ -n "$a2" ]; then
    local d1=$(( a1 - a2 )) d2=$(( a2 - cur ))
    if [ "$d1" -ge 200 ] && [ "$d2" -ge 200 ]; then echo "TREND-WARNING"; return; fi
  fi
  echo "OK"
}

while true; do
  rotate_if_big "$V3_LOG"; rotate_if_big "$V3_HIST"
  AVAIL="$(read_avail_mb)"; LOAD="$(read_load)"; DISK="$(read_disk_pct)"
  AGE="$(v1_last_tick_age_s)"; JCOUNTS="$(journal_counts)"
  MOUNTS="$(corrected_mounts)"; TUN="$(probe_tunnel)"; CS="$(probe_cloud_serve)"
  FAILS="$(v1_fail_count_last_hour)"; TREND="$(trend_state "${AVAIL:-0}")"
  if v1_alive; then
    if [ "${AGE:-999999}" -gt 900 ]; then V1_STATE="V1-STALE"; else V1_STATE="V1-ALIVE"; fi
  else V1_STATE="V1-MISSING"; fi
  if [ "${AVAIL:-9999}" -lt 300 ]; then MEM="CRITICAL"
  elif [ "${AVAIL:-9999}" -lt 500 ]; then MEM="WARNING"; else MEM="OK"; fi
  # Shared-log cap audit: report only, never rotate/truncate V1/V2's log here.
  LOG_SIZE="$(stat -c%s "$SHARED_LOG" 2>/dev/null || echo 0)"
  if [ "$LOG_SIZE" -gt 5242880 ]; then LOG_STATE="LOG-CAP-WARNING"; else LOG_STATE="OK"; fi
  v3_log "--- watchdog-v3 tick --- v1=$V1_STATE age=${AGE}s avail=${AVAIL}MB load=$LOAD disk=${DISK}% mem=$MEM trend=$TREND mounts=[$MOUNTS] tunnel=$TUN cloud-serve=$CS v1_fails_last_hour~$FAILS journal=$JCOUNTS shared_log=$LOG_STATE"
  printf '{"ts":"%s","v1_state":"%s","v1_last_tick_age_s":%s,"avail_mb":%s,"load":"%s","disk_pct":%s,"mem":"%s","trend":"%s","mounts":"%s","tunnel":"%s","cloud_serve":"%s","journal":%s,"shared_log":"%s"}\n' \
    "$(date -u +%FT%TZ)" "$V1_STATE" "${AGE:-999999}" "${AVAIL:-0}" "$LOAD" "${DISK:-0}" "$MEM" "$TREND" "$MOUNTS" "$TUN" "$CS" "$JCOUNTS" "$LOG_STATE" >> "$V3_HIST"
  [ "$MOCK" = "1" ] && break  # mock mode: one tick, then exit for inspection
  sleep 300
done
