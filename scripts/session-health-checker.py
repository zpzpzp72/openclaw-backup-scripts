#!/usr/bin/env python3
'''会话健康度检查 (2026-11-28 v4) —— 全部走官方只读接口,不碰 live DB。

检测项:
  P0   lease 失效      -> 写操作 100% 失败
  P0   上下文被钉死     -> ctx<=32768 的会话;即使现在没报错也是地雷
  P1   上下文占用过高   -> 续用该会话且读大量历史会 context overflow
  P2   逼近上限 / 上次被 abort
  WARN 全局 fallback 链末位是小上下文模型 (只报告, 改配置需 ZP 批准)

机制背景 (2026-11-28 实测):
  会话的 contextTokens 会被最后一次跑过的模型钉死。
  11-26 news-digest 那轮 fallback 落到 ollama/qwen3:4b-instruct(8192),
  把该 cron 会话上限永久写成 8192 -> 之后换大模型也按 8192 算预算 ->
  输入 12903 > 8192 -> 必然 Context overflow, 且会反复发生。

判据来源 (v42): 任务健康与否不取决于属于哪个 agent,
  而取决于它续用的那个会话是否还是可用资产。
'''
import glob
import json
import os
import re
import subprocess
import sys

CTX_TOKEN_LIMIT = 200000
CTX_WARN_RATIO = 0.5
PINNED_CTX_LIMIT = 32768
LOG_GLOB = '/tmp/openclaw/openclaw-*.log'
LOG_TAIL_LINES = 20000
CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.openclaw', 'openclaw.json')


def run_json(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        d = json.loads(r.stdout or '{}')
        if isinstance(d, (dict, list)):
            return d
        return {}
    except Exception as e:
        return {'__error__': str(e)}


def gateway_pid():
    try:
        r = subprocess.run(['pgrep', '-f', 'openclaw.*dist/index.js'],
                           capture_output=True, text=True, timeout=20)
        return int(r.stdout.split()[0]) if r.stdout.strip() else None
    except Exception:
        return None


def lease_evidence():
    # 从 Gateway 日志推断 lease 状态:日志证据, 不是直接读 lease 表。
    leased = set()
    broken = set()
    files = sorted(glob.glob(LOG_GLOB), key=os.path.getmtime)[-2:]
    if not files:
        return None, '无日志文件'
    for f in files:
        try:
            with open(f, errors='ignore') as fh:
                lines = fh.readlines()[-LOG_TAIL_LINES:]
        except Exception:
            continue
        for ln in lines:
            if 'reclamation commit checkpoint expired' in ln:
                for m in re.findall(r'/agents/([A-Za-z0-9_-]+)/agent/', ln):
                    broken.add(m)
            elif 'active-leases' in ln:
                for m in re.findall(r'/agents/([A-Za-z0-9_-]+)/agent/', ln):
                    leased.add(m)
    src = '日志证据(' + str(len(files)) + ' 个文件, 末尾 ' + str(LOG_TAIL_LINES) + ' 行)'
    return {'leased': leased, 'broken': broken}, src


def main_sessions():
    d = run_json(['openclaw', 'sessions', '--all-agents', '--json', '--limit', '300'])
    items = d if isinstance(d, list) else (d.get('sessions') or d.get('items') or [])
    return [s for s in items
            if str(s.get('key', '')).count(':') == 2
            and str(s.get('key', '')).split(':')[2] == 'main']


def pinned_ctx_sessions():
    # 找出上下文被钉死在小模型上的会话 —— 2026-11-28 新增。
    # 这类会话即使现在还没报错也是地雷: 一旦跑需要 >ctx 的任务必然溢出。
    out = []
    d = run_json(['openclaw', 'sessions', '--all-agents', '--json', '--limit', '400'])
    items = d if isinstance(d, list) else (d.get('sessions') or d.get('items') or [])
    for s in items:
        ctx = s.get('contextTokens')
        if not ctx:
            continue
        try:
            ctx = int(ctx)
        except Exception:
            continue
        if ctx > PINNED_CTX_LIMIT:
            continue
        out.append({'key': str(s.get('key', '')), 'ctx': ctx,
                    'model': s.get('model'), 'provider': s.get('modelProvider'),
                    'kind': s.get('kind'), 'agent': s.get('agentId')})
    return out


def chain_landmines():
    # 扫描 openclaw.json: 全局 fallback 链末位是不是小上下文模型。
    # 只报告不改 —— 改 openclaw.json 的模型链需 ZP 明确批准。
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
    except Exception as e:
        return [], str(e)
    ctxmap = {}
    providers = (cfg.get('models', {}) or {}).get('providers') or {}
    for pn, pv in providers.items():
        for m in (pv.get('models') or []):
            lim = m.get('contextWindow') or m.get('limit') or m.get('contextLength')
            if lim:
                ctxmap[pn + '/' + str(m.get('id'))] = int(lim)
    ag = cfg.get('agents') or {}
    chains = []
    dm = (ag.get('defaults') or {}).get('model') or {}
    chains.append(('defaults', dm.get('primary'), dm.get('fallbacks') or []))
    for a in (ag.get('entries') or {}).values():
        m = a.get('model') or {}
        chains.append((a.get('name') or '?', m.get('primary'), m.get('fallbacks') or []))
    bad = []
    for nm, prim, fb in chains:
        if not fb:
            continue
        last = fb[-1]
        lim = ctxmap.get(last)
        if lim is not None and lim <= PINNED_CTX_LIMIT:
            bad.append({'agent': nm, 'last': last, 'ctx': lim})
    return bad, 'ok'


def main():
    pid = gateway_pid()
    ev, src = lease_evidence()
    leased = ev['leased'] if ev else set()
    broken = ev['broken'] if ev else set()
    rows = main_sessions()
    pins = pinned_ctx_sessions()
    out = []
    for s in rows:
        key = str(s.get('key', ''))
        ag = s.get('agentId') or key.split(':')[1]
        tok = s.get('totalTokens') or 0
        issues = []
        lvl = 'OK'
        if ag in broken:
            issues.append('P0 日志证据: 该 agent lease 失效 (reclamation checkpoint expired) -> 写操作 100% 失败')
            lvl = 'P0'
        if tok > CTX_TOKEN_LIMIT:
            issues.append('P1 上下文占用 ' + format(tok, ',') + ' token > ' + format(CTX_TOKEN_LIMIT, ',') + ' -> 续用且读大量历史会 context overflow')
            if lvl != 'P0':
                lvl = 'P1'
        elif tok > CTX_TOKEN_LIMIT * CTX_WARN_RATIO:
            issues.append('P2 上下文占用 ' + format(tok, ',') + ' token 已过 ' + str(int(CTX_WARN_RATIO * 100)) + '% -> 逼近上限')
            if lvl == 'OK':
                lvl = 'P2'
        if s.get('abortedLastRun'):
            issues.append('P2 上一次运行被 abort')
            if lvl == 'OK':
                lvl = 'P2'
        out.append({'agent': ag, 'session': key, 'tokens': tok,
                    'issues': issues, 'severity': lvl,
                    'lease': 'broken' if ag in broken else ('held' if ag in leased else 'unknown')})
    order = {'P0': 0, 'P1': 1, 'P2': 2, 'OK': 3}
    out.sort(key=lambda o: (order[o['severity']], -o['tokens']))
    if '--json' in sys.argv:
        print(json.dumps({'gateway_pid': pid, 'lease_source': src,
                          'lease_evidence': {'leased': sorted(leased), 'broken': sorted(broken)},
                          'pinned_ctx_sessions': pins,
                          'sessions': out}, ensure_ascii=False, indent=2))
        return 1 if (any(o['issues'] for o in out) or pins) else 0
    print('  gateway pid=' + str(pid) + '  数据源=openclaw sessions (官方只读接口)')
    print('  lease 证据: ' + src)
    print('    持有 lease: ' + str(sorted(leased)))
    print('    lease 失效: ' + str(sorted(broken)))
    print('    注: 未出现在两栏的 agent = 不可判定(不是没有 lease)')
    risky = [o for o in out if o['issues']]
    if not risky:
        print('  ✅ 未发现处于风险状态的主会话')
    for lvl, icon in (('P0', '🔴'), ('P1', '🟡'), ('P2', '🔵')):
        g = [o for o in risky if o['severity'] == lvl]
        if not g:
            continue
        print('  ' + icon + ' ' + lvl + ' (' + str(len(g)) + ' 个):')
        for o in g:
            line = '    ' + str(o['agent']).ljust(12) + ' ' + o['session'][:38].ljust(40) + ' ' + str(o['tokens']).rjust(9) + ' token  lease=' + o['lease']
            print(line)
            for i in o['issues']:
                print('        - ' + i)
    if pins:
        print('  🔴 上下文被钉死(' + str(len(pins)) + ' 个会话, 即使现在没报错也是地雷):')
        for x in sorted(pins, key=lambda z: z['ctx']):
            print('    ' + str(x['agent']).ljust(12) + ' ctx=' + str(x['ctx']).rjust(7) + '  model=' + str(x['provider']) + '/' + str(x['model']))
            print('        ' + x['key'][:76])
        print('  -> 处置: 删除重建这些会话 (openclaw sessions delete), 让它们按当前模型链重新建立上限')
    bad, _src = chain_landmines()
    if bad:
        print('  ⚠️ 全局 fallback 链末位是小上下文模型(' + str(len(bad)) + ' 条, 改 openclaw.json 需 ZP 批准):')
        for b in bad:
            print('    ' + str(b['agent']).ljust(14) + ' 末位=' + str(b['last']).ljust(32) + ' context=' + str(b['ctx']))
    print('  -> P0 处置: 停机后 openclaw doctor --fix(需 Gateway 重启)')
    print('  -> P1 处置: 若某任务反复 context overflow, 把它改 isolated 或轮转主会话')
    return 1 if (risky or pins) else 0


if __name__ == '__main__':
    sys.exit(main())