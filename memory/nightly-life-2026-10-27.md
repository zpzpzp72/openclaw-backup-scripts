# NightOps Life — 2026-10-27 (memory)

> 详细报告：`heartbeat/nightly-life-2026-10-27.md`

## 头号事实

- 本场 00:55 触发，LLM 报告生成未启动，属意外触发场次，按极简巡检处理
- gateway RSS **12.0GB** / CPU **82.7%**（ps 实测）——较 10-26 场记录的 10GB 进一步恶化
- OpenClaw 实际运行 **2026.10.5**（`openclaw --version` 确认），latest v2026.10.7 待升级
- news_digest 与 B站日报已连续两日（10/25、10/26）稳定产出

## 明日选题（10-27）

沿用 10-26 场结论：
- **P0-①**「20 万媒体/艺术岗位没了，多少是 AI 的？」（知乎+公众号）★★★★★
- **P0-②**「B站 14 天 140 条复盘：'合集'完胜'爆款'」（知乎+公众号）★★★★☆
- P1-③④⑤：本体见顶论、内容两极、平台适配（微博 4% vs X 0%）

## 异常与待办

- 🔴 gateway 内存持续劣化（10GB→12GB），需人工介入
- 🟡 升级 2026.10.5→2026.10.7，勿裸 npm i -g（prefix 污染坑），用 `openclaw gateway install --force --runtime-path`
- 🟡 BILIBILI_COOKIES / OPENROUTER_API_KEY / 飞书 SecretRef 仍未配置
- 🟡 web_search duckduckgo provider_error 多日，配 fallback
- 🟡 wechat-cli 数据止于 8/28

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
