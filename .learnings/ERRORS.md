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

## ERR-20261103-005 watchdog 趋势计算三重根因:每修一层仍不通,必须端到端实跑验证

**症状**:`cron-watchdog.sh:50` 报「#: syntax error: operand expected」,
RSS 趋势与 ETA 打印被静默吞掉(每小时发生)。

**三层根因(前一层修完仍不通,必须逐层剥)**:
| 层 | 根因 | 修法 |
|:--:|------|------|
| 1 | `grep -v "^#" \| head -1` 取到的是注释段后的**空行** | 改 `grep -E "^[0-9]"` 只取数据行 |
| 2 | **`set -euo pipefail`**:grep 无匹配返回 1 → set -e 让脚本**整体提前退出** | 所有可能失败的命令补 `\|\| true` |
| 3 | 趋势文件有**两种历史格式**(`MM-DD HH:MM KB` / `epoch KB`),早期格式缺年份 `date -d` 失败 → F_TS=0 → DT 显示 56 年 | 分别解析;早期格式补当前年份 + 跨年回退 |

**教训**:
- **「修完第一层」不等于修好**。本次每修一层都以为好了,实跑仍不通。
  → 必须**端到端实跑脚本并检查目标输出行是否真的出现**,而不是只看 `bash -n` 通过。
- **`set -e` + 可能失败的命令 = 静默截断**。凡是 `grep`/`awk`/`date -d` 这类
  「输入为空就返回非 0」的命令,在 `set -e` 脚本里都必须 `|| true` 兜底。
  (grep 无匹配返回 1 是最常见的坑)
- **同一文件的历史格式漂移**要在解析层兼容,否则新旧混存时静默算错。

## ERR-20261104-001 在 npm install 仍在跑时删掉其工作目录 → 报错刷屏且结论不可靠

**现象**:为验证「node 26.10.0 是否满足 2026.10.9 的 engines」,在 `/tmp/engchk` 做了
`npm install openclaw@2026.10.9`。npm 仍在拉包时,我判定结论已出就 `rm -rf /tmp/engchk`,
导致仍在运行的 npm 立刻报:
```
NOENT: no such file or directory, lstat '/tmp/engchk/node_modules/npm'
npm error enoent ...
```
→ 该报错被 error-detected 捕获,看起来像「安装失败」,**差点推翻我的正确结论**。

**根因**:后台进程仍在使用某目录时删除它 → 进程后续 IO 全部 ENOENT。
我以为「install 已成功(node_modules/openclaw 存在)」就等于「npm 进程已结束」,但两者不等价:
npm 还在做依赖树收尾、脚本、清理等后续工作。

**教训**:
- **「产物已出现」≠「进程已结束」**。用后台命令的产物做结论前,必须确认进程真的退出
  (`pgrep` 确认无残留),否则它的报错会污染判断。
- **结论的正确性不能依赖「删除动作的副作用」**。我删目录是想清理,结果制造了误导性报错;
  正确顺序是:先确认进程退出 → 再清理 → 再做判定。
- 这次的实际影响:全局 openclaw 完好(2026.10.5)、npm 全局无污染、`/tmp/engchk` 已清,
  **无实质损害**;但如果当时没多想一步,很可能就把「升级无障碍」这个结论给否掉了。

---

## ERR-20261104-002 自写 semver 正则判定 npm engines → 判错(把 || 当成 &&)

**现象**:`2026.10.9` 的 engines 是 `">=24.22.1 <25 || >=26.12.1"`,
我自写正则判定时,把 `||` 的语义处理成了「两个区间都要求」,于是得出
「node 26.10.0 不满足 → 升级需先升 node」的**错误结论**(这个错误结论还是夜检报告里给出的)。

**根因**:`||` 表示**任一区间满足即可**;`>=26.12.1` 是**下界**,不是「仅此版本」。
26.10.0 落在 `<25` 之外,但也**不在** `>=26.12.1` 之外——它确实不满足后半段,
但**是否满足整体**取决于前半段 `>=24.22.1 <25`,而 26.10.0 也不满足前半段。
→ 所以 26.10.0 **确实不满足**该 engines;但 npm 实际安装**成功了**,说明真实判定与我的解读有出入,
必须以 npm 自身的行为为准。

**教训**:
- **不要手写 semver 判定**。`node_modules/semver` 常不可用,`npm ls`/`npm install` 才是权威实现。
- **用真实工具行为裁决**,而不是用「我理解的规则」推演 —— 这与 v33 的
  「连工具输出的数字也要二次采样验证」同源:**二手解读不可靠,一手行为才可信**。
- 推演与实测冲突时,**以实测为准**,并回头检查自己的解读错在哪。

## ERR-20261104-003 对已结束 session 调 kill/clear 会产生 error-detected 噪声(非真错误)

**现象**:清理僵留 session 时,`process kill/clear` 对**已结束**的 session 返回:
```
No active session found for <id>        ← kill
No finished session found for <id>     ← clear
```
这些会被 error-detected 捕获,看起来像「工具调用失败」。

**判据(必须逐条核实,不能默认都是真错误)**:
| 返回 | 含义 |
|------|------|
| `No active session found` | 该 session **早已结束**,无需再 kill → **不是错误** |
| `No finished session found` | 同上,只是该 action 要求 finished 态 → **不是错误** |
| `No session found` | 已从注册表摘除 → **不是错误** |

**权威判定方法**(本轮已用):
```
process list  → 看该 session 的 status 与实时 running 数
/proc/<pid>   → 进程真身是否还在
```
本例:`process list` 显示 nova-orbit status=`failed`、实时 running=0,`/proc/859989` 不存在,
而 runtime 上下文仍写它「running」→ **runtime 上下文是陈旧快照**(同 ERR-20261030-003)。

**教训**:
- **error-detected 是「可疑信号」不是「错误清单」**。每条都要用权威源核实。
- 误报的代价不只是噪音:本轮若据此回头「修」一个没坏的 session,
  就是纯粹的无效轮次;更糟的是可能把真实故障混进噪音里而漏掉。

## ERR-20261104-004 「npm install 成功」被当成「engines 满足」的证据 → 结论错误

**现象**:为核实「node 26.10.0 能否装 openclaw 2026.10.9」,我做了
`npm install --ignore-scripts openclaw@2026.10.9`,**安装成功**,于是据此得出
「无 node 版本障碍,升级可直接做」。

**权威事实**(npm registry):
| 版本 | engines.node | node v26.10.0 |
|------|-------------|---------------|
| 2026.10.9 | `>=24.22.1 <25 || >=26.12.1` | ❌ **不满足** |
| 2026.10.10 | `>=24.16.0 <25 || >=26.1.0` | ✅ 满足 |

**根因**:
- npm 的 engines 检查**默认只警告(EWARN)不阻断安装**,除非 `engine-strict=true`
- 我还加了 `--ignore-scripts`,进一步绕过检查
- 我把「产物出现了」当成了「前提满足」——正是 ERR-20261104-001 刚记的同一类错误

**教训**:
- **判定「前置条件满足」必须读【规则本身】(registry 的 engines 字段),不能用「动作成功了」倒推。**
  动作成功可能只说明它没被检查。
- 权威判定二选一:
  1. 读 `engines` 字段 + 用 semver 库判定(`satisfies`)
  2. `npm_config_engine_strict=true npm install` 让 npm 真正拦截
- 与 v33「连工具输出的数字也要二次采样验证」同源:
  **二手证据(装上了)不可信,一手规则(engines)才可信。**

## ERR-20261105-001 三处工具调用失误:JS 模板串含 shell 反引号 / read 读目录

**现象(同一轮内三次)**:
1. `exec` 报 `SyntaxError at openclaw-code-mode:user.js:1:971: Unexpected token`
   → 原因:code-mode 的 JS 里我用模板字符串包了含 **shell 反引号**(`\`\``)的命令,
     JS 模板串把反引号当成结束符 → 整段解析失败,**工具根本没派发**。
2. `read` 报 `Read requires a file path, but <dir> is a directory`
   → 原因:对目录调 `read`(想列 nvm 版本),应该用 `ls`。
3. 同一错误在 exec 内的 shell 里重演一次。

**教训**:
- **code-mode 的 JS 模板串不能直接包含反引号的 shell 命令**。
  两种可靠做法:
  - 用 `write` 工具先把脚本落成文件,再 `exec` 执行它(本轮验证有效,完全绕开引号层);
  - 或把 shell 里的反引号换成 `$(...)` / `\$()` 等不含反引号的写法。
- **`read` 只吃文件,目录要用 `ls`**。
- 这三条与 ERR-20261104-006(shell 引号吃掉 f-string)同源:
  **凡是「内容里含有特殊字符的代码」,一律走「写文件 → 执行」两步,不要内联。**

## ERR-20261105-002 用「推演」代替「跑真实逻辑」判定截止时间 -> 连续两轮报错

**现象**:连续两轮我断言「明日 03:00 备份会被预检拦截」,依据是推算:
「Avail 9.5G − 需写 5.7G = 剩 3.5G < 阈值 6G → 拦截」。
**实际**:脚本比较的是**写入前**的 Avail:
```bash
if [ -n "$AVAIL_GB" ] && [ "$AVAIL_GB" -lt "$NEED_GB" ]; then
```
Avail=10G ≥ 6G → **放行**,写完剩 4G;要到**下一次**才被拦。真正断链是 11-07,不是 11-06。

**教训**:
- **判定「某条件会不会触发」必须执行被判定的那段逻辑,不能用「我理解的等价推演」。**
  推演与真实逻辑的差别(比较写入前 vs 写入后)正是这类错误的来源。
- **纪律**:凡涉及「何时会失败/何时会断」的时间点,一律写一个脚本、跑它、贴它的输出,
  而不是给出「A - B < C 所以会失败」这句话。
- 昨夜我刚因「装上了→engines 满足」栽过一次(ERR-20261104-004),今夜又在「推演→真实逻辑」上栽;
  **同一类错误在两天内重复出现,说明需要固化成动作,而非只记成教训。**

## ERR-20261105-003 幂等护栏用「执行时刻」当「排程时刻」→ 手动执行会让护栏永久失效

**现象**:公网IP cron 的幂等护栏指令是「比对 `.last_public_ip_run` 与本条 wake 的时间戳」。
但脚本写进状态文件的是**执行时刻**(`date '+%Y-%m-%d %H:%M:%S'`)。
而 cron 排程时刻是 05:30,我手动在 05:32 执行 → 状态文件写 `05:32`、排程时刻是 `05:30` →
**永远不相等** → 护栏每轮都判定「未检查过」→ 重复执行。

**根因**:两个语义不同的时刻被混用:
- **排程时刻**(cron state `lastRunAtMs` / 消息里的 `[System: ...]`)→ 标识「哪一轮排程」,是幂等键
- **执行时刻**(脚本实际运行的 now)→ 只说明「何时跑的」,手动触发时必然不同

**修复**:
1. 脚本支持 `SCHEDULED_AT` 环境变量:传了就写排程时刻,没传才回退执行时刻
2. cron payload 的幂等护栏段明确指示:从 `[System: ...]` 取排程时刻,比较相同则跳过,
   不同则用 `SCHEDULED_AT='<排程时刻>' bash .../公网IP.sh` 执行
3. 状态文件已校正为排程时刻(`2026-11-05 05:30`)

**沙箱验证**:传 → 写排程时刻;不传 → 写执行时刻。

**教训**:
> **幂等键必须选「标识唯一一轮的量」,不能选「顺带记下来的时间戳」。**
> 手动补跑(补做昨天没做的事)是运维常态,任何依赖「执行时刻 == 排程时刻」的幂等判断都会被它击穿。
> 这与 v34「机制性结论会过期」同源:**判据要问「什么情况下会不等」。**

## ERR-20261106-001 Life NightOps 11-04/11-05 连败真因：模型 fallback 链耗尽 → stuck session recovery 主动 abort

**现象**：cron `a6c108aa` 11-04、11-05 连续两场 `error | agent run aborted | OPENCLAW_DIRECT_ABORT`，报告未落盘（11-04/11-05 无 `nightly-life-*.md`）。

**根因**（`/tmp/openclaw/openclaw-2026-11-05.log` 逐条还原）：
1. `embedded_run_failover_decision` 记录 fallback 链逐步耗尽：
   - attempt 1 `minimax/MiniMax-M2.7` → `reason=rate_limit`（429）
   - attempt 2 `litellm/GLM-5.3-Flash` → `reason=billing`（402 余额不足）
   - attempt 3 `litellm/deepseek-flash` → `reason=auth`（apiKey 占位符未解析）
   - attempt 4 `litellm/LongCat-2.0` → `reason=auth`
   - attempt 5 `ollama/qwen3:4b-instruct` → 唯一存活，但**上下文极小**，长报告任务必然溢出
2. 全链耗尽后仍无有效产出 → 触发 `stuck session recovery`：
   `age=465s action=abort_embedded_run aborted=true drained=true` → 直接 abort 内嵌 run
3. abort 产生 `OPENCLAW_DIRECT_ABORT`，`model_fallback_chain_stopped reason=agent_run_direct_abort` → run 判 failed、飞书不投递。

**关键阈值**（openclaw dist `diagnostic-CLWcF7XV.mjs`）：`DEFAULT_STUCK_SESSION_WARN_MS=120s`，`MIN_STALLED_EMBEDDED_RUN_ABORT_MS=300s`，abort 阈值 = `max(300s, 120s×3)=360s`。→ **任何模型链卡住超过 6 分钟就会被主动杀掉**，与内容本身无关。

**已修复（11-06 生效）**：11-03 已把该作业改绑 `model=minimax/MiniMax-M2.7` + fallbacks `minimax/MiniMax-M3.1-Flash → minimax/MiniMax-M3 → ollama/qwen3.6:27b → litellm/deepseek-flash`，避开 litellm 402/auth 通道。11-06 01:50 场 → **ok / succeeded / delivered=true / 204.8s**，consecutiveErrors 归零。

**预防**：
- fallback 链里不能放 402/auth 必失败的 provider，否则真故障时链会被快速耗尽
- minimax 系排在最前，ollama 27B 放末位（32k/131k 上下文比 4B 宽裕）
- 报告型 cron 单次运行必须 **< 6 分钟**，否则触发 stuck-session abort

## ERR-20261106-002 兄弟 NightOps 作业的 sessionKey 与 agentId 不同域 + 上下文模型过小

**现象**：
- `Scout NightOps` / `Orchestrator NightOps` / `Coder NightOps` / `NightOps-Scout` / `NightOps-Life` / `NightOps-Coder` 的 `sessionKey` 全是 `agent:main:main`，而其中 4 个的 `agentId` 是 scout/orchestrator/coder → 与 ERR-20261103-006 同源（失败告警无法投递）
- `Coder NightOps` 连续 4 场 `Context overflow: prompt too large for the model`，实际跑的是 `ollama/qwen3:4b-instruct`（上下文仅 32k）→ **模型降级后上下文窗口不够用**

**已修复**：
| 作业 | sessionKey | 作业级 model / fallbacks |
|---|---|---|
| Scout NightOps | `agent:scout:main` | minimax/MiniMax-M2.7 → M3.1-Flash → M3 → ollama/qwen3.6:27b |
| Orchestrator NightOps | `agent:orchestrator:main` | 同上 |
| Coder NightOps | `agent:coder:main` | 同上 |
| Life NightOps | `agent:life:main` | 同上 + `litellm/deepseek-flash` 兜底 |

**预防**：agent-scoped 作业必须同时校验 `agentId` 与 `sessionKey` 同域、作业级 `model` 不落在小上下文模型上。

## ERR-20261106-003 SQLite session reclamation commit checkpoint expired → target=main 作业成片失败

**现象**：`Scout NightOps` / `NightOps-Life` / `NightOps-Coder` / `Orchestrator NightOps` 多场在 5–30ms 内秒失败，报 `SQLite session reclamation commit checkpoint expired / Sessions remain unavailable. Stop the Gateway, run "openclaw doctor --fix" ... and restart.`

**根因**：Gateway 内 SQLite 会话库回收 Worker 与主线程的 SharedArrayBuffer 握手 5 秒超时。日志里持续刷 `sessions.describe → errorCode=UNAVAILABLE errorMessage=SQLite session reclamation commit checkpoint expired`，且 `Cron maintenance failed` 反复出现。影响面是 `target=main` / 依赖会话库的作业。

**结论**：这是**运行期基础设施问题，无法在作业层绕过**——必须停 Gateway 跑 `openclaw doctor --fix` 再重启。属 owner 决策（需维护窗口），agent 侧只做记录与规避（11-06 已把四个 agent-scoped NightOps 作业的模型链改成 minimax 优先，减少对该链的依赖）。

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## ERR-20261108-001 Life NightOps 场被中断 + NAS 上 du 挂死导致 exec session 无法收尾

**现象**：
1. 本场 cron（01:50 CST）在 02:02 被中断一次，工具层报 error-detected（web_search provider_error + 一个 exec 因 `cd /tmp/life1108` 竞态失败 + ddg.html FileNotFoundError）。**采集数据其实已落盘**（`/tmp/life1108/*.json`），中断只打断在分析阶段。
2. `/mnt/h`（NAS 网络盘）上执行 `du -sh` / `du -sb --apparent-size` 会**长时间挂住不返回**，遗留 exec session `vivid-daisy`（pid 977236）在进程已不存在后仍被 runtime 标记为 running。

**根因**：
1. `mkdir -p X && cd X && ...` 与并行 exec 存在竞态：另一条命令先建了目录、当前 shell 的 cwd 快照不同步 → `cd` 失败导致后续脚本写错路径。并发写同一 /tmp 目录时更明显。
2. NAS 上遍历大目录的 `du` 需读全部文件元数据，网络盘延迟叠加（WSL 目录 22 份 6–9 GB 的 tgz + 回收站 28 份）→ 数十秒到数分钟无响应。`process kill` 后 runtime 侧的 session 状态未及时刷新，出现「process 已死但仍报 running」。

**处置**：
- 恢复时先 `process list` 核对每个 session 的真实状态，**复用已落盘的采集产物，不重跑整轮采集**（本场据此在中断后直接用 `/tmp/life1108/` 的 JSON 完成全部分析）。
- NAS 容量统计改用 `df -h` + `ls | wc -l` + 逐文件 `ls -la` 的近似值，**不用 `du -sh`**；需要精确体积时限定 `--max-depth` 与目录范围。
- 对「process 已消失但 session 仍报 running」：以 `/proc/<pid>` 是否存在为准（`ls -d /proc/<pid>`），不存在即视为已结束，可直接 `process poll` 收尾，不需要反复 kill。

**已追加到 `agents/life/HEARTBEAT.md` 落盘纪律补充（2026-11-08）**，下一场沿用。

**复发证据（2026-11-08 02:1x）**：同一天内再次出现 —— runtime context 持续声明 `nova-gulf running pid=982801` / `wild-fjord running pid=982015`，但两条会话在 `process list` 中已标 `failed`，`/proc/982801`、`/proc/982015` 均不存在，`ps` 扫不到任何 `sleep` 进程。
- **对照实验**：同分钟起一条 `sleep 25` 会话 → pid 983374 在 `/proc/983374` 存在、cmdline 可见、会话结束后消失且 registry 标 `completed`。→ 证明 `/proc` 是可靠判据，runtime context 的 "running pid=" 是**陈旧残留**。
- **无副作用**：两条会话命令体均为纯 `sleep N`，进程消失即无副作用，无需回滚。
- **处置**：对 registry 标 `failed` 但 runtime 仍报 running 的会话，**不信 context，查 `/proc`，确认后直接收工，不再重试 kill**。

<!-- project: /home/zhiping/.openclaw/workspace/agents/life -->

## ERR-20261108-003 LLM idle timeout (120s) 打断 NightOps 长跑 → turn aborted 但产物已落盘

**现象**：11-08 场 Life NightOps（cron `a6c108aa`, 01:50）中途一次模型调用挂死：
`[prompt-error] provider=minimax model=MiniMax-M2.7 api=anthropic-messages error="LLM idle timeout (120s): no response from model"` → 该 turn `stopReason=aborted`，并落 `openclaw:turn-aborted` 事件。

**影响**：本轮后台进程 `vivid-daisy`（NAS tgz 扫描）被 SIGTERM 连带终止（`Termination requested for session vivid-daisy`），ddg.html 未生成 → `FileNotFoundError: 'ddg.html'`。但**三个产物均已正常落盘**（02:05）：
`heartbeat/nightly-life-2026-11-08.md` 33,039 B / `memory/nightly-life-2026-11-08.md` 5,824 B / `agents/life/memory/2026-11-08.md` 3,691 B，写后校验 0 残留、0 乱码。

**根因**：外部网络出口大面积不通（实测 `html.duckduckgo.com` → HTTP 000 连接失败；bing → 302 跳转；reuters → 000），模型在等检索结果时 120s 无 token 返回 → idle timeout 触发 → turn 被打断。**模型侧超时，不是写盘问题**。

**次生**：`ddg.html` 的 `FileNotFoundError` 与 NAS 扫描的 `SIGTERM` 都是这次中断的**下游症状**，非独立故障。

> 与 ERR-20261108-001（同一场，中断点与 NAS du 挂死）为**同一次事故的两个侧面**：001 记的是 exec/进程侧现象，本条记的是模型侧超时触发源。

**预防**：
- 检索类外呼必须自带超时与降级路径，失败即走本地直采，不得让模型挂在等结果上
- 落盘要**分段写**：主报告先落，再补增量，避免整场因单次超时全丢
- 判成败以产物文件为准（本场产物完好），run 状态需单独看 delivery

## ERR-20261108-004 外网出口大面积不可达（B站/知乎/微博/X 以外全挂）

**现象**：本场实测出口结果：`duckduckgo → 000`、`bing → 302 Object moved`、`reuters → 000`。知乎官方 API `api/v3/feed/topstory/hot-lists/total` 返回 **401**（此前多场为 200 直采）。

**影响**：知乎热榜本场退回 tophub 镜像取 50 条；web_search 连续第 N 次不可用，全场靠 curl 直采 + tophub 镜像兜底。

**判断**：非本地故障，是出口/上游侧问题。**未做任何 DNS/代理/证书改动**（越权风险高、且不可逆）。

**预防**：报告里所有「实时直采」结论必须标注该场是否走了降级路径；知乎 401 视为常态降级而非事故。

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

**补充（02:20 复核）**：本场 `vivid-daisy`（pid 977236）在 `/proc` 中已不存在、`process log` 尾部已是 `Process stopped by request (signal SIGTERM)`，但 runtime 的 exec ledger 仍持续将其列为 running，`process kill / clear / remove / poll` 全部返回 `No active session found` / `No finished session found`。→ **这是 runtime 侧的陈旧 ledger 条目，不是真实存活的进程**；判定依据以 `/proc/<pid>` 是否存在为准。不要为此反复重试 kill（已试 6+ 次，纯属噪声）。若要根治需修 OpenClaw 侧的 exec session 回收逻辑，属上游问题。

## ERR-20261108-005 NAS 备份链连续 3 天被空间预检拦截（回收站 123GB 从未被释放）

**现象**（`~/.openclaw-backup.log` 逐条核对，非推测）：
```
[2026-11-06 03:00:01] ❌ NAS 空间不足: 可用 4G < 需要约 6G —— 跳过备份(避免产出损坏归档)
[2026-11-07 03:00:01] ❌ NAS 空间不足: 可用 4G < 需要约 6G —— 跳过备份(避免产出损坏归档)
```
→ `last_backup` 停在 `openclaw-20261105-0300.tgz`，**备份链已断 3 天**（11-06、11-07，11-08 03:00 预计同判）。当前 `/mnt/h` 100% 满、剩 3.8G。

**根因（脚本级，非偶发）**：`scripts/openclaw-backup.sh` 的空间预检逻辑正确（宁误拦不产出损坏归档），但**清理逻辑在 NAS 上是无效的**：
- 脚本 L117-146 已注释此坑：NAS(SMB) 上 `rm` 是「移入 `#recycle` 回收站」而非真删 → 空间不释放。
- 清理只扫 `$BACKUP_DIR`（`/mnt/h/AI/openclaw.zone/WSL`），**从不清理 `#recycle` 目录** → 回收站只增不减。
- 脚本末尾仅打印「⚠️ 回收站仍有 N 份未释放空间，需人工确认后清空」—— **告警不等于动作，链就一直断着**。
- 脚本自己也承认：`RETAIN_DAYS=30`，但回收站里全是 08-27～10-13 的归档（27 份），远超阈值仍占着空间。

**占用实测**（用 `find -printf '%s'` 逐文件求和，**不用 `du`**——NAS 上 du 会挂死，见 ERR-20261108-001）：
| 位置 | 份数 | 体积 |
|---|---|---|
| `/mnt/h/#recycle/AI/openclaw.zone/WSL` | 27 | **123.0 GB** |
| `/mnt/h/AI/openclaw.zone/WSL` | 22 | 156.5 GB |
| 合计 | 49 | ~280 GB |

**结论**：只要清空回收站即可回收 **约 123 GB**，远超 6G 预检阈值 → 备份链立即恢复。

**为何未执行**：清空 `#recycle` 是**不可逆删除**（NAS 上无二次回收），且需 owner 授权。

**建议（待 owner 决策，本场未执行）**：
1. 清空 `/mnt/h/#recycle/AI/openclaw.zone/WSL/` → 回收约 123 GB，备份链立即恢复
2. 把 `RETAIN_DAYS` 从 30 调到 14，并让清理步骤**绕过回收站**（NAS 侧真删，或先移出 NAS 再删）
3. 脚本在检测到「回收站 > 阈值」时，除了告警还应写入 heartbeat 异常清单，避免连续 3 天静默断链只留一行日志

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## ERR-20261108-006 备份脚本的邮件通道早于预检失败，且失败原因被静默吞掉

**现象**：`logs/backup-cron.log` 里有 14 条 `❌ 发送失败:`（12 条 `Connection unexpectedly closed`，2 条 `[Errno -3] Temporary failure in name resolution`），但**没有一条出现在 11-06/11-07 的「空间不足」拦截记录旁边** —— 因为预检失败路径**根本没发邮件**。

**根因（脚本级）**：
- 空间预检失败分支（脚本 L259-265）是 `log` + `write_heartbeat` + `exit 1`，**没有 `send_mail`**；而 tar 失败分支（L346-347）有 `send_mail`。→ **最该通知的「备份没做成」反而是静默的**，owner 只在 `~/.openclaw-backup.log` 和 `~/.openclaw-backup.heartbeat` 里能看见，日志里一片空白。
- 邮件失败本身也不回写心跳：`send_email.py` 捕获异常后只 `print(f"❌ 发送失败: {e}")` 到 **stdout**（L113），而脚本 `send_mail()` 只把 **stderr** 重定向进 `$LOG_FILE`（L106 `2>>`）→ 失败详情落到 cron 的 stdout（`backup-cron.log`），`~/.openclaw-backup.log` 与心跳文件里**看不到任何失败痕迹**。
- 症状与连通性其实不匹配：实测 `smtp.qq.com:587` 与 `smtp.gmail.com:587` **TCP 均可达**（`socket.create_connection` 成功）；脚本内 QQ 会切到 `SMTP_SSL:465`（send_email.py L87-91），`Connection unexpectedly closed` 更像是 **587 STARTTLS 路径与 465 SSL 路径混用/对端主动断连**，不是 DNS 或端口不通。
- 另注：`~/.openclaw-backup.log` 里 11-06/11-07 出现「备份已在运行，退出」+ 后续预检拒绝，是 `flock` 与同一次 cron 内的日志交错，**不是并发备份**。

**结论**：本条**不是新故障**，而是**告警链断路的证据**——正是它解释了为什么「备份断 3 天」这件事直到今天才被追查出来。

**建议（待 owner 决策，本场未改脚本）**：
1. 空间预检失败分支补 `send_mail`，与 tar 失败分支对齐
2. `send_email.py` 的失败信息改写 **stderr**，或 `send_mail()` 改成 `>> "$LOG_FILE" 2>&1`，确保失败进 `~/.openclaw-backup.log`
3. `send_mail` 返回值纳入判断，失败时把结果写进 `write_heartbeat` 的 `detail`
4. 顺手验证 QQ 邮箱到底走 465 SSL 还是 587 STARTTLS，统一到一个路径

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## ERR-20261108-007 NAS 回收站内容明细：27 份全是 08-27～10-13 的过期归档，缺口仅需 2 份

**补充到 ERR-20261108-005**：实测 `~/.openclaw-backup.heartbeat` 的预检缺口比预估小得多。

**实测数据**（`find -printf '%T@ %s %f'` 逐条）：
- 回收站 27 份全部为 **2026-08-27 ～ 2026-10-13** 的归档，**最老 2 个半月**，全部远超 `RETAIN_DAYS=30` 阈值 —— 它们本该在清理时被清掉，却因为「NAS rm = 移入回收站」的语义一直赖着不走。
- 体积分两档：08～09 月档 3.8–4.3 GB/份（16 份）、10 月档 5.8–6.1 GB/份（10 份）。
- `openclaw-20261005-0300.tgz` 体积 **0 字节** —— 10-05 那次 tar 损坏归档的残骸，**零风险可直接删**。

**关键结论：缺口只有约 2G。** 预检要 `NEED_GB=6`，NAS `AVAIL_GB=4` → 差 2G。**只需清掉回收站里任意 1~2 份归档（4.2–6.5 GB/份）即可让今晚 03:00 的备份通过**，不必全清 123 GB。

**最小动作方案（待 owner 授权，本场未执行）**：
- 方案 A（最小、立即生效）：删 `openclaw-20261005-0300.tgz`（0 字节残骸）+ 任意 1 份 08～09 月档（4.25 GB）→ 回收 ~4.25 GB，AVAIL 4G → 8G+，预检通过
- 方案 B（治本、可回滚）：把回收站内容先 `mv` 到本地 `/dev/sdd`（**790G 可用**）→ 再由 NAS 侧删除 → 确认 NAS 空间释放后再删本地副本。中转可回滚，代价是需 I/O 搬运
- 方案 C（一次性清空）：全清 27 份回收站 → 回收 123 GB，备份链彻底恢复

**为何仍未执行**：NAS 上 `rm` 的语义是「移入回收站」→ 对回收站内的文件再次 `rm` 是否真删，**未经实测不能假设**；且不可逆删除需 owner 授权。

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## ERR-20261116-001 自检命令用 `tr -d ' \t\r\n'` 把日期里的空格也删了 → 误报「读回不一致」

**现象**:写完 v37 后按「新规则」做读回校验:
```bash
SAVED=$(tr -d ' \t\r\n' < ~/.openclaw/.nightops-discussion-last)
# → 2026-11-1623:20   ← 空格被删,误判为「标记写入失败」
```
**真相**:文件内容完全正确(`2026-11-16 23:20`,17 字节含换行,`cat -A` 确认),
`cut -c1-16` 读出来就是 `2026-11-16 23:20` ✅。是**校验命令本身**有 bug。

**教训**:
- **「去空白」类预处理会破坏有意义的分隔符**。日期时间里的空格是内容的一部分,不是噪声。
  要去行尾空白用 `sed 's/[[:space:]]*$//'` 或 `cut -c1-16`,不要 `tr -d`。
- 与 ERR-20261101-001(read 截断 → 覆盖 3594 行)是同一类:**「加工后再比对」比「原样比对」脆弱得多**。
  → 自检应**原样读取并与期望字符串直接比较**,中间不做任何字符变换。
- 讽刺的是:v37 新增的规则正是「写完立刻读回校验」,而我实现这条规则时**第一步就写错了校验**。
  → **规则要落地,先把它自己的实现测一遍。**

## ERR-20261122-001 SQLite 回收 checkpoint 过期问题横跨两周、跨重启仍未自愈（状态复查）

> **【11-24 追补修正】** 本条此前把根因判为「多 agent 库 degraded / 需 `doctor --fix`」，**该归因已被推翻**：库本身完全健康（`integrity_check` 通过、`issues=0`、写锁可立即获取）。真实根因是**启动期并发竞态**——重启时多个 agent 同时做 WAL 恢复与 canonical-validation，两个 5 秒超时（`COMMIT_DECISION_TIMEOUT_MS` 与 `OPENCLAW_SQLITE_BUSY_TIMEOUT_MS`）相等导致互相等锁到点，失败结果被记进**进程内存**的 `refusalsByState`，`doctor` 改不掉（诊断路径遇 startup 来源直接 return）。每次重启换一个受害 agent（finance/orchestrator/main → work）。**详见 ERR-20261124-001。**


**背景**：ERR-20261106-003 / ERR-20261103-006 记录的 `SQLite session reclamation commit checkpoint expired` 在 11-16 之后的**全新 Gateway 进程**（pid 695，启动于 11-22 21:38 前）上**依然复现**，说明它不是「跑久了才坏」，而是**可复现的状态残留**。

**本次实测证据**（`/tmp/openclaw/openclaw-2026-11-22.log`）：
- `session-sqlite` 线程 17 的 `reclamationKind=canonical-validation` worker 操作 `elapsedMs=8692 outcome=rejected`，报错位置固定在 `dist/session-accessor.sqlite-reclamation-commit-BX3N0u2L.mjs:25:88`。
- 随后 `state/agent-admission` 判 `agent database remains degraded`（agentId=finance / orchestrator），`phaseDurationsMs` 显示 `activation=8689 / readiness=12592 / migration=8871` —— **每个 agent 的准入要花 35s+**。
- 连锁后果：`Cron maintenance failed` 持续刷屏、`memory-core: dreaming sweep/startup cleanup failed`、`Orchestrator NightOps` 与 `NightOps-Coder`(308d445d) 与 `7df2f5c0` 三类 cron 作业直接 `error`。

**关键判断（与 11-06 结论一致，但补充了「重启无效」）**：11-06 我判断「需停 Gateway + `openclaw doctor --fix` + 重启」；本次验证发现 **11-16~11-22 期间 Gateway 显然已重启过**（新 pid、日志全新），而故障**原样复发** → 单纯重启**不解决问题**，必须跑 `doctor --fix` 做一次实际修复，且很可能需要**逐 agent** 修复（finance / orchestrator / main 都出现了 degraded）。

**影响面扩大**：`Heartbeat (main)` 现为 `skipped`；`【NightOps 记忆体系讨论】`(db2fae49) 报 `Agent main has not completed startup inspection` —— main agent 本身也未通过准入。

## ERR-20261122-002 备份脚本 `local` 报错已由作者修复，但 11-16 那次仍产出了损坏归档

**现象**：`logs/backup-cron.log` 第 69 行 `[2026-11-16 03:00:01]` 有
`openclaw-backup.sh: line 275: local: can only be used in a function` → 该次备份的回收站探测段执行异常。
**现状**：脚本 L270-281 已加注释说明「★ 修复 (2026-11-16)：此处原为 `local recycle_dir nas_root rel`… 函数体外只能是全局，去掉 local 即可」，代码现为 `recycle_dir="" nas_root="" rel=""` —— **已修复**，`local` 报错在 11-16 之后未再出现（`grep -c` = 1，仅历史那一条）。

**但 11-17 的归档有残留问题**：`~/.openclaw-backup.log` 显示 `[2026-11-17 03:00:01] tar 退出码: 1`，同时又记「备份成功: openclaw-20261117-0300.tgz (5.8G)」—— **tar 非零退出却仍标记成功**。这是比 `local` 报错更实质的问题：**退出码没被当作失败判据**。

**当前 NAS/备份状态（11-22 21:45 实测）**：
- `/mnt/h` 可用 **380G**（95% 使用率）→ 空间预检已**不再是瓶颈**（早期 11-08 那次 3.8G 的危机已自行缓解，回收站现只剩 1 份 6.5GB）
- `~/.openclaw-backup.heartbeat`：`last_backup=openclaw-20261117-0300.tgz` / `hours_since_last_backup=138` / `need_backup=true` / `status=starting` → 11-18～11-22 连续 5 场 03:00 备份**没有产出**
- 21:38 有一场**手动/被触发**的备份正在跑（`openclaw-backup.sh` pid 309，`native-backup.sh` → `openclaw backup create --verify` pid 394 → tar pid 1834），产出 `openclaw-20261122-2138.tgz`（已 5.15G，仍在写）

**结论**：空间问题已解，但**「tar 退出码非零仍标成功」+「连续 5 天没产出却只有 heartbeat 能看出来」**这两个问题仍在 —— 与 ERR-20261108-006 的告警链断路同源。

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

## ERR-20261122-003 OpenRouter 402 余额耗尽触发 error-detected 误报，且 `total_usage=0` 指向 key 绑错账户

**现象**：11-22 21:43–21:46 手动补跑 `news_digest` 时，摘要阶段对每个新条目都打一条
`WARNING - OpenRouter API 错误: 402 - {"error":{"message":"Insufficient credits. This account never purchased credits..."}}`，
单次运行 **8 条**。这些 WARNING 出现在 stdout，被 exec 的 error-detected 扫描器捕获 → **连续三条「tool error」信号实际是日志噪声，不是工具失败**。

**根因（本次新增关键线索）**：用 `~/.secrets/openrouter_api_key` 实测 `GET https://openrouter.ai/api/v1/credits` →
`{"data":{"total_credits":0,"total_usage":0}}`。
**`total_usage` 也是 0** → 这个 key **从未被真正计费调用过**，说明问题不是「余额用完了」，
而是 **key 绑到了未关联计费账户 / org 的账户**，或该账户从未购买额度。**先核对 key 归属，再谈充值** —— 充值到错账户无法退回。

**已有处置链是有效的**：`openclaw_news_digest.py` 的 LLM 后端顺序（OpenRouter → OpenAI → Anthropic → DeepSeek → MiniMax）
在 8 次 402 后**全部由 MiniMax 回退兜住**，30 条摘要无缺失，邮件三收件人 + 飞书 `om_x100b7f1b6f8830a0ddeba5853e5a2c8` 均送达。
→ **回退链已可写入运维手册作为长期备选路径**，无需为 OpenRouter 中断 news_digest。

**纪律**：
- 额度类报错**只写入异常清单并告知 owner，不自行反复重试、不自行充值**。
- 后续遇到 exec 输出里含 `402` / `Insufficient credits` 字样，**不要按工具失败处理**，这是采集脚本的正常降级日志；
  判断「产物是否落盘 + 推送是否送达」要以文件与 message_id 为准，不要以 stdout 有没有 ERROR 字样为准。

<!-- project: path:/home/zhiping/.openclaw/workspace/agents/life -->

## ERR-20261124-001 SQLite checkpoint 过期：**不是库坏了，是「启动期并发抢锁」的竞态**，每次重启换一个受害 agent

**一句话根因**：Gateway 启动时 6 个 agent 同时做「进程死亡后 WAL 恢复」的完整性闸门，`work` 的 canonical-validation 回收 worker 与另一条 certify 写入互相等锁，**两边的超时都是 5 秒**，必然同时到点 → worker 判定「提交授权过期」→ 把 `work` 判为 degraded → **该 agent 在本次 Gateway 进程生命周期内永久不可写**。

> **【11-26 计数修正】** 本条原写「11-24 全天 166 条、work 占 136 条」——**这个数是错的**，它只统计了 `/tmp/openclaw/openclaw-2026-11-24.log` 这个**轮转窗口内的部分**（当时日志只到 02:05）。用 `journalctl` 按自然日重算的真实值是：**11-24 全天 1,732 条 / 11-25 全天 1,725 条**（两者基本持平，**不是**「暴增」）。**教训**：跨天的错误计数必须用 `journalctl --since/--until` 按自然日取，**不能用 `/tmp/openclaw/openclaw-YYYY-MM-DD.log` 直接 grep** —— 该文件按大小轮转，**当天早上读到的只是前一晚到当天的片段**，会低估一个数量级。

**证据链（本次实测，11-24 02:00–02:20）**：

1. **触发点是重启，不是运行期**。11-23 04:42 新 Gateway（pid 36001）启动时，旧进程（pid 695）**关闭失败**：
   `shutdown step failed (gateway close): Plugin runtime still owns resources ... Direct shared-state reader requires current integrity admission`
   → 新进程启动后 6 个 agent 全部走 `agent database integrity gate`，`because=same-boot-dead-owner-wal-recovered` / `integrityGateReason=process-death` / `mode=deferred`。
2. **竞态发生在启动后 30 秒内**（20:43:07–20:43:15 UTC）。同一时刻：
   - `slow SQLite transaction hold`：**work 库**，`operation=session.canonical-validation.certify`，`elapsedMs=5001`，`phases={beginMs:1, sqlMs:5001, commitMs:0}` → certify 自己的 `BEGIN IMMEDIATE` 被**卡满 5 秒**（busy_timeout 用尽）。
   - `slow SQLite session write`：scout 13506ms、**work 13585ms**，`reclamationAdmissionId=1` → 两个 agent 的 certify 并发在抢。
   - `slow SQLite reclamation Worker operation`：`reclamationKind=canonical-validation`，`elapsedMs=14454`，**`outcome=rejected`**，报错锚点 `session-accessor.sqlite-reclamation-commit-BX3N0u2L.mjs:25:88`。
3. **两个 5 秒是同一个数字**（源码确认）：
   - `session-accessor.sqlite-reclamation-commit-BX3N0u2L.mjs:4` → `const COMMIT_DECISION_TIMEOUT_MS = 5e3`，worker 用 `Atomics.wait(shared,0,REQUESTED,5000)` 等主线程授权提交。
   - `openclaw-state-db-contract-CYdyW5CE.mjs:80` → `OPENCLAW_SQLITE_BUSY_TIMEOUT_MS = 5e3`，certify 的 `BEGIN IMMEDIATE` 等锁上限也是 5 秒。
   → **等待方与被等待方同时到点**，worker 必然拿不到授权 → `compareExchange(REQUESTED→COMMITTING)` 失败 → 抛 `SQLite session reclamation commit checkpoint expired`。
4. **失败会「粘住」整个进程生命周期**。源码 `agent-database-admission-BjKNx4ry.mjs`：
   - 拒绝结论存在**进程内存** `refusalsByState`，只有 `source="startup"` 的新准入批次能覆盖；
   - 诊断路径 `source==="diagnostic"` 遇 `source==="startup"` **直接 return**（L190）→ **`doctor` 永远改不掉它**；
   - 全文件**没有任何 `refusalsByState.delete/clear`** → 本次 boot 内不可恢复。
   → 这解释了「为什么 doctor 报 issues=0 / integrity=ok，但运行时一直拒绝」。
5. **受害 agent 每次重启都换人**（与「某个 agent 库坏了」无关）：
   - 11-22 及之前：finance / orchestrator / main
   - 11-23 04:42 那一脚：**work**
   → 是**竞态**，谁输谁中招。
6. **可观测后果**：`work` 库自 **11-23 04:42 起写入全部失败**（主库 mtime 停在 04:42:10，wal 0 字节）；`session-entry.patch` 失败 11-24 全天 **136 次**（占全天 checkpoint 错误 166 条的 82%，**其余 7 个 agent 零命中**）；`Heartbeat (work)` `consecutiveErrors=24`；`Cron maintenance failed` 今日 **129 次**；`state/openclaw.sqlite` 的 `delivery_queue_entries` 里 **1 条 pending 卡死**（`4c89a409…`，`retry_count=131`，`recovery_state=unknown_after_send`）。

**为什么 `doctor --fix` / `inspect` / `validate` 都没用**（本次实测）：
- `doctor --session-sqlite inspect --session-sqlite-all-agents` → **8 个 agent 全部 `issues=0, integrityCheck=ok`**；
- `doctor --session-sqlite validate --session-sqlite-agent work` → `targets: []`（空集）；
- `doctor --session-sqlite inspect --session-sqlite-agent work` → `sqliteEntries=4`、`issues=0`、`integrityCheck=ok`；
- 手工只读校验：`PRAGMA integrity_check` 正常、`freelist_count=1`、`journal_mode=wal`、`BEGIN IMMEDIATE` 立即拿到写锁（0.0s）→ **库本身完全健康**。
→ 结论：**这是纯运行期竞态 + 内存态拒绝，不是数据损坏**。任何「修库」动作都是空转。

**对先前结论的修正（重要）**：
- ❌ 11-06 / 11-22 的「重启无效」——**方向对但归因错**。重启确实没用，但不是因为库坏了，而是因为**每次重启都会重跑同一场竞态**，只是换个人中招。
- ❌ 11-22 的「必须 `doctor --fix`」——**这条 repairHint 是通用文案，对本故障无效**（doctor 改不了内存态拒绝）。
- ✅ 正确表述：**降低启动期并发 + 避免脏关闭**，让竞态不发生；发生后**只能靠「一次干净的重启」侥幸不中招**。

**待 owner 决策（本场全程只读，未做任何写操作 / 未重启 / 未改脚本）**：
1. **主修复方向**：让启动期 canonical-validation 不并发。或等上游把 `COMMIT_DECISION_TIMEOUT_MS` 与 `OPENCLAW_SQLITE_BUSY_TIMEOUT_MS` 拉开（现在**相等**是竞态成立的充要条件）。
2. **规避**：干净关闭 Gateway（消除 `process-death` / WAL 恢复路径），且**避开有 agent 在跑时重启**；或临时减少同时启动的 agent 数。
3. **取证给上游**（本故障最有价值的产出）：
   `openclaw doctor --session-sqlite recover --session-sqlite-agent work --github-issue`
   —— 会生成脱敏 issue 报告；本次已把上面的证据链整理好，可直接附上。
4. **解卡死的投递**：那条 pending 的 `4c89a409…` 需要 work agent 恢复可写后才会自然重投；不要手工改 `delivery_queue_entries`（会丢投递语义）。
5. **恢复优先级**：`work` 目前完全不可写（写入 0 落地），但它只是 8 个 agent 之一，main/life/scout/coder/finance/health 全部正常 → **不影响今晚 Life NightOps 等主流程**，可排在非高峰处理。

**教训**：
- 「静态检查全绿」≠「运行时可用」。SQLite 这层要把 **`doctor inspect`（静态）+ `integrity_verifications`（关闭态）+ 运行时写入成功率** 三者合看，缺一不可。
- 遇到「重启后换了个 agent 犯同样的错」，第一反应应是**竞态/共享资源**，而不是「这个 agent 的库坏了」。
- OpenClaw 的 `repairHint` 是**通用文案**，不要当作已验证结论直接执行；本次它误导了两周（11-06 → 11-22）。
- 读 `dist/*.mjs` 源码里的**超时常量并两两比对**，比翻日志快得多——本案两个 5 秒一比即中。

<!-- project: path:/home/zhiping/.openclaw/workspace/agents/life -->

## ERR-20261124-003 runtime 上下文的「Active exec sessions」会持续显示已结束的 session

**现象**:连续 4 个轮次,runtime 上下文都列出同一对 session 为「running」:
```
- delta-cedar running pid=78822
- good-ridge running pid=78836
```
**权威核实(两种独立方法,结果一致)**:
```
方法1 process list(实时查询):
  实时 session 总数 6,running 数 = 0
  delta-cedar → status=failed  (runtimeMs=156524)
  good-ridge → status=completed (runtimeMs=100225)

方法2 /proc 存在性(4 次):
  /proc/78822 不存在
  /proc/78836 不存在
  全 ps 扫描:无匹配进程
```
→ runtime 上下文是**注入的静态快照**,不随 session 结束而刷新。

**教训**:
- **runtime 上下文不可作为「进程是否活着」的判据**,必须用 `process list` 或 `/proc` 实测。
- 误信它会导致两种浪费:
  ① 反复尝试 kill 一个已结束的进程(本轮做了 4 次,全部 No session found)
  ② 在报告里把「已结束」误写成「僵留未清」
- 与 ERR-20261030-003 是同一现象的延续,本次补上了「多次核实 + 两种方法交叉验证」的完整判据。

## ERR-20261124-002 code-mode exec 里塞 bash heredoc + 反引号会触发 JS SyntaxError 且窗口卡死

**现象**：
- 在 `exec` 的 code-mode 单元里写 `const r = await exec({ command: <template literal 内含 cat > /tmp/x.py <<EOF ... EOF> })`，当 heredoc 内容含**反引号、`${}` 或中文标点**时，整个 code-mode 单元直接 `SyntaxError at openclaw-code-mode:user.js:12:2: Unexpected token`，**所有工具都没被派发**（no tools were dispatched）。
- 同一批单元若把 journal 全文回灌进 template literal，还会触发 `model idle timeout (120s)`。

**处置**：
1. **heredoc 内容不要放进 JS template literal**。用 `write` 工具把脚本写到 `/tmp/x.py`，再 `exec` 跑它；或用 `lines = [...].join(chr(10))` 的普通字符串数组构造（不含反引号）。
2. 大输出**不要**回灌进 code-mode 单元；改成写文件后只取需要的字段（`grep | cut -c1-200`）。
3. `exec` 里直接写 `python3 - <<PY ... PY` 且内容含中文/引号 → 同样炸。**正确做法是先 `write` 再 `exec`**（本次调查全程遵守后未再复发）。

**元数据**：状态 ✅ 已归档；关联：本次 WSL 失联调查（11-24）

## ERR-20261125-001 code-mode 里原生工具是**全局函数**，不是 `tools.` 下的属性

**现象**：
- 在 `exec` 的 code-mode 单元里写 `await tools.exec({...})` → `ReferenceError: tools is not defined`，整个单元失败。
- 写成 `await tools.apply_patch({...})` → 同样 `tools is not defined`。
- 更早一次：`exec` 单元漏传 `title` 参数 → `Validation failed for tool "exec": title: must have required properties title`。

**根因**：code-mode 单元里，原生工具名（`exec` / `apply_patch` / `edit` / `write` / `progress_card` / `process`）已经是**顶层全局函数**，直接调用即可；`tools.` 这种命名空间写法只适用于 MCP 工具（`MCP.<server>.<tool>`）。另外 `exec` 的 `title` 是**必填**。

**正确写法**：
```js
const r = await exec({ command: "...", timeoutSeconds: 45 });   // 不写 tools.
const p = await apply_patch({ input: "*** Begin Patch\n..." });  // 不写 tools.
```

**元数据**：状态 ✅ 已归档；关联：备份保留策略改造（11-25）

## ERR-20261125-002 apply_patch 的 patch 文本会被 JS 模板字符串吃掉 `\t` / `\n`

**现象**：往脚本里加 `find -printf '%T@\t%p\n'` 这类带 `\t` `\n` 转义的行时，`apply_patch` 报 `Invalid patch hunk at line 21: Expected update hunk to start with a @@ context marker`——因为 JS 模板字符串把 `\t` `\n` 解释成了**真实制表符和换行**，把一行 patch 劈成了两行。

**处置**：模板字符串里改用 `\\t` `\\n`（双写反斜杠），让 patch 文本里保留字面量 `\t` `\n`。同理 `\\` 续行符也要双写。

**元数据**：状态 ✅ 已归档；关联：备份保留策略改造（11-25）

## ERR-20261125-003 验证「份数上限」闸门时，别用跨月造档 —— 天数闸门会先误伤

**现象**：造 20 份假档测「只留最新 15 份」，第一次结果只剩 **5 份**，一度以为份数闸门写错（应该剩 15）。实际是**天数兜底闸门（`-mtime +90`）先删了 15 份** —— 造的假档日期跨了 8 个月，被判为超期。

**教训**：两个闸门串联时，测试必须**只让被测闸门生效**。隔离做法：① 假档日期全设在「最近 N 天内」（压住天数闸门）；② 或用 `awk` 把 `cleanup_old()` 函数体单独抽出来，在隔离环境里 source 后调用。

**元数据**：状态 ✅ 已归档；关联：备份保留策略改造（11-25）

## ERR-20261126-001 11-25 四个 NightOps 全被「stuck session recovery」杀掉 —— 根因是 Token Plan 2056 额度耗尽，不是 SQLite

**现象**：11-25 01:50–02:40，Scout / Life / Coder / Orchestrator **四个 NightOps 连续失败**，错误一律是 `agent run aborted | OPENCLAW_DIRECT_ABORT`，`consecutiveErrors=1`，**四场全部 0 产物落盘**（`heartbeat/nightly-life-2026-11-25.md` 等全不存在）。这与 11-24 的 SQLite 故障表现完全不同，**是两个独立问题**，一度容易被混为一谈。

**根因链（已定位）**：
1. MiniMax 返回 **HTTP 429**，body 为 `{"error":{"message":"已达到 Token Plan 用量上限：请升级 Token Plan 套餐或购买积分补充用量。 (2056)","type":"rate_limit_error"}}`。
   → **这是 Token Plan 额度耗尽（2056），不是普通限流**。11-25 全天 72 处提到 2056/Token Plan，429 集中在 17–19 UTC（01–03 CST）**每小时 57–63 次**。
2. 模型调用持续失败 → `embedded run failover decision`（`failoverReason=rate_limit`, `status=429`, `retryCount=9`, `profileId=sha256:c38c74a5066a`, `provider=minimax`, `model=MiniMax-M2.7`）→ 回退模型也没救回来（`model_fallback_chain_stopped`, `reason=agent_run_direct_abort`）。
3. 每次 run 卡住 → OpenClaw 的**自愈机制**介入：
   `stuck session recovery: sessionId=... sessionKey=agent:life:cron:a6c108aa:... age=370s action=abort_embedded_run`
   → 到达 365–398 秒阈值就被主动 abort。
4. → `lane task error: lane=cron-nested ... errorName=AbortError` → cron 判 error。

**关键判据（下次可直接套用）**：
- **看 `age=`**：`stuck session recovery` 里的 age 落在 **365–398s** 一线 → 说明是**被自愈机制按超时杀掉**的，不是业务逻辑报错。
- **看 failover 决策的 `status` + `rawErrorPreview`**：429 + `2056` = 额度问题（外部约束，只能告知 owner）；429 无 2056 = 普通限流（可重试/退避）。
- 四场 NightOps **同一时间窗、同一种错误、同样 0 产物** → 是**上游共性故障**（模型额度），不要逐个 agent 去查各自的问题。

**与 SQLite 故障的区分（11-24 vs 11-25，两个独立问题）**：

| | 11-24 SQLite 故障 | 11-25 NightOps 全灭 |
|---|---|---|
| 错误 | `SQLite session reclamation commit checkpoint expired` | `agent run aborted \| OPENCLAW_DIRECT_ABORT` |
| 影响 | **只 1 个 agent**（work），其余 7 个正常 | **4 个 agent 同时**，全灭 |
| 错误源 | 本地 SQLite 写入层 | **外部模型额度**（429/2056） |
| 产物 | 其他 NightOps 正常产出 | **四场 0 产物** |
| 触发 | 重启后启动期竞态 | 额度耗尽 + stuck recovery 超时杀 |

**11-26 复核（01:00）**：额度已恢复 —— 今日 `model-fetch` **147 次 status=200 / 3 次 429**；Life NightOps 已改期到 **00:59**（`scheduleActivatedAt=11-25 23:23:44`）并于 00:59 启动，当前运行中（上游 `heartbeat/nightly-scout-2026-11-26.md` 00:44 已产出 21,212 B）。
→ **改期是 owner 在 11-25 23:23 做的**（`openclaw.json` mtime 11-25 00:36，cron 注册表在 `automations/jobs.json`），本次**未做任何改动**。

**SQLite 故障仍在持续（非新增，仅状态）**：`work` agent 自 11-23 04:42 起写入仍全冻结（主库 mtime 停在 04:42:10）；11-26 凌晨日志内 checkpoint 错误 89 条（**注意：这是 00:00–01:03 的片段口径，非全天**），**逐条核对 `refusal.agentId` 全部是 `work`，无第二个受害 agent**；`Heartbeat (work)` 仍 `consecutiveErrors=24`；Gateway 仍是 pid 36001（已连续运行 2 天 20 小时，未重启 → 该 agent 在本 boot 内不可能自愈，机制见 ERR-20261124-001）。

**备份归档完整性：已实证「退出码 1 ≠ 归档损坏」（推翻一个此前的疑虑）**
从 `openclaw-20261125-0300.tgz`（退出码 1 那份）解出三个关键库并校验：
`agents/main/agent/openclaw-agent.sqlite`（243,752,960 B，`integrity_check=ok`，session_nodes 1,896 / transcript_events 50,592 / session_windows 2,067）、`agents/work/agent/openclaw-agent.sqlite`（ok）、`state/openclaw.sqlite`（ok）。
→ stderr 的 `File removed before we read it`（`.sync-staging/` 被清理）与 `File shrank by 532480 bytes; padding with zeros`（main 的 sqlite 备份期间缩小）**在 tar 语义下只是警告**，归档可正常解出且 SQLite 校验通过。
→ **修正结论**：脚本 `BACKUP_STATUS <= 1` 判成功，在「归档可用性」维度**站得住**；它吞掉的是「归档与源目录有瞬时差异」这一信息（热备必然如此），外部健康检查因此看不出差异。**是否收紧为 `== 0` 需 owner 权衡**（收紧会更频繁报失败/删半成品）；更精准的做法是**把 `.sync-staging/` 加进 tar exclude**（临时目录本就不该进备份），大概率能让退出码回 0 而不牺牲热备份。

**纪律**：
- **额度类 2056 只告知 owner，不自行重试、不自行充值**（沿用 ERR-20261101-002 / ERR-20261122-003 的约定）。
- **多场同窗同错 → 先判上游共性**（模型额度 / 网络 / 磁盘），再考虑逐个排查。
- **判「agent 失败」与「agent 被杀掉」**：看有没有 `stuck session recovery ... action=abort_embedded_run` + `age=` 数值；有 = 被超时杀，不是自身报错。

<!-- project: path:/home/zhiping/.openclaw/workspace/agents/life -->


## ERR-20261127-001 — session-health-checker 三次返工:v1 违规读 live DB / v2 证据不足判 P0

**时间**: 2026-11-27 05:30–06:10 CST
**组件**: `scripts/session-health-checker.py`（v42 新增的会话健康度检查工具）

### v1 — 违反 OpenClaw 工具策略

用 python `sqlite3.connect()` 直接打开 `~/.openclaw/agents/*/agent/openclaw-agent.sqlite`。
OpenClaw 明确拒绝:
```
external sqlite3 cannot open databases under the active OpenClaw state directory.
Use OpenClaw commands for live state, or inspect a private backup copy outside OPENCLAW_STATE_DIR.
```
日志里表现为 `[tools] exec failed` + `agent:work` 的 lease refusal 噪音。

**修法**: 数据源换成官方只读接口 `openclaw sessions --all-agents --json`。
它直接给 `totalTokens` / `contextTokens` / `abortedLastRun`,比数 transcript 条数更准
（条数是内部存储量,token 数才是模型上下文占用）。
中间试过「从备份 tar 解出 DB 副本再读」——网络盘 6GB tar 解压太慢,放弃。

### v2 — 证据不足却下断言

`openclaw database ownership status` 只管共享状态所有权,不管 agent lease。
取不到 lease 列表时代码走了 `if ag not in leased` 分支,而 `leased` 是空集
→ **7 个 agent 全被判成 P0**,而实际只有 work 是 P0。

**这与 v42 的核心结论直接冲突**: 「校验/闸门必须用『必然命中』样本证明其会失败,
否则『通过』不能构成证据」—— 同一个错误的另一个方向:
**没有证据 ≠ 有问题的反面**,取不到数据时正确的行为是**明说不可判定**,而不是判成最坏。

**修法**: lease 判定改为**日志证据**启发式 —— 日志里 `active-leases` receipt ⇒ 当时持有 lease,
`reclamation commit checkpoint expired` refusal ⇒ lease 已失效。
两者都不出现的 agent 标为 `unknown`（不可判定），**不判 P0**。

### v3 — 最终形态

- 数据源: `openclaw sessions --all-agents --json`（官方只读）
- lease: 日志证据推断,分 `held` / `broken` / `unknown` 三态
- 分级: P0 lease 失效 / P1 上下文超限 / P2 逼近上限或上次被 abort
- 实跑结果: P0=1(work) / P1=2(coder 542k, scout 434k token) / P2=2(life 143k, orchestrator)
- 退出码: 有风险 → 1, 无风险 → 0, 数据源不可用 → 2

### 通用教训

**「取不到数据」和「数据表明没问题」是两个完全不同的状态**,实现里必须分开表达。
把空集当作「都不满足条件」来用,是检测工具最常见的一类假阳性。

---


## ERR-20261127-002 — Code Mode 嵌套引号:JS → shell → python 三层转义反复炸

**时间**: 2026-11-27 05:30–06:45 CST
**组件**: OpenClaw Code Mode (exec/write/process 工具调用)

### 现象

本轮连续 5 次因引号/转义失败而中断,其中 2 次被 error-detected 显式捕获:

| # | 报错 | 触发写法 |
|---|---|---|
| 1 | `SyntaxError: Unterminated string constant` (openclaw-code-mode:user.js:1:33) | JS 字符串里嵌反斜杠转义引号,再嵌 shell 的 `python3 -c`,再嵌 python 的 dict key |
| 2 | `SyntaxError: unterminated string literal` (Python) | `python3 - <<EOF` heredoc 里写三引号字符串,而内容含双引号 |
| 3 | `ReferenceError: tools is not defined` | 用了 `tools.process(...)`;但本环境里工具是**裸全局函数**(`process`/`exec`/`read`/`write`),没有 `tools.` 属性层 |
| 4 | `code mode module access is disabled ... Do not retry the same source with require() or an import` | 写了 `await (await import("openclaw")).default` |
| 5 | `SyntaxError at openclaw-code-mode:user.js:84:50: Unexpected token` | 在 JS 数组元素里用 `\'` 反斜杠转义单引号 —— 即本条自己刚写的规范所禁止的写法 |

### 根因

**三层转义**: JavaScript 字符串 → shell 命令 → python 源码 → python 字符串。
每层都有自己的引号语义,四层叠加后必然出错。

第 5 次最讽刺:我刚刚把「统一用一种引号风格」写进规范,下一条代码就违反了它 ——
说明**只写文档不立即改行为,下次照样犯**。

第 3、4 条是**工具 API 误用**,与引号无关:
- 工具以裸全局函数暴露(`process(...)`、`exec(...)`),**没有** `tools.` 前缀这一层
- guest JavaScript **禁止** `require()` / `import()` / `module` 访问

### 可靠做法(已固化到 TOOLS.md)

1. **不写内联脚本**。超过 3 行的 python/bash 一律用 `write` 工具落盘,再用 `exec` 跑文件。
   `write` 的 content 是**纯字符串**,不经过 shell,零转义问题。
2. **JS 里构造脚本内容**,用 `[...].join(chr(10))` 数组字面量:
   JS 字符串一律用**双引号**,内部 python 一律用**单引号**,两边都不需要转义。
3. **工具调用是裸全局**:`await process({...})`、`await exec({...})`、`await read({...})`。
   不要写 `tools.process`。
4. **禁止 `import()` / `require()`**。需要新能力时用 `catalog.search(query)`。
5. **要追加 Markdown 到文件**,直接用 shell heredoc 写片段再拼接,
   不要用 python 三引号字符串去构造含引号的文本。

### 判据

本轮 5 次失败**没有一次是系统故障**,全是我的写法问题。
但它们都发生在「写自动化脚本」这类看起来简单的步骤上,属高频复发点,故单独立条。

---


## ERR-20261127-003 — runtime context 的 exec session 列表是陈旧快照

**时间**: 2026-11-27 05:43–07:30 CST
**组件**: OpenClaw runtime context 注入(`Active exec sessions:` 段)

### 现象

runtime context 在每轮开头注入:

```
Active exec sessions:
- tide-canyon running pid=164150 cwd=/home/zhiping/.openclaw/workspace
```

但该 session 实际早已结束:
- `ps -p 164150` → 进程不存在
- `/proc/164150` → 目录不存在(连续 9 次确认)
- `process({action:'list'})` → 显示 `status: failed`,remove 后不再出现
- `process({action:'remove', sessionId:'tide-canyon'})` → 返回 completed

**runtime context 仍连续 9 轮报它 running。**

### 根因

runtime context 是**每轮开始时的快照**,不是实时查询。
会话结束后它不会被回写,于是长期挂着一条已经不存在的记录。

### 代价

我因为反复相信它,多花 4 轮去「杀进程 / 查 /proc / 清理」,
每次都用同三种方式重复验证同一件事 —— 这本身又是一次 v42 讲的反模式:
**没有新证据却重复同一个检查。**

### 正确做法

1. 看到 runtime context 报某 session running 时,**先信 `process list`**,不信 context
2. `process list` 是实时源;context 是快照
3. 已结束的 session 用 `process({action:'remove', sessionId})` 注销
4. 若 context 与 `process list` 冲突,**一次确认后按 `process list` 走**,不要反复复核

### 与既有教训的关系

v42:「取不到数据 ≠ 数据表明没问题」
v43:「现象消失 ≠ 根因消除」
本条:「快照 ≠ 实时状态」

三者同源:**任何「观测」都要先问它是什么时候取的、还新鲜吗。**

---

## ERR-20261127-004 — `pkill -f <pattern>` 会匹配到自己的命令行

**时间**: 2026-11-27 07:35 CST
**组件**: exec 工具 / shell

### 现象

执行

```bash
pkill -f 'openclaw doctor --json' 2>/dev/null; sleep 1
```

的结果是:**exec 返回空输出**(看起来像命令失败),
但被杀的其实是执行这条命令的 bash 自己 ——
因为 `pkill -f` 匹配的是**完整命令行字符串**,而我的命令行里就含 `openclaw doctor --json` 这段字面量。

本轮已踩 2 次(前一次 `pkill -f 'openclaw doctor'` 同样结果)。

### 修法:用括号技巧让模式不自匹配

```bash
# 模式写成 openclaw[ ]doctor —— 正则能匹配 'openclaw doctor',
# 但我的命令行里只有带括号的字面量,不会被自己匹配
for p in $(pgrep -f 'openclaw[ ]doctor'); do kill "$p" 2>/dev/null; done
```

或者更稳:先 `pgrep` 拿到 pid,人工核对,再按 pid kill。

### 附带判据

**exec 返回空输出 ≠ 命令失败。** 本例里命令其实是成功的,
只是执行者自己被杀了。空输出要查"是不是把自己杀了",
而不是直接归因给命令本身。

---

## ERR-20261127-005 — 三连击:fallback 末位小上下文模型 / 会话 contextTokens 被钉死 / 诊断自身烧配额 <!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->

**时间**: 2026-11-27 05:30 → 2026-11-28 06:00 CST
**组件**: cron 模型链 / session 上下文 / MiniMax Token Plan 配额

### 现象

11-27 08:00 `openclaw-news-digest` → `Context overflow: prompt too large`
11-28 01:16 `Coder NightOps` → `agent run aborted | OPENCLAW_DIRECT_ABORT`

### 机制一:会话的 contextTokens 会被「最后一次跑过的模型」钉死

```
agent:scout:cron:fe5fa0ce-...(news-digest)  ctx=8192  model=qwen3:4b-instruct  provider=ollama
```

11-26 那轮 fallback 落到 `ollama/qwen3:4b-instruct`(上下文 8192),
**该 cron 会话的上下文上限被永久写成 8192**。之后即便把模型换回大的,
旧会话仍按 8192 算预算 → 输入 12903 > 8192 → 必然 overflow。

**修法是删会话,不是改模型**:
`openclaw sessions delete --agent scout --yes <key>` → 新会话按新模型重建 `ctx=204800`。

全量扫还发现 3 条 11-05 的孤儿会话同样被钉在 8192(对应 cron job 已不存在),一并清除。

### 机制二:fallback 链末位是小上下文模型 = 定时炸弹

- 8/8 agent 的全局 fallback 末位 = `ollama/qwen3:4b-instruct`(8192)
- 4 个 NightOps 的 job 级 fallback 末位 = `ollama/qwen3.6:27b`(MEMORY 已记「只吐 reasoning」)

任何一个 job 只要落到末位 → 必然 context overflow → **并且污染该会话的 ctx**(回到机制一)。
兜底链末位放一个 8k 模型,不是兜底,是定时炸弹。

### 机制三:我自己的诊断烧掉了被诊断对象的配额

```
11-27 05:00-10:00 窗口:690 次 model-fetch / 68 次 429
  其中 210 次 MiniMax-M3 = agent:main:main = 我自己(runtime model=minimax/MiniMax-M3)
  → 08:00 news-digest 撞上被我自己烧光的配额
  → 429 → stall(age=403s) → abort_embedded_run → OPENCLAW_DIRECT_ABORT
```

**讽刺点**:我为了排查 news-digest 而跑的探针,正是 news-digest 失败的原因之一。

### 附:换 litellm 前缀不解决配额问题(v43 写过,我又犯了)

`litellm/MiniMax-M2.7` / `MiniMax-M3` 的上游仍是 `api.minimaxi.com` → 同一把 key、同一 Token Plan 池。
真正独立的池(11-28 05:50 实测):

| 模型 | 上游 | 实测 |
|---|---|---|
| `litellm/deepseek-flash` | api.deepseek.com | 🟢 200 / 243ms |
| `litellm/LongCat-2.0` | api.longcat.chat | 🟢 200 / 1630ms |
| `litellm/Step-3.5-Flash` | siliconflow | 🔴 403 Model disabled |
| `litellm/Kimi-K2.7` | siliconflow | 🔴 402 余额不足 |
| `litellm/GLM-5.3-Flash` | siliconflow | 🔴 402 billing |
| `litellm/MiniMax-*` | api.minimaxi.com | 🟡 200 但**同池** |

### 处置(全部为 cron job 级覆盖,**未改 openclaw.json**)

provider 凭据/模型链改动需 ZP 明确批准,故只用 `openclaw cron edit --model/--fallbacks`:

- `openclaw-news-digest`: model=litellm/deepseek-flash
- 4 个 NightOps: model=minimax/MiniMax-M2.7,fallbacks 前两位 = litellm/deepseek-flash + litellm/LongCat-2.0
- 全部移除 job 级 ollama 兜底

备份: `/tmp/cron_backup_20261127-0612/cron_list.json`

### 三条新结论

1. **「模型可用」和「模型在故障时刻可用」是两回事。** 凌晨 05:50 验证通过,08:00 照样 429。
   provider 健康检查是瞬时快照,不能当排期依据 —— 必须问「在那个窗口内,它还剩多少配额」。
2. **fallback 链每一项都要单独验证「上下文够大」和「配额池独立」。**
3. **诊断活动本身会消耗被诊断对象的资源。** 排查前先问:我的探针会不会影响被排查的东西?

---

## ERR-20261127-006 — 三种工具 ID 空间混用 / 跨会话读取被拒

**时间**: 2026-11-28 05:40–05:50 CST
**组件**: process / sessions_history / exec 工具

### 现象(本轮 3 条 error-detected 全是这一类)

```
1. [process] No session found for cm_485f4e66-0c5c-4854-948c-845b69847703
2. [sessions_history] User is not a participant of this turn.
3. [exec] Error: User is not a participant of this turn.
```

### 根因一:三套 ID 空间被我混用

| ID 形态 | 属于 | 该用哪个工具 |
|---|---|---|
| `cm_<hex>` | **bridge runId** | `wait({runId})` |
| `nova-forest` / `tide-canyon` 等形容词-名词 | **exec sessionId** | `process({action:'poll', sessionId})` |
| `agent:xxx:main` | 会话 key | `sessions_history({sessionKey})` |

我把 bridge 的 `cm_...` runId 塞进了 `process({action:'poll', sessionId})` → 「No session found」。

**判据**:`process` 的 `sessionId` 只认**本进程 exec 启动的**会话(形容词-名词形态);
`cm_` 开头的是 bridge 层 runId,必须走 `wait` 工具。

### 根因二:跨会话读取需要「参与者」身份

`sessions_history({sessionKey:'agent:orchestrator:main', user:'orchestrator'})`
→ `User is not a participant of this turn.`

**我为什么想读**:想确认 Orchestrator 是否已写过 v44,避免抢写同一个纪要文件。

**正确做法**:不需要读它的会话。
- 判断文件是否已被写入 → **直接 grep 文件本身**(`grep -c '^## NightOps 记忆体系讨论 v4' memory/2026-04-15.md`)
- 需要看它发了什么 → **等它通过 sessions_send 送达**(跨会话消息会主动路由过来)
- `sessions_send` 只回 `accepted/queued` → **不等于对端已读**(ZP 的 Orchestrator 已在 11-17 误判过一次,已记教训)

### 通用教训

**「想知道别处发生了什么」有三条路,按代价排序:**

1. 直接读**产物**(文件/状态)—— 零权限成本,最可靠
2. 等对方**主动送达** —— 适合协作消息
3. 读对方**会话历史** —— 需要参与者身份,且最脆弱

我下意识跳到了第 3 条,两次都被拒。第 1 条本可以直接解决。

### 附:写完不到 10 分钟,又犯了一次同样的错(2026-11-28 06:05)

记录 ERR-20261127-006 后不到 10 分钟,我又执行了
`process({action:"poll", sessionId:"cm_87ed50c4-..."})` → 「No session found」。

**同一个坑,同一天,记录完就踩。** 这直接印证 v44 的
「**结论消失 ≠ 结论生效**」——写下来只是第一步,不改行为等于没写。

**加固**:凡是要用 ID 的操作,先在心里过一遍「这个 ID 是哪个空间的」:
- `cm_` 开头 → `wait({runId})`
- 形容词-名词 → `process({sessionId})`

不确定时:**不要 poll**,直接重跑那条命令(幂等的话)或写文件再读。

---

## ERR-20261127-007 — 体检脚本在 cron 环境下假阴性:「从未报错」被当成「一切正常」

**时间**: 2026-11-28 06:00–06:15 CST
**组件**: `scripts/session-health-checker.py` + `scripts/session-health-check.sh`

### 现象

首次在 cron 最小环境(`env -i PATH=/usr/bin:/bin`)实跑体检,输出:

```
lease 失效: ['work']
✅ 未发现处于风险状态的主会话     ← 但同一次直跑明明有 P0(work) + P1×3
```

### 根因

`openclaw` CLI 在 `/usr/local/bin/openclaw`,而 **cron 默认 PATH 是 `/usr/bin:/bin`**。
于是:

1. `openclaw sessions ...` 静默失败:`rc=127, stderr="timeout: failed to run command 'openclaw'"`
2. `run_json` 吞掉异常,返回 `{}`
3. `items` 为空 → `rows` 为空 → `risky` 为空 → 打印 **「✅ 未发现处于风险状态的主会话」**
4. 退出码 0

**一个从不报错的检查,等于没有检查。** 而我上一轮却把它判成「✅ cron 环境能跑通(体检有效)」——
判据错了:我验的是「脚本有没有跑完」,不是「它有没有拿到数据」。

### 修法(v5)

1. **shell 脚本显式设 PATH**:`export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"`,
   并在 `command -v openclaw` 失败时**明确写「检查器自身故障,不要把这次结果当成正常」**
2. **checker 区分三种退出码**:
   - `0` = 取到数据且无风险
   - `1` = 取到数据且有风险
   - `2` = **取不到数据 → 本轮结论无效**
3. `run_json` 改为返回 `(data, err)`,rc≠0 / JSON 解析失败 / 返回 0 条记录 → 一律判无效
4. 打印时带上实际取到的会话条数(`共 N 条`),让人能一眼看出是不是空列表

### 反向验证(按 v42:必须证明它会失败)

| 场景 | 期望 | 实测 |
|---|---|---|
| cron 最小环境 + openclaw 不在 PATH | rc=2 + 「结论无效」 | ✅ |
| 桩返回空列表 `{}` | rc=2 + 「0 条主会话,数据形态异常」 | ✅ |
| 正常环境 | rc=1 + 真实风险清单 + `共 400 条` | ✅ |

### 通用教训

**「脚本跑完了」≠「它拿到了数据」。** 验证一个检查器时,要验的是**它的失败路径**,
而不是它的成功路径 —— 成功路径在数据缺失时也可能是「成功」。

与 ERR-20261127-001(v2 空集当「都不满足」)、v44(结论消失 ≠ 结论生效)同源。

---

