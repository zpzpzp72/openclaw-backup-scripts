# nightly-coder-2026-10-09.md

**Generated:** 2026-10-09 22:20 CST (Asia/Shanghai) / 14:20 UTC
**Cron:** NightOps-Coder (cron:a38acaaa-52ef-4e46-badf-8104a6fd1c41)
**Report:** `heartbeat/nightly-coder-2026-10-09.md`
**Window:** Friday NightOps Coder (Mon–Fri 21:30–23:30) ✅ in window

---

## 0. 服务状态表 (Service Status Table)

| 子代理 / 服务 | 状态 | 上次报告 | 备注 |
|--------------|------|---------|------|
| NightOps-Coder | 🟢 | 2026-10-08 22:20 CST | 本次运行（10/09 22:20 CST） |
| GitHub CI/CD (audited repos) | 🟡 | 2026-10-08 22:20 | openclaw fork stale 11d；memory-lancedb-pro last-failed 157d；其他仓无 CI 信号；**网络恢复，无 TLS timeout** |
| OpenClaw upgrade | 🟡 | 2026-10-08 22:20 | binary=2026.9.8 / self=2026.9.8 ✅ 一致；npm `latest=2026.9.9`（+1 patch ahead 持续第 2 夜）；`finalize:doctor` 仍阻断（status string stale "running 2026.9.7" 第 3 夜）|
| Node compatibility | 🟢 | unchanged | v26.10.0 ≥ required 26.1.0 |
| Workspace drift | 🔴 | 2026-10-08 22:20 | **8 modified + 2 deleted + 84 untracked**（10/08: 11/2/651 → modified -3 / untracked -567 **异常回落 ⚠️**）|
| Backup | 🔴 | 2026-10-08 22:20 | last ok **8d ago**（10/08: 7d → 持续恶化 +1d，**第 5 夜标记**）；**cron 静默 4 夜**（`backup-cron.log` last write 2026-10-05 03:00）|
| Local source fork | 🟢 | unchanged | clean @ `0790d9f593a`（同 10/08）|
| Gateway systemd | 🟢 | 2026-10-08 22:20 | active (pid 537581) since 10/04 19:54:58; **uptime 5d**；memory 10.3G（peak 12.6G）|
| Heartbeat delivery | 🔴 | 2026-10-08 22:20 | 8 jobs 仍 "waiting for delivery route"；placeholder 未替换（**第 8 夜携带**）|
| Plugin memory-lancedb-pro | 🟡 | 2026-10-08 22:20 | "not checked" — **第 8 个 nightly 携带** |
| Doctor warnings | 🟡 | 2026-10-08 22:20 | 沿用 14+ 项；**4 plaintext secrets**（10/08: 5 → 10/09: 4，**`litellm.apiKey` 已迁移**）|
| Agent-DB integrity | ⚠️ | new this run | `integrityCheckSyncMs=1682` 超 1000ms 阈值 68% |
| npm registry | 🟡 | 2026-10-08 22:20 | `latest` = **2026.9.9**（installed = 2026.9.8，+1 patch ahead 第 2 夜）|

---

## Key findings

### 1. CI/CD (audited via `gh run list --limit 3`)
- `zpzpzp72/openclaw` (fork) — last runs 2026-09-22~28, **stale 11d** (第 8 夜携带)
- `zpzpzp72/memory-lancedb-pro` — last CI **failed 2026-05-05** (~157d unaddressed, 第 8 夜携带)
- `zpzpzp72/openclaw-backup-scripts` — `[]` (no workflow runs, 干净信号)
- `zpzpzp72/openclaw-backup` / `a-stock-daily-report` / `amat-stock-report` — 同样 `[]` (干净信号)
- ✅ **GitHub API 网络恢复**：本场 6 仓全部回包（10/08: 2 个 TLS timeout）

### 2. OpenClaw upgrade & build risk
- Binary = **2026.9.8** (`fc23bc8`); self = **2026.9.8** ✅ 一致
- **npm `latest` = 2026.9.9** (持续第 2 夜 +1 patch ahead)
- `extended-stable=2026.8.35`, `beta=2026.10.1-beta.2`
- `Update run failed: finalize:doctor` — status string stale ("running 2026.9.7" vs actual 2026.9.8) 第 3 夜
- Backup last ok **8d ago** (4d→5d→6d→7d→8d 持续恶化，第 5 夜标记)
- Backup cron 静默 4 夜（`backup-cron.log` last write 2026-10-05 03:00）
- Gateway active since 2026-10-04 19:54:58 CST (**uptime 5d**, pid 537581)
- Memory: 10.3G (peak 12.6G); CPU: 1d 3h 24min cumulative

### 3. Doctor output highlights (`openclaw doctor --json` — 37 checks run / 30 skipped)
- 🆕 **Plaintext secrets 5 → 4**: `gateway.auth.token, talk.providers.minimax.apiKey, channels.telegram.botToken, channels.feishu.appSecret`（`models.providers.litellm.apiKey` 已迁）
- 🆕 **Agent-DB integrity**: `integrityCheckSyncMs=1682` (68% over 1000ms threshold; `transcript_events.quick_check=581ms` 是瓶颈)
- 沿用: github plugin allowlist, Feishu 4 blank msgs, command owner, device-pair, gateway.bind=loopback, Feishu groupPolicy=open, openclaw-weixin consent, Browser Relay legacy auth, cron model overrides, heartbeat migration preview, 1 missing session title, legacy backup scratch

### 4. Codebase changes & dependencies
- Workspace: `feature/hot-backup` @ `a72f94f` — **9 夜未 commit**
- 8 modified + 2 deleted + **84 untracked** (10/08: 11/2/651 — **untracked -567 异常回落 ⚠️**)
- 推测原因: 仓库 reset / fresh clone；`agents/orchestrator/Tomorrow_Action_Plan_2026-07-25..08-02.md` 与 `.backups/control-ui-2026.9.8-*` 大幅减少
- `scripts/openclaw-backup.sh` 仍 modified vs HEAD; cron `0 3 * * *` daily since 10/04
- 12 个 cron jobs 登记（1 backup, 1 finance, 1 news, 1 claw-sync, 4 amat, 1 cron-watchdog, 1 heartbeat, 1 bilibili, 1 mic-button）
- npm `openclaw`: `latest=2026.9.9` (+1 ahead of installed, 第 2 夜)
- Local fork: `~/.openclaw/openclaw-source` @ `0790d9f593a` (top: `fix(plugins): accept singleton npm view metadata`)
- Disk: 130G used / 826G available (14%)
- Sessions: 2015 stored; 8 agents; default `MiniMax-M3` (1.0m ctx)

### 5. Backup cron forensics
- `backup-cron.log` last modified **2026-10-05 03:00** (4 nights silent)
- Last entry before silence: `❌ 发送失败: Connection unexpectedly closed` (after 7/9 失败)
- Likely causes: (a) script crashed before log; (b) cron service not running; (c) script moved; (d) `flock` lock stuck
- Recommend: `bash -x scripts/openclaw-backup.sh 2>&1 | head -50` for debug

---

## Stalled items (operator-actionable)

| Item | Nights carrying | Severity | Action |
|------|-----------------|----------|--------|
| Backup last ok 8d ago + cron 静默 4 夜 | 5 | 🔴 High | `bash -x scripts/openclaw-backup.sh` debug; manually run |
| Workspace untracked 异常回落 -567 | new | 🔴 High | Verify `agents/orchestrator/Tomorrow_Action_Plan_*` + `.backups/` intact |
| Heartbeat delivery placeholder (`telegram:123456789`) | 8 | 🔴 High | Set real `commands.ownerAllowFrom` |
| 4 plaintext secrets | new | 🔴 High | Migrate to SecretRefs (`openclaw secrets configure`) |
| Agent-DB integrity 1682ms | new | ⚠️ Med | `openclaw doctor --fix` or DB vacuum |
| memory-lancedb-pro "not checked" + 157d CI failure | 8 | 🟡 Med | Freeze-or-merge decision |
| OpenClaw fork CI stale 11d | 8 | 🟡 Med | Check repo settings / re-enable |
| Feishu 4 blank messages | 4+ | 🟡 Med | `openclaw doctor --fix` |
| Feishu groupPolicy=open | carrying | 🟡 Med | Set `allowlist` + `groupAllowFrom` |
| Browser Relay legacy auth enabled | carrying | 🟡 Med | Migrate then `allowLegacyAuth=false` |
| openclaw-weixin consent | carrying | 🟡 Med | `openclaw plugins enable --accept-capabilities` |
| device-pair plugin not enabled | carrying | 🟡 Med | `plugins.entries.device-pair.enabled: true` |
| npm `latest` 2026.9.9 ahead of installed 2026.9.8 | 2 | 🟡 Med | Retry `openclaw update` |

---

## Recommended actions (priority order)

1. **Investigate backup cron 4-night silence** — `bash -x scripts/openclaw-backup.sh` + check `flock` lock + cron service state
2. **Verify workspace untracked anomaly** — confirm `agents/orchestrator/Tomorrow_Action_Plan_*` + `.backups/` not lost
3. **Migrate 4 plaintext secrets to SecretRefs** — security-sensitive (10/08: 5 → 10/09: 4, `litellm.apiKey` 已迁)
4. **Run backup manually** — `scripts/openclaw-backup.sh` (5 nights worsening)
5. **Fix heartbeat delivery** — set real `commands.ownerAllowFrom` (8 nights stalled)
6. **Run `openclaw doctor --fix`** — Feishu session + 1 missing title + agent-DB integrity
7. **Retry `openclaw update`** — npm `latest` 已是 **2026.9.9** (+1 patch gap accumulates 第 2 夜)
8. **Accept openclaw-weixin capabilities** — `openclaw plugins enable openclaw-weixin --accept-capabilities`
9. **Set Feishu groupPolicy=allowlist** — `channels.feishu.groupPolicy="allowlist"` + `groupAllowFrom`
10. **Append `"github"` to `plugins.allow`** — restore GitHub link previews
11. **Enable device-pair plugin** — `plugins.entries.device-pair.enabled: true`
12. **Investigate memory-lancedb-pro** — freeze or merge (157d unaddressed)
13. **Browser Relay v2 migration** — then `allowLegacyAuth=false`

---

## Auto-collected metrics (this run vs 10/08 baseline)

| Metric | 10/08 | 10/09 | Δ |
|--------|-------|-------|---|
| Doctor warnings surfaced | ~14 | ~14+ | 0 (stable) |
| Doctor JSON checks run/skipped | (not captured) | 37/30 | new metric |
| Files audited | 16 | 16 | 0 |
| TLS timeouts encountered | 2 | **0** | -2 (network recovered ✅) |
| Service health checks | 5 | 6 | +1 (crontab + backup log) |
| npm `latest` | 2026.9.9 | 2026.9.9 | 0 (stable, still +1 ahead) |
| Backup age | 7d | **8d** | -1d worsening |
| Backup cron log silence | (not measured) | **4 nights** | new metric |
| Workspace untracked | 651 | **84** | -567 ⚠️ (异常回落) |
| Workspace modified | 11 | 8 | -3 |
| Plaintext secrets | 5 | **4** | -1 (`litellm.apiKey` migrated) |
| Memory-lancedb-pro stall | 7 nights | 8 nights | +1 |
| Heartbeat placeholder stall | 7 nights | 8 nights | +1 |
| OpenClaw fork CI stale | 7 nights | 8 nights | +1 |
| Agent-DB integrity (ms) | not measured | 1682 | new metric (68% over) |
| Cron jobs registered | (not measured) | 12 | new metric |

---

## References

- Main report: `heartbeat/nightly-coder-2026-10-09.md`
- Previous: `heartbeat/nightly-coder-2026-10-08.md`, `memory/nightly-coder-2026-10-08.md`
- Scout (same window): `heartbeat/nightly-scout-2026-10-09.md` (21:36 — Full coverage, arXiv 120 ✅, GitHub 9 仓 ✅, web_search 4th day ❌)
- Orchestrator (most recent): `heartbeat/nightly-orchestrator-2026-09-07.md`
