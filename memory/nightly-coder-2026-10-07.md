# Nightly Coder — Memory Index — 2026-10-07

**Companion to:** `heartbeat/nightly-coder-2026-10-07.md`
**Session:** cron:a38acaaa-52ef-4e46-badf-8104a6fd1c41
**Slot:** Night #63, Wed 22:21 CST (in-window)

## Headline signals

| Key | Value | Δ vs 10/06 |
|-----|-------|-----------|
| OpenClaw binary | 2026.9.8 | same |
| Gateway self-report | 2026.9.8 | ✅ **2026.9.7 → 2026.9.8 resolved** |
| `update` blocker | `finalize:doctor` | same (msg text stale) |
| Backup last-ok | 6d ago | 🔴 5d → 6d (worse) |
| Workspace dirty | 93 entries (11M + 2D + 629U) | 🔴 +3M, +546U |
| Memory-lancedb-pro | "not checked" | 🔴 6th night |
| Heartbeat delivery | placeholder | 🔴 6th night |
| OpenClaw fork CI stale | 9 days | 🟡 6th night |

## Action queue (carry-forward to next Coder / operator)

1. `scripts/openclaw-backup.sh` — manual rerun (last ok 6d)
2. `openclaw update` — retry (drift resolved)
3. `openclaw doctor --fix` — Feishu session repair
4. `plugins.allow` — append `"github"`
5. `commands.ownerAllowFrom` — replace `telegram:123456789` placeholder
6. Workspace — commit or discard `feature/hot-backup` drift; add `.backups/` + `.graphify_*.json` to `.gitignore`
7. `memory-lancedb-pro` — disable plugin or fix CI; sixth consecutive night flagged

## Cross-references

- Scout: external network degraded again (web_search provider_error, web_fetch ECONNRESET) — same as 10/06
- Orchestrator: last report 2026-10-06 23:06; this Coder run precedes tonight's orchestrator run
- Repo URL convention: `zpzpzp72/<repo>`