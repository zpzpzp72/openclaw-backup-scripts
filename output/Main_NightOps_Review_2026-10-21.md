# Main NightOps — 全局复盘 2026-10-21 05:00

## 服务状态表

| 服务 | 状态 | 详情 |
|---|---|---|
| Backup (03:00) | 🟢 正常 | openclaw-20261021-0300.tgz, 8.8GB, 03:12 完成 |
| FastAPI :8080 | 🟢 正常 | python pid 615 监听中 |
| 代理 :25017 | 🔴 宕机 | 第 9 天, 端口未监听, 无进程 |
| News Digest | 🟢 已恢复 | 10-20 成功 (MiniMax 降级路径) |
| OpenRouter API | 🔴 余额耗尽 | 402 Insufficient credits |
| orchestrator NightOps | 🟡 有产出 | 计划已生成, 无法推送 |
| coder NightOps | 🟡 有产出 | 报告已生成 |
| scout NightOps | 🟢 有产出 | 报告已生成 |
| life NightOps | 🔴 无报告 | 4 条消息后中断 |
| sessions_send | 🔴 禁用 | 子 Agent 无法主动推送 |

## 升级审核

### P0 — 需要 Owner 决策
1. **M365_Copilot_Playwright_Proxy 归档裁决** — 199 天停滞, 4×P0 未解, 距 11-07 硬归档线剩 **13 天**。
   - P0-1 REPO_STALE / P0-2 ORIGIN_ORPHAN (4 个 NightOps commit 被阻塞)
   - P0-3 MISSING_GITIGNORE + STAGED_PYC (.pyc 已暂存, 会阻塞任何提交)
   - P0-4 COPILOT_BARE_EXCEPT (browser.py:41 静默吞掉 Playwright 错误)
2. **NAS 容量逼近上限** — /mnt/h 96% 已用, 剩余 313G, 单份备份 ~1GB/天且逐日增大。
   预计 **~4-5 个月**内耗尽, 现有 34 份历史备份无保留策略。
3. **代理 25017 第 9 天宕机** — 外网新闻源依赖降级路径维持。

### P1 — 建议本周处理
- life NightOps 连续中断 (memory 最后写入停在 2026-09-08), Bootstrap 或指令读取阶段卡死。
- sessions_send 禁用导致子 Agent 只能写文件, 无主动上报通道。
- OpenRouter 余额耗尽, 目前靠 MiniMax 单点支撑。

## 全局趋势
- ✅ 备份链连续正常, News Digest 打破 8 天空档。
- 🔴 代理 25017 / Life Agent 双长期故障。
- 🔴 新增风险: NAS 容量无保留策略。

## 待办归属
- Owner: M365 归档裁决 + NAS 保留策略 + 代理恢复
- Coder: .gitignore + unstaging .pyc (可在裁决前先做, 无风险)
