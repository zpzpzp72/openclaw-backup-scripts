# 🌃 Main NightOps 复盘 — 2026-10-27 (周二) 03:00 场

**Runtime:** agent=main | session=agent:main:cron:603be37f-4a00-440c-8632-aee35cdfcc78
**窗口：** ✅ Mon–Fri 00:30–03:00（03:00 场，周二）
**收集方式：** 落盘报告 + cross-agent-log + 实测（ps/stat/df/gh）+ 已有 23:00 场产出合并（无重复生成）

---

## 1. 子 Agent 报告收集

| Agent | 本日报告 | 状态 | 要点 |
|---|---|---|---|
| Scout | `nightly-scout-2026-10-27.md` **缺位**（最新为 10-26 00:45） | ⚠️ 顺延 | arXiv 140 条目 ✅、GitHub 24 端点 ✅、HN top 30 ✅、RSS 三源 ✅；**头号发现：mcp/servers v2.1.0 一次修 8 个漏洞**（filesystem TOCTOU×4、server-everything 跨源 env 外泄、fetch SSRF×3）；升级须显式版本号（semver 陷阱）；CVE-2026-111497 Brotli RCE CVSS 9.2（HN 365 分）；MCP spec 连续 10 场无 release（已 90 天）；web_search 连续 8 天失败为唯一红灯 |
| Life | `nightly-life-2026-10-27.md` (00:55) | ✅ | 极简场：B站日报与 news_digest 连续 2 日恢复 30 条；平台地图知乎🟢公众号🟢B站🟡微博🔴X🔴；P0 双选题：①「20 万媒体/艺术岗位没了，多少是 AI 的？」②「B站 14 天 140 条复盘：'合集'完胜'爆款'」 |
| Coder | `nightly-coder-2026-10-27.md` (01:30) | ✅ 回归 | **中断 7 天后回归**（10-26 关注点闭环）。备份 5 天连绿但 /mnt/h 98% 容量告警；`.memory-write.lock.lock` 进 tar 扫描→tar 退出码 1（产物完好），修正思路 backup.sh 加 --exclude；git 590 dirty（579 untracked+11 changed）+ahead 25；Gateway RSS 2GB（重置后）、CPU 148% @ 01:15 待白天核验；AMAT 邮件+飞书双通道首通；copilot_proxy audit.test.ts 3892 行待拆 |
| Orchestrator | `nightly-orchestrator-2026-10-27.md` (02:45，非标时间) | ✅ | 合并+10-28 明日计划落盘：P0×3（Memory 复查/fallback 重写/MiniMax 套餐）；注意 02:40 仍处 MiniMax burst 耗尽窗口（02:00–05:00）内，报告以 cache/低耗为主，可接受⚠️ |
| main(自身) | 本文件 | ✅ | 全局复盘落盘 ✓ |

## 2. 系统服务状态总表（03:05–03:07 实测）

| 服务/组件 | 状态 | 实测证据 |
|---|:---:|---|
| Gateway 进程 | 🔴 | pid 497240，01:13 起 uptime ~1h50m；**RSS 5.95GB**（ps 5953628KB）、**CPU 168-171%不回落**（10-26 记录为 86.9%→本日更恶劣）。⚠️ 10-26 复盘中 pid 319857/10.94GB 数据已过期——**用户已于 10-27 01:13 重启**，P0-1"重启"半边达成；heap 上限 4096MB，RSS 5.95GB 已超 heap 上限，堆外增长模式与既往一致（非泄漏）；**会话保留策略（清 1956 json + 605 zst）仍未处理**，为防回升真杠杆，待 ZP 授权 |
| 03:00 备份流程 | 🟢→🟡 | 心跳 `last_run=2026-10-27 03:00:01`，status=starting，need_backup=true，**hours_since_last_backup=23（<25h 阈值，未触发强制 tar）**；⚠️ 无 openclaw-backup.sh 进程在跑（ps 03:05/03:07）——脚本可能已快结束或异常退出，心跳 status 尚未更新为 ok/error，**异常挂起点待核** |
| 03:00 备份产物 | 🟢 | `openclaw-20261027-0300.tgz`（03:08 落盘 4.1GB，完整流末尾非零 tar block 核验通过；较前两日 9.2GB/9.4GB 明显缩小）⚠️ 体积骤减超 5GB，且**落盘早于心跳 status 更新**：疑为「先写 tar 后写心跳」时序或 tgz 未含 LanceDB 9.5G 大体量目录——**待核对 tgz 内容清单 vs exclude 规则**。tar 退出码 1（.memory-write.lock.lock 被扫入）延续在案 |
| /mnt/h 磁盘 | 🔴 | **98%（剩 178G）**，较 10-26 记录 186G 继续下降；h 盘接近满，需 ZP 清旧档 |
| 飞书出站 | 🟢 | 直连 200（延续） |
| web_search | 🔴 | 连续 9 天（10-06→10-27） |
| news_digest | 🔴 | 延续昨况；BILIBILI_COOKIES / OPENROUTER_API_KEY 未补齐 |
| 版本 | 🟡 | 2026.10.5 vs 2026.10.7 |
| Heartbeat delivery | 🔴 | 8 job 占位 telegram:123456789（延续） |
| Workspace git | 🔴 | **597 dirty**（11 changed + 586 untracked，本日新增 heartbeat 复盘/main 记忆/heartbeat-state 变更+新增 daily-verify-2026-10-27.md） |
| CI/健康检查 | 🟡 | GitHub Health Check 5/5 通过（03:06）；memory-lancedb-pro CI 10-05 红灯在案；独立 Windows 健康检查每 6h 运行 |

## 3. 升级审核（Orch 计划逐项裁决）

**裁定原则**：不替 ZP 动 systemd；删除资产、改配置属授权级——全部列 ZP 白日队列。

| # | 事项 | 裁决 | 路由 |
|---|---|---|---|
| P0-1a | Gateway 重启 | ✅ 已由 user 执行（01:13，pid 497240，RSS 5.95GB） | **完成半项** |
| P0-1b | 会话保留策略（清 1956 json+605 zst） | ✅ 分析成立，删除资产须 ZP 亲自/授权；重启仅买时间 | **ZP 白日** |
| P0-2 | 重启后 3-4h RSS/CPU 复查 | ✅ 分析成立；今日 3-4h 后复查 | Coder |
| P0-3 | MiniMax Token Plan 三选一 | ✅ 分析成立（配额管理：`mmx quota` 查余量，CN key 走 api.minimaxi.com） | **ZP 拍板** |
| P0-4 | M365 push 凭证 PAT/SSH | ✅ 凭证类须 ZP 亲自配置（截止 10-29 剩 2 天） | **ZP 白日** |
| P1-5 | qwen3.6:27b ECONNREFUSED | ✅ Coder 白天执行 | Coder |
| P1-5b | 临时 fallback 链 4b→deepseek-flash/pro→M2.7 | ✅ 证据链完整；写入配置待 ZP 拍板后由 Main 白天执行 | ZP 拍板→Main |
| P1-8 | 监控 08:00 news digest | ✅ Orch 心跳照办 | Orch |
| P2-10 | health/finance 停摆去留 | 判定维持“跑但产出缺位”观察；去留 ZP 决策 | **ZP 决策** |
| P2-11 | 备份脚本 --exclude .memory-write.lock.lock | ✅ 提案成立，并入下一版 backup.sh | Coder |
| P2 | untracked 收口 / PR 评估 / Heartbeat 路由改飞书 | 例行 + 路由改飞书建议（8 job 全部占位） | Orch/Coder |

## 4. 全局复盘

**本场特征：报告收集层 100% 落地（3/4 落盘，Scout 顺延），执行层 0% 主动执行**——受 v3 规则与授权边界约束，所有变更项均列 ZP 白日队列。

**A. 质量亮点**
- Coder 中断 7 天后回归，关键深挖发现有效（memory-write.lock、备份盘容量、git 状态）。
- 10-26 关注点「Coder nightly 恢复」当日闭环，口径验证有效。

**B. 系统层三根轴**
1. **Gateway 内存**：重启后 RSS 5.95GB（堆外增长模式确认，非泄漏）；`--max-old-space-size=4096` 下 RSS 超 heap 上限印证堆外；**真杠杆=会话保留策略**，待 ZP 授权。
2. **磁盘水位**：/mnt/h 98% 剩178G继续下降+备份盘 98%（Avail 279G→183G→178G 连日下滑）；备份盘剩余 271G→178G，5 日内降 93G，**10-27 当晚备份仍有失败风险**。建议优先清旧档（RETAIN_DAYS=30 名存实亡，39 份未清）。
3. **MiniMax 429 / fallback**：凌晨 83% 429 峰值 = Token Plan 5h 窗口耗尽（非认证）；deepseek-flash/pro 为可用备选，临时链写入等 ZP。

**C. 内容/情报主线**
- 「批准必须绑定到具体效果」主线保持；MCP v2.1.0 修复面 + arXiv 安全论文支撑安全叙事。
- 内容 P0 双选题就绪：①「20 万媒体岗位中美同题」②「B站 14 天复盘」可同日双发。
- 10-27 场 Orch 报告于 02:40 生成，仍在 MiniMax burst 窗口（02:00-05:00）内——**错峰调度未覆盖 Orch 场次**，建议后续再前移 Orch 晚场触发时间。

**D. 本场无变更说明**
- 无 npm 安装、无配置/调度器变更；产出：本报告 + nightly-main 记忆 + heartbeat-state.json 同步 + daily-verify 文件新增（untracked 增 3 项）。

## 5. 下一场关注点（10-28 周二 00:30 起）

| 关注点 | 判定标准 |
|---|---|
| 03:00 备份结果（心跳确认） | /mnt/h 98% 收敛；无 backup.sh 命失败告警 |
| RSS/CPU 增速 | <200MB/h，且 CPU 不持续 >80% |
| 08:00 news digest | cron 是否成功 |
| Scout 10-27 恢复 | `nightly-scout-2026-10-27.md` 落盘 |
| qwen3.6:27b 探活 | ECONNREFUSED 是否消失 |
| 主群会话 failed 恢复 | sessions_list 快照 |
| Workspace git 收口 | untracked 下降 |
| MiniMax 429/配额 | 429 频次回落 / `mmx quota` 余量 |
| arXiv 周一批次 | cs.AI 突破 2610.31667 |
| MCP spec / Go SDK v1.9.0 | tags / releases |
| web_search 恢复 | provider 配置修复 |

---
**产出：** `heartbeat/main-nightops-review-2026-10-27.md`（本场终版）· `memory/nightly-main-2026-10-27.md` · `heartbeat/heartbeat-state.json` 同步 · `heartbeat/daily-verify-2026-10-27.md`（夜间验证补位）
**无 npm 安装 / 无配置变更 / 无 subagent 挂靠。下一场：2026-10-28 周三 00:30 起。**
