# Coder 夜检报告 — 2026-11-03（01:20 CST 窗口，NightOps）

Agent: main (Coder) | Host: AMD-AI9-X1-HX370 (WSL2) | Repo: /home/zhiping/.openclaw/workspace

NightOps 窗口检查：周二凌晨 01:20，处于计划夜检窗口内，按计划执行 ✅

## 一、服务状态总表

| 项目 | 状态 | 说明 |
|---|---|---|
| Gateway 进程（PID 648941） | ✅ | 存活，端口 18789 正常响应（Control UI build 2026.10.5-release-1b58cb9） |
| Gateway RSS | ⚠️ | 实时 10.57GB；趋势文件最新采样 10.60GB（≈01:15 CST），较 10-30 采样 4.58GB 持续爬升，与 V8 堆上限 + arena 碎片棘轮的根因诊断一致，未突变 |
| 根分区 / | ✅ | 17% 已用（154G/1007G，余 803G），健康 |
| /mnt/d (D:) | ✅ | 28% 已用（134G/477G，余 344G），健康 |
| /mnt/c (C:) | ⚠️ | 94% 已用（余 32G），Windows 侧持续高位；10-31 已回收 34GB 后仍高，建议继续留意 |
| /mnt/h (NAS dxp4800plus) | ❌ | 100% 满（7.2T/7.2T，仅剩 21G）。cleanup_old 的「NAS 上 rm ≠ 释放空间」静默失效问题仍未解决，备份链随时可能推失败 |
| /mnt/m | ✅ | 挂载点确认不存在（c/d/h/wsl/wslg/z），与状态文件一致，此前陈旧项已收口 |
| GitHub CI | ✅(空转) | 仅 fork openclaw 有工作流，末次运行 09-28（Node 22 Compat skipped；CodeQL 系列止于 09-22 success/cancelled/openclaw Performance cancelled），无新触发 |
| 备份推送链 | ✅ | openclaw-backup-scripts 11-02 16:56 CST 成功推送（db83e0c5 之后继续前进）；openclaw-backup 私有仓 11-01 19:30 CST（NAS 100% 满的状态下，最后一次推送仍然成功） |
| heartbeat-state.json | ⚠️ | 记录停在 2026-10-28T03:12 CST（nightops/nightly_main/gateway_restart 均 10-28），gateway_pid_seen 仍为旧 PID 497240（当前实际 648941），NAS 记录 98%（实际 100%）；属 orchestrator 流程的状态文件，未越权代写，已在下方遗留项标记 |

## 二、GitHub CI / 仓库

- zpzpzp72 名下本轮有推送的仓库仅 openclaw-backup-scripts（11-02 16:56 UTC）与 openclaw-backup（11-01 19:30 UTC，私有）。其余长期静默。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- openclaw-backup-scripts 的 actions runs 总数为 0、workflows 为 0（带 token 的 gh run list 与匿名 API 双路确认）；openclaw-backup 同样为 0/0。<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- fork openclaw 的 Node 22 Compat 最新一次为 skipped（09-28），CodeQL / CodeQL Critical Quality success、CodeQL Android Critical Security 与 OpenClaw Performance cancelled（均止于 09-22）：陈旧无告警。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 工作区 git 日志 10-30 00:41 以来新增 40 提交，其中 11-02 23:22 的 v32 讨论纪要包含两条与备份链直接相关的教训：「趋势误判」与「预检被覆盖」。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## 三、OpenClaw 升级与构建风险

- 本地安装版本 2026.10.5（Control UI build 2026.10.5-release-1b58cb9）；npm latest **2026.10.9**（约 10-29 03:22 UTC 发布，发布 4 天余，已过 0-day 风险期）；extended-stable 已前进至 **2026.9.36**（10-29 19:40 UTC），beta=2026.10.10-beta.5。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 评估意见：升级风险 ⚠️ 中低。patch 级差距、上游无新 CI 触发可供佐证。注意 10-30 的根因修正（V8 堆 96% 上限 + glibc arena 碎片棘轮，见 `6b056c2e`）与已预置的 `MALLOC_ARENA_MAX=2`（待重启生效）：升级重启后应复测 RSS 曲线，验证该环境变量是否生效并确认 10.9 是否带官方碎片治理。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 本地核心仓库均无 CI 工作流，无构建失败面（备份仓已两次空跑确认 runs=0 / workflows=0）。<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## 四、依赖与安全

- 当晚至今无新 npm 安装 → 未触发安装后安全审计条件（规约保持待命）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 遗留项：vendored `openclaw-zero-token/package.json` 仍停留在 2026.3.28（约 7 个月陈旧，与 2026.10.5 差距继续扩大）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## 五、代码库变化（10-30 00:41 → 现在，共 40 提交）

- 备份链修复：d469c05a「恢复丢失的 NAS 空间预检 + 修正 cleanup_old 的谎报完成」、c3182f7d 公网 IP 脚本记录成功时刻 + cron 幂等护栏——正是 v32 教训落地。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 故障分析（10-30 上午）：SQLite checkpoint expired 因果链（30 分钟预算检查 → 握手 → 主线程繁忙）、IMA 自我复制填满 /mnt/c 事故、provider 占位符根因。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 磁盘危机（11-01~11-02）：/mnt/c 100% 根因（File History 保留策略禁用）、回收 34GB、D 盘 21G=VSS 影子待授权、NAS 21G/100% 危机与回收站 123GB（c7ce900c）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 流程教训：watchdog 逐小时算术误报（ERR-20261103-004）、read 截断导致 3594 行覆盖事故（9f5c07b7）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- 研究产出：11-02 graphify 报告更新 + 夜间语料批量入库（e6afc103 等）、11-03 00:56 最新一批（db83e0c5）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## 六、遗留事项（供 owner/orchestrator 处理）

1. NAS 100% 满（剩 21G）：cleanup_old 修复（d469c05a）后需观察是否恢复释放，回收站 123GB（c7ce900c）待清。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
2. heartbeat-state.json 停在 10-28（gateway_pid_seen=497240、mnt_h=98%）：orchestrator 收口时一并刷新。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
3. 升级窗口：2026.10.9 ready（extended-stable 亦已前移到 2026.9.36），等 owner 授权 + 维护窗口；升级重启后复测 RSS 与 MALLOC_ARENA_MAX。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
4. openclaw-zero-token/ vendored 依赖清理（持续）。 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

— Coder Agent · 2026-11-03 01:20
