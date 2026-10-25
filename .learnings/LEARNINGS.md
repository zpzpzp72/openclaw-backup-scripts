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
