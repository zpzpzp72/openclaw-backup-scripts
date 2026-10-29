# Tomorrow Action Plan — 2026-10-31

> 生成：2026-10-30 02:45 Orchestrator NightOps（cron d7773686）。报告源：Scout 10-30 ✅、Coder 10-30 ✅、Life 10-29 ✅、Main 10-29 ✅。

## P0
1. Gateway RSS 12.25GB 第6次劣化（根因=trajectory 256KB 展开副本）→ ZP 择机重启；重启后 Coder 3-4h 复测（目标 <200MB/h）
2. /mnt/h 98%：回收站滞留 17 份被删备份 ≈140G，SMB 9P 下 rm 不释放 → 待 ZP 授权清 /mnt/h/#recycle/AI/openclaw.zone/WSL/（不可逆，需拍板）
3. OpenClaw 2026.10.5 → npm 10.9（0 天新鲜度）或浸泡选 10.8；清单已备（822f46fd），待 owner + 维护窗口

## P1
4. 模型单点：OpenRouter 402 充值或放弃；LiteLLM@NAS DB 恢复；MiniMax 429 观察再现
5. web_search 连续 11 场失败 → 知乎直采 API 接入 digest 替代中文源（中位龄 231 天）
6. git：push 凭证（backup 2 commits + copilot_proxy 5 orphan）或启动 U-4 零 commit 模式
7. 微博 hot_band 403 → cookie 或固化 tophub；微信 Windows 侧重导出

## P2
8. Health 空转 / Finance 04-07 停摆 → 复活/合并/关闭，ZP 决策
9. watchdog line50 语法错、/mnt/m 心跳 stale、ruff 安装（U-5）
10. NightOps 错峰至 00:30–03:30，避 MiniMax burst 窗口

## 亮点
- 安全：.backups（434MB 备份+含凭据配置）已被 Coder 移除——本周期最重要安全修复
- 备份推送链幂等化端到端实测通过；NightOps 报告链恢复（Scout/Coder 连续两晚准点）

## 主要阻塞
- 3 项授权：清回收站 ~140G / 会话保留清理 / 重启 Gateway（全需 ZP）

## 观察点（10-31 场）
Gateway RSS 是否破 12.5GB；MCP SEP-3392 首个 SDK、Mistral Large 4 评测、Gemini 4 Carbon 是否公开；MiniMax 429 是否再现
