#!/usr/bin/env python3
"""入库前脱敏:把抓取内容中的密钥/公共 token 替换为占位符。

为什么需要:Scout 每晚抓网页并原样入库,页面里常含 apiKey 配置。
GitHub push protection 会按正则拦截(含 pk. 公共 token),
导致 push 失败;若其中是真密钥,还会造成泄漏。
用法: python3 scripts/sanitize-secrets.py <file> [file...]
退出码: 0 全部已脱敏 / 1 出错
"""
import re
import sys
import pathlib

PATTERNS = [
    # 高置信度硬密钥(必须脱敏)
    (re.compile(rb'(?<![A-Za-z0-9_-])((?:sk|rk|ghp|gho|glpat|sk-proj|xox[baprs]|AKIA|AIza)[.][A-Za-z0-9_.-]{20,})'), b'<REDACTED-SECRET>'),
    # Mapbox 公共 token(pk. 前缀,设计上可公开,但 push protection 仍会拦)
    (re.compile(rb'(?<![A-Za-z0-9_-])(pk\.eyJ[A-Za-z0-9_.-]{20,})'), b'pk.eyJ[REDACTED]'),
    # 通用 apiKey/token 字段
    (re.compile(rb'"(?:apiKey|api_key|accessToken|access_token|secret|clientSecret)"\s*:\s*"([A-Za-z0-9_.-]{20,})"'), b'"apiKey": "<REDACTED>"'),
]

def sanitize(path: pathlib.Path) -> int:
    data = path.read_bytes()
    orig = data
    n = 0
    for pat, repl in PATTERNS:
        data, k = pat.subn(repl, data)
        n += k
    if data != orig:
        path.write_bytes(data)
    return n

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    total = 0
    for a in sys.argv[1:]:
        p = pathlib.Path(a)
        if not p.is_file():
            print(f'  跳过(不存在): {a}')
            continue
        try:
            k = sanitize(p)
            total += k
            if k:
                print(f'  ✅ 脱敏 {k} 处: {a}')
        except Exception as e:
            print(f'  ❌ {a}: {e}')
            sys.exit(1)
    print(f'  合计脱敏 {total} 处')
