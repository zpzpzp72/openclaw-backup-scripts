# Tomorrow_Action_Plan — 2026-10-20

## ⚠️ 最高优先级：网络恢复

- **[P0]** 检查 WSL2 网络状态：`wsl --shutdown` 重启 / 检查 DNS 配置
- **[P0]** 确认网络恢复后手动触发 news-digest 重试（Scout）
- **[P0]** 验证飞书 webhook/announcement 是否恢复正常投递

---

## 系统恢复

- **[P1]** 手动运行一次完整 NightOps 确认各 agent 输出
- **[P1]** 检查 heartbeat 状态：5个 agent heartbeat 是否全部 `running`
- **[P1]** 确认 backup-cron DNS 问题是否已随网络恢复而解决

---

## 待重建节奏（7天未 NightOps）

- **[P2]** Coder / Life / Finance / Health — 各自补发近况简报
- **[P2]** 重建 NightOps 日志节奏（Orchestrator 每晨 04:50）
- **[P2]** 回顾 2026-10-12 ~ 10-18 期间遗漏的行业动态（Scout）
