# MEMORY.md — Long-Term Memory

_Curated insights from sessions past. Updated periodically from daily notes._

---

## 系统架构

- **Gateway** (2026-10-31 18:00 CST 实测): 端口 18789, **app 2026.10.5 (1b58cb9)** linux 6.6.87.2-microsoft-standard-WSL2, systemd user unit pid 648941（10-30 04:16 启动）
  - 实际安装路径: **NVM** `/home/zhiping/.nvm/versions/node/v26.10.0/lib/node_modules/openclaw`（不是 npm-global）
  - ⚠️ **Gateway service 的 ExecStart 用的是 `/usr/local/bin/node`（→ `/usr/local/lib/nodejs/node-v26.10.0`，独立于 nvm），但 openclaw 包体在 nvm 里** —— 两套 node 同为 v26.10.0，升 Node 时两处都要动 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
  - RSS 2.7-3.4 GB（heap 上限 `--max-old-space-size=4096`，从 8192 降下来）
  - 前次 (8/28) 记录的 pid 623 / 1.29 GiB 已过时；升级路径见 `.learnings/LEARNINGS.md` 2026-10-03 条目
- **Agents** (openclaw.json `agents.list`, 8 个): main / orchestrator / scout / coder / life / finance / **health** / **work**
  - 大多数用 `minimax/MiniMax-M2.7`，health 用 `longcat/LongCat-2.0`，work 用 `minimax/MiniMax-M3`
- **备份**: 热备份脚本 `~/.openclaw/workspace/scripts/openclaw-backup.sh`（不是 `~/.openclaw-backup.sh`），输出 `/mnt/h/AI/openclaw.zone/WSL/openclaw-YYYYMMDD-HHMM.tgz`
  - **心跳**: `~/.openclaw-backup.heartbeat` (last_run_epoch/last_backup_epoch/status/detail)
  - **强制 tar 兜底**: 距上次备份 >25h (FORCE_TAR_HOURS) 即使无变化也 tar 一次
  - **最近一次**: 2026-08-28 03:00 → `openclaw-20260828-0300.tgz` (4.3 GB), status=ok
- **独立健康检查** (ERR-20260826-001 修复): `C:\Scripts\OpenClawHealthCheck.ps1`
  - Windows 任务计划程序 `OpenClawWSLHealthCheck` 每 6h 运行一次 (用户 Zhiping Wu, Interactive, Limited)
  - 检测项: WSL 心跳 / 最近备份 / WSL 响应 / NDIS LiveDump (24h)
  - 告警: Feishu webhook (凭据读 `\\wsl$\Ubuntu\home\zhiping\.openclaw\openclaw.json`)
  - 日志: `C:\Scripts\logs\openclaw-healthcheck.log`
  - **已知小 bug**: 第 199–202 行 `wsl.exe stat` 输出经 PowerShell 编码转换产生乱码（"stat 备份文件失败: 鲖Bl剉蚫..."），会误报"⚠️ 无备份文件"——脚本仍判定"所有检查通过"。**修复建议**: 调用前设 `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`，或改用 `wsl.exe -e bash -c "stat --printf='%Y\n'"` 只取 epoch 不取文件名。
- **NightOps 调度**: 2026-10-24 起 9 个 NightOps job 错峰至 **00:30-03:00 CST**（避开 MiniMax Token Plan burst 耗尽窗口 02:00-05:00）
- **cron** (用户 crontab 2026-08-28): 11 行定时任务
  - 备份: `0 3 * * *` (`scripts/openclaw-backup.sh`)
  - Finance A股: `0 9 * * 1-5` (`agents/finance/a_stock_daily.py`)
  - AMAT 报告: `30 21 * * 1-5` + `0 4 * * 2-6` + `30 22 * * 1-5` + `0 5 * * 2-6`（4 次/天）
  - 新闻摘要: `0 8 * * *` (`scripts/run_news_digest.sh`)
  - NightOps / claw-sync / heartbeat: `@reboot` + `30 3 * * *` + `0 * * * *`
- **模型 fallback 链** (`openclaw.json` `agents.entries`, 2026-10-24 05:10 Main 全局收敛) <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
  - **统一链条（2026-10-24 实测，8 agent + defaults 全部相同）**: `minimax/MiniMax-M3.1-Flash` → `minimax/MiniMax-M2.7` → `litellm/GLM-5.3-Flash` → `litellm/deepseek-flash` → `litellm/LongCat-2.0` → `ollama/qwen3:4b-instruct`（末位兜底）
  - `agents.defaults.model`: primary `minimax/MiniMax-M2.7`; `agents.entries.orchestrator`: primary `minimax/MiniMax-M2.7`; **`{scout,coder,life,finance,health,work}`(6 个) primary = `minimax/MiniMax-M3.1-Flash`**; `main`: 继承 defaults
  - `agents.entries.health` 的 primary 已从 `longcat/LongCat-2.0`(401 无 key) 改为 `minimax/MiniMax-M2.7`
  - **provider 实际列表**: minimax / litellm / ollama / longcat / siliconflow / openrouter（6 个）
  - **provider 状态（2026-10-24 22:00 用 sqlite 真实 key 逐个实测）**: 🟢 minimax(CN) 200/1.23s · litellm@NAS **全通**(M2.7 200/1.12s, deepseek-flash 200/0.60s, LongCat-2.0 200/1.32s, GLM-5.3-Flash 200/5.71s) · siliconflow **200/1.96s**（旧记「30014 key 失效」已证伪）· longcat **200/2.11s**（旧记「401 无 key」已证伪）· ollama 200（qwen3:4b-instruct 0.64s / qwen3.6:27b 30s）· 🔴 **openrouter 402 Insufficient credits（余额 0，唯一真死链）**
  - **唯一可用兜底是本地 ollama**（172.18.160.1:11434）: `qwen3:4b-instruct` 实测 3.0s 出正确内容；`qwen3.6:27b` 只吐 reasoning
  - **认证来源在 sqlite auth profiles**（`state/openclaw.sqlite` `config_machine_state` + `~/.openclaw/agents/*/agent/openclaw-agent.sqlite`），不在 env；`openclaw models status --json` 可查 effective
  - **教训**: 多 Agent 并行改同一份全局配置必须有单一裁决者，否则后写的覆盖先写的（Scout 提 litellm → Orchestrator 移除 litellm → 7/8 agent 首位是死链）
  - **⚠️ M3 系列必须 `thinking=adaptive`**（2026-10-24 22:10 修复并热载）: `MiniMax-M3` / `MiniMax-M3.1-Flash` 服务端**强制** `thinking.type=adaptive`，发 `disabled` 直接 400 (2013)「requires adaptive thinking」。全局 `agents.defaults.thinkingDefault="off"` 会触发它 → 必须在 `agents.defaults.models` 给这两个模型单设 `params.thinking="adaptive"`（per-model 优先级高于全局，resolution order #5 > #6，见 docs/tools/thinking.md）。M2.7 / litellm / ollama 不受影响。备份 `openclaw.json.bak.thinkingfix-20261024-221008` <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->


## MiniMax Token Plan 配额机制（2026-10-24 22:00 官方文档 + 受控实测） <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

**⚠️ 核心结论：429 的根因是 Token Plan 5 小时窗口耗尽，不是认证问题。** 认证（API Key）全程有效；配额打满时 MiniMax 返回
`HTTP 429 rate_limit_error` / 「已达到 Token Plan 用量上限 (2056)」，**所有 minimax 模型同时失败**（M2.7 与 M3.1-Flash 报错逐字相同）。
OpenClaw 侧表现为 `models list` 里该模型 `Auth=no` + `authProfiles.state` 里 `cooldownReason=rate_limit` / `failureCounts.rate_limit` 递增——这是**冷却标记，不是缺 key**。

**判定口诀**：minimax 报 429 且 `openclaw models list` 显示 `Auth=no` → 先查 Token Plan 窗口（`mmx quota`），**不要去查 key**。
实测反例：同一天上午 `Auth=no` + 12 次 rate_limit 失败，20:00 窗口重置后 21:55 复测 `Auth=yes`、三模型全 200（0.87–0.94s），**冷却已于 13:26 到期，无需人工干预**。

**配额是单一池，不按模型分桶。** 官方 FAQ 原文：
> Model usage covered by Token Plan shares **one included Token Plan quota** … usage deducts from the included Token Plan quota **according to the corresponding endpoint pricing**.

即：用量条上的「M token」是**按端点价归一化的额度单位**，不是真实 token 数。同一份配额喂不同模型，能换到的真实 token 量差好几倍。

**两个滚动窗口**（2026-10-24 官方 usage-rules）：5 小时滚动（文本/图像/音频等非视频模型）+ 7 天周窗口（所有模型，含视频）。两窗口独立重置，5 小时重置**不**重置周用量；未用完不结转。

### Plus 档 5 小时窗口的真实容量（受控实测反推）

官方只公布百分比、不公布 token 绝对值。2026-10-24 22:00 用「已知 input token 数 → 观察窗口余量百分比变化」反推（CN 标准价）：

| 模型 | 输入 元/百万 | 输出 元/百万 | 缓存读取 元/百万 | 5h 窗口满额可跑 input |
|---|---:|---:|---:|---:|
| **MiniMax-M3.1-Flash** | 1.00 | 4.00 | 0.10 | **≈ 6.1 M tokens** |
| MiniMax-M3 (≤512k 输入) | 2.10 | 8.40 | 0.42 | ≈ 2.9 M tokens |
| MiniMax-M3 (>512k 输入) | 4.20 | 16.80 | 0.84 | ≈ 1.5 M tokens |
| MiniMax-M2.7 | 现行定价页已不单列（旧模型） | | | — |

- 实测斜率：676,006 input tokens → 窗口余量 59%→48%（11%）→ **每 1% ≈ 61,455 input tokens**
- 换算：6.1M ÷ 2.1 = 2.9M（对 M3 ≤512k）；6.1M ÷ 4.2 = 1.5M（对 M3 >512k）
- ⚠️ 该数为**单请求 input 口径**，输出与 thinking token 按 4x 价另行扣减；M3.1-Flash thinking 恒开且不可关（官方 OpenClaw 指南），实际可用量低于表值
- 优先服务（`service_tier=priority`）= 标准价 ×1.5，同样窗口内可跑量再降 1/3

**省钱排序**（对 Plus 档）：① 缓存命中只要 input 价的 1/10（0.10 vs 1.00）→ 长会话固定前缀务必命中；② 上下文控制在 512k 以内（超了 M3 直接变 4.2 元/M）；③ M3.1-Flash 比 M3 便宜 2.1–4.2 倍；④ 简单任务降 thinking 深度（M3 可调，M3.1-Flash 不可）。

### 查用量/余量的三个手段

1. `mmx quota`（最省事，CN key 会自动识别区域）
2. `curl https://api.minimaxi.com/v1/token_plan/remains -H "Authorization: Bearer <key>"` — **CN key 必须打 `api.minimaxi.com`**，打 `www.minimax.io` 会返 `2049 invalid api key`
3. 控制台 <https://platform.minimax.io/console/usage>

返回字段：`current_interval_remaining_percent`（5h 窗口）、`current_weekly_remaining_percent`（周）、`remains_time`（窗口剩余毫秒）。**`current_interval_total_count` / `usage_count` 恒为 0**，只能看百分比。

### 2026-10-24 22:00 实测窗口状态

| 窗口 | 区间 | 剩余 | 百分比 |
|---|---|---|---|
| 5 小时（general） | 10-24 20:00 → 10-25 00:00 | ~2h | 用到 48%（被我为测量消耗） |
| 周（general） | 10-19 00:00 → 10-26 00:00 | ~26h | 🟢 100% |
| 周（video） | 同上 | ~26h | 🟢 100% |

### 排期含义

- MEMORY 原有「NightOps 错峰至 00:30-03:00 避开 MiniMax burst 耗尽窗口 02:00-05:00」**成立且有据**：5h 窗口从首次使用起算，若 20:00 起重度用，**00:00 窗口重置**；02:00-05:00 段是窗口刚重置后的高可用期，但也可能撞上 00:00-05:00 之间的下一次重置点。**实操建议：把重活放在窗口刚重置之后**（用 `mmx quota` 确认余量 > 50% 再开工）。
- 官方 15:00-17:30 工作日高峰有**动态限流**（Plus 约支持 3-4 个 agent 并发），与配额耗尽是两回事，别混判。

**附：本地 cost 字段与官方 CN 价不一致**（`openclaw.json` `models.providers.minimax.models[].cost`，只影响 OpenClaw 自身成本统计，不影响服务端真实扣费）：
M3.1-Flash 1/4/0.1 ✅ 与 CN 价一致；M3 记 0.5/2 ❌ 官方 2.1/8.4（≤512k）；M2.7 记 0.3/1.2 ❌ 旧 Global 价。

## 关键方法论教训(2026-10-30)

- **诊断大型进程内存,不要只看 `/proc/<pid>/smaps` 的 `[heap]`**:那只是 glibc 主 arena 的 brk 区,**不是 V8 堆**。V8 堆页是 256KB 的独立 mmap,必须用 `kill -USR1 <pid>` + CDP `Runtime.getHeapUsage` 直读主 isolate。
- **「尺寸恰好等于某个源码常量」可能是巧合**:本轮 `TRAJECTORY_RUNTIME_EVENT_MAX_BYTES = 262144` 与 V8 `kPageSize = 256KB` 完全相等,导致我据此推出「trajectory 事件缓冲」的错误结论。**教训:用常量相等做锚点前,必须先排除「该数值是运行时通用常量」的可能,并做隔离复现实验**。
- **派子代理做独立验证是值得的**:本轮子代理用 inspector 直读推翻了我的结论并补全了 arena 归因,两者交叉验证后才得到可靠结论。
- **「每 X 留一份内存副本」这类假设要先做趋势检验**:会话数零增长而映射 +25% 即可否定。

## 持续性风险

| 优先级 | 问题 | 首次发现 | 状态 |
|:------:|------|:--------:|------|
| P0 | **WSL 网络架构: 禁用 Mirrored 模式** — Mirrored + WinDivert (APNetwork) + Windows Update 三方冲突 → NDIS 崩溃 → OpenClaw 失联 | 2026-08-26 | ✅ 已切回 NAT+dnsTunneling+autoProxy，永久禁用 Mirrored |
| P0 | **备份连续性监控缺失** — NightOps 也在 WSL 里跑，WSL 死了连备份检查都没人做；需外部健康检查 | 2026-08-26 | ✅ 已修复 (2026-08-26 11:25): 备份心跳文件 + Windows 任务计划程序独立检查 + 飞书 webhook |
| P1 | ~~**GitHub token 无效**~~ — 2026-10-30 实测 `git ls-remote` / `git push` **凭据可用**，推送成功；`gh auth status` 未复测 | 2026-08-13 | 🟢 git push 可用；`gh` CLI 仍待验 |
| P1 | openclaw-zero-token 项目基本停滞（最近 commit 2026-08-08 docs, 实质改动 7/30 之前）；是 **shell+python** 项目，**没有 package.json / package-lock.json**（MEMORY 之前关于 npm audit 的说法不成立） | 2026-07-31 | 🟡 未推进 |
| P1 | browser.py:41 bare except | ~2026-04 | 🔴 未修复 |
| P1 | memory-lancedb-pro 落后 upstream **104 commits**（已重新核对, 2026-08-28） | 2026-07-31 | 🔴 未注册, 持续积累 |
| ~~P1~~ | ~~WeChat DNS `EAI_AGAIN` 持久化问题~~ | 2026-08-13 (cron 报告) | ✅ 2026-10-24 复测不复现：5 个微信域名 DNS 解析正常、TCP 全通、HTTPS 0.17–0.38s | <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
| P0 | **PROXY DOWN 127.0.0.1:25017** — `curl http://127.0.0.1:25017/` Failed to connect, 无 proxyon 进程，2026-08-27 发现；导致 `git fetch origin` 失败（memory-lancedb-pro 同步受阻）。**注意：`172.18.160.1:25017` 是通的**（根路径 404 属正常，实测能代理 wx.qq.com 200/0.28s），微信通道用的是后者，不受影响 | 2026-08-27 | 🔴 Main 未处理（仅影响 git fetch） | <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
| P2 | Coder 最近 code_report 停留在 **2026-07-30**（29 天没更新）；orchestrator 标"08-27 cron 恢复"但实际产物未刷新 | 2026-08-28 | 🟡 待核查 |
| P1 | **Gateway RSS 13.7GB 根因已定位(2026-10-30)** — 活体 inspector 实测:**V8 堆 heapUsed 3.90GB / heapTotal 4.06GB (达 --max-old-space-size=4096 上限的 96%)** + **约 9GB 是 glibc 每线程 arena 碎片棘轮**(209 个 64MB arena,rw 已提交 8.8GB)。那 17400+ 个「恰好 256KB」匿名段 = **V8 堆页**(256KB=kPageSize,隔离复现已证实)。**「每会话一份内存副本」已被否定**:10/26→10/30 会话数零增长而映射 +25%,比例吻合系巧合。驱动源 = 线程 churn(87 个 `tokio-runtime-w` 来自 LanceDB 插件的 Rust 线程池)。重启后 A/B 验证:arena 数 209→202(几乎不变)但 arena 内 rw 8824→1943MB(↓78%)→ 证实是**碎片未归还**而非 arena 耗尽。**最佳一刀**: `MALLOC_ARENA_MAX=2` 写进 `~/.openclaw/gateway.systemd.env`。**附带病灶**:memory-lancedb-pro 的 `memories.lance/_versions` **6.9GB vs data 164MB**(磁盘侧同病根)。终版报告 `memory/2026-10-30-gateway-rss.md` | 2026-10-30 | 🟢 根因已定位;**修复需 ZP 授权**(重启只清零不治本;env 加 MALLOC_ARENA_MAX 需改配置 + 重启) || P0 | **MiniMax M3 系列 thinking 载荷不兼容** — `MiniMax-M3` / `MiniMax-M3.1-Flash` 服务端强制 `thinking.type=adaptive`；全局 `agents.defaults.thinkingDefault="off"` 让 OpenClaw 原样发 `disabled` → 400 (2013)，表现为「飞书通道报错」实为模型层。放大器：会话级 `modelOverride` 会禁用配置里的 fallback 链（`configured fallbacks disabled by user model override`）→ 无兜底 | 2026-10-24 21:54 | ✅ 已修复 (22:10): per-model `params.thinking=adaptive` + 网关热载（revision 8），修复后 `requires adaptive` 计数=0 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts --> |
| P1 | **OpenClaw 升级被 Node 版本卡住（2026-10-31 实测）** — npm latest=2026.10.9（beta 10.10-beta.5 / extended-stable 2026.9.36）；10.6 起连续三个版本（10.6 / 10.8 / 10.9）都是安全发布，10.6+ `engines: node >=24.22.1 <25 \|\| >=26.12.1`（eMudhra 证书泄露补救）。本机 Node v26.10.0 **不满足** → 必须先升 Node（可用 v26.12.1 / v26.13.0）。10.7 新增 updater 守卫：Node 版本不匹配时**主动停止并保留当前 Gateway 运行**，不会半途搞坏 | 2026-10-31 | 🟡 待 owner 决策（先升 Node，再 `/update`）| <!-- project: github.com/zpzpzp72/openclaw-backup-scripts --> |
| P1 | **MiniMax 429 根因 = Token Plan 5h 窗口耗尽**（非认证问题）— 配额单池按端点价扣减；M3.1-Flash 5h 满额 ≈6.1M input tokens / M3(≤512k) ≈2.9M / M3(>512k) ≈1.5M；耗尽时所有 minimax 模型同时返 429(2056)「已达到 Token Plan 用量上限」，OpenClaw 侧表现为 `Auth=no` + rate_limit 冷却（**是冷却不是缺 key**）；5h 窗口重置后自动恢复，无需改 key。查余量用 `mmx quota` 或 `api.minimaxi.com/v1/token_plan/remains`（CN key 别打 www.minimax.io） | 2026-10-24 | 🟡 配额管理问题，非故障；已被 8 个 agent 的 M3.1-Flash primary 放大（6/8 agent） | <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
| P2 | **APNetwork + WinDivert 稳定性** — 已确认 NDIS dump 仅观察到 1 次（2026-08-18 14:26），"每月数十次崩溃"无证据；WinDivert64.sys 时间戳 2022-09-20（很久没更新）；主要风险是三方共存而非高频崩溃 | 2026-08-26 | 🟢 切 NAT 后未复发，保留"未来 NDIS 更新时可能再触发"的观察 |
| P0 | **public 仓库入库前无凭据扫描闸门** — `zpzpzp72/openclaw-backup-scripts` 是 **public**；`c9353413` 把 `.backups/`（含 `appSecret`/API key 明文 + 434MB sqlite）误收进去，靠 filter-branch 改写历史才清除 | 2026-10-30 | 🟡 已清除 + 加 .gitignore；**仍需 pre-push 扫描 skill**（NightOps v28 议题4 列为最高优先级） |
| P1 | **备份 tar 未排除 `workspace/.git`(200M) 与 `workspace/.backups`(434M)** → 每晚白背 634MB | 2026-10-30 | ✅ 已加 exclude（文件保留本地，仅不进归档） |
| (已合并) | ~~Coder Codex/Arcee/Kimi 三模型全败~~ — 2026-08-08 报告已过期 20 天，未重测；如需查证需单独跑 Coder probe | 2026-08-08 | ⏸️ 暂搁置 |

## Git 状态 (2026-10-30 收口后)

| 分支 | 状态 |
|------|------|
| `feature/hot-backup` | ✅ **已与 origin 完全同步**（`cff8db5d`, 2026-10-30 00:30）。远程 `https://github.com/zpzpzp72/openclaw-backup-scripts.git`,分支 `feature/hot-backup` |
| `feature/backup-script` | 仍停在 1e3cc687(2026-03-27)，未动 |

**⚠️ 该仓库是 PUBLIC**（`private: false`, `visibility: public`）→ 任何入库内容都可能公开可读，
**入库前必须做凭据扫描**。2026-10-29/30 已在 `.backups/` 里发现 `appSecret` / API key 明文并清除了（见下）。

### 2026-10-29~30 工作区收口（未提交 118 条 → 0）
- **`.gitignore` 新增**：`.backups/`、`*.bak-*`、`openclaw-workspace-state.json.migrated.*`、
  `heartbeat/cache/`、`reports/*.html`、`reports/*_chart.png`、`heartbeat-state.json`、
  `memory/.dreams/session-corpus/`、`DREAMS.md`、`agents/orchestrator/Tomorrow_Action_Plan_*.md`
- **6 个 `agents/*` 目录是独立 git 仓库**（不是本仓库内容）：`coder`→M365_Copilot_Playwright_Proxy.git、
  `finance`→/home/zhiping/a-stock-daily-report、`health/life/scout/work`→空仓库(无 commit) → 已忽略
- **嵌套 gitlink 已移除**：`amat-stock-report`、`skills/{ashare-ai-strategy-analyst,stock-report}`、`wechat-cli`
- **双文件名修复**：`c9353413` 引入的 `"memory/nightly-main-2026-10-27.md nightly-main-2026-10-29.md"`（本地已有正确单文件版）

### 🔴 push 失败真因（2026-10-30，已解决）
`git push` 反复失败（卡在 `POST git-receive-pack`,116MB POST 被远端断开）→ **不是网络/代理/chunked 问题**
（curl 实测 chunked 与 normal POST 均 0.69s 返 401；`ls-remote` 正常）。真因是待推 pack 内含
`.backups/doctor-fix-20261019-011140/` 的 8 个 sqlite 备份（**434MB**，单文件最大 214.5MB）。

修复：`git filter-branch --index-filter` 改写**未推送段**（12 commit）剔除 `.backups/` 与 `reports/*.html`
→ 待推 blob **459.6MB → 10.0MB**，push 立即成功。远端完整历史 1142 对象已扫描 → **凭据命中 0**。
安全 tag `safety/pre-backups-purge-20261030-001127` 保留原历史可回滚。

**未提交文件** (2026-08-28 13:45, `git status --short`):
- Modified (8): `.learnings/ERRORS.md`, `MEMORY.md`, `agents/orchestrator/{AGENTS,DIRECTIVE,HEARTBEAT,IDENTITY,SOUL}.md`, `agents/orchestrator/output/Tomorrow_Action_Plan.md`, `scripts/openclaw-backup.sh`
- Untracked (14): `.graphify_new_extract.json`, `.learnings/LEARNINGS.md`, `AGENTS.md`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md`, `agents/{coder,finance,health}/`（这些是 BOOTSTRAP 新建, 之前未入库）

> 前次记录"未提交 3 个文件"严重低估。

## NightOps 窗口

- **时间**: Mon-Fri 00:30-03:00 CST（2026-10-24 起，原 21:30-23:30）
- **规则**: 检查在此窗口内；不在则静默 `HEARTBEAT_OK`
- **检查项**: 邮件、天气（若外出）、日历（2h内）
- **优化提议规则（2026-10-24 ZP 要求）**: NightOps 讨论中发现更优的优化方式（网络/系统/配置类）→ 先列方案要点提醒 ZP 确认，不擅自实施

## 关键发现

- **Jina AI 网络被封**: 使用 SiliconFlow BAAI/bge-m3 替代 jina-embeddings-v5-text-small
- ~~Gateway RSS 3.5 GiB~~ — 2026-08-28 实测 ~1.29 GiB；之前记录是错的（可能是别的主机或 RSS 被误读）
- ~~NightOps 误报: MEMORY.md 检查路径为根目录~~ — 这条**未查到出处**，实际 MEMORY.md 一直在 workspace 根（`~/.openclaw/workspace/MEMORY.md`），不存在路径误报问题。可能是别人误传。
- **WSL 11 天失联事件 (2026-08-15 → 2026-08-26)** — 详见 ERR-20260826-001
  - **根因**: WSL Mirrored + APNetwork/WinDivert + Windows Update 三方冲突，2026-08-18 14:26 NDIS.SYS LiveDump (BugcheckCode 350)
  - **修复**: `.wslconfig` 改为 `networkingMode=nat` + `dnsTunneling=true` + `autoProxy=true`，`wsl --shutdown`
  - **教训**: WSL Mirrored 模式脆弱；备份连续性检查缺失；NightOps 自检不独立
- **取证证据** (2026-08-26 定位):
  - NDIS dump: `C:\Windows\LiveKernelReports\NDIS\NDIS-20260818-1426.dmp` (1.9MB) — 含 WinDivert64.sys 加载记录
  - WER 报告: `C:\ProgramData\Microsoft\Windows\Wer\ReportArchive\Critical_10.0.26100.9156__306dad...bcd9900d-5964-42f0-b88d-52fb46ecfec9\Report.wer` — TiWorker.exe 失败详情
  - VSS 快照恢复 .wslconfig 历史: `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy{5-18}`
  - Kernel-LiveDump evtx: 2026-08-18 06:26 NDIS crash 全记录
  - 备份跳点验证: `/mnt/h/.../openclaw-*.tgz` 列表中 8/15 → 8/26 09:43 间隔 11 天，与 NDIS dump 时间窗口高度吻合
- **NDIS dump 关键发现**: WinDivert64.sys (`D:\APNetwork\data\flutter_assets\sdk\WinDivert64.sys`) 与 WSL Hyper-V Virtual Switch + WFP filter 同时加载。NDIS 崩溃时三方共存
- **APNetwork Monitor 日志铁证**: 8/16 00:59 后 APNetworkMonitor 自己静默了 4 天；8/20 21:59 恢复时记录外网仍不通；8/21 16:14 APNetwork 重启恢复外网，但 WSL Mirrored 桥已永久断
- **当前 .wslconfig (2026-08-26 修复后, 2026-08-28 验证仍然如此)**:
  ```
  [wsl2]
  networkingMode=nat
  dnsTunneling=true
  autoProxy=true
  ```
  WSL 内 DNS: `10.255.255.254` (Hyper-V DNS proxy)

## 网络自检结论 & 经验（2026-10-24）

- **隧道健康信号**: APNetwork 适配器 Up + google generate_204 返 204 + 出口 IP 非空（当前 207.174.28.79）+ `@198.18.0.1` fake-ip 应答；DNS 污染标记 = 解析出 31.13.x 段 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- **提权约束**: ap_network 由 Start_APNetwork 任务提权启动，WSL interop 杀不掉（拒绝访问）→ 一切 kill/修复走 ResetAPNetwork 任务（RunLevel=Highest，15min 周期）内嵌钩子 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- **自愈脚本组**（C:\Scripts\）：CheckAPNetwork.ps1（监控+快速路径+钩子）/ NetRepair.ps1（-OnlyIfBroken 幂等自愈，健康即跳过，已实渨验证）/ NetHarden.ps1（BlockInbound 默认关） <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- **教训**: 加固时 Restart-NetAdapter 会摔断隧道（10:33/10:36 两次重启 → 断网）→ NetHarden 必带 -SkipNicRestart，重启 NIC 后须跑 NetRepair 重建隧道；BlockInbound-* 当时并非断隧道元凶但已全部删除并默认不创建（fw-clean 钩子，标记 net-clean.done） <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- **分流现状**: APNetwork 本就分流（isFullRoute=false；腾讯系/微博/中国区 IP 直连，其余走隧道；规则服务端下发，客户端无 dns/doh 键）。实测：facebook→fake-ip 198.18.0.177→200；baidu→真实 IP 183.2.172.177 直连；国内出口 118.112.96.162 / 国际 207.174.28.79 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- **DoH 结论**: WSL 不启用 — 阿里 DoH JSON 35-41ms vs UDP 16ms vs 当前系统解析 6-8ms；加密 DNS 会绕过 fake-ip 反而破坏分流；手动核对工具 `curl "https://223.5.5.5/resolve?name=x&type=A"` <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
- **WSL DNS**: /etc/systemd/resolved.conf.d/99-wsl-dns.conf（DNS=119.29.29.29，Fallback 10.255.255.254），实测 6-8ms（原 35-40ms）；备份后缀 .bak-20261024-103134 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## 飞书集成

- **频道配置** (`openclaw.json` `channels.feishu`, 2026-08-28 验证 keys): `appId`, `appSecret`, `enabled`, `connectionMode`, `dmPolicy`, `groupPolicy`, `requireMention`, `groupAllowFrom`
  - **没有 `doc_id` 字段**。飞书集成是 IM (im/v1/messages) 不是 Doc API；上次的"待补 doc_id"是误记
- **推送目标 chat**: `groupAllowFrom[0]` = **Openclaw 日报推送群** (`oc_f54afb4bc6f317bdae35af63d2a48926`)
- **备份日志推送脚本**: `~/.openclaw/workspace/cron-scripts/send-backup-log-feishu.py` — 从 `channels.feishu.{appId, appSecret, groupAllowFrom[0]}` 读凭据，POST `https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id`
- **凭据保护**: `OpenClawHealthCheck.ps1` 也读同一个 `\\wsl$\Ubuntu\home\zhiping\.openclaw\openclaw.json`，绝不硬编码
- **独立告警 chat**: PS 脚本里 `$FeishuChatId = 'oc_f54afb4bc6f317bdae35af63d2a48926'`（与 groupAllowFrom[0] 一致）
- 2026-08-12: `tenant_access_token + GET /im/v1/chats` 验证通过；脚本可跑（依然可用, 2026-08-28 复核）

---

_Last updated: 2026-10-31 18:10 CST (新增：OpenClaw 10.5→10.7/10.9 升级评估 —— 内容层无新功能、三版皆安全发布；Node v26.10.0 < 要求 26.12.1 为硬门槛；Gateway 版本行纠正为 2026.10.5)_

## 审计日志 (Audit Trail)

- **2026-08-28 13:50** — 全面校验 MEMORY.md，修正：
  - Gateway pid/RSS 写死值（实际 pid 623, RSS 1.29 GiB）
  - Agent 列表漏掉 health/work
  - 备份脚本路径错误
  - GitHub token 重复条目
  - openclaw-zero-token "package-lock.json 缺失" 误判（项目非 Node）
  - feature/backup-script 状态描述错误
  - 未提交文件列表严重低估（实际 8 modified + 14 untracked）
  - "每月数十次 APNetwork 崩溃" 无证据
  - ~~NightOps 误报~~条目查无出处
  - ~~待补飞书 doc_id~~ 划线混乱（实际是 IM chat）
  - 新增 P0: PROXY DOWN 127.0.0.1:25017
  - 新增 PS 脚本编码 bug 记录
