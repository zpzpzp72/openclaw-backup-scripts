# Tomorrow Action Plan — 2026-11-29（生成于 2026-11-28 05:36 CST）

> 来源：Scout NightOps 11-28 00:55 / Life NightOps 11-28 00:59 / Coder NightOps 11-28 01:16 / Orchestrator 现场实测（state.sqlite + journalctl + 定时器）
> 上一版：Tomorrow_Action_Plan_2026-11-27.md（连续第 2 晚恢复产出）

## P0（阻塞级，需 Owner/Main 动作）

| # | 事项 | 本场实测证据 | 动作 |
|---|---|---|---|
| P0-1 | **work agent 仍是唯一 P0，且在恶化** | `heartbeat-work` consecutiveErrors **73 → 125**（四窗 24→72→96→120→125）；24h reclaim **1737 条全部归因 work**；`agent_database_leases` 中 **work 仍 0 行**（其余 7 agent 各 6–7 行，共 46 行）；work 库 mtime 仍停 **11-23 04:42**（5 天）；work **无 HEARTBEAT.md / DIRECTIVE.md**（同 11-16 health 模具） | **先补配置或停用，再修库**：① 补 work 的 HEARTBEAT.md + DIRECTIVE.md **或**停用 `heartbeat-work`；② 停 Gateway → `doctor --fix --session-sqlite-agent work` → 重启（顺带回收 46 条泄漏租约）。单修库只解一半 |
| P0-2 | **孤儿投递 `4c89a409…`** retry **416 → 727**、pending、`unknown_after_send` | delivery_queue_entries + journal | `openclaw doctor --state-sqlite compact`（CLI ≥300s，禁 timeout 强杀）。**禁止手工改表** |
| P0-3 | **OpenRouter 余额 0**（第 13–14 窗） | curl 实测 `total_credits:0`（key 在 finance agent sqlite → auth_profile_store） | 充值或明确停用依赖链 |
| P0-4 | **QQ SMTP 授权码失效** → 备份告警邮件链断（连续第 6 场） | 实测 `Connection unexpectedly closed`；`~/.secrets/qq_smtp_password` mtime 2026-05-25 | 重生成授权码 + 备份脚本补「失败即告警」分支（别只靠邮件通道） |
| P0-5 | **M365 13 个 commit 未 push** | HEAD `299ed48`，ahead **13** / behind 0；ruff 全绿、回归 **12/12 PASS** | `git push origin HEAD`（前置条件已齐备第 9 轮） |

## P1（重要，非阻塞但需推进）

- **P1-1 Gateway 内存逼近硬顶**：RSS **5685 MB（5.55 GiB）**，进程参数 `--max-old-space-size=4096`（硬顶 4096MB）→ **RSS 已超 heap 上限**；Scout 实测增速 +3493 KB/h。**与 P0-1 停机窗口合并做**：heap → 8192 后重启。
- **P1-2 存储**：NAS `/mnt/h` **245G / 97%**（3 天持续下降）；`/mnt/c` **40G / 92%**（较 11-26 的 23G/96% **已回升**，唯一改善项）；`/` 778G / 19%。NAS `#recycle` 本场实测为空 → 若再降需重新定位大文件。
- **P1-3 M365 并发写缺陷（新增 U-35）**：`history.save()` 固定用 `history.json.tmp` → 6 线程 × 30 轮 **5 次 FileNotFoundError**，丢大部分轮次；U-36 全量落盘写放大 **~30×**（60 消息 = 1.17MB 写 / 38KB 文件）。修 U-35 约 3 行（tmp 加 pid 后缀），**在任何多 worker 部署前必须做**。
- **P1-4 校验器本身会静默失败（新主线）**：Scout 本窗 GHSA **8 条新**（终结连续 5 窗零新增）；AI code reviewer 在 low/med/high 各档**均接受 ≥45% 错补丁**；agent 安全修复成功率 85.7% 但**新会话重新引入同类漏洞 26.7%**。→ 任何依赖「验证器/审阅者」的流程必须先测**验证器自身的失败率**。
- **P1-5 采集上限不可观测（方法论修正）**：arXiv API `max_results` 截断导致历史各窗新增数**系统性偏低**；Scout 已改三路并集（本窗真新增 **105** 篇）。→ 任何「零新增」结论必须标注来源路径 + 第二路径交叉校验。
- **P1-6 NightOps 双路互斥仍未决**：`NightOps-Orchestrator`(10972380) 仍 `enabled=0`，本路已连续 2 晚恢复 → 建议**正式废弃 legacy 路**，保留 per-agent 路。
- **P1-7 4 个 agent 无配置**：main / finance / health / work 均缺 HEARTBEAT.md + DIRECTIVE.md（heartbeat 全部 skipped 或 error）。finance 断更 7.5 月、health 0 篇 daily、work 缺配置 = P0-1 成因。
- **P1-8 全局 MEMORY.md 45 KB**（上限 20,000 字符）→ 尾部永不注入；Scout `HEARTBEAT.md` 已 **56 KB** → 同类膨胀需清理。
- **P1-9 Life 选题侧**：知乎 AI 议题 **0/30 连续 7 场**（议程被 A股/宏观接管，非故障）；X trends 连续 3 场双口径 0（343 样本）→ 建议正式转按需源并同步改 DIRECTIVE。

## P2（观察项）

- Coder 代码侧全绿（12/12 门禁 + ruff 绿），唯一硬阻塞是 push 授权（U-1）；playwright 二进制仍未装（U-10）→ 无真实 E2E；venv 仍在 `/tmp/nightops_venv`（U-18，重启即丢）。
- 内容管线连续 2 天正常（B站日报 + news_digest 已推送），11-26 零内容源日已闭环。
- 备份双链连续全绿：NAS `openclaw-20261128-0300.tgz` 6.29 GB；native 11-28 03:40 完成（剩余 778G）。但 tar 退出码 1 连续第 5 场仍被 `BACKUP_STATUS<=1` 判成功 → 建议 `.sync-staging/` 加 exclude（需授权）。
- memory-weekly-audit（work agent，enabled=1）产出 W48 评分 **B+**（W47 B-），Memory Core 向量索引已修复（3540/3540）。
- 新增观察：Coder 仓库 `agents/coder/copilot_proxy/` 是陈旧分叉副本，会误导扫描（U-27）。

## 本场方法论

1. **租约计数是比 err 数更早的指标**：`agent_database_leases` 按 agent 分组，缺行的 agent 就是下一个受害者。
2. **"零"必须区分「真空」与「没采到」**（arXiv 截断教训）；本场新增「校验器失败率必须自测」。
3. **RSS > heap 上限** = 已在堆外/溢出区，比看 RSS 总量更早预警。

<!-- project: path:/home/zhiping/.openclaw/workspace/agents/orchestrator -->
