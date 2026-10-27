# OpenClaw Coder 夜检报告 — 2026-10-28（01:23 Asia/Shanghai）

Agent: main (Coder) | Host: AMD-AI9-X1-HX370 (WSL2) | Repo: /home/zhiping/.openclaw/workspace

## 一、GitHub CI/CD 状态（账号 zpzpzp72，共 17 个仓库）

| 仓库 | 可见性 | 最近推送 (UTC) | CI 状态 | 标记 |
|---|---|---|---|---|
| openclaw-backup | PRIVATE | 2026-10-26 19:30 | 未配置 workflow（数据备份仓库） | ⚪ |
| openclaw （fork，上游 openclaw/openclaw） | PUBLIC | 2026-07-23 | 混合：见下方明细 | ⚠️ |
| openclaw-backup-scripts | PUBLIC | 2026-09-06 | 未配置 workflow | ⚪ |
| 其余 14 个仓库 | 大多 PUBLIC | 2026-03 之前 | 未配置 workflow，长期无推送 | ⚪ |

fork 仓库 `zpzpzp72/openclaw` 最近运行明细（2026-09-21 ~ 09-28，基准分支）：

| Workflow | 时间 (UTC) | 结论 | 标记 |
|---|---|---|---|
| CodeQL Critical Quality | 09-22 11:56 | success | ✅ |
| CodeQL | 09-22 10:32 | success | ✅ |
| Install Smoke | 09-22 08:30 | **failure** | ❌ |
| Scheduled Live And E2E Checks | 09-22 09:22 | **failure** | ❌ |
| PR CI Sweeper | 09-21 13:55 / 19:17 | **failure**（×2） | ❌ |
| Node 22 Compat | 09-28 11:46 | skipped | ⏭ |
| CodeQL Android Critical Security | 09-22 12:28 | cancelled | ⛔ |
| OpenClaw Performance / QA-Lab / Control UI Locale | 09-22 | cancelled / skipped | ⛔ |

结论：✅ 静态质量与安全扫描通过；❌ 安装冒烟（Install Smoke）、Live/E2E、PR 清理链三类持续失败，集中于 09-21/09-22，之后无新触发（活跃度低）。

## 二、OpenClaw 升级与构建风险

- 本地安装版本：**2026.10.5 (1b58cb9)**；npm latest：**2026.10.8** → 存在新版本可升级。
- 构建风险：本地为全局 npm 安装（非源码构建），升级动作本身风险低；但 fork 的 Install Smoke 失败说明上游安装链路在 09-22 存在问题，升级前建议确认上游是否已修复。
- Gateway 运行正常：PID 497240 与 `heartbeat/heartbeat-state.json` 记录一致 ✅。
- 风险评级：**⚠️ 中低**（patch 级差距 3 个小版本，非紧急；建议在维护窗口执行 `openclaw update --yes`，需 owner 授权）。

## 三、代码库变化与依赖更新

最近 3 次提交（本地 workspace 仓库，含未推送改动的工作区）：

| 提交 | 时间 +0800 | 说明 | 规模 |
|---|---|---|---|
| 952e5a12 | 10-28 00:43 | docs(nightops): 记忆体系讨论纪要 v28 | +150 行（memory/2026-04-15.md） |
| f169a9ed | 10-28 00:42 | feat(scout): 10-28 夜间研究（OpenAI ETH 推翻 / Anthropic S-1 / 接口层攻防） | 约 1.5 万行（graphify 快照 9452 行 + scout-raw 语料） |
| 24b74a5f | — | docs(learnings): set -e 静默中断与 exclude 路径失效根因 | 小 |

依赖与供应链观察：

- 本轮（今晚）**未安装任何新 npm 包** → 触发安全审计的条件不满足，无需执行 npm 审计（规约保持待命）。
- 工作区根目录无 package.json；`wechat-cli` 仅有 ruff/pytest 的 pyproject 配置。
- ⚠️ 遗留项：`openclaw-zero-token/` 内含 vendored `package.json`，版本停在 **2026.3.28**（陈旧约 7 个月，落后当前安装版 2026.10.5）。若有人从该目录构建，会引入旧代码 —— 标记为待清理/同步项。

## 四、附带系统观察（heartbeat-state 交叉核对）

| 项目 | 实测 | 状态文件记录 | 判定 |
|---|---|---|---|
| Gateway PID | 497240 存活 | 497240 | ✅ 一致 |
| lastChecks.nightops | — | 10-27 03:00 (+08) | ✅ 正常节律 |
| /mnt/h (NAS dxp4800plus) | 98%（7.1T/7.2T，剩 177G） | 98% | ⚠️ 接近满 |
| /mnt/m | 路径不存在（已卸载/改名） | 97% | ❌ 状态陈旧 |

## 五、服务状态总览

| 服务 | 状态 | 指示 |
|---|---|---|
| GitHub API & gh CLI | 正常 | ✅ |
| OpenClaw Gateway (PID 497240) | 正常 | ✅ |
| npm registry 访问 | 正常 | ✅ |
| 本地核心仓库 CI | 未配置 | ⚪ |
| fork openclaw CI（质量/安全扫描） | 通过 | ✅ |
| fork openclaw CI（安装/冒烟/E2E） | 失败（09-22） | ❌ |
| /mnt/h NAS 空间 | 98% 用量 | ⚠️ |
| /mnt/m 挂载点 | 缺失（状态陈旧） | ❌ |

— Coder Agent · 2026-10-28 01:23
