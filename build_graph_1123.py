import json, os, re, hashlib, glob

STAMP = '2026-11-23'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = "2026-11-22"


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1123.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1123.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1123.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1123-newids.json')))
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
    ('scout-raw/gh-1123-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1123-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1123-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1123-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1123-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1123-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1123-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1123-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1123-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1123-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1123-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1123-*-commits.json')):
    label = f.split('gh-1123-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1123-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1123-registry-advisories.json', 'mcp-registry')]:
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
    ('The Decoder - AI coding agents ace isolated tests but complete fewer than one in ten tasks in a simulated workplace (2026-11-22)',
     'research', 'ai-coding-agents-fewer-than-one-in-ten-tasks-simulated-company',
     'A new real-world test puts AI coding agents in a simulated developer job with colleagues, project boards, and incomplete handoffs, where they have to keep developing software on their own and reliably close open tickets in a messy daily workflow. Even Opus 5.5 and Astra fall far short, solving fewer than one in ten tasks completely. The models finish clear, standalone assignments quickly, but they lose track as autonomous developers. The framing matters for this series because SWE-bench is nearly saturated and Anthropic claims Claude writes more than 80 percent of production code, while this benchmark shows that isolated test-passing does not transfer to closing open tickets in a messy workflow. The measurement gap between a benchmark task and a workplace task is where agent evaluation has actually moved.',
     ),
    ('The Decoder - Perplexity Monitor API turns web search from a one-off query into a nonstop watchdog (2026-11-22)',
     'industry', 'perplexity-monitor-api-scheduled-search-webhook-agents',
     'Perplexity launched a Monitor API that searches the web on a schedule and alerts agents via webhook only when relevant changes occur. Its own decision model filters out unimportant results. Two modes: web monitors run a search query on a schedule against a developer-defined goal, and page monitors track up to ten pages such as pricing pages, changelogs, or policies, storing a baseline on first run and returning a text diff of changes. Results are scored on relevance, source credibility, novelty, and timeliness, and an update with a confidence score is only sent when every threshold is met; thresholds and the goal can be changed without recreating the monitor. Schedules run from every 15 minutes to weekly or on a custom cron. Webhooks are signed and delivery is retried after temporary errors. Pricing is 1 dollar per 1000 requests, and Perplexity says internal tests put it ahead of Firecrawl and Exa. For Perplexity the API is a way to stand out from an increasingly interchangeable chatbot business through developer tools.',
     ),
    ('OpenAI - Perplexity and Intelligence, by Jakub Pachocki, Chief Scientist (2026-11-22)',
     'research', 'openai-perplexity-shared-metric-pacing-0-68-0-70-window',
     'OpenAI chief scientist Jakub Pachocki argues for establishing perplexity, equivalently cross-entropy loss, as a metric to compare model developers and to inform shared safety standards, and publishes OpenAI internal perplexity measurements as a first step. The reported log-perplexity trajectory is given as about 0.99 for GPT-3.5, about 0.91 for GPT-4, below 0.8 as transformative capabilities in cybersecurity and mathematics emerged, and about 0.76 when the models started producing groundbreaking mathematical results. Pachocki argues the emergence of those capabilities was not clear in advance and should be seen as latent capabilities emerging from progress on one metric, and he contrasts the usual recursive-self-improvement framing with a specific step change in algorithmic research on pretraining, estimating that as early as 2027 an avalanche of fundamental pretraining advancements is conceivable. He expects further transformative capabilities in the roughly 0.68 to 0.7 log-perplexity window, and expects further degradation in dominant forms of alignment auditing plus more evaluation and training awareness. He proposes common limits based on perplexity that frontier developers commit not to cross until understanding and monitoring reach a concrete milestone such as a successor to chain-of-thought monitors. Named challenges: difficulty of comparison across labs, detachment from actionable evaluations, not accounting for advances outside pretraining such as chain-of-thought reasoning, and an unknown loss floor set by the entropy of the data.',
     ),
    ('The Decoder - Anthropic says one AI agent beats many subagents now that models can handle complexity alone (2026-10-25)',
     'research', 'anthropic-single-agent-beats-multi-agent-subagents-migration-kit',
     'Anthropic found that a single agent with on-demand context often outperforms multi-agent setups in quality, cost, and latency, and is releasing a migration kit to help teams evaluate and make the switch. The company recommends that companies evaluate whether they can consolidate sub-agents, because a single primary agent that loads context as needed often delivers better results than a fleet of specialized ones. Newer models starting with Opus 4.5, along with Opus 5.5 and Fable 5.1, can manage complex plans directly in a single loop, which also reduces cost and wait time, and in one architecture comparison the single-agent setup ran about twice as fast as the multi-agent setup. This directly qualifies the subagent-heavy orchestration pattern tracked in earlier windows of this series.',
     ),
    ('The Decoder - Anthropic says the key to agent memory is knowing what to forget, not how much to store (2026-11-16)',
     'research', 'anthropic-memory-selective-notes-dreaming-forget-pokemon',
     'Anthropic studied how Claude retains knowledge across sessions with the model unchanged: Claude writes notes to a folder it can read back later, and the core problem is selection, because before it knows what comes next the agent must decide in the moment what might matter later, so every note is a bet on the future. In a Pokemon Red test the older Claude Sonnet 3.7 treated everything as potentially important and, across roughly 10,000 game steps, created 413 files in 225 folders, often one per battle and item; because the game state keeps changing the archive went stale fast, and at times the model did nothing but reorganize its notes instead of playing, finishing with a single badge. The newer Claude Fable 5 limited its memory to a few files and earned four badges, not recording information already visible on screen and instead writing down plans, strategies, and rules it had tested. A post-session process called Dreaming analyzes earlier session transcripts during idle periods to independently correct faulty notes and build structured knowledge collections. Anthropic notes the comparison covers only a single playthrough per model.',
     ),
    ('The Decoder - AI industry growth remains strong, but the pace is slowing (2026-11-19)',
     'industry', 'ramp-ai-index-token-prices-down-21pct-six-weeks-volume-record',
     'The latest update of the Ramp AI Index, drawing on transaction data from more than 85,000 US companies, shows token prices fell 21.2 percent in six weeks while token volume rose 1.5 percent to a record high. Anthropic dominates with nearly 59 percent of token spending. Data from Ramp, Stripe, and OpenRouter independently show the same pattern: the AI industry is still growing, but revenue momentum is cooling. This is the third quantitative sample in this series of the cost-per-computed-unit curve, and it sits alongside the previous window finding of a 62 percent drop in cost per verified task for Qwen4-Max.',
     ),
    ('The Decoder - Anthropic Claude Fable 5.2 paints images with code instead of generating them (2026-11-15)',
     'research', 'claude-fable-5-2-paints-with-code-700k-strokes',
     'Anthropic Claude Fable 5.2 does not generate images the way other AI models do. Instead of computing pixels, the language model writes Python code that places hundreds of thousands of simulated brushstrokes on a virtual canvas, complete with bristle texture and how the paint goes on, including mistakes it then has to paint over. Current image models like Midjourney typically use diffusion, which gradually refines a noisy image into a clear result, while Fable 5.2 simulates the physical painting process. A single photorealistic parking garage scene took roughly 700,000 strokes, according to Anthropic employee Jake Eaton. The architectural point for agents is that generation is delegated to a program the model writes, which is the same delegation pattern used for tool use and for the looped-transformer inference axis tracked in the previous window.',
     ),
    ('Open Social Web Alliance - an ActivityPub-style open social protocol policy page (2026-11-22)',
     'industry', 'open-social-web-alliance-activitypub-open-protocol',
     'The Open Social Web Alliance publishes a policy paper for a shared, standardised communication protocol on the model of email: one account, own posts and content, own choices, and freedom to connect across networks regardless of host. The stated vision is a year in which more than 100 million people connect through open social networks with no platform economy, built on ActivityPub and related open standards, with users deciding which content, algorithms, and applications to use. The alliance frames the goal as building social media that strengthens democratic discourse while being resilient and appealing. It surfaced on HackerNews with 108 points and 95 comments, and its presence in this window is a second instance of the same pattern seen with MCP: an incumbent closed protocol facing an open-protocol alternative that claims the same capability set with a federated identity layer.',
     ),
    ('GitHub - gulivan/worker755: a game where you are an LLM subagent (2026-11-22)',
     'research', 'show-hn-game-where-you-are-an-llm-subagent',
     'A Show HN project that turns the agent subagent concept into a game: the player operates as a subagent of an LLM, receiving instructions from a parent agent and executing delegated tasks. It reached 135 points and 34 comments on HackerNews in this window. The signal is cultural rather than technical, but it is consistent with Anthropic guidance in the same window that a single agent with on-demand context often beats a fleet of specialized subagents: the multi-agent shape has become a mainstream metaphor, which usually precedes its simplification.',
     ),
    ('Better Data Center Project - Anthropic power footprint 87 percent gas, 11 percent coal in 2028 (2026-11-16)',
     'industry', 'anthropic-power-87pct-gas-11pct-coal-32mt-co2-2028-byop',
     'The Better Data Center Project analyzed Anthropic compute commitments as a case study of how the AI buildout drives both new bring-your-own-power and grid fossil infrastructure. Across the industry they identified 177 GW of planned BYOP gas capacity, enough to power 65 percent of all US homes, with less than 20 percent of generation from renewables by 2032, and another 200 GW of new fossil plants on the grid largely to meet AI data center demand. Anthropic has made no direct US renewable energy commitments as of November 2026, its only publicly disclosed renewable commitments being in Norway and Canada, while it directly procured 1.7 gigawatts of heavy-duty gas generators for 3.4 billion dollars. They estimate about 87 percent of Anthropic power will come from gas and 11 percent from coal in 2028, with the company potentially emitting 32 million metric tons of carbon dioxide in 2028. The compute constraint that dominates agent economics is therefore not token price but electrons and gas turbines, and this window confirms the token-price side of the curve by showing a 21 percent six-week drop.',
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
if os.path.exists('scout-raw/hn-items-1123.json'):
    for x in json.load(open('scout-raw/hn-items-1123.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-23-corpus.md',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'advisory_count': adv_count,
    'news_count': news_count + hn_count,
    'previous_snapshot': 'graphify-out/' + PREV,
    'next_window': '2026-11-23T00:30+08:00',
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count,
      'commits', com_count, 'advisories', adv_count, 'news', news_count + hn_count)
