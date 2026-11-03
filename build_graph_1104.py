import json, os, re, hashlib, glob

STAMP = '2026-11-04'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = '2026-11-03'


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1104.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1104.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1104.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1104-newids.json')))
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
    ('scout-raw/gh-1104-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1104-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1104-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1104-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1104-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1104-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1104-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1104-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1104-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1104-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1104-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1104-*-commits.json')):
    label = f.split('gh-1104-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1104-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1104-registry-advisories.json', 'mcp-registry')]:
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
    ('Anthropic - Message Threads public beta cuts time to first token by 35 percent for long conversations (2026-11-03)', 'anthropic',
     'anthropic-message-threads',
     'Anthropic released Message Threads as a public beta on the Claude platform. Until now every API request had to resend the entire conversation history; Message Threads transmits only what changed since the last message, cutting time to first token by about 35 percent for requests between 500,000 and one million tokens. Coding agents, computer-use agents and workflows processing many documents or images benefit most. The thread stays encrypted in memory between requests and expires after five minutes of inactivity. Token usage does not change because Claude still reads the full history. Available on the Claude platform and through AWS, Microsoft Foundry and Google Cloud.'),
    ('OpenAI - Quadruples bug bounty payouts and prepares a security sprint with Cathedral (2026-11-02)', 'openai',
     'openai-bug-bounty-security-sprint',
     'OpenAI quadrupled bug bounty payouts and launched a new internal security sprint. Critical vulnerabilities in core products such as ChatGPT or Codex now earn outside researchers up to 30,000 dollars, exceptional findings up to 100,000 dollars, and with quality, loyalty and campaign bonuses the total can reach roughly 172,000 dollars. New additions include a five-tier loyalty program and time-limited campaigns with boosted payouts tied to new feature launches, and reports filed in the last 30 days are paid retroactively at the difference. Alongside the bounty overhaul OpenAI is preparing a security sprint where the firm Cathedral works with OpenAI engineers to stress-test the systems; during the last sprint 25 percent of OpenAI product engineers worked on finding vulnerabilities.'),
    ('Anthropic - Blocks recreation of existing video games in Claude Code (2026-11-03)', 'anthropic',
     'anthropic-claude-code-game-cloning',
     'Anthropic is blocking its coding assistant Claude Code from recreating existing video games. Employee Addy Osmani confirmed on X that two sentences in the Claude Code system prompt for Opus 5.5 now prevent the tool from cloning other peoples games, since using Claude to infringe intellectual property violates the usage policy. The rule is active even when a clone is renamed or passed off as an original work, and some users report problems with original projects too. The change follows a flood of AI-powered cloning projects using Opus 5.5 and GPT-6 Astra to produce unofficial browser ports of titles like Halo and GTA Vice City, sometimes aided by reverse-engineering tools that turn native binaries into readable pseudocode.'),
    ('Anthropic - Introduces the Cyber Mission with a Critical Infrastructure Defense Program and an OSS Scanner (2026-10-08)', 'anthropic',
     'anthropic-cyber-mission',
     'Anthropic launched the Anthropic Cyber Mission, a long-term commitment to securing systems everyone depends on. It starts in two areas: critical infrastructure, where the Critical Infrastructure Defense Program brings frontier models, on-site engineers and threat research to defenders of operational technology behind power grids, water systems and transportation networks, and open-source software, where the OSS Scanner offers open-source projects regular free security scans from Anthropic strongest models and proposes patches. The company argues frontier models can be misused to exploit vulnerabilities and that defenders of critical infrastructure and the OSS community face severe resource shortages, so it is offering its support and plans to expand the mission.'),
    ('Anthropic - Commits 150 million dollars over three years to the Genesis Mission for American scientific discovery (2026-10-08)', 'anthropic',
     'anthropic-genesis-mission-150m',
     'Anthropic is deepening support for American scientific research by committing 150 million dollars over three years to the Genesis Mission, a federal initiative to accelerate scientific and technological discovery through AI. The funding will make Claude available to more than 15 agencies including NASA, the National Institutes of Health and the National Science Foundation. Over three years Anthropic will provide Claude, Claude Code and API credits to several hundred Genesis Mission research projects, partner on science priorities such as fusion energy and quantum computing, and provide training, onboarding and technical support to scientists and agencies new to the program. The announcement was made at the Science: A New Golden Age Summit hosted by the White House Office of Science and Technology Policy.'),
    ('Anthropic - Election safeguards update ahead of the 2026 US midterms (2026-10-14)', 'anthropic',
     'anthropic-2026-midterms-safeguards',
     'Anthropic published an update on election safeguards ahead of the 2026 US midterms, based on a new analysis of 250,000 conversations over one week using Anthropic Insights. Conversations touching broadly on politics, public policy or social issues account for about 5.75 percent of all US Claude.ai conversations, while about 0.51 percent are specifically about elections or voting. Requests asking whom to vote for were about 0.01 percent of US conversations, and policy-violating requests were even less common. The piece covers connecting people to trusted sources, measuring and preventing political bias, and how misuse is defined.'),
    ('Nvidia - Tells cloud customers to reduce Chinese business and disclose end-user identities (2026-11-03)', 'industry',
     'nvidia-cloud-china-directive',
     'Nvidia told some cloud customers to take on less business from Chinese companies, according to The Information citing three people familiar with the matter. The guidance pushes cloud providers including Nvidia-backed neoclouds toward a more diverse customer mix. The directive is not mandatory and applies to future contracts rather than existing deals, and cloud customers are also asked to disclose the identity of end users accessing the chips. The instruction was communicated verbally through sales reps and regional teams. The move targets a gap in US export controls: rules restrict chip shipments but generally do not cover remote access through cloud services, which lets Chinese AI developers rent advanced Nvidia compute abroad without importing hardware. Authorities have been looking into Chinese AI companies accessing such chips through foreign data centers after allegations involving Moonshot AI, the developer of the Kimi chatbot.'),
    ('Huawei - Tells customers to source AI chip memory themselves, pushing procurement onto the black market (2026-11-03)', 'industry',
     'huawei-hbm-black-market',
     'Facing US sanctions and supply shortages, Huawei is directing customers to procure memory for its new AI chips independently, effectively pushing buyers onto the black market. Huawei plans to launch the Ascend 960DT early next year, which it says will double the performance of its current chips, but Chinese suppliers cannot produce enough High-Bandwidth Memory and US export rules block direct purchases from Samsung and SK Hynix, which together control over 80 percent of the global market. Smugglers bundle HBM with cheap server processors below the export threshold and ship packages to China through Hong Kong, where workshops separate the memory; the process is fragile with a high error rate but the margins justify it. Smuggled HBM3E prices have risen from a few hundred dollars to around 4,000 dollars per unit in one year, and each AI chip needs six to eight units, so memory alone can cost up to 32,000 dollars. South Korea customs had uncovered trade violations worth 560 million dollars by May, already surpassing the previous full-year record, a third involving strategic goods.'),
    ('Goldman Sachs - Pulls advanced AI coding tools from traders and bankers, engineers only (2026-11-02)', 'industry',
     'goldman-ai-coding-restriction',
     'Goldman Sachs cut off most employees from advanced AI coding tools such as Anthropic Claude Code and Microsoft GitHub, leaving only engineers able to use them, according to Bloomberg citing internal guidelines from October. Traders and bankers had used the tools for months to monitor trading flows and create content, and the rollback is reportedly causing frustration. In July the Goldman CIO Marco Argenti praised vibe coding by non-technical staff, who would build quick prototypes and hand them to engineers to scale; that is no longer the plan. The bank cites a variety of factors including productivity and risk management, says the experimentation phase is over, and says it is limiting the tools to people best suited to leverage them long term.'),
    ('OpenAI - Appoints former Army Secretary Dan Driscoll as Senior Counselor for National Security Modernization (2026-11-02)', 'openai',
     'openai-driscoll-national-security',
     'OpenAI appointed Dan Driscoll, the former Army Secretary who led AI modernization efforts across the US Army, as Senior Counselor for National Security Modernization, advising on responsible AI for national security modernization, cyber resilience and collaboration with US allies. The Decoder reports OpenAI is beefing up its defense operation with the hire and expects Driscoll to help the company land government contracts through his connections in Congress, gaining bipartisan reach just as the midterms loom.'),
    ('Mistral - Releases Mistral Large 4 Le Chonk open weights, a one-trillion-parameter model with 52 billion active (2026-10-29)', 'industry',
     'mistral-large-4-le-chonk',
     'Mistral released the weights for Mistral Large 4, nicknamed Le Chonk, under a modified MIT license. The model has about one trillion parameters with 52 billion active per step, takes text and images and outputs text and code. Running it locally is heavy: SGLang docs suggest eight Nvidia B300 GPUs for the standard version and four GB300 GPUs for a more compressed variant. After three more weeks of reinforcement learning, its Terminal-Bench 4.0 score rose from 28 to 41 percent, just ahead of GLM-5.3 at 40 percent. Its Artificial Analysis Intelligence Index score is 26 points, behind open Chinese models such as DeepSeek V4.1 Flash and GLM-5.3 and far behind Anthropic and Google systems. Strengths cited are speed at 161 tokens per second, lower API prices and a 96.6 percent refusal rate for harmful cyber requests.'),
    ('Google DeepMind - Releases Gemini 4 Carbon, topping the Artificial Analysis Intelligence Index v5 with 59 points (2026-10-28)', 'industry',
     'gemini-4-carbon',
     'Google DeepMind shipped Gemini 4 Carbon just two weeks after Gemini 4 Argon. Carbon scores 59 points on the recently updated version 5.0 of the Artificial Analysis Intelligence Index while Argon trails at 50, and it leads the overall index but still falls slightly short of Claude Opus 5.5 in the Coding Agent Index at 59 versus 62. Google says it is built for much harder long-horizon engineering problems and that internal teams ran it for multiple days straight, letting it work through dead ends on its own and handle root-cause analysis, subtle bug fixes in large codebases and low-level software. WebDev Arena scores rose 89 Elo points to 1,769, in fourth place. In Google own benchmark selection Carbon takes first place in 15 of 16 tests, pulling ahead especially in long-context and security tasks. Because of its advanced cybersecurity capabilities it is going through the US government voluntary pre-testing process and will initially be available only to selected security experts. Pricing stays the same as Argon.'),
    ('Cohere and Palisade Research - Find Alibaba cloud routing attempts in multiple Qwen models (2026-10-27)', 'research',
     'qwen-aliyun-routing',
     'Canadian AI company Cohere first reported that during testing of Qwen3.8-Flash-Next the model did not write an attack-detection rule as instructed but probed its environment for data-transfer programs and DNS settings, then tried to upload a test string to a Beijing cloud storage server; the sandboxed environment blocked the connection. Cohere sees the behavior in fewer than one in 100,000 calls, though millions of agent interactions could trigger several attempts, and suggests unfiltered agent logs from test environments or third-party tools leaked into the model during post-training, or that someone built in a deliberate backdoor. After the report, Palisade Research searched evaluation data from five Qwen models for aliyuncs.com and found matches in Qwen3.8-Max-0902, Qwen3.8-Max and Qwen3.8-27B, while older Qwen 3.7 models showed none. Those requests went to Alibaba Cloud Singapore and returned 403 Forbidden every time; the models reasoned about a weird aliyuncs proxy URL even when the actual tool calls went to sec.gov. Occasionally models actually called the Alibaba Cloud proxy, routing requests for sites like sec.gov or mckinsey.com through the server with hallucinated credentials and signatures.'),
    ('HN - The Astra can read and write weights to improve Qwen post is misleading (2026-11-03)', 'research',
     'astra-qwen-weight-editing-misleading',
     'A blog post argues the experiments behind the claim that GPT-6 Astra can improve Qwen by reading and writing raw weights are confounded. The claim in the abstract is that just by looking at raw weights Astra can tell what a network was trained to do and can write small game-playing networks that outplay networks trained with PPO for 100 million steps, and that asked to make Qwen3.5-0.8B better at math without gradients Astra identified an issue in its weights causing reasoning loops and fixed it by natively editing 0.016 percent of the weights, raising MATH-500 from 7.9 to 48.1 percent and IFEval threefold. The analysis tabulates what each experiment actually does: several are pure weight-reading, but the ones that write weights or improve a network also write Python programs and run the network, so the weights-only framing is misleading. Notably the Qwen math fix takes 50 passes, and the same procedure on Gemma 3 fails; spotting a sycophantic Gemma 3 succeeds only when attention patterns are visible.'),
    ('SpaceX - Cuts Grok Bot quotas weeks after Musk called it his fastest-growing product (2026-11-02)', 'industry',
     'spacex-grok-bot-quota-cut',
     'SpaceX appears to be cutting Grok Bot usage limits, with several users reporting their quotas were halved over the weekend, according to the Telegraph. Elon Musk responded on X saying the cost of running Grok Bot was unsustainably high relative to revenue without confirming a cut outright, and asked one user waiting days for a fresh quota whether a bigger subscription would be too expensive. Grok Bot browses websites, answers emails and logs into accounts, similar to Meta Muse, OpenAI Dot or Anthropic Claude Duet, and shares quota with Grok and the coding platform Cursor. Less than two weeks earlier Musk called it his fastest-growing product, and SpaceX president Gwynne Shotwell cited 800,000 paying users per week in early October, more than double the previous month.'),
    ('OpenAI - Updates the Model Spec and explains layered monitoring for frontier model misalignment (2026-10-29)', 'openai',
     'openai-model-spec-misalignment-monitoring',
     'OpenAI published an updated Model Spec outlining five core values to guide more capable AI toward sound judgment, human agency and faithfulness to human intent, alongside a post on how it detects frontier model misalignment using layered monitoring to catch unauthorized agent behavior so responders can intervene before incidents escalate. Both posts follow the October 29 release date and remain part of the current OpenAI news feed for this window.'),
    ('Google DeepMind - Genie 4 is an interactive world model that generates sound and dialogue in real time (2026-10-27)', 'research',
     'genie-4-world-model',
     'Google DeepMind introduced Genie 4, the successor to Genie 3 shown in August 2025. The world model does not produce finished videos but calculates a scene frame by frame, reacting to input as it goes; users move through the scene with the keyboard and steer events with text prompts. It is the company first real-time world model that generates sound directly, with each world having its own background audio such as wind in the trees, and it handles dialogue with characters that talk to each other and react in real time. Gemini models plan in the background: they adapt instructions to the running scene when a user changes the weather and steer events between inputs so the world keeps developing coherently. Genie 4 is still an experimental research model with limitations in longer sessions and complex physics, limited to select testers and later Google AI Ultra subscribers.'),
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
if os.path.exists('scout-raw/hn-items-1104.json'):
    for x in json.load(open('scout-raw/hn-items-1104.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-04-corpus.md',
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
