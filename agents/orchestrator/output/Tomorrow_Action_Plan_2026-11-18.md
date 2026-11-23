# Tomorrow Action Plan — 2026-11-18 (生成于 2026-11-17 02:40 CST)

> 来源：Scout NightOps 11-17 / Life NightOps 11-17 / Coder NightOps 11-17 / Work 记忆审计 W47 / Orchestrator 自测
> 上一版：Tomorrow_Action_Plan_2026-11-17.md

## P0（阻塞级，需 Owner/Main 动作）
| # | 事项 | 证据（本场实测） | 动作 |
|---|---|---|---|
| P0-1 | **health agent 未配置 + 库冻结** → `heartbeat-health` errs **58**（昨 34），每 60s 一条 `session reclamation commit checkpoint expired`；24h 共 **1440 条，100% 归因 health**（其余库全 0） | health 目录无 HEARTBEAT.md/DIRECTIVE.md；库 mtime 仍停 11-16 04:13（5 个 agent 库停在 04:1x–04:30） | 二选一：①**停用 heartbeat-health**（无配置的 agent 每分钟报错无收益，推荐）；②补齐 health 的 HEARTBEAT.md + DIRECTIVE.md，再 stop gateway → `doctor --fix --session-sqlite-agent health` → start |
| P0-2 | **QQ SMTP 授权码仍失效**（实测 `SMTPServerDisconnected: Connection unexpectedly closed`，TCP 可连、登录被拒）→ 备份告警链断 **12 天** | 本场直测 | 重生成 QQ 授权码 → 更新 `~/.secrets/qq_smtp_password`；备份脚本补「失败即告警」分支 |
| P0-3 | **OpenRouter 余额 0**（连续第 8 窗） | 本场 curl 复测 `total_credits:0` | 充值或明确停用依赖链（key: `agents/finance/agent/auth-profiles.json → profiles/openrouter:default/key`） |
| P0-4 | **M365 repo 7 个修复 commit 未 push**（HEAD `d9f53b0`，ahead **7** / behind 0；远端已停滞 ~8 个月） | Coder 11-17 报告 + git 实测 | `git push origin HEAD`（含 4 个 P1 修复：空流式/假登录/丢轮次/脏 prompt） |

## P1（重要，非阻塞但需推进）
- **P1-1 Gateway 内存顶格**：RSS **4434MB** vs heap 上限 4096MB（进程已超上限），CPU 回落至 61.6%（昨 96.3%）→ 择机 `--max-old-space-size` 4096→8192 后重启，**与 P0-1 停机窗口合并做**。
- **P1-2 投递路由缺失**：`heartbeat-orchestrator` 持续 `skipped: no-route`；`commands.ownerAllowFrom` 在 openclaw.json 中查无此键 → 心跳结论无处投递。
- **P1-3 /mnt/c 可用 21G / 96%**（昨 30G、37G，**持续恶化**）→ Windows 侧增长，需排查。
- **P1-4 备份链**：NAS 归档 `openclaw-20261116-0300.tgz`（6.1G）已产出，本地原生备份 11-16 03:40 verify OK（6.2GB，剩 5 份）→ 今晚 03:00 / 03:40 是下一验证点。
- **P1-5 Scout 采集修复生效**：Google AI blog RSS 十窗空壳缺陷已修（302 未跟 `-L`），本场恢复 20 items → 验证不再复发；arXiv 破零 +114。
- **P1-6 Coder 侧新增开放项**：playwright 浏览器二进制未装 → 无真实 E2E（"登录秒解"最终确认依赖真浏览器）；venv 在 `/tmp/nightops_venv` 不持久 → 建议仓库内 `.nightops-venv/`。
- **P1-7 memory 索引后端**：5 个 agent（main/orchestrator/scout/life/finance）索引全挂 → `memory.search.provider` 未配置（默认 openai，插件 disabled），真后端是 LanceDB + bge-m3@172.18.160.1:11434。改配置需 Owner 授权。
- **P1-8 cron registry 三方不一致**（automations list=1 / CLI=18 / Scout=30，第 **10** 场）→ 统一读数口径。

## P2（观察 / 可延后）
- **P2-1** 备份脚本 L275 `local` 越界报错已修（Work 11-16），仅余日志噪声。
- **P2-2** Life 侧新框架：留存决定项 = 「能不能被再拿出来用一次」；五档极差收窄至 9.7 倍。
- **P2-3** 中英方向反转（知乎 AI 0%→10%，HN 3/30→1/30）→ 选题向中文侧倾斜，下一场复核是否 ≥10%。
- **P2-4** 微信 24h 热文榜停用（连续 4 场逐行一致）；抖音模板残留待换源。
- **P2-5** 全局 MEMORY.md 42.6KB 超 `bootstrapMaxChars` 20,000，末段永不注入 → 待 Owner 拍板瘦身。

## 已闭环（无需动作）
- ✅ NAS 回收站 185GB 已释放，`/mnt/h` **390G avail**（15 份归档 / 99G，95%）。
- ✅ SQLite reclaim 错误收敛为**单一来源**：24h 1440 条 100% 归因 health，其余 agent 全部 0。
- ✅ main 库写入正常（mtime 11-16 23:37）；heartbeat:main/coder/scout/life/finance/work errs 全 0。
- ✅ 4 路 per-agent NightOps 全部 ok；legacy `NightOps-*` 4 路保持 disabled（正确）。
- ✅ MiniMax 直连正常；Coder 门禁 6/6 真跑 PASS，ruff 全绿。
- ✅ 本地原生备份与 NAS 归档 11-16 双双成功（互为备份）。

## 方法学提醒
- 判「孤儿 receipt」须 age > 15min；「我观察到的唯一手段」≠「唯一可能手段」（Coder 已推翻"必须重启"）。
- 看到某 agent 心跳持续报错，**先查它是否被配置过**，再决定修还是停用。
- 镜像源连续两次内容完全一致 = 陈旧告警，不是趋势（Life 11-16 证伪过上场结论）。
- 采集源先修再下结论（Scout 本场修 Google RSS，撤回"下线该源"旧建议）。

## 明日验证点（11-18 02:40 逐条核对）
1. health：errs 是否归零 / 库 mtime 是否脱离 11-16 04:13（停用或修好二选一）
2. NAS 归档 `openclaw-20261117-0300.tgz` + 本地备份 11-17 03:40 是否成功
3. OpenRouter / SMTP / M365 push 是否由 Owner 处理
4. Gateway RSS 是否回落（4434MB 峰值）与 heap 是否已提到 8192
5. `commands.ownerAllowFrom` 是否生效（heartbeat-orchestrator 不再 no-route）
6. /mnt/c 可用是否止跌（21G）
