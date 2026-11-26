# TOOLS.md — 工具使用规范

> 本文件记录 OpenClaw Code Mode 工具的**实测**用法与坑。
> 每条都来自真实失败,不是文档抄写。

## Code Mode 基础

### 工具是裸全局函数,没有 `tools.` 前缀

```js
// 对
const r = await exec({ command: "ls" });
const p = await process({ action: "poll", sessionId: "x" });
const f = await read({ path: "/tmp/a" });
await write({ path: "/tmp/a.py", content: "..." });

// 错(会抛 ReferenceError: tools is not defined)
const r = await tools.exec({ command: "ls" });
```

### guest JavaScript 禁止模块访问

`require()` / `import()` / `module` 一律被拒:
```
code mode module access is disabled. Call an enabled async tool global from guest JavaScript;
use catalog.search(query) when the bounded quick index omits it.
```

**不要重试同一个源**。需要新工具时用 `catalog.search(query)`,结果可调用。

## 引号与转义:最容易反复踩的坑

### 规则 1 — 超过 3 行的脚本,一律用 `write` 落盘再跑

```js
// 对:write 的 content 是纯字符串,不经过 shell,零转义
await write({ path: "/tmp/patch.py", content: pySource });
await exec({ command: "python3 /tmp/patch.py" });

// 错:python3 -c 里嵌 JS 字符串再嵌 python 字典 → 四层转义
await exec({ command: "python3 -c \"import json;print(json.load(open(1))[2])\"" });
```

### 规则 2 — 在 JS 里构造脚本内容,用数组 join + 双引号字符串

```js
const py = [
  "import pathlib",
  "p = pathlib.Path('memory/x.md')",   // 内部 python 单引号在 JS 双引号里原样写
  "p.write_text(p.read_text() + chr(10) + body)",
].join(String.fromCharCode(10));
await write({ path: "/tmp/a.py", content: py });
```

**关键**:JS 字符串用**双引号**,里面的 python **单引号原样写**(不需要逃逸)。
反过来:JS 用单引号时,python 内部的双引号需要写成 `\"` —— 那就更容易出错。
**统一选一种,别混用。**

### 规则 3 — 绝不用 heredoc 跑 python

```bash
# 错:heredoc 里的三引号和 python 内容的双引号打架
python3 - <<PYEOF
old = """text with double quotes inside"""
PYEOF

# 对
python3 /tmp/patch.py
```

### 规则 4 — write 返回 changed:true 后再 exec

若脚本报 SyntaxError 且行号指向 heredoc,说明内容被 shell 吃了 —— 改用 write。

## Shell 专项

### 引号层级速查

| 需求 | 写法 |
|---|---|
| python 代码含单引号 | JS 双引号包整段,python 单引号原样写 |
| python 代码含双引号 | 同上,或 python 改用单引号 |
| 想在 python 里塞正则/JSON | **落盘**,别内联 |
| 输出含长 JSON | 管道给 python 再处理 |

### 管道后的退出码

`cmd | head` 的 `$?` 是 head 的,不是 cmd 的。要判 cmd 的退出码用 `PIPESTATUS[0]`。

## sqlite / 数据库

**禁止**用外部 `sqlite3` 或 python `sqlite3` 打开 `~/.openclaw/` 下的活跃 DB:
```
external sqlite3 cannot open databases under the active OpenClaw state directory.
Use OpenClaw commands for live state, or inspect a private backup copy outside OPENCLAW_STATE_DIR.
```

**改用官方只读接口**:

| 需求 | 命令 |
|---|---|
| 列会话(含 totalTokens / contextTokens) | `openclaw sessions --all-agents --json --limit 300` |
| 共享状态所有权 | `openclaw database ownership status --json` |
| agent DB schema 兼容性 | `openclaw database preflight-agent <file>` |
| 备份校验 | `openclaw backup --help` |
| cron 列表 | `openclaw cron list --json` |
| 单个 job | `openclaw cron get <id>` |
| 改 job | `openclaw cron edit <id> --cron <expr> --tz Asia/Shanghai` |

**注意**:`openclaw database` 没有 `status` 子命令(只有 `ownership` / `preflight` / `preflight-agent`)。

## 检测类工具的通用纪律

> 见 `.learnings/ERRORS.md` ERR-20261127-001 / ERR-20261127-002

1. **取不到数据 ≠ 数据表明没问题。** 两者必须用不同状态表示。
   把空集合当「都不满足」是检测工具最常见的假阳性来源。
2. **闸门必须用「必然命中」样本证明它会失败。**
   一个从未失败过的闸门,它给出的「通过」不构成任何证据。
3. **自测样本不能以任何形式存在于仓库文件里**(含运行时拼装、分段拼接)。
   正确做法:运行时由 python 用随机内容生成,文件内零 token 串。
4. **用官方接口代替直连底层存储**,即使直连「能工作」——
   它会绕过工具策略、产生拒绝噪音、并可能污染正在跑的 Gateway。

## 日志分析

Gateway 日志在 `/tmp/openclaw/openclaw-YYYY-MM-DD.log`,每行一个 JSON:
- `o["1"]` 是消息体,`o["0"]` 是 subsystem,`o["_meta"]["date"]` 是 **UTC** ISO 时间
- 日志时间是 UTC,排程是 CST → **分析时必须 +8h**,否则时间线会错 8 小时
- 抽关键词用 `grep -o` 或 python `re`,别用多层嵌套引号