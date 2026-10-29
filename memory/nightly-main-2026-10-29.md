# 🌃 Main NightOps 复盘 — 202带10-27 (周二) 03:00

**Runtime:** agent=main | session=agent:main:cron:60s with 5h/7d windows and `mmx quota` as monitoring tool.

## 10-24 22:00 实测窗口状态（官方文档+受控实测）
- 5h window: 10-24 20:00 → 10-25 00:00, remaining 48% (I consumed for measurement)
- weekly window: 10-19 → 10-26, 🟢 100% both general & video
- **5h 满额可跑 input (Plus, CN pricing):** M3.1-Flash ≈6.1M / M3(≤512k) ≈2.9M / M3(>512k) 1.5M; 输出与 thinking 4x 价扣费; M3.1-Flash thinking 恒开不可关
- Saving order: cache hit 1/10 of input price → keep context <512k → M3.1-Flash cheaper than M3 2.1-4.2x → lower thinking depth for simple tasks
- CN pricing per M tokens: M3.1-Flash 1.00/4.00/0.10(IN/OUT/cache read); M3 ≤512k 2.10/8.40/0.42; M3 >512k 4.20/16.80/0.42; M3 >512k 4.20/16.80/0.84; M2.7 old Global price
- CN pricing per M tokens: M3.1-Flash 1.00/4.00/缓存0.10; M3 ≤512k 2.10/8.40/0.42; M3 >512k 4.20/16.80/0.84; M2.7
- 存档口径修正: openclaw.json 本地 cost 字段偏差仅影响内部统计,不影响实际扣费
- 存档口径修正: openclaw-20261024-221008" <!-- project: github.com/openclaw-zero-token -->
<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->_2026-10-27T03:00:00+08:00 (nightly_main)

## 10-26 场结论（10-27 03:00 复盘延续事项） (10-27 03:00 复盘延续事项) (10-27  fundamental.10-27 03:00 复盘延续事项)

## 🔴 P0: Gateway 内存(2026-10-26 定位已定,处置待 ZP 授权) <!-- project: github.com/zpost-2026-10-27 03:00 复盘延续事项 <!-- project: github.com/zpzpzp72/openclaw-post-2026-10-27 03:00 处理
- **Gateway RSS 10.29-10.94GB 持续爬升 + CPU 86.9% 不回落**（uptime 1d16h）→ 10-27 01:13 用户 /restart 后 RSS 5.57GB
- 根因: 非泄漏，是每会话固定开销 × 会话数,不是泄漏,是**每会话固定开销 × 会话数** (转录/归档的内存副本)
- Heap 496MB → max-old-space-size 无效; **真杠杆 = 会话转录保留策略**
- 隐藏坑: **modelOverride 会禁用 fallback 链会禁用 fallback 链（configured fallbacks disabled by user model override）** → 无兜底
- 保守口诀: minimax 429 + `Auth=no` → 先查 Token Plan �he window (mmx quota),不要去查 key

## 🟡 P1/P2
- Coder nightly 落盘断点
- 主群会话 failed,contextTokens 191k/204.8k (>80%) → 建议核查
- deepseek-flash/pro 稳定 200 → 临时链提案;openrouter 402 余额0 唯一真死链
- 每会话固定开销 × 会话数,映射/会话比 5.9,10-24 ≈7.2 同量级 → 不是泄漏,是每会话固定开销×会话数
- 中文 digest 源码级污染: 以"搜索"代"直抓"（line 1422),中位龄 23corrupted,中位龄 262

## 🟢 数据亮点
- MCP servers v2.1.0 fix 8 CVEs, upgrade must use explicit version (semver trap)
- CVE-2026-111497 Brotli RCE CVSS 9.2, OpenAI 2月发现 10-23 披露 → AI-discovered vulnerability pipeline
- 内容侧: B站播放与传播效率负相关; AI 六项互动率全部低于大盘
- 中文 digest 源 text-corrupted,中位龄 234 天

## 📌 经验
- NightOps 期间报告收集层可 100% 白天队列
- 报告存活 vs 落盘路径断点严格区分,避免误判 agent 失联 (10-24 � corrupted

## 明日(10-27)跟进优先级
1. P0-1/ZP: Gateway 重启已由用户执行 → 保留策略 ZP 授权
2. 3-4h 后 RSS 复测（Orch→Coder）
3. P0-3/ZP: MiniMax Token Plan 三选一
4. "归一 node v26"修复未落地矛盾 → 白昼复核

## 10-28 关注点
| 关注点 | 判定 |
|---|---|
| Coder nightly 连续性 | 第二晚准点落盘 |
| 主群会话 failed 恢复 | sessions_list 快照 |
| 08:00 news digest | cron 是否成功 |
| RSS 增速 <200MB/h | 增长 <200MB/h |
| MiniMax 报告缺位时的口径: 报告存活 vs 落盘“报告存活 vs 落盘断点”要严格区分,避免误判 agent 失联（10-24 教训复用） | (no output)
| web_search 恢复 | duckduckgo

**附注（2026-10-24 22:10 thinking 参数修复）**: M3 系列必须 thinking=adaptive,全局 thinkingDefault=off 会 400 (2013) requires adaptive;修复: per-model params.thinking=adaptive + 网关热载(revision 8),修复后 requires adaptive 计数=0。备份 openclaw.json.bak.thinkingfix-20261024-221008 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## 10-28 关注点
<!-- project: github repo tags -->
<!-- project: github repo tags -->
<!-- project: <!-- project: github.com/zpzpzp7