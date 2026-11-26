#!/usr/bin/env bash
# ═══ 闸门自测 ═══
# 背景 (2026-11-26): 我写的 push 前密钥闸门用 grep -E 的 (?<!) 后顾断言,
#   ERE 不支持该语法 → 报 warning 后【静默跳过】且退出码仍为 0,
#   于是我「验证通过」了,而 push 仍被 GitHub 拦下。
#   → 一个从未失败过的闸门,其「通过」不构成任何证据。
# 本脚本给每个闸门配两个用例:
#   ① 正例:必然命中的样本 → 必须报错 + 退出码非 0
#   ② 反例:干净样本     → 必须放行 + 退出码 0
# 只有两者都通过,闸门才被认为可信。
#
# ★ 本文件自身【不得包含任何完整 token 串】,否则它会被 push 前闸门
#   (以及 GitHub push protection)拦下 —— 2026-11-26 连踩四次:
#   ① 样本直接写死 ② 运行时拼装但仍写死 ③ 分段拼接但拼起来仍是完整串
#   ④ 片段本身已够长(单个字面量就已构成完整形态)。
#   正解: 每段都不够长,只有【运行时拼接后】才形成完整形态。
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
PASS=0; FAIL=0
trap 'rm -rf "$TMP"' EXIT

check() {  # check <名称> <期望:hit|clean> <文件> <闸门命令...>
  local name="$1" expect="$2" file="$3"; shift 3
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$expect" = hit ]; then
    if [ "$rc" -ne 0 ]; then echo "  ✅ $name: 命中样本正确报错 (rc=$rc)"; PASS=$((PASS+1))
    else echo "  ❌ $name: 命中样本却放行! (rc=0) — 闸门静默失效"; FAIL=$((FAIL+1)); fi
  else
    if [ "$rc" -eq 0 ]; then echo "  ✅ $name: 干净样本正确放行"; PASS=$((PASS+1))
    else echo "  ❌ $name: 干净样本被误拦 (rc=$rc)"; FAIL=$((FAIL+1)); fi
  fi
}

# 样本在运行时生成:每段都不够长,拼接后才形成完整形态 → 文件内零完整 token 串
python3 -c "import json,secrets;p='pk'+'.eyJ1Ijoi'+secrets.token_hex(24);print(json.dumps({'mapbox':{'apiKey':p},'k':1}))" > "$TMP/hit.json"
python3 -c "import json;print(json.dumps({'mapbox':{'apiKey':'pk.eyJ[REDACTED]'},'k':1}))" > "$TMP/clean.json"
printf 'plain text no secrets here\n' > "$TMP/clean.txt"

echo "=== 闸门自测 ==="
check "pre-push-secret-guard (hit)"  hit  "$TMP/hit.json"  python3 "$SCRIPT_DIR/pre-push-secret-guard.py" --file "$TMP/hit.json"
check "pre-push-secret-guard (clean)" clean "$TMP/clean.json" python3 "$SCRIPT_DIR/pre-push-secret-guard.py" --file "$TMP/clean.json"

# sanitize-secrets 是「执行器」不是「闸门」:成功时退出码 0 才是正确行为。
# 因此它的用例判据是「执行后内容已脱敏」,而不是「退出码非 0」。
cp "$TMP/hit.json" "$TMP/san.json"
python3 "$SCRIPT_DIR/sanitize-secrets.py" "$TMP/san.json" >/dev/null 2>&1
if grep -q 'REDACTED' "$TMP/san.json" && ! grep -qP 'pk\.eyJ[A-Za-z0-9_.-]{20,}' "$TMP/san.json"; then
  echo "  ✅ sanitize-secrets: 命中样本已正确脱敏"; PASS=$((PASS+1))
else
  echo "  ❌ sanitize-secrets: 命中样本未被脱敏"; FAIL=$((FAIL+1))
fi

echo "=== 结果: 通过 $PASS / 失败 $FAIL ==="
[ "$FAIL" -eq 0 ] || { echo "  ⚠️ 有闸门不可信,禁止用于生产"; exit 1; }
exit 0
