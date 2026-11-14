import json, os, re, hashlib, glob

STAMP = '2026-11-07'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = '2026-11-06'


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1107.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1107.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1107.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1107-newids.json')))
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
    ('scout-raw/gh-1107-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1107-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1107-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1107-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1107-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1107-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1107-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1107-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1107-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1107-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1107-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1107-*-commits.json')):
    label = f.split('gh-1107-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1107-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1107-registry-advisories.json', 'mcp-registry')]:
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
    ('METR - Anthropic may have crossed its own AI acceleration warning threshold back in July (2026-11-06)',
     'research', 'metr-anthropic-acceleration-audit',
     'METR got eleven weeks of access to Anthropic internal research data and found that the rate at which Anthropic models improve has roughly doubled, with about 80 percent of that acceleration tracing back to AI being used in the company own research. Anthropic redacted the most important evidence, and whether AI is speeding up development of better AI is a key early warning signal in the safety debate, because a feedback loop could form where models improve their successors faster and faster and lead, per METR, to a sudden emergence of extreme and risky capabilities. Anthropic Responsible Scaling Policy flags exactly this as a risk indicator: if the pace of AI progress doubles because of automated AI research that should trigger a warning level. From August 12 to October 29, 2026, a team of 2.5 full-time staffers received benchmark results from unreleased models, training metrics, employee surveys and internal analyses, plus roughly 15 interviews with Anthropic researchers, and METR took no money from Anthropic while working on Anthropic devices for security reasons. Since October 2025 Anthropic model test scores have climbed about 1.9 times faster than between March 2024 and October 2025 on the AECI composite metric, meaning Anthropic achieved in one year what previously took two, roughly comparable to the jump from Claude 2.1 to Sonnet 4.5. The rate rose from about 15 AECI points per year before October 2025 to 29 after, and three unreleased models trained between July and October 2026 were included. Anthropic had recently committed to bringing external auditors in and announced a METR collaboration involving employee-like access in October, while the audit itself is a separate narrower project.'),
    ('Anthropic - $1.5 trillion IPO hits resistance as investors balk at valuation (2026-11-06)',
     'anthropic', 'anthropic-ipo-valuation-resistance',
     'Anthropic IPO is in trouble as investors push back on the $1.5 trillion valuation and the tech market sells off, according to Reuters, with potential backers doubting the planned roadshow can kick off next week as scheduled. As recently as September the company was eyeing a valuation of up to $2 trillion, and now some investors think even $1.5 trillion is too rich, one reportedly floating a valuation of just $1 trillion. Investors want a steeper discount because Anthropic is still losing money and burning through cash to scale AI infrastructure, and they are waiting on October revenue numbers that are missing from the updated S-1 filing. The midterm elections made things worse as ballot initiatives targeting data center expansion passed in several states, triggering the sharpest tech selloff in a year, and the Wall Street Journal also reports IPO investors are skeptical. If AI stocks stay under pressure Anthropic could delay the offering, which some estimates peg at up to $100 billion in size, and a delay could further shake confidence in the broader AI sector.'),
    ('Perplexity - Launches Teammates, an always-on AI agent that works around the clock (2026-11-06)',
     'industry', 'perplexity-teammates-always-on-agent',
     'Perplexity now has its own AI agent that runs around the clock and handles work tasks on its own. While Perplexity Computer executes one-off assignments, the new Teammates stay active and work through ongoing projects independently, with each Teammate running on its own virtual machine with a desktop and browser. Users track progress through dedicated threads in the Perplexity app and can interact with the agents via Slack. Perplexity joins SpaceX, Meta, OpenAI and Anthropic, which already offer similar agents through Grok Bots, Muse, Dots and Duet. Teammates require the Max plan at $200 per month, while Dots start at $100 and Duet is available from $20, and in practice the cheaper options will likely hit their usage limits fast, days after high agent consumption forced SpaceX to impose stricter usage caps on Grok Bots. Perplexity annualized revenue topped $750 million as of August.'),
    ('Thinking Machines - Inkling 2 Small claims top spot among western open-weight models (2026-11-06)',
     'industry', 'thinking-machines-inkling-2-small',
     'Thinking Machines, the startup from former OpenAI CTO Mira Murati, is releasing Inkling 2 Small, a mixture-of-experts model with 594 billion parameters of which 17 billion are active at any given time. On the Artificial Analysis Intelligence Index it scores 31, an 18 point jump over its predecessor Inkling Small which scored 13, and roughly on par with Google Gemini 3.8 Flash, with especially strong gains in agentic tasks. On AutomationBench-AA the score jumps from 5 to 46 percent and on FrontierCode 2.0 from 5 to 25 percent, and on the knowledge work benchmark AA-Briefcase it hits 1,527 Elo, 615 points above its predecessor. The improved performance comes at a price since the model generates more output tokens and costs six times as much per task as its predecessor. It accepts text and images and offers adjustable thinking depth to choose between speed and thoroughness, and Inkling models are designed as base models for fine-tuning. It is initially available as a proprietary offering through the Tinker platform, with weights under an Apache license to follow.'),
    ('Anthropic - Adds Personal Finance so users can connect bank accounts to Claude (2026-11-06)',
     'anthropic', 'anthropic-personal-finance-plaid',
     'Anthropic lets Claude users connect their bank accounts and ask questions about their money through a new feature called Personal Finance, which gives Claude read-only access and cannot move, manage or invest funds. The connection runs through Plaid so Claude never sees a bank password, and users can break down spending by category, check upcoming payments or ask things like whether they are spending more than they earn. The feature launches as a beta in the US for Pro, Max and Ultra subscribers, with Anthropic saying conversations in the Personal Finance section will not be used for model training, that users can disconnect at any time, and that it will not show ads or sponsored recommendations. Longer term Anthropic wants to connect Claude with licensed financial advisors and regulated firms, while OpenAI already offers a similar US feature called Finances.'),
    ('OpenAI - Unveils GPT-6 Cyber, a model trained to find, exploit and patch vulnerabilities (2026-11-05)',
     'openai', 'openai-gpt-6-cyber',
     'OpenAI introduced GPT-6 Cyber, a model trained specifically to hunt for security vulnerabilities, develop working exploits and suggest patches, and trained to stay within its assigned boundaries. Without any special safety instructions GPT-6 Cyber avoided boundary violations in 99.93 percent of cases, up from 94.49 percent for its predecessor, and with safety instructions enabled it stayed within bounds in 100 percent of tests, with a honeypot inspired by the Hugging Face incident used during training. OpenAI rates GPT-6 Cyber as Critical in the cybersecurity category of its own Preparedness Framework, the same rating given to GPT-6 Astra. On ExploitGym, a benchmark testing whether a model can exploit a given vulnerability in a remote system, it scores 48.5 percent versus 32.1 percent for predecessor GPT-5.6 Cyber, and on a new test for finding vulnerabilities in web apps without source code access OpenAI reports 40.3 percent versus 32.0 percent for GPT-6 Astra, with GPT-6 Astra with safeguards enabled scoring 0.0 percent. In targeted tests the model found 81 previously unknown critical vulnerabilities in Firefox which Mozilla has already patched, and in the Linux kernel it reproduced 1,724 vulnerabilities and developed working exploits for 948 of them, more than five times as many as its predecessor. All benchmark numbers come from OpenAI itself with no independent testing of the model.'),
    ('Google - Gemini Omni 1.2 Flash goes general availability with 15 second clips and 30 percent lower price (2026-11-05)',
     'industry', 'google-gemini-omni-1-2-flash',
     'Google DeepMind is making its Gemini Omni 1.2 Flash video generation model generally available. The updated model creates clips up to 15 seconds long, supports conversational editing and costs 30 percent less than its predecessor, rolling out through the Gemini API, Google AI Studio, Google Cloud Console, Flow, Google Vids, the Gemini app for AI Ultra subscribers and Google Ads. Every generated video carries an imperceptible SynthID watermark, clips now run between three and 15 seconds versus a previous maximum of 10, and pricing drops 30 percent to $0.07 per second for 720p video. Conversational Editing lets users tweak a clip step by step, changing background, lighting or aspect ratio without regenerating, and works across the full 15 second length, paired with a tiered workflow where drafts are made at 360p or 720p, details corrected with a follow-up edit, and only the final result upscaled to 1080p or 4K to cut cost. Google also promises better reference adherence, accepting character images, product photos, motion clips up to three seconds and audio cues as inputs, with faces, clothing, packaging typography and brand colors staying consistent across camera angles, and less visual drift or morphing across motion and transitions.'),
    ('Baidu - Releases ERNIE 5.5 Flash Base, a 280B MoE open foundation model without post-training (2026-11-05)',
     'industry', 'baidu-ernie-5-5-flash-base-280b',
     'Baidu released ERNIE-5.5-Flash-Base, an open foundation model that ships deliberately without fine-tuning or post-training, so developers decide where to take it, with a post-trained version supposed to follow. ERNIE 5.5 uses a mixture-of-experts architecture with 280 billion parameters of which 14 billion are active per input, was pre-trained on 33.5 trillion tokens with a training context up to 128,000 tokens, and is designed to support context up to one million tokens during fine-tuning and inference. Baidu reports the model competes with similarly sized open foundation models like DeepSeek V4 Flash, Hy3-preview-Base and MiMo V2.5 across exam, STEM, reasoning, knowledge, code, multilingual and long context categories using the same evaluation pipeline. Weights are available on Hugging Face in FP8 and BF16.'),
    ('The Decoder - Frontier Radar #5 profiles 27 neolabs betting against the current AI recipe (2026-11-06)',
     'research', 'frontier-radar-5-neolabs',
     'OpenAI is talking about the AGI era and Nvidia CEO Jensen Huang says AGI has arrived, with OpenAI president Greg Brockman calling GPT-6 Astra a turning point, while at the same time co-creators of today models are leaving OpenAI, Google DeepMind and Meta to start their own labs, raising billions with no product to show. The Decoder sorted 45 neolabs by research bets, profiled 27 in detail across six bets plus nearly 20 more in brief, and argues the shared motive is doubt about whether today recipe alone, meaning ever-larger language models trained on internet data refined with reinforcement learning, gets to AGI. Named departures include Ilya Sutskever founding Safe Superintelligence, Jerry Tworek running Core Automation, David Silver founding Ineffable Intelligence after AlphaGo, Yann LeCun leaving Meta after twelve years to found AMI, and Jeff Dean after 27 years at Google founding Discovery Loop. The money follows with Nvidia reportedly investing five billion dollars in SSI in July, Prometheus from Jeff Bezos pulling in twelve billion dollars at a 41 billion valuation in June, and Flapping Airplanes raising one billion dollars in an October Series A. Motives are mixed and not all technical, ranging from paper billionaire status and strategy disputes to wanting to do research without product pressure, and the piece notes established companies struggle with ideas that threaten their business, citing the innovator dilemma, with precedents from Transformer at Google in 2017, AlphaGo at DeepMind, and the Anthropic and OpenAI breakouts.'),
    ('OpenAI - Customer and university announcements in the feed (2026-11-05)',
     'openai', 'openai-customer-announcements-1105',
     'The OpenAI news feed added several items in the window: Australian universities are creating AI-native graduates by expanding access to ChatGPT and bringing AI into teaching and learning to prepare students for an AI-enabled workforce; Cult.fit builds operational muscle with Codex to help teams across functions build tools and move faster; Merge uses GPT-6 Astra, ChatGPT and Codex to review product code and support marketing, with teams also using AI to plan executive dinners and prepare sales updates; Flipsnack grew product signups by focusing ChatGPT Ads campaigns on getting people to try its product, lowering cost per signup; and Franklin Templeton is developing AI workflows starting with equity research to help portfolio managers compare research views and examine investment risks.'),
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
if os.path.exists('scout-raw/hn-items-1107.json'):
    for x in json.load(open('scout-raw/hn-items-1107.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-06-corpus.md',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'advisory_count': adv_count,
    'news_count': news_count + hn_count,
    'previous_snapshot': 'graphify-out/' + PREV,
    'next_window': '2026-11-08T00:30+08:00',
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count,
      'commits', com_count, 'advisories', adv_count, 'news', news_count + hn_count)
