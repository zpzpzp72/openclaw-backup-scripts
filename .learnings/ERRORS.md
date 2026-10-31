# ERRORS / 运行备忘

> ⚠️ **只追加,不要整篇覆盖**。本文件是跨 session 的累计教训库。
> 新增条目请用 `cat >> .learnings/ERRORS.md <<'EOF' ... EOF` 追加到文件末尾,
> 或在编辑时保留既有全部内容。
> 历史事故:2026-10-30 02:45 orchestrator NightOps 整篇覆写,246 行仅剩 16 行,
> 已由 git 历史恢复。若再次发生,请检查是否有 agent 用 write 覆盖而非追加。

## 本轮遇到的错误与处置

1. **exec: 外部 sqlite3 被拒开活跃 state DB（沙箱保护）**
   - 触发：`sqlite3 state/openclaw.sqlite` 直接查询
   - 处置：工具层保护，属预期；改用 `openclaw` CLI（如 `openclaw models status`）或复制 DB 到非 state 目录再查

2. **bash: `2>/summary` → Permission denied**
   - 触发：想写 `2>/dev/null`，误写成 `2>/summary`，stderr 被重定向到一个不存在的可执行文件
   - 处置：修正拼写重跑即可；报错貌似权限问题，实为拼写问题

3. **read 路径手误**
   - 触发：读不存在的文件（如 `heartbeat/nightly-coder-2026-10-24.md`、`agents/scout/memory/2026-10-25.md` 不存在）
   - 处置：利用 read 报错的 "Did you mean:" 候选列表定位真实文件，比 find 更快；据此确认 coder 无 10-24 场、最新为 10-25，orchestrator 最新 daily 为10-24

4. **`openclaw agent exec` 参数错误**
   - 触发：`--thinking adaptive` 不被 MiniMax-M2.7 支持（合法值 off/minimal/low/medium/high/ultra）；`--agent` flag 不存在（agent 名为位置参数）
   - 处置：按报错提示改为合法参数重试；agent 通路验证更可靠的方式是看会话是否真实落盘产物（今夜 coder 02:20、orchestrator 02:40 均已落盘，通路健康）

## 通用注意
- 读文件优先用 read 工具（bash cat 长行会连行，read 报错自带候选提示）
- 探测 provider 用 `openclaw models status` 看 effective/cooldown，勿用配置里的占位符字面量

## 2026-10-25 诊断「配置不对」类问题：必须读 dist 判定函数，别靠猜

**现象**：`openclaw gateway status` 报 3 条 service config issue（PATH 缺 pnpm/bin、PATH 含版本管理器、ExecStart 用版本管理器 node）。

**误差点**：差点直接手写一个「看起来合理」的 PATH 去改 unit。

**正确做法**：
1. `grep -rl '<报错原文>' ~/.nvm/versions/node/v26.10.0/lib/node_modules/openclaw/dist` 定位判定函数（本次在 `service-audit-D-KyNX3q.mjs` 的 `auditGatewayServicePath` / `auditGatewayRuntime`）
2. 读清它比对的是哪两个集合（expected = `getMinimalServicePathPartsFromEnv()` 最小集；actual = unit 里的值）
3. 用 openclaw **自己的函数**算出期望值（`node -e import(...dist/service-env-*.mjs)` 直接调 `getMinimalServicePathPartsFromEnv`），不要手拼
4. 改完只 `daemon-reload`，不重启 → 用 `openclaw gateway status` 复跑验证（判定读的是 unit 文件，不需重启即可验证）

**通用规律**：任何「openclaw 说我的配置不对」的问题，报错文本都能在 dist 里 grep 到判定函数。**先定位判定逻辑，再动手**。

## 2026-10-25 后台 sudo / 长时间 cp / 阻塞式 message send 三类操作踩坑

1. **后台脚本里 `sudo` 会阻塞**：`sudo` 在无 TTY 的 setsid/nohup 下等密码 → 脚本卡住。必须写 `sudo -n`，并用 `sudo -n true` 先验。
2. **exec 工具会打断长时间前台命令**：`cp -a` 整个 node 目录（88500 文件）必被超时打断，留下半截目录。**只复制需要的单个文件**（本次只 cp `bin/node` 一个二进制），后台 + `sudo -n`。
3. **`openclaw message send` 是长连接阻塞**：前台执行会被工具超时打断，看起来像失败。**改用 `sessions_search` 查目标群会话**，确认消息是否落地。
4. 验证 `doctor --lint` 之类的长命令时，用 `setsid nohup ... > file 2>&1 </dev/null &` 再单独 `cat` 文件读结果，不要在前台等。

## 2026-10-25 Code Mode 里误用 `tools.*` → ReferenceError: tools is not defined

**现象**：在 `exec` 的 Code Mode 里写 `await tools.sessions_history({...})` → `ReferenceError: tools is not defined`。

**原因**：Code Mode 的可用函数是**全局直接调用**（`sessions_history(...)`、`sessions_search(...)`、`sessions_list(...)`），没有 `tools` 命名空间。`tools` 只是给「读 prompt 里的工具声明」用的描述性名字，不是运行时对象。

**正确写法**：
```js
const h = await sessions_history({ sessionKey: "...", limit: 6 });
text(JSON.stringify(h).slice(0, 2000));
```

**规律**：Code Mode 里 `exec`/`read`/`write`/`apply_patch` 是全局函数；`catalog.search()` 用于找**未在声明里列出**的工具。写完立即报 ReferenceError 就说明多了个 `tools.` 前缀。

## 2026-10-25 修 `~/.local/bin/node` 前必须先查「谁依赖它」

**现象**：`openclaw` 报 `current Node failed runtime admission`，直觉以为 nvm 的问题。

**真实根因**：`~/.local/bin/node` 是 **v24.15.0**，比 openclaw 底线 `>=24.16.0` 低 0.1；它在 PATH 第 1 位，每次都被 launcher 拒。

**替换前必查项（这次都查了，结论：安全）**：
1. `grep -rl '<绝对路径>' ~/.bashrc ~/.profile ~/.openclaw/openclaw.json` → 无引用
2. `grep -l 'env node' ~/.local/bin/*` → 只有 corepack，而它**替换前就坏**（依赖 `./lib/corepack.cjs` 已不存在）
3. `npm config get prefix` = `/home/zhiping/.local` → 确认 `~/.local/lib/node_modules` 里的 native 模块是否 ABI 绑定
4. pnpm 实际在 `~/.npm-global/bin`（**不同 prefix**）→ 不受影响

**做法**：不删原件，`mv node node-v24.15.0.bak` + `ln -sfn` 新目标 → 一条 `mv` 即可回退。

**通用规律**：动「用户 PATH 里的默认 node」之前，先做上面 4 项；`npm config get prefix` 常常和直觉里的位置不一样。

## 2026-10-27 备份脚本:一封失败的邮件静默吃掉整条后处理链

**现象**:旧备份自 2026-07-31 起再未清理(堆积 40 份、NAS 98%),心跳 `last_backup` 永远指向上一档,每份备份仍是 8.9G。三个现象看起来是三个独立 bug。

**真相:同一个根因**。`send_mail` 发送 completion email 失败返回非零 → 脚本 `set -e` → **整个脚本在此中止** → 其后的 `cleanup_old` 与最终心跳**从不执行**。

**定位方法(可复用)**:在日志里 grep「某个成功标志」的最后出现时间 —— 「备份完成邮件已发送」最后一条是 07-30,而「备份成功:」每天都有 → 中断点就在两者之间。**多个症状同时出现时,先找共同的上游失败点,别当成多个 bug 分别修。**

**修复要点(已落地 commit b52dd9fe)**:
1. `send_mail ... || log "⚠️ 已忽略"` —— **通知失败不得中断主流程**
2. `cleanup_old` 移到 `send_mail` **之前** —— 双保险
3. exclude 路径写错(`.openclaw/data/lancedb` 目录根本不存在,真实是 `.openclaw/memory/lancedb-pro`)→ 模式永不命中 → 每份打包 9.4G 向量库
4. 心跳 `last_backup` 用的 `LATEST_BACKUP` 是**备份前**解析的旧值 → 备份成功后要重新赋值

**通用教训**:
- `set -e` 脚本里,**任何可选动作(发邮件/通知)都必须 `|| true` 兜底**,否则一次外部服务抖动就会静默砍掉后续所有逻辑。
- **exclude/glob 模式要验证目标路径真实存在** —— 路径写错时 tar 不报错,只是静默不生效,体积异常是唯一线索。
- 「某现象这次没出现」≠「根因消除」(10-27 tar 退出码变 0 只是锁文件时序没撞上)。

**顺带**:用 heredoc 传 python 脚本改文件时,`\\n` 会被 shell 与 python 双重转义,导致字符串匹配失败(报 AssertionError 且**未写入任何改动**)。改用**逐行定位 + 精确行号重写**更稳;失败时先看 `diff` 确认「没改动」再重试,别重复同一写法。

## ERR-20261029-001 工具面在轮次中途收窄为只读,导致三项工作悬空

**现象**:同一轮内 `exec`/`write` 从 `function` 变成 `undefined`,`store` 报
`Code Mode store/load is unavailable in restart-safe cells`。探针返回可用但实际调用时已被回收。

**影响**:10-29 复盘、`memory/2026-10-29.md` 落盘、矛盾日志句 commit 均延后到下一轮。

**教训**:
1. 探针结果只代表**那一刻**,不保证后续调用可用 → 每轮首次写操作前重新探针
2. `store` 在 restart-safe cell 不可用 → 恢复后**先核实是否真的落盘**,不要凭直觉补写
3. 只读面下仍可用 `read`/`ls` 完成事实核实,不要空手交付

---

## ERR-20261029-002 用「写入前的本地快照」判断 crontab 是否生效 → 误判

**现象**:上轮用 `/tmp/crontab.latest` 与 `crontab.bak-*` 对比,判定 crontab 写入未生效,
实际 `crontab -l` 显示第 18 行 `40 3 * * * push-backup-summary.sh` 已生效。

**根因**:`crontab.latest` 是**改动前**的快照,不是写入后的实际状态;用它对比等于自己和自己比。

**教训**:**判定全局状态(crontab/systemd/配置)必须读「权威源」本身**——即 `crontab -l`、
`systemctl show`,而不是自己写的临时快照。写入后应立即 `crontab -l` 复核并数出现次数防重复。

---

## ERR-20261029-003 修改前未确认原实现是否已覆盖 → 产生无行为变更的 commit

**现象**:提交「tar 加 `--warning=no-file-changed`」(98eb8106),但真实 tar 命令第 242 行
**2026-07-13 就已有**该参数,改动实际只落在一行 log 文本 → 无任何行为变化,
随后又 revert(daa417a0)多一个 commit。

**教训**:**动手前先 grep 目标实现是否已包含该行为**。若已包含,要么放弃改动,
要么改成真正有增量的内容(如本轮把矛盾日志句改为短路写法)。

## ERR-20261030-001 c9353413 把 434MB 数据库备份误收进 public 仓库 → push 被远端断开

**现象**:`git push` 反复失败。错误演进:
1. 卡在 `POST git-receive-pack (chunked)`,119s 无输出
2. 加 `-c http.postBuffer=524288000` 后明确报错:
   `POST git-receive-pack (116416597 bytes)` → `send-pack: unexpected disconnect while reading sideband packet` →
   `fatal: the remote end hung up unexpectedly`

**排查路径(错误的诊断弯路)**:
- 先怀疑 chunked 编码被阻断 → curl 实测 chunked POST 与 normal POST **都是 0.69s 返 401**,chunked 没被阻断
- 先怀疑网络/代理 → `curl github.com` 0.71s,`ls-remote` 正常 → 网络没问题
- **真因**:待推 pack 里塞着 `.backups/doctor-fix-20261019-011140/` 的 8 个 sqlite 文件(合计 434MB,单文件最大 214.5MB)
  → 116MB 的 POST 被 GitHub 断开

**更严重的问题**:`.backups/openclaw.json.before-*` 含 **appSecret / API key 明文**,
而该仓库是 **public**(`private: false`, visibility=public)。

**修复**:
1. `git rm --cached -r .backups/` + `.gitignore` 加 `.backups/`
2. `git filter-branch --index-filter` 改写未推送段(12 commit),从历史彻底剔除
   - 待推 blob:459.6MB → **10.0MB**;push 立即成功(exit 0)
   - 远端确认 `.backups` 文件数 = 0
3. 全量扫描远端完整历史 1142 个对象 → **凭据命中 0**(未发生泄露)
4. 保留安全 tag `safety/pre-backups-purge-20261030-001127` 以便回滚

**教训**:
- **「push 失败」先查 pack 体积**:`git rev-list --objects origin/branch..HEAD | git cat-file --batch-check`
  列出最大 blob —— 比猜网络/编码快得多
- **public 仓库必须做凭据扫描**:`"appSecret"\s*:\s*"..."`、`sk-[A-Za-z0-9]{24,}`、
  `LITELLM_MASTER_KEY\s*=` 三条正则覆盖本项目已知凭据形态
- **仅从索引移除不够**:文件已进入 commit 历史,不改写历史 blob 仍会被上传
- 大文件(>50MB)入库前必须问「这该进 Git 吗」

---

## ERR-20261030-002 pkill 模式匹配到自身 shell → 命令被自己杀掉

**现象**:`pkill -f 'git push'` 后,执行该命令的 bash 自身被 SIGKILL,
后续诊断步骤全部丢失,输出只剩第一段标题。

**教训**:
- `pkill -f <pattern>` 会匹配**命令行中含该字符串的当前 shell 本身**
- 正确做法:`ps -eo pid,args | grep '[g]it push'`(方括号技巧)先定位 PID,再 `kill <PID>`
- 或用 `kill -9 <pid>` 精确杀,不用模式匹配

## ERR-20261030-003 runtime 报 session 仍在跑,但 /proc 已无该进程 → 假警报,勿反复清理

**现象**:runtime 上下文持续列出 `fresh-shoal` 为「running, pid 607358」,
但 `ps`/`/proc/607358` 均查无此进程。反复 `process kill/remove` 只得到
`No active session found` / `No session found`。

**真相**:`process list` 返回的 6 个 session 中,匹配到 `fresh-shoal` 字样的那条
其实是 **`salty-cedar`**,其 command 文本里含 `fresh-shoal` 字样(我自己写的 grep 模式)
→ 字符串匹配命中,并非该 session 本身。**`status=running` 的 session 实际为 0 个**。

**教训**:
- runtime 的 session 索引可能是**陈旧快照**;判定「进程是否活着」用 `ps`/`/proc` 实测,不靠 runtime 文本
- `process list` 的结果要按 **sessionId 精确比对**,不要用「命令行里含某字符串」当匹配条件
- 反复尝试清理一个已消失的对象是**无效轮次**;确认无副作用后即可停止

---

## ERR-20261030-004 长耗时网络命令在 exec 内会超时丢结果 → 必须 nohup + 轮询日志文件

**现象**:`openclaw update status` / `npm view openclaw version` 走代理链路,
单次超过 120s,exec 返回 "running" + sessionId,后续 wait 拿不到最终输出,
多次重复执行反而互相干扰(`/tmp/upd.log` 被并发覆盖)。

**正确做法**:
```bash
nohup bash -c '...' > /tmp/upd.log 2>&1 &   # 后台写文件
sleep N; cat /tmp/upd.log                  # 轮询读取
```
**教训**:
- 预计耗时 >60s 的命令一律后台化 + 日志轮询,不要依赖 exec 的 wait 链
- 同一命令**不要并发启动多次**(会互相覆盖日志/抢锁)
- 已拿到结论后**主动 kill 残留查询进程**,避免空转耗 token

## ERR-20261030-005 push 被拒的精确原因是 GitHub pre-receive 对 >100MB blob 的硬拒绝

**现象演进**(三次尝试,三种症状,同一根因):
1. `git push` 卡在 `POST git-receive-pack (chunked)`,119s 无输出
2. 加 `http.postBuffer=524288000` 后:`POST git-receive-pack (116416597 bytes)` →
   `send-pack: unexpected disconnect while reading sideband packet` →
   `fatal: the remote end hung up unexpectedly`
3. 最早的 push 终于返回完整错误:
   `! [remote rejected] feature/hot-backup -> feature/hot-backup (pre-receive hook declined)`

**精确根因**:`pre-receive hook declined` = GitHub 拒绝接收含 **>100MB blob** 的推送。
实测待推历史中:
```
214.5 MB  .backups/doctor-fix-20261019-011140/agents__main__agent__openclaw-agent.sqlite
```
单 blob 214.5MB 远超 GitHub 的 100MB 硬限制 → 服务端在接收阶段就拒绝,
客户端看到的「远端断开」只是**服务端拒绝后的连接中断现象**,不是网络问题。

**为什么前两次诊断都走偏**:
- 第 1 次:以为是 chunked 编码被阻断 → curl 实测 chunked 与 normal POST **都是 0.69s 返 401**,chunked 没问题
- 第 2 次:以为是网络/代理 → `curl github.com` 0.71s、`ls-remote` 正常,网络没问题
- **正确顺序**:push 失败 → **先查待推对象的 blob 尺寸分布**,再查网络
  ```bash
  git rev-list --objects origin/branch..HEAD | \
    git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' | \
    sort -k2 -rn | head
  ```

**修复与验证**:
- `git filter-branch --index-filter` 改写未推送段 → 待推 blob 459.6MB → **10.0MB**
- push 立即成功(exit 0),远端确认 `.backups` 文件数 = 0、无 >100MB blob
- 远端完整历史 1142 对象凭据扫描 → 命中 0

**教训**:
- 「远端断开 / hung up」是**服务端拒绝后的表象**,不是网络故障的证据
- 遇到 push 失败,**先量 pack 和最大 blob**,再看网络 —— 顺序反了会浪费大量轮次
- 大文件(>50MB)入库前必须问「这该进 Git 吗」;public 仓库尤其如此

---

# ERRORS / 运行备忘

## 2026-10-30 01:06 write 工具“伪成功”问题（首次遇到）

**触发**：`write` 工具对 `heartbeat/nightly-scout-2026-10-30.md` 返回 "Successfully wrote 13317 bytes"，但随后 `ls` 显示 `No such file or directory`，文件实际不存在；同场另一文件 `memory/nightly-scout-2026-10-30.md` 则正常落盘（17096 字节），说明不是全局故障，且与写入内容/长度无关（13KB 不算大）。

**处置**：
1. 对重要产出文件，write 后必须用 `ls -la`/`wc -c` 验证真实存在与字节数，不能只信工具返回的成功消息。
2. 发现伪成功时直接重新 write 同一路径，本场重写即成功（13317 字节落盘）。

**教训**：
- write 的成功返回与磁盘真实状态可能不一致，产出文件一律事后校验（ls/wc），重要文件写入后验证应成为固定收尾步骤。
- 同一目录下并发/相继 write 两个文件时，验证应逐个进行，避免只验了一个就默认另一个也成功。

---

- [2026-10-30 02:45][Orch] NightOps cron 会话收到 <error-detected> 假阳性：引用 exec 标准输出片段(nightly-scout 内容)，当日两次 exec 实际均成功退出；判为调度层误报，仅记录，若同模式再现再深查。

## ERR-20261030-006 `python3 -c "..."` 内用 f-string 双引号 → 被 shell 吃掉 → NameError

**现象**:
```bash
python3 -c "
import json
...
print(f'  {k:12} primary={str(m.get(\"primary\")):32} fallbacks={fb}')
"
→ NameError: name 'primary' is not defined
```
**根因**:外层是双引号,内层 f-string 里的 `m.get("primary")` 的双引号被 shell 提前闭合 →
传给 python 的代码里 `primary` 变成了裸标识符 → NameError。
**教训**:
- `python3 -c "..."` 里**不要出现双引号**,一律用单引号;需要引号时改用 `'''...'''` 或写临时 .py 文件
- 更稳的做法:**一律写临时脚本文件再执行**(如 /tmp/x.py),彻底避开 shell 引号地狱
- 本次该错误只影响一条诊断命令的输出格式,未造成副作用;但同型错误在写配置时会静默改错值

## ERR-20261031-001 网关重启会让未消费的 cron systemEvent wake 被反复重放

**现象**:`【NightOps 记忆体系讨论】`(cron `20 23 * * *`,kind=systemEvent,id=db2fae49-…)
的**同一次排程**(原始时间戳恒为 2026-10-30 23:20)在单个会话内被投递 **7 次**,
每次都要求「输出讨论纪要到 memory/2026-04-15.md」。

**根因**:
- 该任务是 **systemEvent**(只派发事件,`lastDurationMs=13`,不自行执行)
- 网关每次重启,**未消费的 wake 会被重新投递**(本会话期间网关因工具面收窄/取证重启了多次)
- 负载均衡/多 session 会让同一 wake 被送到不同 session → 各写一份 → 纪要重复膨胀

**已采取的防护(幂等模式,与备份摘要推送同构)**:
```
状态文件: ~/.openclaw/.nightops-discussion-last   (记录已回答的排程时间戳)
payload 追加「幂等护栏」段落:
  若系统时间戳([System: ...] 的时间)已记录在该文件 → 直接回复「本轮已讨论过,跳过」,
  不重复追加纪要;回答后把该时间戳写入该文件。
```
**验证**:`openclaw cron get` 确认原文四个议题完整保留 + 护栏存在;状态文件与本次 wake 时间戳一致 → 本轮应跳过。

**教训**:
- **cron 驱动的产出任务必须幂等**。`systemEvent` 型尤其危险 —— 它自己不执行,
  每次重放都会真的触发一次「写文件/发消息」型 agent 行为。
- **区分标识**:同一排程的重放,`[System: ...]` 的时间戳是唯一稳定标识(不同于 `lastRunAtMs`)。
- **不要靠「多写几版」掩盖重复**:纪要类文件每版都要有新增证据,否则是纯噪声。

## ERR-20261101-001 read 返回截断内容 → read-modify-write 抹掉 3594 行历史(v30 写入时自犯)

**现象**:向 `memory/2026-04-15.md`(4709 行)追加 v30 时,走了 read-modify-write:
```js
const cur = await read({ path });            // ← 返回的是【截断】内容,只有 1115 行
const res = await write({ path, content: prev + memo });   // ← 用截断的 prev 覆盖了整个文件
```
→ 文件从 4709 行掉到 1115 行,**v28 / v29 两段讨论纪要全部消失**。

**发现方式**:写完立刻核对行数(vs git HEAD)与关键段落 grep 计数,发现 v28/v29 命中数变 0。

**恢复**:`git checkout -- memory/2026-04-15.md` → 4709 行,v28/v29 恢复,随后改用
`cat >> file <<'EOF'` **原子追加**(不经 read-modify-write)写入 v30 → 4852 行,三段齐全。

**根因**:`read` 工具在文件较大时**会返回截断内容**(且截断点在响应的 `content` 字段里不带显式标记),
调用方若不校验行数就把它当作完整文件回写,等于用局部内容覆盖全量。

**教训**:
- **read 的返回值必须与目标文件的真实大小核对**(行数/字节数),确认是全量后才可用于回写。
- **大文件一律用 `cat >>` 原子追加**,不要 read-modify-write;两者混用是本次事故的直接原因。
- 这正是 NightOps v29 议题1 讨论的「agent 越界」的**自证案例**:
  v29 说「写入必须幂等追加,覆盖需先读后写 + diff 校验」——
  而我自己在写 v30 时就犯了「先读后写」这个错,说明**规则必须写进工具层的默认行为,而不是靠每次记得**。
- 与 ERR-20261030-006(shell 引号吃掉 f-string)同类:**都是「构造命令/内容」的引号与转义陷阱**,
  且都能被「写完立刻核对产物」的固定动作挡住。
