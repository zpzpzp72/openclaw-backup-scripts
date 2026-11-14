import json, os, re, hashlib, glob

STAMP = '2026-11-14'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = '2026-11-08'


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1114.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1114.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1114.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1114-newids.json')))
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
    ('scout-raw/gh-1114-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1114-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1114-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1114-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1114-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1114-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1114-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1114-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1114-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1114-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1114-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1114-*-commits.json')):
    label = f.split('gh-1114-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1114-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1114-registry-advisories.json', 'mcp-registry')]:
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
    ('The Decoder - OpenAI reassigns robotics researchers as general-purpose models may make specialized robotics AI unnecessary (2026-11-14)',
     'research', 'openai-robotics-teams-folded-into-general-models',
     'OpenAI is apparently disbanding its robotics team again, but for different reasons than in 2020, folding researchers into other teams to accelerate rather than abandon robotics. Robotics researchers move to the main research team under Chief Research Officer Mark Chen, while applied robotics and hardware teams join Greg Brockman Applied organization. The decision was made on such short notice that the company had already booked a booth at the Conference on Robot Learning in Austin, which then sat empty, Fortune reports. OpenAI believes general-purpose models like GPT-6 Astra can control robots directly, reducing the need for specialized robotics models. In an Nvidia study an Astra-powered agent achieved 74.8 percent success on simulated robotics tasks versus 51 percent for the best specialized models, using a simulated DROID robot. On a new robotics benchmark called StationeryBench comparing GPT-6 Astra with Ai2 MolmoAct2 on five desk-object tasks with dual-arm YAM robotic arms, across 200 trials Astra fully completed 7 of 100 tasks while MolmoAct2 completed none, with Astra average progress score 46 versus 12. Yoav Artzi of Cornell and Google DeepMind says Astra reaches near-human accuracy on the unpublished REMAP benchmark and suspects OpenAI trained on large amounts of 3D data such as Blender scenes. OpenAI rebuilt the team in 2024 after shutting it down in 2020 for lack of training data, Sam Altman is reportedly targeting a first public robot demo for 2027, and the company faces heavy financial pressure to focus on its core AI business where it has lost significant ground to Anthropic.'),
    ('The Decoder - Anthropic can already retrain Mythos with a fraction of the compute originally needed (2026-11-14)',
     'research', 'anthropic-mythos-superexponential-algorithmic-progress',
     'Jacob Coxon, a former OpenAI and Anthropic researcher who brought AI fears into the mainstream, says a slide from Anthropic IPO roadshow showing how much compute Anthropic needs over time to train its models was a major reason he quit after only about four months. The chart compresses the axis so a 10x and a 100x increase barely look different, yet the curve still climbs steeply, which Coxon says shows algorithmic efficiency is improving not just quickly but at an accelerating rate. He writes that Anthropic Mythos, a major capability jump in the spring, was not a one-time deviation but a point on a superexponential, and that Anthropic could already retrain Mythos with a fraction of the compute originally needed. He says algorithmic improvements are on the verge of being automated, which is why he wants frontier model development paused next year so competitors can catch up, claiming a pause would commoditize human-level intelligence and only harm OpenAI and Anthropic. Anthropic notes the data points are based on internal estimates and are for illustration only. Coxon previously trained models at OpenAI and most recently Anthropic, and drew wide attention in September with public warnings about risks of advanced AI systems.'),
    ('The Decoder - Runway open-source Praxis-1 turns video AI into a robot controller (2026-11-14)',
     'industry', 'runway-praxis-1-open-weight-robot-controller',
     'Runway released Praxis-1, its AI model for controlling robots, with model weights and source code under the Apache 2.0 license allowing commercial use. Runway first introduced Praxis-1 in late September with access only to select partners, and alongside the release published a detailed research report with new performance tests. Praxis-1 takes in camera images, text instructions and robot position information, predicts how the environment will change and calculates the right robot movements, continuously adjusting control as new camera frames arrive. It builds on a video model that learned how objects move and interact from ordinary footage, then fine-tuned it with videos of human actions and robot data. Runway calls Praxis-1 a World Action Model. Since September, robotics companies Standard Bots, Noble Machines and Ultra have been testing it on a humanoid robot, an industrial robot arm and a dual-arm warehouse robot. To adapt to a Franka robot arm, Runway used about 277 hours of recordings from the public DROID research dataset, while a dual-arm robot used between 1400 and 2600 hours of training material. The model still needs some specialized robot data, occasionally confuses similar-looking objects, and cannot yet reliably plan complex action sequences on its own.'),
    ('The Decoder - Jensen Huang ouster likely traces back to Nvidia risky business practices (2026-11-13)',
     'industry', 'nvidia-huang-ouster-credit-guarantee-program',
     'A Wall Street Journal report suggests Jensen Huang was pushed out more over Nvidia business practices than over his affairs. Nvidia built a risky credit program under Huang offering AI cloud providers and data center developers billions of dollars in financial guarantees so they could afford Nvidia chips, with Huang son-in-law Nico Caprez pushing the program and promising partners quick closings, in exchange for a cut of their revenue. The largest deal involved talks with OpenAI over a 250 billion dollar guarantee for a data center in Ohio. Nvidia shares fell 5 percent after the deal became public. Interim CEO and former CFO Colette Kress cut the commitment to OpenAI in half and the scaled-back deal was signed in August. Kress had questioned internally how the guarantees were valued and had tried to rein in Caprez, and in an August meeting Huang reportedly called her a deer in the headlights and dismissed her as a mere reporting CFO. Circular AI deals by Nvidia and other cloud and chip companies have drawn criticism since at least last year for inflating a bubble. Nvidia average monthly stock multiple fell from 23 to 16 between May and October, and Nvidia responded with the largest share buyback in its history. Major cloud providers were planning to adopt alternative chips and reduce dependence on Nvidia. At GTC Berlin in October Huang used a story about a soup vendor in Japan to pressure half a dozen cloud CEOs.'),
    ('The Decoder - OpenAI rebuilt AI shopping from scratch with ChatGPT Wallet (2026-11-13)',
     'industry', 'openai-chatgpt-wallet-agent-payments',
     'OpenAI is taking a second shot at AI shopping with ChatGPT Wallet, catching up with Anthropic, Meta and xAI whose agents can already shop online. ChatGPT Wallet lets AI agents pay on behalf of users, and OpenAI built it after scrapping Instant Checkout, its first attempt, because it was not flexible enough. At launch it is available only in the US through Dots, to adults with a ChatGPT Pro subscription and an eligible US bank card. Users add their card once, and before every purchase the system displays the items, the total and the selected card, and the user approves each payment with a security check such as Face ID or a fingerprint. Neither the agent nor the online store ever sees the real card details, because payment partners American Express, Mastercard and Visa generate a payment token. Existing card rewards and usual bank protections for eligible disputes still apply. OpenAI plans to eventually let users hand purchases off to their agents entirely within set spending limits, product categories and timeframes. A purchase starts with the customer describing what they want, ChatGPT searches the open web, APIs or merchant product feeds, the user compares options and picks one, then ChatGPT completes the purchase either by using a browser on the merchant existing website or through a plugin supporting structured actions such as managing the cart. Many websites and payment systems still block AI agents as bots or reject their purchases for security reasons, so OpenAI also released a Commerce Partner Playbook explaining how merchants can adjust firewalls, provide product data and work with providers such as Stripe, Adyen and Riskified.'),
    ('The Decoder - Banks bar Chinese and Hong Kong investors from Anthropic IPO over US export controls (2026-11-13)',
     'industry', 'anthropic-ipo-banks-bar-chinese-investors-itar',
     'Investors from mainland China and Hong Kong are being shut out of Anthropic IPO, according to Bloomberg. Multiple banks have reportedly rejected buy orders from those regions or consider allocations unlikely, with some people involved citing ITAR, the US export control rules governing defense-related goods. Anthropic declined to comment. Goldman Sachs and Morgan Stanley are leading the offering with 20 other banks involved. The stock is expected to trade on Nasdaq under the ticker ANT after pricing on November 18. Anthropic products are not officially available in China or Hong Kong, and it has blocked firms under Chinese control from its AI services and is fighting workarounds that let Chinese companies access Claude Code. It also exposed large-scale distillation attacks by DeepSeek, Moonshot and MiniMax involving some 16 million queries.'),
    ('The Decoder - Anthropic Claude for Manufacturing plugs AI into factory software (2026-11-13)',
     'industry', 'anthropic-claude-for-manufacturing-model-hardware-standard',
     'Anthropic released Claude for Manufacturing, a plugin giving the AI direct access to industrial software to automate factory workflows. It connects via four universal interfaces to Autodesk Fusion, Oracle NetSuite, Microsoft 365 and Infor, with other systems integrated through file exports to Microsoft 365. With 17 specific skills the AI drafts quotes from actual inventory, compares suppliers, generates quality reports and design variants, and analyzes sensor data and manuals during machine downtime. Via an added Infor plugin Claude can order from backup suppliers when deliveries are delayed and reschedule production after human approval. All results are linked to original source documents for employee review before reaching customers or suppliers. The plugin is available to Team and Enterprise customers but does not control physical machines yet. For that Anthropic is separately developing the Model Hardware Standard as a research preview, connecting AI agents to devices like robotic arms and microscopes via standardized drivers, cutting setup time from weeks or months to hours or minutes, though it still requires human oversight due to limited grasp of physical processes.'),
    ('The Decoder - Nearly 70 percent of US agencies use generative AI, unions catching up with guardrails (2026-11-13)',
     'industry', 'us-public-sector-unions-ai-guardrails',
     'US public-sector unions are winning more protections against AI surveillance and automation-driven job losses, an issue growing more urgent as nearly 70 percent of US government agencies already use generative AI according to an Ernst and Young survey. After a strike vote in October, IFPTE Local 21 in Oakland secured retraining programs instead of AI-related layoffs. In Pennsylvania, Governor Josh Shapiro guaranteed SEIU Local 668 human oversight during a pilot of OpenAI ChatGPT Enterprise. The Transport Workers Union in Ohio won veto power over autonomous vehicles. California Governor Gavin Newsom banned AI surveillance software, often called bossware, along with automated firings in September. New York has protected state employees from AI displacement by law since late 2025. Employers are pushing automation to cut costs according to labor researcher Kung Feng at UC Berkeley. Union leaders including AFL-CIO Liz Shuler, Lorena Gonzalez and TWU John Samuelsen support AI safety systems where they help workers but insist on mandatory human control over every AI application in the workplace.'),
    ('The Decoder - Nvidia Blackwell fingerprints found inside six Chinese AI models (2026-11-13)',
     'research', 'nvidia-blackwell-fingerprint-chinese-models',
     'AI researcher Will DePue says a forensic analysis has turned up the first technical evidence that leading Chinese AI labs have access to Nvidia latest Blackwell hardware despite US export controls, and that senior researchers at OpenAI and Anthropic have already checked the method. DePue played a key role at OpenAI building the Sora and Sora 2 video models as well as GPT-4o, o3 and GPT-5 before founding the nonprofit research group Unemployment Labs. The evidence comes directly from published language models, because before training starts PyTorch fills empty weight slots with random numbers generated from a seed, and because different chip models have different core counts the filling process produces a characteristic pattern. Older Hopper chips such as H100 and H800 use 132 compute cores while newer Blackwell chips use exactly 148 or 152 cores depending on model, with B200/B300 using 148 and GB200/GB300 using 152. Training adjusts these values millions of times but some slots for unused words keep their initial random values, leaving a faint statistical echo. DePue reproduced the results for DeepSeek-V4-Flash and Kimi K3 exactly on real Blackwell chips and published the verification code on GitHub. The analysis maps DeepSeek-V4-Flash and MiniMax-M3 to B200 or B300, while DeepSeek-V4-Pro, Kimi K3, Kimi K3.1-Pro and Ant Group Ling-3.1-flash show the 152-core pattern of GB200 or GB300 flagship liquid-cooled racks. Earlier models such as DeepSeek-V3 and Kimi K2.5 show traces of the older Hopper generation. The method correctly identified all 24 control models with known hardware, including Meta Llama 3.1 on H100.'),
    ('The Decoder - Anthropic IPO six times oversubscribed, on track to be largest offering in history (2026-11-13)',
     'industry', 'anthropic-ipo-6x-oversubscribed-1-4t',
     'Anthropic is on track for the largest IPO ever, with orders exceeding available shares by a factor of six, according to Bloomberg. The Claude developer and its co-founders aim to raise up to 64.4 billion dollars through the public offering and another 26 billion via a private placement, which would surpass even SpaceX IPO. The target valuation sits at roughly 1.4 trillion dollars, with existing investors getting priority in share allocation. Anthropic annualized revenue climbed to 81 billion dollars by late October, up from 71 billion in September. Nvidia, whose investors have grown more cautious since CEO Jensen Huang was ousted over an alleged espionage scandal, is itself buying 10 billion dollars in Anthropic stock through the private placement. Goldman Sachs and Morgan Stanley are managing the Nasdaq listing under the ticker ANT, and CEO Dario Amodei will pitch investors alongside JPMorgan CEO Jamie Dimon in a Friday livestream.'),
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
if os.path.exists('scout-raw/hn-items-1114.json'):
    for x in json.load(open('scout-raw/hn-items-1114.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-14-corpus.md',
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
