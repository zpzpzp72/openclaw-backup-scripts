#!/usr/bin/env python3
"""push 前密钥扫描闸门。退出码: 0 通过 / 1 命中需处理。"""
import re, subprocess, sys, pathlib

# 支持两种调用:
#   1) 无参/REPO 形态: 扫 git diff REPO..HEAD 的待推文件
#   2) --file <path>...  : 直接扫指定文件(供自测使用)
files_mode = '--file' in sys.argv
if files_mode:
    names = sys.argv[sys.argv.index('--file') + 1:]
    REPO = None
else:
    REPO = sys.argv[1] if len(sys.argv) > 1 else 'origin/feature/hot-backup'
EXT = ('.html', '.xml', '.json', '.md', '.txt', '.py', '.sh', '.csv')

HARD = re.compile(rb'(?<![A-Za-z0-9_-])((?:sk|rk|ghp|gho|glpat|sk-proj|xox[baprs]|AKIA|AIza)[.][A-Za-z0-9_.-]{20,})')
PK   = re.compile(rb'(?<![A-Za-z0-9_-])(pk\.eyJ[A-Za-z0-9_.-]{20,})')

if not files_mode:
    try:
        names = subprocess.run(['git','diff','--name-only',f'{REPO}..HEAD'],capture_output=True,text=True,timeout=120).stdout.split()
    except Exception as e:
        print(f'  (无法获取待推列表: {e})')
        sys.exit(0)

hard, pk = [], []
for name in names:
    if not name.endswith(EXT):
        continue
    p = pathlib.Path(name)
    if not p.is_file():
        continue
    try:
        d = p.read_bytes()
    except Exception:
        continue
    if HARD.search(d):
        hard.append(name)
    elif PK.search(d):
        pk.append(name)

if hard:
    print('❌ 检出硬密钥,拒绝 push:')
    for n in hard: print('    ', n)
    print('   处理: python3 scripts/sanitize-secrets.py <上述文件> 后重新提交')
    sys.exit(1)
if pk:
    print('❌ 检出 Mapbox pk. token(GitHub push protection 会拦),拒绝 push:')
    for n in pk: print('    ', n)
    print('   处理: python3 scripts/sanitize-secrets.py <上述文件> 后重新提交')
    sys.exit(1)
print(f'  ✅ 密钥扫描通过(扫 {len(names)} 个待推文件)')
sys.exit(0)
