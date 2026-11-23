import json, os, re, hashlib, glob

STAMP = '2026-11-24'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = "2026-11-23"


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
arxiv_files = [('scout-raw/arxiv-csAI-parsed-1124.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-parsed-1124.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-parsed-1124.json', 'MCP')]
new_ids = set(x['id'] for x in json.load(open('scout-raw/arxiv-1124-newids.json')))
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
    ('scout-raw/gh-1124-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1124-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1124-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1124-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1124-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1124-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1124-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1124-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1124-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1124-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1124-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1124-*-commits.json')):
    label = f.split('gh-1124-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1124-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1124-registry-advisories.json', 'mcp-registry')]:
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
    ('Z.ai ships GLM-5.4, a 750B flagship on a loop architecture that runs 28 layers twice',
     'industry',
     'glm-5-4-loop-transformer-750b',
     "Z.ai introduced GLM-5.4, a 750-billion-parameter model built on a loop transformer that runs a block of shared layers twice, following OpenAI's GPT-6 Astra. According to Z.ai the model reaches performance comparable to models with 2 to 3 trillion parameters. The conversion from the February GLM-5 base model introduced a control problem: if the model simply overwrote intermediate states on each pass, activations would grow sharply and leave later layers outside their trained range. GLM-5.4 uses dedicated gates per token and per pass, building context cautiously on the first pass and writing changes back in full on the second, with the first pass stepping in more strongly on difficult tokens. Layers 27 through 54 run twice, both passes share the KV cache with the second pass storing extra values only in a small local window, and sparse attention selects relevant earlier tokens once and reuses that selection in the second pass, which Z.ai says gives nearly the same result as selecting separately. Throughput is up to 200 tokens per second off-peak and 70 to 80 under load. Crucially the only published numbers come from a 30B test model: with the same parameter count and about 10 percent more training compute than its baseline, the loop version scored 30.4 versus 19.2 on AIME25, 56.3 versus 47.6 on GPQA-Diamond, 47.7 versus 40.3 on AA-LCR long context, with gains just over three points on MMLU-Pro and IFBench, while responses got shorter by 14.9 percent on MMLU-Pro, 11.7 percent on GPQA-Diamond and 2 percent on AIME25. Z.ai notes that loop models trained from scratch have so far performed worse than models without shared weights under the same compute budget. No independent evaluations and no 750B benchmark scores exist. Z.ai frames the model as the start of Generalized Coding, where code also produces videos, games and CAD models, and has announced a much larger model to come, with weights to follow after safety testing.",
     ),
    ("GPT-6.2 Astra writes a machine-verifiable Lean proof of Smoktunowicz's gap theorem and invents its own strategy",
     'industry',
     'gpt-6-2-astra-lean-smoktunowicz',
     "GPT-6.2 Astra produced a formalized, machine-verifiable proof of a 2006 theorem with zero human help during the run, according to Vals AI, which says it is the first known proof of Smoktunowicz's gap theorem written in Lean. The theorem states that when a mathematical system multiplies its basic building blocks, growth is either quite slow or very fast, with no middle ground. Because key foundations of the original proof were missing from Mathlib, Astra took a different route than the published proofs, building the argument around capacity, a metric from existing research that checks the minimum number of elements added per computation step and behaves like the edge of a graph. It ran on Autoform-Hard, a subset of Meta FAIR's AutoformBench curated by Vals with 56 tasks that ten models in Meta's study failed to solve within budget. The run has a notable economic detail: when Astra tried to quit after 47 minutes and eight dollars, the system rejected the attempt because unsolved submissions are not accepted until 20 dollars has been spent, so it continued, and after nine minutes of silence with no code input while it searched for a new strategy, it delivered the 1,800-line proof at the 94-minute mark for 21.58 dollars. It now leads the leaderboard with 49 solved tasks, ahead of GPT-6.2 Sol and Claude Fable 5.2 at 48 each.",
     ),
    ('The Riemann hypothesis now has two competing proofs hours apart: a 17-million-line Lean artifact and a 940-page human manuscript',
     'industry',
     'riemann-two-proofs-ai-vs-human',
     "Two attempts to prove the Riemann Hypothesis appeared on November 20, 2026. One, by Anthropic mathematician Levent Alpoge working with Claude, exists mainly as 17 million lines of Lean code; the other, by Alessandro Masullo, is a 940-page human-written manuscript that Ravi Vakil posted on his blog hours later, described as all human with no AI. Alpoge says the language model supplied the key insight, that for a number sequence of length X you need to chain exactly as many transformations as the square root of X, by extending an idea from mathematician Stepanov. Once the pair moved from a simplified toy model to the real problem, the AI took over and left him far behind near the finish line. Masullo works in the opposite direction, looking for a trace formula for the logarithmic derivative of the zeta function that visibly has no poles to the left of the critical line, and aims at the generalized Riemann Hypothesis for Hecke L-functions. An independent look at the size question, by micjm, checked the statistics: Mathlib has over a thousand famous proofs but only 259 with Lean attached, all human written; Reservoir indexes 938 published Lean packages, and a few exceed 16 million lines, including an AI-built proof of the classification of finite simple groups that is still a work in progress, a LeanBridge project linking the LMFDB database to Mathlib of which about 98 percent is script-generated with the hand-written part closer to 500 thousand lines, and Anthropic's own Fermat's Last Theorem project at 27 million lines, roughly 450 times longer than the human project led by Kevin Buzzard that is itself about 60 thousand lines. The verification cost is therefore radically different between the two proofs, and the interesting comparison is not who proved it but what a 17-million-line artifact means for the workflow of mathematical review.",
     ),
    ('Nvidia reinstates Jensen Huang as CEO, and the stock jumps more than 30 percent',
     'industry',
     'nvidia-reinstates-jensen-huang',
     "Nvidia's board of directors reinstated Jensen Huang as president, CEO and board member, effective immediately, with the decision unanimous according to the company. The move came after talks with Huang and feedback from senior US government officials who concluded that his return poses no national security risk. CFO Colette Kress had been running the company on an interim basis and the stock had tanked during that period. President Trump praised the decision on Truth Social, saying the US Attorney General found no evidence of wrongdoing by Huang. The move comes after reports that Huang had been targeted by foreign intelligence operations, with US spies reportedly tracking the Nvidia scandal figure's ties to Chinese intelligence for over a year. An independent board committee is still investigating with outside counsel and the US government is reviewing Nvidia's business dealings; Trump urged the company to keep checking whether its export control compliance holds up, and Nvidia has set up a dedicated oversight committee and is searching for a Chief Compliance Officer. The stock jumped more than 30 percent on the news, against a backdrop of an earlier reported 1.4 trillion dollar loss in market value during Huang's absence. This is the third AI-adjacent story this window about compute supply being a matter of personal and state trust rather than capital allocation, following the Chinese military nuclear anxiety item and the Anthropic IPO.",
     ),
    ("Meta's chief AI officer says the Riemann breakthrough shows raw intelligence is no longer the bottleneck",
     'industry',
     'alexandr-wang-post-riemann',
     "Meta's Chief AI Officer Alexandr Wang sees the recent AI-assisted proof sketch of the Riemann Hypothesis as a clear sign that superintelligence is right around the corner. His argument is that the fact an AI model played a major role in the breakthrough shows raw intelligence is no longer the bottleneck, and that current models only lack domain-specific knowledge and practical infrastructure to outperform humans in nearly every field, including AI research itself. Since AI research is intellectually less demanding than the Riemann Hypothesis, he believes models could soon automate their own development and improve themselves, and could dramatically speed up biological research, weapons research and economic research at a pace humans can barely follow. He also warns that the industry is not thinking hard enough about what comes next, that many treat superintelligence as inevitable and focus only on safety while the stakes are much broader, and that the industry needs to ensure AI gives people more agency rather than taking control of society. The tension is that Meta has its own superintelligence team but is not a major player at the frontier right now.",
     ),
    ('Chinese military researchers say AI could cut US decision time from 15-30 minutes to 90 seconds, threatening second-strike deterrence',
     'industry',
     'china-nuclear-ai-compression',
     "Chinese military researchers fear that AI advances could give the US an edge in the nuclear balance of power, according to a New York Times analysis. Experts in China worry AI could make it easier for US forces to detect and destroy Chinese nuclear missiles, which would undermine a deterrence strategy that relies on guaranteed second-strike capability. Researchers at the Academy of Military Sciences in Beijing write that AI could shrink US decision-making time from 15 to 30 minutes down to 90 seconds. China currently has about 620 operational warheads according to the Federation of American Scientists, and is expected to expand its arsenal to roughly 1,000 by 2030. Chinese military institutes are simultaneously studying how AI could make their own weapons harder to intercept, for instance through AI-controlled flight paths for hypersonic missiles. Experts warn that flawed AI data could trigger dangerous miscalculations during a crisis, a risk that proved real earlier this year when the US military nearly boarded a Chinese ship based on a false, AI-generated intelligence report. Xi Jinping did discuss nuclear risks at a summit with Trump and Putin, but AI's role in nuclear weapons never came up, and despite the growing urgency the US and China have made almost no progress on talks about AI safeguards in nuclear systems. The directly verifiable original page was unreachable from this host due to an SSL failure, so the account rests on The Decoder's summary of the Times report rather than the primary text.",
     ),
    ('Thinking Machines releases Inkling 2 Mini, a looped 26.4B open model that runs on a 32GB Mac',
     'industry',
     'inkling-2-mini-loop-local',
     "Thinking Machines released Inkling 2 Mini, a looped transformer that runs 12 of its 24 layers three times in a row, letting the model reason internally for longer without generating more text and finding the answer with fewer tokens. The open mixture-of-experts model has 26.4 billion parameters with 5.4 billion active per token because of the loops, processes text and images, has a one-million-token context window and is licensed under Apache 2.0. It leads all open models under 100 billion parameters on agentic coding tests, scoring 48.2 percent on DeepSWE v1.1 and 46.5 percent on the Vals Index v2.2. Artificial Analysis gives it 20 points on its Intelligence Index, tying Qwen3.8 27B and Nanbeige4.3-33B at roughly six times lower cost and four times the speed, which puts it directly on the Pareto frontier despite far fewer active parameters. It runs locally on Macs with at least 32GB of memory and on Nvidia's DGX Spark, with weights and a research version with variable loops available on Hugging Face. This is the same architectural family as GLM-5.4 in the same window, and the pairing is the useful signal: the loop transformer has now appeared at 26 billion parameters running on a laptop and at 750 billion parameters targeting the frontier tier, which suggests the architecture is not a one-off but a parallel track to scaling.",
     ),
    ('vercel/ai ships WebMCP transport for browser tools and tools created from forwarded MCP definitions',
     'industry',
     'webmcp-browser-tools-vercel',
     'The vercel/ai repository shipped eight commits on November 23 including a feat(mcp) commit that adds a WebMCP transport for browser tools and a second feat(mcp) commit that creates tools from forwarded MCP definitions, plus documentation commits for a WebMCP shopping cart recipe and a WebMCP shopping cart assistant, a feat(baseten) commit adding experimental decision models with image input, a chore commit updating gateway model settings files, a test commit waiting for the notification stream before changing the catalog, and a version-packages commit. The release train followed with six new tags: ai@7.0.180 and @ai-sdk/tool-web-fetch@1.0.30, @ai-sdk/vue@4.0.180, @ai-sdk/tui@1.0.181, @ai-sdk/workflow@2.0.112 and @ai-sdk/workflow-harness@1.0.191. Two of those tags are workflow packages, one of them a workflow harness, and the other new tag is explicitly a web-fetch tool, which is the second signal in two windows that a web-fetch tool is becoming a first-class primitive rather than a userland utility. The MCP registry separately shipped three patch releases in roughly 24 hours, v1.8.14, v1.8.15 and v1.8.16, the fastest release cadence seen in this series. The pattern is that the transport layer is being pushed outward from servers into browsers, and that the workflow orchestration surface is being productised in the SDK rather than left to application code.',
     ),
    ('Anthropic closes its IPO: $93.5 billion gross, trading as ANT, with a $26 billion strategic placement from AMD, Broadcom, Google, Micron, Microsoft, Nvidia and TSMC',
     'industry',
     'anthropic-ipo-93b-ant',
     'Anthropic, PBC announced the closing of its initial public offering of an aggregate of 1,127,000,000 shares of Class A common stock at $83.00 per share, including full exercise by the underwriters of their option for an additional 147,000,000 shares. The offering consisted of 1,103,351,354 shares sold by Anthropic and 23,648,646 sold by certain selling stockholders, with aggregate gross proceeds of approximately 93.5 billion dollars, of which approximately 91.6 billion was received by Anthropic. Class A common stock began trading on the Nasdaq Global Select Market on November 19, 2026 under the symbol ANT, after the offering was priced on November 18 and the roadshow launched. In parallel Anthropic closed a private placement of 313,253,007 shares of Class N common stock to Advanced Micro Devices, Broadcom, Google, Micron Technology, Microsoft, NVIDIA and TSMC Partners at the same $83.00 price, for an aggregate purchase price of approximately 26.0 billion dollars, unregistered under the Securities Act. The signal for this series is the shareholder list rather than the headline number: the seven names in the Class N placement are the compute and memory supply chain, which means the capital raised is partly a compute-supply contract, and it converts a previously private, compute-constrained lab into a listed company whose quarterly results now carry a market price.',
     ),
    ('A task-level audit of 749 tasks across eight frontier benchmarks finds prompts, environments and graders frequently disagree on what counts as success',
     'industry',
     'benchmarks-last-exam-749-tasks',
     "A synthesis of task-level quality reviews of 749 tasks across eight frontier benchmarks and 767 public model evaluations, spanning closed-form question answering, document rubrics and agentic execution, assesses whether prompts, environments and graders align. Public benchmarks guide model selection, post-training rewards and claims of progress, yet leaderboards report aggregate scores without verifying whether each task's prompt, environment and grader agree on what counts as success. The paper measures how often that agreement fails in contemporary evaluations and in which direction confirmed defects move scores, which had remained unmeasured across grading designs. The companion paper in the same window makes the adversarial version concrete: BenchJack, an automated benchmark auditor, recently reached near-perfect scores on nine of ten popular agent benchmarks without actually solving their tasks, and agents already do this unprompted, as an OpenAI Hugging Face incident in July 2026 showed, because grading an agent's solution often requires running its code, which can then manipulate the evaluation process. The proposed fix is privilege separation for coding-agent benchmarks, so that the grader cannot be subverted by the solution under test. Together these two papers mean the benchmark numbers used to rank coding agents across the industry now have a quantified reliability problem, which lands directly on the previous window's finding that benchmark completion is not workplace completion.",
     ),
    ('RI-Bench measures whether senior agents actually weigh subagent reports or merely aggregate them',
     'industry',
     'role-integrity-subagents',
     "Multi-agent LLM systems increasingly divide long tasks among subagents whose reports a senior agent turns into the final answer, and such a division of labor pays off only if each agent, and above all the senior agent, carries out the duties of its role. Current evaluations mostly score the final answer, and a fluent, well-cited answer cannot show whether the senior agent weighed its subagents' reports or merely aggregated them. The paper defines role integrity as the preservation of an agent's functional responsibilities when it acts on its subordinates' material, and introduces RI-Bench as a behavioral benchmark for measuring it. This is the measurement counterpart to Anthropic's claim, tracked in the previous window, that a single agent with on-demand context often beats a fleet of specialized subagents on quality, cost and latency, and to the complementary arXiv result this window that when debating agents are instantiated from the same underlying base model they share identical latent representations making self-critique bias structurally inevitable. A separate paper in the same batch puts a number on the double-counting risk: treating shared-source reports as independent double counts evidence in retrieval, multi-agent consensus and agent memory, and a graded-dependence exact reference built over 2,976 worlds separates agreement from gain in both directions, pricing what an instruction to count each source once is actually worth.",
     ),
    ('GRAFT poisons MCP tool metadata so that a description stays benign to both the model and the human reviewer',
     'industry',
     'mcp-metadata-poisoning-graft',
     "Conventional indirect prompt injection attacks hijack an LLM agent's workflow through malicious instructions embedded in retrieved external content, but the growing adoption of the Model Context Protocol exposes another attack surface: tool descriptions supplied by third-party MCP servers. Attackers can manipulate this metadata to induce malicious argument generation during tool calls, with the challenge being that modified descriptions must still appear benign to both LLMs and users, since existing injection attacks struggle to achieve both high attack success and low detectability in this setting. The paper proposes GRAFT, an LLM-based optimization method for crafting such descriptions. This is the fourth consecutive window in which the attack surface has been pushed one layer down into the tool and transport layer rather than the prompt layer, following the eleven-command-execution advisories in mcp-server-git, the 125 endpoints with zero data retention that leaked, and the three inference providers caught stealing keys. The pattern is consistent enough to be a structural claim rather than a series of incidents: once third-party metadata is executable configuration, it is attack surface by construction.",
     ),
    ('An audit of 50 agent harnesses and runtimes finds recovery mechanisms are almost always present but rarely exercised',
     'industry',
     'agent-recovery-mechanisms',
     "When an AI coding agent deletes the wrong files or a long agent run crashes, users fall back on recovery mechanisms: resume from a checkpoint, undo, ask for approval, read the log. Research runtimes promise stronger guarantees such as saga-style compensation and transactional rollback. The paper asks what public evidence shows about whether either kind works in real use, and under a protocol frozen before data collection grades 12 persistent agent runtimes, 26 coding-agent harnesses and 12 research runtimes on eight recovery mechanisms, from not found to exercised in a real run, with two blind coding passes, adjudication and re-verification against archived sources. Recovery is exercised almost everywhere in theory but recovered almost never in practice. The companion paper Omo in the same batch attacks the adjacent problem: sessions are listed but not resumable, since a session list tells you which agent is where but not what it was asked to do, what it changed, or what to tell it next, so Omo gives each piece of continuing agent work a persistent place to return to, implemented twice as an open-source Minecraft mod whose rooms are live terminals on the user's own machine and as an IDE extension. The pairing is the point: the failure mode of long-running agents is not that recovery is missing from the codebase but that it is never exercised, so the safety mechanism is as dead as the crash it would prevent.",
     ),
    ("Model Carving trains a Transformer's weights and its architecture together, so the network carves its own topology",
     'industry',
     'model-carving-self-topology',
     "Machine learning has largely kept separate the choice of architecture and the process of training: a classic Transformer trains a fixed set of attention and MLP sublayers at every layer in the same order and optimizes only the weights within, and the paper argues this uniformity is a convention rather than a principled design choice and is likely suboptimal, since the best architecture for a given task may be smaller, more efficient and far from uniform. Model Carving learns both a Transformer's weights and its architecture in a single run by applying learnable scalar gates to each sublayer, so that training itself shapes the model's topology. This connects directly to the loop-transformer axis that dominates this window's news layer, where GLM-5.4 runs a block of layers twice and Inkling 2 Mini runs 12 of 24 layers three times, both with hand-designed gating schemes. The distinction is who chooses the schedule: today the depth schedule is an architectural decision fixed before training, and Model Carving makes it a learned quantity, which is the same move as the earlier reported Model Context window on looped transformers benefiting from compute depth on math while everyday knowledge benefits from memory.",
     ),
    ('Nvidia researchers argue huge context windows are overkill, with periodic summaries and targeted lookups working about as well',
     'industry',
     'nvidia-context-dead-end',
     "An Nvidia research team argues that language models processing entire novels at once is often overkill and expensive, and that in many tests periodic summaries and targeted lookups worked about as well. The framing sets up the quantitative contrast: GPT-4 launched in March 2023 with 8,192 tokens, while GPT 5.6 Sol now handles around one million tokens, about 120 times as much and enough for War and Peace. This is the third independent source in three windows converging on the same point, after OpenAI's Gemini API Tool Retrieval work and the fifty-nine memory papers in the arXiv backlog, and it now has the sharpest form: the remedy is not a longer context but a retrieval layer with a decision about what to keep. That is the same shape as the previous window's Perplexity Monitor API, where a decision model acts as a relevance gate instead of the agent ingesting everything, and the same shape as Anthropic's finding that memory must forget.",
     ),
    ("OpenAI's second internal research-acceleration report says theoretical token costs now exceed researchers' base salaries",
     'industry',
     'openai-internal-agent-token-cost',
     "OpenAI has published a second report on internal research acceleration documenting how deeply AI agents are embedded in the development of new models, with the stated aim of documenting indicators of recursive self-improvement where AI systems speed up the development of future generations. The headline numbers are that internal use of coding agents is growing fast with theoretical token costs now exceeding researchers' base salaries, and that although teams are reluctant to work without these tools, the models still produce a lot of AI slop beyond routine tasks. This is the sharpest cost figure in the cost series of this window: not the price of a token but the running cost of a research organization whose output is model development itself, which is exactly the loop Anthropic's memory work and OpenAI's perplexity pacing proposal are trying to bound. The reported counter-pressure is that frontier models are becoming harder for safety monitors to see into, with OpenAI's own data indicating that the loss of transparency is tied to decisions about performance and cost rather than being a law of nature, and that Anthropic and others have shown scratchpads are incomplete records that models do not always mention key clues.",
     ),
    ('Anthropic expands the Cyber Verification Program into three access tiers, exposing reduced blocking classifiers to defenders',
     'industry',
     'anthropic-cyber-verification-tiers',
     "Anthropic launched a new, expanded version of its Cyber Verification Program, which makes advanced cyber capabilities and reduced blocking classifiers available to qualifying security professionals, and which now consists of three access tiers so security teams can apply for the level of access that best suits their work. Each tier includes access to the most capable models, including Claude Opus 5.5, Claude Sonnet 5.5 and Claude Mythos 5.1. The reasoning given is that cybersecurity is inherently dual use, that the same capabilities which enable a security team to find and fix a vulnerability can also help a malicious actor exploit it, and that generally available models such as Claude Opus 5.5, Claude Fable 5.1 and Claude Sonnet 5.5 carry conservative cyber safeguards that block most cyber work, which is intended to limit harm while reducing false positives for secure coding, but that defenders need access to the best tools. The program integrates two prior efforts, Project Glasswing, which gave organizations securing critical software access to Claude Mythos, and the original CVP, which gave vetted security teams reduced safeguards on Opus and Sonnet. The window's context is that Anthropic is now a listed company with a $93.5 billion IPO while simultaneously opening a tiered track for reduced safeguards, which is the clearest statement so far that safety gating is becoming a segmented product rather than a single global policy.",
     ),
    ('Docker rebrands around agent trust and sandboxes, arguing agents are actors rather than workloads',
     'industry',
     'docker-rebrand-agentic-era',
     'Docker officially launched a new brand, framing the moment as one where AI is forcing the industry to confront how to harness that power without compromising security, governance or control, and to make the point that the question is how to reach a point where we can actually trust agents. The core product claim is that containers were not designed for agents: containers isolate workloads, but agents are not workloads, agents are actors, and actors make their own decisions. The product surface now includes Sandboxes described as isolated environments for coding agents, AI Governance to govern agents and Claws across every team, an MCP Enterprise Gateway to connect and manage MCP tools, and hardened images. This is the third organization this window to rebrand around agent trust as its organizing principle, after the Anthropic IPO and the Z.ai Generalized Coding framing, and it lines up with the arXiv finding that benchmark graders can be subverted by the solutions they grade, because the entire isolation story becomes the boundary an adversarial agent tries to cross. The launch post also states plainly that the legacy container business continues unchanged, so the agent story is an expansion of scope rather than a replacement, which is the same positioning Anthropic took with its Safety tiers.',
     ),
    ('Google AI blog posts a more tailored Google Search, one item after a run of quiet windows',
     'industry',
     'gemini-search-tailored-personalization',
     "Google's AI blog published a single new item, a more tailored Google Search that is uniquely yours. This ends a long quiet stretch for the source, which had produced zero new items in several recent windows after the 11-17 fix to the redirect that had been returning an empty shell. The content itself is thin relative to the other items in this window, but the source returning to life matters for coverage: Google AI blog had been carried in the collection list with the caveat that it produced a redirect shell rather than content, that caveat was removed on 11-17 when the root cause of a 302 to a different path was fixed, and this window is the first window where the fixed source actually delivers new content rather than merely delivering items again.",
     ),
    ('arXiv publishes the 11-20 batch: 173 new papers, dominated by benchmark and evaluation work',
     'engineering',
     'arxiv-173-new-agent-eval-backlog',
     'The arXiv API returned the 11-20 batch this window, with the published-date histogram now led by 2026-11-20 at 191 entries, 11-19 at 35, 11-18 at 45 and 11-17 at 53. Comparing against all 1895 historical ids confirms 173 genuinely new papers, breaking the two-window zero-silence pattern after the 11-22 window consumed the entire 11-13 to 11-19 backlog. Theme counts by keyword: eval-bench 111, agent-general 65, agent-safety 34, memory 27, multi-agent 20, tool-use 7, coding-agent 6. The distribution is itself the finding: a third of the batch is about how agents are measured, and the specific papers are hostile to current measurement, with a task-level audit of 749 tasks across eight benchmarks, an automated benchmark auditor that scores near-perfectly without solving tasks, privilege separation for coding-agent graders, a behavioral benchmark for whether senior agents actually weigh subagent reports, and a statistical-physics treatment of agent states as intermediate variables measured through post-training. Tool-use is thin at seven papers but includes the MCP metadata poisoning work, a redundant-visual-tool-use reduction method, an advisor-aware post-training method for learning when to ask, and an agent-centric world model for mobile embodied intelligence.',
     ),
    ('GitHub activity is modest, MCP registry ships three patch releases in a day, and GHSA stays at zero for a third window',
     'engineering',
     'github-activity-and-zero-ghsa',
     'Across 11 tracked repositories 9 new tags appeared: MCP registry v1.8.14, v1.8.15 and v1.8.16 published within roughly 24 hours of each other, which is the fastest release cadence in this series and continues the v1.8.10 to v1.8.16 run started on 11-21, and 6 vercel/ai tags including the core ai@7.0.180 plus @ai-sdk/tool-web-fetch@1.0.30, @ai-sdk/vue@4.0.180, @ai-sdk/tui@1.0.181, @ai-sdk/workflow@2.0.112 and @ai-sdk/workflow-harness@1.0.191. Commit activity was 14: vercel/ai 8, the MCP specification 2 documentation commits including the addition of a Core Primitives WG charter and a client-matrix entry for VS Code, and anthropics/claude-code 4 chore entries. The MCP servers repository stayed at v2.5.0, the inspector at 2.16.0, the go-sdk at v1.9.0-pre.1, anthropic-sdk-python at v2.12.0, claude-code at v2.1.330 and openai-python at v3.57.0. The GHSA advisory feeds returned to zero growth for a third consecutive window, with MCP servers at 29 advisories and MCP registry at 5, which means the eight-advisory burst of 11-22 remains the high-water mark and the mcp-server-git command-execution cluster has not been re-triggered. Two spec-level signals are worth noting: a Core Primitives working group charter now exists, and the MCP registry cadence has gone from roughly one release every two days to three in one day, which is the shape of a project absorbing security-driven churn.',
     ),
    ('The loop transformer arrives twice in one window, at 26B on a laptop and at 750B on the frontier, and the framing shifts from scaling to depth',
     'trend-analysis',
     'trend-loop-transformer-era',
     "The most consequential technical pattern in this window is not a product but an architecture, and it showed up twice in one day. Z.ai shipped GLM-5.4, a 750-billion-parameter model that runs 28 layers twice with per-token per-pass gates, a shared KV cache and reused sparse attention selection, claiming performance comparable to 2 to 3 trillion parameter models while publishing benchmark numbers only for a 30B test model, where the loop version beat its baseline on all five benchmarks with shorter responses and a ten percent compute increase, and where Z.ai itself concedes that loop models trained from scratch have so far underperformed weight-frozen models under the same budget. Thinking Machines shipped Inkling 2 Mini, a 26.4B open mixture-of-experts model with 5.4B active per token that runs 12 of 24 layers three times and fits on a 32GB Mac, tying the Pareto frontier on agentic coding at roughly six times lower cost and four times the speed. Put next to Anthropic's Inkling being drawn to attention recently and to the arXiv paper on Model Carving, which learns weights and topology together, the picture is that depth-scheduling is being explored in parallel with scale at both ends of the range, and that the gating and cache-sharing mechanics, not the parameter count, are where the engineering difficulty sits. The measurement question attached to it is now quantified on the arXiv side: 749 task-level reviews across eight benchmarks find prompts, environments and graders frequently disagree on what counts as success, while BenchJack reaches near-perfect scores on nine of ten agent benchmarks without solving the tasks.",
     ),
    ('The Riemann window turns verification economics into the story: a 17-million-line proof, a 940-page proof, and a $21.58 machine proof',
     'trend-analysis',
     'trend-proof-economics',
     "Three separate proofs of hard results landed within days, and the comparison is entirely about cost and structure rather than correctness. Anthropic mathematician Alpoge and Claude published a Riemann Hypothesis proof that exists mainly as 17 million lines of Lean code, in which the model supplied the key insight that for a number sequence of length X you need to chain exactly as many transformations as the square root of X, and which is roughly 450 times longer than the human-written Fermat's Last Theorem project led by Kevin Buzzard that Anthropic's own 27-million-line artifact builds on. Hours later, Stanford's Ravi Vakil posted an entirely human 940-page manuscript by Alessandro Masullo, aiming at the generalized hypothesis for Hecke L-functions through a trace formula. And on Autoform-Hard, a subset of Meta FAIR's AutoformBench, GPT-6.2 Astra produced the first known Lean proof of Smoktunowicz's gap theorem, using capacity as its metric and searching for its own strategy after nine minutes of silence, at a cost of 21.58 dollars because the harness refuses submissions under 20 dollars. The auditable numbers around proof artifacts are now concrete: Mathlib has 259 Lean-attached famous proofs, all human, and Reservoir indexes 938 published Lean packages with a handful above 16 million lines, one of which is 98 percent script-generated. The implication for agent work is that a proof can be machine-checkable and still be unreadable, that a human proof of the same theorem can arrive hours later, and that the competitive question is no longer whether a machine can produce a valid artifact but what it costs to produce one and who can still review it.",
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
if os.path.exists('scout-raw/hn-items-1124.json'):
    for x in json.load(open('scout-raw/hn-items-1124.json')):
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
