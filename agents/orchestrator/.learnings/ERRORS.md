# Errors

Append structured entries:
- ERR-YYYYMMDD-XXX for command/tool/integration failures
- Include symptom, context, probable cause, and prevention

## ERR-20260724-001: System falsely flags ls metadata as error + premature NightOps check
- **Symptom**: Multiple error signals `[exec] ls: cannot access '[REDACTED]': No such file or directory` — not real errors; also (Command exited with code 2) when checking next-day-brief-07-24
- **Context**: 03:30 AM heartbeat, checking for next-day-brief-07-24 before NightOps scheduled time (04:50)
- **Probable cause**: 
  1. System falsely flags `ls` metadata header lines as errors (same pattern as ERR-20260722-003, ERR-20260723-001/003/005)
  2. next-day-brief-07-24, coder-review-07-24, content_plan don't exist yet because NightOps hasn't run (we're at 03:30 AM, scheduled for 04:50)
- **Prevention**: Only check for next-day outputs after the scheduled NightOps time (04:50); before that, files won't exist yet
- **Resolution**: This is a system false positive + premature check; no action needed. Will recheck at/after 04:50 NightOps

## ERR-20260724-002: System ENOENT false positive - Scout/Life workspace missing
- **Symptom**: Error signal `[read] ENOENT: no such file or directory, access '[REDACTED]'` — not a real error
- **Context**: 06:00 AM heartbeat, system detected ENOENT when reading Scout/Life workspace files
- **Probable cause**: Scout/Life/Health Agent workspace directories genuinely don't exist in `workspace/agents/` — this was already confirmed at 03:01 AM and documented in Phase 1 at 05:30 AM
- **Prevention**: This is a system false positive that matches a real situation (workspace missing); already documented in memory/2026-07-24.md and pushed to Main at 05:30
- **Resolution**: Already handled — P0 pushed to Main at 05:30; no new action needed

## ERR-20260724-003: Recurring system false positive exec metadata error (7th occurrence)
- **Symptom**: Error signal `[exec] -rw-r--r-- 1 zhiping zhiping 850 Jul 24 04:41 [REDACTED]` — not a real error
- **Context**: 07:00 AM heartbeat (system timestamp: 7:00 AM, heartbeat header showed 6:30 AM stale)
- **Probable cause**: System falsely flags `ls -lt` metadata header line as error; path redacted by system; actual data is legitimate file timestamp showing Coder code_report (Jul24 04:41) — unchanged since 05:30 check
- **Prevention**: This is a system false positive; confirmed at 06:30 and 07:00 checks that Coder code_report (Jul24 04:41) is unchanged
- **Resolution**: No action needed; data confirmed unchanged at 06:30

## ERR-20260724-004: System false positive exec metadata error (8th occurrence)
- **Symptom**: Error signal `[exec] -rw-r--r-- 1 zhiping zhiping 850 Jul 24 04:41 [REDACTED]` — not a real error
- **Context**: 19:00 heartbeat check
- **Probable cause**: System falsely flags `ls -lt` metadata header line as error; path redacted by system; actual data is legitimate file timestamp showing Coder code_report (Jul24 04:41) — unchanged since 05:30
- **Prevention**: Pattern matches ERR-20260721-001, ERR-20260722-001/002/003/004, ERR-20260723-001/003/005, ERR-20260724-003 — system-level false positive
- **Resolution**: No action needed; data confirmed unchanged

## ERR-20260725-001: sed delimiter conflict with forward slashes in replacement string
- **Symptom**: `sed: -e expression #1, char 192: unknown option to 's'`
- **Context**: 01:30 heartbeat, updating HEARTBEAT.md Phase 2 trackers with Scout/Life workspace rebuild
- **Root cause**: First sed attempt used `/` as delimiter, but replacement string contained `/` (in URLs/paths like `Scout/Life/Health`), causing sed to misinterpret the command
- **Fix**: Retried with `|` as delimiter instead — succeeded (`Done`)
- **Prevention**: When replacing text containing `/`, use `|` or `#` or `@` as sed delimiter instead of `/`
- **Resolution**: Already handled — retried with `|` delimiter, update succeeded

## ERR-20260725-002: awk command accidentally replaced entire file instead of single line
- **Symptom**: `awk 'NR==50 {print "*Next heartbeat: 2026-07-26 04:50 AM (NightOps)"}' file > tmp && mv tmp file` replaced entire HEARTBEAT.md with only line 50
- **Context**: 05:05 heartbeat, trying to update "Next heartbeat" line in HEARTBEAT.md
- **Root cause**: awk output redirection replaced the file before awk started, resulting in an empty file being moved into place
- **Fix**: Restored HEARTBEAT.md from scratch by rewriting the entire file
- **Prevention**: Use `sed -i` or `head/tail` with proper line selection, or use a temp file with a different name than the target
- **Resolution**: HEARTBEAT.md fully restored with all Phase 2 tracker data intact

## ERR-20260726-001: sed delimiter conflict with newlines in replacement string
- **Symptom**: `sed: -e expression #1, char 130: unknown option to 's'`
- **Context**: 05:03 heartbeat, updating HEARTBEAT.md Next heartbeat and Last updated lines
- **Root cause**: Replacement string contained newline character `\n` and the pattern also contained `/` (in "NightOps 第15夜完成"), causing sed to misinterpret after the first `/` delimiter
- **Fix**: Switched to `#` as delimiter (`sed -i 's#pattern#replacement#'`) — succeeded
- **Prevention**: When replacement contains `/` and newlines, always use alternate delimiter (`#`, `|`, `@`)
- **Resolution**: Update succeeded using `#` delimiter

## ERR-20260726-001: sed "Invalid preceding regular expression" - backslash in replacement
- **Symptom**: `sed: -e expression #1, char 229: Invalid preceding regular expression`
- **Context**: 06:30 heartbeat, updating HEARTBEAT.md Kimi K3 tracker from "2d倒计时" to "1d+" in Phase 2
- **Root cause**: The replacement string contained `\*\*` (escaped asterisks) which confused sed's regex engine — the double asterisk `**` is not a valid regex quantifier without preceding token
- **Fix**: Removed escaped asterisks, used plain `**` in replacement string — succeeded
- **Prevention**: Don't escape asterisks that aren't regex quantifiers; plain text replacements don't need escaping
- **Resolution**: Phase 2 tracker updated to "1d+🔴 P0（07-27凌晨发布窗口）"

## 2026-09-03 sessions_send Agent-to-Agent Blocked
**Error**: `sessions_send` to `agent:main:main` → `forbidden: Agent-to-agent messaging is disabled. Set tools.agentToAgent.enabled=true to allow cross-agent sends.`
**Impact**: 无法主动推送 P0 警报给 Main（NighOps-Orchestrator streak recovery、Main NightOps 3x consecutive error）
**Workaround**: 记录到 memory log，等待 Main 主动联系
**Config**: `tools.agentToAgent.enabled` 需设为 `true` 才能跨 agent 发送

## ERR-20261107-001: 「SQLite session reclamation commit checkpoint expired」不是租约泄漏，是 5s 提交授权超时
- **Symptom**: `AgentDatabaseAdmissionError` / `reason: SQLite session reclamation commit checkpoint expired`，每分钟 `Cron maintenance failed` + `sessions.describe UNAVAILABLE`，target=main 成片失败
- **Context**: 11-05 起持续；此前误判为「agent_database_leases 租约泄漏 → 需 doctor --fix」
- **Root cause**: `dist/session-accessor.sqlite-reclamation-commit-BX3N0u2L.mjs` 中 `COMMIT_DECISION_TIMEOUT_MS = 5e3`。
  回收 worker 申请提交授权，同进程同步写入者需在 5s 内执行 `Atomics.compareExchange(shared,0,REQUESTED,COMMITTING)`，
  否则抛 "checkpoint expired"。main 库 272MB（transcript_events 99MB + trajectory_runtime_events 68MB），
  回收事务持写锁 > 5s → 必然错过窗口。**与 lease 是否 stale 无关**。
- **Prevention**: 遇到该报错，先查 `agent_database_leases` 的 owner_pid/owner_start_time 是否等于当前进程（是则非 stale），
  再比对各 agent 库体积与 transcript 行数。**重启 Gateway 不能解决**（无 stale lease 可清）。
  有效手段：`openclaw doctor --session-sqlite compact --session-sqlite-agent <id>`（需停机）+ 提高 `--max-old-space-size`。
- **Verification**: `openclaw doctor --session-sqlite inspect --session-sqlite-all-agents` → 8 agent 全 0 issue；
  `PRAGMA integrity_check` = ok → 库未损坏，是时序问题

## ERR-20261107-002: 外部 sqlite3 / python sqlite3 不能直接读 OPENCLAW_STATE_DIR 下的库
- **Symptom**: `external sqlite3 cannot open databases under the active OpenClaw state directory. Use OpenClaw commands for live state, or inspect a private backup copy outside OPENCLAW_STATE_DIR.`
- **Context**: 想直接查 `agent_database_leases` 表定位 P0-2
- **Root cause**: OpenClaw 对活动 state 目录做了只读隔离保护，防止外部进程绕过其写入层
- **Prevention**: 先 `cp` 到 `/tmp/xxx/` 之外的私有副本再查（如 `cp ~/.openclaw/state/openclaw.sqlite /tmp/diag/state.sqlite`），
  用 python `sqlite3.connect('file:...?mode=ro', uri=True)` 打开副本；**不要**用 `sqlite3` CLI 直接开原库。

## ERR-20261107-003: 原生备份输出目录不能位于 ~/.openclaw 内
- **Symptom**: `Backup output must not be written inside a source path: /home/zhiping/.openclaw/backups/native is inside /home/zhiping/.openclaw`
- **Prevention**: `openclaw backup create --output` 指向 ~/.openclaw 之外（如 `~/openclaw-backups`）。

## ERR-20261107-004: orchestrator main 会话上下文溢出导致 turn 反复中断
- **Symptom**: `400 invalid params, context window exceeds limit (2013)` / `compactionTokens=204801` / `providerPayloadBytes=781332`，
  随后 `lane task error: agent run superseded by a newer session writer` → 触发 main-session-restart-recovery → 再次溢出，循环
- **Prevention**: orchestrator:main 累积到数百条消息后需 `/reset` 或 `/new`；不要在一个会话里无限追加长文件读取结果

## ERR-20261107-005: error-detected 反复把「我读到的文件内容 / 我执行的命令回显」误判为工具错误
- **Symptom**: 连续多轮 `<error-detected>` 报出 `[exec] === lock file stat === ...`、`[exec] === cron authority lock investigation ...`、
  `[read] To: [REDACTED] Subject: OpenClaw 备份完成 ...`、`[read] # Errors Append structured entries ...` 等
- **Context**: 03:02 / 03:14 两轮恢复轮的 error-detected 段
- **Root cause**: 这些不是工具失败，而是 **exec 输出与 read 内容本身**（命令回显、被读文件的前几行）被系统当成错误信号提取。
  同 ERR-20260724-001/003/004 一类。真正的失败（如 ERR-20261107-003 的 backup output path）在原始 exec 返回里已明确给出。
- **Prevention**: 判断「工具是否失败」要看 exec 的 **exit code / status**，而不是 error-detected 段里出现的文本；
  出现在 `=== ... ===` 后的内容一律是命令回显。已再次确认本轮 3 条信号全为假阳性，无需重跑对应动作。

## ERR-20261107-006: 长任务的完成通知会迟到，抵达时工作早已完成 —— 不要因此重跑
- **Symptom**: 03:27 时收到 `Exec completed (grand-sh, code 0)`，但该 exec（`timeout 900 openclaw backup create`）
  的归档早在 03:27 就已生成并验证完毕；通知本身在 03:50 才抵达
- **Context**: 03:15 前台跑备份 → 归档生成于 03:27 → 03:27 我已 collect 到结果 → 03:50 才收到 completion 通知
- **Root cause**: exec 的 completion 通知与结果采集是两条独立通道，通知可延后送达
- **Prevention**: 收到迟到通知时，**先按路径/时间戳核对产物是否已存在**（本例：两个 .tar.gz、无 staging 残留、
  0 个遗留 backup 进程、service Result=success）→ 确认无重复无残留后**不重跑**。
  重跑会白白再写 6.7GB 且可能与 timer 撞车。

## ERR-20261107-007: 被杀掉的 nohup 运行会在日志里留下「只有 start、没有 done」的孤儿条目
- **Symptom**: `native-backup.log` 里出现 `[03:33:03] === native backup start ===` 之后**没有**对应的
  `=== native backup done ===` / `✅ verify OK`；而 03:36 那次（systemd 托管）两条齐全
- **Root cause**: 03:33 那次用 `nohup ... &` 挂在 exec session 下，session 结束时进程被连带 kill，
  只留下了 staging 目录（`.openclaw-backup-publish-*`），没有归档
- **Prevention**: 判断一次备份运行是否完整，看日志里 **start 与 done 是否成对**；
  出现孤儿 start = 该次运行被中断。清理判据：
  ① 无 `.openclaw-backup-publish-*` 残留 ② 归档数与成功次数一致 ③ 无遗留 backup 进程
- **注**: 脚本本身对 >1 天的残留 staging 目录会自动 `rm -rf`（见 native-backup.sh 开头），但被中断的当次需手动清

## ERR-20261108-001: 邮件失败被误判为网络问题 —— 实际是 SMTP 授权码失效
- **Symptom**: NAS 备份脚本 `send_mail` 连续多天 `❌ 发送失败: Connection unexpectedly closed`
- **Context**: 11-08 03:00 夜间巡检；此前日志里也混有 `Temporary failure in name resolution`
- **Root cause**: **不是网络**。DNS/TCP/TLS 全部正常（smtp.qq.com:587 STARTTLS 成功，TLSv1.3 证书校验 OK），
  但 `AUTH PLAIN` 后服务器回 **535 Login fail** → QQ 邮箱 SMTP 授权码已失效/被限制
  → smtplib 把 535 包装成 `SMTPServerDisconnected: Connection unexpectedly closed`，**错误信息误导**
- **Prevention**: 遇到 "Connection unexpectedly closed" 不要直接归因网络。用 `s.set_debuglevel(2)` 抓 SMTP 会话，
  看服务器**实际返回码**（235/535/550/554）。535 = 凭证问题，与网络无关
- **附带问题**: 脚本 `send_mail` 原先只重定向 stderr，而 send_email.py 的成败详情 print 到 stdout
  → canonical 日志只剩上层「已发送」，看不到「❌ 发送失败」，断链 3 天无人察觉（11-08 已修为整体捕获 stdout+stderr）

## ERR-20261108-002: 9p(SMB) 挂载上 `du` 会挂起，统计目录体积必须逐文件 stat
- **Symptom**: `du -sh /mnt/h/#recycle/...` 长时间无输出（>4 分钟），命令被 timeout 杀掉
- **Context**: 统计 NAS 回收站体积以评估可释放空间
- **Root cause**: /mnt/h 是 9p(drvfs) 挂载，`du` 需要反复 stat+readdir，SMB 延迟叠加导致极慢
- **Prevention**: 在 9p/SMB 挂载上**禁止用 du 统计目录体积**；改用
  `for f in <glob>; do stat -c %s "$f"; done` 逐文件累加（27 份文件约 2 秒完成）

## ERR-20261117-001: 系统心跳的 scratch 存在数据库里，不是文件 —— 「缺 HEARTBEAT.md」是伪线索
- **Symptom**: health agent 的 `heartbeat-health` 每 30 分钟报 `SQLite session reclamation commit checkpoint expired`，
  而 work/finance 同样没有 `HEARTBEAT.md` 却正常 skipped
- **Root cause**: heartbeat scratch 存在 **state.sqlite 的 `cron_job_scratch` 表**（job_id → content），
  **不是** workspace 里的文件。health 的 scratch 与 5 个正常 skip 的 agent **完全相同**
  （244B comments-only 模板）。真正的差异是 **leases=0**
- **Prevention**: 判断心跳为何跳过/失败时，先查 `cron_job_scratch` 表，
  **不要**用 `ls workspace/agents/<a>/HEARTBEAT.md` 推断。
  `isHeartbeatContentEffectivelyEmpty`（heartbeat-nZ1C5oCa.mjs）只把空白/注释/标题/空列表项视为空。
- **附带**: skip 判定发生在**会话获取之后**，所以 DB 写不进去的 agent 在「本该 skip」之前就先炸

## ERR-20261117-002: system-owned monitor job 不能用 cron 客户端改
- **Symptom**: `openclaw cron disable heartbeat-health` → `Error: system-owned monitor jobs cannot be edited by cron clients`
- **Context**: job 的 `declarationKey = heartbeat:health`，由系统按 agent 自动生成（`doctor-heartbeat-task-migration` 负责同步）
- **Prevention**: 看到「关掉某个心跳」的建议前，先确认它是否 system-owned：
  `select declaration_key from cron_jobs where name=?`；非空且形如 `heartbeat:<agent>` 即系统所有。
  可改的替代路径 = 停 Gateway 后 `doctor --fix`，或改 agent 配置本身

## ERR-20261117-003: cron_jobs 表的主键列名是 job_id，不是 id
- **Symptom**: `sqlite3.OperationalError: no such column: id`（查 cron_jobs）
- **Root cause**: `cron_jobs` 的列是 `store_key, job_id, declaration_key, owner_agent_id, name, ...`，
  **没有 `id` 列**。而 `cron_job_scratch` 表用的才是 `job_id`（两表靠 job_id 关联）
- **Prevention**: 查 cron_jobs 前先 `PRAGMA table_info(cron_jobs)`；
  心跳 scratch 的正确查法是 `select job_id, content from cron_job_scratch`，
  再用 `cron_jobs.job_id` 关联出 job 名与 agent

## ERR-20261128-001: sessions_send 的 accepted/queued 不等于已送达 —— 11-17 我误判过一次
- **Symptom**: 11-17 我给 main 推送 P0 后，返回 `status: accepted, targetDisposition: queued`，
  我据此在报告里写「投递验证：main 的 DB mtime = 03:44:29 → 消息确已落盘」
- **实际情况**: 11-17 04:02 收到 inter-session 消息：
  `sessions_send delivery to agent:main:main failed: aborted. The target may not have received the message`
  → **消息根本没送达**；03:44:29 的 DB 写入很可能是我自己那条 `sessions_list(agentId=main)` 造成的
- **Root cause**: `accepted / queued` 只表示**投递请求被接收**，真正的 delivery 状态在
  `delivery.status` 字段里（本例为 `pending`）。把它当成送达 = 误报
- **Prevention**:
  1. 读 `delivery.status`；只有 `delivered`/`confirmed` 才算送达
  2. 不要用「DB mtime 变了」当送达证据 —— 那只能证明**有写**，不能证明**是这条消息的写**
  3. 要么等对端回执，要么在消息里要求对方回一条 ack，再据此确认
