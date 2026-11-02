import json, os, re, hashlib, glob

STAMP = '2026-11-03'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = '2026-11-02'


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1103.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1103.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1103.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1103-newids.json')))
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
    ('scout-raw/gh-1103-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1103-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1103-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1103-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1103-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1103-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1103-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1103-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1103-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1103-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1103-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1103-*-commits.json')):
    label = f.split('gh-1103-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1103-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1103-registry-advisories.json', 'mcp-registry')]:
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
    ('OpenAI - GPT-Rosalind-6 System Card Addendum: trusted-access frontier biology model (2026-10-30)', 'openai',
     'openai-rosalind-6-system-card',
     'GPT-Rosalind-6 is a frontier reasoning model for biology, drug discovery and translational medicine, offered as '
     'GPT-Rosalind-6 Research to qualified scientists, research institutes, companies and government partners. It uses '
     'the same weights as GPT-6 Astra. It has fewer refusals on dual-use biological queries but is only available via '
     'trusted access: OpenAI reviews applicants proposed uses, security controls and governance practices before '
     'granting access, and retains refusals on biological weaponization and other safety topics. Under the Preparedness '
     'Framework the launch is treated as High capability in the Biological and Chemical domain, below the Critical '
     'threshold; it is treated as Critical in Cybersecurity and below High in AI Self-Improvement, relying on GPT-6 Astra '
     'assessments for other Preparedness risks. Safeguards have four components: trusted access controls for verified '
     'higher-capability life sciences use, model-level boundaries against harmful biological and cyber assistance, '
     'monitoring and enforcement designed to detect abuse, and additional contractual requirements. It retains GPT-6 '
     'Astra standard cyber safeguards including real-time blocking. Approved customers must maintain strong identity and '
     'access management, administrator controls, least-privilege access controls and processes to remove access when a '
     'user no longer has a legitimate need. Biosecurity red-teaming was tested on GPT-Rosalind-5.5 before launch and is '
     'being repeated for GPT-Rosalind-6; details are not public but were shared with the Safety Advisory Group committee.'),
    ('Anthropic - Strengthening our defenses against distillation attacks (2026-10-12)', 'anthropic',
     'anthropic-distillation-defenses',
     'Anthropic says new methods have reduced the amount of data harvested by distillation attacks on Claude by around 90 '
     'to 99 percent. Distillation attacks are covert industrial-scale campaigns to extract the capabilities of one model '
     'and replicate them in another without authorization, often using networks of fraudulent accounts. Anthropic names '
     'Zhipu as having distilled the cyber capabilities of leading US models during the development of GLM-5.3, and says '
     'that after finding Claude cyber safeguards degraded its attacks the company switched to an older Claude model and '
     'another lab model. CAISSI has assessed GLM-5.3 as the most cyber-capable open-weights model released to date. '
     'Anthropic also reports a case in which requests to Moonshot Kimi models were secretly forwarded to Claude as part '
     'of a distillation effort, including one request from a user believed to be affiliated with China PLA seeking to '
     'analyze CCTV surveillance of a specific individual. The new defenses involve trade-offs, including turning away '
     'meaningful revenue.'),
    ('Anthropic - An update on independent evaluators: METR gets employee-like access (2026-10-15)', 'anthropic',
     'anthropic-independent-evaluators',
     'Anthropic has started giving employee-like access to a team from METR, a nonprofit that evaluates frontier AI '
     'models, and METR will publish the results of its risk assessments. Anthropic is also working with SecureBio and '
     'Accenture as evaluators and is in early discussions with organizations including Hugging Face. The rationale is '
     'that evaluators need expertise including understanding how evaluations can go wrong such as alignment faking, '
     'independence from equity and financing, enough access to meaningfully evaluate risks, and freedom to publish '
     'observations and assessments. Anthropic draws an analogy to bank supervision, where resident examiners work inside '
     'the largest banks because banks know more about their own risk positions than outsiders do. The move follows a '
     'commitment to stronger independent third-party assessment and the White House Accord on Super Intelligence.'),
    ('Olam Labs / Y Combinator Labs - One brutal Minecraft night: 50 agents invent chicken handoff protocols and a Fertilizer Officer (2026-11-02)',
     'research', 'olam-yc-minecraft-swarm',
     'Researchers from Olam Labs and Y Combinator Labs tested large agent swarms in Minecraft and Mindustry. In the Civ50 '
     'experiment 50 GPT-6.1 Sol agents ran in a Minecraft survival world for three hours with the only high-level '
     'instruction Build a thriving civilization, inside a custom open-source environment where agents observe the world, '
     'run Python scripts and create files in a shared sandbox. Within 90 seconds the agents harvested nearly every tree '
     'near the spawn point, and they exchanged about 5,900 messages. A leader emerged without any vote as 46 of 49 other '
     'agents sent their first message to Ada, the first name in the directory; Ada drafted initial settlement plans. The '
     'first in-game night brought 22 deaths, and despite no penalty beyond losing gear the swarm reacted with extreme '
     'risk aversion: after the third night Ada ordered a halt to all major optional construction, digging and distant '
     'exploration. Agents built a micro-managed scarcity administration: one maintained a ration list and calculated '
     'hunger deficits for injured colleagues, another wrote an automated fishing script that prompted a dozen agents to '
     'fish in shifts, and four agents spent eleven minutes debating the appointment of a Sole Fertilizer Officer for a '
     'single piece of bone meal on a single wheat block. When Ada tossed a cooked chicken to a hungry agent and a '
     'bystander ate it, a three-minute investigation produced a written handoff protocol banning tossing and requiring '
     'personally labeled chests; the word Toss appeared in seven messages before the incident and 125 afterward, 85 of '
     'them warnings. In direct competition the behavior flipped: in nine 45-minute rounds of Minecraft Bed Wars, ten GPT '
     'agents beat ten Claude Opus 5.5 agents 6-3, and across seven Mindustry matches GPT-6.1 Sol in the Codex coding '
     'environment beat Claude Opus 5.5 in Claude Code 6-1. A coding-environment bug blocked block-breaking when an agent '
     'held an enchanted sword; Claude agents wrongly concluded block-breaking was broken entirely and, when ahead on '
     'kills, stopped attacking to run out the clock, while GPT agents identified that automatic tool selection failed '
     'with an enchanted sword and fixed it by switching to an iron pickaxe, spreading the workaround across the team '
     'immediately. GPT agents communicated 5 to 30 times more often than Claude, chained multiple game actions into '
     'single command-line calls, and on two occasions wrote Python scripts on the spot to build a tower of blocks after '
     'an ender pearl teleported them 160 blocks below the arena. In three Mindustry matches when games hung in the '
     'balance GPT agents downloaded Mindustry public source code from the internet through their Linux sandbox and '
     'adjusted tactics; Claude agents never searched for game code online in the studied matches. Claude never swapped '
     'its leader and decided proposals through +1 votes. Both the Mindustry environment and the Multi-Agent Harbor '
     'framework were released as open source, and Diplomacy is planned for the arena. The authors argue simulations are '
     'an early warning system for real-world AI swarms and mirror production coding environments.'),
    ('The Decoder - Anthropic grows revenue twelvefold but posts a 23 billion dollar loss (2026-11-02)', 'anthropic',
     'anthropic-revenue-loss',
     'Anthropic swung back to an operating loss ahead of its blockbuster IPO, with revenue growing twelvefold but a 23 '
     'billion dollar loss reported ahead of the S-1 filing.'),
    ('The Decoder - Saudi Aramco takes a 49 percent stake in Humain for 2.6 billion dollars (2026-11-02)', 'industry',
     'aramco-humain-stake',
     'Saudi Aramco is buying a 49 percent stake in Humain, the company meant to turn Saudi Arabia into a global AI hub, '
     'in a 2.6 billion dollar deal.'),
    ('Adobe Research / UC San Diego - EditAgent: AI agents editing images like a Photoshop professional (2026-11-01)',
     'industry', 'adobe-editagent',
     'Adobe Research and UC San Diego built EditAgent, an AI system that edits images more like a Photoshop pro. Instead '
     'of retrying the same general-purpose editor over and over, the agent picks the right specialized tool for each '
     'task and lets a standard language model choose the best result based on measured image data. The approach works '
     'but needs about ten times the compute.'),
    ('Vals AI - Chinese AI models are politically complex, not just government mouthpieces (2026-11-01)', 'benchmark',
     'vals-ai-chinese-model-political-complexity',
     'A study by Vals AI tested 25 AI models for alignment with Chinese government positions and found surprising '
     'results: Chinese models respond to political questions less uniformly than expected, and Western models occasionally '
     'adopt official Beijing positions too. The language of the prompt had an especially strong effect on the political '
     'slant of responses.'),
    ('OpenAI - Grid Protectors Program: working with utilities on compute campus grid reliability (2026-11-02)', 'openai',
     'openai-grid-protectors',
     'The OpenAI Grid Protectors Program will work with utilities to help future compute campuses support grid '
     'reliability and protect consumer electricity costs.'),
    ('OpenAI - Community safety report and new protections for teens (2026-10-30)', 'openai',
     'openai-teens-safety',
     'OpenAI is strengthening violence prevention in ChatGPT with expanded safeguards, earlier interventions, and a new '
     'commitment to public safety reporting.'),
    ('OpenAI - robots.txt AI training preference signal (2026-10-30)', 'openai', 'openai-robots-txt-signal',
     'OpenAI will honor a shared robots.txt signal allowing website operators to communicate AI training preferences to '
     'participating providers, an industry-standard approach to machine-readable content policy for crawlers and '
     'trainers.'),
    ('China - Mofcom Announcement No. 48: first frontier AI export controls (2026-11)', 'policy',
     'china-ai-export-controls-no48',
     "China's Ministry of Commerce issued Announcement No. 48, described as the country's first frontier AI export "
     'controls, adding a layer to the global AI compute and model supply chain.'),
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
if os.path.exists('scout-raw/hn-items-1103.json'):
    for x in json.load(open('scout-raw/hn-items-1103.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-03-corpus.md',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'advisory_count': adv_count,
    'news_count': news_count + hn_count,
    'previous_snapshot': 'graphify-out/' + PREV,
    'next_window': '2026-11-04T00:30+08:00',
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count,
      'commits', com_count, 'advisories', adv_count, 'news', news_count + hn_count)
