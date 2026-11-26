#!/usr/bin/env python3
"""会话健康度检查:预测「续用主会话的任务」会以什么方式失败。

背景 (2026-11-26): 两类 error 根因同构 ——
  heartbeat-work      续用 agent:work:main   → 该 DB 无现役 lease → 每小时 reclaim 超时 (err=94)
  openclaw-news-digest 续用 agent:scout:main → 该 session 17451 条/8.1MB → 隔天 context overflow
而 isolated 的任务(memory-weekly-audit / 四个 NightOps)持续 ok。

→ 判据:任务健康与否不取决于属于哪个 agent,
        而取决于【它续用的那个会话是否还是可用资产】。

用法: python3 scripts/session-health-checker.py [--json]
"""
import json, sqlite3, subprocess, os, glob, sys, datetime

LEASES_DB = '/home/zhiping/.openclaw/state/openclaw.sqlite'
AGENTS_DIR = '/home/zhiping/.openclaw/agents'
CTX_EVENT_LIMIT = 5000       # transcript 条数超此值 → 疑似 context overflow
CTX_BYTES_LIMIT = 5 * 1024 * 1024

def gateway_pid():
    try:
        return int(subprocess.run(['pgrep','-f','openclaw.*dist/index.js'],capture_output=True,text=True,timeout=20).stdout.split()[0])
    except Exception:
        return None

def leased_agents(pid):
    if not pid:
        return set()
    try:
        c = sqlite3.connect(f'file:{LEASES_DB}?mode=ro', uri=True, timeout=8)
        return {r[0] for r in c.execute('SELECT DISTINCT agent_id FROM agent_database_leases WHERE owner_pid=?', (pid,))}
    except Exception:
        return set()

def main():
    pid = gateway_pid()
    leased = leased_agents(pid)
    out = []
    for f in sorted(glob.glob(f'{AGENTS_DIR}/*/agent/openclaw-agent.sqlite')):
        ag = os.path.basename(os.path.dirname(os.path.dirname(f)))
        try:
            c = sqlite3.connect('file:' + f + '?mode=ro', uri=True, timeout=8)
            for key, cid in c.execute('SELECT session_key, current_session_id FROM session_nodes'):
                if not key.startswith('agent:' + ag + ':main'):
                    continue
                n = c.execute('SELECT COUNT(*) FROM transcript_events WHERE session_id=?', (cid,)).fetchone()[0]
                b = c.execute('SELECT SUM(LENGTH(event_json)) FROM transcript_events WHERE session_id=?', (cid,)).fetchone()[0] or 0
                issues = []
                if ag not in leased:
                    issues.append('该 agent 无现役 lease → 写操作必触发 reclaim 超时')
                # 注意:上下文超限是【风险】不是【必然失败】——
                # 实测 agent:main:main 也有 14319 条,但 heartbeat-main 仍 err=0。
                # 取决于任务实际读了多少历史。
                if n > CTX_EVENT_LIMIT:
                    issues.append(f'transcript {n} 条 > {CTX_EVENT_LIMIT} → 【风险】续用该会话且读大量历史的任务会 context overflow')
                if b > CTX_BYTES_LIMIT:
                    issues.append(f'事件体 {b//1048576}MB > {CTX_BYTES_LIMIT//1048576}MB → 【风险】上下文超限')
                out.append({'agent': ag, 'session': key, 'events': n, 'bytes': b, 'leased': ag in leased, 'issues': issues})
            c.close()
        except Exception:
            pass
    # 分级:两类根因的处置方式完全不同,不能混报
    #  P0 lease 缺失 → 写操作必失败(每次都失败,100% 可预测)
    #  P1 上下文超限 → 【风险】而非必然失败:实测 agent:main:main 也有 14319 条,
    #     但 heartbeat-main 仍 err=0(取决于任务实际读多少历史)
    for o in out:
        if any('lease' in i for i in o['issues']):
            o['severity'] = 'P0'
        elif o['issues']:
            o['severity'] = 'P1'
        else:
            o['severity'] = 'OK'
    risky = [o for o in out if o['issues']]
    if '--json' in sys.argv:
        print(json.dumps({'gateway_pid': pid, 'leased': sorted(leased),
                        'P0': [o for o in risky if o['severity'] == 'P0'],
                        'P1': [o for o in risky if o['severity'] == 'P1']},
                       ensure_ascii=False, indent=2))
        return 1 if risky else 0
    print(f'  gateway pid={pid}  有 lease 的 agent: {sorted(leased)}')
    if not risky:
        print('  ✅ 未发现处于风险状态的主会话')
        return 0
    p0 = [o for o in risky if o['severity'] == 'P0']
    p1 = [o for o in risky if o['severity'] == 'P1']
    if p0:
        print(f'  🔴 P0 lease 缺失({len(p0)} 个,写操作 100% 失败):')
        for o in p0:
            print(f"    {o['agent']:12} {o['session'][:40]:42} {o['events']:6} 条 {o['bytes']//1048576:5}MB")
            for i in o['issues']:
                print(f'        - {i}')
    if p1:
        print(f'  🟡 P1 上下文超限({len(p1)} 个,仅续用该会话的任务会失败):')
        for o in p1:
            print(f"    {o['agent']:12} {o['session'][:40]:42} {o['events']:6} 条 {o['bytes']//1048576:5}MB")
            for i in o['issues']:
                print(f'        - {i}')
    print('  → P0 处置: 停机 openclaw doctor --fix(需 Gateway 重启)')
    print('  → P1 处置: 若某任务反复 context overflow,把它改 isolated 或轮转主会话')
    return 1

if __name__ == '__main__':
    sys.exit(main())
