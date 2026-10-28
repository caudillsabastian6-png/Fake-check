# Multi-backend roles — SSD + Seagate + Cloudflare Workers — Oct 28, 2026

Design doc, playground only. No live change is made by this file.
The live backend today is Penguin home via the Cloudflare Tunnel
(`api.cardcauldrontcg.com` → Penguin `localhost:8766`). That stays
the live writer until a move is separately approved.

## 1. Verified facts (do not relitigate in this doc)

| Piece | Verified fact |
|---|---|
| SSD | /dev/sda, LABEL "SSD", 238.5G, vfat, mounted /mnt/ssd-238, root-owned. The guest user CANNOT write directly (vfat ignores chown/uid remounts); root/sudo CAN. Today it is a backup target via a 15-minute `sudo cp` cron, verified in sync with the live DB. |
| Seagate Cauldron | /dev/sdd1, LABEL "Cauldron", 1.8T/1.9T, exfat, /mnt/cloud-master. Remount read-write FAILED Oct 28, 2026. From the guest it cannot be a live writer. Treat it as read-only from the guest until a remount is proven, never assumed. |
| Penguin home (live writer today) | `~/card-cauldron-backend/` — app.py (stdlib only, no pip, no Pillow, no numpy), backend.db (~28 KB, Oct 28 11:48), start.sh, 15-min backup-to-SSD cron. Health: ok, prototype true, live false, host penguin-ssd-backend. |
| Cloudflare Workers | Undeployed. Worker source exists in playground (`backend-worker-2026-10-28/worker.js`, name `card-cauldron-backend`, D1 binding commented out). Free tier: 100,000 requests/day (not 10,000). A wrangler dev attempt failed on shell backgrounding, not on code. |
| Cloudflare Tunnel | `card-cauldron-cloud`, id c5709615-…, healthy, origin Penguin. Routes: cloud → :8080 (directory listing, NOT the backend), api → :8766 (the backend). Tunnel token lives on Penguin only — never print, rotate, or copy it. |
| G1 | HP EliteDesk 800 G1 Mini, arrives by Fri Oct 30, 2026. RAM/display route settled. Not yet in hand, so it cannot be the live host today. |

## 2. The one rule that governs everything

**One live writer. Everything else is a copy, a cache, or an edge.**

Three simultaneous live writers (Penguin SQLite + SSD file + Worker
D1) would split truth: a leaderboard score or referral claim could
land in one store and not the others, and there would be no
authoritative answer to "did this user already claim this?". Until a
single database is chosen as truth with the others as replicas, the
roles below are the only safe arrangement.

## 3. Proposed roles

### Penguin home — LIVE WRITER (today, unchanged)
- Owns: backend.db (leaderboard, feedback, referrals), all POST
  endpoints, all uniqueness rules (one code per owner, one claim per
  friend, one score row per post).
- Why it stays writer for now: it is the only host that already runs
  the code, holds the data, and is reachable via the Tunnel. Moving
  the writer is a migration with a cutover checklist, not a config
  tweak.
- Weaknesses, stated: a Chromebook guest (sleep, reboot, bridge
  outage), stdlib-only (no Pillow matcher, no numpy), and a single
  point of failure. Those are arguments for a standby, not for three
  writers.

### SSD — BACKUP + IMAGE-POOL STORE (not a live writer yet)
- Owns: the 15-minute backup copy of backend.db (already working),
  plus the image pool (pool v2 files, crops, hashes) as a store the
  backend can READ from.
- Why not a live writer today: the guest cannot write to vfat
  directly; every write needs sudo, which makes a per-request live
  writer fragile and unauditable. The sudo-cp backup is the right
  shape for vfat: infrequent, atomic (copy to temp, then rename),
  verified after each run.
- Path to live writer: re-evaluate at G1 arrival (Oct 30). If the
  backend moves to G1 (a real Linux host, not a Chromebook guest),
  the SSD can be mounted with proper ownership and become a live
  writer candidate — but only after a proven mount + write test +
  a migration that moves backend.db intact, referral tables included.

### Seagate Cauldron — COLD ARCHIVE, READ-ONLY FROM THE GUEST
- Owns: long-term archive copies (pool snapshots, DB snapshots,
  original photos), written rarely and deliberately, never per-request.
- Why not a writer: the Oct 28 remount-rw failure is unresolved.
  Until a remount is proven from the guest, any design that needs
  Seagate writes will silently fail. Archive writes, if ever needed,
  happen from a host that can actually mount it rw, with the drive
  identified by size + label + UUID first — never by letter alone.
- Never format any drive by letter. Never format Potion's Files
  (DA6E-295E) or Seagate Cauldron (EEDE-FDE7). That rule survives
  every backend change.

### Cloudflare Workers — PUBLIC EDGE, NOT A WRITER (first deployment)
- Owns, when deployed: rate limiting, auth-token checks (for
  protected reads like GET /feedback/list, which today has NO
  owner-key), caching of public leaderboard reads, hiding the
  origin (Penguin IP/tunnel) from the public, and honest error pages
  when the origin is down.
- Does NOT own, in its first deployment: leaderboard writes,
  referral claims, feedback writes, or any uniqueness rule. Those
  proxy through to Penguin, the single writer. A Worker that also
  writes to D1 while Penguin writes to SQLite is the three-writer
  split-truth failure in §2, just with nicer branding.
- Later, IF a single database is chosen (e.g. D1 becomes truth and
  Penguin becomes a replica, or vice versa), the Worker can graduate
  to writer — but that is a migration with its own approval, data
  move, and cutover test, not a flag flip.
- Cost check: 100k requests/day free tier. The demo's leaderboard
  traffic is far below that today; the edge role costs $0 at
  current scale. That does not make Workers free forever — it makes
  the edge role cheap to try.

## 4. How a request flows in the proposed arrangement

1. Phone/demo → `api.cardcauldrontcg.com` → Worker edge.
2. Worker: rate-limit check → (for protected routes) auth check →
   cache check for public GETs (leaderboard top, pool stats).
3. Cache miss / any POST → Tunnel → Penguin app.py (the writer).
4. Penguin writes backend.db, returns the result.
5. Worker caches the public GET result briefly, returns it.
6. Every 15 minutes, Penguin's cron copies backend.db to the SSD
   (sudo cp, verify after copy). Seagate gets a manual snapshot
   only when the owner names a snapshot point.

## 5. Failure modes and what the user sees

| Failure | User sees | Recovery |
|---|---|---|
| Penguin asleep / rebooted / bridge down | Leaderboard "offline" message (honest, never a fake board) | Penguin restart via start.sh + health check; SSD backup is the restore point. |
| Tunnel down | Same honest offline message | Tunnel health check; token is never rotated to fix this without owner approval. |
| SSD backup fails | Nothing user-visible; an alert in the backend log | Next 15-min run retries; live DB is unaffected (backup is a copy, not the writer). |
| Worker down (edge only) | Origin still reachable directly only if the owner allows it; otherwise offline message | Worker redeploy; Penguin is untouched. |
| Seagate unavailable | Nothing user-visible (archive only) | No action; archive is not on the request path. |

## 6. Re-evaluation point: G1 arrival, Oct 30, 2026

When G1 is in hand, re-decide in this order, with a fresh owner yes
per move: (1) check RAM layout and SSD/WiFi/power; (2) move the
backend code + backend.db (referral tables included) to G1 and
re-test; (3) test SSD as a G1-mounted live store (proper ownership,
write test, no sudo-per-request); (4) only then consider promoting
Workers from edge to writer, or keeping Penguin as standby. Do not
pre-commit to any of those moves in this doc — each needs its own
test evidence.
