# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:** Zhiping Wu
- **What to call them:** ZP
- **Pronouns:** _(optional)_
- **Timezone:** Asia/Shanghai (CST, UTC+8)
- **Notes:** 运维重度用户；自建 OpenClaw 多 agent 体系（main/orchestrator/scout/coder/life/finance/health/work）

## Context

### 语言（明确要求）

- **默认用中文回复。** 2026-10-03 明确质问"你为什么不说中文"；2026-10-19 再次要求"记住尽量用中文回复"。
- 技术名词（provider 名、model id、命令、文件路径）保留英文原样，解释与结论用中文。
- 不要因为首轮用英文问候就整场英文。

### 沟通偏好（多轮对话已验证）

- **偏好结构化**：状态表 + 短句 + 优先级编号。
- **不要"请示才动"**：能安全自证的修复直接做完并汇报，别先问一遍再动手。
- 但**配置 / 调度器类改动要先看现状**，改动前保留合并原值（AGENTS.md Red Lines）。
- 不接受"看起来像证据"的推断；要求可复现实测（毫秒延迟、HTTP 状态码、进程 RSS 等）。
- 深夜排障场景回复要**短、直接、敢决断**，少用表格装饰和大段 emoji。
- v3 规则（用户已主动接受）：**不要替他动 systemd**，他自己终端跑 `/restart`。

### 当前生活事项

- 2026-10-03 起在**银川**出差 3 天（宁夏）。行程偏历史人文线：西夏陵、贺兰山岩画、镇北堡西部影城、中卫沙坡头、宁夏博物馆；吃手抓羊肉、羊肉小揪面、八宝茶。
- 银川昼夜温差 10–15°C，沙漠行程需防晒 + 薄外套。

### 运维环境

- WSL2 (linux 6.6.87.2-microsoft-standard-WSL2) + Windows 宿主 + NAS 上的 LiteLLM 代理。
- Gateway 由 systemd user unit `openclaw-gateway.service` 管理。
- 仓库：github.com/zpzpzp72/openclaw-backup-scripts（工作区即该仓库）。

---

_每次 session 后回头补充。_
