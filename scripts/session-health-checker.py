#!/usr/bin/env python3
'''会话健康度检查 (2026-11-28 v5) —— 全部走官方只读接口,不碰 live DB。

★ v5 修正: 取不到数据 ≠ 数据表明没问题。
  v4 在 cron 环境下 openclaw CLI 不在 PATH -> sessions 静默失败 -> 返回空列表 ->
  打印「✅ 未发现处于风险状态的主会话」= 假阴性。一个从不报错的检查等于没有检查。
  v5: 数据取不到时返回 rc=2 并明确标注「本轮结论无效」,绝不打印 OK。

检测项:
  P0   lease 失效      -> 写操作 100% 失败
  P0   上下文被钉死     -> ctx<=32768 的会话;即使现在没报错也是地雷
  P1   上下文占用过高   -> 续用该会话且读大量历史会 context overflow
  P2   逼近上限 / 上次被 abort
  WARN 全局 fallback 链末位是小上下文模型 (只报告, 改配置需 ZP 批准)

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
RC_OK = 0
RC_RISK = 1
RC_NODATA = 2



def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


CFG = load_config()


def run_json(cmd):
    '''返回 (data, err)。err 非空表示这一取数失败了 —— 调用方必须区分。'''
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except Exception as e:
        return None, 'exec 异常: ' + str(e)
    if r.returncode != 0:
        return None, 'rc=' + str(r.returncode) + ' stderr=' + (r.stderr or '').strip()[:200]
    try:
        d = json.loads(r.stdout or '')
    except Exception as e:
        return None, 'JSON 解析失败: ' + str(e) + ' raw=' + (r.stdout or '')[:120]
    if not isinstance(d, (dict, list)):
        return None, '返回类型异常: ' + type(d).__name__
    return d, None


def sessions_items(limit):
    d, err = run_json(['openclaw', 'sessions', '--all-agents', '--json', '--limit', str(limit)])
    if err:
        return [], err
    items = d if isinstance(d, list) else (d.get('sessions') or d.get('items') or [])
    if not items:
        return [], 'openclaw sessions 返回 0 条记录(异常:正常应有数百条)'
    return items, None


def gateway_pid():
    try:
        r = subprocess.run(['pgrep', '-f', 'openclaw.*dist/index.js'],
                           capture_output=True, text=True, timeout=20)
        return int(r.stdout.split()[0]) if r.stdout.strip() else None
    except Exception:
        return None


def lease_evidence():
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


def main_sessions(items):
    return [s for s in items
            if str(s.get('key', '')).count(':') == 2
            and str(s.get('key', '')).split(':')[2] == 'main']


def pinned_ctx_sessions(items):
    out = []
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
    cfg = CFG
    if not cfg:
        return [], "openclaw.json 读取失败"
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



def job_chain_landmines():
    """扫描 cron job 级模型链 —— v45 议题4 第 1 项。

    背景 (2026-11-28):
    1. 429 事故当天没有任何自动检查发现 job 级链有问题。
    2. heartbeat-* 类任务 payload.kind=heartbeat,CLI 拒绝 per-job 模型覆盖
       (invalid cron.update params: payload.kind="agentTurn" requires message),
       所以这类任务只能继承 agent 全局链 —— 只能靠检测发现问题。

    检测两件事:
      a. job 级链末位是不是小上下文模型(会钉死会话 ctx)
      b. job 级链里有没有独立配额池模型(否则 MiniMax 429 时无退路)
    """
    d, err = run_json(["openclaw", "cron", "list", "--json"])
    if err:
        return [], err
    jobs = d if isinstance(d, list) else (d.get("jobs") or d.get("items") or [])
    ctxmap = {}
    providers = (CFG.get("models", {}) or {}).get("providers") or {}
    for pn, pv in providers.items():
        for m in (pv.get("models") or []):
            lim = m.get("contextWindow") or m.get("limit") or m.get("contextLength")
            if lim:
                ctxmap[pn + "/" + str(m.get("id"))] = int(lim)
    out = []
    for j in jobs:
        p = j.get("payload") or {}
        fb = p.get("fallbacks") or []
        prim = p.get("model")
        if not fb and not prim:
            # heartbeat 类: CLI 拒绝 per-job 模型覆盖,只能继承 agent 全局链
            if str(p.get('kind')) != 'heartbeat':
                continue
            aid = j.get('agentId')
            ga = None
            for v in ((CFG.get('agents') or {}).get('entries') or {}).values():
                if str(v.get('name')) == str(aid):
                    ga = v.get('model') or {}
                    break
            gp = ga.get('primary') if ga else None
            gfb = (ga.get('fallbacks') or []) if ga else []
            gchain = ([gp] if gp else []) + list(gfb)
            gsmall = [c for c in gchain if ctxmap.get(c) is not None and ctxmap[c] <= PINNED_CTX_LIMIT]
            gind = [c for c in gchain if 'deepseek-flash' in c or 'LongCat' in c]
            out.append({'job': str(j.get('name')), 'id': str(j.get('id')),
                        'kind': 'heartbeat', 'primary': gp,
                        'fallbacks': list(gfb), 'small': gsmall,
                        'has_independent': bool(gind),
                        'inherited': True,
                        'status': j.get('status')})
            continue
        chain = ([prim] if prim else []) + list(fb)
        small = [c for c in chain if ctxmap.get(c) is not None and ctxmap[c] <= PINNED_CTX_LIMIT]
        ind = [c for c in chain if "deepseek-flash" in c or "LongCat" in c]
        out.append({"job": str(j.get("name")), "id": str(j.get("id")),
                    "kind": str(p.get("kind")), "primary": prim,
                    "fallbacks": list(fb), "small": small,
                    "has_independent": bool(ind),
                    "status": j.get("status")})
    return out, None


def main():
    pid = gateway_pid()
    ev, src = lease_evidence()
    leased = ev['leased'] if ev else set()
    broken = ev['broken'] if ev else set()

    items, serr = sessions_items(400)
    if serr:
        print('  ❌ 数据获取失败: ' + serr)
        print('     → 本轮结论【无效】。这不代表系统健康,只代表检查器没拿到数据。')
        print('     → 常见原因: openclaw CLI 不在 PATH / gateway 未运行 / 会话库被锁')
        return RC_NODATA

    rows = main_sessions(items)
    pins = pinned_ctx_sessions(items)
    if not rows:
        print('  ❌ 取到 ' + str(len(items)) + ' 条会话但 0 条主会话 —— 数据形态异常,判定无效')
        return RC_NODATA

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
                          'sessions_total': len(items),
                          'pinned_ctx_sessions': pins,
                          'sessions': out}, ensure_ascii=False, indent=2))
        return RC_RISK if (any(o['issues'] for o in out) or pins) else RC_OK

    print('  gateway pid=' + str(pid) + '  数据源=openclaw sessions(官方只读接口,共 ' + str(len(items)) + ' 条)')
    print('  lease 证据: ' + src)
    print('    持有 lease: ' + str(sorted(leased)))
    print('    lease 失效: ' + str(sorted(broken)))
    print('    注: 未出现在两栏的 agent = 不可判定(不是没有 lease)')
    risky = [o for o in out if o['issues']]
    if not risky:
        print('  ✅ 未发现处于风险状态的主会话(本次已成功取到 ' + str(len(rows)) + ' 条主会话)')
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
    jobs, jerr = job_chain_landmines()
    if jerr:
        print("  ⚠️ job 级链检测不可用: " + jerr)
    else:
        risky_jobs = [x for x in jobs if x["small"] or not x["has_independent"]]
        if risky_jobs:
            print(f"  ⚠️ job 级模型链隐患({len(risky_jobs)}/{len(jobs)} 个 job):")
            for x in risky_jobs:
                tags = []
                inh = ' (继承全局链)' if x.get('inherited') else ''
                if x["small"]:
                    tags.append("含小上下文模型" + str(x["small"]))
                if not x["has_independent"]:
                    tags.append("无独立配额池兜底(MiniMax 429 时无退路)")
                print(f"    {x['job'][:28]:30} kind={x['kind']:10}{inh} {' | '.join(tags)}")
            print("  → 小上下文项: 改 job 级链(需 cron edit;heartbeat 类不支持,只能靠全局链)")
            print("  → 无独立池项: 给该 job 加 litellm/deepseek-flash 或 litellm/LongCat-2.0 兜底")
        else:
            print(f"  ✅ job 级模型链检查通过({len(jobs)} 个 job)")

    bad, _src = chain_landmines()
    if bad:
        print('  ⚠️ 全局 fallback 链末位是小上下文模型(' + str(len(bad)) + ' 条, 改 openclaw.json 需 ZP 批准):')
        for b in bad:
            print('    ' + str(b['agent']).ljust(14) + ' 末位=' + str(b['last']).ljust(32) + ' context=' + str(b['ctx']))
    print('  -> P0 处置: 停机后 openclaw doctor --fix(需 Gateway 重启)')
    print('  -> P1 处置: 若某任务反复 context overflow, 把它改 isolated 或轮转主会话')
    return RC_RISK if (risky or pins) else RC_OK


if __name__ == '__main__':
    sys.exit(main())