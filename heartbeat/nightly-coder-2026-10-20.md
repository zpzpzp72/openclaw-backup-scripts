# Nightly Coder Report - 2026-10-20

**Generated:** 2026-10-20 22:20 (Asia/Shanghai) - Tue NightOps Coder slot (cron:a38acaaa-52ef-4e46-badf-8104a6fd1c41)
**Runtime:** OpenClaw **2026.10.5** (1b58cb9) | gateway self-report 2026.10.5 OK | host AMD-AI9-X1-HX370 | WSL2 6.6.87.2
**Window:** Tue 22:20 - inside standard Mon-Fri 21:30-23:30 NightOps slot OK
**Continuity:** Night after yesterday - no coverage gap. Delta vs last report 2026-10-19 22:20.

---

## 0. 服务状态表 (Service Status Table)

| 子代理 / 服务 | 状态 | 上次报告 | 备注 |
|--------------|------|---------|------|
| NightOps-Coder | 🟢 | 2026-10-19 22:20 CST | 本场 10/20 22:20 CST，连续第 2 夜，无缺口 |
| OpenClaw binary | 🟢 | 2026.10.5 | 二进制 = gateway self = npm latest = **2026.10.5**，三方一致 |
| npm dist-tags | 🟢 | 2026.10.5 | latest **2026.10.5**; extended-stable 2026.9.33; beta 2026.10.10-beta.2（beta 未采纳） |
| Gateway systemd | 🟢 | pid 24075 | **pid 24075 未变**（同 10/19）— restart 后稳定 >24h，无再次重启 |
| Node 双版本分歧 | 🔴 | v24.15.0 / v26.10.0 | **第 2 夜未解**：shell `node -v` = **v24.15.0**；gateway 进程实际跑 **v26.10.0**（nvm）。PATH 层 24 优先，走 shell 的脚本会取错版本 |
| Node service (systemd) | 🟡 | not installed | openclaw 自身无 node systemd unit（预期行为，gateway 走 user systemd） |
| GitHub auth | 🟢 | zpzpzp72 | keyring token，scopes: gist/read:org/repo/workflow |
| GitHub API 网络 | 🟢 | 0 timeout | 本场 5 仓 actions/runs 全部回包，无 TLS 超时（连续第 3 夜稳定） |
| CI - openclaw fork | 🔴 | 2026-09-28 | **stale 22d**（+1d），Actions 未被新提交触发（疑似 fork 上禁用/未 watch upstream） |
| CI - memory-lancedb-pro | 🔴 | 2026-05-05 failure | **~168 天未处理**（+1d），**第 19 夜携带**；插件仍在生产启用 |
| CI - 其余 3 仓 | 🟢 | empty | backup-scripts / openclaw-zero-token / amat-stock-report 无 workflow run |
| Open PR（backup-scripts） | 🟡 | 2 个陈旧 | #4 (2026-04-11, 194d) / #2 (2026-03-19, 185d) 均 OPEN；#4 与已合入 STOP_GATEWAY 功能重复，建议关单 |
| Workspace drift | 🟡 | 8M/1D/89?? | 10/19: 9/1/87 → M -1、untracked +2；9 files, +552/-1065 |
| 本地分支 | 🟢 | feature/hot-backup | 与 origin **完全同步**（0 unpushed commits） |
| openclaw-source fork | 🟢 | 0790d9f593a | clean，与 10/19 同 commit（自 10/09 未变） |
| Backup 归档 | 🟢 | 2026-10-20 03:12 | **openclaw-20261020-0300.tgz 8.54 GiB**（环比 10/18 +0.63GB）；10 月 16 份齐全 |
| Backup 日志 | 🟡 | 2026-10-20 03:12 | 写入正常；**连续 3 条「❌ 发送失败: Connection unexpectedly closed」** = 事后飞书通知持续失败 |
| openclaw status backup 字段 | 🟡 | "last ok 19d ago" | **第 2 夜 status string 滞后**（实际 03:12 成功）；metadata 刷新 bug 延续 |
| Heartbeat delivery route | 🔴 | 8 jobs 无路由 | main/coder/finance/health/life/orchestrator/scout/work 全部 "waiting for delivery route"，占位 telegram:123456789 未替换 - **第 19 夜携带** |
| Telegram botToken secret | 🟡 | inactive surface | secret ref 已配置但挂载在未启用 surface（telegram enabled=false），属预期 |
| Plugin memory-lancedb-pro | 🟡 | enabled / not checked | 第 19 夜 "not checked" |
| Plugin openclaw-weixin | 🟡 | capability consent | doctor: 需 `openclaw plugins enable openclaw-weixin --accept-capabilities` |
| Security audit (CRITICAL) | 🔴 | 3 项 | small_params、open_groups_with_elevated、open_groups_with_runtime_or_fs / control_plane_tools — **本场实跑 audit 确认** |
| Security audit (WARN) | 🟡 | 8 项 | sessions.visibility=all + agentToAgent 无 allowlist、unpinned npm specs、missing integrity、feishu groupPolicy=open 等 |
| News digest cron | 🟢 | 2026-10-20 08:01 | Feishu 上传成功（file_key + message_id 均返回） |
| AMAT cron | 🔴 | token 获取失败 | `[amat-feishu] [feishu_push] 获取 token 失败` — 与 memory 中「AMAT cron 长期停摆」一致，飞书侧未打通 |
| Cron 注册表 | 🟢 | 11 条 | @reboot cron-watchdog 在位；backup 03:00、news 08:00、bilibili 10:00、a_stock 09:00、amat 三班次、mic-button */6h |

> 图例：🟢 正常 · 🟡 降级/告警 · 🔴 失败/需人工处理

---

## 1. GitHub 仓库 CI/CD 状态

| 仓库 | 最近运行 | 结论 | 判定 |
|------|----------|------|------|
| zpzpzp72/openclaw | Node 22 Compat / 2026-09-28 | skipped | 🔴 **stale 22d** |
|  | CodeQL Android Critical Security / 2026-09-22 | cancelled | 🟡 |
|  | CodeQL Critical Quality / 2026-09-22 | success (6m42s) | 🟢 历史绿 |
| zpzpzp72/memory-lancedb-pro | CI / 2026-05-05 | **failure** (3m27s) | 🔴 **~168d 未处理** |
|  | CI / 2026-04-06 | success | — |
| zpzpzp72/openclaw-backup-scripts | [] | — | 🟢 无 CI |
| zpzpzp72/openclaw-zero-token | [] | — | 🟢 无 CI |
| zpzpzp72/amat-stock-report | [] | — | 🟢 无 CI |

**要点**
- **fork 的 Actions 事实上已死**：本仓 OpenClaw 在 10/09-10/19 完成 2026.9.8 到 2026.10.5 大升级，但 Actions **零新 run**。要么 fork 上 Actions 被禁用，要么未 watch upstream。建议白天确认 `.github/workflows` 与 Actions enabled 状态，否则该 fork 的 CI 信号已无参考价值。
- **memory-lancedb-pro 是唯一真·红灯**：CI 挂了 168 天，插件却仍在生产启用（doctor 报 enabled / not checked）。这是本场**最值得白天优先处理**的 DevOps 项 —— 要么修 CI，要么临时降级插件。
- 无 TLS 超时，网络层连续 3 夜健康。

### 本地克隆状态

| 路径 | 分支 | 状态 |
|------|------|------|
| ~/.openclaw/workspace | feature/hot-backup @ a72f94f | 🟡 dirty：8 M / 1 D / 89 untracked |
| ~/.openclaw/openclaw-source | (fork) | 🟢 clean @ 0790d9f593a |

**漂移解读：** 未跟踪 87→89（agents/coder 等目录持续产出），已修改 9→8（MEMORY.md / ERRORS.md 被夜间任务再次覆写）。**属正常夜间 churn，不构成风险**；但 89 个 untracked 已接近需要一次 `git add -A && commit` 收口的临界点，否则长期游离于备份分支之外。

---

## 2. OpenClaw 升级与构建风险

| 项 | 值 | 判定 |
|----|-----|------|
| 二进制版本 | 2026.10.5 (1b58cb9) | 🟢 |
| Gateway 自报 | 2026.10.5 | 🟢 一致 |
| npm latest | 2026.10.5 | 🟢 **已追平，无待装升级** |
| npm beta | 2026.10.10-beta.2 | 🟢 明确不采纳 |
| Update run | ✅ OpenClaw updated to 2026.10.5. | 🟢 上轮升级已收口 |
| Gateway 可达 | ws://127.0.0.1:18789 / 319ms | 🟢 |
| Gateway 进程 | pid **24075**（同 10/19） | 🟢 稳定 >24h |
| Channels | Feishu ON/OK · openclaw-weixin ON/OK | 🟢 |
| Sessions | 1970 stored / 8 stores | 🟢 |
| Tailscale / Telemetry | off / disabled (update checks only) | 🟢 攻击面收敛 |

### 构建风险：Node 版本分歧（本场唯一 P0 技术风险）

```
shell  : node -v  ->  v24.15.0      (PATH 命中 nvm 默认/系统版本)
gateway: 进程内    ->  v26.10.0      (nvm v26.10.0 显式启动)
```

openclaw 2026.10.5 的实际运行环境是 **v26.10.0**（正确），但**任何走 shell 的脚本、cron job、手工命令都会拿到 v24.15.0**。影响面：
- `scripts/openclaw-backup.sh`、news-digest、bilibili、amat 等 cron 全部走 shell
- Node 24 与 25/26 的 ESM/API 行为差异可能在特定脚本上静默降级
- **建议白天二选一**：(1) shell PATH 切到 nvm v26；(2) 确认 openclaw 最低要求已降至 24 并在 AGENTS.md 记录事实

其余构建面无新风险。

---

## 3. 代码库变化与依赖更新

### 3.1 依赖更新（本场无动作）
- npm dist-tags 三日未动（latest 2026.10.5 / beta 2026.10.10-beta.2），**无待处理依赖升级**
- 本夜未安装任何新 npm 包，故**未触发供应链审计流程**（standing rule #4 不适用）
- 遗留审计项（连续第 2 夜）：插件索引含 8 个 **unpinned npm specs**（deepseek / duckduckgo / feishu / kimi / longcat / moonshot / openclaw-weixin / tavily），且 openclaw-weixin **缺 integrity 元数据**。属供应链加固项，非紧急。

### 3.2 代码库变化
- **本场无提交**：workspace 与 origin/feature/hot-backup 零差异，HEAD 仍为 a72f94f（chore: add .gitignore，2026-09-07）。
- 仓库最后实质提交仍是 2026-09-07 的 `.gitignore`，**距今 43 天无代码提交** —— 这是 Coder Agent 信号上的核心事实：**本工作区当前无活跃开发管道**。
- 唯一活跃的「代码」是 agents/coder、agents/finance 等子代理目录与 nightly 报告产出，属运行期数据而非源码。
- 陈旧 PR：#4（194d）、#2（185d）。**#4 与已合入的 STOP_GATEWAY 功能重复，建议关闭**；#2（tar 前 10s wait）仍需判断是否并入。

### 3.3 夜间产物（代码库外的实质变化）
- `heartbeat/` 新增 3 份：nightly-main / nightly-scout / nightly-life-2026-10-20.md
- `memory/` 同步 3 份；`.graphify_*` 增量文件 21:41 刷新，graphify 管线仍在跑
- backup-cron.log 03:12 flush，归档 8.54GB

---

## 4. 本场实跑的新证据（前几夜未覆盖）

1. **首次完整执行 `openclaw security audit`** — 确认 3 CRITICAL + 8 WARN，而非沿用旧记录。
   - CRITICAL: `models.small_params`（小模型需沙箱化并禁用 web 工具）、`security.exposure.open_groups_with_elevated`、`..._runtime_or_fs` / `..._control_plane_tools`
   - 根因是 Feishu `groupPolicy="open"` + `tools.elevated: enabled` + 小模型（MiniMax-M3）三者叠加
   - 修复路径：`channels.feishu.groupPolicy="allowlist"` + `channels.feishu.groupAllowFrom=[...]`；收紧后 critical 可望降到 0
2. **doctor 插件诊断新项**：`openclaw-weixin` 缺 capability consent，需 `openclaw plugins enable openclaw-weixin --accept-capabilities`（一次性）。
3. **browser relay legacy auth 仍开启**（`browser.extensionRelay.allowLegacyAuth=true`），doctor 建议迁移到 v2 后关闭。
4. **AMAT 飞书推送失败已定性为 token 获取失败**，不是邮件通道问题（邮件 attempted 正常）。
5. **备份通知连续 3 次「Connection unexpectedly closed」** —— 归档本身成功，失败的是事后飞书通知，与 backup status 的 "19d ago" 滞后同源。

---

## 5. 行动项（按优先级）

| # | 优先级 | 事项 | 归属 |
|---|--------|------|------|
| 1 | P0 | **Node 版本分裂**：shell v24.15.0 vs gateway v26.10.0，影响全部 cron 脚本 | 白天人工 |
| 2 | P0 | **memory-lancedb-pro CI 红灯 168 天**，插件仍在生产启用：修 CI 或降级插件 | 白天人工 |
| 3 | P1 | **security audit 3 CRITICAL**：Feishu groupPolicy=open + elevated tools + 小模型 | 白天人工（改配置需谨慎） |
| 4 | P1 | **Heartbeat delivery route 19 夜无解**：8 job 占位 telegram:123456789；telegram 已 enabled=false，应改配 Feishu chat_id | 白天人工 |
| 5 | P2 | **备份通知推送持续失败** + openclaw status backup 字段滞后（metadata 刷新 bug） | 白天人工 |
| 6 | P2 | **AMAT cron 飞书 token 获取失败**（邮件通道正常） | 白天人工 |
| 7 | P2 | **workspace 89 个 untracked**，建议一次性 commit 收口 | 白天人工 |
| 8 | P2 | **陈旧 PR #4（重复）建议关闭**、#2 评估并入；仓库 43 天无提交，无活跃开发管道 | 白天人工 |
| 9 | P3 | openclaw-weixin capability consent；插件 spec pin 精确版本 + 补 integrity | 白天人工 |
| 10 | P3 | 确认 openclaw fork 的 GitHub Actions 是否 enabled | 白天人工 |

> 本场无任何自动执行变更 —— 全部为只读检查。NightOps Coder 角色定位为观测与上报，不在夜间窗口修改配置。

---

## 6. 与上夜（2026-10-19）的差异摘要

- **Gateway pid 稳定**（24075 未变），10/19 的 restart 风险已释放
- **AMAT cron 仍红**，但根因从「笼统停摆」细化为「飞书 token 获取失败」
- Node 分歧从「可能是降级」变为「已确证双版本并存」
- drift 微变：9M/87?? 到 8M/89??（正常 churn）
- security audit 首次实跑，CRITICAL 项首次量化
- 无新的升级动作需求（latest 已追平）

---

*NightOps-Coder · 2026-10-20 22:20 CST · 数据全部来自本场实跑命令输出（git / gh api / openclaw status / openclaw doctor / openclaw security audit / crontab -l / 文件系统检查）*
