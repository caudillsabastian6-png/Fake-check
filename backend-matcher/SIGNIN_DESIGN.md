# Sign-in design — backend — DESIGN ONLY, Oct 28, 2026

Playground design. No live deployment, no real user passwords, no
changes to the demo or the live Penguin backend. This document is
for owner + Latch review before anything is built live.

## 1. Goal

Replace the demo's local-only sign-in (a gate on the device, no
server account) with a real server-side account, so that coins,
referral counts, leaderboard names, and check history can be
account-bound instead of device-bound — without ever letting a
password touch the demo's localStorage or a verdict depend on who
is signed in. A verdict is about the card, never about the account.

## 2. What is stored (and what is never stored)

Accounts table (proposed, server database only):

| Field | Rule |
|---|---|
| id | Server-generated, never the display name. |
| display_name | User-chosen, shown on leaderboard. Uniqueness enforced at claim time; impersonation is a known limit until verified accounts exist — leaderboard names stay "bragging rights" until then. |
| email | Only if the user gives one for reset. Optional at sign-up. |
| password_hash | `hashlib.scrypt` output, per-user random salt (≥16 bytes), parameters tuned so one hash costs ~100 ms on the target host. Salt + parameters stored WITH the hash (that is normal and safe); the password itself is never stored, never logged, never emailed. |
| password algorithm | scrypt via stdlib `hashlib` (works on Penguin stdlib). bcrypt only if a bcrypt library is actually available on the deployment host — do not add a dependency to get it. |
| created_at, last_login_at | Timestamps only. |
| status | active / locked / deleted. Deleted = soft-delete first (data retained for the user's own export, then purged on request). |

NEVER stored: plaintext passwords, password hints that are the
password, session tokens in plaintext (see §3), or any credential in
the demo bundle, in a log, in localStorage, or in a repo file.

## 3. Sessions

- On login, the server mints a random session token
  (`secrets.token_urlsafe(32)`), stores only its SHA-256 hash in a
  sessions table with user id, expiry (30 days, sliding to a 90-day
  cap), device label, and created IP (for the user's own session list,
  not for tracking).
- The raw token goes to the client once, in an HttpOnly, Secure,
  SameSite=Lax cookie (or an Authorization header for API clients).
  It is never put in a URL, never in localStorage in the demo's
  current architecture, and never printed in a log.
- Logout deletes the session row. "Log out everywhere" deletes all
  of that user's session rows.
- Every authenticated request re-checks: session exists, not expired,
  account not locked. A failed check returns 401 with no detail
  about which part failed.
- Brute-force guard: after 5 failed logins for one account in 15
  minutes, that account is locked for 15 minutes and the response
  stays a generic "sign-in failed" (no "wrong password" vs "no such
  account" distinction — that distinction leaks account existence).

## 4. Account-bound data (migration from device-local)

Today the demo keeps, per device, in localStorage: `op_profile_v1`
(display name, bio, avatar) and `op_coins` (game coins), and
referral free checks are counted server-side by code + name with no
account link. Under this design:

- Coins: a server `balances` row per user (game coins, earned only,
  never bought with money in the demo; real-money purchases are a
  separate owner decision and are NOT in this design).
- Referral: `referrals` / `referral_claims` gain a `user_id` column;
  the 10/10 free-check rule (once per friend, never own sign-up)
  is enforced by user id, not by a typed name.
- Leaderboard: posting a score requires a session; the posted name
  is the account's display name, not a free-typed string, which
  closes the name-impersonation hole on the board.
- Migration: on first server sign-in, the demo offers a one-time
  import of the device's local coins/profile, shown to the user for
  confirmation, then the device copy is cleared. No silent merge,
  no double-spend: the import is idempotent (one import row per
  device id).

## 5. Proposed endpoints (backend only, not built)

- `POST /auth/register` {display_name, password, email?} → 201 + session.
- `POST /auth/login` {display_name-or-email, password} → session.
- `POST /auth/logout` → deletes this session.
- `GET /auth/me` → display name, coins, referral count (session required).
- `GET /auth/sessions` → the user's own session list; `DELETE` one.
- `POST /auth/reset/request` {email} → always returns the same
  "if that email exists, a reset link was sent" message (no existence
  leak), rate-limited to 3/hour per IP.
- `POST /auth/reset/confirm` {token, new_password} → token is random,
  single-use, expires in 1 hour, stored hashed like a session token.
- All auth endpoints rate-limited (login 10/min/IP, register 5/hour/IP).

## 6. Password reset — needs owner approval before it is deployed

A reset flow that sends email needs a sender, a domain, and a
decision about who receives what — none of which is approved here.
Until the owner approves the reset channel, the deployed fallback is:
no self-serve email reset; a locked-out user contacts the owner, who
issues a one-time reset link from the server console. That fallback
is slower and safer than a half-built email flow. Do not build or
deploy an email reset on the strength of this design doc alone.

## 7. What stays local-only in the demo until this is reviewed

- The demo's current sign-in gate (`opLoginGate`) and Settings
  sign-in stay local-only. They must NOT collect a real password,
  must NOT send anything to the backend, and must NOT be relabelled
  as "your account" until this design is reviewed by the owner and
  Latch and a live auth deployment is separately approved.
- Demo game coins stay device-local until the migration in §4 is
  built and tested; server coins and device coins must never be
  added together by hand.
- Biometric unlock (device-local only, e.g. phone fingerprint to
  unlock the app) is a separate feature from server sign-in and is
  NOT in this design: a biometric never replaces a server password,
  it only unlocks the device's stored session.
- No password, token, or hash value appears in any test, log, or
  report generated from this design.

## 8. Review checklist before any live auth build

- [ ] Owner approves this design and the reset fallback in §6.
- [ ] Latch reviews: password storage, token storage, rate limits,
      migration idempotence, and the "verdict never depends on account"
      rule.
- [ ] Deployment host chosen (see MULTIBACKEND_ROLES.md — Penguin
      stdlib CAN run scrypt + token logic; it cannot run the Pillow
      matcher, which is a separate deployment question).
- [ ] Test accounts only, then a closed test with real users, before
      any public sign-in button ships in the demo.
