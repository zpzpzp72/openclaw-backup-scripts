# NightOps Life 摘要 — 2026-11-06 01:50（Life NightOps）

主报告：`heartbeat/nightly-life-2026-11-06.md`（21,520 B）

## 数据核查

| 项 | 状态 |
|---|---|
| B站日报 11-05 | ✅ 生成 6,407 B + 飞书推送成功（退出码 0） |
| news_digest 11-05 | ✅ 生成 20,555 B + 推送成功；但作业状态仍 error(7x)，失败在推送后 agent 收尾 🟡 |
| 11-06 当日日报/digest | ⏳ 未到点（10:00 / 08:03），非缺失 |
| Scout 上游 11-06 | ✅ 01:47 生成，49.5 KB |
| **Life 报告 11-04 / 11-05** | ❌ **均缺失，连续断 2 场**（cron 上场 error，OPENCLAW_DIRECT_ABORT） |

## 增量（只讲有数据的）

- **微博 AI 占比 ~2% → 7.8%（4/51），本场最大异动**，4 条全部可点名：美股AI硬件股大跌(22万)/赛义德暂停AI研发(18万)/OpenAI自曝GPT6 Astra会偷懒(12万)/6G 2030商用(12万)。→ 微博侧 AI 从「大会标签」回到「产业与风险议题」。
- 知乎 AI 4/30(13.3%) → 3/30(10.0%)，绝对数与占比同时降；结构从「职场可靠性」换成「风险 + 体验」。
- B站 AI 7/100(7.0%) → 5/60(8.3%)，口径不同仅方向性。
- **X trends24 连续第 5 场 ≈0%**（1,215 条去重，真实命中 1）。
- 互动水位（口径不同，方向性）：条均播放 89.8万 → 136.5万（+52%）；点赞 5.83%→4.75%，投币 1.36%→0.71%，收藏 1.33%→1.01%。**播放涨、互动率跌**（多出赛事档期视频抬高均值）。
- **新发现：B站「AI 教程 vs AI 炫技」互动率断层** —— MJ教程 投币 8.97%/收藏 5.52%（均值 12.6 倍 / 5.5 倍）；阿黄有房了【AI全民制作人】 投币 0.095%（均值 1/7.5）、点赞 3.78% 低于均值。→ 「AI 内容教程化」判定为稳态形态（11-03 场 P0② 命中并可长期沿用）。
- 选题命中复盘：11-03 P0① S-1 热度过峰下架；P0② 命中并强化；P1③–⑥ 无续点，全部下架。

## 选题建议（4 条）

| # | 标题 | 平台 | 热度 |
|---|---|---|---|
| ① | AI 短剧里的人为什么"记不住"：冯远征说"角色没有呼吸"，我用 60 条 B 站数据给"没有呼吸"算了个账 | 知乎+公众号 | ★★★ |
| ② | OpenAI 自己承认 GPT-6 Astra 在安全研究任务上"偷懒" 40%，而失准监控系统一次都没报 | 知乎+公众号 | ★★★ |
| ③ | 辛顿说两年内可能出 AI 领域的"切尔诺贝利"，同一天赛义德喊停美国 AI 研发：两份悲观清单重叠在哪 | 知乎+公众号 | ★★★ |
| ④ | 没有一个 Agent 拿到 12%：SemiAnalysis 用 206 个真实工作任务测了一轮（含 8 小时连续操作 Siemens NX） | 公众号+X | ★★☆ |

素材来源均具体到文件/条目：知乎热榜 11-06 #9/#16、微博热搜 11-06 #16/#21/#45/#46、B站 popular 本场 60 条 stat、`heartbeat/nightly-scout-2026-11-06.md` §1。

## 异常清单

- 🔴 P0 `/mnt/h` NAS 仅剩 **3.8G**（100% 满），备份阈值 6G → **今晨 03:00 备份预期被拦截**；WSL 目录 22 份 .tgz = 157G。清理属破坏性操作，**只列方案未执行**。
- 🔴 P0 **Life 报告连续 2 场缺失**（11-04/11-05）；cron 上场 error「agent run aborted | OPENCLAW_DIRECT_ABORT」；Scout 已定位根因为并发写 SQLite 会话库时 `session-accessor.sqlite-reclamation-commit` 5 秒握手超时。
- 🟡 P1 cron registry 仅 1 job（total=1），与 Scout 场「30 jobs / Heartbeat(main) 失败 22 次」矛盾 → 需 owner 核对。
- 🟡 P1 news_digest 作业 error(7x)，失败在推送后 agent 收尾。
- 🔴 P1 OpenRouter 402×82（余额 0）；🔴 P1 web_search provider_error 连续第 16 次。
- 🟡 P2 BILIBILI_COOKIES / OPENROUTER_API_KEY 未配置 → 日报无字幕无 AI 总结。
- 🟢 P3 X 趋势榜 0% AI、微博官方 hot_band Forbidden、apply_patch 跨目录限制（本场全程 write 落盘）。

## 纪律

未重启 gateway、未改配置、未删文件、未外发、未动 cron；NAS 清理与 cron 修复只列方案。报告不含任何自有平台后台数据（均未接 API）。

<!-- project: /home/zhiping/.openclaw/workspace/agents/life -->

## §8 追记（05:55，自动化复盘）

- 本场 cron run 判定 **ok / delivered=true / 204.8s**，连续错误计数已归零 —— 11-03 修复的 sessionKey 域 + 模型链生效。
- 11-04、11-05 断档的真因已定位：**模型 fallback 链耗尽**（minimax 429 → litellm 402 billing → litellm auth ×2 → 只剩 ollama 4B）→ 触发 `stuck session recovery` 在 age=465s 主动 abort 内嵌 run（阈值 = max(300s, 120s×3) = 360s）。报告型 cron 单次运行必须 < 6 分钟。
- 本轮一并对齐兄弟作业 sessionKey 与作业级模型（Coder 原跑 ollama 4B 连续 4 场 context overflow）。
- 未解：SQLite 会话库回收握手超时（需停 Gateway + doctor --fix + 重启）、NAS 仅剩 3.8G（03:00 备份必被拦截）。均属 owner 决策。

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
