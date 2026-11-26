#!/usr/bin/env python3
"""会话健康度检查 (2026-11-27 重写 v3)。

★ 三次教训都写在这里:
  v1: 用 python sqlite3 直连 live agent DB → 违反 OpenClaw 工具策略
      ("external sqlite3 cannot open databases under the active OpenClaw state directory")
  v2: lease 判定拿不到数据时,把所有 agent 都判成 P0 → 【证据不足却下断言】
  v3: lease 只从【日志证据】(active-leases receipt)推断;取不到就明说不可判定,
      绝不默认判 P0。数据源全部是官方只读接口,不碰 live DB。

判据 (v42): 任务健康与否取决于【它续用的那个会话是否还是可用资产】。
  P0: 有证据表明某 agent 的 lease 已失效 → 写操作会 100% 失败
  P1: 主会话上下文占用超限 → 续用它且读大量历史的任务有 overflow 风险
      (是【风险】非必然: 实测 agent:main:main 占用高但 heartbeat-main err=0)

用法: python3 scripts/session-health-checker.py [--json]
"""
import json, os, re, subprocess, sys, glob

CTX_TOKEN_LIMIT = 200_000   # MiniMax-M2.7 上限 205k,取保守值
CTX_WARN_RATIO = 0.5
LOG_GLOB = "/tmp/openclaw/openclaw-*.log"
LOG_TAIL_LINES = 20000

def run_json(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return json.loads(r.stdout or "{}")
    except Exception as e:
        return {"__error__": str(e)}

def gateway_pid():
    try:
        r = subprocess.run(["pgrep", "-f", "openclaw.*dist/index.js"],
                           capture_output=True, text=True, timeout=20)
        return int(r.stdout.split()[0]) if r.stdout.strip() else None
    except Exception:
        return None

def lease_evidence():
    """从 Gateway 日志推断 lease 状态。返回 (有证据的 agent 集合, 证据来源说明)。

    日志里出现 active-leases receipt ⇒ 该 agent 当时持有 lease;
    出现 reclamation checkpoint expired refusal ⇒ 该 agent 的 lease 已失效。
    两者都是【日志证据】,不是直接读 lease 表。
    """
    leased, broken = set(), set()
    files = sorted(glob.glob(LOG_GLOB), key=os.path.getmtime)[-2:]
    if not files:
        return None, "无日志文件"
    pat_ok = re.compile(r"active-leases")
    pat_bad = re.compile(r"reclamation commit checkpoint expired")
    for f in files:
        try:
            with open(f, errors="ignore") as fh:
                lines = fh.readlines()[-LOG_TAIL_LINES:]
        except Exception:
            continue
        for ln in lines:
            if pat_bad.search(ln):
                for m in re.findall(r"/agents/([A-Za-z0-9_-]+)/agent/", ln):
                    broken.add(m)
            elif pat_ok.search(ln):
                for m in re.findall(r"/agents/([A-Za-z0-9_-]+)/agent/", ln):
                    leased.add(m)
    return {"leased": leased, "broken": broken}, f"日志证据({len(files)} 个文件,末尾 {LOG_TAIL_LINES} 行)"

def main_sessions():
    d = run_json(["openclaw", "sessions", "--all-agents", "--json", "--limit", "300"])
    items = d if isinstance(d, list) else (d.get("sessions") or d.get("items") or [])
    return [s for s in items
            if str(s.get("key", "")).count(":") == 2
            and str(s.get("key", "")).split(":")[2] == "main"]

def main():
    pid = gateway_pid()
    ev, src = lease_evidence()
    leased = ev["leased"] if ev else set()
    broken = ev["broken"] if ev else set()
    rows = main_sessions()
    out = []
    for s in rows:
        key = s.get("key", "")
        ag = s.get("agentId") or key.split(":")[1]
        tok = s.get("totalTokens") or 0
        issues, lvl = [], "OK"
        if ag in broken:
            issues.append("P0 日志证据:该 agent lease 失效 (reclamation checkpoint expired) → 写操作 100% 失败")
            lvl = "P0"
        if tok > CTX_TOKEN_LIMIT:
            issues.append(f"P1 上下文占用 {tok:,} token > {CTX_TOKEN_LIMIT:,} → 续用且读大量历史会 context overflow")
            lvl = "P0" if lvl == "P0" else "P1"
        elif tok > CTX_TOKEN_LIMIT * CTX_WARN_RATIO:
            issues.append(f"P2 上下文占用 {tok:,} token 已过 {int(CTX_WARN_RATIO*100)}% → 逼近上限")
            lvl = "P0" if lvl == "P0" else ("P1" if lvl == "P1" else "P2")
        if s.get("abortedLastRun"):
            issues.append("P2 上一次运行被 abort")
            lvl = "P0" if lvl == "P0" else ("P1" if lvl == "P1" else "P2")
        out.append({"agent": ag, "session": key, "tokens": tok, "issues": issues,
                    "severity": lvl,
                    "lease": ("broken" if ag in broken else
                              ("held" if ag in leased else "unknown"))})
    out.sort(key=lambda o: ({"P0": 0, "P1": 1, "P2": 2, "OK": 3}[o["severity"]], -o["tokens"]))
    if "--json" in sys.argv:
        print(json.dumps({"gateway_pid": pid, "lease_source": src,
                         "lease_evidence": {"leased": sorted(leased), "broken": sorted(broken)},
                         "sessions": out}, ensure_ascii=False, indent=2))
        return 1 if any(o["issues"] for o in out) else 0
    print(f"  gateway pid={pid}  数据源=openclaw sessions(官方只读接口)")
    print(f"  lease 证据: {src}")
    print(f"    持有 lease: {sorted(leased) or "(日志窗口内未记录)"}")
    print(f"    lease 失效: {sorted(broken) or "(无)"}")
    print("    注: 未出现在两栏的 agent = 不可判定(不是没有 lease)")
    risky = [o for o in out if o["issues"]]
    if not risky:
        print("  ✅ 未发现处于风险状态的主会话")
        return 0
    for lvl, icon in (("P0", "🔴"), ("P1", "🟡"), ("P2", "🔵")):
        g = [o for o in risky if o["severity"] == lvl]
        if not g:
            continue
        print(f"  {icon} {lvl} ({len(g)} 个):")
        for o in g:
            print(f"    {o['agent']:12} {o['session'][:36]:38} {o['tokens']:>9,} token  lease={o['lease']}")
            for i in o["issues"]:
                print(f"        - {i}")
    print("  → P0 处置: 停机后 openclaw doctor --fix(需 Gateway 重启)")
    print("  → P1 处置: 该 agent 的 target=main 任务改 isolated,或轮转主会话")
    return 1

if __name__ == "__main__":
    sys.exit(main())