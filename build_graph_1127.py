import json, os, re, hashlib, glob

STAMP = '2026-11-27'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = "2026-11-26"


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1127.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1127.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1127.json', 'MCP')]
new_ids = set(x.get('id_base') or x['id'].split('v')[0] for x in json.load(open('scout-raw/arxiv-1127-newids.json')))
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
    ('scout-raw/gh-1127-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1127-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1127-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1127-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1127-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1127-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1127-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1127-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1127-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1127-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1127-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1127-*-commits.json')):
    label = f.split('gh-1127-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1127-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1127-registry-advisories.json', 'mcp-registry')]:
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
    ('US export controls halt Nvidia server shipments to four Southeast Asian countries and push thousands of B300 chips into the secondary market',
     'industry',
     'nvidia-halts-sea-shipments-b300-secondary-market',
     "The Financial Times reported that Nvidia told manufacturing partners including Dell and Supermicro to halt server shipments to Malaysia, Singapore, Thailand and Indonesia, following tighter Commerce Department Bureau of Industry and Security rules designed to close the cloud loophole through which Chinese companies rented advanced Nvidia chips from foreign data centres. US Trade Representative Jamieson Greer told CNBC the goal was to block indirect access including smuggling through Southeast Asia and remote access via third-country data centres. Southeast Asian cloud providers now have 90 days to apply for a licence, an executive said had led to chaos, and banks have already halted about 500 million dollars in loans to Singapore-based provider Aolani for a planned ByteDance deal. The second-order effect is larger than the halted shipments: GPU Mart's Jack Duhamel confirmed to CNBC that dealers have listed an unusually large number of Nvidia GPUs for sale since the announcement, including thousands of B300 chips originally intended for data centres with Chinese rental customers. The signal for this series is that controls are now enforced at the reseller and cloud-licence layer rather than at the manufacturer, and that the enforcement mechanism is an enforcement of who may rent rather than who may buy.",
     ),
    ('Chinese frontier labs visibly slow: GLM-5.5 slips to Q1 2027, Moonshot development cycle doubles to 12 months, and training data pivots to Google and Meta',
     'industry',
     'china-labs-slowed-export-curbs-distillation-and-data-pivot',
     "Reuters reported, citing sources, that Z.AI's roughly 3-trillion-parameter GLM-5.5, planned for November, is likely to slip into the first quarter of 2027, with the company bridging the gap by releasing the 750-billion-parameter GLM-5.4 on Monday and claiming a new design lets it keep up with systems of 2 to 3 trillion parameters. Without foreign computing power, Moonshot AI's development cycle could double from six to 12 months, likely delaying Kimi K4 until mid-2027, and with OpenAI and Anthropic blocking data scraping for distillation, Moonshot is turning to the latest Google and Meta models for training while stepping up its search for compute capacity in Europe. The Information separately reported that Deepseek internally estimated its gap to top US models could grow from three to six months to nine months if distillation disappears completely, that Moonshot cancelled a 150 million dollar Blackwell deal in Indonesia, and that MiniMax, miHoYo and Alibaba are leaning more heavily on domestic chips and on training data for their own reinforcement learning. Two different mechanisms are now confirmed at once, on the compute side and on the data side, which is the first window where the chip constraint and the distillation constraint are measured together rather than separately.",
     ),
    ('Microsoft documents ARTEX, where specialised AI agents run automated cyberattacks at machine speed and switch language models on failure',
     'industry',
     'microsoft-artex-autonomous-cyberattack-agents',
     "Microsoft Threat Intelligence published an analysis of ARTEX, an AI-powered penetration-testing framework released in July 2026 whose source was published by GitHub user Autumn-27 and deleted in October, with copies still distributed elsewhere and a commercial Pro version sold by the Chinese security firm ThreatBook. Microsoft says state-backed groups from China and North Korea have integrated ARTEX into operations including Salt Typhoon, Crystal Typhoon, Onyx Sleet and Storm-0940, and that financially motivated groups use it for supply-chain attacks. The framework distributes attack tasks on its own, switches between language models when something fails, drives existing tools such as Metasploit, and operates at machine speed, leaving defenders minutes to respond; it was recently suspected in the intrusion into an analytics system run by the CIA, NGA and ODNI, which surfaced shortly before FinCEN reported a security incident, with FBI and Department of Agriculture incidents earlier. Microsoft's recommended defence is deception rather than blocking, specifically decoy systems and faked success signals that trick the attacking agent into calling off an attack. The structural point is that the attacker now has a per-task cost close to zero and an adaptive model-routing capability, while the defender's lever is behavioural rather than a signature.",
     ),
    ('OpenAI begins piloting Private Inference, processing queries on independently verifiable isolated hardware so enterprise data is never read or retained',
     'industry',
     'openai-private-inference-pilot',
     "CEO Sam Altman said OpenAI is piloting the previously announced Private Inference offering with its first enterprise customers, describing it as a first step toward private intelligence for everyone, and OpenAI is scaling compute capacity for it. Queries are processed on specially isolated hardware whose security can be independently verified, and a companion Private Safety Processing system lets OpenAI scan for abuse without storing customer data, with flagged content encrypted and stored in the customer's own cloud and readable only by a secured review system. The scope is business customers, whose data OpenAI already does not train on; consumer ChatGPT conversations are still used for training by default unless users opt out. Google is pursuing a similar approach with Private AI Compute. This continues the enterprise-adoption thread tracked across recent windows, where the binding constraint on deployment has been trust and review rather than capability, and it pairs with the 1Password incident in the same window, where a breach reached backend account records but explicitly not vault contents.",
     ),
    ('1Password discloses a backend breach that reached account records and private source code, and states that vault contents were never accessed',
     'industry',
     '1password-backend-breach-vaults-intact',
     "1Password disclosed an incident in which an attacker executed malicious code against backend services and downloaded administrative data including customer names and email addresses, account and user identifiers, account creation and last sign-in times, public keys, SRP parameters, tokens present in certain emailed invitation, provisioning and recovery links, and non-secret internal metadata. The company states that at no time were customer vault contents accessed by or available to the attacker, and that the keys protecting vaults were not affected. The attacker also copied source code from private repositories and gained access to the CI/CD system, which contains infrastructure secrets; 1Password has triggered rotation of all credentials that may have been exposed and states there is no impact to availability or product security. Because invite and recovery tokens had to be combined with an SSO sign-in or a six-digit emailed code, the company expanded that code from six numeric digits to ten alphanumeric digits. The case is a useful calibration point for agentic threat models: the blast radius stopped exactly at the boundary the architecture was designed to hold, but the adjacent systems, source code and CI, were fully reachable.",
     ),
    ('Amodei argues AI governance is a bad idea in the same terms he uses against autocracy, while endorsing task automation in bounded domains',
     'industry',
     'amodei-ai-governance-bad-idea-democratic-legitimacy',
     "In a lengthy post on X, Anthropic CEO Dario Amodei responded to an Axios report that some Anthropic employees believed humanity would safely hand authority to superintelligent systems, and often should, rather than fight for control. He wrote that AI must be governed by legitimate democratic processes, that political decisions should stay in human hands, and that handing over governance to AI is a bad idea in the same way he argues against autocracy, adding that we should never sacrifice legitimacy or self-determination on the altar of efficiency or security. He accepted that automating specific tasks such as driving, developing cancer drugs and writing software could benefit humanity and save lives, but warned of end-to-end automation bringing job disruption and models building new models without human oversight, and that humans would simply prefer to do some activities themselves to stay engaged. He also noted that other AI CEOs repeat human-control slogans while shipping more automation, and said Anthropic refused to allow its existing models to be used for autonomous weapons during its dispute with the Pentagon, willing to risk the company over it. The distinction being drawn is between automating tasks and delegating governance, which is a sharper version of the delegation-versus-review split this series has been tracking.",
     ),
    ('Amazon and Meta negotiate over Muse as shopping agents reach 51 percent of agentic orders and ads worth 68.6 billion dollars are the sticking point',
     'industry',
     'amazon-meta-muse-agentic-commerce-ads',
     "Amazon and Meta are in talks to end the block on Meta's AI shopping agent Muse in Amazon's online store, with ad revenue and control over search results the main sticking points per Fortune. Amazon worries that shopping agents like Muse could weaken its relationship with customers and bypass the ads on its platform, a business worth 68.6 billion dollars a year, and CEO Andy Jassy said shopping through third-party agents so far has not been more convenient or better than going directly to a retailer, though he did not rule out opening access; any deal would need sign-off from both CEOs. Amazon previously blocked Perplexity and the US appeals court later allowed Perplexity's agent back. Muse is Meta's most successful consumer AI product with more than 10 million users in the US and Canada, and Meta is already seeing Instagram ad gains because Muse helps users organize saved products. Forter Intelligence data has Muse at 51 percent of all agentic orders, Grok at 24 percent and ChatGPT at 22 percent. The interesting number is the 51 percent, because it means the agentic channel has become the primary demand-side surface and the platform's ad business is now structurally exposed to it.",
     ),
    ('FCC clears SpaceX for up to 1 million satellites carrying orbital AI data centres, with radio links as optical fallback',
     'industry',
     'fcc-spacex-1m-starmind-orbital-ai-datacenters',
     "The Federal Communications Commission has authorized SpaceX to deploy up to 1 million satellites for orbital data centres, according to Reuters. The Starmind constellation of orbital compute modules is intended to meet part of the growing demand for AI computing power on Earth, and the FCC also approved radio links that let SpaceX monitor and control the satellites if their optical connections fail. This is a capacity-side answer to the compute constraint that dominates this window's other stories: the same week that export controls closed one route to advanced chips, a regulator cleared a route to move compute off the planet entirely. The scale of the authorization, one million spacecraft, is far beyond any launched constellation and sits with the physical limits of launch cadence and orbital debris rather than with semiconductor supply.",
     ),
    ('OpenAI claims the matrix multiplication exponent is exactly 9/4 and a matching lower bound on Fourier-transform gate count, and a researcher reacts with open astonishment',
     'science',
     'openai-matrix-multiplication-omega-9-over-4-and-fourier-lower-bound',
     "Scott Aaronson wrote that after OpenAI's and Anthropic's proofs of VP not equal VNP, and hot on the heels of the Alpage and Anthropic proof of the Riemann hypothesis, OpenAI claimed that the exponent of matrix multiplication omega is exactly 9/4, a lower bound matching the upper bound OpenAI proved in the October 6 Mathocalypse drop. He said the first shock is that the answer to a central mystery of algorithms dating to Strassen in the late 1960s is a rational number, and that the AI was able to prove a lower bound of the form omega greater than 2, which he had never expected to be much easier than P not equal NP. During dessert, a further OpenAI release proved the true number of linear gates needed to compute the Fourier Transform is N log N to the one half plus o(1), improving on the FFT bound from the 1960s and on OpenAI's own October release, with a matching lower bound. The HN thread reached 1823 points. The verification-economics thread from prior windows continues to apply, since the earlier window already established that a machine-checkable artifact can still be unreadable, and the review cost of a 17-million-line proof is the part that does not scale with the claim.",
     ),
    ('GPT-6.2 Astra is the first model to beat Googlers 2015 code-golf records, on 32 problems in 8 languages scored by byte count, and OpenAI simultaneously tightens usage limits',
     'engineering',
     'gpt62-astra-codegolf-records-and-usage-limits',
     "bjin revived an internal Google code-golf site from 2015 as a benchmark: 32 problems, 8 languages, 256 cells, each model given 30 minutes per problem in each language to make its solution as short as possible, scored by byte count rather than by whether the code works, against the oracle of the known best and the recorded human records. The leaderboard on HN at 434 points reports that GPT-6.2 Astra is the first model to beat Googlers' own records. Separately in the same window, a thread reporting OpenAI cutting GPT-6.2 usage with Astra hitting limits 40 percent faster and Sol 25 percent faster reached 415 points. The pairing is the substantive part: a benchmark whose scoring function is byte count with a hard human record to beat is unusually resistant to the reward-hacking and grader-manipulation problems that this series has flagged in agent benchmarks, because the grader is a rule-based byte comparison, and it is being used exactly as the field is being told to price frontier capability against a measured frontier artifact.",
     ),
    ('arXiv publishes 176 new papers, and the strongest signals are that agent patches are not mostly over-editing, that memory hallucination is a use-time conflict, and that benchmarks now measure coverage rather than a score',
     'engineering',
     'arxiv-176-new-patch-necessity-memory-hallucination-and-coverage-benchmarks',
     "The arXiv API returned the 11-25 batch, and comparing against all 2334 historical ids confirms 176 genuinely new papers, with the published-date histogram led by 11-25 at 196 entries then 11-24 at 37, 11-23 at 47, 11-22 at 30, 11-21 at 26, 11-20 at 40, 11-19 at 11 and 11-18 at 13. Theme counts by keyword: eval-bench 113, coding-agent 42, planning-reasoning 39, multi-agent 26, rl-training 25, agent-safety 23, memory 20, security 18, interpretability 18, tool-use 8, MCP 2. Five papers carry most of the signal. How Much Do Coding Agents Over-Edit introduces Delta Residue Attribution, replaying 7,660 resolved GitHub Copilot CLI trajectories from 18 frontier models on SWE-bench Verified and DeepSWE, reverting each unit of the final patch and rerunning tests to decide whether the unit is needed; agent patches do change more lines than developers', but on SWE-bench Verified most extra edits add tests (61 percent) and documentation (13 percent) while on DeepSWE most extra edits are code (58 percent), agents' code is on average at least as necessary as developers', 11 percent of an agent patch code units on SWE-bench Verified are still unneeded and 89 percent of those change behavior, and code necessity is unrelated to resolve rate on SWE-bench Verified while negatively correlated on DeepSWE at Spearman -0.59. TASK Memory finds use-time memory hallucinations across five open models, with memory-ignoring up to 46 percent of queries, memory-misapplying up to 24 percent and 49 percent when retrieval is combined with weight editing, and version confusion at 53 percent, addressed by combining a text note with activation steering and knowledge editing. Solve Vision with Code poses identical visual-reasoning tasks to video models and to coding agents that render the answer video, on a 500-instance suite with symbolic ground truth, and finds coding agents are the stronger visual reasoners. SPLICE addresses the all-fail group problem in group-based RL on long-horizon agent tasks by splicing learner-conditioned options into failed current-policy trajectories instead of importing complete solutions from a stronger model. HoMe treats the memory harness, code prompts and configuration for construction maintenance retrieval and generation, as an optimizable artifact, with session-level memory versioning and execution traces to localise shared failure mechanisms. And Tune for Retention challenges the premise that SFT is inherently prone to catastrophic forgetting, showing that jointly choosing hyperparameters for gain and retention lets vanilla SFT retain prior capabilities far better than previously suggested.",
     ),
    ('GitHub ships 7 new tags, all of them dependency bumps, while commit volume holds at 85 and GHSA stays flat for a fifth window',
     'engineering',
     'github-7-new-tags-all-dependency-bumps-ghsa-flat-fifth-window',
     "Across 11 tracked repositories 7 new tags appeared, all on 2026-11-26: openai-python v3.60.0, and six vercel/ai packages, ai@5.0.294, ai@6.0.338, ai@7.0.183, and @ai-sdk/zai@1.0.14, @ai-sdk/zai@2.0.24 and @ai-sdk/zai@3.0.59. All six vercel/ai releases are dependency-only patch bumps with no functional change, driven by a single upstream commit 80d778a updating @ai-sdk/provider-utils to 5.0.85 and @ai-sdk/gateway to 4.0.156. Commit activity was 85: vercel/ai 20, anthropics/anthropic-sdk-python 20, anthropics/claude-code 20, openai/openai-python 18, modelcontextprotocol/modelcontextprotocol 7, and modelcontextprotocol/servers 0. The openai-python v3.60.0 release body is the substantive part even though the version bump is small: it adds spend alerts and response compaction fields, supports updating session vaults, clarifies message retries and Batch endpoints, clarifies Realtime audio noise reduction, and documents inline skill upload limits. The GHSA advisory feeds returned zero growth for a fifth consecutive window, with MCP servers at 29 advisories and MCP registry at 5, and MCP servers shipped zero commits in the window, which is the first fully silent repo in the tracked set.",
     ),
    ('The window turns on a three-way split: chip controls and data controls are now binding on frontier capability, the attacker marginal cost is falling to machine speed, and evaluation is moving toward coverage and necessity rather than a score',
     'trend-analysis',
     'trend-constraints-bind-on-both-sides-eval-shifts-to-coverage-and-necessity',
     "Three constraints bound this window's frontier capability simultaneously and from both sides. On the supply side, Nvidia halted server shipments to four Southeast Asian countries under rules designed to close the cloud rental loophole, pushing thousands of B300 chips into the secondary market, and in the same week Reuters reported GLM-5.5 slipping to Q1 2027 and Moonshot's cycle doubling to 12 months, with Chinese labs losing distillation data and pivoting training to Google and Meta models. On the security side, Microsoft's ARTEX analysis documents autonomous attacking agents that redistribute tasks, switch language models on failure and run at machine speed, with defenders pushed toward deception and fake success signals, and 1Password disclosed a breach that reached backend account records and private source code while vault contents held, showing that the boundary the architecture was designed to hold did hold. On the evaluation side, Delta Residue Attribution measured what 7,660 agent trajectories across 18 models actually changed and found that agents are not mostly over-editing, with 89 percent of unneeded code units still changing behaviour, DRBench Pro makes structured knowledge coverage the primary target for deep research agents, and the code-golf benchmark scores byte counts against 2015 human records, which is close to unhackable by comparison with the agent benchmarks that scored near-perfect without solving the tasks. The common thread is that every credible measurement this window is of a countable property, lines changed, bytes written, vulnerabilities fixed, orders routed, chips withheld, accounts exposed, rather than of model quality in the abstract, and that the two sides of the market, frontier labs and the attackers, are both now operating under explicit physical and legal constraints rather than under capability constraints.",
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
if os.path.exists('scout-raw/hn-items-1127.json'):
    for x in json.load(open('scout-raw/hn-items-1127.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-27-corpus.md',
    'node_count': len(nodes),
    'edge_count': len(links),
    'arxiv_count': arxiv_count,
    'release_count': rel_count,
    'commit_count': com_count,
    'advisory_count': adv_count,
    'news_count': news_count + hn_count,
    'previous_snapshot': 'graphify-out/' + PREV,
    'next_window': '2026-11-28T00:30+08:00',
}
json.dump(manifest, open(OUT + '/manifest.json', 'w'), ensure_ascii=False, indent=1)
print('nodes', len(nodes), 'links', len(links), '| arxiv', arxiv_count, 'releases', rel_count,
      'commits', com_count, 'advisories', adv_count, 'news', news_count + hn_count)
