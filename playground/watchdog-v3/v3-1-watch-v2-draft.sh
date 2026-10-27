#!/bin/bash
# DRAFT-NOT-INSTALLED — V3.1, watcher for V2 (host-health-focused).
# DO NOT COPY TO PENGUIN. DO NOT RUN ON PENGUIN WITHOUT A FRESH OWNER YES
# NAMING THIS EXACT FILE, AFTER THE MOCK TESTS IN v3.1-spec.md §6 PASS.
#
# What this draft does: AUDIT / REPORT ONLY.
#   Validates V2's vitals lines, tracks V2's tick freshness, re-derives
#   V2's memory/disk states from vitals and compares them to V2's log,
#   counts V2 restart lines per hour (audit counter — see below),
#   probes the checks V2 lacks (mounts corrected paths, tunnel,
#   cloud-serve) read-only, and writes its OWN report log + history.
# What this draft NEVER does:
#   - edit, kill, restart, or start V2, V1, tailscaled, cloudflared,
#     cloud-serve, or any service
#   - mount, remount, format, dd, delete, or touch drive contents
#   - rotate a token, or put a secret in any log, vitals, or report line
#   - alert the owner (fix-not-alert)
#
# TOP LAYER (owner update, Oct 27, 00:35 ET): the AI Loop watches over
#   the PROCESS of this script, not just its output lines — its spec,
#   its tick logs once live, its upgrade proposals, and whether it
#   stayed audit-only / fix-not-alert / never-delete /
#   never-rotate-tokens. The AI Loop does NOT auto-edit this script,
#   does NOT restart it, and does NOT approve its own upgrades.
#   Owner approval is the final gate. There is NO V4.
#
# RESTART COUNTER — READ THIS BEFORE READING THE CODE:
#   V2's header claims "max 3 restarts per service per hour", but V2's
#   code implements no counter (AI Loop audit §3, item 2). This draft
#   IMPLEMENTS THE COUNTER AS AN AUDIT COUNTER: it counts restart lines
#   and reports RESTART-RATE-VIOLATION when the count exceeds 3/hour.
#   It does NOT gate or suppress any restart, because this draft
#   restarts nothing. The gating block at the end of the tick loop is
#   COMMENTED OUT on purpose, so a reader can see what gating would
#   look like in a future owner-approved non-audit build, without this
#   draft performing it. Until that future build is approved, every
#   V3.1 report must say: "restart limit: reported, not enforced."
#   Alternative resolution, for the owner to pick (not picked here):
#   remove the max-3/hour claim from V2's header.
#
# <300 MB PAUSE CLAIM — READ THIS TOO:
#   V2 logs "pause non-essential jobs" below 300 MB but pauses nothing.
#   This draft AUDITS that claim: below 300 MB it reports
#   V2-CLAIM-UNIMPLEMENTED unless a shed record exists. It performs
#   no shed. The real shed order (crew browser first, then cloud-serve
#   pause, then batch jobs, never tailscaled/sshd/watchdog) is a
#   PROPOSAL in v3.1-spec.md §3.4, not code executed here.
#
# Paths below are PROPOSALS for a future install, not live paths.
# Mock mode: WATCHDOG_V3_1_MOCK=1, WATCHDOG_V3_1_MOCK_DIR set. Mock mode
# reads mock files only and writes to the mock output dir only.
set -u
V31_LOG="${V31_LOG:-$HOME/watchdog-v3-1.log}"
V31_HIST="${V31_HIST:-$HOME/watchdog-v3-1-history.jsonl}"
V31_LOCK="${V31_LOCK:-/tmp/watchdog-v3-1.lock}"
V2_VITALS="${V2_VITALS:-$HOME/bridge-watch-vitals.jsonl}"
V2_LOG="${V2_LOG:-$HOME/bridge-watch.log}"
MOCK="${WATCHDOG_V3_1_MOCK:-0}"
MOCK_DIR="${WATCHDOG_V3_1_MOCK_DIR:-}"

if [ "$MOCK" != "1" ]; then
  exec 9>"$V31_LOCK" || exit 1
  flock -n 9 || { echo "watchdog-v3.1 already running, exiting"; exit 0; }
fi
rotate_if_big() {
  if [ -f "$1" ] && [ "$(stat -c%s "$1" 2>/dev/null || echo 0)" -gt 5242880 ]; then
    mv "$1" "$1.1" 2>/dev/null || true
  fi
}
v31_log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$V31_LOG"; }

v2_alive() {
  if [ "$MOCK" = "1" ]; then [ -f "$MOCK_DIR/v2_alive" ]
  else pgrep -f bridge-watch-v2.sh >/dev/null; fi
}
last_vitals_line() {
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/vitals_last.txt" 2>/dev/null || echo ""
  else tail -1 "$V2_VITALS" 2>/dev/null || echo ""; fi
}
vitals_age_s() {
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/vitals_age_s.txt" 2>/dev/null || echo 999999; return; fi
  [ -f "$V2_VITALS" ] || { echo 999999; return; }
  local m now; m="$(stat -c%Y "$V2_VITALS" 2>/dev/null || echo 0)"; now="$(date +%s)"; echo $(( now - m ))
}
# Validate one vitals line: all fields present, numeric where numeric.
# Echoes VALID or VITALS-MALFORMED:<reason>. Never crashes on a bad line.
validate_vitals() {
  local line="$1"
  [ -z "$line" ] && { echo "VITALS-MALFORMED:empty"; return; }
  echo "$line" | grep -q '"avail_mb":[0-9]' || { echo "VITALS-MALFORMED:no-avail_mb"; return; }
  echo "$line" | grep -q '"load":"[^"]*"' || { echo "VITALS-MALFORMED:no-load"; return; }
  echo "$line" | grep -q '"disk_pct":[0-9]' || { echo "VITALS-MALFORMED:no-disk_pct"; return; }
  echo "$line" | grep -q '"tailscaled":"[^"]*"' || { echo "VITALS-MALFORMED:no-tailscaled"; return; }
  echo "VALID"
}
restart_count_last_hour() { # audit counter: count V2 restart lines, last hour window by log tail
  local svc="$1"
  if [ "$MOCK" = "1" ]; then cat "$MOCK_DIR/restart_count_${svc}.txt" 2>/dev/null || echo 0; return; fi
  # Note: V2's log shares ~/bridge-watch.log with V1; this counts lines
  # mentioning tailscaled restart in the recent tail as a proxy in this
  # draft. A future build must parse timestamps properly per hour window.
  grep -i 'tailscaled.*restart\|trying restart' "$V2_LOG" 2>/dev/null | tail -50 | wc -l
}
probe_mounts() {
  local out="" p
  for p in "/mnt/shared/removable/Cauldron" "/mnt/shared/removable/SSD" "/mnt/shared/removable/potions fil"; do
    if [ "$MOCK" = "1" ]; then
      [ -f "$MOCK_DIR/mount_$(basename "$p" | tr ' ' '_')" ] && out="$out present" || out="$out absent"
    else [ -d "$p" ] && out="$out present" || out="$out absent"; fi
  done
  echo "$out" | sed 's/^ //'
}
probe_tunnel() {
  if [ "$MOCK" = "1" ]; then [ -f "$MOCK_DIR/tunnel_present" ] && echo present || echo absent; return; fi
  pgrep -f cloudflared >/dev/null && echo present || echo absent
}
probe_cloud_serve() {
  if [ "$MOCK" = "1" ]; then [ -f "$MOCK_DIR/cloud_serve_ok" ] && echo ok || echo fail; return; fi
  curl -sf -o /dev/null http://127.0.0.1:8080/ && echo ok || echo fail
}
trend_state() { # same rule as V3: 3 ticks falling >=200 MB each
  local cur="$1" a1 a2
  a1="$(tail -2 "$V31_HIST" 2>/dev/null | head -1 | grep -o '"avail_mb":[0-9]*' | cut -d: -f2 || echo "")"
  a2="$(tail -1 "$V31_HIST" 2>/dev/null | grep -o '"avail_mb":[0-9]*' | cut -d: -f2 || echo "")"
  if [ -n "$a1" ] && [ -n "$a2" ]; then
    local d1=$(( a1 - a2 )) d2=$(( a2 - cur ))
    if [ "$d1" -ge 200 ] && [ "$d2" -ge 200 ]; then echo "TREND-WARNING"; return; fi
  fi
  echo "OK"
}

while true; do
  rotate_if_big "$V31_LOG"; rotate_if_big "$V31_HIST"
  LINE="$(last_vitals_line)"; VALID="$(validate_vitals "$LINE")"
  AGE="$(vitals_age_s)"
  AVAIL="$(echo "$LINE" | grep -o '"avail_mb":[0-9]*' | cut -d: -f2 || echo 0)"
  DISK="$(echo "$LINE" | grep -o '"disk_pct":[0-9]*' | cut -d: -f2 || echo 0)"
  TS="$(echo "$LINE" | grep -o '"tailscaled":"[^"]*"' | cut -d'"' -f4 || echo unknown)"
  if v2_alive; then
    if [ "${AGE:-999999}" -gt 900 ]; then V2_STATE="V2-STALE"; else V2_STATE="V2-ALIVE"; fi
  else V2_STATE="V2-MISSING"; fi
  if [ "${AVAIL:-9999}" -lt 300 ]; then MEM="CRITICAL"; PAUSE_CLAIM="V2-CLAIM-UNIMPLEMENTED:pause-below-300MB"
  elif [ "${AVAIL:-9999}" -lt 500 ]; then MEM="WARNING"; PAUSE_CLAIM="n/a"
  else MEM="OK"; PAUSE_CLAIM="n/a"; fi
  TREND="$(trend_state "${AVAIL:-0}")"
  RC="$(restart_count_last_hour tailscaled)"
  if [ "${RC:-0}" -gt 3 ]; then RATE="RESTART-RATE-VIOLATION:tailscaled:${RC}/hour:reported-not-enforced"
  else RATE="OK:${RC}/hour"; fi
  MOUNTS="$(probe_mounts)"; TUN="$(probe_tunnel)"; CS="$(probe_cloud_serve)"
  # Claim-gap report: V2's header claims tunnel/cloud-serve; its code does not check them.
  CLAIM_GAP="V2-CLAIM-GAP:tunnel,cloud-serve"
  v31_log "--- watchdog-v3.1 tick --- v2=$V2_STATE vitals=$VALID age=${AGE}s avail=${AVAIL}MB disk=${DISK}% tailscaled=$TS mem=$MEM trend=$TREND restart_rate=$RATE pause_claim=$PAUSE_CLAIM claim_gap=$CLAIM_GAP missing_checks_mounts=[$MOUNTS] missing_checks_tunnel=$TUN missing_checks_cloud_serve=$CS vitals_sequence=VITALS-NO-SEQUENCE"
  printf '{"ts":"%s","v2_state":"%s","vitals":"%s","vitals_age_s":%s,"avail_mb":%s,"disk_pct":%s,"tailscaled":"%s","mem":"%s","trend":"%s","restart_rate":"%s","pause_claim":"%s","claim_gap":"%s","mounts":"%s","tunnel":"%s","cloud_serve":"%s"}\n' \
    "$(date -u +%FT%TZ)" "$V2_STATE" "$VALID" "${AGE:-999999}" "${AVAIL:-0}" "${DISK:-0}" "$TS" "$MEM" "$TREND" "$RATE" "$PAUSE_CLAIM" "$CLAIM_GAP" "$MOUNTS" "$TUN" "$CS" >> "$V31_HIST"
  # --- FUTURE GATING, COMMENTED OUT ON PURPOSE (audit draft restarts nothing) ---
  # if [ "${RC:-0}" -gt 3 ]; then
  #   v31_log "RESTART-SUPPRESSED:tailscaled (would suppress a 4th restart in this hour in a future non-audit build)"
  # fi
  [ "$MOCK" = "1" ] && break
  sleep 300
done
