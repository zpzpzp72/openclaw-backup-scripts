# nightly-coder-2026-10-08.md

**Generated:** 2026-10-08 22:20 CST (Asia/Shanghai) / 14:20 UTC
**Cron:** NightOps-Coder (cron:a38acaaa-52ef-4e46-badf-8104a6fd1c41)
**Report:** `heartbeat/nightly-coder-2026-10-08.md`
**Window:** Thursday NightOps Coder (Tue/Wed/Thu 21:30-23:30) ✅ in window

---

## 0. 服务状态表 (Service Status Table)

| 子代理 / 服务 | 状态 | 上次报告 | 备注 |
|--------------|------|---------|------|
| NightOps-Coder | 🟢 | 2026-10-07 22:21 CST | 本次运行（10/08 22:20 CST） |
| GitHub CI/CD (audited repos) | 🟡 | 2026-10-07 22:21 | openclaw fork stale 10d；memory-lancedb-pro last-failed 156d；**部分仓 TLS timeout** |
| OpenClaw upgrade | 🟡 | 2026-10-07 22:21 | binary=2026.9.8 / self=2026.9.8 ✅ 一致；但 **npm `latest` 已升至 2026.9.9（+1 patch ahead）**；`finalize:doctor` 仍阻断 |
| Node compatibility | 🟢 | unchanged | v26.10.0 ≥ required 26.1.0 |
| Workspace drift | 🔴 | 2026-10-07 22:21 | **93 dirty / 651 untracked**（10/07: 93/629 → untracked +22 持续微涨） |
| Backup | 🔴 | 2026-10-07 22:21 | last ok **7d ago**（10/07: 6d → 持续恶化 +1d） |
| Local source fork | 🟢 | unchanged | clean @ `0790d9f593a` |
| Gateway systemd | 🟢 | 2026-10-07 22:21 | active (pid 537581) since 10/04 19:54; **uptime 4d** |
| Heartbeat delivery | 🔴 | 2026-10-07 22:21 | 8 jobs 仍 "waiting for delivery route"；placeholder 未替换（**第 7 夜携带**） |
| Plugin memory-lancedb-pro | 🟡 | 2026-10-07 22:21 | "not checked" — **第 7 个 nightly 携带** |
| Doctor warnings | 🟡 | 2026-10-07 22:21 | 沿用：github plugin allowlist、Feishu blank messages、command owner；新增：**openclaw-weixin capability consent** + **heartbeat migration preview (scout/life)** + **5 plaintext secrets** |
| npm registry | 🟡 | new this run | `latest` = **2026.9.9**（installed = 2026.9.8，+1 patch ahead） |

---

## Key findings

### 1. CI/CD (audited via `gh run list --limit 3`)
- `zpzpzp72/openclaw` (fork) — last runs 2026-09-22~28, **stale 10d** (第 7 夜携带)
- `zpzpzp72/memory-lancedb-pro` — last CI **failed 2026-05-05** (~156d unaddressed, 第 7 夜携带)
- `zpzpzp72/openclaw-backup-scripts` — `[]` (no workflow runs, 干净信号)
- ⚠️ GitHub API 本场出现间歇性 `net/http: TLS handshake timeout` (api.github.com) — 网络问题，**非 CI 故障**

### 2. OpenClaw upgrade & build risk
- Binary = **2026.9.8** (`fc23bc8`); self = **2026.9.8** ✅ 一致
- 🆕 **npm `latest` = 2026.9.9** (10/07 时仍 2026.9.8) — **+1 patch ahead**
- `extended-stable=2026.8.35`, `beta=2026.10.1-beta.2`
- `Update run failed: finalize:doctor` — status string stale ("running 2026.9.7" vs actual 2026.9.8)
- Backup last ok **7d ago** (4d→5d→6d→7d 持续恶化，第 4 夜标记)
- Gateway active since 2026-10-04 19:54:58 CST (**uptime 4d**, pid 537581)
- Memory: 9.9G (peak 12.6G); CPU: 22h 18min cumulative

### 3. Doctor output highlights (新增项 🆕 标记)
- 🆕 5 plaintext secrets in config: `gateway.auth.token, models.providers.litellm.apiKey, talk.providers.minimax.apiKey, channels.telegram.botToken, channels.feishu.appSecret`
- 🆕 Feishu groupPolicy="open" — 建议 `allowlist` + `groupAllowFrom`
- 🆕 Legacy Browser Relay auth enabled (`allowLegacyAuth=true`)
- 🆕 Plugin "openclaw-weixin" requires capability consent
- 🆕 Legacy backup scratch at `/tmp/openclaw-backup-IpNBRS` 无 lifetime token
- 🆕 Cron: 2 jobs override `payload.model` (`M2.7`, `M2.7-highspeed` vs default `MiniMax-M3`)
- 🆕 Heartbeat migration preview (scout, life HEARTBEAT.md → scratch)
- 沿用: github plugin allowlist, Feishu 4 blank msgs, command owner, device-pair, gateway.bind=loopback

### 4. Codebase changes & dependencies
- Workspace: `feature/hot-backup` @ `a72f94f` — **8 夜未 commit**
- 11 modified + 2 deleted + **651 untracked** (10/07: 629, +22 持续微涨)
- Top untracked: `.backups/control-ui-2026.9.8-*` snapshots, `.graphify_*.json`, root identity files
- `scripts/openclaw-backup.sh` 仍 modified vs HEAD; cron `0 3 * * *` daily since 10/04
- npm `openclaw`: `latest=2026.9.9` (+1 ahead of installed)
- Local fork: `~/.openclaw/openclaw-source` @ `0790d9f593a` (top: `fix(plugins): accept singleton npm view metadata`)
- Disk: 130G used / 827G available (14%)
- Sessions: 2033 stored; 8 agents; default `MiniMax-M3` (1.0m ctx)

---

## Stalled items (operator-actionable)

| Item | Nights carrying | Severity | Action |
|------|-----------------|----------|--------|
| Backup last ok 7d ago | 4 | 🔴 High | Run `scripts/openclaw-backup.sh` manually |
| Heartbeat delivery placeholder (`telegram:123456789`) | 7 | 🔴 High | Set real `commands.ownerAllowFrom` |
| memory-lancedb-pro "not checked" + 156d CI failure | 7 | 🟡 Med | Freeze-or-merge decision |
| OpenClaw fork CI stale 10d | 7 | 🟡 Med | Check repo settings / re-enable |
| Workspace untracked growth (83→651) | 3 | 🟡 Med | Add `.backups/` to `.gitignore` |
| Feishu 4 blank messages | 4+ | 🟡 Med | `openclaw doctor --fix` |
| Feishu groupPolicy=open | new | 🟡 Med | Set `allowlist` + `groupAllowFrom` |
| 5 plaintext secrets | new | 🔴 High | Migrate to SecretRefs |
| Browser Relay legacy auth enabled | new | 🟡 Med | Migrate then `allowLegacyAuth=false` |
| openclaw-weixin consent | new | 🟡 Med | `openclaw plugins enable --accept-capabilities` |
| npm `latest` 2026.9.9 ahead of installed 2026.9.8 | new | 🟡 Med | Retry `openclaw update` |

---

## Recommended actions (priority order)

1. **Retry `openclaw update`** — npm `latest` 已是 **2026.9.9** (+1 patch gap accumulates)
2. **Migrate 5 plaintext secrets to SecretRefs** — security-sensitive (`openclaw secrets configure`)
3. **Run backup manually** — `scripts/openclaw-backup.sh` (4 nights worsening)
4. **Fix heartbeat delivery** — set real `commands.ownerAllowFrom` (7 nights stalled)
5. **Run `openclaw doctor --fix`** — non-destructive; fixes Feishu session + 1 missing title
6. **Accept openclaw-weixin capabilities** — `openclaw plugins enable openclaw-weixin --accept-capabilities`
7. **Set Feishu groupPolicy=allowlist** — `channels.feishu.groupPolicy="allowlist"` + `groupAllowFrom`
8. **Append `"github"` to `plugins.allow`** — restore GitHub link previews
9. **Investigate memory-lancedb-pro** — freeze or merge (156d unaddressed)
10. **Add `.backups/` to `.gitignore`** — stop untracked growth
11. **Browser Relay v2 migration** — then `allowLegacyAuth=false`

---

## Auto-collected metrics (this run vs 10/07 baseline)

| Metric | 10/07 | 10/08 | Δ |
|--------|-------|-------|---|
| Doctor warnings surfaced | ~6 | ~14 | +8 (new surface area) |
| Files audited | 16 | 16 | 0 |
| TLS timeouts encountered | 0 | 2 | +2 (GitHub API intermittent) |
| Service health checks | 5 | 5 | 0 |
| npm `latest` | 2026.9.8 | 2026.9.9 | +1 patch |
| Backup age | 6d | 7d | -1d worsening |
| Workspace untracked | 629 | 651 | +22 |
| Memory-lancedb-pro stall | 6 nights | 7 nights | +1 |
| Heartbeat placeholder stall | 6 nights | 7 nights | +1 |
| OpenClaw fork CI stale | 6 nights | 7 nights | +1 |

---

## References

- Main report: `heartbeat/nightly-coder-2026-10-08.md`
- Previous: `heartbeat/nightly-coder-2026-10-07.md`, `memory/nightly-coder-2026-10-07.md`
- Scout (same window): `heartbeat/nightly-scout-2026-10-08.md` (21:38 — arXiv ✅, GitHub ⚠️ rate-limited, web_search ❌ 3rd day)
- Orchestrator (most recent): `heartbeat/nightly-orchestrator-2026-10-07.md`
