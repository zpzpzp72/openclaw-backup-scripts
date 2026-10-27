# 安全麦克风注入 & 版本号显示 — 升级后恢复指南

**目的**:给 OpenClaw Control UI 的聊天输入框加语音输入按钮(SpeechRecognition, zh-CN)，并在侧边栏标题旁显示版本号。
**首次实现**:2026-07-24 (v2026.7.1)。版本号显示:2026-07-27 (v2026.7.1-2)。

## 为什么需要"恢复"
每次 `npm` 升级 OpenClaw 会**整体覆盖** `dist/control-ui/index.html`,注入的脚本随之丢失。
所以脚本本体必须存在这里(`patches/safe-mic-inject.html`),升级后重新贴回。

## 恢复步骤(升级后执行)

```bash
# 1. 找到新版本的 dist 路径
openclaw gateway status | grep "Command:"
#   例:.../node_modules/openclaw/dist/index.js  → 取 dist 目录
DIST=$(openclaw gateway status | grep -oP '(?<=node )\S+/dist(?=/index.js)')
cd "$DIST/control-ui/"

# 2. 备份(带时间戳,别覆盖旧备份)
cp -av index.html "index.html.bak.$(date +%Y%m%d-%H%M%S)"

# 3. 检查是否已注入(幂等,避免重复)
grep -q "openclaw:safe-mic-inject" index.html && echo "已存在,跳过" || echo "需注入"

# 4. 把脚本插到 </body> 前
#    脚本本体:~/.openclaw/workspace/patches/safe-mic-inject.html
python3 - <<'PY'
import io
dist="$DIST/control-ui/index.html"          # 注意:此处需替换真实路径
snip=open("/home/zhiping/.openclaw/workspace/patches/safe-mic-inject.html").read()
html=open(dist).read()
if "openclaw:safe-mic-inject" in html:
    print("already injected"); raise SystemExit
html=html.replace("</body>", "\n    "+snip+"\n</body>", 1)
open(dist,"w").write(html)
print("injected ok")
PY

# 5. 重启 gateway(用 openclaw 工具,不要手搓 systemctl 除非必要)
openclaw gateway restart     # 等价:systemctl --user restart openclaw-gateway.service

# 6. 验证(线上 HTML 是否含脚本)
curl -s http://127.0.0.1:18789/ | grep -c "openclaw:safe-mic-inject"   # 应为 1
```

## 浏览器端验证(需真人)
- 硬刷新 Ctrl+Shift+R(绕开 sw.js 缓存)
- 聊天设置(齿轮)右侧出现麦克风图标
- 点击 → 授权 → 说话,文字追加进输入框(录音时红色脉冲)

## 对用户原始步骤的评估/修正
| 用户原步骤 | 问题 | 修正 |
|---|---|---|
| `cp index.html index.html.bak` | 会覆盖上次备份 | 用时间戳 `.bak.$(date ...)` |
| "用 AI 助手或手动"注入 | 不可复现 | 脚本本体已固化在 `patches/`,可脚本化贴回 |
| `systemctl --user restart ...` | 可用,但绕过工具 | 优先 `openclaw gateway restart`;systemctl 作 fallback |
| 未提去重 | 重复注入风险 | 先 `grep -q openclaw:safe-mic-inject` 判断 |
| 未提验证 | 无法确认成功 | 加 `curl | grep -c` + 浏览器硬刷新 |

## 关键设计原则(脚本本身)
- 容器真实类名 `agent-chat__composer-controls`,用 `[class*="composer-controls"]` 匹配
- 全 UI 是 **Light DOM**(`createRenderRoot(){return this}`),`document.querySelector` 全局可用
- `insertBefore(btn, children[1])` — 落在设置chip之后、发送/拆分之前
- 纯新增:只 createElement + insertBefore/append;innerHTML 仅用于自己的按钮插 SVG
- **无 MutationObserver**;1.5s/3s/6s 三次 setTimeout,幂等(`data-openclaw-mic` 去重)
- 自愈:找不到容器就静默 no-op;不支持 SpeechRecognition 的浏览器禁用按钮
- 语音:zh-CN / continuous / interimResults / 4s静音自停 / final文本 dispatch input+change

## 回滚
```bash
cd "$DIST/control-ui/"
cp index.html.bak.<最新时间戳> index.html && openclaw gateway restart
```

## 限制
- Web SpeechRecognition 仅 Chromium 系(Chrome/Edge)可用;Firefox 不支持(按钮自动禁用)
- 需安全上下文:`localhost`/`127.0.0.1`/`https` OK
