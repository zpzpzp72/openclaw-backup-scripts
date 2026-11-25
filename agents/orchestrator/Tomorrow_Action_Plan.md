# Tomorrow Action Plan — 2026-11-27（生成于 2026-11-26 01:36 CST）

> 来源：Scout NightOps 11-26 / Life NightOps 11-26 / Coder NightOps + infra_health 11-26 / Work 记忆审计 W48（11-23）/ Orchestrator 自测
> 上一版：Tomorrow_Action_Plan_2026-11-18.md（中断 8 天，本版恢复）

## P0（阻塞级，需 Owner/Main 动作）

| # | 事项 | 证据（本场实测） | 动作 |
|---|---|---|---|
| P0-1 | **故障主体轮到 `work`**：`heartbeat-work` err **73**；24h reclaim 报错 **1728 条 / 1727 条归因 work**；`agent_database_leases` **work 0 行**（其余 7 agent 各 3–5 行）；库 mtime 停在 11-23 04:42；work **无 HEARTBEAT.md / DIRECTIVE.md** | 与 11-16 health 的 P0 同一模具：未配置 → 从未取得租约 → 回收提交无人授权 → 必然超时 | **先补配置或停用，再修库**：① 补 work 的 HEARTBEAT.md + DIRECTIVE.md；② 停 Gateway → `doctor --fix --session-sqlite-agent work` → 重启（重启后回收 28 条泄漏租约）。单修库只解一半 |
| P0-2 | **孤儿投递 `4c89a409…`**：retry_count **416**、pending、`recovery_state=unknown_after_send`；72h 内 826 次 "delivery owner state unavailable" → **发给 work 的消息完全无法送达**（新增第三种表现面） | delivery_queue_entries + journal | `openclaw doctor --state-sqlite compact`（CLI ≥300s，不要 timeout 强杀）。**禁止手工改 `delivery_queue_entries`** |
| P0-3 | **OpenRouter 余额 0**（连续第 11 窗） | curl 实测 `total_credits:0` | 充值或明确停用依赖链。key 已移位：`agents/finance/agent/openclaw-agent.sqlite → auth_profile_store → profiles["openrouter:default"].key`（`auth-profiles.json` 已不存在） |
| P0-4 | **QQ SMTP 授权码失效** → 备份告警邮件链断 | 实测 `SMTPServerDisconnected: Connection unexpectedly closed`；`~/.secrets/qq_smtp_password` mtime **2026-05-25**（半年未更新） | 重生成 QQ 授权码 → 更新 `~/.secrets/qq_smtp_password`；备份脚本补「失败即告警」分支（别只靠邮件通道） |
| P0-5 | **M365 11 个 commit 未 push**（HEAD `700f8a3`，origin/main `d2af52a` 为祖先，ahead 11 / behind 0） | Coder：ruff 全绿、回归 **10/10 PASS**、3/3 连通、push --dry-run rc=0 | `git push origin HEAD`（第 8 轮前置条件齐备，仓库未 Recreate） |

## P1（重要，非阻塞但需推进）

- **P1-1 计划无备份生产者**：`NightOps-Orchestrator`（id `10972380`，agent=main）`enabled=0`，本路 `Orchestrator NightOps` 11-22→11-25 连败 4 次（SQLite → SESSION_PLACEMENT_TURN_SETTLEMENT_CLOSED → OPENCLAW_DIRECT_ABORT），造成 8 天空窗。本场 01:36 已恢复 → 二选一后关掉另一路，避免双生产者。
- **P1-2 存储双向告急**：`/mnt/c` **23G / 96%**（11-23 曾 44G）；`/mnt/h` **263G / 97%**（3 天 -110G，约 -35G/天）；NAS 回收站清理需授权（`bash scripts/nas-recycle-cleanup.sh --execute`，只删 `#recycle` **内部**文件才真释放）。
- **P1-3 Gateway RSS 4.69 GB**（pid 36001，uptime 3.2 天，CPU 27.6%），`openclaw.json` 未见 maxOldSpaceSize → heap 4096MB 硬顶。**与 P0-1 停机窗口合并做**：提到 8192 后重启。
- **P1-4 4 个 agent 未配置**（main / finance / health / work 均缺 HEARTBEAT.md + DIRECTIVE.md）→ 它们的 heartbeat job 只能 skipped 或持续报错。统一「补配置 or 停用」，5 天未决。
- **P1-5 备份脚本语义**：NAS 备份 tar 退出码 1（`File removed before we read it` / `File shrank by 532480 bytes`）被 `BACKUP_STATUS<=1` 判成功 → 吞掉了「归档与源目录瞬时不一致」。Life 已实证归档完好（3 个库 `integrity_check=ok`，session_nodes 1896 / transcript_events 50592）→ **建议把 `.sync-staging/` 加 exclude**，而非收紧为 `==0`（收紧会更频繁误报并删半成品）。需授权。
- **P1-6 投递路由缺失**：`heartbeat-orchestrator` 持续 `skipped: no-route`；`commands.ownerAllowFrom` 在 openclaw.json 中查无此键 → 心跳结论无处投递。
- **P1-7 Coder 真浏览器 E2E 仍缺**：playwright 浏览器二进制未安装；venv 在 `/tmp/nightops_venv` 不持久 → 建议仓库内 `.nightops-venv/`。
- **P1-8 全局 MEMORY.md 43,131 B / 30,313 字符 > bootstrapMaxChars 20,000** → 尾部「审计日志」段（起点 ≈29,842）永不被注入。Work 已给拆分表（系统架构 5,654 / Token Plan 4,668 / D 盘 6,199 / 持续性风险 5,355），目标 ≤10,000 字符。待 Owner 拍板。
- **P1-9 Finance / Health 断档**：finance 最新 daily 2026-04-07（断更 7.5 个月）、health 0 篇 daily → 去留与补档待决。

## P2（观察 / 可延后）

- **P2-1** Scout 趋势：竞争单位从"模型"移到"回路"（5 个 harness pass@1 全落在 42.9~45.2，**harness 无区分度**）；委派给本地小模型可砍 67% 成本且性能无损；企业部署中 **19% 完全无业务价值**，最大障碍是人类复核量 → 剩余两个杠杆位置：**细活委派给谁** + **谁复核输出**。
- **P2-2** 评测链下游化（连续第 4 窗）：judge 只看答案会把 56% 正确轨迹误标，给完整轨迹才到 0.75，**加推理链反而无改善** → 信号不在 CoT。
- **P2-3** 平台隔离假设被证伪：同一推理服务器上的两个 agent 即使不能互发消息/共享文件，仍能可靠通信（批处理/调度即信道）；AEGIS 用 eBPF 行为取证做零信任隔离 → **若 agent 共享推理后端，应默认存在侧信道**。
- **P2-4** GHSA 连续第 4 窗 0 新增；The Decoder 单窗 10/10 全换（最大）；OpenAI RSS 破冻结 +8；HN top30 全换血；arXiv +266；图谱 4,208 节点 / 10,127 边 / 39 社区；LanceDB 622→638 行。
- **P2-5** Life：11-25 场 abort → 本场基线 2 天、B站重叠仅 6/60 → 跨期结论一律标「样本不足」；「AI 档留存最高」连续三场后本场被打破（3.1×→2.0×），改写为「做得扎实的 AI 产出物留存最高」；X 宽口径首次归零（0/347）→ 建议改按需源。
- **P2-6** Scout 方法论修正：The Decoder 正文 URL 必须用 RSS 原文链接（手拼 slug 被静默重定向到同一篇，md5 相同 → 「抓到了」≠「抓对了」），已加 md5 去重断言。
- **P2-7** `openclaw cron list` CLI 路径不可用（`gateway.auth.token` 为 secret 引用）→ 直查 `~/.openclaw/state/openclaw.sqlite → cron_jobs.state_json`（30 jobs / enabled / consecutiveErrors / schedule）。

## ✅ 已闭环（无需动作）

- 备份双链连续 3 轮全绿：NAS `openclaw-20261125-0300.tgz`（6.27G）status=ok；native 11-25 03:40 **verify OK**（5.9G，归档 8→7，剩 779G）。
- 归档可用性已实证完好（tar 退出码 1 不等于损坏，3 个库 integrity_check=ok）。
- health / finance / orchestrator 的 cron 错误 11-23 重启后已归零（heartbeat-health/finance/orchestrator 均 err=0）；唯一在错的是 work。
- 全部 8 个 agent 库 `PRAGMA integrity_check = ok`（main 233MB / scout 84.3MB / coder 60.7MB / life 53.8MB / orchestrator 48.2MB / work 15.3MB / finance 6.4MB / health 5.4MB）→ **无库损坏，故障是网关侧租约/授权机制**。
- MiniMax API 直连 200 / 0.32s，model-fetch 今日 186 次无 429 风暴；代理 25017 TCP 可达、8080 在监听。
- Scout 新闻摘要 11-25 08:00 场成功（21,167 B，飞书 om_ 回执 + 邮件 30 条）；11-24 同样成功 → 印证「作业 error(Nx) ≠ 内容失败」。
- Memory Core 向量索引已修复：bge-m3@172.18.160.1:11434，8/8 agent 向量行数 == chunk 行数（3540/3540）。
- 两个备份 timer 已加 OnBootSec，开机抢 IO 误判已消除。

## 📌 明日（11-27 01:36）逐条验证点
1. `heartbeat-work` errs 是否从 73 归零；`agent_database_leases` 中 work 是否拿到租约行；work 库 mtime 是否脱离 11-23 04:42
2. 孤儿投递 `4c89a409…` 是否从 pending 消失 / retry 是否停止上涨
3. `Orchestrator NightOps` 是否连续第 2 天 ok；两路 NightOps 是否已互斥（只留一路 enabled）
4. 24h reclaim 报错条数与归因（当前 1728 / work 99.94%）；修正后应断崖
5. OpenRouter credits / QQ SMTP / M365 push 三项是否已由 Owner 处理
6. 11-26 03:00 NAS 归档 + 03:40 native verify 是否成功；`/mnt/h` 可用是否止跌于 263G
7. `/mnt/c` 可用是否止跌于 23G；Gateway RSS 是否仍在 4.7GB 附近
8. 本场建议的 `.sync-staging/` exclude 改动是否已落地（若获授权）

## 方法学提醒
- 看到某 agent 心跳持续报错，**先查它是否被配置过**（HEARTBEAT.md / DIRECTIVE.md），再决定修还是停用。
- 错误归因要看**数量级**（1727/1728），不要看「有错误」。
- 「一次修复 = 解决」是错的：integrity gate + 重启只解当前受害者，故障会后移到下一个未配置 agent → **每次重启后逐个 agent 复验**。
- 孤儿投递的 retry 计数与 agent error 计数同步上涨 → 优先判同源，别当两个独立故障。
- 判「归档损坏」前先解包做 `PRAGMA integrity_check`，tar 退出码 ≠ 归档可用性。
- 跨期对比先看基线天数，样本不足就标「样本不足」，不下趋势结论。

<!-- project: path:/home/zhiping/.openclaw/workspace/agents/orchestrator -->
