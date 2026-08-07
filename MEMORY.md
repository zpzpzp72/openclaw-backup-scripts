# MEMORY.md — Long-Term Memory

_Curated insights from sessions past. Updated periodically from daily notes._

---

## 系统架构

- **Gateway**: pid 691775, 端口 18789, 内存 3.5 GiB（轻微超3GiB阈值但稳定）
- **备份**: 热备份脚本 `openclaw-backup.sh`，输出 `/mnt/h/AI/openclaw.zone/WSL/`
- **cron**: Main NightOps session `agent:main:cron:603be37f-4a00-440c-8632-aee35cdfcc78`
- **模型**: minimax/MiniMax-M2.7 (default) → longcat/LongCat-2.0 → ollama/qwen3.6:27b

## 持续性风险

| 优先级 | 问题 | 首次发现 | 状态 |
|:------:|------|:--------:|------|
| P1 | openclaw-zero-token 116d 停滞 | 2026-07-31 | 🟡 未推进 |
| P1 | browser.py:41 bare except | ~2026-04 | 🔴 未修复 |
| P2 | memory-lancedb-pro 未注册 | 2026-07-31 | 🔴 104 commits 积压 |
| P2 | Coder 三模型全败（rate limit/billing/timeout） | 2026-08-08 | 🔴 Token额度耗尽 |

## Git 积压

| 分支 | 状态 | 待办 |
|------|------|------|
| `feature/hot-backup` | 领先 origin 1 commit | `git push` |
| `feature/backup-script` | 需与 hot-backup 协调 | 合并或删除 |

## NightOps 窗口

- **时间**: Mon-Fri 21:30-23:30 CST
- **规则**: 检查在此窗口内；不在则静默 `HEARTBEAT_OK`
- **检查项**: 邮件、天气（若外出）、日历（2h内）

## 关键发现

- **Jina AI 网络被封**: 使用 SiliconFlow BAAI/bge-m3 替代 jina-embeddings-v5-text-small
- **Gateway RSS 3.5 GiB**: 轻微超阈值，但系统有 24 GiB 可用，暂时无需重启
- **NightOps 误报**: `MEMORY.md` 检查路径为根目录，实际文件可能在 `agents/orchestrator/` 子目录

## 飞书集成

- 飞书文档读写技能已配置
- 备份日志发送脚本: `cron-scripts/send-backup-log-feishu.py`
- 待完成: 配置飞书 doc_id 以自动发送备份摘要

---

_Last updated: 2026-08-08_
