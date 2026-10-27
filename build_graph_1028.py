import json, os, re, hashlib, glob

STAMP = '2026-10-28'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)


def slug(s, n=70):
    s = re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_').lower()
    return s[:n] if s else 'node_' + hashlib.md5(s.encode()).hexdigest()[:8]


nodes, links = [], []
seen_node, seen_link = set(), set()


def add_node(nid, label, kind, attrs=None):
    if nid in seen_node:
        return nid
    seen_node.add(nid)
    nodes.append({'id': nid, 'kind': kind, 'label': label, 'attrs': attrs or {}})
    return nid


def add_link(src, tgt, rel, conf='EXTRACTED'):
    key = (src, tgt, rel)
    if key in seen_link:
        return
    seen_link.add(key)
    links.append({'source': src, 'target': tgt, 'relation': rel, 'confidence': conf})


theme_id = add_node('theme-' + STAMP, 'AI/Agent/MCP ' + STAMP, 'theme', {'date': STAMP})

THEME_RULES = [
    ('mcp', ['model context protocol', 'mcp server', 'mcp gateway', 'mcp agent', 'mcp-', 'mcp ']),
    ('agent-safety', ['safety', 'attack', 'injection', 'corrupt', 'poison', 'phishing', 'vulnerab', 'credential',
                      'supervis', 'governance', 'governed', 'launder', 'approval', 'authoriz', 'adversar', 'audit',
                      'verif', 'secure', 'trust', 'jailbreak', 'exploit', 'privilege', 'scope']),
    ('memory', ['memory', 'memori', 'retriev', 'forget', 'integrity', 'persistent', 'kv cach', 'trajectory']),
    ('tool-use', ['tool', 'tool-use', 'tool selection', 'function call']),
    ('multi-agent', ['multi-agent', 'multi agent', 'sub-agent', 'delegat', 'orchestrat', 'herding', 'cascade',
                      'routing', 'collaborat']),
    ('eval-bench', ['bench', 'eval', 'evaluation', 'diagnos', 'metric']),
    ('rl-train', ['reinforcement learning', 'rl ', 'post-train', 'distillat', 'reward', 'rlhf', 'policy optimization']),
    ('planning', ['plan', 'skill', 'workflow', 'search', 'routing']),
    ('enterprise', ['enterprise', 'gateway', 'policy-driven', 'budget', 'vendor', 'multi-tenant', 'observability']),
]


def classify(text):
    t = text.lower()
    for name, kws in THEME_RULES:
        for k in kws:
            if k in t:
                return name
    return 'general'


# ---- arXiv ----
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1028.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1028.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1028.json', 'MCP'),
               ('scout-raw/arxiv-toolagent-parsed-1028.json', 'tool-agent')]
arxiv_count = 0
for f, qset in arxiv_files:
    if not os.path.exists(f):
        continue
    for x in json.load(open(f)):
        aid = x['id'].split('v')[0]
        nid = 'arxiv:' + aid
        theme = classify(x['title'] + ' ' + x['summary'])
        add_node(nid, x['title'], 'arxiv', {'id': aid, 'theme': theme, 'cats': x['cats'][:3],
                                           'published': x['published'][:10], 'query_set': qset,
                                           'source': 'arxiv'})
        add_link(theme_id, nid, 'contains')
        arxiv_count += 1

# ---- releases ----
REL_FILES = [
    ('scout-raw/gh-1028-modelcontextprotocol-servers.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1028-modelcontextprotocol-modelcontextprotocol.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1028-modelcontextprotocol-registry.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1028-modelcontextprotocol-inspector.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1028-modelcontextprotocol-python-sdk.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1028-modelcontextprotocol-typescript-sdk.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1028-modelcontextprotocol-go-sdk.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1028-modelcontextprotocol-swift-sdk.json', 'MCP swift-sdk', 'mcp-sdk-swift'),
    ('scout-raw/gh-1028-modelcontextprotocol-csharp-sdk.json', 'MCP csharp-sdk', 'mcp-sdk-csharp'),
    ('scout-raw/gh-1028-modelcontextprotocol-ruby-sdk.json', 'MCP ruby-sdk', 'mcp-sdk-ruby'),
    ('scout-raw/gh-1028-modelcontextprotocol-rust-sdk.json', 'MCP rust-sdk', 'mcp-sdk-rust'),
    ('scout-raw/gh-1028-modelcontextprotocol-java-sdk.json', 'MCP java-sdk', 'mcp-sdk-java'),
    ('scout-raw/gh-1028-modelcontextprotocol-kotlin-sdk.json', 'MCP kotlin-sdk', 'mcp-sdk-kotlin'),
    ('scout-raw/gh-1028-modelcontextprotocol-php-sdk.json', 'MCP php-sdk', 'mcp-sdk-php'),
    ('scout-raw/gh-1028-modelcontextprotocol-ext-apps.json', 'MCP ext-apps', 'mcp-ext-apps'),
    ('scout-raw/gh-1028-anthropics-anthropic-sdk-python.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1028-anthropics-claude-code.json', 'claude-code', 'claude-code'),
]
rel_count = 0
for f, label, tag in REL_FILES:
    if not os.path.exists(f):
        continue
    d = json.load(open(f))
    if not isinstance(d, list):
        continue
    repo_id = 'repo:' + tag
    add_node(repo_id, label, 'repo', {'tag': tag})
    add_link(theme_id, repo_id, 'tracks')
    for r in d[:4]:
        tagname = str(r.get('tag_name'))
        nid = 'release:' + tag + ':' + tagname
        add_node(nid, label + ' ' + tagname, 'release',
                 {'repo': label, 'tag': tagname, 'published': r.get('published_at'),
                  'url': r.get('html_url')})
        add_link(repo_id, nid, 'released')
        add_link(nid, theme_id, 'observed_in')
        rel_count += 1

# ---- commits ----
com_count = 0
for f in sorted(glob.glob('scout-raw/gh-1028-commits-*.json')):
    label = f.replace('scout-raw/gh-1028-commits-modelcontextprotocol-', 'MCP ').replace('-', ' ').replace('.json', '')
    d = json.load(open(f))
    if not isinstance(d, list):
        continue
    repo_id = 'repo:' + slug(label).replace('_', '-')
    add_node(repo_id, label, 'repo', {'tag': slug(label).replace('_', '-')})
    add_link(theme_id, repo_id, 'tracks')
    for c in d[:12]:
        try:
            msg = c['commit']['message'].split(chr(10))[0]
            date = c['commit']['author']['date'][:10]
        except Exception:
            continue
        nid = 'commit:' + hashlib.md5((label + msg + date).encode()).hexdigest()[:10]
        add_node(nid, msg[:90], 'commit', {'repo': label, 'date': date, 'sha': c.get('sha', '')[:8]})
        add_link(repo_id, nid, 'committed')
        add_link(nid, theme_id, 'observed_in')
        com_count += 1

# ---- advisories ----
adv_count = 0
for f, repo_tag in [('scout-raw/gh-1028-advisories-servers.json', 'mcp-servers'),
                    ('scout-raw/gh-1028-advisories-registry.json', 'mcp-registry')]:
    if not os.path.exists(f):
        continue
    for a in json.load(open(f)):
        gid = a.get('ghsa_id')
        if not gid:
            continue
        nid = 'advisory:' + gid
        add_node(nid, a.get('summary', gid)[:110], 'advisory',
                 {'ghsa': gid, 'severity': a.get('severity'), 'published': a.get('published_at'),
                  'repo': repo_tag})
        add_link('repo:' + repo_tag, nid, 'advisory')
        add_link(nid, theme_id, 'observed_in')
        adv_count += 1

# ---- news ----
NEWS = [
    ('OpenAI - Working with academic communities to build scientific understanding (2026-10-26)', 'openai', 'openai-math-scientific',
     'OpenAI published results on the Kakeya conjecture, the Exponential Time Hypothesis and quantum chromodynamics, '
     'including Lean formalizations, and asked researchers to verify and build on them. The Exponential Time Hypothesis '
     'is False: a deterministic algorithm exactly counts satisfying assignments of fixed-width CNF formulas in '
     'subexponential time and polynomial space, refuting ETH via the 3-SAT case. A working group led by Russell '
     'Impagliazzo, Ramamohan Paturi and Ryan Williams will examine the proof; materials were released immediately at '
     'the group request. The openai/math catalogue now holds 721 manuscripts in 373 families with ~42% of top-line '
     'results formalized in Lean.'),
    ('OpenAI - Introducing GPT-6.1 Terra (2026-10-26)', 'openai', 'gpt-6-1-terra',
     'Bringing fast and capable computer use to everyone. Also shipped the same day: Greptile using GPT-6 Astra for '
     'code review, CodeRabbit using GPT-6.1 Sol for code security, ChatGPT Signals work-usage data across 165 work '
     'activities in ~100 countries, and Codex Ultrafast for incident investigation. GPT-6.1 Terra is available on the '
     'Vercel AI Gateway.'),
    ('OpenAI - Greptile takes bug detection beyond code review with GPT-6 Astra (2026-10-26)', 'openai', 'greptile-gpt6-astra',
     'How Greptile uses GPT-6 Astra to test user workflows, Daybreak to strengthen security, and Codex to reduce rework.'),
    ('Anthropic - files S-1 with the SEC for proposed initial public offering (2026-10-26)', 'anthropic', 'anthropic-s1-sec',
     'Anthropic filed an S-1 with the SEC for a proposed initial public offering, announced on the Anthropic news page '
     'on Oct 26, 2026. This is the first concrete IPO filing step by a frontier lab and reframes the governance and '
     'funding baselines that agent-safety work has to operate inside.'),
    ('Anthropic - Donating Agent Skills to the Agentic AI Foundation (2026-10-22)', 'anthropic', 'agent-skills-donation',
     'Anthropic donated Agent Skills to the Agentic AI Foundation, noting that ChatGPT, Cursor, GitHub Copilot and VS Code '
     'have integrated Agent Skills since the standard was published in December 2025. The same window saw MCP TypeScript SDK '
     'v2.4.0 ship Skills over MCP (SEP-2640), so the skills layer is converging across both ecosystems.'),
    ('Vercel - How Vercel Agent accesses production safely (2026-10-23)', 'vercel', 'agent-permission-scopes',
     'Plan determines permissions. The agent investigates under a read-only baseline, then proposes a plan; approving grants '
     'the scopes. Named scopes such as read:deployment versus read-write:deployment. Beyond the read-only baseline a plan '
     'waits for approval as a whole. The scope registry is shared with the OAuth service so stale or renamed scopes are '
     'caught during planning. Resuming work requires an active approved plan; a stopped plan fails the check even with an '
     'unexpired token.'),
    ('Vercel - Discover 1000+ services on Vercel Connect from the CLI (2026-10-26)', 'vercel', 'vercel-connect-cli',
     'More than 1000 services are discoverable from the CLI on Vercel Connect, alongside Scale AI AgentEnv evals running on '
     'Vercel Sandbox and Vercel Agent now validating alerts before paging.'),
    ('Registry - MCP registry v1.8.6 search optimization (2026-10-27)', 'mcp', 'registry-1-8-6',
     'Registry v1.8.6 selects search page keys through covering indexes before fetching complete records, plans searches for '
     'their actual parameter values, optimizes namespace suffix searches, and requires at least three Unicode characters for '
     'nonempty search terms (shorter searches return HTTP 422). Validated burst capacity uses a 3-CPU PostgreSQL quota with '
     'the application connection pool unchanged. The preceding day was infrastructure work: production PostgreSQL shared '
     'buffers raised, GCP node size per environment configured, production node CPU capacity increased, promoted to 1.8.5, '
     'and observability for slow listing requests, request backlog and database waits.'),
    ('ext-apps - MCP ext-apps v2.0.4 (2026-10-27)', 'mcp', 'ext-apps-2-0-4',
     'pdf-server now exposes a single interact app tool by default instead of thirteen per-action app tools, because each '
     'per-action tool meant a separate approval card on hosts that approve app tools individually; per-action tools remain '
     'behind --split-app-tools. map-server adds a get-screenshot app tool. A solid-js override bump to 1.9.17 refreshed '
     'vulnerable transitives. An attempted 2.1.0 version bump was reverted the same day.'),
    ('Ruby SDK - v1.8.2 (2026-10-27)', 'mcp', 'ruby-sdk-1-8-2',
     'Finishes the encoding fixes of 1.8.1 on the client and the HTTP transport: no longer fails a request or a stream on a '
     'frame or reply it cannot encode. Consults resources_subscribe_handler for the resource URIs of a subscriptions/listen '
     'stream, strips stdio client frames as bytes, skips an unencodable stdio ping, answers an ungeneratable HTTP reply '
     'with Internal error, drops an ungeneratable buffered notification, and reports failed session notifications through '
     'the server configuration.'),
    ('Rust SDK - rmcp-v3.8.0 (2026-10-26)', 'mcp', 'rust-sdk-3-8-0',
     'Exposes body-free HTTP status errors and stops SSE reconnects on permanent GET errors. The macros crate accepts nested '
     'x-mcp-header annotations and ships LICENSE files.'),
    ('C# SDK - v2.3.0 plus 3 commits (2026-10-20/27)', 'mcp', 'csharp-sdk-2-3-0',
     'Match protocol property names case-sensitively (#1934); require explicit opt-in for legacy OAuth metadata fallback '
     '(#1952); and the server/discover probe must not commit the negotiated protocol version (#1956).'),
    ('Go SDK - 13 commits (2026-10-26/27)', 'mcp', 'go-sdk-hardening',
     'Validate the RFC 9207 iss in PerformOIDCLogin (#1442); forward an ID-JAG only to the MCP authorization server (#1438); '
     'reject null titled enum entries in elicitation schemas (#1447); preserve number precision during schema validation '
     '(#1462); forward session state through LoggingTransport (#1434); wrap ErrConnectionClosed for notifications and '
     'interrupted calls; process singleton headers correctly; stop disabled client capabilities from exposing roots; and use '
     'the default maxEventSize.'),
    ('MCP spec - still no release, 92 days (2026-10-26)', 'mcp', 'spec-still-unreleased',
     'The newest modelcontextprotocol/modelcontextprotocol tag remains 2026-07-28, now 92 days old, for an 11th consecutive '
     'run with no spec release. The spec repo added a client support matrix for Tasks and merged the file-uploads charter '
     'downloads PR. governance-wg had no commits in the window.'),
    ('Claude Code - v2.1.311 (2026-10-26)', 'anthropic', 'claude-code-2-1-311',
     'Fixes a long freeze at startup and after reading or editing files when a CLAUDE.md file holds a very long list item; '
     'fixes interrupting Claude not taking effect until a timeout while an MCP server had not answered a resource read or a '
     'skill was still downloading; fixes standard-context sessions stopping with "Usage credits required for 1M context" when '
     'a request ran over 200K tokens by compacting and continuing; fixes Write and Edit stalling up to 5 seconds and '
     'reporting 0 lines changed when changing thousands of lines; and fixes subagents being unable to use MCP tools from '
     'servers that finish connecting after the subagent starts.'),
    ('HackerNews - The Mythical Man-Month in the Age of AI (2026-10-27)', 'hackernews', 'mythical-man-month-ai',
     'Essay at 351 points and 228 comments asking what engineers still need to know when agents do the work. Sits alongside '
     '"AI promised less work. I have never worked more" at 554 points and 477 comments.'),
    ('HackerNews - PHP2Shell exploitation trends (2026-10-27)', 'security', 'php2shell-trends',
     'Wiz published exploitation trends for PHP2Shell at 136 points and 44 comments, following the PHP vulnerability class '
     'that GPT-5.6 Sol had helped surface in the 10-24 run.'),
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

for label, org, tag, body in NEWS:
    nid = 'news:' + tag
    th = classify(body)
    if th != 'general':
        add_node('theme:' + th, th, 'cluster', {})
        add_link(nid, 'theme:' + th, 'relates_to', conf='INFERRED')

for n in list(nodes):
    if n['kind'] == 'arxiv':
        tn = 'theme:' + n['attrs']['theme']
        add_node(tn, n['attrs']['theme'], 'cluster', {})
        add_link(n['id'], tn, 'belongs_to', conf='INFERRED')

# HN items as nodes
hn_count = 0
if os.path.exists('scout-raw/hn-1028.json'):
    for x in json.load(open('scout-raw/hn-1028.json')):
        if x['score'] < 100:
            continue
        nid = 'hn:' + hashlib.md5(x['title'].encode()).hexdigest()[:10]
        add_node(nid, x['title'][:110], 'news',
                 {'org': 'hackernews', 'score': x['score'], 'comments': x['comments'], 'url': x['url']})
        add_link(theme_id, nid, 'covers')
        add_link('org:hackernews', nid, 'published')
        hn_count += 1

if adv_count:
    add_link('theme:agent-safety', 'repo:mcp-servers', 'governs', conf='INFERRED')

json.dump({'nodes': nodes, 'links': links}, open(OUT + '/snapshot.json', 'w'), ensure_ascii=False, indent=1)
manifest = {
    'date': STAMP,
    'kind': 'nightly-scout-snapshot',
    'sources': ['arxiv:cs.AI', 'arxiv:cs.MA', 'arxiv:mcp', 'arxiv:tool-agent',
                'github:mcp-org-17repos-releases', 'github:mcp-org-9repos-commits',
                'github:security-advisories-servers+registry',
                'github:anthropic-sdk-python+claude-code', 'github:openai-math-raw',
                'hn:firebaseio-top30', 'rss:openai/vercel/google-ai/google-news',
                'anthropic:news-html-table', 'web_fetch:vercel-agent-permission-scopes'],
    'raw_dir': 'scout-raw',
    'corpus': 'graphify-out/raw/scout-2026-10-28-corpus.md',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'advisory_count': adv_count,
    'news_count': news_count + hn_count,
    'next_window': '2026-10-29T00:30+08:00',
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count,
      'commits', com_count, 'advisories', adv_count, 'news', news_count + hn_count)
