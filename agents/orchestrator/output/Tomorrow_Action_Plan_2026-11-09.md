# Tomorrow Action Plan — 2026-11-09

_生成：2026-11-08 02:40 CST · Orchestrator NightOps · 来源：Scout/Life/Coder 11-08 场 + cron/state 实测_

## P0（需 Owner/Main 授权，不可自动执行）

1. **NAS 备份链断档第 3 天 → 今晚 03:00 第 4 次被拦截**
   - 根因（Life 已实测）：NAS(SMB) 上 `rm` = 移入 `#recycle`，空间不释放；清理只扫 `WSL/`，从不扫回收站。
   - **最小动作**：删 0 字节残骸 `openclaw-20261005-0300.tgz` + 任意 1 份 08～09 月档（4.25GB）→ 回收 ~4.25GB，AVAIL 4G→8G+，今晚备份即可通过。
   - 治本：回收站内容先 `mv` 到本地 `/dev/sdd`（790G 可用）→ NAS 侧删除 → 确认释放后再删本地副本；同时 `RETAIN_DAYS` 30→14 且清理绕过回收站。
   - 影响面参考：`/mnt/h/#recycle/AI/openclaw.zone/WSL` 27 份 ≈123GB；`/mnt/h/AI/openclaw.zone/WSL` 22 份 ≈156.5GB。
   - 本地原生备份链路 🟢 健康（11-07 03:48 verify OK，6.3G@~/openclaw-backups，剩 791G）→ NAS 只是异地副本，非单点。

2. **SQLite session reclamation：main 库写入仍冻结**
   - 观测：main 库 272.9MB（11-07 为 261MB）；main/finance/health/work 四库 mtime 停在 11-05 07:18~07:19；`agent_database_leases` 中 scout/coder 各有重复租约、finance/health 新增各 1 条，main/work 仍 0 owner。
   - 后果：`target=main` 的 job 成片失败 —— heartbeat:main **error 71x**（46→70→71）、memory-dreaming 2x、公网IP 2x、NightOps-记忆体系 3x，均为 `agent main unavailable (SQLite session reclamation commit checkpoint ...)`。
   - 动作：停 Gateway → `doctor --session-sqlite compact --session-sqlite-agent main` → heap 4096→8192 → `doctor --fix` → 重启。
   - 备注：`sessions_send/sessions_list` 带 agentId=main 会被同一错误阻断 → 系统内推送绕不过此 P0，必须 Owner 在 Gateway 外执行。

3. **M365 `git push origin HEAD` 授权**
   - 本地积压 3 个修复 commit（含 P0 `0c593a1` event-loop split + `40b27fc` stdlib 遮蔽修复），远端 `d2af52a` 仍是 HEAD 祖先（ahead 3 / behind 0，非分叉）；push --dry-run rc=0。
   - 远端 pushed_at 仍停在 2026-03-18 → 停滞 ~8 个月。

## P1（可自动派发 / 低风险）

4. **Coder U-10**：跑 `playwright install chromium`，补端到端验证（playwright 1.64.1 已装但无浏览器）。
5. **Coder U-12**：`history.py` 每条消息全量 `json.dump` → O(n²) 写放大，改增量/追加写。
6. **Coder U-13**：`/api/chat/stream` 名不副实（复用非流式实现），要么改名为 `/api/chat` 要么实现真流式。
7. **Scout/Life**：备份脚本告警链修复 —— 预检失败分支不发邮件（L259-265 只 log+write_heartbeat+exit 1）；且 `send_email.py` 的失败详情 `print` 走 stdout 而 `send_mail()` 只重定向 stderr → 日志里看不到失败痕迹。改为失败即告警 + 详情写 stderr。
8. **Scout**：LanceDB 版本清理 error 41x（weixin 投递目标缺失）、DNS-Drift-Monitor / NightOps-Dedup 各 error 10x —— 独立于 SQLite 主因，需单独修。

## P2（观察 / 择机）

9. OpenRouter 余额连续第 4 窗为 0（finance agent key 实测 `total_credits: 0`）→ 需 ZP 充值或换 key。
10. Gateway RSS 3.30–3.42GB（两次实测非单调），watchdog ~1.8MB/h，无泄漏 → 本周择机重启一次即可。
11. 合并重复 NightOps：工作日版 `0597835a` vs 每日版 `c46eeb63`。
12. `scout-raw/`、`graphify-out/` 中间产物只保留最近 7 天。
13. 跟踪 claude-code 隐私 mod(#107768) 是否修复 issue #107757。
14. `web_search` provider_error 连续第 18 次 + ddg html 000 / bing 302 / reuters 000 → 外网出口大面积不通，但直连 github/npm 200，属**非阻塞**。

## 趋势与健康观察

- **NightOps 双轨**：per-agent 4 路全 🟢（Scout 01:30 / Life 01:50 / Coder 02:20 / Orch 02:40，均 target=isolated + ok）；legacy `NightOps-*`（target=main）已 disable，未复发。
- **Agent 24h 产出**：coder 44 / scout 5 / orch 6 / life 2 / finance 1 / health 0 / work 0 → health/work 持续休眠，finance 已复活动作但仍受 OpenRouter 0 余额限制。
- **用户心理状态**：🟢 无负向信号。Life 本场无心理风险条目；Life NightOps 场次因 `LLM idle timeout (120s)` 被打断并 SIGTERM 掉 NAS 扫描进程，属下游症状非独立故障。
- **Scout 技术观察（值得记住）**：Anthropic 提出「agent memory 的组件」——记忆=跨会话保留的上下文（排除权重更新/in-context learning/compaction），CL-Bench 上 Opus 5 首次闭合学习循环（规则+如何知道规则为真+早前答案+已知坑），Sonnet 4.6 只留一堆未验证猜测。→ 直接启示：**本机记忆条目的每条结论应附「验证依据」与「已知坑」**，正对应 Scout 本场 3 条工具修复经验。
- **外部信号**：OpenAI 110 亿美元融资（1.25 万亿估值首笔 tranche）；开放权重与闭源网络安全能力差仅 8 个百分点（GPT-6 Sol 80.8% vs Deepseek V4.1 Flash 72.8%，成本 $22 vs $3）；Nous Arete-27B 证明权重级政治偏置可被微调剥离（宣传率 22%→<1%）。

## 待 Owner 拍板清单（累积）

1. P0-1 NAS 回收站删除授权（最小 4.25GB / 全量 123GB）
2. P0-2 Gateway 停机 doctor --fix 流程
3. P0-3 `git push origin HEAD`（M365）
4. `/reset` `agent:orchestrator:main`（495 msg / 204,801 tokens，overflow 2013）
5. 设置 `commands.ownerAllowFrom`
6. OpenRouter 充值/换 key
