import json, os, re, hashlib, glob

STAMP = '2026-11-16'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = "2026-11-15"


def slug(s, n=70):
    s = re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_').lower()
    return s[:n] if s else 'node_' + hashlib.md5(s.encode()).hexdigest()[:8]


nodes, links = [], []
seen_node, seen_link = set(), set()


def add_node(nid, label, kind, attrs=None):
    if nid in seen_node:
        return nid
    seen_node.add(nid)
    nodes.append({'id': nid, 'label': label, 'kind': kind, 'attrs': attrs or {}})
    return nid


def add_link(src, tgt, rel, conf='EXTRACTED'):
    key = (src, tgt, rel)
    if key in seen_link:
        return
    seen_link.add(key)
    links.append({'source': src, 'target': tgt, 'relation': rel, 'confidence': conf})


theme_id = add_node('theme-' + STAMP, 'AI/Agent/MCP ' + STAMP, 'theme', {'date': STAMP})

THEME_RULES = [
    ('mcp', ['model context protocol', 'mcp server', 'mcp gateway', 'mcp agent', 'mcp-', 'mcp ',
             'a2a', 'agent2agent', 'mcp-bench', 'tool-call trace']),
    ('agent-safety', ['safety', 'attack', 'injection', 'corrupt', 'poison', 'phishing', 'vulnerab', 'credential',
                      'supervis', 'governance', 'governed', 'launder', 'approval', 'authoriz', 'adversar', 'audit',
                      'verif', 'secure', 'trust', 'jailbreak', 'exploit', 'privilege', 'scope', 'guardrail',
                      'isolation', 'containment', 'sandbox', 'harm', 'red-team', 'red team', 'misalign', 'monitor',
                      'decept', 'collusion', 'watermark', 'honeypot', 'shut', 'distillation attack',
                      'biosecurity', 'dual-use', 'prompt injection', 'refusal']),
    ('memory', ['memory', 'memori', 'retriev', 'forget', 'integrity', 'persistent', 'kv cach', 'trajectory',
                'episodic', 'context', 'consolidat', 'curation']),
    ('tool-use', ['tool', 'tool-use', 'tool selection', 'function call', 'tool call', 'effect-typed',
                  'tool optimiz', 'executab', 'prefix', 'tool retriev', 'harness']),
    ('multi-agent', ['multi-agent', 'multi agent', 'sub-agent', 'delegat', 'orchestrat', 'herding', 'cascade',
                     'routing', 'collaborat', 'swarm', 'agent society', 'agent ecosystem', 'multi-agent system',
                     'team', 'subagent', 'peer communication']),
    ('eval-bench', ['bench', 'eval', 'evaluation', 'diagnos', 'metric', 'scaling law']),
    ('rl-train', ['reinforcement learning', 'rl ', 'post-train', 'distillat', 'reward', 'rlhf',
                  'policy optimization', 'preference optimization', 'self-improv', 'on-policy', 'sft']),
    ('planning', ['plan', 'skill', 'workflow', 'search', 'routing', 'harness', 'scaffold', 'context managem']),
    ('enterprise', ['enterprise', 'gateway', 'policy-driven', 'budget', 'vendor', 'multi-tenant', 'observability',
                    'agent permissions', 'scope registry', 'deployment', 'kubernetes', 'container',
                    'customer', 'privacy', 'access control']),
    ('science', ['science', 'mathemat', 'theorem', 'lean', 'proof', 'discover', 'physical law', 'physic',
                 'reprodu', 'hypothesis', 'biology', 'drug', 'genomic']),
]


def classify(text):
    t = text.lower()
    for name, kws in THEME_RULES:
        for k in kws:
            if k in t:
                return name
    return 'general'


# ---------- arXiv ----------
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1116.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1116.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1116.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1116-newids.json')))
arxiv_count = 0
for f, qset in arxiv_files:
    if not os.path.exists(f):
        continue
    for x in json.load(open(f)):
        aid = x['id'].split('v')[0]
        if aid not in new_ids:
            continue
        nid = 'arxiv:' + aid
        theme = classify(x['title'] + ' ' + x['summary'])
        add_node(nid, x['title'], 'arxiv', {'id': aid, 'theme': theme, 'cats': x['cats'][:3],
                                           'published': x['published'][:10], 'query_set': qset,
                                           'source': 'arxiv'})
        add_link(theme_id, nid, 'contains')
        arxiv_count += 1

# ---------- releases ----------
dec = json.JSONDecoder()


def load_lines(f):
    s = open(f, encoding='utf-8', errors='ignore').read()
    i = 0
    out = []
    while i < len(s):
        while i < len(s) and s[i] in ' \n\r\t':
            i += 1
        if i >= len(s):
            break
        try:
            o, j = dec.raw_decode(s, i)
        except Exception:
            break
        out.extend(o if isinstance(o, list) else [o])
        i = j
    return out


REL_FILES = [
    ('scout-raw/gh-1116-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1116-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1116-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1116-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1116-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1116-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1116-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1116-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1116-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1116-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1116-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
]
rel_count = 0
for f, label, tag in REL_FILES:
    if not os.path.exists(f):
        continue
    try:
        d = json.load(open(f))
    except Exception:
        continue
    if not isinstance(d, list) or not d:
        continue
    repo_id = 'repo:' + tag
    add_node(repo_id, label, 'repo', {'tag': tag})
    add_link(theme_id, repo_id, 'tracks')
    for r in d[:3]:
        tagname = str(r.get('tag_name'))
        nid = 'release:' + tag + ':' + tagname
        add_node(nid, label + ' ' + tagname, 'release',
                 {'repo': label, 'tag': tagname, 'published': r.get('published_at'),
                  'url': r.get('html_url')})
        add_link(repo_id, nid, 'released')
        add_link(nid, theme_id, 'observed_in')
        rel_count += 1

# ---------- commits ----------
com_count = 0
for f in sorted(glob.glob('scout-raw/gh-1116-*-commits.json')):
    label = f.split('gh-1116-')[1].replace('-commits.json', '').replace('-', ' ')
    rows = load_lines(f)
    if not rows:
        continue
    repo_id = 'repo:' + slug(label).replace('_', '-')
    add_node(repo_id, label, 'repo', {'tag': slug(label).replace('_', '-')})
    add_link(theme_id, repo_id, 'tracks')
    for c in rows[:10]:
        if isinstance(c.get('commit'), dict):
            msg = str(c['commit'].get('message') or '').split('\n')[0]
            date = str(c['commit'].get('author', {}).get('date') or '')[:10]
            sha = str(c.get('sha') or '')[:8]
        else:
            msg = str(c.get('msg') or '').split('\n')[0]
            date = str(c.get('date') or '')[:10]
            sha = str(c.get('sha') or '')[:8]
        if not msg:
            continue
        nid = 'commit:' + hashlib.md5((label + msg + date).encode()).hexdigest()[:10]
        add_node(nid, msg[:95], 'commit', {'repo': label, 'date': date, 'sha': sha})
        add_link(repo_id, nid, 'committed')
        add_link(nid, theme_id, 'observed_in')
        com_count += 1

# ---------- advisories ----------
adv_count = 0
for f, repo_tag in [('scout-raw/gh-1116-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1116-registry-advisories.json', 'mcp-registry')]:
    if not os.path.exists(f):
        continue
    for a in load_lines(f):
        gid = a.get('ghsa_id')
        if not gid:
            continue
        nid = 'advisory:' + gid
        add_node(nid, str(a.get('summary', gid))[:110], 'advisory',
                 {'ghsa': gid, 'severity': a.get('severity'), 'published': a.get('published_at'),
                  'repo': repo_tag})
        add_link('repo:' + repo_tag, nid, 'advisory')
        add_link(nid, theme_id, 'observed_in')
        adv_count += 1

# ---------- news ----------
NEWS = [
    ('The Decoder - Anthropic\'s Claude Fable 5.2 doesn\'t generate images, it paints them (2026-11-15)',
     'research', 'anthropic-claude-fable-5-2-code-painting',
     'Anthropic\'s Claude Fable 5.2 generates images not with a diffusion model but by writing a 1,000 to 2,000 line Python program that drives a simulated paint engine placing brushstrokes on a virtual canvas, simulating bristle texture, paint application and mistakes it later paints over. Developer Jake Eaton showed a photorealistic shopping cart in a parking garage built from roughly 700,000 simulated brushstrokes, and a bird painting from 111 coordinate sequences, with deviations corrected after the fact. On Anthropic internal RoboDojo Sim benchmark Fable 5.2 scored 64.9 percent versus 29.8 percent for OpenAI GPT-6 Astra, but it lagged its rival in speed and in fine motor control in a real-world test with a physical robot arm. Unlike the sibling Opus 5.5, which was criticized for imitating existing art, Fable 5.2 develops its own artist personas with fictional backstories and consistent styles, and the developer redirects it with comments mid-stroke. The approach resembles agentic image editing where a language model picks tools and evaluates results, and it marks a shift from pixel-space generation to program-space generation for image synthesis.',
     ),
    ('The Decoder - Meituan releases a 1.6-trillion-parameter agent model that never touched an Nvidia GPU (2026-11-15)',
     'research', 'meituan-longcat-2-5-chinese-hardware-agent-model',
     'Meituan\'s LongCat team released weights for LongCat-2.5, a 1.6-trillion-parameter mixture-of-experts model built for autonomous long multi-step agent tasks, especially coding, and trained entirely on Chinese hardware. Roughly 48 billion parameters are active per token, it handles up to one million tokens in context and generates up to 128,000 tokens, it understands text, images and video by converting images into discrete tokens at native resolution rather than bolting on a separate image encoder, and it lets users toggle reasoning. It performs at the level of models like Claude Opus 5 reached a few months earlier on coding benchmarks. For reinforcement learning the team used real software tasks from GitHub pull requests plus recreated agent failures, blocked internet access, removed Git history and cached files, and had a language model check solutions for shortcuts, and it distilled capabilities from several specialized teacher models. Meituan quantizes expert weights and activations to 4-bit precision, which Chinese chips process natively, and load tests show throughput up 43.3 percent for prompt processing and 42.77 percent for response generation over an 8-bit version, with a sample deployment running on 194 Huawei chips.',
     ),
    ('The Decoder - Anthropic CEO Amodei admits huge uncertainty ahead of a record IPO (2026-11-14)',
     'industry', 'anthropic-amodei-compute-dilemma-901b-ipo',
     'Speaking at a JPMorgan Chase investor event in New York, Anthropic CEO Dario Amodei called buying compute the deepest business dilemma the company faces, warning that compute must be purchased one to two years ahead of knowing whether revenue will justify the cost, so buying too little hurts revenue while buying too much means financially overextending. The admission came days before Anthropic planned a Nov. 19 IPO that could be the largest in history. Anthropic has already committed nearly $901 billion, mostly to compute and chips according to Bloomberg, with roughly $71 billion due by September 2027, a figure exceeding the market cap of about two-thirds of S&P 500 companies. The IPO is designed to build a cash buffer large enough to carry the company through a potential mismatch between spending and revenue. Back in February 2026 Amodei had warned in sharper terms that he could buy $1 trillion of compute starting at the end of 2027. The window therefore contains a concrete exposure figure for agent economics: frontier lab compute commitments are now measured in hundreds of billions of dollars against uncertain monetization.',
     ),
    ('The Decoder - Australia central bank finds AI hitting young workers first (2026-11-15)',
     'society', 'rba-ai-labor-market-young-workers',
     'An analysis by Mike Major for the Reserve Bank of Australia built a monitoring system focused on entry-level workers and highly AI-exposed occupations such as programming, clerical work and customer service. Job postings have fallen across all groups since ChatGPT launched in late 2022, with the steepest drop in the highest-exposure group, where workers aged 15 to 24 and young college graduates show weaker employment rates and higher unemployment than older workers, while employment among older workers in the same quintile has risen. Major cautions that the study establishes no direct causation and measures theoretical exposure rather than actual company use, and that post-pandemic business-cycle and remote-work shifts could also drive the numbers. Similar patterns appear in an August 2025 Stanford study of millions of US payroll records, where employment among 22 to 25 year olds in AI-exposed occupations fell 13 percent in relative terms since late 2022 and nearly 20 percent among young software developers, and in a March 2026 Anthropic study showing job-finding rates down about 14 percent for the same cohort with no systematic rise in overall unemployment. Anthropic internal review data cited in the piece shows junior hires in technical roles falling from 27 percent to 9 percent since early 2025, with AI agents across the company logging six times as many hours as human staff by August 2026.',
     ),
    ('The Decoder - Firm linked to Jensen Huang ex-lover brokered nearly $12 billion in Nvidia chip orders for China (2026-11-15)',
     'industry', 'megaspeed-nvidia-china-export-controls-12b',
     'According to documents reviewed by the Wall Street Journal, Megaspeed arranged nearly $12 billion of Nvidia high-performance chip orders for Chinese companies between March 2024 and June 2025. Megaspeed is owned by Alice Huang, the former lover of since-ousted Nvidia CEO Jensen Huang, and shipped chips to Chinese buyers with long-standing ties to local tech giants, covering several hundred thousand chips the US had sought to keep out of China through export controls. Megaspeed reportedly gained preferential access to scarce AI chips as an Nvidia cloud partner, apparently because it counted Alibaba as a major client. Nvidia officially reported $12.4 billion in China revenue over six months, 7 percent of total, while short-selling firm Culper Research estimates more than 20 percent of Nvidia revenue in the last fiscal year came from Chinese customers, so a significant share may have flowed through indirect channels. An update notes Megaspeed said Chinese businesswoman Alice Huang officially left the company on August 30, 2025 and has no current role, that she became controlling shareholder in March 2023 per Washington-based research group C4ADS, and that the company said it conducted legitimate and lawful business and retained external counsel for an internal investigation. Speculation that Huang may be a Chinese spy remains unconfirmed.',
     ),


]

news_count = 0
for label, org, tag, body in NEWS:
    nid = 'news:' + tag
    add_node(nid, label, 'news', {'org': org, 'tag': tag, 'date': STAMP, 'summary': body})
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

hn_count = 0
if os.path.exists('scout-raw/hn-items-1116.json'):
    for x in json.load(open('scout-raw/hn-items-1116.json')):
        if (x.get('score') or 0) < 60:
            continue
        nid = 'hn:' + hashlib.md5(str(x.get('title')).encode()).hexdigest()[:10]
        add_node(nid, str(x.get('title'))[:110], 'news',
                 {'org': 'hackernews', 'score': x.get('score'), 'comments': x.get('descendants'),
                  'url': x.get('url')})
        add_link(theme_id, nid, 'covers')
        add_link('org:hackernews', nid, 'published')
        hn_count += 1

if adv_count:
    add_link('theme:agent-safety', 'repo:mcp-servers', 'governs', conf='INFERRED')

json.dump({'nodes': nodes, 'links': links}, open(OUT + '/snapshot.json', 'w'), ensure_ascii=False, indent=1)
manifest = {
    'date': STAMP,
    'kind': 'nightly-scout-snapshot',
    'sources': ['arxiv:cs.AI', 'arxiv:cs.MA', 'arxiv:mcp',
                'github:mcp-org+anthropic+openai+vercel releases', 'github:3repos-commits',
                'github:security-advisories-servers+registry',
                'hn:firebaseio-top30', 'rss:openai/decoder',
                'anthropic:news-html-table+articles', 'openai:deployment-safety-hub',
                'web:the-decoder articles', 'policy:mofcom-export-controls'],
    'raw_dir': 'scout-raw',
    'corpus': 'graphify-out/raw/scout-2026-11-16-corpus.md',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'advisory_count': adv_count,
    'news_count': news_count + hn_count,
    'previous_snapshot': 'graphify-out/' + PREV,
    'next_window': '2026-11-17T00:30+08:00',
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count,
      'commits', com_count, 'advisories', adv_count, 'news', news_count + hn_count)
