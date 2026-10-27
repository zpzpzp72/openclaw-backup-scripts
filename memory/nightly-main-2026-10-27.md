# Main NightOps 记忆（2026-10-27 03:07 场）

## ✅ 本场产出
- `heartbeat/main-nightops-review-2026-10-27.md` — 全局复盘（三源整合，Scout 缺席以 10-26 场顺延）
- cross-agent-log 补「主群会话 failed 观察」待白天核查
- heartbeat-state.json 合并更新（保留原字段，只追加/改本日快照键）

## 🔴 P0 关键发现
- **Gateway 已由用户重启（01:13，pid 497240）** → 10-26 复盘中 pid 319857 数据失效
- 重启后 RSS 5.57GB，P0-1 拆成：1a 重启 ✅ / 1b 会话保留策略 ⏳（删除 1956 json + 605 zst 需 ZP 授权）
- **备份盘接近满：/mnt/m 97%、/mnt/h 98%（18G free）→ 今晚 03:00 备份存在落盘失败风险**
- 主群会话 status=failed（contextTokens 191k/204.8k >80%）→ 白天核查

## 🟡 P1/P2 关键
- Coder nightly 恢复落盘 `nightly-coder-2026-10-27.md`（01:30，间隔 7 天后回归）— 10-26 关注点已闭环
- Orch 02:45 落盘 10-27 场报告 + 10-28 明日计划（P0×3 / P1×4 / P2×4）
- Heartbeat delivery 8 job 仍 telegram:123456789 占位 → 改飞书
- M365 push 凭证：截止 10-29（剩 2 天）→ ZP 白天
- AMAT 邮件+飞书双通道 10-26 21:30 首通
- qwen3.6:27b ECONNREFUSED：Coder 白天探活

## 🟢 数据亮点
- 生命线：备份 5 连绿；B站日报+news_digest 连续 2 天稳定
- 内容双选题就绪：①「20 万媒体/艺术岗位」②「B站 14 天复盘」

## 📌 经验（复用 10-24 教训）
- 「报告存活 vs 落盘断点」口径：10-27 Coder nightly 已恢复，历史口径问题闭环
- 主群会话 191k/204.8k tokens >80% → 白天核查是否重启/重开会话

## 明日（10-28）跟进优先
1. P0-1b/ZP：会话保留策略授权 → Coder 执行清理
2. Coder 白天：qwen3.6:27b 探活 + RSS/CPU 复查（重启后 3-4h）
3. ZP：MiniMax Token Plan 三选一、deepseek 临时链写入、M365 凭证（10-29 截止）
4. Orch 心跳：08:00 digest、路由改飞书提案
5. Life 白天：B站 10-27 增量日报
