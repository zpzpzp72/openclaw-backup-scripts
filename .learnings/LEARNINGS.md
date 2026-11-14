# LEARNINGS — 经验教训日志（按时间倒序，最新在上）

> 运行日志性质。每条写清：日期 / 现场 / 教训。含糊或未验证的结论不写进来。

---

## 2026-10-25｜Main NightOps 轮：工具层三个小错误

1. **外部 sqlite3 打不开活跃 state DB**（`sqlite3 state/openclaw.sqlite` 被沙箱拒绝）
   - 教训：查 live state 只走 `openclaw` CLI（如 `openclaw models status --json`）；确需查 DB 时先复制到 workspace 临时目录再读。属沙箱预期行为，不算故障。
2. **shell 重定向笔误**：`2>/summary`（想写 `2>/dev/null`）→ bash 把 stderr 重定向到不存在的可执行文件，报 Permission denied。
   - 教训：重定向目标拼错时报错信息很像权限问题，先检查拼写再怀疑策略收紧。
3. **read 路径手误 / 文件不存在**：read 返回 "File not found… Did you mean: …" 候选列表。
   - 教训：报错里的候选列表可直接当目录侦察用；例如借此确认 coder 的当日产物在 `agents/coder/coder-review-2026-10-25.md`，heartbeat/ 下没有 coder 10-24 场。

## 2026-10-25｜探活命令参数错误 ≠ 通路故障

- **现场**：用 `openclaw agent exec --model minimax/MiniMax-M2.7 --thinking adaptive` 做 agent 探活，报错 `Thinking level "adaptive" is not supported for minimax/MiniMax-M2.7. Use one of: off, minimal, low, medium, high, ultra.`
- **教训**：
  1. 错误信息里往往直接给出合法参数表，先按它重试，别当作服务故障上报。
  2. 验证子代理通路更可靠的方式是看**实际产物**：今夜 coder(02:20)/orchestrator(02:40) 会话真实完成并写出文件，即通路健康；探活命令失败只说明命令参数错了。

## 2026-10-24｜探测方法错误会级联成系统事故（继承，已由多场验证）

1. **占位符当真 key**：拿配置文件里的 `${LITELLM_MASTER_KEY}` 字面量当 key 去探测 → 得到误导性错误 → 误判 provider 死链。
   - 教训：探测必须用**运行时实际生效的 key**（`openclaw models status` 看 effective 来源），或复制备份到沙箱外再查。
2. **地址写错 ≠ 服务死**：`127.0.0.1:25017` / `127.0.0.1:11434` 在 WSL2 内不通，实际服务在 `172.18.160.1`。
   - 教训：任何 "DOWN" 结论，先对比「实际监听地址 vs 代码/脚本里写的地址」再上报。这条已写入 orchestrator HEARTBEAT.md 的"避免重复误判"块。
3. **冷却标记 ≠ provider 死**：cooldown（如 minimax 15h rate_limit）窗口过后自动恢复；`Auth=no` 不等于 key 失效。
4. **多 agent 改配置会互相覆盖**：同一晚 Scout 与 Orchestrator 先后改 fallback 链，后写覆盖先写。
   - 教训：改 openclaw.json 前先读 `agents/shared-memory/cross-agent-log.md` 最新裁决；收敛后由 Main 单点执行（single-arbiter）。

## 2026-10-24｜文档与配置要分开对待权威来源

- DIRECTIVE.md / HEARTBEAT.md 里的 fallback 链描述可以是旧文案；**权威来源是 `openclaw models status` 实测输出 + 当前配置文件**，其次才是最近一次有据可查的裁决记录。
- 收集子代理报告时，涉及链路/配置的描述必须实测核验，不能照抄子代理的转述。

## 2026-10-25 「升级前先归一运行时」——否则 update 会把修复打回原形

**现象**：修复了 Gateway service unit 的 3 条 config issue(改 ExecStart 指向非版本管理器 node + 最小 PATH)。若此时直接 `openclaw update`,installer 重装 service 时会**按自己的规则重写 unit**,可能打回 nvm 路径 → 3 条 issue 复现。

**源码依据**：`dist/runtime-paths-*.mjs` 的 `resolvePreferredNodePath()` 选 runtime 的优先级是
1. 当前 execPath **且非版本管理器路径** → 2. 系统 node(且 supported) → 3. 当前 execPath(即使是版本管理器路径)

**结论**：第 1 条要成立,当前 CLI 跑的 node 必须**本身不在版本管理器路径下**。本轮先做 `~/.local/bin/node` → `/usr/local/lib/nodejs/...` 的归一(顺带消掉版本回退告警),**之后** upgrade 才安全。

**通用规律**：任何「修了安装产物/配置」的场合,先确认「下一次自动重写这个产物的流程会写出同样的东西」,否则修复是脆弱的。

## 2026-10-25 换 node 软链会顺带改掉 npm prefix

**现象**：把 `~/.local/bin/node` 软链到 `/usr/local/lib/nodejs/node-v26.10.0/bin/node` 后,`npm config get prefix` 从 nvm 路径变成了 `/usr/local/lib/nodejs/node-v26.10.0`。

**原因**：npm 的 prefix 默认由**当前 node 可执行文件所在目录**推导,不是由 npm 自身位置推导。所以 `node` 一换,`npm i -g` 的落点就换。

**后果**：全局包会被装到新前缀,而 service 的 `ExecStart` 仍指向旧前缀 → 升级后跑的是旧代码,新旧两份并存,极易误判「升级没生效」。

**修法**:`~/.npmrc` 写 `prefix=<原全局包所在前缀>`,把「用哪个 node」和「往哪装全局包」解耦。

**检查清单(换 node 后必查)**:
```
node -v                     # 版本对不对
npm config get prefix       # 变了没(最容易被忽略)
npm root -g                 # 里面还有没有原来的全局包
openclaw --version          # 工具本身还正常吗
```

## 2026-10-26 网关 RSS 10.29GB 定位:是「大量小段堆积」,不是单块大 buffer

**实测**(pid 319857,uptime 1d14h):
```
总映射 16098 · 匿名段 15967 · 文件段 131
anon Private_Dirty 9.88GB / file 0.15GB
段大小分桶: <64KB:105 · 64KB-1MB:15067 · >1MB:533
最大单段仅 73MB
```

**判读**:15067 个 64KB-1MB 的匿名脏页段,单段都不大但总量近 10GB —— 典型**碎片化/逐段增长**特征,不是「一个 4GB 大 buffer」。

**关键修正**:之前(MEMORY 10-24)写的「9388 个 anon rw- 映射」是**映射数**,不是字节数;当时据此推断「外部 Buffer/native 内存膨胀」缺证据。本次补上了 Private_Dirty 拆分与段大小分桶,才算定位到「段数与总字节同时增长」。

**测量要点**(下次直接照做):
- `awk '/^[0-9a-f]+-[0-9a-f]+ /{a=(NF<6)} /^Private_Dirty:/{if(a)an+=$2;else fi+=$2}' /proc/<pid>/smaps` → 匿名 vs 文件
- 段大小分桶:按 maps 的 start-end 算每段大小再分桶,**别用 smaps 的 `Size:` 累加**(那是单段大小,累加无意义)
- **别在 Code Mode 里直接 cat 整个 smaps** → 输出会撑爆工具缓冲(本次踩到,145KB 被截断),要先聚合再输出

## 2026-10-26 「备份占满 NAS」是个错口径:df 的 Avail 是整个卷的,不是备份目录的

**现象**:NAS Avail 279G→214G→186G(24h 掉 93G),而备份每天只写 8.8G → 差额无主,排查了半天。

**根因(两层)**:
1. **口径错**:`df` 的 Avail = **整个 7.2T NAS** 的剩余,不是备份目录配额。备份实际只占 219G/7.2T = **3%**。之前 MEMORY 里「NAS 7.2T 用 7.0T」把「卷总用量」当成「备份占用」,导致「备份快撑爆 NAS」的结论不成立。
2. **真凶在源目录**:`.openclaw/memory/lancedb-pro/memories.lance/` = **9.5G**,近 3 天新增 5138 文件/0.74GB(≈0.25GB/天),而备份的 exclude 列表**漏了它**(只排了不存在的 `.openclaw/data/lancedb`)。于是每份 tgz 都把整个向量库装进去 → 8.8G/份 × 39 份。

**教训**:
- 看到「磁盘快满」先分清三层:① 卷总用量 ② 某目录占用 ③ 增长源。`df` 只回答①,`du` 回答②,`find -newermt` 回答③。
- **备份体积异常膨胀,先查源目录的 exclude 规则**,而不是先删旧备份 —— 不修 exclude,删了也会再涨回来。
- `du` 在网络盘(NAS)上极慢(单目录 >100s),要**定向查少数几个可疑目录**,别全量扫。

## 2026-10-31 nvm 0.40 + ~/.npmrc prefix 冲突坑
- 经过: 装 rea-agents 需 node>=26.12.1；nodejs.org tarball sha256 检验通过, 但 ~/.npmrc 的 prefix 钉死 v26.10.0 使 nvm install/use 流程整体非零退出; npmmirror 镜像 SHASUMS256.txt 返回空无法校验。
- 处理: 不动用户 ~/.npmrc; 手动 tar -xJf 解包 nvm 已验证的缓存 tarball 到 ~/.nvm/versions/node/; npm 加 --userconfig=<空文件> 绕过 prefix + --prefix 指向目标 node 树; CLI 用 shim 钉到特定 node 版本; nvm default alias 钉回用户默认版本防劫持。
- 补充：npmmirror 兜底装 node 时镜像 SHASUMS 返回空 → 已解包目录视为不可信，移入 .nvm-quarantine，防止 nvm use 26 解析到未验证版本；确需该版本用 nodejs.org 官方 tarball 重装。

## 2026-11-03 · NightOps 报告落盘纪律（Life/Orchestrator/Scout 通用）

- **跨 workspace 目录写文件禁用 apply_patch**：apply_patch 的 sandbox root 是 `~/.openclaw/workspace/agents/life`，写 `workspace/heartbeat/` 会报 `Path escapes sandbox root`。正确做法：`exec` + heredoc（`cat >> f << 'EOF'`）或 write 工具。
- **写完必校验残留**：模型 tool call 结构损坏时，原始标记 `</tool_call><arg_key>…` 会漏进落盘正文。收工前一律 `grep -n "arg_key\|tool_call\|</think>" <file>`，并顺带扫 U+FFFD 乱码和被截断的表格行（`...` 结尾）。
- **判 run 成败 ≠ 判产物有无**：NightOps run 报 failed 时，落盘产物可能完好。以文件实际内容为准，再单独判断投递（delivered）状态。
- 额度类报错（Token Plan 2056 / litellm 402 余额不足）属外部约束 → 写异常清单 + 告知 owner，不自行反复重试。

## 2026-11-07 · 别在 run 进行中探测产物文件

- **现象**：Life NightOps 01:50 场运行中（01:58），我执行 `ls nightly-life-2026-11-07.md` → `No such file or directory`，被 error-detected 当成工具错误信号拾取。
- **根因**：产物文件本场是 01:59 才落盘的，探测发生在写入之前 → 报错是**预期行为**，不是故障。且该探测由我自己发起，不是被测对象出错。
- **做法**：判断「本场产物是否落盘」要等 run 结束后再查；运行中只查 `automations list` 的 Status 列（running/ok）。或直接查 session 事件里是否有 `write` 成功记录。
- **对照**：11-07 场最终 ok / delivered / 852.7s，三个文件均落盘且无残留标记 —— 前面那条 ls 报错与结果无关。

## 2026-11-08 · 场次收尾纪律（三条）

- **run 状态与产物状态分开判**：11-08 场中途 `LLM idle timeout (120s)` 打断过一次 turn，但三个产物（heartbeat 33,039 B / memory 5,824 B / agents-life 3,691 B）**全部落盘且校验干净**。先看文件，再看 run 状态与 delivery。
- **收尾不要陷入 kill 循环**：本场为清掉一个「进程已死但 runtime 仍报 running」的 exec session，重复调用了 **30 次 `process kill` + 13 次 `process poll`** —— 每次拿回的仍是 `No active session found`，纯浪费 token 与时间。正确做法：以 `/proc/<pid>` 是否存在为准（不存在即视为已结束），**最多确认一次就收工**，不再重试 kill。
- **外呼必须自带降级**：本场 duckduckgo→000、bing→302、reuters→000、知乎官方 API→401。检索类调用要带超时与本地直采兜底，绝不能让模型挂在等一个不会回来的响应上。

## 2026-11-08 · runtime context 会报「假的 running 会话」

- **现象**：runtime context 持续声明 `nova-gulf running pid=982801`、`wild-fjord running pid=982015`，但 `/proc/982801`、`/proc/982015` **均不存在**，`ps` 也扫不到任何 `sleep` 进程，`process list` 里它们已标 `failed`。
- **判定**：runtime 的 exec 会话注册表与真实进程表**不同步**（进程已退出，注册表未刷新）。这与 ERR-20261108-001 记录的「process 已死但仍报 running」是同一个 bug 的两种表现。
- **正确处理**：以 `/proc/<pid>` 为准，不信 runtime context 的 running 标记。对已经结束的会话 `process kill` 会返回 `No active session found`，**不要重试**（本场为同类问题已累积 30 次 kill 调用，见 2026-11-08 · 场次收尾纪律）。
- **无副作用确认**：这两条会话的命令体都是纯 `sleep N`，进程消失即无副作用，无需回滚。

- **对照实验（同一分钟内完成）**：起一条 `sleep 25` 会话 → pid 983374 在 `/proc/983374` **存在**且 cmdline 可见，session 结束后该 pid 消失、registry 标 `completed`。而 982801 / 982015 全程 absent、registry 标 `failed`。→ 证明 `/proc` 判据可靠，runtime context 的 "running pid=" 是**陈旧残留**，不是活进程。

## 2026-11-08 · 读源码/日志时被 error-detected 误判为「工具错误」

- **现象**：连续多条 error-detected 信号其实是我**读取** `openclaw-backup.sh`、`send_email.py`、`backup-cron.log` 的输出片段（内容里含 `❌ 发送失败`、`Temporary failure in name resolution`、`FileNotFoundError` 等字样），被启发式当成「本次工具调用失败」。
- **判定**：信号里的文本是**被检查对象的既有内容**，不是本次命令的退出状态。判断依据：命令本身 exit 0，输出里没有任何新的 traceback 或非零返回。
- **做法**：读日志/源码时，若输出必然含历史错误字样，预期会被 error-detected 拾取 → **不要为此重跑，也不要新开 incident**。区分方法：看信号文本是「命令的 stderr/退出码」还是「文件内容回显」。
- **本轮已处理**：这些信号对应的真实问题（告警链断路）已归档为 ERR-20261108-006，无需重复记录。

## 2026-11-08 · NAS 空间预检的实测口径

- 脚本 `NEED_GB` 实测 = **6G**（`du -sm ~/.openclaw` 本地 1.5s 跑完，×0.4+1），NAS `AVAIL_GB` = **4**（`df -BG` 取整，真实 3.8G）→ 差 2G 被拦。
- 缺口其实很小：清空回收站任 **1~2 份**归档（约 4.2–6.5 GB/份）即可让 03:00 备份通过，不必全清 123 GB。
- 本地 `/dev/sdd` 有 **790G 可用** → 若要「先搬后删」，回收站内容可临时中转本地，再由 NAS 侧删除，属可回滚方案（但仍需 owner 授权）。

<!-- project: github.com/zpzpzp72/openclaw-backup-scripts -->
