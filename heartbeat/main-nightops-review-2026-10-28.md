# 🌃 Main NightOps 复盘 — 2026-10-28 (周三) 03:00 场

**Runtime:** agent=main | session=agent:main:cron:603be37f-4a00-440c-8632-aee35cdfcc78
**窗口：** ✅ Mon–Fri 00:30–03:00（03:00 场，周三）

---

## 1. 子 Agent 报告收集

| Agent | 本日报告 | 落盘时间 | 状态 |
|---|---|---|:---:|
| Scout | `nightly-scout-2026-10-28.md` | 00:41 | 🟢 |
| Coder | `nightly-coder-2026-10-28.md` | 01:23 | 🟢 |
| Orchestrator | `nightly-orchestrator-2026-10-28.md` | 02:55 | 🟢 |
| Life | `nightly-life-2026-10-28.md` 未落盘（最新 10-27） | — | 🔴 缺席第 3 场 |
| main(自身) | 本文件 | 03:12 | 🟢 |

## 2. 系统服务状态总表（03:11–03:13 实测）

| 服务/组件 | 状态 | 实测证据 |
|---|:---:|---|
| Gateway 进程 | 🔴 | pid 497240，uptime 1d02h；RSS **9.9GB** / CPU 82%；watchdog 连续 WARN 超阈值 8GB，增速 ~74MB/h → 3–4 天内重回 12GB+ |
| 03:00 备份（10-28） | 🟢 | `openclaw-20261028-0300.tgz` 03:06:53 落盘 **6.0G**（较前日 8.9G -33%，exclude 部分生效） |
| cleanup_old | 🟡 | 本次未触发（10 份老档全在，71.2GB 未释放）；释放速度 < 产品增速 |
| /mnt/h 磁盘 | 🔴 | **98%（剩 171G）**，连续下滑：178→177→171G |
| /mnt/m 挂载点 | ❌ | 路径不存在，heartbeat-state 记录陈旧（已修正移除） |
| 版本 | 🟡 | 2026.10.5 vs latest 2026.10.8（升级需 ZP 授权） |
| 飞书出站 | 🟢 | 直连 200（延续） |
| web_search | 🔴 | 连续 10 天 provider_error（10-06→10-28） |
| news_digest | 🔴 | BILIBILI_COOKIES / OPENROUTER_API_KEY 未补齐 |
| Heartbeat delivery | 🔴 | 8 job 占位 telegram:123456789 |
| Workspace git | 🟡 | 69 dirty（53+15+1），较 Orch 昨晚 648 大幅收敛，nested repo 仍阻断 |
| Watchdog | 🟢 | 运行连续、告警按阈值正常发出 |
| Health/Finance | ⚪ | 持续无产出（待 ZP 决策） |

## 3. 升级仲裁

| 事项 | 裁决 | 归属 |
|---|---|---|
| P0-1 git 收口 648→69 | 成立；agents/ nested repo 待处理 | Coder 白天 |
| P0-2 备份 cleanup_old 未触发 | 成立；tar 退出码捕获亦缺 | Coder 白天 |
| P0-3 Gateway RSS 9.9GB 超阈值 | 成立；arena 实验**待 ZP 授权** | ZP→Coder |
| P0-4 Life 缺席排查 | 升级：cron 打卡正常但零产出，查脚本 stderr | Coder 白天 |
| P1 发文 / web_search / MCP 包 / 升级 10.5→10.8 / key 补齐 | 成立；凭据类须 ZP 亲自 | ZP/Coder 白天 |
| P2 交付路由 / zero-token pkg / CI 红灯 / PR 评估 | 延续例行 | Coder/Orch |

## 4. 全局复盘

**本场特征：报告层 3/4 落地，执行层 0%（按 v3 规则不替 ZP 动系统）。**

- **亮点**：Scout 最强信号（ETH / S-1 / 接口攻防）；Orch 交叉验证量化 RSS 增速（~74MB/h）并实测证伪 cleanup 生效；备份 exclude 修复初见成效（8.9→6.0G）
- **三根轴**：
  1. Gateway RSS 9.9GB +4GB/日 → 3–4 天重回 12GB；真杠杆=保留策略+arena 对照，待 ZP
  2. /mnt/h 98% 剩 171G 连续下滑 + cleanup 未触发 → **风险比昨日升一级，建议 ZP 白日优先清旧档**
  3. 备份链修复 3 项中 2 项（cleanup、退出码捕获）未按预期 → 明晚核验升级为两项
- **情报主线**保持完整：「批准≠没越界」「证明机器可重跑」「接口层攻防」
- **Orch 误报澄清**：memory 文件名含空格的文件实测不存在，判误报
- **无变更说明**：无 npm 安装、无配置/调度器变更、无重启发动

## 5. 下一场关注点（10-29 周四 00:30 起）

| 关注点 | 判定标准 |
|---|---|
| backup.sh cleanup 调用链 | 老档 7.5~8.9G×10 自动清；tar 退出码 |
| RSS & CPU | <200MB/h；CPU 不持续>80% |
| Life 恢复 | nightly-life-2026-10-28/29.md 落盘 |
| 08:00 digest | cron 成功 |
| web_search 恢复 | provider 修复 |
| MCP spec 发版 | 92 天+ |
| openai/math 外部回应 | 复核工作组结论 |
| Anthropic S-1 文件 | 安全/评测支出条款 |
| git 收口 | 69 dirty → 接近 0 |
| MiniMax 配额 | 429 频次 / mmx quota |

---
**产出：** `heartbeat/main-nightops-review-2026-10-28.md` · `memory/nightly-main-2026-10-28.md` · heartbeat-state.json 同步
**无 npm 安装 / 无配置变更 / 无重启发动。下一场：2026-10-29 周四 00:30 起。**
