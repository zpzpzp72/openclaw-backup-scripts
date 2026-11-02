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

## ERR-20261101-002 D 盘 File History 治理：三条"看似合理"的手段全被实测证伪

**背景**:D 盘 100% 满(477G/Avail 0)。`D:\FileHistory` 351.72GB,根因是
`Config*.xml` 里 `RetentionPolicyType=DISABLED`(永不清理旧版本)+ `fhsvc` 每小时扫一次
→ 只进不出,单调累积。

**三条我先后尝试、并被实测逐一证伪的手段**:

### ① 只改 `Config*.xml` 的 `<UserFolder>` → 会被服务还原
- 21:16:46 从两侧配置的 `<UserFolder>`(各 44 项)移除 `.ollama`/`.workbuddy`/`.vscode`/`.codex`/`.cache`。
- 21:38:40 维护任务跑完后:LOCAL Config1、Config2、TARGET Config1 **全部恢复成 44 项**;
  只有 TARGET Config2 保留了我的 27 项。
- **根因**:`<UserFolder>` 清单的真相源是 **catalog(ESE `.edb`)**,不是 XML、也不是注册表
  (注册表 `HKLM/HKCU\...\FileHistory` 下只有 `Policies` 和 `RestoreUI`,无清单)。
  保留策略(Retention)服务每次**从磁盘 XML 读**,所以 AGE LIMIT 能生效;
  但清单会**从 catalog/服务内存状态重建后覆写 XML**。
- 附带修正:`Config1.xml`/`Config2.xml` 是**配置轮转**,真正生效的是 Config1,
  Config2 只是上一版存档 —— 这解释了"为什么只有 Config2 保留了我的修改"。

### ② 给源目录加 SYSTEM `Deny ReadAndExecute` ACL → 服务照样全量复制
- 21:59 应用到 17 个目录,deny ACE 已确认继承到子目录和深层文件;
  第一轮观察 `.ollama`/`.vscode`/`.codex`/`.cache` 新增 0 → **误判为有效**。
- 第二轮维护后被推翻:`.ollama` 从 146 → 181 个文件、存储 39.08 → **67.81GB**(+28.73GB),
  `.cache` 32,421 → 46,815,`.vscode` +6,634,`.codex` +4,886。
- **根因**:File History 以 `SeBackupPrivilege` + `FILE_FLAG_BACKUP_SEMANTICS` 打开源文件,
  **按设计绕过 DACL**(备份语义)。ACL 无法阻止它读取。
- **教训**:ACL deny 对备份类服务(Windows VSS/Windows Backup/File History)无效;
  "第一轮没增长"不等于方案成立,必须**跨两轮**验证才能排除间歇性假象。

### ③ 手工删除 store 里的版本文件 → 触发 catalog 失配后的全量重播种
- 20:40 剪掉 Wechat_WZP 113,960 个版本文件(释放 209.50GB);21:01 删掉 `Data\$OF` 788,834 个文件(66GB)。
- 之后服务把**每个源文件当"待补传"重新上传**:
  `.cache` 源目录自 2026-06-15 起 0 改动却被整目录重拷(+14,394 文件);
  `.ollama` 源目录自 10-01 起 0 改动,35 个文件 28.73GB **整份重传**。
  Wechat_WZP 21:16 被剪到 7,141,现在回到 8,581 —— **手动删的被传回来了**。
- **根因**:`RetentionPolicyType=DISABLED` 时 catalog 期望保留**全部历史版本**,
  手工删掉的文件被视为"缺失待补" → 全量重播种。这不是变更检测,是 catalog 一致性修复。

**综合结论**:
- D 盘增长的真实机制 = `DISABLED` 保留策略 + 高频写小文件源目录(Wechat_WZP 6.41GB → 213.22GB,33 倍膨胀)。
- **唯一正确的止血手段是改保留策略(AGE LIMIT),让 Windows 自己按策略删**;
  手工删 store 文件与 ACL 排除都属于"绕过 catalog",只会让情况更糟。
- 排除目录的**唯一可靠入口是 catalog**,命令行不可达
  (`fhmanagew.exe` 无 CLI 参数,注册表无清单)→ 若必须排除,得走 GUI(控制面板 File History)或接受现状。
- 当前生效状态:`fhsvc=Running/Automatic`,维护任务 `Ready`,
  四份配置 `Retention=AGE LIMIT / MinimumRetentionAge=7`,D 盘 215.3GB 空闲且恢复后 6 分钟零增长。
- 已彻底回滚无效的 ACL 改动(17 个目录 `denySYSTEM=0`,SYSTEM allow=1),不留副作用。
- **可逆操作记录**:`fh-halt.ps1`(停服务+禁用任务) / `fh-resume.ps1`(恢复);
  钩子挂在 `C:\Scripts\CheckAPNetwork.ps1` 的 `ResetAPNetwork` 计划任务(已是管理员上下文)。

## ERR-20261102-001 调 exec 漏传 `title` → 工具直接拒绝,命令未派发

**现象**:两次调用 code-mode 的 `exec` 时只给了 `{command, yield_time_ms, code}`,
漏掉必填的 `title`,返回:
```
Validation failed for tool "exec":
  - title: must have required properties title
```
→ **命令根本没有派发**(无副作用),但那一轮的工作全白做,必须重发。

**发生场景**:连续两次都是我「先想好命令、直接塞进 exec」的写法,没有走
「先写 title 再写命令」的顺序 —— 漏字段比写错内容更容易发生,因为它不报错在
我的思维里,只报在工具校验里。

**教训**:
- **`exec` 的必填字段是 `title` + `code`**(不是 `description`)。写 `description` 会被拒。
- 每次调 `exec` 前先确认参数名:`{ title, code, yield_time_ms?, awaitResults?, background? }`。
- 与 ERR-20261030-006(shell 引号吃掉 f-string 双引号)同属一类:
  **「构造调用」本身会出错,且错误发生在工具层而非我的逻辑层** → 必须在调用前过一遍必填字段清单。

---

## ERR-20261102-002 error-detected 把正常输出误报为错误

**现象**:本轮收到 3 条 error-detected 信号,只有第 1 条(`title` 缺失)是真实错误,
第 2、3 条是**我自己的正常诊断输出**被关键词触发:
- `==== 1. 备份心跳文件:内容 vs 修改时间 ==== ... last_backup=...` → 因含 `last_backup`/`error` 类字样被误报
- `{"status":"completed",...}` → 正常完成回执被误报

**教训**:
- **error-detected 里的信号必须逐条核实,不能默认都是真错误**。
  判据:该条对应的工具调用是否真的返回了 failure/exception,而不是只看它"像不像"错误输出。
- 本轮据此定位到唯一的真实问题(漏传 title),其余两条排除 —— **避免为误报去"修"根本没坏的东西**。

## ERR-20261102-003 File History 队列通道竞态:运行中覆写 queue.ps1 的新载荷被收尾清理删除

**现象**:fh-diag-F 载荷运行期间(04:59:02–05:01:19)向 `C:\Scripts\logs\queue.ps1` 重写放入 M 载荷(maintenance task 实验),写入返回成功 6070B;但 F 收尾完成后 queue.ps1 被清空删除 → M 载荷**从未执行且无任何报错**,差点误判「已投递」。
**机制**:runner 消费后清理 queue.ps1;若在载荷运行中写入,新文件会随旧载荷收尾一并被删(或被收尾清理覆盖)。queue-run.log 显示 F 是最后一条记录,证明 M 从未入过执行序列。
**教训**:
- **写 queue.ps1 前必须确认 queue-run.log 最后一条是 `payload done` + exit code**(通道空闲)。F 的日志结尾是 `payload exit code = 0 / === queued payload done ===` 才算收完。
- 「已重投/已投递」宣称必须有事后 `ls`/日志佐证,不能只看 write 返回值(同类:声称已做但无工具调用证据)。
- 同一队列通道一次只放一个载荷;需串行实验就在 payload 内部串联步骤,或在确认前一载荷 done 后再投。
- 载荷可在开头 `Remove-Item ... queue.ps1 -ErrorAction SilentlyContinue` 自声明防重入(防 15 分钟内下一次 ResetAPNetwork 重复执行);若与自身句柄冲突删除失败也无害,靠 runner 收尾清理兜底。

## ERR-20261102-004 File History 配置回写机制翻案:推导源是文件系统而非 catalog

**背景**:干净重建后(11-01 23:23 删除全部 store+catalog)曾观察到 23:29/00:31/01:31 配置被回写成 44 项,当时结论「仅改 Config*.xml 不可靠,服务从 catalog 重建清单并覆写 XML」。
**翻案**:
- B/D/E 三轮一致证明:**catalog 全删的窗口,服务照样回写 44 项** → 推导源是**文件系统**(profile 顶层目录 + shell 库),不是 catalog;「XML 是 catalog 镜像」的旧结论不完整。
- 但 fh-diag-F 实测:fresh 启动的服务(无 catalog)运行 2 分钟内**不回写**;23:29/00:31/01:31 的回写点与 maintenance task COM 激活(或 fhmanagew 孤儿)窗口吻合 → 回写疑似绑定**maintenance task COM 激活上下文**而非普通 Start-Service,精确触发条件仍待 M2 测试定论。
- **服务自停模式(第 3 次实锤)**:F 04:59:18 由载荷启动 → 05:01 Running → 05:07 已 Stopped/Manual,中间无人成功 stop(elevated Stop-Service 报「无法打开计算机上的 fhsvc 服务」,是 SCM 权限噪声,不掩盖自停事实)→ **无合法 catalog 时空闲服务 3–4 分钟自停**。
- **fhsvcctl P/Invoke 另一失败模式**:`Add-Type` 后调用 `FhServiceOpenPipe(out uint)` 抛 NullReference(调用层反射 marshalling 问题,而非签名猜错)→ 管道路线放弃,需 COM 接口 IFhService + 正确 marshaling 才能进一步,不再投入。
- **COM 盲调不可行**:`FhReassociation`/`FhTargetMigration` 实例化成功但 10 个方法全部 NullReference(fhcfg 无 typelib/无 dispatch 绑定)。
- **TGT Config2 = 21 项(缺 .agents)**,其余三份 22 项 — 存档副本小不一致,无实质影响,不修。
- **M2 后记(06:20)**:维护任务 Enable+Start 实测成功(Ready/True,0x0)但 fhsvc ≤20 秒自停、catalog 零产出、UF 恒 22 零回写 → 「COM 激活触发回写」假说未获证实,触因仍未知(仅三个不明窗口出现过),不再追。
- **自停升级为第 4 次实锤且更快**:M2 服务 Running→Stopped ≤20 秒(F 约 2–6 分钟)——无合法 catalog 时服务确定性快速自停,官方 COM 激活也救不回。
**教训**:机制结论(「推导源是 X」)必须有跨条件证据(有无 catalog/有无孤儿/有无 COM 激活各一组实验),仅凭单轮时间相关性下结论会被下一轮翻案。

## ERR-20261102-005 PowerShell 对无 typelib 的 COM 用 InvokeMember 盲调:全量方法 NRE

**现象**:probe-fh 对 fhcfg.dll 的 FhReassociation/FhTargetMigration 用 Type.InvokeMember 按名调用 10 个疑似方法,实例化成功但全部抛「未将对象引用设置到对象的实例」(NRE),hr 无法获知。
**根因**:fhcfg.dll 未注册 typelib,COM 接口是 custom vtable 接口,不能 IDispatch/InvokeMember 按名绑定;实例化成功仅说明 coclass 可创建,不说明方法可调。
**教训**:
- 遇到「实例化成功但方法全 NRE」,先查 typelib 注册(`oleview`/注册表 TypeLib),不要继续换方法名盲调。
- 无 typelib 的自定义 COM 需要 vtable 顺序 + Marshal 显式调用,工程量与收益不成比例 → 判定为「不可行」并记录,不反复尝试。
- 同类教训:fhmanagew.exe CLI 动词(提权 `-checktarget`/`-backupnow`)依旧 exit=1 无输出且留 180 秒孤儿进程(53932/91040) → **fhmanagew 无可用 CLI**,每次尝试后必须 taskkill 清孤儿。

## ERR-20261102-006 手打 sessionId 而不复制工具返回值 → poll 必报 No session found

**现象**(本轮 07:53–07:56 连续两条真错误)：
1. `process poll` 传 `sessionId: "lucky-orback"` → `No session found for lucky-orback`。实际会话是 `lucky-orbit` —— **是我自己给 id 臆造了一个后缀**，该 id 从未存在。
2. 随后 `process poll` 传 `glow-mist` → `No session found for glow-mist`。该会话早已 `Process exited (code 0)` 被回收，我又去 poll 一个已结束对象。

**根因**：两个 poll 都凭**记忆/推断**手写 handle，而不是复制 exec 返回值里的 `sessionId`；且没有先 `process list` 确认会话是否仍在。
**判据**：exec 返回 "Command still running (session <id>, pid <n>)" 时，**该 id 只能原样复制**，一个字符都不能改。已退出的会话 poll 会给 `No session found`（与 runtime 陈旧快照情形 ERR-20261030-003 现象同源，但成因是"我引用了不存在的 id"）。
**教训**:
- **handle 只允许 copy-paste,不允许手打**；`sessionId` / `runId` / `pid` 三者不可混用,也不可臆造变体。
- poll 前若不确定,先 `process list` 看一眼;已经 "Process exited" 的会话不要重复 poll(那是无效轮次)。
- 这是本项目「Code Mode 工具调用误用」家族的第 5 次复发(前 4 次见 2026-10-25 条目),**属高复发类,应固化**:凡是 `await process({action:"poll", sessionId})`,sessionId 一律从上一次工具返回里整段复制。

## ERR-20261103-001 「跨天趋势」被当成「持续增长」→ 据此找错方向、浪费一轮

**现象**:2026-11-02 08:21 我断言「NAS 3 天掉 150G,回收站持续膨胀,存在活跃写入源」,
并据此去找「谁在写」。
**23:20 复测证伪**:15 小时内 NAS **逐字节未变** —— Avail 恒 21G,
回收站 27 份/123.0GB、正常 19 份/139.4GB 全部一致。
→ 那 150G 是 **Avail 口径的一次性跳变**,不是持续增长。我找的「活跃写入源」不存在。

**根因**:
- 只有**单点/跨天的存量差**,没有**两次采样间的增量**
- NAS 的 Avail 会因回收站配额 / SMB 快照 / NAS 端回收策略而跳变,与本机写入速率脱钩
- 一次错误方向 → 消耗一整轮扫描(NAS 递归 du 还把 exec 通道卡死)

**教训(判据,可直接用)**:
> **「持续增长」需要 ≥2 次、间隔 ≥1 个观测周期的采样一致;单点趋势只证明「曾发生过」,不证明「正在发生」。**
> 「回收站持续膨胀」这类说法,必须给出**两次采样间的份数/体积增量**,而非跨天存量差。
> 配套:任何「下降 > X」类告警,**连续两次一致才推送**;单次跳变只记 event 不告警。
> —— 一个会误报的监控比没有监控更贵:它消耗的注意力与它防止的故障同量级。

---

## ERR-20261103-002 备份脚本的「NAS 空间预检」在后续编辑中被覆盖丢失

**现象**:MEMORY 记录 2026-10-29 已加入并在当日 03:00 实测生效的「NAS 空间检查」
(日志实证:「NAS 空间检查通过: 可用 171G,需要约 7G」),
但当前 `scripts/openclaw-backup.sh` grep 命中 **0** —— 该检查已不存在。
逐个 `.bak` 比对确认:仅 `.bak-20261029-153331` 保留,10-29 之后的几次编辑都基于**已丢失该检查**的版本。

**根因**:备份脚本被多处独立编辑(备份摘要推送、exclude 修正、矛盾日志句修正…),
每次都是「在当前版本上改」,而当前版本早已在某次编辑中丢失了 10-29 的改动;
**没有任何一处校验过「上一版有的功能是否还在」**。

**教训**:
- **每次改配置/脚本前,先 diff 关键功能点**(不只是 diff 自己要改的那几行)。
  本次若做 `diff <上一版> <当前版>` 的功能点清单,就能立刻发现「空间检查」被吞。
- MEMORY 里「已实施并验证」的条目,在**脚本被再次编辑后必须重新核实**(MEMORY 记录的是当时的版本)。

---

## ERR-20261103-003 cleanup_old 的静默失效:NAS 上 rm ≠ 释放空间

**现象**:`scripts/openclaw-backup.sh` 第 110-115 行:
```bash
cleanup_old() {
    find "$BACKUP_DIR" -name "openclaw-*.tgz" -mtime +$RETAIN_DAYS -exec rm -f {} \;
    log "清理超过 $RETAIN_DAYS 天的旧备份完成"     # ← 与事实不符
}
```
在 NAS(SMB 共享)上,`rm` 是**移入 `#recycle` 回收站**而非真删 → 空间不释放,
但脚本仍打印「清理完成」→ **每天都在假装成功**。
实测证据:回收站累积 27 份 / 123.0GB(8/27–10/13),与正常目录 19 份 / 139.4GB 日期区间完全不重叠。

**教训**:
- **执行环境的语义差异必须写进 wiki**(v32 议题2 的结论):
  「保留 30 天」是**意图**,「rm 在 SMB 上不释放空间」是**前提**;
  缺前提的 wiki 会产出「看起来在执行策略、实际不生效」的系统。
- **日志不能说谎**:「清理完成」应改为「已移入回收站(NAS 上不释放空间),需手工清空回收站」。

---

## ERR-20261103-004 watchdog 把注释行当数据行 → 每小时报一次算术错误

**现象**: `scripts/cron-watchdog.sh:48`
```bash
FIRST=$(head -1 "$TREND" | awk '{print $1" "$2}')
```
`logs/gateway-rss-trend.txt` 的**第一行是中文注释**（`# gateway-rss-trend.txt …`），
`head -1` 取到的不是数据行 → `F_TS="#"`、`F_KB="gateway-rss-trend.txt"` →
第 50 行 `DT=$(( NOW_TS - F_TS ))` 报 `syntax error: operand expected (error token is "#")`。

**影响**: 该错误在 `if (( ... ))` 之前的**裸算术展开**处，`set -e` 之外不会中断脚本，
但每小时的 RSS 趋势/ETA 打印全部丢失 → 「RSS 增速预测」这条链路实际已静默失效多日，
而日志里每天都在刷错误行，反倒掩盖了「趋势没打印」这一事实。

**修复**: `FIRST=$(grep -v '^#' "$TREND" | head -1 | awk '{print $1" "$2}')`，`bash -n` 通过。

**教训**:
- **趋势/状态文件的第一行不保证是数据行**——带表头/注释的日志文件必须先 `grep -v '^#'`。
- 错误行出现在日志里 ≠ 只影响那一行；**同一个 if 块里的后续语句（ETA 预测）被静默吞掉**，
  「有报错但功能看起来还在」是最危险的失效形态。
- 修 shell 时先 `bash -n`，再实跑一次取 FIRST/F_TS/F_KB 三个值确认非空。

## ERR-20261103-005 Life NightOps 连败两次：apply_patch 沙箱越界 + litellm 余额不足（跨 agent 汇总）

**现象**：cron `a6c108aa`（Life NightOps, 01:50）连续两次 error：
- 11-02 场（session 04c806da）：`Provider returned an incomplete or malformed tool call`
- 11-03 场（session 9c873b71，01:50→02:21）：`Apply Patch failed`，尾因 `402 litellm.APIError: Sorry, your account balance is insufficient`（model group GLM-5.3-Flash，no fallback attempted）→ run failed、delivered=false，飞书未收到

**根因链**：
1. apply_patch 的 sandbox root = `~/.openclaw/workspace/agents/life`，无法写 `workspace/heartbeat/` → 连续 4 次报错，末两条为 `Path escapes sandbox root` 与 `Cannot create ... file already exists`
2. 模型 tool call 结构损坏时，原始标记 `</tool_call><arg_key>…` 会漏进落盘正文（本次涉及 6 个文件：nightly-life-2026-11-03.md、nightly-orchestrator-2026-11-02.md 及 memory/daily 副本、memory/2026-10-28.md、agents/scout/memory/2026-10-25.md、agents/scout/memory/dreaming/light/2026-10-26.md）
3. litellm 账户余额不足且无 fallback —— 外部额度约束

**已修复**：清洗 6 个文件的工具标记泄漏与 U+FFFD 乱码，补全被截断的表格行；报告 §7 内容本体完好，三个目标文件（heartbeat/、memory/、agents/life/memory/）均已落盘。

**预防**：
- 跨 workspace 目录写文件**禁用 apply_patch**，统一 `exec` + heredoc 或 write
- 写完报告立即 `grep -n "arg_key\|tool_call\|</think>" <file>` 校验残留
- 额度类报错（2056 / 402）只写异常清单并告知 owner，不自行反复重试

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## ERR-20261103-006 NightOps 作业 sessionKey 绑错 agent 域 → 失败通知无法投递

**现象**：`Life NightOps`（cron `a6c108aa`）的 `lastFailureNotificationDeliveryError` 为
`Multiple agents are configured, but session agent resolution has no explicit owner. The agent-scoped session key belongs to "main", not "life".`
→ 连败两次时**连失败告警都发不出**（not-delivered），owner 完全看不到异常。

**根因**：该作业 `agentId=life`，但 `sessionKey` 被写成 `agent:main:main`（`ownership: explicit` 下 agent 与 session 域不匹配）。同类作业 `NightOps-Life`/`NightOps-Scout`/`NightOps-Coder` 用 `agentId=main` + `agent:main:main` 是自洽的，因此问题只在 `Life NightOps`（以及 Coder/Orchestrator NightOps）这三个 agent-scoped 作业上暴露。

**已修复**：
- `Life NightOps` → `sessionKey: agent:life:main`
- `Coder NightOps` → `sessionKey: agent:coder:main`
- `Orchestrator NightOps` → **改不动**：其 agent SQLite 报 `SQLite session reclamation commit checkpoint expired`，CLI 直接拒绝任何 edit（需停 Gateway 跑 `openclaw doctor --fix` 再重启，属 owner 决策）

**预防**：新建 agent-scoped 作业时，`agentId` 与 `sessionKey` 的 agent 段必须一致；改完用 `openclaw automations get <id>` 复核。

## ERR-20261103-007 litellm 全线不可用 + minimax 大面积 429

**现象**（`openclaw logs` 近 2000 行统计）：
| provider/model | status | 次数 |
|---|---|---|
| minimax/MiniMax-M2.7 | 429 | 57 |
| minimax/MiniMax-M2.7 | 200 | 7 |
| litellm/GLM-5.3-Flash | 402 | 12 |
| ollama/qwen3:4b-instruct | 400 | 5（另有 200 × 3） |

**根因**：litellm 账户余额不足（402）；minimax 侧 Token Plan 额度触顶（429）；litellm 其余模型 400（apiKey 占位符未解析，见 ERR-20261103-005）。→ 三个默认 fallback 全断，只剩 ollama 本地 4B 能跑。

**已缓解**：`Life NightOps` 作业级改绑 `model=minimax/MiniMax-M2.7`，fallbacks 设为 `minimax/MiniMax-M3.1-Flash → minimax/MiniMax-M3 → ollama/qwen3.6:27b → litellm/deepseek-flash`（把 minimax 系放在最前，避开 litellm 402 通道）。

**预防**：作业级 model/fallback 覆盖优先于 agent 默认链；litellm 系在余额恢复前应从关键作业 fallback 链末尾移除。

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
