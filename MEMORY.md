# MEMORY.md — Long-Term Memory

_Curated insights from sessions past. Updated periodically from daily notes._

---

## 系统架构

- **Gateway** (2026-10-03 17:30 CST 验证): 端口 18789, **app 2026.9.7 (c074824)** linux 6.6.87.2-microsoft-standard-WSL2
  - 实际安装路径: **NVM** `/home/zhiping/.nvm/versions/node/v26.10.0/lib/node_modules/openclaw`（不是 npm-global）
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
- **cron** (用户 crontab 2026-08-28): 11 行定时任务
  - 备份: `0 3 * * *` (`scripts/openclaw-backup.sh`)
  - Finance A股: `0 9 * * 1-5` (`agents/finance/a_stock_daily.py`)
  - AMAT 报告: `30 21 * * 1-5` + `0 4 * * 2-6` + `30 22 * * 1-5` + `0 5 * * 2-6`（4 次/天）
  - 新闻摘要: `0 8 * * *` (`scripts/run_news_digest.sh`)
  - NightOps / claw-sync / heartbeat: `@reboot` + `30 3 * * *` + `0 * * * *`
- **模型 fallback 链** (`openclaw.json` `agents.entries`, 2026-10-24 实测校正) <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
  - `agents.defaults.model`: primary `minimax/MiniMax-M3`; fallbacks `longcat/LongCat-2.0` → `ollama/qwen3.6:27b`
  - `agents.entries.main`: 无 primary(继承 defaults); fallbacks **`litellm/MiniMax-M2.7`** → `longcat/LongCat-2.0` → `ollama/qwen3.6:27b`
  - `agents.entries.{orchestrator,scout,coder,life,finance}`: primary `minimax/MiniMax-M2.7`, fallbacks `litellm/MiniMax-M3` → `longcat/LongCat-2.0` → `ollama/qwen3.6:27b`
  - `agents.entries.health`: primary `longcat/LongCat-2.0`; `work`: primary `minimax/MiniMax-M3`, fallbacks `litellm/deepseek-flash` → …
  - **provider 实际列表**: minimax / litellm / ollama / longcat / siliconflow / openrouter（6 个，不止之前记的 3 个）
  - **认证来源在 sqlite auth profiles**（`state/openclaw.sqlite` `config_machine_state` + `~/.openclaw/agents/*/agent/openclaw-agent.sqlite`），不在 env；`openclaw models status --json` 可查 effective

## 持续性风险

| 优先级 | 问题 | 首次发现 | 状态 |
|:------:|------|:--------:|------|
| P0 | **WSL 网络架构: 禁用 Mirrored 模式** — Mirrored + WinDivert (APNetwork) + Windows Update 三方冲突 → NDIS 崩溃 → OpenClaw 失联 | 2026-08-26 | ✅ 已切回 NAT+dnsTunneling+autoProxy，永久禁用 Mirrored |
| P0 | **备份连续性监控缺失** — NightOps 也在 WSL 里跑，WSL 死了连备份检查都没人做；需外部健康检查 | 2026-08-26 | ✅ 已修复 (2026-08-26 11:25): 备份心跳文件 + Windows 任务计划程序独立检查 + 飞书 webhook |
| P1 | **GitHub token 无效** — `gh auth status` 失败，Coder/CI/PR 全线受阻 | 2026-08-13 | 🔴 需手动 `gh auth login -h github.com` |
| P1 | openclaw-zero-token 项目基本停滞（最近 commit 2026-08-08 docs, 实质改动 7/30 之前）；是 **shell+python** 项目，**没有 package.json / package-lock.json**（MEMORY 之前关于 npm audit 的说法不成立） | 2026-07-31 | 🟡 未推进 |
| P1 | browser.py:41 bare except | ~2026-04 | 🔴 未修复 |
| P1 | memory-lancedb-pro 落后 upstream **104 commits**（已重新核对, 2026-08-28） | 2026-07-31 | 🔴 未注册, 持续积累 |
| ~~P1~~ | ~~WeChat DNS `EAI_AGAIN` 持久化问题~~ | 2026-08-13 (cron 报告) | ✅ 2026-10-24 复测不复现：5 个微信域名 DNS 解析正常、TCP 全通、HTTPS 0.17–0.38s | <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
| P0 | **PROXY DOWN 127.0.0.1:25017** — `curl http://127.0.0.1:25017/` Failed to connect, 无 proxyon 进程，2026-08-27 发现；导致 `git fetch origin` 失败（memory-lancedb-pro 同步受阻）。**注意：`172.18.160.1:25017` 是通的**（根路径 404 属正常，实测能代理 wx.qq.com 200/0.28s），微信通道用的是后者，不受影响 | 2026-08-27 | 🔴 Main 未处理（仅影响 git fetch） | <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
| P2 | Coder 最近 code_report 停留在 **2026-07-30**（29 天没更新）；orchestrator 标"08-27 cron 恢复"但实际产物未刷新 | 2026-08-28 | 🟡 待核查 |
| P1 | **Gateway RSS 4.9 GB vs `--max-old-space-size=4096`** — 2026-10-24 实测 pid 262802: VmRSS 5,007,848 kB / VmHWM 同值 / RSS≈RSS_anon 4.9 GB / VmSwap 0；其中 **V8 [heap] 仅 496 MB，另有 4.2 GB 在 9388 个 anon rw- 映射里（非 V8 堆）** → 外部 Buffer/native 内存膨胀，非 JS 堆泄漏。**实测仍在缓慢增长**：5,007,848 kB (01:48) → 5,155,484 kB (02:05) → 5,180,124 kB (02:07)，约 **+11 MB/min**，非平台期，属**持续性外部内存累积**。CPU 100–148%，GC 抖动 → 通道消息延迟 | 2026-10-24 | 🟡 待定位那 4.2 GB 的具体占用方（候选：sqlite blob 读取 / transcript archive 解压 / capture_blobs） | <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
| P2 | **APNetwork + WinDivert 稳定性** — 已确认 NDIS dump 仅观察到 1 次（2026-08-18 14:26），"每月数十次崩溃"无证据；WinDivert64.sys 时间戳 2022-09-20（很久没更新）；主要风险是三方共存而非高频崩溃 | 2026-08-26 | 🟢 切 NAT 后未复发，保留"未来 NDIS 更新时可能再触发"的观察 |
| (已合并) | ~~Coder Codex/Arcee/Kimi 三模型全败~~ — 2026-08-08 报告已过期 20 天，未重测；如需查证需单独跑 Coder probe | 2026-08-08 | ⏸️ 暂搁置 |

## Git 积压 (2026-08-28 验证)

| 分支 | 状态 | 待办 |
|------|------|------|
| `feature/hot-backup` | 领先 origin 1 commit (2f10a82c docs: add MEMORY.md)；**推送受阻**（GitHub token 无效 + PROXY DOWN） | `git push` |
| `feature/backup-script` | 领先 origin **0** commit (1e3cc687 2026-03-27) — 跟 hot-backup 同步；跟 origin 已同步，不是"需协调" | 考虑删除或合并 |

**未提交文件** (2026-08-28 13:45, `git status --short`):
- Modified (8): `.learnings/ERRORS.md`, `MEMORY.md`, `agents/orchestrator/{AGENTS,DIRECTIVE,HEARTBEAT,IDENTITY,SOUL}.md`, `agents/orchestrator/output/Tomorrow_Action_Plan.md`, `scripts/openclaw-backup.sh`
- Untracked (14): `.graphify_new_extract.json`, `.learnings/LEARNINGS.md`, `AGENTS.md`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md`, `agents/{coder,finance,health}/`（这些是 BOOTSTRAP 新建, 之前未入库）

> 前次记录"未提交 3 个文件"严重低估。

## NightOps 窗口

- **时间**: Mon-Fri 21:30-23:30 CST
- **规则**: 检查在此窗口内；不在则静默 `HEARTBEAT_OK`
- **检查项**: 邮件、天气（若外出）、日历（2h内）

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

## 飞书集成

- **频道配置** (`openclaw.json` `channels.feishu`, 2026-08-28 验证 keys): `appId`, `appSecret`, `enabled`, `connectionMode`, `dmPolicy`, `groupPolicy`, `requireMention`, `groupAllowFrom`
  - **没有 `doc_id` 字段**。飞书集成是 IM (im/v1/messages) 不是 Doc API；上次的"待补 doc_id"是误记
- **推送目标 chat**: `groupAllowFrom[0]` = **Openclaw 日报推送群** (`oc_f54afb4bc6f317bdae35af63d2a48926`)
- **备份日志推送脚本**: `~/.openclaw/workspace/cron-scripts/send-backup-log-feishu.py` — 从 `channels.feishu.{appId, appSecret, groupAllowFrom[0]}` 读凭据，POST `https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id`
- **凭据保护**: `OpenClawHealthCheck.ps1` 也读同一个 `\\wsl$\Ubuntu\home\zhiping\.openclaw\openclaw.json`，绝不硬编码
- **独立告警 chat**: PS 脚本里 `$FeishuChatId = 'oc_f54afb4bc6f317bdae35af63d2a48926'`（与 groupAllowFrom[0] 一致）
- 2026-08-12: `tenant_access_token + GET /im/v1/chats` 验证通过；脚本可跑（依然可用, 2026-08-28 复核）

---

_Last updated: 2026-08-28 13:50 CST (审计修正: 13 处过期/未查证条目)_

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
