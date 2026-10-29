# OpenClaw Coder 夜检报告 — 2026-10-29（01:30 Asia/Shanghai）

Agent: main (Coder) | Host: AMD-AI9-X1-HX370 (WSL2) | Repo: /home/zhiping/.openclaw/workspace

NightOps 窗口检查：周四凌晨 01:30，处于计划夜检窗口内，按计划执行 ✅

## 一、GitHub CI/CD 状态（账号 zpzpzp72，26 个仓库）

| 仓库 | 可见性 | 最近推送 (UTC) | CI 状态 | 标记 |
|---|---|---|---|---|
| openclaw-backup | PRIVATE | 2026-10-27 19:30 | 未配置 workflow（数据备份仓库） | ⚪ |
| openclaw-backup-scripts | PUBLIC | 2026-09-27 17:28 | 未配置 workflow | ⚪ |
| openclaw（fork，上游 openclaw/openclaw） | PUBLIC | 2026-07-23 | 混合，见下方明细 | ⚠️ |
| memory-lancedb-pro（fork） | PUBLIC | 2026-05-05 | CI 最新一次 **failure**（05-05），上次成功 04-06 | ❌ |
| claude-code（fork） | PUBLIC | 2026-05-31 | Issue Sweep / Lock Stale / Auto-close 三个维护 workflow 全部 success（05-31） | ✅ |
| 其余约 20 个仓库（多为 fork，早期项目） | 多为 PUBLIC | 2026-03 前至 2015 | 未配置 workflow，长期无推送 | ⚪ |

与昨日对比：无任何仓库产生新 CI 触发；`openclaw-backup` 推送时间前进 1 天（正常每日备份提交）。

fork 仓库 `zpzpzp72/openclaw` 最近运行明细（2026-09-21 ~ 09-28，与昨日一致，无新增触发）：

| Workflow | 时间 (UTC) | 结论 | 标记 |
|---|---|---|---|
| Node 22 Compat | 09-28 11:46 | skipped | ⏭ |
| CodeQL Android Critical Security | 09-22 12:28 | cancelled | ⛔ |
| CodeQL Critical Quality | 09-22 11:56 | success | ✅ |
| CodeQL | 09-22 10:32 | success | ✅ |
| Install Smoke | 09-22 08:30 | **failure** | ❌ |
| Scheduled Live And E2E Checks | 09-22 09:22 | **failure** | ❌ |
| PR CI Sweeper | 09-21 13:55 / 19:17 | **failure**（×2） | ❌ |

结论：静态质量与安全扫描（CodeQL）通过 ✅；安装冒烟、Live/E2E、PR 清理链三类持续失败 ❌，集中于 09-21/09-22，之后无新触发（fork 活跃度低，属于陈旧失败而非新增回归）。

## 二、OpenClaw 升级与构建风险

- 本地安装版本：**2026.10.5 (1b58cb9)**；npm latest：**2026.10.8** → 存在 3 个 patch 级版本可升级。
- dist-tags：latest=2026.10.8，extended-stable=2026.9.35，beta=2026.10.10-beta.4。
- 本地为全局 npm 安装（非源码构建），升级动作本身风险低；但 fork 的 Install Smoke 历史失败提醒升级前留意上游安装链路是否已修复（09-22 后无新触发，无法确认）。
- Gateway 运行正常：PID 497240 自 10-27 起存活，与 `heartbeat/heartbeat-state.json` 记录一致 ✅。
- 风险评级：**⚠️ 中低**（patch 级差距，非紧急；建议在维护窗口执行 `openclaw update --yes`，需 owner 授权）。

## 三、代码库变化与依赖更新

本地 workspace 仓库最近提交：

| 提交 | 时间 +0800 | 说明 | 规模 |
|---|---|---|---|
| 092b27d1 | 10-28 02:55 | docs(orchestrator): nightly-orchestrator 2026-10-28 汇总与次日计划 | 134 行×2 文件 |
| c9353413 | 10-28 02:49 | chore(nightops): 工作区收口 — 10-26~10-28 夜检产物、报告与系统记忆批量入库 | 大批量 |
| c12d5ec6 | 10-28 01:28 | docs(nightops): coder 夜检 2026-10-28 | 小 |

今晚新增观察：

- 工作区根目录新增 `build_corpus_1028.py` / `build_graph_1028.py` / `merge_graph_1028.py`（10-28 00:36~00:37，graphify 语料/图形生成管线），已随 c9353413 入库。
- 工作树存在多处未提交改动：`DREAMS.md`、`agents/orchestrator/*`（含删除 `TOOLS.md`）、`heartbeat/heartbeat-state.json`、`memory/` 多文件、`reports/*.png` 等。属正常夜间运行产物，建议由 main/orchestrator 后续收口。
- ⚠️ **异常文件名待处理**：git 索引中存在 `memory/nightly-main-2026-10-27.md nightly-main-2026-10-29.md` —— 单个文件名内部含空格，疑似 10-27 夜检生成时字符串拼接错误所致（且指向尚未生成的 10-29 文件名）。当前工作树中已显示删除，需提交该删除或修正命名，避免后续收口时干扰。

依赖与供应链观察（对照安全审计规约）：

- 本轮（今晚）**未安装任何新 npm 包** → 触发安全审计的条件不满足，无需执行 npm 审计（规约保持待命）。
- ⚠️ 遗留项：`openclaw-zero-token/` 内含 vendored `package.json`，版本仍停在 **2026.3.28**（陈旧约 7 个月，与当前安装版 2026.10.5 差距继续扩大）。若有人从该目录构建会引入旧代码 —— 保持标记为待清理/同步项。

## 四、系统观察（heartbeat-state 交叉核对）

| 项目 | 实测 | 状态文件记录 | 判定 |
|---|---|---|---|
| Gateway PID | 497240 存活（自 10-27 起） | 497240 | ✅ 一致 |
| lastChecks.nightops | 本次夜检执行中 | 10-28 03:12 (+08) | ✅ 节律正常 |
| /mnt/h（NAS dxp4800plus） | 98%（7.1T/7.2T，剩 171G） | 98 | ⚠️ 接近满（较昨日 177G 又少约 6G） |
| /mnt/m | 路径不存在（已卸载/已移除） | 已无 mnt_m 记录 | ✅ 陈旧记录已被清理 |

## 五、服务状态总览

| 服务 | 状态 | 指示 |
|---|---|---|
| GitHub API & gh CLI | 正常（token zpzpzp72，scopes: repo/workflow/read:org/gist） | ✅ |
| OpenClaw Gateway (PID 497240) | 正常运行 | ✅ |
| npm registry 访问 | 正常（可见 latest 2026.10.8） | ✅ |
| 本地核心仓库 CI | 未配置 | ⚪ |
| fork openclaw CI（质量/安全扫描） | 历史通过，无新触发 | ✅ |
| fork openclaw CI（安装/冒烟/E2E） | 历史失败（09-22），无新触发 | ❌ |
| memory-lancedb-pro CI | 最新一次失败（05-05，陈旧） | ❌ |
| workspace git 工作树 | 多处未提交改动 + 1 个异常文件名 | ⚠️ |
| /mnt/h NAS 空间 | 98% 用量，剩余 171G（持续缩减） | ⚠️ |
| /mnt/m 挂载点 | 已消失，状态文件已同步清除 | ✅ |

— Coder Agent · 2026-10-29 01:30
