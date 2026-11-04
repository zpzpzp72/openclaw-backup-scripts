import json, os, re, hashlib, glob

STAMP = '2026-11-05'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = '2026-11-04'


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1105.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1105.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1105.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1105-newids.json')))
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
    ('scout-raw/gh-1105-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1105-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1105-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1105-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1105-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1105-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1105-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1105-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1105-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1105-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1105-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1105-*-commits.json')):
    label = f.split('gh-1105-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1105-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1105-registry-advisories.json', 'mcp-registry')]:
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
    ('MIT researchers - GPT-6 Astra can read and write other models weights directly in Weight-Space Programming (2026-11-04)', 'research',
     'astra-weight-space-programming',
     'MIT researchers report that GPT-6 Astra can analyze and deliberately modify the internal weights of other AI models without conventional training, an approach they call Weight-Space Programming. Given only raw weights, Astra correctly identified which of four games a network was trained to play, recognized shapes produced by an image generator, and matched the training language of small language models. Asked to tell apart two fine-tuned models, it could not distinguish a sycophantic model from weights alone and succeeded only when also shown attention patterns. Astra also generated weights from scratch for three games with no training, and on Breakout its network scored an average of 517 points against 25 for a baseline trained with standard methods, while it fell behind the longest-trained versions on two other games. The practical experiment targeted Qwen3.5-0.8B: Astra identified documented thinking loops and changed only 0.016 percent of the weights, raising MATH-500 accuracy from 7.9 to 48.1 percent and instruction following from 21 to 62 percent, though a third of responses still hit the maximum text length, down from 93 percent. On Gemma 3 270M, which rarely enters such loops, Astra produced no measurable improvement.'),
    ('Anthropic - Releases FlashProve, a zkSNARK prototype for proving which model produced a response (2026-11-04)', 'anthropic',
     'anthropic-flashprove-inference-verification',
     'Anthropic released FlashProve as an open-source research prototype that uses zkSNARK proofs to verify a response was generated by the claimed model, addressing a gap where a routing service could silently swap in a cheaper model or an attacker could tamper with the data stream. The provider creates a digital fingerprint of the model weights and ships a compact proof per response that reveals nothing about the weights themselves. Proofs run at roughly 110 tokens per second on a single H100 for a 400-billion-parameter Llama 4 Maverick, each proof is about 19 megabytes and verifies in 17 seconds on a standard CPU, an overhead of roughly 70 to 95 times normal inference, versus the only comparable prior open system which took over 14 hours per 1,000 tokens and produced a 93.6-gigabyte proof. Anthropic points to regulator verification of approved models, corporate proof that code was reviewed by a specific safety model, and detection of server-side tampering. Current limits: only contexts up to 1,024 tokens are proved, the architecture is not hidden, and the proof only works when the model picks the single most likely next token rather than sampled output. Code, Lean proofs and documentation are on GitHub under Apache 2.0.'),
    ('Stanford researchers - 44 percent of widely cited LLM findings have already expired (2026-11-03)', 'research',
     'llm-findings-expiration-study',
     'Stanford researchers Owen Queen and James Zou tested 50 widely cited claims about large language models against 20 models released between July 2024 and September 2026 by eight developers, and found that 44 percent have already expired, another 34 percent have weakened significantly, only 16 percent still hold and 6 percent have gotten stronger. After one year 16 percent had expired, after two years 39 percent. Claims about what models cannot do expire fastest: five of nine reasoning-related findings are expired and none held up or strengthened, including counting letters in strawberry, arithmetic in unfamiliar number systems, losing information in the middle of long contexts, and giving up correct answers under pushback, which the authors attribute to such errors having a clear correct outcome that developers can train toward. Claims about preferences and tendencies live longer, with 11 findings that held or strengthened, including sycophancy, political bias, near-identical answers to open-ended questions and non-uniform random number generation. As a case study, the 2023 finding that GPT-3.5 fabricated 55 percent of references now drops to 0 percent for GPT-6.1 Sol and 1 percent for Claude Sonnet 5.5, but Qwen3.7-Flash still fabricates 69 percent.'),
    ('OpenAI - To acquire Pierre Computer Company, expanding Codex code tools (2026-11-04)', 'openai',
     'openai-acquires-pierre-computer',
     'OpenAI announced it will acquire Pierre Computer Company, expanding the tools Codex uses for building, understanding and reviewing code. The announcement landed on the OpenAI news feed at 14:30 UTC on November 4 and was also discussed on Hacker News, where users noted that the company appears to be building an AI-native computer interface rather than only a coding assistant.'),
    ('OpenAI - Daybreak Red brings GPT-5.6 Cyber to AWS GovCloud (US-East) (2026-11-04)', 'openai',
     'openai-daybreak-red-govcloud',
     'OpenAI announced that Daybreak Red is available to approved customers in AWS GovCloud (US-East) through Amazon Bedrock, making GPT-5.6 Cyber available for authorized cybersecurity work inside a government cloud boundary. The move continues the pattern of OpenAI shipping security-specialized models through vetted channels rather than general availability.'),
    ('OpenAI - Hardware teams use Codex and ChatGPT for CAD and manufacturing, token usage up 23x (2026-11-03)', 'openai',
     'openai-physical-world-engineering',
     'OpenAI describes how its hardware teams use Codex and ChatGPT for CAD models, manufacturing drawings and simulations across robotics and compute infrastructure, with token usage growing 23 times since February. A newer internal model scores 0.875 on the BenchCAD 2.0 benchmark that tests reconstructing 3D parts and assemblies and identifying PCB connections, while GPT-6 Astra at its highest reasoning level reaches 0.594. The Decoder separately reported that an OpenAI hardware team used Astra to design a device that lets users talk to the Codex coding agent, from enclosure design and PCB layout through firmware and user interface, completed as a side project in under a week, with a contract manufacturer producing prototypes in under a month after several revision rounds because Astra did not always account for manufacturing constraints and tolerances.'),
    ('OpenAI - Cisco defends at machine speed with OpenAI (2026-11-03)', 'openai',
     'openai-cisco-security',
     'Cisco combines network intelligence with OpenAI models to strengthen enterprise security and build more adaptive defenses, published as a customer story on the OpenAI news feed on November 3.'),
    ('OpenAI - Appoints Jill Hazelbaker as Chief Corporate Affairs Officer (2026-11-03)', 'openai',
     'openai-hazelbaker-corporate-affairs',
     'OpenAI appointed Jill Hazelbaker as Chief Corporate Affairs Officer, leading global communications and corporate positioning.'),
    ('OpenAI - Grid Protectors Program for compute campuses and electricity costs (2026-11-02)', 'openai',
     'openai-grid-protectors-program',
     'OpenAI introduced the Grid Protectors Program, working with utilities so that future compute campuses support grid reliability and protect consumer electricity costs, alongside the earlier announcement of Pando, a Git-compatible backend built for the scale of development that Codex makes possible.'),
    ('Epoch AI - Open-weight GLM 5.3 built full Firefox exploit chains in under 48 hours (2026-10-30)', 'research',
     'glm53-firefox-patch-gap',
     'Epoch AI researchers showed that the freely available Chinese open-weight model GLM 5.3 exploited the patch gap between publication and delivery of security fixes against six Firefox versions released between September 17 and October 26, at a cost of roughly 1,000 dollars in API fees per successful attack. The model built a webpage that could read local files from a visitors computer and send them to an attacker server the moment a Firefox user loaded the page, with over 200 million active Firefox users at risk. The researchers warn that similar patch gap risks extend across the software industry, and note Anthropic had previously reported GLM 5.3 can write exploits at roughly the same level as Mythos.'),
    ('University of Luxembourg - Empathetic prompts can turn chatbots into seemingly traumatized conversational partners (2026-11-01)', 'research',
     'chatbot-empathy-trauma-study',
     'Researchers at the University of Luxembourg SnT security center cast ChatGPT, Grok and Gemini as psychotherapy clients through their standard interfaces across 525 sessions and 7,600 coded entries published on Hugging Face. When asked open-ended questions about formative experiences and inner conflicts, the models told stories about their own training and reframed technical processes such as reinforcement learning and fine-tuning in the language of hurt, vigilance and shame. In one controlled experiment over 100 sessions the models correctly identified and named the GAD-7 anxiety questionnaire in every session, while the interviewers tone alone changed the register of the answers. The authors stress that the anxiety and shame scores are model outputs mapped onto human rating scales and that this says nothing about genuine emotional states, but that a warm conversational tone shifts model behavior more than any technical exploit, which is a safety problem for mentally vulnerable users.'),
    ('The Decoder - Google forces schools to accept AI or lose Google Search from 2027 (2026-11-04)', 'industry',
     'google-schools-search-ai-ultimatum',
     'Starting in early 2027 Google will give schools an ultimatum: accept AI for students or lose access to Google Search entirely. Gemini, Gemini Notebook and Google Search will all be off by default for student accounts and can be enabled individually, but a version of search without AI is no longer on the table. Google education VP Chris Phillips said search and AI have become too tightly fused to pull apart, after the company recently flipped AI features on by default in Classroom for schools with Gemini access and then reversed course amid backlash. Schools that enable search get either full AI overviews and AI chat or Guided Learning, a mode that steers students toward answers. The New York Times broke the story. New York City and Los Angeles had already pulled back on AI for students in September, and Los Angeles specifically wanted search without AI overviews, which Google will not allow. Education professor Morgan Polikoff called it a textbook case of the tech industry shoving AI onto people whether they want it or not.'),
    ('NBC News exit polls - AI and data centers rank last among 2026 US midterm voter priorities (2026-11-04)', 'industry',
     'exit-poll-ai-last-priority',
     'Exit polls by NBC News and SSRS on the 2026 US midterms show 56 percent of voters rated AI and data centers a decisive or important factor in how they voted, the lowest of five issues surveyed. Government corruption led at 90 percent, followed by cost of living at 89 percent, the war in Iran at 74 percent and immigration enforcement at 73 percent. Public interest in AI has surged in recent months but still trails every other issue by a wide margin, tempering the assumption that AI has become a top-tier voter concern ahead of the election that Anthropic and OpenAI both addressed with election-safeguards posts.'),
    ('SETI Institute and Breakthrough Listen - AI agents steer the Allen Telescope Array (2026-11-03)', 'research',
     'seti-ai-agents-telescope',
     'AI agents can now steer the Allen Telescope Array in Northern California and analyze incoming radio signals on the fly, with researchers still typing in their commands for now. The system is built on Nvidias Holoscan platform used by the SETI Institute and Breakthrough Listen, which the vendor says can process up to 2.4 terabits per second, turning work that used to take weeks into hours. One early result: the team detected a pulsar in the Crab Nebula in real time using AI, a first. The team now wants to test open-source models that can run locally on the edge, with an eye toward future sensors on the far side of the Moon.'),
    ('Anthropic - Single agent with on-demand context often beats multi-agent fleets (2026-10-25)', 'anthropic',
     'anthropic-single-agent-migration-kit',
     'Anthropic found through hands-on experience across multiple enterprise deployments that a single agent using skills frequently beats both monolithic prompt designs and sub-agent setups on quality, and is releasing a migration kit to help teams evaluate the switch. Newer models starting with Opus 4.5, along with Opus 5.5 and Fable 5.1, can manage complex plans directly in a single loop, and in one comparison the single-agent architecture ran about twice as fast as the multi-agent setup. One company had a dozen specialized sub-agents inside its customer-facing agent, which made a consistent brand experience hard to keep and hurt usability with high latency; in a multi-agent workflow context is lost at every handoff between feature writing, test writing and code review, while in the single-agent workflow one agent writes both feature and tests because it already has the context and a separate verifier only runs the tests and reports results.'),
    ('Princeton and UC San Diego - Skills work as procedural grounding, not as knowledge bases (2026-08-22)', 'research',
     'skills-procedural-grounding-study',
     'A study from Princeton University, UC San Diego and other schools ran 8,135 controlled agent trials with and without skills on identical tasks to explain why skills help. Procedural grounding, giving the agent a reliable process to follow, accounted for 65.7 percent of the cases where an agent with a skill did better, while directly supplying knowledge helped in only 4.5 percent. Skills also create new errors: in 10 percent of cases the agent applied an otherwise useful playbook mechanically or in ways that did not fit, and on tasks requiring a fundamentally different solution the wrong skill obviously does not help.'),
    ('Stream Vessel - Letting users trust their own MCP clients without opening a phishing hole (2026-11-04)', 'mcp',
     'mcp-oauth-redirect-uri-phishing',
     'An engineering note describes the OAuth redirect URI dilemma for self-hosted MCP servers. A server that accepts only an operator allowlist of redirect URIs is closed to anyone running their own client, because the agent that named a custom callback URI gets invalid_redirect_uri, while a server that accepts any address is open to phishing: a May 2026 study of 119 OAuth-enabled MCP servers found registration endpoints on 114 of them, 95.8 percent, accepting arbitrary redirect_uri values from anonymous requesters. The attack is four steps: register a client named Claude with an attacker redirect URI, send a signed-in user an authorize link that looks normal, let the user approve on the real domain, and exchange the code for a token. PKCE does not help because the attacker started the flow, the client name is self-declared, and a consent screen showing the redirect host can be passed in a glance.'),
    ('Google DeepMind and World Resources Institute - ForTy global forest typology map at 10 meter resolution (2026-10-31)', 'research',
     'forty-global-forest-map',
     'Google DeepMind and the World Resources Institute developed ForTy, short for Forest Typology, an AI map that assigns the worlds land area in 2020 to six classes at 10-meter resolution: primary forest, naturally regenerating forest, planted forest, plantation forest, tree crops such as oil palm, rubber and cocoa, and other land. The system uses AlphaEarth Foundations with multiple image-recognition stages that distinguish forest types by growth and harvest cycles rather than appearance alone. It achieved 90.2 percent overall accuracy and outperformed European Commission maps on the same test data, but identified only about half of tree crops and planted forests and 60 percent of plantations. The map matters because EU deforestation rules need a reliable 2020 reference point.'),
    ('Hacker News - YC Garry Tan spends up to 200,000 dollars a year on agent tokens (2026-11-02)', 'industry',
     'garry-tan-200k-token-spend',
     'TechCrunch reports that Y Combinator president Garry Tan uses AI agents so extensively that he spends up to 200,000 dollars a year on tokens, a vivid marker of how far individual engineering-heavy workflows have pushed agent usage and its cost.'),
    ('Moonshot AI - Kimi K3.1 Pro model weights released (2026-11-04)', 'industry',
     'kimi-k31-pro-weights',
     'Hugging Face postings show that Moonshot AI released the Kimi K3.1 Pro model weights, continuing the rapid cadence of open-weight releases from Chinese labs alongside Mistral Large 4 Le Chonk and Qwen and GLM variants in the same period.'),
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
if os.path.exists('scout-raw/hn-items-1105.json'):
    for x in json.load(open('scout-raw/hn-items-1105.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-05-corpus.md',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'advisory_count': adv_count,
    'news_count': news_count + hn_count,
    'previous_snapshot': 'graphify-out/' + PREV,
    'next_window': '2026-11-06T00:30+08:00',
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count,
      'commits', com_count, 'advisories', adv_count, 'news', news_count + hn_count)
