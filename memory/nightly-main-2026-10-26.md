# Main NightOps 记忆（2026-10-26 03:00 场）

## ✅ 本场产出
- `heartbeat/main-nightops-review-2026-10-26.md` — 全局复盘（三源整合 + 16 项 P2 观察）
- cross-agent-log 追加「coder 状态澄清」条目

## 🔴 P0 关键发现
- **Gateway RSS 10.29–10.94GB 持续爬升 + CPU 86.9% 不回落**（uptime 1d16h），劣化持续
- 根因：**非泄漏，是会话量线性增长**（15194 anon 映射 / 2571 会话 ≈ 5.91 映射·会话）
- Heap 仅 496MB → `--max-old-space-size` 无效；**真杠杆 = 会话转录保留策略**
- 需 ZP 白天决定：①重启买时间 ②清理 1956 json + 605 zst ③保留策略（数据风险，ZP 亲自做）

## 🟡 P1/P2 关键
- Coder 本场 **cron 存活但 nightly 落盘缺席**（`nightly-coder-2026-10-26.md` 缺位；`code_report-2026-10-26.md` 02:30 已落盘）→ 10-27 需重点观察是否恢复
- 主群会话 `agent:main:feishu:group` **status=failed**，contextTokens 191471/204800（>80%）→ 建议核查
- MiniMax 凌晨 429 最高 83% → Token Plan 5h 窗口耗尽；三选一交 ZP
- deepseek-flash/pro 稳定 200 → 临时 fallback 链提案已获批准备（待 ZP 拍板写入）
- 10-24 四件建议落实核验：飞书 SecretRef ✅ 已解决；其余 3 项（BILIBILI_COOKIES / OPENROUTER_API_KEY / news_digest 0 条退出码）未核验

## 🟢 数据亮点
- MCP servers v2.1.0：3 server × 8 CVE，8 条 GHSA 同日公开；升级需显式版本号（semver 陷阱）
- CVE-2026-111497 Brotli RCE CVSS 9.2，OpenAI 2月发现 10-23 披露 → AI 发现漏洞流水线化
- 内容侧：B站播放与传播效率负相关；AI 六项互动率全部低于大盘
- 中文 digest 源码级污染：以“搜索”代“直抓”（line 1422），中位龄 234 天

## 📌 经验
- NightOps 期间报告收集层可 100% 落地，但执行层受“ZP 授权边界”约束 —— 涉及配置/凭证/删除资产时保持只读，列入白日队列
- 「报告存活 vs 落盘路径断点」要严格区分，避免误判 agent 失联（10-24 教训复用）

## 明日（10-27）跟进优先
1. P0-1/ZP：Gateway 重启 + 会话保留策略
2. P0-2/Orch→Coder：重启后 3-4h 复查 RSS/CPU
3. P0-3/ZP：MiniMax Token Plan 三选一
4. P1-5/Coder：qwen3.6:27b ECONNREFUSED + 临时 fallback 链（需 ZP 批准）
5. P1-8/Orch：08:00 news digest settlement 是否复发
