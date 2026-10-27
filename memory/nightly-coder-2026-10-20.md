# Coder NightOps 记忆条目 — 2026-10-20

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
<!-- Night #78 Coder slot · 2026-10-20 22:20 CST · 回写 heartbeat/nightly-coder-2026-10-20.md -->

## 事实沉淀（可 recall）

### 1. OpenClaw 版本面已稳定追平
- 二进制 / gateway self / npm latest 三方一致 = **2026.10.5 (1b58cb9)**
- dist-tags: latest 2026.10.5 | extended-stable 2026.9.33 | beta 2026.10.10-beta.2
- 连续第 2 夜无待装升级；**不要主动采纳 beta**

### 2. Node 双版本分裂（P0，已确证，非猜测）
- shell `node -v` = **v24.15.0**（PATH 命中 nvm 默认/系统版本）
- gateway 进程内 node = **v26.10.0**（nvm 显式启动，status OS 行显示 node 26.10.0）
- 影响：openclaw-backup.sh、news-digest、bilibili、amat 等**全部走 shell 的 cron 都会取到 v24**
- 处置建议（二选一）：shell PATH 切 v26；或确认最低要求后写入 AGENTS.md

### 3. security audit 已实跑并量化（本场首次）
- **3 CRITICAL**：`models.small_params`、`security.exposure.open_groups_with_elevated`、`..._runtime_or_fs` / `..._control_plane_tools`
- **8 WARN**：tools.sessions.visibility=all + agentToAgent 无 allowlist、8 个 unpinned npm specs、openclaw-weixin 缺 integrity、Feishu groupPolicy=open、Feishu doc create 可授予权限、trusted_proxies_missing、multi_user_heuristic
- 根因单一：**Feishu groupPolicy=open + tools.elevated=enable + 小模型(MiniMax-M3)** 三者叠加
- 修复主路径：`channels.feishu.groupPolicy="allowlist"` + `groupAllowFrom` 白名单

### 4. CI/CD 结论
- `zpzpzp72/openclaw` fork 的 Actions **事实停摆**：最新 run 停在 2026-09-28（stale 22d），10/09→10/19 大升级期间零新 run → 疑似 Actions 在 fork 上被禁用或未 watch upstream
- `zpzpzp72/memory-lancedb-pro` CI 最后一次 **failure @ 2026-05-05**，~168 天未处理且插件仍在生产启用 = 当前唯一真·代码红灯
- `openclaw-backup-scripts` / `openclaw-zero-token` / `amat-stock-report` 无任何 workflow run（干净信号）

### 5. 仓库已无活跃开发
- `~/.openclaw/workspace` HEAD = a72f94f (2026-09-07)，**43 天无代码提交**
- 与 origin/feature/hot-backup **零差异**（0 unpushed）
- 陈旧 PR：#4 (194d, 与已合入 STOP_GATEWAY 重复，建议关) / #2 (185d, tar 前 10s wait 待评估)
- drift: 8 M / 1 D / 89 untracked（正常夜间 churn，但接近收口临界点）

### 6. 备份链路
- 归档目录实际路径 = **`/mnt/h/AI/openclaw.zone/WSL`**（脚本 BACKUP_DIR），非 `~/.openclaw/backups`
- 最新 `openclaw-20261020-0300.tgz` = 8.54 GiB；10 月共 16 份齐全
- 归档本身成功；**失败的是事后飞书通知**（连续 3 条 `Connection unexpectedly closed`）
- `openclaw status` 仍报 `Backups: last ok 19d ago` → **metadata 刷新 bug**，第 2 夜延续，不要据此判断备份失败

### 7. 已定性的失败项
- **Heartbeat delivery route**：8 个 job（main/coder/finance/health/life/orchestrator/scout/work）全 "waiting for delivery route"，占位 `telegram:123456789` 未替换。telegram 已 enabled=false，实际通道是 Feishu（chat_id oc_f54afb4bc...）→ 第 19 夜携带
- **AMAT cron**：根因明确为 `[amat-feishu] [feishu_push] 获取 token 失败`，**不是**邮件通道问题（邮件 attempted 正常）
- **memory 中「AMAT cron 长期停摆」的记忆条目可更新为更精确版本**

### 8. 健康子系统
- News digest cron 🟢（2026-10-20 08:01 Feishu 上传成功，file_key + message_id 均返回）
- cron 注册表 11 条齐全，@reboot cron-watchdog 在位
- openclaw-weixin 通道 ON/OK，但插件缺 capability consent

## 明日（白天）优先动作

1. 解决 Node 版本分裂（shell v24 vs gateway v26）
2. memory-lancedb-pro：修 CI 或临时降级插件（168 天红灯）
3. Feishu groupPolicy 收紧为 allowlist（可一次性消掉 3 CRITICAL 的主因）
4. 把 heartbeat delivery route 从占位 telegram 改为 Feishu chat_id
5. workspace 89 个 untracked 一次性 commit 收口；关闭重复 PR #4

## 未执行说明

本场全程只读（git / gh api / openclaw status|doctor|security audit / crontab -l / ls）。未做任何配置修改、未安装 npm 包、未触发重启 —— NightOps Coder 角色定位为观测与上报，变更留待白天人工窗口。
