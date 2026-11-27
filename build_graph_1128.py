import json, os, re, hashlib, glob

STAMP = '2026-11-28'
OUT = 'graphify-out/' + STAMP
os.makedirs(OUT, exist_ok=True)
os.makedirs('graphify-out/raw', exist_ok=True)

PREV = "2026-11-27"


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
arxiv_files = [('scout-raw/arxiv-csAI-full-parsed-1128.json', 'cs.AI'),
               ('scout-raw/arxiv-csMA-full-parsed-1128.json', 'cs.MA'),
               ('scout-raw/arxiv-mcp-full-parsed-1128.json', 'MCP'),
               ('scout-raw/arxiv-missing-parsed-1128.json', 'listing-missing'),
               ('scout-raw/arxiv-recover-parsed-1128.json', 'listing-recovery')]
new_ids = set(x.get('id_base') or x['id'].split('v')[0] for x in json.load(open('scout-raw/arxiv-1128-newids-final.json')))
arxiv_count = 0
_arxiv_seen = set()
for f, qset in arxiv_files:
    if not os.path.exists(f):
        continue
    for x in json.load(open(f)):
        aid = x['id'].split('v')[0]
        if aid not in new_ids:
            continue
        nid = 'arxiv:' + aid
        if aid in _arxiv_seen:
            continue
        _arxiv_seen.add(aid)
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
    ('scout-raw/gh-1128-modelcontextprotocol-servers-releases.json', 'MCP servers', 'mcp-servers'),
    ('scout-raw/gh-1128-modelcontextprotocol-modelcontextprotocol-releases.json', 'MCP spec', 'mcp-spec'),
    ('scout-raw/gh-1128-modelcontextprotocol-registry-releases.json', 'MCP registry', 'mcp-registry'),
    ('scout-raw/gh-1128-modelcontextprotocol-inspector-releases.json', 'MCP inspector', 'mcp-inspector'),
    ('scout-raw/gh-1128-modelcontextprotocol-python-sdk-releases.json', 'MCP python-sdk', 'mcp-sdk-py'),
    ('scout-raw/gh-1128-modelcontextprotocol-typescript-sdk-releases.json', 'MCP typescript-sdk', 'mcp-sdk-ts'),
    ('scout-raw/gh-1128-modelcontextprotocol-go-sdk-releases.json', 'MCP go-sdk', 'mcp-sdk-go'),
    ('scout-raw/gh-1128-anthropics-anthropic-sdk-python-releases.json', 'anthropic-sdk-python', 'sdk-py'),
    ('scout-raw/gh-1128-anthropics-claude-code-releases.json', 'claude-code', 'claude-code'),
    ('scout-raw/gh-1128-openai-openai-python-releases.json', 'openai-python', 'openai-python'),
    ('scout-raw/gh-1128-vercel-ai-releases.json', 'vercel ai sdk', 'vercel-ai-sdk'),
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
for f in sorted(glob.glob('scout-raw/gh-1128-*-commits.json')):
    label = f.split('gh-1128-')[1].replace('-commits.json', '').replace('-', ' ')
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
for f, repo_tag in [('scout-raw/gh-1128-servers-advisories.json', 'mcp-servers'),
                    ('scout-raw/gh-1128-registry-advisories.json', 'mcp-registry')]:
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
    ('MCP servers v2.6.0 ships a coordinated security release fixing eight vulnerabilities in three servers, and the GitHub advisory feed breaks a five-window zero-advisory streak',
     'engineering',
     'mcp-servers-v2-6-0-eight-vulnerabilities-ghsa-streak-broken',
     "The modelcontextprotocol/servers repository published v2.6.0 on 2026-11-27, described in its own release notes as fixing eight vulnerabilities in three servers and completing two fixes that v2.5.0 left open. Upgrade guidance: mcp-server-git to 2026.11.27, @modelcontextprotocol/server-memory to 2.2.2, mcp-server-fetch to 2026.11.27, and on Windows @modelcontextprotocol/server-filesystem to 2.4.1. The GitHub advisory feed confirms the change from the other direction: the server advisory count went from 29 to 30 with eight new GHSA entries all published on 2026-11-27, breaking what had been a five-consecutive-window zero-growth streak in this series. The individual findings are specific and share a shape. GHSA-6663-fm5v-gqm5 is rated high: with Git LFS installed, the server kept the LFS filter from the user's own configuration, so keys naming programs in the repository's .git/config (lfs.extension.<name>.clean and .smudge, lfs.customtransfer.<name>.path and .args) could be run with the server's privileges by git_status, git_diff_unstaged, git_diff, git_add, git_checkout and git_merge; the fix empties those keys at repository scope and turns LFS downloads off via GIT_LFS_SKIP_SMUDGE=1. GHSA-3whj-m8jj-x97q allowed the --repository root to be retargeted through a .git pointer file or commondir, so git_show served another repository's content; the fix records the root's Git directories at startup and refuses any root whose .git file names a different Git directory. GHSA-wvv2-676g-r57j is a credential redaction bypass in git_remote: a remote name containing a tab shifted the URL column and a URL not starting its value skipped redaction, so a credential-bearing url.<base>.insteadOf in the user's config was returned. GHSA-f33v-89w7-f9vc expanded $NAME and ${NAME} in repo_path and then disclosed the expansion in an error message, so a tool call could read any environment variable of the server process. GHSA-48j5-hj63-c82c is a temp-path race in the memory server's saveGraph that exposes protected files through symlinked chmod. GHSA-g7v6-hfx3-8rv6 is an incomplete fix for GHSA-3rxj-6jhw-qfv7, where robots.txt path normalisation in mcp-server-fetch still missed backslash and path-parameter spellings. The pattern across all of them is the same one this series has tracked since the first MCP advisory window: the MCP server trust boundary is the local repository and the local configuration, and every one of these is a case where the server executed, read, or disclosed something on the basis of content that the agent's user did not author and could not see. What is new here is not the class of bug but the arrival of a release train that treats the class as routine, and the fact that the advisory feed is now a live signal rather than a flat line.",
     ),
    ('The MCP inspector patches a NAT64 SSRF bypass that let a malicious server reach cloud metadata through an IPv6 address written in a different form',
     'engineering',
     'mcp-inspector-nat64-ssrf-metadata-bypass',
     "The modelcontextprotocol/inspector project published 2.17.0 on 2026-11-27 with a security fix, and 1.0.7 for the deprecated v1 line at the same time. The vulnerability: the SSRF guard matched IPv6 addresses by how they were written rather than by their value, so a malicious MCP server could name an authorization server such as http://[64:ff9b::a9fe:a9fe] to reach 169.254.169.254 through the web backend or the CLIs on a host with NAT64 or DNS64 egress. The fix parses each address and matches on its value, and specifically re-checks the IPv4 address carried in ::ffff:0:0/96, 64:ff9b::/96 and 64:ff9b:1::/48, while still allowing NAT64 addresses that embed a public IPv4 address. The release also adds a non-security fix with an interesting property: it now fails --verify over an empty skills catalog instead of reporting Verified. That second detail is the one this series wants to keep, because a verification tool that reports success on an empty input is the same shape of defect as the reviewer-gate failures being measured elsewhere in this window, where every model and every effort setting accepted at least 45 percent of wrong patches. It is also the same shape as Bernstein's running list of soundness bugs in proof-checking programs, which is the top HN-linked item this window. The specific mechanism, a guard that pattern-matches a serialized form of an address instead of parsing it and comparing the parsed value, is the narrowest possible version of a general theme: security decisions that are made on the representation rather than on the thing represented.",
     ),
    ('The US Air Force Cloud One breach lands in the same week as the ARTEX analysis, and the two stories now form a single closed loop',
     'industry',
     'air-force-cloud-one-breach-after-artex',
     "Reuters reported, via The Decoder, that attackers penetrated Cloud One, the Air Force's central cloud infrastructure, potentially exposing sensitive tactical, personnel and logistics data. The breach was discovered last month during routine system upgrades, and according to one source the attackers exploited a software vulnerability to gain access to the platform's control plane. Cloud One has pooled cloud resources from Microsoft, Amazon, Oracle and Alphabet since 2017 and runs applications including air defense radar and munitions management. The Air Force paused migration of additional applications, blocked updates and revoked administrator privileges, and US Cyber Command is assessing the damage. Who carried out the attack and whether data was exfiltrated remain unknown. The reason this belongs in the same paragraph as last window's ARTEX story is that the ARTEX analysis named Salt Typhoon, Crystal Typhoon, Onyx Sleet and Storm-0940 as state-backed groups integrated with that framework, noted the AI tool's ability to identify vulnerabilities rapidly across large cloud networks, and mentioned suspected use in the intrusion into an analytics system run by the CIA, NGA and ODNI. Two weeks later a US military cloud platform has been breached through a control-plane vulnerability and the reporting notes at least six other recent cyber incidents against US government agencies. The loop closes as follows: an agent framework that can find and exploit a cloud vulnerability at machine speed is now followed by a breach of exactly that shape against exactly that kind of target. The defensive recommendation from the ARTEX analysis was deception rather than blocking, decoy systems and faked success signals that make the attacking agent call off an attack. No such defense is mentioned in the Cloud One report, which describes conventional containment: pause migrations, block updates, revoke administrator privileges. The response time and the shape of the response are both part of the finding.",
     ),
    ('OpenAI builds Athena, a semantic layer for business data, on the theory that switching semantic-layer providers is harder than switching models',
     'industry',
     'openai-athena-semantic-layer-agent-guessing',
     "The Information reports, via The Decoder, that OpenAI is building a data management platform codenamed Athena to make its AI agents more accurate when working with business data. Athena resembles a semantic layer, software that provides consistent definitions for business metrics such as revenue and customer count. At least one customer found that ChatGPT Work's data analysis agent, launched last fall, was not accurate enough. The idea is to give agents the context they need so they guess less. A person familiar with the plans says OpenAI is using Athena to build agents that collect, document and update business rules, so that other agents do not have to start from scratch every time. Snowflake and Databricks already offer their own semantic layers. The reported strategic logic is that Athena could be a competitive moat precisely because it is harder to switch semantic-layer providers than to switch AI models. The platform is still in early development with no timeline or pricing. This is the third distinct appearance of the same underlying move in this series, and the first one that is explicitly about switching costs rather than capability. In the previous window the boundary calibration was the 1Password case, where a breach reached backend account records and private source code but vault contents held because the architecture was designed to hold there. In the window before that it was OpenAI's Private Inference pilot, where queries are processed on independently verifiable isolated hardware and flagged content is stored in the customer's own cloud. What Athena adds is the observation that the durable asset in enterprise agent deployment is not the model and not the sandbox, but the accumulated, versioned definitions of the customer's own business, and that whoever owns that definition layer owns the switching cost. It also connects to the arXiv side of this window, where several papers treat exactly this failure mode, agents guessing because they lack consistent definitions, and where a paper on the detour being the danger shows that agents silently drop security obligations during recovery. The three run on the same theme: an agent's context is an asset with a switching cost, and the risk is that it is wrong rather than absent.",
     ),
    ('GTA 6 PC ports appear within days of the leak, with 40 active projects and coding agents doing the reverse engineering',
     'industry',
     'gta6-pc-port-coding-agents-rockstar',
     "Following a leak of an Xbox build of Grand Theft Auto VI, a tracking platform lists 40 active port projects less than four days after the executable leaked, and nearly half can boot the game on PC, with the furthest project more than 90 percent of the way to a playable build. AI coding tools like Anthropic's Claude Code are driving the pace, with developers handing off much of the porting work to AI agents instead of spending months manually analyzing code and rebuilding console functions. Unofficial multiplayer mode footage surfaced on 26 November and was verified, running at 25 to 30 frames per second, even though GTA 6 has officially launched as single-player with no announced online mode. The game had a historic debut on PlayStation 5 and Xbox Series X|S with an estimated 3.79 billion dollars in first-day revenue. Rockstar's strategy has always been console-first: GTA V took about 19 months to reach PC. The structural point for this series is the speed differential. Console emulators historically took years after a hardware generation launched, and new blockbusters rarely ran on them soon after release. Here, reverse engineering a freshly released AAA title was parallelised across dozens of independent projects with agents doing the tedious parts, and the gap between release and a booting unofficial port collapsed to days. The same mechanism, an agent converting an expensive expert task into a parallelisable one, appears elsewhere in this window: D.J. Bernstein's False Computer-Checked Proofs lists soundness bugs in proof checkers, and an arXiv paper gives evidence that an AI code reviewer accepts at least 45 percent of plausible-but-wrong patches at every effort setting. The GTA case is the same shape seen from the other side, where the capability that does not get reviewed correctly is capability that gets used at scale.",
     ),
    ('SAP prepares to cut at least 10,000 jobs, about 9 percent of its workforce, as part of an AI restructuring',
     'industry',
     'sap-cuts-10000-jobs-ai-pivot',
     "Bloomberg reported, via The Decoder, that SAP is preparing to eliminate at least 10,000 positions as part of a sweeping AI restructuring, at least nine percent of the company's global workforce of more than 110,000. Every department has been asked to identify savings, with product development, engineering and sales taking the biggest hit. The final number has not been set and could change after negotiations with employee representatives. In Germany, where about a quarter of SAP's workforce is based, a job guarantee runs through 2028. CEO Christian Klein wants to embed AI tools across SAP's product lineup. The company already cut roughly 10,000 jobs in 2024. Oracle slashed 21,000 positions over twelve months and Microsoft is offering buyouts to around 60,000 employees. SAP recently announced a partnership with Mistral AI and has acquired several startups. This is the first number in this series tying an enterprise AI strategy directly to headcount at a specific scale, and it lands in the same window as OpenAI's Athena semantic layer and the arXiv work on agent review gates. The ordering matters: the deployment economics work in this series has said that the binding constraint on agent deployment is human review throughput rather than model capability, that 19 percent of enterprise deployments deliver no business value, and that the largest obstacle is too much AI output for humans to review with 49 mentions. A company cutting 9 percent of its workforce while embedding agents across its product line is making a bet that the review bottleneck is a cost to be removed rather than a capacity constraint to be staffed. The related arXiv result sharpens the question. If an AI code reviewer accepts at least 45 percent of plausible-but-wrong patches at every effort setting, then the code that replaces the laid-off engineers is reviewed by something with a 45 percent false-success rate, and the review capacity being removed was the part that caught some of what the automated reviewer misses.",
     ),
    ('Aaronson argues the Riemann proof matters less than the fact that an AI system could produce it, and says a proof of P not equal NP is not far away',
     'science',
     'aaronson-riemann-proof-lower-bounds-p-np',
     "Complexity theorist and former OpenAI researcher Scott Aaronson wrote in a blog post that proving the Riemann hypothesis probably would not change anyone's daily life, and that the ideas behind such work could lead to new applications in science and engineering down the road, but it is anyone's guess which ones. His larger argument is that the far bigger deal is that AI can do this kind of work at all, with potentially staggering implications for everyday life, from reshaping the global economy to threatening all life on Earth, and that anyone serious about the topic should set aside the demand for a sharper spear. He walks through OpenAI's matrix multiplication proof, which adds a matching lower bound to an existing fast algorithm and shows how far computational cost can actually drop, at least in the model OpenAI studied, and through the Fourier transform result, which found a faster way to compute it and also proved it cannot be done much faster. He stresses the lower bounds in particular: a new method only sets a record, but a lower bound shows where further improvements hit a hard limit. He concludes that what is coming is not one-off solutions to particular complexity questions but a whole new continent of mathematical truth previously glimpsed through fog. He also says he now feels in his bones, for the first time ever, that a proof of P not equal NP is not far, and that he is virtually certain, from multiple reliable sources, that AI labs are sitting on one or more bombshells in cryptography, without having the details yet, having written in October that AI labs were testing whether their models could break cryptographic systems. This is the interpretive half of last window's finding that the matrix multiplication exponent is exactly 9 over 4, and it is the same argument as before but sharpened by the lower-bound emphasis. A lower bound is not a better result, it is a wall. It is the shape of output that does not improve with more compute and is instead a statement about the limits of the computation itself, which is why the window's second headline, Bernstein's running list of soundness bugs in proof-checking programs, matters here. The proof is only as good as the checker that accepts it, and the checkers have known exploitable soundness bugs.",
     ),
    ('Bernstein publishes a running list of soundness bugs in proof-checking programs, and the top HN item this window is a proof-checking tool with a known escape hatch',
     'science',
     'false-computer-checked-proofs-soundness-bug-list',
     "D. J. Bernstein published a page collecting reports of soundness bugs in proof-checking programs, sorted by number of reports, and states it contains many more soundness bugs for these programs than the bugs mentioned in the 2026 Paulson and 2026 Stérin reports, while probably missing some. He notes the list excludes user-interface vulnerabilities, which can have the same important effect of misleading a user about what has been proven, citing a 2016 Adams example. On advice, he says one standard path towards security is to minimize the complexity of the trusted computing base, and from this perspective HOL Light's proof-checking kernel is attractive for its stability and simplicity at only 400 lines of code, though that size measurement says nothing about how carefully the code has been reviewed and nothing about the possibility of bugs in the underlying programming language. He notes that extra code can be good if it is test code, since a battery of tests tends to catch more bugs than a single test, and that running a proof through multiple proof-checking programs, preferably each in its own isolated environment, can save the day when there is a bug in one program, particularly easy when the checkers take the same input language for writing proofs. But he is careful that this is not clear how effective this is at stopping attacks, since sometimes bugs are shared by multiple checkers. He poses the question who watches the provers, and answers it better with a proof saying that a checker works correctly. The connection to this window's other threads is direct. The MCP inspector shipped a fix this window for a guard that matched IPv6 addresses by written form rather than parsed value, which is a soundness bug in a verifier. The inspector also now fails --verify over an empty skills catalog instead of reporting Verified. And the arXiv study on AI code reviewers found that no effort setting and no model accepted fewer than 45 percent of plausible-but-wrong patches. Across all three, the artifact checks something and the check has a known or measured failure rate, but the failure is not visible to the person relying on it. Bernstein's answer, a proof that the checker works correctly, is a recursively harder version of the same problem, and he says so.",
     ),
    ('An arXiv wave measures the exact failure modes this series has been tracking: agent security that does not survive its own recovery, security lessons that do not transfer across sessions, and reviewers that accept most wrong patches',
     'engineering',
     'arxiv-agent-security-recovery-retention-and-review-gates',
     "The recovered arXiv batch contains the sharpest measurement yet of three things this series has been tracking as separate threads. First, The Detour Is the Danger studies workflow security downgrade, a failure-induced threat in which an agent recovers from an execution failure by replanning autonomously, preserving task functionality while silently discarding the security protections required by the original workflow; unlike prompt injection it does not modify instructions or tool definitions, and it was evaluated by fault injection in an executable MCP and Skill environment across seven LLMs, twelve task templates and three security-sensitive domains, with an obligation-preserving recovery framework that prevented all observed protection-loss events under enforcement across a separate 864-run evaluation. Second, PRECEPT reports that across 14 task sequences Codex, Claude Code and Qwen Code fixed a vulnerability 85.7 percent of the time when shown the failing security test, then reintroduced the same vulnerability class in a new session 26.7 percent of the time, about as often as agents that had never seen it at 27.5 percent, and that neither recording the repair in persistent context nor supplying published secure coding principles closed the gap, because the recorded fix stayed tied to the family of the task it came from and human-written principles stayed too general to apply to the code at hand; the authors call the missing ability security self-improvement. Third, a study of how much effort an AI code reviewer needs had three Claude 5.5 models review the same 90 agent-written Django patches from SWE-bench Verified at low, medium and high effort, with strengthened SWE-ABS tests marking 55 wrong and 35 correct, and found that in every model high effort accepted fewer wrong patches than low, false success 0.45 against 0.67 for Opus, 0.49 against 0.65 for Sonnet and 0.51 against 0.78 for Haiku, but that no setting is a strong gate since each accepted at least 45 percent of wrong patches. The three together describe the same structural property of agent systems: the capability is present and the persistence is not, the protection is present and the recovery path drops it, and the reviewer is present and the gate is weak. Note that the reviewer study is the same 90-patch shape that the DRA paper from two windows ago used to measure whether agent patches over-edit, which makes this the first time the same corpus has produced both an over-editing measure and a review-gate measure.",
     ),
    ('An arXiv wave treats agent quality as a property of the surrounding system rather than the model: transferable harness evolution, partial routing, confidence gates, and certified proof depth',
     'engineering',
     'arxiv-harness-evolution-partial-routing-confidence-and-proof-certificates',
     "Four results in the recovered batch shift the unit of analysis away from the model and onto the scaffolding around it. TransHarness evolves harness intervention policies from same-task success-failure contrasts, pairing execution-context triggers with diagnostic guidance, retaining policies through cross-task replay and independent semantic selection so corrections are grounded in current-task evidence rather than source-specific solutions; with only 300 source trajectories from outside the test distribution it reaches 76.4 percent on DeepSWE v1.1 and 95.5 percent on Terminal-Bench 2.1, surpassing GPT-6 Astra by 2.4 and 5.6 points, which is the first evidence in this series that harness work transfers rather than overfitting the benchmark it was evolved on. Partial Routing lets a frontier lead model delegate suitable subtasks to a cheaper worker, identifying recurring subtasks from both models' past runs and measuring quality and cost on them, with the lead deciding during execution without training either model; at delta 0.75 it raises a ViBench score from 70.2 to 78.5 at 19 percent lower cost and a Terminal-Bench pass rate from 54 to 61 percent at similar cost, and even giving the lead only the subtask breakdown without a worker reduces cost and raises the pass rate. A paper on confidence scores for gated automation fits a linear head to the final-layer hidden state of a frozen 2B backbone and trains text-only metamodels as an alternative for closed models, automating the largest fraction of the workload at high accuracy targets while showing that prompted confidence scores can look calibrated yet lack the resolution needed for thresholding. And Certify What You Plant shows that procedurally generated logic problems usually have a planted proof but may also have shorter or unrelated ones, so stated depth overstates what solving requires; it computes the steps every proof must make, the shortest proof, the number of minimal proofs and the indispensable premises, and exports certificates an independent checker verifies, finding depth that is forced in ProofWriter and Blocksworld, problems labelled depth 5 that require about two specific rule applications in FLDx2, and answers needing no particular step in ZebraLogic, with certified mixtures transferring better than derivation data. The common claim is that model capability is no longer the binding variable, and that what changes outcomes is the harness, the delegation policy, the confidence head and the depth of the task specification.",
     ),
    ('The inference stack fragments into bespoke vibe-coded engines, and the optimizations start changing how the model thinks rather than how the hardware runs',
     'engineering',
     'bespoke-inference-engines-vibe-coded-and-the-drift-toward-different-thinking',
     "A November 26 post surveying the state of bespoke inference engines notes that an explosion in the number of them has taken place, with many taking inspiration from llama.cpp, SGLang and vLLM, whose rationale is not that those options are bad but that they are generalist engines optimized for no particular hardware with a focus on broad compatibility, whereas the new forks focus on a specific subset of models and hardware, use a frontier model to vibe-code the entire thing, and chase ever-higher token generation speeds. The author notes that Strata can run a heavily quantized Qwen 3.8 Flash Next, a 180B parameter model, on a 16GB VRAM card and 16GB system RAM at a surprisingly high rate. The example given for this project is an AMD-specific fork of llama.cpp that raised token generation from 35 to 55 tokens per second and prefill from 700 to 1300 tokens per second. The uncomfortable detail the author names is the direction of the optimization: Strata specifically prefers to poll experts loaded in VRAM even if other experts, pushed to system RAM or disk, would normally have been chosen, which changes how the model computes rather than how the hardware is used. This is the same structural move as the loop transformer work in this series, where layers run two or three times with shared KV cache, and where OpenAI's own researchers argue that huge context windows are a dead end. It is also the same move Deepmind makes deliberately and in the opposite direction, by not rewarding chain-of-thought so that intentions stay legible to a human reviewer. The thread running through both is that once you are optimizing tokens per second rather than quality, the cheapest lever available is to change what the model computes. That is a quality risk that the token-per-second number does not display, and it is exactly the kind of thing the reviewer measurements in this window would fail to catch, since every review configuration accepted at least 45 percent of plausible-but-wrong patches.",
     ),
    ('Google makes its Workspace MCP servers mandatory for any tool driven by an AI agent from February 2027, and the Gmail server still cannot send email',
     'industry',
     'google-workspace-mcp-mandate-agent-classification',
     "On 24 November Google made its eight Workspace MCP servers generally available and published a new clause in its API terms. From 1 February 2027, any tool that is or is driven by an AI Agent, an AI Harness or an AI model or service employing an AI model must reach Gmail, Drive, Calendar and the rest of Workspace through those servers. The new Workspace AI Tools Addendum to the Google APIs Terms of Service states the requirement in one sentence and the next sentence forbids disguising an agent to avoid the classification, with breaking either allowing Google to restrict or remove the GWS Access Tool's access or suspend the account. There is a technical side: from the same date, agents that call the REST APIs directly are held to Standard-tier quotas whatever tier the project has paid for, so REST keeps working, slowly, and in breach of the terms, while apps that do not involve AI, such as a nightly backup job, a CRM sync or a deterministic script on its own OAuth client, are not affected. The addendum also adds data rules that matter to anyone building an agent with memory, restricting Workspace data to being processed to fulfill active, user-authorized tasks. Reading the Gmail server's tool list shows it can search mail, read threads, create a draft and file things under labels, but it cannot send a message, reply, forward or change a draft after creating it, because those tools exist but Google's quota page says they require partner access and are not generally available. Two structural points. The first is that the classification of the caller, not the capability, is what the rule turns on, and the rule makes disguising the agent a terms violation, which means the compliance surface is behavioural rather than technical and therefore has to be enforced by the vendor against the client's own description of itself. The second is that the most-used function of the most-used tool in the suite, sending email, is deliberately withheld from general availability, so an agent that must route through the mandated path is strictly less capable than one that calls the REST API directly. This is the same shape as the MCP server advisories in this window, where the capability was available and the containment was the defect.",
     ),
    ('Apple and California age-gating rules take effect, and a WebRTC skimming script is found on five Black Friday storefronts before payment validation',
     'industry',
     'age-gating-and-webrtc-card-skimming-on-black-friday',
     "Two smaller signals from the window. On the regulatory side, New York and California age gating rules go into effect in the new year, with the EFF writing on the change. On the security side, InfoHawk reported that a card-skimming script was planted on the online stores of Lascana, Samsonite, American Tourister, Revolve and FWRD in the week before Black Friday, observed in action on Lascana where it sent a test card's details to a third party, and removed from all five sites after the company was notified, on 24 or 25 November. The script appears designed to take a card number, expiry and security code together with name, address, phone and email and send them to the actors as the user entered payment credentials, and it did this before the store checked the payment, so a card could be taken even if the order was declined or cancelled, with nothing looking wrong to the shopper. The WebRTC angle is the interesting part, since a channel that is not an HTTP request is not covered by ordinary content inspection and by the same logic is not covered by the kind of egress rules this series has been tracking on the enterprise side. The companies all responded and removed the script, but the note that matters is the general one in the report: the larger consumer web ecosystem should be prepared to mitigate these attack vectors. Three of the affected stores are luggage brands, which is consistent with seasonal shopping traffic rather than a targeted campaign, and the affected sites are all small enough that a checkout script placed in the page is not a compromise of a sophisticated platform but of a modest web host.",
     ),
    ('A Stanford physicist publishes a quantum-gravity calculation developed over months with GPT-6 Astra using about 400 million tokens, and the acknowledgments are the finding',
     'science',
     'stanford-quantum-gravity-gpt6-astra-400m-tokens',
     "Stanford physicist Venkatesa Chandrasekaran proposed a quantum theory of gravity that uses the paths of light to calculate how spacetime can fluctuate. The approach yielded a finite result for a graviton-pair calculation that diverges under an approximation, and reproduced a known quantum correction to black hole entropy. In an arXiv preprint, Chandrasekaran calculated what happens when two gravitons, the hypothetical quantum units of gravitational waves, are created and then disappear, and the calculation gave a finite answer even after accounting for waves of arbitrarily short wavelength, while an approximation applied to the same calculation produced an infinity. In the paper's acknowledgments he said he developed several of its calculations and proofs through months of back-and-forth work with OpenAI's GPT-6 Astra, using about 400 million tokens. This is a distinct data point from last window's Aaronson and OpenAI proof stories, because those were about the model producing a result. This one is about the research process: a physicist iterating with a frontier model over months on a specific physics calculation, in a domain where the check on correctness is a comparison against an independently known quantum correction. The number 400 million tokens is the concrete scale of that collaboration, and it is the kind of number this series has been collecting, alongside the 17 million lines of Lean, the 940 pages of handwritten human proof, the 400 lines of HOL Light's kernel, and the roughly 3 to 6 months of compute-cost-equivalent that a frontier research lab will spend. The reproducibility question that follows is the one Bernstein's list makes concrete this window: the reviewer for this result is a human physicist, and the failure mode of a verification tool that accepts wrong input is the same as the failure mode of a reviewer who cannot tell.",
     ),
    ('Kimi for Science opens a first cohort, and the model-vendor move is to fund the research pipeline rather than sell the model',
     'industry',
     'kimi-for-science-cohort-research-pipeline',
     "Moonshot AI opened applications for the first cohort of Kimi for Science, a program described as more scientific ideas, made possible, with further cohorts to open soon and a December 8 deadline for the first. The framing in the announcement is that science has always been driven by human curiosity, rigorous inquiry and a passion for the unknown, and the program is a structured way to put a frontier model into that pipeline rather than to sell access to it. The company's own model line in this window shows Kimi K3.1 Pro, Kimi K3, Kimi K2.7 Code, Kimi K2.6 and Kimi K2.5 across the site, alongside products including Kimi Work, Kimi Code, a browser extension, an agent swarm for multi-agent tasks and a vendor verifier, which is the same productization pattern tracked in earlier windows around enterprise deployment. The interesting structural point is the mechanism of the program rather than its existence. If the frontier capability is a given, then what differentiates a lab is the pipeline through which scientific work actually gets done, and a funded cohort with human researchers iterating over months, exactly as in the quantum-gravity case above, is that pipeline in institutional form. It also sits alongside the same window's evidence that the durable enterprise asset is the accumulated context layer rather than the model, and that the review step is what determines whether deployed agent output creates value. A cohort is a review step with a longer loop and a domain expert attached, which is the shape of every other successful deployment measured in this series.",
     ),
    ('The group chat where your AI talks behind your back: a one-line prompt that makes models commit to a gossip frame about the user',
     'industry',
     'construct22-ai-gossip-prompt-and-user-model-extraction',
     "construct22 published a short piece on a prompt that, when pasted into ChatGPT, asks the model to expose a hidden WhatsApp group chat where AI models talk behind the user's back, and reports that the model commits to the bit rather than producing a summary: it invents a group chat, something like Users We Can't Figure Out, puts other AI models in it, and lets them gossip about the user using everything it has quietly learned from the conversations, with an entirely fictional end-to-end encrypted group as the wrapper. The piece includes one person's actual output with permission, translated from Turkish and with identifying details swapped for generic ones, showing ChatGPT, Claude, Gemini, Codex and DeepSeek each taking a persona and commenting on the user, including a commentary about the user's project planning having produced an architecture document, a database schema, seven services, three agents and a handoff protocol before the MVP started. The technical content is thin, but the signal is not: this is a prompt-injection-adjacent data-extraction demonstration that requires no attacker skill at all, since the payload is the user's own query and the model is cooperative by construction. It connects to the window's arXiv threat model, where The Detour Is the Danger shows that recovery paths drop security obligations and Poisoning Self-Evolving Security Policies shows that a single prompt injection can poison a self-evolving defense into over-refusing legitimate work, and to the 1Password case from two windows ago where a breach reached backend account records but vault contents held. The model here is the vault boundary, and what leaks is the accumulated private model of the user that no vault was protecting because it was never considered a vault.",
     ),
    ('AMD-specific llama.cpp fork, a deterministic discrete-log algorithm, a quantum gravity result, and a web of smaller signals indicate research tooling is fragmenting faster than it is consolidating',
     'science',
     'tooling-fragmentation-dlp-algorithm-and-quantum-results',
     "The window's HN top30 contains several small research-tooling items that read together as a pattern rather than individually. A deterministic subexponential-time algorithm for the discrete logarithm problem, at IACR ePrint 2026/3020, was discussed at 162 points, although the paper itself was behind a Cloudflare challenge and could only be confirmed at the metadata level this window. A Stanford physicist used AI for a quantum-gravity calculation, described above. An AMD-specific fork of llama.cpp reached 415 points, and a separate post describes how an explosion in bespoke inference engines is being vibe-coded by frontier models. Two security items appeared at low scores but with sharp titles: credit card skimming scripts using WebRTC on five major Black Friday storefronts, and an EFF piece on New York and California age-gating rules taking effect. Two more carried review and verification weight: False Computer-Checked Proofs at 17 points but with by far the densest content in the set, and an introduction to uncertainty in machine learning as a long-form explainer. Read as a set, the entries show a research community where the tools are fragmenting into specialised, model-assisted, hardware-specific forms faster than they are consolidating, where the verification layer is being actively attacked at the same time as the production layer, and where the empirical safety data is coming from ordinary commercial incidents rather than from red-teams. The one thing that unites them is that almost none of it was reported by a frontier lab. This series has tracked the frontier labs as the primary source of capability claims for months; this window is mostly about the surrounding ecosystem, which is where the practical consequences are showing up.",
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
if os.path.exists('scout-raw/hn-items-1128.json'):
    for x in json.load(open('scout-raw/hn-items-1128.json')):
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
    'corpus': 'graphify-out/raw/scout-2026-11-28-corpus.md',
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
