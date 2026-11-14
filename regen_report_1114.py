import json, collections, re
from pathlib import Path
import networkx as nx
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json, to_html

g = json.load(open('graphify-out/graph.json'))

G = nx.Graph()
for n in g['nodes']:
    G.add_node(n['id'], **{k: v for k, v in n.items() if k != 'id'})
for l in g['links']:
    s = l.get('source') or l.get('_src')
    t = l.get('target') or l.get('_tgt')
    if s is None or t is None:
        continue
    G.add_edge(s, t, **{k: v for k, v in l.items() if k not in ('source', 'target', '_src', '_tgt')})

communities = cluster(G)
cohesion = score_all(G, communities)
gods = god_nodes(G)
surprises = surprising_connections(G, communities)

STOP = set('the a an of and or to in for on with by is are was were be been being at as from that this it its '
           'via using use used new toward towards more less than then when what which how why can may not no '
           'over under into out up down about llm ai model models request pull merge chore update'.split())


def words(s):
    return [w for w in re.split(r'[^A-Za-z0-9]+', s.lower()) if len(w) > 2 and w not in STOP]


# tf-idf over community membership: terms distinctive to this community
_doc_freq = collections.Counter()
for cid, members in communities.items():
    seen = set()
    for m in members:
        seen.update(set(words(G.nodes[m].get('label', ''))))
    for w in seen:
        _doc_freq[w] += 1
N = len(communities)


def auto_label(cid):
    cnt = collections.Counter()
    for m in communities[cid]:
        cnt.update(set(words(G.nodes[m].get('label', ''))))
    scored = []
    for w, c in cnt.items():
        if c < 2 and len(communities[cid]) > 40:
            continue
        idf = __import__('math').log(N / (1 + _doc_freq[w]))
        scored.append((c * idf, c, w))
    scored.sort(reverse=True)
    top = [w for _, _, w in scored[:4]]
    if not top:
        top = [w for _, _, w in cnt.most_common(4)]
    return ' & '.join(w.title() for w in top) if top else 'Community ' + str(cid)


def member_labels(cid):
    return ' || '.join(G.nodes[m].get('label', '') for m in communities[cid])


# ---------- content-based label rules (stable across runs, unlike community ids) ----------
RULES = [
    ('MCP Servers, Inspector & Spec Toolchain Security',
     lambda txt: txt.count('MCP servers') >= 5 and ('mcp-server' in txt or 'GHSA' in txt)),
    ('MCP Registries, SDKs & Multi-Window Scout Snapshots',
     lambda txt: ('MCP registry' in txt or 'modelcontextprotocol' in txt) and 'registry' in txt.lower()),
    ('MCP Specification, SDKs & Inspector Releases',
     lambda txt: txt.count('MCP spec') >= 4 or txt.count('MCP python-sdk') >= 4
     or txt.count('MCP typescript-sdk') >= 4 or txt.count('MCP go-sdk') >= 4),
    ('Agent Memory, Tool Use & Claude Code Ecosystem',
     lambda txt: 'claude-code' in txt.lower() or 'claude code' in txt.lower()),
    ('OpenAI, Vercel & Agent Skill Planning',
     lambda txt: 'openai-python' in txt.lower() and 'vercel ai sdk' in txt.lower()),
    ('MCP Server Registry Releases & Release Stream',
     lambda txt: 'MCP registry' in txt and txt.count('release') >= 2),
    ('Prompt Injection, Memory Poisoning & Agent Detection',
     lambda txt: any(k in txt.lower() for k in ['prompt injection', 'memory poison', 'hijack', 'detector'])),
    ('Multi-Agent Swarms, Swarm Coordination & Team Defense',
     lambda txt: any(k in txt.lower() for k in ['swarm', 'multi-agent', 'peer communication', 'perimeter defense'])),
    ('Agent Safety, Guardrails & Deployment Trust',
     lambda txt: any(k in txt.lower() for k in ['guardrail', 'safety', 'distillation attack', 'biosecurity',
                                                'dual-use', 'red-team', 'privilege'])),
    ('Agent Harnesses, Tool Use & Context Management',
     lambda txt: any(k in txt.lower() for k in ['harness', 'tool-use', 'tool use', 'context management'])),
    ('RL Training, Reward & Post-Training',
     lambda txt: any(k in txt.lower() for k in ['reinforcement learning', 'rlhf', 'post-train', 'reward model'])),
    ('Long-Context, Memory Systems & Retrieval',
     lambda txt: any(k in txt.lower() for k in ['long-context', 'memory system', 'retrieval', 'forget'])),
    ('Planning, Skill Routing & Workflow Automation',
     lambda txt: any(k in txt.lower() for k in ['planning', 'skill routing', 'workflow'])),
    ('Model Evaluation, Benchmarks & Diagnostics',
     lambda txt: any(k in txt.lower() for k in ['bench', 'evaluation', 'evaluating', 'benchmark'])),
    ('Inference Infrastructure, Scheduling & Efficiency',
     lambda txt: any(k in txt.lower() for k in ['inference', 'scheduling', 'kv cach', 'attention', 'speculative'])),
    ('Privacy, Access Control & Secure Deployment',
     lambda txt: any(k in txt.lower() for k in ['privacy', 'access control', 'authorization', 'trusted access'])),
]

labels = {}
for cid in communities:
    txt = member_labels(cid)
    label = None
    for name, test in RULES:
        try:
            if test(txt):
                label = name
                break
        except Exception:
            continue
    labels[cid] = label or auto_label(cid)

# ensure uniqueness
used = collections.Counter(labels.values())
for cid in list(labels):
    if used[labels[cid]] > 1:
        labels[cid] = auto_label(cid)
        used[labels[cid]] += 1

Path('.graphify_labels.json').write_text(json.dumps({str(k): v for k, v in labels.items()}, indent=1))

questions = suggest_questions(G, communities, labels)
detection = {'total_files': 0, 'total_words': 0, 'warning': 'cluster-only mode — file stats not available'}
report = generate(G, communities, cohesion, labels, gods, surprises,
                  detection, {'input': 0, 'output': 0}, '.', suggested_questions=questions)
Path('graphify-out/GRAPH_REPORT.md').write_text(report)

analysis = {
    'communities': {str(k): v for k, v in communities.items()},
    'cohesion': {str(k): v for k, v in cohesion.items()},
    'gods': gods,
    'surprises': surprises,
    'questions': questions,
}
Path('.graphify_analysis.json').write_text(json.dumps(analysis, indent=1))

to_json(G, communities, 'graphify-out/graph.json')
if G.number_of_nodes() <= 5000:
    to_html(G, communities, 'graphify-out/graph.html', community_labels=labels)
    print('graph.html written')

print('nodes', G.number_of_nodes(), 'edges', G.number_of_edges(), 'communities', len(communities))
for cid in sorted(communities, key=lambda c: -len(communities[c])):
    print(' ', cid, len(communities[cid]), '|', labels[cid][:70], '| cohesion', round(cohesion.get(cid, 0), 4))
