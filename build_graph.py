import json, os, re, hashlib
from datetime import datetime, timezone

STAMP = '2026-10-24'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

def slug(s, n=70):
    s = re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_').lower()
    return s[:n] if s else 'node_' + hashlib.md5(s.encode()).hexdigest()[:8]

nodes = []
links = []
seen_node = set()
seen_link = set()

def add_node(nid, label, kind, attrs=None):
    if nid in seen_node: return nid
    seen_node.add(nid)
    nodes.append({'id': nid, 'kind': kind, 'label': label, 'attrs': attrs or {}})
    return nid

def add_link(src, tgt, rel, conf='EXTRACTED'):
    key = (src, tgt, rel)
    if key in seen_link: return
    seen_link.add(key)
    links.append({'source': src, 'target': tgt, 'relation': rel, 'confidence': conf})

theme_id = add_node('theme-' + STAMP, 'AI/Agent/MCP ' + STAMP, 'theme', {'date': STAMP})

# ---- arXiv nodes ----
THEME_RULES = [
    ('mcp', ['model context protocol', 'mcp server', 'mcp gateway', 'mcp agent', 'mcp-']),
    ('agent-safety', ['safety', 'attack', 'injection', 'safety', 'corrupt', 'poison', 'phishing', 'vulnerab', 'credential', 'supervis', 'governance', 'governed', 'launder', 'approval']),
    ('memory', ['memory', 'memori', 'retriev', 'forget', 'integrity', 'persistent', 'kv cach']),
    ('tool-use', ['tool', 'tool-use', 'tool selection', 'function call']),
    ('multi-agent', ['multi-agent', 'multi agent', 'sub-agent', 'delegat', 'orchestrat', 'herding', 'cascade']),
    ('eval-bench', ['bench', 'eval', 'evaluation', 'audit', 'diagnos', 'metric']),
    ('rl-train', ['reinforcement learning', 'rl ', 'post-train', 'distillat', 'reward', 'rlhf', 'policy optimization']),
    ('planning', ['plan', 'skill', 'workflow', 'search', 'routing']),
]

def classify(text):
    t = text.lower()
    for name, kws in THEME_RULES:
        for k in kws:
            if k in t: return name
    return 'general'

arxiv_files = [('scout-raw/arxiv-csAI-parsed.json','cs.AI'), ('scout-raw/arxiv-mcpexact-parsed.json','MCP'), ('scout-raw/arxiv-toolagent-parsed.json','tool-agent')]
arxiv_count = 0
for f, qset in arxiv_files:
    if not os.path.exists(f): continue
    for x in json.load(open(f)):
        aid = x['id'].split('v')[0]
        nid = 'arxiv:' + aid
        theme = classify(x['title'] + ' ' + x['summary'])
        add_node(nid, x['title'], 'arxiv', {'id': aid, 'theme': theme, 'cats': x['cats'][:3], 'published': x['published'][:10], 'query_set': qset, 'source': 'arxiv'})
        add_link(theme_id, nid, 'contains')
        arxiv_count += 1

# ---- GitHub release nodes ----
REL_FILES = [
    ('scout-raw/gh-mcp-spec-releases.json','MCP spec','mcp-spec'),
    ('scout-raw/gh-mcp-servers-releases.json','MCP servers','mcp-servers'),
    ('scout-raw/gh-mcp-inspector-releases.json','MCP inspector','mcp-inspector'),
    ('scout-raw/gh-anthropic-sdk-py.json','anthropic-sdk-python','sdk-py'),
    ('scout-raw/gh-modelcontextprotocol-python-sdk.json','MCP python-sdk','mcp-sdk-py'),
    ('scout-raw/github-mcp-ts.json','MCP typescript-sdk','mcp-sdk-ts'),
    ('scout-raw/github-mcp-rust.json','MCP rust-sdk','mcp-sdk-rust'),
    ('scout-raw/github-mcp-csharp.json','MCP csharp-sdk','mcp-sdk-csharp'),
    ('scout-raw/github-mcp-go.json','MCP go-sdk','mcp-sdk-go'),
    ('scout-raw/gh-claude-code-releases.json','claude-code','claude-code'),
]
rel_count = 0
for f, label, tag in REL_FILES:
    if not os.path.exists(f): continue
    d = json.load(open(f))
    if not isinstance(d, list): continue
    repo_id = 'repo:' + tag
    add_node(repo_id, label, 'repo', {'tag': tag})
    add_link(theme_id, repo_id, 'tracks')
    for r in d[:3]:
        tagname = str(r.get('tag_name'))
        nid = 'release:' + tag + ':' + tagname
        add_node(nid, label + ' ' + tagname, 'release', {'repo': label, 'tag': tagname, 'published': r.get('published_at'), 'url': r.get('html_url')})
        add_link(repo_id, nid, 'released')
        add_link(nid, theme_id, 'observed_in')
        rel_count += 1

# ---- commit nodes ----
COMMIT_FILES = [
    ('scout-raw/gh-spec-commits.json','MCP spec'),
    ('scout-raw/gh-servers-commits.json','MCP servers'),
    ('scout-raw/github-mcp-registry.json','MCP registry'),
    ('scout-raw/gh-extauth-commits.json','MCP ext-auth'),
    ('scout-raw/gh-extapps-commits.json','MCP ext-apps'),
]
com_count = 0
for f, label in COMMIT_FILES:
    if not os.path.exists(f): continue
    d = json.load(open(f))
    if not isinstance(d, list): continue
    repo_id = 'repo:' + slug(label).replace('_','-')
    for c in d[:6]:
        try:
            msg = c['commit']['message'].split(chr(10))[0]
            date = c['commit']['author']['date'][:10]
        except Exception: continue
        nid = 'commit:' + hashlib.md5((label + msg + date).encode()).hexdigest()[:10]
        add_node(nid, msg[:90], 'commit', {'repo': label, 'date': date, 'sha': c.get('sha','')[:8]})
        add_link(repo_id, nid, 'committed')
        add_link(nid, theme_id, 'observed_in')
        com_count += 1

# ---- news nodes ----
NEWS = [
    ('OpenAI - Decisions API GA (2026-10-22)','openai','decisions-api','Built with GPT-6 Luna; bounded-answer decisions up to 10x faster than GPT-6 Luna via the Responses API. Native GPT-Live integration, prompt caching, inference residency in US and EU, native JSON inputs, up to 400 questions per request.'),
    ('OpenAI - Patch the Planet (2026-10-21)','openai','patch-the-planet','GPT-5.6 Sol discovered critical PHP vulnerabilities; Wiz independently reported both. PHP maintainers led the fixes. A Defender Window let defenders prepare ahead of disclosure. 1 billion USD subsidized Daybreak access committed. PHP version checker released as a Codex skill.'),
    ('OpenAI - Securing our frontier model training environment (2026-10-23)','openai','model-containment','Strengthened containment for internal frontier-model training and evaluation, red-teamed by their own strongest models. Addresses sandbox escape, internal service exploitation, and cross-sandbox agent communication.'),
    ('Kimi - Kimi K3.1 Pro and K3.1 Pro Highspeed (2026-10-23)','moonshot','kimi-k3-1-pro','Most capable 3T-class open-weight model to date with a 1M-token context window. Large-scale joint RL across hundreds of downstream domains. Highspeed variant is 2-3x faster. Weights by Nov 4. Available on Vercel AI Gateway.'),
    ('Vercel - How Vercel Agent accesses production safely (2026-10-23)','vercel','agent-permission-scopes','Plan determines permissions. The agent investigates, then proposes a plan; approving grants the scopes. Named scopes such as read:deployment versus read-write:deployment. Any plan beyond read-only waits for approval as a whole.'),
    ('Vercel - Death to long-lived static credentials (2026-10-22)','vercel','oidc-for-agents','Machine-to-machine auth still resembles HTTPS in 2010. Long-lived static credentials remain the default. As agents gain more work they hold credentials granting far broader permissions. Built OIDC UI and set new Marketplace auth requirements.'),
    ('Google - Gemini 4 Argon (2026-10-13)','google','gemini-4-argon','Built to solve the hardest problems.'),
]
news_count = 0
for label, org, tag, body in NEWS:
    nid = 'news:' + tag
    add_node(nid, label, 'news', {'org': org, 'tag': tag, 'date': label[-12:-1], 'summary': body})
    add_link(theme_id, nid, 'covers')
    org_id = 'org:' + org
    add_node(org_id, org, 'org', {})
    add_link(org_id, nid, 'published')
    news_count += 1

# cross-links: news <-> arxiv themes
for label, org, tag, body in NEWS:
    nid = 'news:' + tag
    th = classify(body)
    if th != 'general':
        add_link(nid, 'theme:' + th, 'relates_to', conf='INFERRED')

for n in list(nodes):
    if n['kind'] == 'arxiv':
        tn = 'theme:' + n['attrs']['theme']
        add_node(tn, n['attrs']['theme'], 'cluster', {})
        add_link(n['id'], tn, 'belongs_to', conf='INFERRED')

snapshot = {'nodes': nodes, 'links': links}
json.dump(snapshot, open(OUT + '/snapshot.json', 'w'), ensure_ascii=False, indent=1)
manifest = {
    'date': STAMP,
    'kind': 'nightly-scout-snapshot',
    'sources': ['arxiv:cs.AI','arxiv:cs.MA','arxiv:agent/mcp-keyword','arxiv:mcp-exact','arxiv:tool-agent','github:mcp-org','github:spec/servers/inspector/anthropic-sdk-py','github:mcp-sdk-ts/rust/csharp/go','github:registry/ext-auth/ext-apps','github:claude-code','hn:firebaseio','rss:openai/google/vercel','web_fetch:articles'],
    'raw_dir': 'scout-raw',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'news_count': news_count,
    'next_window': '2026-10-25T00:30+08:00'
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count, 'commits', com_count, 'news', news_count)
