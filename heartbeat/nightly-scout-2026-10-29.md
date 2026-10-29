# 🌙 Nightly Scout Report — 2026-10-29 (Thursday)

**Generated:** 2026-10-29 01:30–01:45 CST (Asia/Shanghai) / 2026-10-28 17:30–17:45 UTC
**Window:** NightOps Scout — ✅ 在 Mon–Fri 00:30–03:00 窗口内（周四 00:30 触发）
**Runtime:** OpenClaw Scout NightOps (cron `c46eeb63-de42-4938-9fe1-3fb63dd9c342`)
**Task:** 趋势扫描任务（读取 DIRECTIVE.md / HEARTBEAT.md，执行趋势扫描）

---

## 0. DIRECTIVE.md 检查

- `DIRECTIVE.md` 内容仅为「（暂无指令）」→ **无新指令，本场为空扫描**

## 1. ⚙️ 系统状态检查

| 项 | 状态 | 证据 |
| --- | --- | --- |
| gateway 进程 | 🟢 运行中 | PID 497240（已运行 2天0小时32分） |
| gateway RSS | 🔴 **10.6GB（远超 6GB 阈值）** | RSS 11,097,072 KB；watchdog 于 01:15 已发出 WARN |
| gateway CPU | 🔴 **63.3% 累计使用率偏高** | ps 实测 63.3%（全周期均值） |
| model-fetch | ✅ 正常 | 今日 10-29 model-fetch ok=80/err=2（成功率 97.6%） |
| MiniMax 429 | 🟢 今日大幅缓解 | 10-29 仅 84 次 429（10-28 为 259 次，10-27 为 1256 次） |
| LiteLLM proxy | ✅ 正常 | litellm/GLM-5.3-Flash 稳定 200，延迟 1.0–5.9 秒 |
| 代理 25017 | ✅ TCP 可达 | 172.18.160.1:25017 连通测试成功 |
| 8080 FastAPI | ✅ TCP 可达 | 127.0.0.1:8080 连通测试成功 |
| cron status | 🟢 31 jobs / 运行正常 | 本场 Scout NightOps `c46eeb63` 在运行中 |
| 每日新闻摘要 | ✅ 10-28 08:00 场成功并发飞书 | `om_x100b6127f25198a0c0e87cf85358c8b`（21,382B 上传成功） |
| memory | ✅ 今日 10-29 笔记已创建 | `memory/2026-10-29.md` |

## 2. 🔴 头号发现：Gateway 内存劣化模式第五次复现，建议尽快重启

**本场最强系统性信号**（非 AI 行业趋势，而是本 infra 侧长期问题的延续）。

### 2.1 现状数据（2026-10-29 01:42 实测）
- **RSS = 11.02GB**（较 10-28 01:30 的 9.31GB **增长约 1.7GB**）
- **增长速率 = 74,677 KB/h ≈ 73 MB/h**（watchdog 01:15 实时计算）
- **Uptime = 2天0小时32分**（自 10-27 01:13 重启后）
- **CPU = 63.3%**（全周期累计，较 10-27 的 ~112–117% 峰值回落，但仍偏高）

### 2.2 历史趋势对照表

| 观测时间 | RSS | 增速 | 评估 |
|---|---|---|---|
| 10-24 01:24（上一重启后） | 3.75GB | — | 重启后 |
| 10-24 05:26 | 6.5GB | 上升 | 劣化模式第二次复现 |
| 10-26 02:30 | 9.5GB | 继续爬升 | 劣化模式第三次复现 |
| 10-27 00:55 | 12.0GB / CPU 82.7% | 继续爬升 | 劣化模式第四次复现（需要重启）|
| 10-28 01:30 | 9.31GB / CPU 77.7% | 缓升 | 10-27 重启后，较 12GB 有改善 |
| **10-29 01:42（本场）** | **10.6GB / CPU 63.3%** | **~73 MB/h** | **突破 8GB 阈值，劣化模式第五次复现** |

### 2.3 建议
- **P0：建议 ZP 择机重启 gateway**（当前功能暂时健康，model-fetch 成功率 97.6%，但重启窗口应避免在 08:00 新闻摘要任务前进行）
- 依旧需**定位泄漏根因**而非反复重启（该问题已四次复现）
- watchdog 已持续捕获 RSS 超阈值并发出 WARN 通知（生效中）

## 3. 🟡 MiniMax 429 情况

- **今日 10-29 0 点–01:42 共 84 次 429**（较 10-28 同期 259 次改善 67%）
- **429 集中在 01:34–01:39**（来自 main agent 的 embedded run 报错 `已达到 Token Plan 用量上限 (2056)`）
- **主因仍是 MiniMax Token Plan 配额耗尽**（10-24 05:26 遗留问题，仍需 ZP 进行充值或升级）
- 主 fallback `litellm/GLM-5.3-Flash` 依然稳定 200（延迟 1.0–2.7s），业务未受影响

## 4. 🟢 每日新闻摘要运行状态

- **10-28 08:00 场 ✅ 成功**：`news_digest_20261028_080309.html`（21,382B）
  - file_key `file_v3_0016t_20b64da5-e81e-4c92-a319-3afcb3ef725g`
  - Feishu 推送消息 ID `om_x100b6127f25198a0c0e87cf85358c8b`
- 10-28 08:09 复验产物 `news_digest_20261028_080944.html` 也正常
- **OpenRouter 依然 402（0 余额）**，未做充值（属 ZP 决策，备用不可用）
- 今日 01:36 无新摘要产出，属预期（08:00 场待今日观察）

## 5. 🟢 cron 任务健康度

- 31 jobs / triggersEnabled=true
- **本场 Scout NightOps（c46eeb63）✅ 正常执行**
- **Cron NightOps-Coder（8872e811）✅ 10-29 00:20 完成**
- 🟡 `NightOps-Scout` (0597835a) 最近一次 01:27 仍报 `⚠️ Tool Call failed`
- 🔴 OpenClaw Backup Log 仍 error ×2（旧遗留）
- 🔴 Health-Weekly-IMA-Scan 仍 error ×3（旧遗留）
- 🟡 Main NightOps 10-27 01:00 报 429 Token Plan 402（需充值或升级 MiniMax Token Plan 才能根治）

## 6. 跨源综合：三条正在重复的主线

### 主线 A — Gateway 内存泄漏（延续 10-24 起五次复现）
- 10-24 3.75GB → 10-26 9.5GB → 10-27 12GB → 10-28 9.31GB → **10-29 10.6GB**
- 重启仅是缓解，未解决泄漏根因；watchdog 一直持续追踪。
- 内存趋势文件 `gateway-rss-trend.txt` 持续记录增长曲线 — **73MB/h** 稳定增长速率可以进一步定位泄漏源（10-26 曾建议 MALLOC_ARENA_MAX=2 测试，未见实施）。

### 主线 B — MiniMax 配额限制（延续 10-24 起）
- 自 10-24 以来持续存在，10-29 仍未解决；早峰（08:00）与 NightOps 时段（00:30–02:00）容易触发 429。
- fallback 到 LAN LiteLLM 服务的 `GLM-5.3-Flash` 一直成功，业务连续性有保障。

### 主线 C — 非主干任务的持续失败（延续多场）
- `Backup Log` ×2、`Health-Weekly-IMA-Scan` ×4、`memory-weekly-audit` ×4 等长期 error 任务，属「非主干但持续失败」，建议评估：合并到其他夜班 job 或关闭。
- `NightOps-Scout` (0597835a) 最近一次错误 `⚠️ Tool Call failed`，可继续观察（本场 c46eeb63 已成功执行）。

---

## 7. 本场产出物

| 产物 | 路径 |
|---|---|
| 本报告 | `heartbeat/nightly-scout-2026-10-29.md` |
| 记忆版摘要 | `memory/2026-10-29.md` |

## 8. 下一场关注点（10-30 00:30）

1. **gateway RSS**：如未重启，按 73MB/h 预计 10-30 00:30 到 **~12.8GB**（第 3 天）
2. **MiniMax 429**：是否随 10-29 早峰进一步恶化
3. **10-29 08:00 新闻摘要场**：是否成功推送
4. **OpenRouter**：是否充值或换 key
5. **NightOps-Scout (0597835a)**：Tool Call 错误是否重现
6. **Backup/Weekly 类 cron**：是否评估合并或关闭
