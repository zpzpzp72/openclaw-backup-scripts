# Tomorrow_Action_Plan — 2026-11-08

> NightOps 2026-11-07 02:40 CST 汇总 · 输入：scout 11-07(02:30)、life 11-07(02:05)、coder 11-07(02:24)、orchestrator 自查
> 归一化：Signal / Impact / Blocker / Opportunity / Next Step

---

## 🔴 P0 — 需 Main 今晚拍板（今晚 03:00 是硬时间点）

- **P0-1 NAS 备份断档 2 晚，今晚 03:00 第 3 次预检拦截**
  - Signal: `/mnt/h` 7.2T 已 100%，仅剩 3.8G；`~/.openclaw-backup.heartbeat` status=error，detail=「可用 4G < 需要 6G」，last_backup 仍停在 `openclaw-20261105-0300.tgz`
  - Impact: 备份链已连续 2 晚失败，仓库/会话无异地副本；今晚 03:00 将是第 3 次拦截
  - Blocker: `/mnt/h/#recycle/AI/openclaw.zone/WSL/` 28 份 ≈123GB 全是 08-27~10-10 过期包；NAS(SMB) 上 `rm` 只是移入回收站，`RETAIN_DAYS=30` 清理**从不释放空间**
  - Opportunity: 一次清空回收站即可回收 ~123GB，足够连续备份 10+ 场
  - Next Step: **授权删除回收站 28 份旧 tgz**（不可逆，需 owner 明确点头）→ 再把 `RETAIN_DAYS` 30→14 并让清理脚本绕过回收站 → 再删 `WSL/` 中 10 月下旬前的 14 份（~108GB）
  - 注: heartbeat 文件里 `recycle_backups=0 / recycle_gb=0` 是**假阴性**（脚本自身 rm 后不感知 SMB 回收站），不能作为「无需清理」的依据

- **P0-2 Gateway 重启可一次性解掉两个 P0（租约自锁 + 内存正增长）**
  - Signal: 根因已锁定为 `state/openclaw.sqlite.agent_database_leases` 租约泄漏——scout/orchestrator/coder 各 2 条同 path 旧租约（11-05 07:19）从未 release；main/health/work 完全无租约 → main 库 272MB 回收量最大 + 无 clean-close 权限 → 5s 握手超时 → Heartbeat(main) error 46x（11-06 为 22x，**在恶化**）
  - Impact: main 侧心跳全线不可用；target=isolated 的 NightOps 与 news-digest 正常，故障面被限制在 main
  - Blocker: 需要停 Gateway 才能跑 `openclaw doctor --fix`
  - Opportunity: 源码级结论——**重启 Gateway 会让旧租约 owner_pid 变 stale 并被自动判 stale 清理**，因此「重启」本身就是一次有效清理动作，**可先于 doctor --fix 尝试**；且 Gateway RSS 已从 11-06 的 2.78GB 升到 **3.24GB**（watchdog +142KB/h），重启同时回收内存
  - Next Step: **一次重启，同时解决 P0-2 与内存趋势** → 重启后 30 分钟内验证 Heartbeat(main) error 计数是否回落；若仍失败再跑 `openclaw doctor --fix` + 升级 openclaw 2026.10.5

- **P0-3 M365 push 授权（本地已就绪，技术上可行）**
  - Signal: HEAD `40b27fc`（stdlib 遮蔽已修 + ruff/CI 落地），ahead 2 / behind 0，非分叉；`git ls-remote` ×5 → 4×rc=0 / 1×rc=128 gnutls_handshake → **判定为间歇性，非凭证缺失、非出站封锁**
  - Impact: 两个已验证修复仍困在本地；远端 pushed_at 停在 2026-03-18，外部停滞 ~2 周（D14+）
  - Blocker: 无需授权即可执行技术动作，但推送到远端属外部副作用，需 owner 点头
  - Next Step: 授权 `git push origin HEAD`（建议重试循环：rc≠0 时 sleep 20s 重试，最多 5 次，命中间歇窗口即成功）

---

## 🟡 P1 — 可自动派发 / 次日跟进

- **P1-1 云端 fallback 全断**：OpenRouter 余额 0（连续第 3 窗确认）/ LiteLLM@NAS 无鉴权且后端 DB 挂 / SiliconFlow key 失效 / LongCat 无 key → 本地 `ollama/qwen3.6:27b` 与 `qwen3:4b-instruct`（实测 3.5s）是唯一兜底。**需 owner 充值或换 key**，否则单点风险长期挂账。
- **P1-2 web_search(duckduckgo) 连续第 17 次 provider_error**；`alignment.openai.com` 直连 SSL_ERROR_SYSCALL → OpenAI misalignment 报告改由 The Decoder 转述（已成既定降级方案，可从「异常」降为「已知降级」）。
- **P1-3 Life 报告连续性**：11-07 场 run ok / delivered=true / 852.7s，产物三份落盘且无残留标记 —— 连续性恢复成立（非「偶发」）。但 852.7s 远高于 360s abort 阈值，需在 11-08 场确认阈值是否已放宽，否则随时可能再断。
- **P1-4 cron registry 可见性矛盾**：Scout 场 31 jobs，Life 场与本场均显示 total=1（已持续 2 场）。**需 owner 在 Control UI 核对真实 job 数与 triggersEnabled 状态**——若 registry 真的只暴露 1 条，NightOps 错峰与合并方案全部无法执行。
- **P1-5 Health agent 仍处停摆**：memory 目录只有 dreaming/，无任何 nightly 产出，cron registry 中查无该 agent 作业。**待 owner 拍板去留**（与 Finance 停摆近 7 个月同属一类挂账项）。
- **P1-6 Finance 停摆近 7 个月**（最后报告 04-07）：待 owner 拍板去留，不再每场占用注意力。

## 🟢 P2 — 观察项

- Life：微博 AI 归零（0/52，观察项①闭环）→ 11-08 核对是否回归；知乎 AI 13.3%↑，产出物化三档口径（作品型 29.63% / 资讯型 1.48% / 猎奇型 0.11%，基线 4.29%）下场面复算。
- Scout：LanceDB 464→516 行，主图 2,565 节点 / 6,058 边 / 38 社区；GHSA 连续 6 窗零新增，但 MCP spec 本窗修了 oneOf 类型检查绕过 → 安全压力在验证逻辑而非已知 CVE。
- 中间产物清理：`scout-raw/`、`graphify-out/` 仅保留最近 7 天。
- BILIBILI_COOKIES / OPENROUTER_API_KEY 仍未配置。

---

## ✅ 本场已闭环（不再占用注意力）

- M365 stdlib 遮蔽（`selectors.py`）→ 已修 + 验证 + 提交本地 `40b27fc`；ruff 34→0 违规 + CI（lint / import-smoke）已落地。
- News Digest 11-06 08:00 场 20,854B 推送成功，作业状态回到 ok。
- 代理 25017 / 8080 FastAPI / ollama 11434（172.18.160.1）双端口可达。
- 根分区 17%、M365 bare-except 0 hits、tracked .pyc = 0、Coder 卫生归档完成。
- MiniMax 直连正常（watchdog err=1，无 429 峰值）；错峰方案优先级下调（实测 heartbeat 相位跨度 26/30 分钟，同相并不严重）。

---

## 📌 明日（11-08）需 Main 拍板的三件事（按紧急度）

1. **NAS 回收站清理授权**（P0-1）—— 今晚 03:00 即第 3 次备份拦截，越晚处理积压越多。
2. **Gateway 重启**（P0-2）—— 一次动作同时解 SQLite 租约自锁与 RSS 3.24GB 正增长。
3. **M365 `git push` 授权**（P0-3）—— 修复已就绪，仅差一次 push。
