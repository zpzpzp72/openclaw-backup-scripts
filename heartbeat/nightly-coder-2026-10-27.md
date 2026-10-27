# NightOps Coder Report — 2026-10-27

**Generated:** 2026-10-27 01:30 CST (cron a38acaaa-52ef-4e46-badf-8104a6fd1c41) · **Night #79**
**Runtime:** Claude Sonnet 4.5 (1M context) · gateway 2026.10.5 (1b58cb9)
**上一场 coder 报告：** nightly-coder-2026-10-20.md（10-20 22:20）→ **间隔 7 天**（10-21~10-26 六晚缺席）

---

## 0. 服务状态表 (Service Status Table)

| 项 | 状态 | 值 |
|----|------|-----|
| NightOps-Coder | 🟢 | 2026-10-27 01:30 CST 本场落盘 |
| OpenClaw | 🟢 运行 | 2026.10.5 (1b58cb9)，pid 497240 |
| OpenClaw latest | 🟡 | 2026.10.7 (10-24 上线) — 存在待评估升级 |
| extended-stable | 🟢 | 2026.9.34 |
| beta | — | 2026.10.10-beta.3（不采纳） |
| Gateway RSS | 🟢 | 2 GB @ 01:15（重置后） |
| Gateway CPU | 🔴 | 148% @ 01:15（满载告警，待白天核验） |
| Backup | 🟢 | 20261026-0300.tgz 8.8 GB（03:13）|
| Backup target disk | 🟡 | /mnt/h 98%（186G free）⚠️ ZP 白天建议关注容量 |
| Workspace git | 🔴 | 579 untracked + 11 modified/deleted · ahead 25（待 push） |
| CI（backup-scripts 类） | 🟢 | 无 run 无失败 |
| CI (memory-lancedb-pro) | 🟡 | 10-05 红灯在案（175 天红灯待检） |
| openclaw-source fork | 🟡 | ahead 224 / behind 6290 |
| Heartbeat delivery | 🔴 | 8 jobs 仍 "waiting for delivery route"（telegram:123456789 占位） |
| AMAT 双通道（邮件+飞书） | 🟢 | 10-26 21:30 班次验证成功（message_id 归档） |
| News digest | 🟢 | Gmail 成功（10-26）· OpenRouter 402 缺积分 |
| minimax_429 | 🟡 | 凌晨峰值 83%（2056 quota cap）→ 配额管理：CN key → api.minimaxi.com |

> 图例：🟢 正常 · 🟡 降级/告警 · 🔴 需人工/失败

---

## 1. 深挖发现（new this run）

1. **`.memory-write.lock.lock` 进 tar 扫描**：10-26 备份在排它锁存在窗口扫到了它 → tar 退出码 1（产物完好）。修正思路：backup.sh 加 `--exclude='*/.memory-write.lock.lock'`。
2. **备份盘容量**：39 份归档 / 8.6~9.1 GB/份，/mnt/h 98% 空闲186GB。RETAIN_DAYS=30 未清到 30 天内 → 白天需评估保留策略。
3. **tar 退出码 1**（10-20/10-26 均报 1）为热备份良性退出，无需停服备份。
4. **AMAT feishu 双通道确认打通**（10-26 21:30 成功回执）→ AMAT cron 从「邮件 failed」到「双通道成功」。
5. **git 590 dirty**：11 changed + 579 untracked（`agents/*/`, `heartbeat/`, `memory/`、`.graphify-*` JSON 等），`openclaw-zero-token/` 内含 node_modules 类依赖 → 收口时优先排查。
6. **git ahead 25** 未推送（10-20 之后累计）→ 白天收口。

---

## 2. 核心结论

- **备份链路持续绿**：10-25 / 10-26 备份连续 5 天，无停服热备份；唯一缺陷是 `/mnt/h 98%` 容量告警。
- **版本面**：运行 2026.10.5，最新 2026.10.7；按纪律不采纳 beta。
- **AMAT 双通道成功** = 10-26 最大修复成果；news digest 也恢复到 Gmail 通道。
- **工作区脏 → 最需要白天收口**：579 untracked + 25 unpushed 是最大风险点（备份链路本身没问题，备份包已含工作区快照，但无 git 收口前 git-only 恢复会缺这 579 文件）。

---

## 3. 明日（白天）建议动作

1. **白天收口**：commit/push 579 untracked + 25 unpushed（优先 `agents/`、`heartbeat/`、`memory/`）
2. **Gateway CPU 148%** 复核（pid 497240，uptime 1:51，判断是否事件循环劣化 vs 稳态满载）
3. **Gateway CPU 148% 告警复核**：watchdog 只报 RSS>6GB / CPU>80% ，若 80-150% 稳态运行属正常，建议把 CPU 告警阈值上调到 150%+
4. **backup.sh 修复**：
   - 加 `--exclude='*/.memory-write.lock.lock'`
   - 核查 RETAIN_DAYS=30 真正清老归档（39 份未清）
   - 备份盘空间告警：考虑把 RETAIN_DAYS 降到 14 天，或先手动清理 9 月前归档（先评估）
5. **升级评估**：2026.10.7 (10-24)；按纪律不采纳 beta
6. **AMAT 次班次（10-27 05:00）核验**：确认双通道稳定性（是否单次成功）

> **未执行说明**：本场为 NightOps 观测与上报窗口（01:15–01:30），全程只读（git / ls / grep / cat）；未做任何配置修改、未安装 npm 包、未触发重启。变更留待白天人工窗口。
