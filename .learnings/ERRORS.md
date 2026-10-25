# ERRORS / 运行备忘 — 2026-10-25 NightOps

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
