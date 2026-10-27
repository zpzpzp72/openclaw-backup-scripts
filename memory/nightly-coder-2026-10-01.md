# Memory: Nightly Coder — 2026-10-01

## Headline takeaways

- **OpenClaw is 2 patches behind.** Installed `2026.9.5 (ec9c1a1)`; npm `latest` is `2026.9.7`. Two patch releases available.
- **Node.js is still below the required minimum.** Running `v24.15.0`; OpenClaw declares `engines.node: >=24.16.0 <25 || >=26.1.0`. Same condition flagged in the 2026-09-08 nightly report — not yet fixed.
- **Workspace has a large uncommitted changeset** on `feature/hot-backup`: +557/-1094 across 10 tracked files, plus several untracked persona files at root (`AGENTS.md`, `IDENTITY.md`, `SOUL.md`). MEMORY.md rewritten; orchestrator `HEARTBEAT.md` and `TOOLS.md` deleted; `ERRORS.md` trimmed by 883 lines.
- **Backup is healthy.** Latest `openclaw-20261001-1041.tgz` (4.0 GB) written at 10:41 today; the FORCE_TAR fallback (added 2026-08-26) fired after a 535-hour gap since the previous real backup (2026-09-09 03:00).
- **No GitHub CI signal.** None of the active repos have Actions configured; `gh run list` returns empty across the board. Nothing to regress.
- **Upstream drift is unchanged.** Local `main` on the OpenClaw fork is 224 ahead / 6,293 behind `openclaw/openclaw main`.

## Durable facts (for next cron run)

- Workspace is on branch `feature/hot-backup`, HEAD `a72f94fd chore: add .gitignore`.
- The active backup script is `~/.openclaw/workspace/scripts/openclaw-backup.sh` (not the 2,468-byte root copy `openclaw-backup.sh` — that one is stale and should be removed or symlinked).
- `openclaw-backup.sh` writes heartbeat to `~/.openclaw-backup.heartbeat`; schema = `last_run / last_run_epoch / last_backup / last_backup_epoch / hours_since_last_backup / need_backup / force_tar_reason / status / detail`.
- `gh run list --limit N` from cron is fast and safe; `git fetch upstream` against `~/.openclaw/openclaw-source` is slow — give it a 20–30 s timeout and fall back to `git rev-list --left-right --count` if it hangs.

## Open action items (carry forward)

1. Upgrade Node.js to ≥24.16.0 (or ≥26.1.0) — blocks `openclaw update` to 2026.9.7.
2. Commit the workspace `feature/hot-backup` changeset (already diff'd, low risk).
3. Delete or symlink the stale root `openclaw-backup.sh`.
4. Plan an upstream sync of the OpenClaw fork (6,293 commits behind).
5. Add a minimal CI workflow to one repo so the next nightly run has something to inspect.

## Watchlist entities

- OpenClaw release cadence: 2026.9.5 → 2026.9.6 → 2026.9.7 within ~10 days; expect more 2026.9.x patches.
- `openclaw/openclaw` upstream — large structural refactors (plugin pruning, gateway reconnect replays, swarm collector hardening) shipped 2026-07-23 batch; review when syncing.
- Node.js LTS track: confirm 24.x → 24.16.0+ availability on this host's package manager before scheduling the upgrade.
