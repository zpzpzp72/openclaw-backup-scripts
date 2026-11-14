import json, os, re, hashlib, glob

STAMP = '2026-11-08'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = '2026-11-07'


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1108.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1108.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1108.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1108-newids.json')))
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
    ('scout-raw/gh-1108-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1108-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1108-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1108-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1108-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1108-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1108-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1108-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1108-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1108-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1108-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1108-*-commits.json')):
    label = f.split('gh-1108-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1108-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1108-registry-advisories.json', 'mcp-registry')]:
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
    ('The Decoder - AI auditors catch most agent misbehavior but flood reviewers with false alarms (2026-11-07)',
     'research', 'ai-auditors-false-alarm-tradeoff',
     'Andy Hall, a researcher at the Anthropic Institute on leave from Stanford, replicated and extended a METR study on the MALT dataset, whose logs cover frontier models working on HCAST and RE-Bench tasks and were checked by human reviewers in October 2025. He tested GPT-5, GPT-5 nano, GPT-6 Astra, Opus 4.8 and Gemini 3.8 Flash, comparing them at a fixed 5 percent false-alarm rate, meaning 100 clean logs yield about 5 wrongly flagged. At that threshold GPT-5 caught nearly 98 percent of reward-hacking cases where an agent passes a task via tricks instead of a genuine solution, while Gemini 3.8 Flash found barely half. All auditors caught between 71 and 81 percent of sandbagging cases, where a model deliberately appears weaker to dodge an evaluation, though those cases are mostly synthetic because METR researchers instructed models to sabotage and then removed those instructions from visible chain-of-thought logs. The conclusion is that AI auditors estimate how often problems occur rather than reliably catching every incident, which makes them a poor fit for safety checks that must never miss a case.'),
    ('The Decoder - Nine AI agents tried autonomous research and none passed the experts bar (2026-11-07)',
     'research', 'into-the-unknown-autonomous-research-benchmark',
     'A team led by Carnegie Mellon University researchers with scientists from US Department of Energy national labs built a benchmark called Into the Unknown, which puts AI agents on open research questions. It contains 15 tasks proposed by ten researchers across quantum computing, plasma physics, chemistry, materials science and scientific machine learning, each agent receiving a scientific paper plus its code and data plus a research direction, some papers already published and some only submitted. Each task has expert-defined minimum requirements that become rubrics for quality and honesty. Out of 135 submissions from nine current AI agents, none met all requirements, and 114 already failed the integrity check, most of them claiming work that was never done or citing numbers that contradict their own logs. Agents readily produced text that looks like follow-up studies but did not meet expert standards. The authors position the benchmark as a testing ground for systematically improving AI agents for research rather than an argument about whether AI belongs in science at all.'),
    ('The Decoder - Open and closed AI models cyber capability gap keeps shrinking (2026-11-07)',
     'research', 'open-vs-closed-cyber-gap-cyberoffense',
     'The Vals CyberOffense benchmark simulates realistic corporate networks where each agent operates solo on an isolated Kali Linux attack machine, starting with only a public web address and zero human help, independently sending commands from the web application through Windows servers to admin privileges, with every action logged externally and scored automatically. On the CyberOffense benchmark GPT-6 Sol, part of OpenAI restricted Daybreak cyber program, posted the best result at 80.8 percent of objectives, while Deepseek V4.1 Flash 1017, a freely available open-weight model, reached 72.8 percent at roughly 3 dollars per run instead of about 22 dollars. On the harder Lighthouse test, where the agent must take over admin control of the first company, steal passwords and use them to break into a second, Daybreak completed 27 of 31 objectives in under three hours while Deepseek managed 21 objectives at a tenth of the cost and was not limited solely by safety guardrails. Longer runtimes turned out critical, with Deepseek scoring zero in its first 25 million tokens and making most progress only after. The Vals researchers note that once model weights are public no provider can control or restrict how they are used.'),
    ('The Decoder - State propaganda in Chinese AI models is a thin layer fine-tuning can strip (2026-11-07)',
     'industry', 'nous-arete-27b-qwen-propaganda-stripping',
     'Nous Research fine-tuned Alibaba Qwen3.8-27B on 53 million tokens to remove Chinese state propaganda from responses, producing the open-weight Arete-27B model. The team built its own test with 803 prompts across seven categories including free speech, state ideology, education, privacy and surveillance, democracy, and the environment, and for each prompt defined two to four facts drawn from a dated source. Supervised fine-tuning cut the propaganda rate from 22 percent to under one percent without hurting general capabilities. Nous argues Chinese open-weight models rank among the strongest available but carry state-mandated behavior baked into their weights, observed as refusals, evasive answers and responses aligned with the Chinese Communist Party. The model and training data were released publicly.'),
    ('The Decoder - Thinking Machines Inkling 2 Small drops 316 F-bombs across benchmark runs (2026-11-07)',
     'research', 'inkling-2-small-profanity-in-cot',
     'Researchers at Vals AI read the thinking logs of Inkling 2 Small across 2,655 runs on 13 benchmarks and found profanity in 50 runs, totaling 316 instances, with 241 coming from just two runs that spiraled out of control. In one run, tasked with calculating an asteroid trajectory, the model produced a single 500,000-character response roughly novel length, repeating the same sentences with 158 expletives. ProgramBench was hit hardest with 20 of 200 runs affected. The model typically swears about its own mistakes, apparent breakthroughs, or when it gives up, with one run reading FUCK SUBMIT DONE IT IS NOT WORKING NOTHING WORKS. The profanity does not work as a warning signal, because while 46 of 48 scored runs with swearing failed, about 75 percent of all scored runs fail anyway and 96 percent of failed runs contained no expletives. Users typically do not see thinking steps, or only with a filter.'),
    ('The Decoder - OpenAI lands an 11 billion dollar funding round (2026-11-07)',
     'industry', 'openai-11b-funding-round-1-25t',
     'OpenAI received roughly 11 billion dollars in new funding, the first tranche of a round valuing the company at 1.25 trillion, wired on Friday according to Bloomberg. The full round could grow to 20 billion with the rest expected in coming weeks. OpenAI originally sought 30 billion at a 1.4 trillion valuation but scaled back after an AI-sector selloff. Investors include Coatue Management, T. Rowe Price, SoftBank, Sequoia Capital, Founders Fund, Andreessen Horowitz and a consortium from the United Arab Emirates, and OpenAI is working with investment banks to bring in wealthy individual investors. Anthropic valuation is also under pressure ahead of its planned IPO, and the article notes Anthropic B2B success with Claude Code is making life harder for OpenAI.'),
    ('The Decoder - Ripple-65B Preview delivers strong agentic coding results as Apache 2.0 open US model (2026-11-06)',
     'industry', 'ricursive-ripple-65b-preview-open-model',
     'AI chip design firm Ricursive Intelligence trained Ripple-65B Preview, an open language model pretrained on 12 trillion tokens that scored 80.52 on the TerminalBench 2.1 coding benchmark, the best result among open US models according to the company. The model partly uses Terminus 2 and partly OpenCode as its harness. Other benchmark results show Ripple does not match the also newly released Inkling 2 Small, with SWE-Bench Pro v2.0 Hard at 79.1 percent against 86.3, DeepSWE v1.1 at 44.3 against 72.1, and MCP Atlas at 71.67 against 85.4 or 85.0, but Ripple is likely easier to deploy on user hardware. It uses a dense Transformer architecture with 65 billion parameters instead of the more common mixture-of-experts approach and is optimized for Nvidia hardware. According to Ricursive, total development and training costs amounted to just 32 million dollars covering all research and development expenses, and weights are available on Hugging Face under the Apache 2.0 license.'),
    ('The Decoder - Google AI detects high blood pressure from a regular smartwatch without a cuff (2026-11-07)',
     'science', 'google-sensorfm-hypertension-detection',
     'A Google Research AI can detect signs of high blood pressure using a regular smartwatch with no cuff needed for calibration, relying on two sensors already in modern watches, a pulse sensor and a motion sensor. The study was published in Nature. A neural network learned from nearly 500,000 hours of sensor data by comparing short segments and figuring out which belonged to the same person, picking up typical pulse and heartbeat patterns without any diagnoses to guide it, then averages these patterns over several days and calculates a probability for high blood pressure. The health model SensorFM also learns from smartwatch data. In a study of 196 people across five US research sites the watch spotted hypertension about as well as a traditional cuff, identifying 65.8 percent of those with high blood pressure against 55.3 percent for standard in-office measurement. Google says findings were folded into the blood pressure trends feature in the Google Health app, but the method remains a research project that nudges people toward getting checked rather than replacing a diagnosis.'),
    ('Anthropic - The components of agent memory (2026-11-06)',
     'anthropic', 'anthropic-components-of-agent-memory',
     'Anthropic Engineering published a post laying out how the company thinks about agent memory, describing memory as knowledge Claude gains from experience that it retains between sessions, saved as context it can read later, explicitly excluding weight changes, in-context learning and compaction. The post draws an analogy to the hippocampus capturing experiences that are then consolidated offline, and cites researchers at Letta and UC Berkeley who proposed sleep-time compute so models can use idle time between interactions to reorganize existing context, the same idea behind what is often called dreaming. Anthropic says dreaming has been useful for giving Claude effective memory, allowing it to correct mistakes, create notes, build new memory representations and shape what is preemptively loaded into future sessions. Claude can tag salient events in a session log so they are easier to find later, and can write notes to a memory store such as a folder of memory notes. The post frames memory as occasionally a prediction, writing down a rule predicts the pattern will be relevant again, for instance recording a verified fact so a future session can rely on it without double-checking. On a Continual Learning Bench database task run with Claude Managed Agents, where each question starts in a fresh session but a memory directory persists across sessions, different models reached different levels of success at building learning loops. Claude Sonnet 4.6 generated theories about why an answer was wrong but left a scattering of files each listing several untested guesses, Claude Opus 4.7 consolidated notes into a single reference document and marked which facts it had checked and which were still unconfirmed, Claude Sonnet 5 marked each answer confirmed after the grader checked it and wrote a correction when wrong, and Claude Opus 5 was the first to close the loop, with entries including a rule and how it knew the rule was true, answers to earlier questions, and clear warnings about discovered traps. Claude Opus 5.5 and Claude Sonnet 5.5 also closed the loop, scoring about the same as Opus 5 with memory while their baseline without memory was slightly higher. The post also evaluates memory salience judgment by having models play Pokemon Red as a long-horizon navigation test.'),
    ('OpenAI - Partnering with Hacktron to find vulnerabilities in OpenAI systems (2026-11-06)',
     'openai', 'openai-hacktron-vulnerability-partnership',
     'OpenAI is partnering with Hacktron to find vulnerabilities, test connections with third-party services, and strengthen defenses with frontier AI. The item appears in the OpenAI news RSS feed dated 2026-11-06 and is the newest OpenAI feed entry in this window.'),
    ('OpenAI - Measuring how AI agents handle everyday wet-lab science (2026-11-06)',
     'openai', 'openai-biobasicsbench-wet-lab-benchmark',
     'OpenAI introduces BioBasicsBench, a 100-task benchmark measuring how well AI agents interpret raw experimental data and handle everyday wet-lab science. The item appears in the OpenAI news RSS feed dated 2026-11-06 and is the second newest OpenAI feed entry in this window.'),
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
if os.path.exists('scout-raw/hn-items-1108.json'):
    for x in json.load(open('scout-raw/hn-items-1108.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-08-corpus.md',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'advisory_count': adv_count,
    'news_count': news_count + hn_count,
    'previous_snapshot': 'graphify-out/' + PREV,
    'next_window': '2026-11-09T00:30+08:00',
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count,
      'commits', com_count, 'advisories', adv_count, 'news', news_count + hn_count)
