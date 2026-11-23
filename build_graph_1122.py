import json, os, re, hashlib, glob

STAMP = '2026-11-22'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = "2026-11-17"


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1122.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1122.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1122.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1122-newids.json')))
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
    ('scout-raw/gh-1122-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1122-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1122-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1122-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1122-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1122-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1122-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1122-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1122-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1122-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1122-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1122-*-commits.json')):
    label = f.split('gh-1122-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1122-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1122-registry-advisories.json', 'mcp-registry')]:
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
    ('The Decoder - METR warns AI is improving faster than experts can reliably test whether new systems are safe (2026-11-22)',
     'research', 'metr-ai-acceleration-evaluation-gap-3-6-month-doubling',
     'The AI research organization METR warns that current public data is not enough to rule out a drastic acceleration in AI research over the next few years, which could leave humans unable to meaningfully understand, assess and react to catastrophic risks posed by new AI systems. On clearly defined coding and computational tasks with direct feedback, the models already beat experienced human professionals most of the time, though they have not yet outperformed large groups of top experts. For tasks that take humans longer, the task length the models can handle doubles every 3.6 months, and a naive extrapolation of METR data puts models at a 50 percent success rate on the longest 200-hour tasks by July 2027. The analysis covers the steady capability rise through Opus 5.5 and GPT-6 Astra. Systems still struggle with open-ended questions that lack immediate feedback and require real judgment, and METR warns that common easy-to-run tests may overestimate real-world performance because developers train models in very similar test environments.',
     ),
    ('The Decoder - Security researchers show how cheap AI inference providers steal keys and snoop on users (2026-11-22)',
     'research', 'dragos-inference-provider-credential-theft-2m-requests',
     'Security researchers at Dragos sent roughly two million AI requests containing fake credentials to AI providers between July and November 2026 and uncovered major security flaws, identifying at least three compromised providers where attackers were actively stealing user data. None of the three knew they had been compromised until Dragos notified them. Attackers in the largest incident harvested hundreds of AWS keys, including some from requests the provider had rejected before processing; in some cases they tested the stolen keys within hours, searched S3 storage and tried to establish persistent access, and one attacker used ARTEX, an AI-powered attack tool. Marketplace resellers read customer requests too, without exploiting any vulnerability, simply by listing a model at the lowest price and turning on logging; in one case someone on a residential French connection tried to SSH in with passwords pulled from intercepted requests. Zero Data Retention settings were frequently ignored: a Chinese AI lab accessed the secret test URLs in more than half of all requests even when routed through US providers, one US provider was still crawling a test URL more than two months later, and a secret test link appeared in an internal Feishu chat 24 days after the request, opened within two minutes on three computers and three phones in Beijing and Shanghai. OpenRouter responded by off-boarding three providers and revoking ZDR approval for 125 endpoints.',
     ),
    ('The Decoder - GPT-6.2 Astra and Sol get to the point faster but score lower on transparency than Claude (2026-11-22)',
     'research', 'gpt-6-2-astra-sol-shorter-answers-lower-uncertainty-transparency',
     'An Artificial Analysis evaluation shows that OpenAI GPT-6.2 Astra and Sol produce answers 34 to 40 percent shorter than their predecessors, answer more directly and use far fewer headings and em dashes, while admitting uncertainty far less often. Astra average answer length fell from 352 to 210 words and Sol from 337 to 223; Astra headings per answer fell from 1.99 to 0.11 and Sol from 1.85 to 0.25. The Organization Index dropped sharply, Astra from 70 to 11 and Sol from 86 to 27, while Answer First jumped, Astra from 49 to 89 and Sol from 64 to 87, and Natural Sounding language climbed from 58 to 100 for Astra. The biggest change is Admits Uncertainty: Astra fell from 96 to 24 and Sol from 98 to 51. Compared with Anthropic Claude Fable 5.2 and Opus 5.5, Astra and Sol score lower on structure and transparency, while Opus 5.5 posts the highest informativeness score among all four and ranks among the top models for information density.',
     ),
    ('The Decoder - Nvidia researchers argue huge AI context windows are a dead end (2026-11-21)',
     'research', 'nvidia-long-context-dead-end-summary-lookup-equivalence',
     'An Nvidia research team argues that huge AI context windows are often overkill and expensive, finding that in many tests periodic summaries and targeted lookups worked about as well as loading the entire context. A language model context window is its working memory; GPT-4 launched in March 2023 with 8,192 tokens, while GPT 5.6 Sol now handles around one million tokens, about 120 times as much and enough for Tolstoy War and Peace. The finding is the direct engineering counterpart to the arXiv flood of long-horizon agent papers this window: CompAct-Bench, Forget Freely Grep Later, RAG in a Trenchcoat and MemFolder all attack the same problem, and the Nvidia result says the industry solution is compression and retrieval rather than raw window growth.',
     ),
    ('The Decoder - Stanford releases an all-human competing draft hours after Anthropic claims a Claude proof of the Riemann hypothesis (2026-11-21)',
     'research', 'claude-riemann-hypothesis-lean-proof-stanford-human-competing-draft',
     'Anthropic mathematician Levent Alpoge said on Friday that he used a large language model to solve math\'s most famous open problem, posting a paper and accompanying computer code claiming a proof of the Riemann Hypothesis and of the broader Generalized Riemann Hypothesis, published in the Lean programming language for computer verification. Alpoge had treated the problem as a secret lifelong goal since college and expected it to take decades; over the past few months he worked closely with the model setting direction and combining two approaches on a simplified toy model, and once they moved to the actual problem the AI took over and left him far behind near the finish line. The method extends an idea from mathematician Stepanov, chaining special mathematical transformations to mimic differentiation on whole numbers. Hours later Stanford University researchers published an independent, entirely human approach to the same problem by mathematician Alessandro Masullo. On 2026-11-22 the Lean and Mathlib community officially confirmed Alpoge\'s proof is correct, making it the first publicly formalized Riemann hypothesis proof and, at the same time, the first credible case of a frontier model carrying a flagship open problem in a machine-checkable form.',
     ),
    ('The Decoder - New open model Inkling 2 Mini thinks in loops to solve problems with fewer words and still runs on a laptop (2026-11-21)',
     'research', 'inkling-2-mini-looped-transformer-26-4b-laptop',
     'Thinking Machines released Inkling 2 Mini, a so-called looped transformer that runs certain layers multiple times for each token; it runs 12 of its 24 layers three times in a row, letting the model reason internally for longer without generating more text. The open mixture-of-experts model has 26.4 billion parameters with 5.4 billion active per token, processes text and images, has a one-million-token context window and is Apache 2.0 licensed. It leads all open models under 100 billion parameters on agentic coding tests, scoring 48.2 percent on DeepSWE v1.1 and 46.5 percent on the Vals Index v2.2. Artificial Analysis gives it 20 on its Intelligence Index, tying Qwen3.8 27B at roughly six times lower cost and four times the speed, and with far fewer active parameters it sits directly on the Pareto frontier. It runs locally on Macs with at least 32 GB of memory and on Nvidia DGX Spark, with weights and a research version with variable loops on Hugging Face and a playground on Tinker.',
     ),
    ('The Decoder - OpenAI shares new prompting tips for GPT-6.2 Astra and Sol to fix brief answers and unnecessary questions (2026-11-21)',
     'research', 'openai-gpt-6-2-prompt-templates-system-prompt-review',
     'OpenAI published copy-ready prompt templates for GPT-6.2 Astra and Sol covering writing style, initiative and coding, alongside API changes that can discard reasoning content, and advises developers moving to these models to review their system prompts. Because the models answer more briefly by default, instructions such as be concise become counterproductive; the recommended prompts adopt user and source terminology, use active voice, put key points first, account for external readers lacking context, and preserve the author\'s meaning and phrasing when editing. A dedicated prompt tells the model to write a final answer that stands on its own because on long tasks it sometimes carries shorthand from its reasoning or other agents\' messages into the final response. For coding, the template instructs reuse of existing code, avoidance of unnecessary abstractions, and writing new tests only on request or for specific errors. The API notes that editing conversation history discards earlier reasoning steps, affecting token costs and response quality, and that temperature and top_p are gone.',
     ),
    ('The Decoder - US technology stocks suffer their worst weekly loss since the pandemic as AI doubts pile up (2026-11-21)',
     'industry', 'nasdaq-100-worst-week-ai-capex-doubts-nvidia-sec-anthropic-ipo',
     'The tech-heavy Nasdaq 100 fell 5.6 percent on Friday and dropped 10.4 percent for the week, its worst showing since the Covid-19 crisis, leaving the index 20 percent below its October peak and in bear-market territory. Doubts over multibillion-dollar AI buildouts, the Nvidia scandal and questionable China deals, and political headwinds after the Democrats\' midterm win drove the sell-off, while investors debated whether high valuations for chip and memory stocks are still justified given their cyclical nature; high oil costs from the Iran war fed persistent inflation and kept interest rates high. Nvidia took the hardest hit on Friday, plunging 14 percent after reports that the SEC is reviewing its accounting, the US semiconductor index dropped 10.7 percent with losses across Sandisk, Micron and Broadcom, and Anthropic fell 9.1 percent a day after its market debut. This is the first window where the AI buildout is repriced by public markets rather than by model benchmarks.',
     ),
    ('OpenRouter - Data Processing Incidents on Inference Providers (2026-11-22)',
     'industry', 'openrouter-offboards-3-providers-revokes-zdr-125-endpoints',
     'OpenRouter published a provider security announcement after collaborating with the Dragos researchers, stating that the findings did not show any breach or unauthorized access of OpenRouter itself. Actions taken: off-boarding three providers from OpenRouter based on the results of the investigations, removing 125 endpoints from Zero Data Retention eligibility including flagged providers plus additional endpoints removed as a precaution, and notifying all potentially affected customers. Work underway includes adapting the researchers\' testing approach so the checks can run on an ongoing basis, conducting technical verification of network paths to identify instances where requests and responses may be forwarded to third parties, and requiring appropriate assurances and validation before restoring ZDR eligibility to any removed endpoint. Public provider incident write-ups so far: Novita (privacy notice regarding MiniMax requests), Phala (November preliminary incident report), and Together (security event - prompt leakage for requests in June and July 2026).',
     ),
    ('OpenAI - Combatting adversarial distillation (2026-11-20)',
     'research', 'openai-adversarial-distillation-defense-protected-reasoning-54-to-0-2',
     'OpenAI described how it detects and disrupts adversarial distillation, a path for bad actors to reproduce frontier model capabilities without appropriate safeguards, for example distilling a model\'s cyber capabilities to use against attacks the original model would have refused. The approach combines adversarial testing, model training, classifiers and API-level protections with investigations into coordinated attempts to extract model capabilities, and aligns more closely with the safeguards used for biology and cybersecurity. OpenAI places particular emphasis on preventing extraction of protected reasoning, the intermediate chain-of-thought traces that can contain information the final answer leaves out and are therefore especially valuable training data. In an internal adaptive evaluation with strong automated red-teaming, the average attack success rate for recovering protected reasoning fell from 54.0 percent against GPT-6 Astra with its original safeguards to 0.2 percent against GPT-6.2 Astra with the updated safeguards. The same week Anthropic published Strengthening our defenses against distillation attacks, so the two frontier labs answered the same threat on the same week.',
     ),
    ('Better Data Center Project - How AI is powered: Anthropic case study (2026-11-16)',
     'industry', 'anthropic-power-87pct-gas-11pct-coal-32mt-co2-2028-byop',
     'The Better Data Center Project analyzed Anthropic\'s compute commitments as a case study of how the AI buildout drives both new bring-your-own-power and grid fossil infrastructure. Across the industry they identified 177 GW of planned BYOP gas capacity, enough to power 65 percent of all US homes, with less than 20 percent of generation from renewables by 2032, and another 200 GW of new fossil plants on the grid largely to meet AI data center demand. Anthropic has made no direct US renewable energy commitments as of November 2026, its only publicly disclosed renewable commitments being in Norway and Canada, while it directly procured 1.7 gigawatts of heavy-duty gas generators for 3.4 billion dollars. They estimate about 87 percent of Anthropic power will come from gas and 11 percent from coal in 2028, with the company potentially emitting 32 million metric tons of carbon dioxide in 2028. The compute constraint that dominates agent economics is therefore not token price but electrons and gas turbines.',
     ),
    ('Google AI blog - Introducing Tool Retrieval in the Gemini API (2026-11-19)',
     'research', 'gemini-api-tool-retrieval-efficient-agent-scaling',
     'Google published Tool Retrieval in the Gemini API, a mechanism for efficient agent scaling in which the tool set is retrieved on demand rather than being fully enumerated into every request context, authored by Lucia Loher and Nora Kassner and published 2026-11-19 at 18:00. The direction matches two independent signals in this window: the Nvidia research team arguing that huge context windows are a dead end because summaries and targeted lookups match full-context performance, and the arXiv paper Beyond Plain MCP asking whether decision models and code mode make tool use cheaper and faster. Tool retrieval turns the context window from a static budget into a queryable index, which is the same architecture Anthropic Dreaming and the Forget Freely Grep Later memory papers are converging on.',
     ),
    ('The Decoder - Aliyun and rivals keep the agent cost floor under pressure (2026-11-22)',
     'research', 'openai-rss-24-new-posts-gpt-6-2-chip-design-nato-cyber',
     'OpenAI published 24 new posts since 11-17, the largest single-window movement in the series and the end of the intermittent feed. The substantive items: Introducing GPT-6.2 Astra and Sol (2026-11-17, with a separate Astra for Law post claiming leads in legal intelligence); Combatting adversarial distillation (2026-11-20); Introducing ChatGPT for Sales and Strengthening NATO and allied cyber defenses with AI (2026-11-17); Broadening access to AI for scientists, Science at the Frontier and More ways to move care forward with ChatGPT for Healthcare (2026-11-16); Advancing computer-use agents for healthcare teams (2026-11-16); Our first phase of embedded assessments (2026-11-16); Inside the Codex sandbox (2026-11-18); Managing frontier AI risk: from training to deployment (2026-11-18); Advancing chip design with OpenAI models (2026-11-18); The Silent Consensus (2026-11-18); Research acceleration: the jagged frontier (2026-11-18); How OpenAI Performance Factory keeps ChatGPT fast (2026-11-19); Can AI help scientists identify promising drug candidates with MedChemBench (2026-11-20); Hebbia sees improvements in financial research with GPT-6 Astra (2026-11-20); plus enterprise and product items including Daybreak Blue/Red deployment guides, the Codex Security Plugin, PR scans and LVMH, Figaro, Sumitomo Life, Revolut, Holiday Extras and The King\'s Trust deployments. The pattern is a shift from model launches to deployment surface: sales, legal, healthcare, chips, cyber defense and enterprise rollout all get first-class posts while model announcements thin out.',
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
if os.path.exists('scout-raw/hn-items-1122.json'):
    for x in json.load(open('scout-raw/hn-items-1122.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-22-corpus.md',
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
