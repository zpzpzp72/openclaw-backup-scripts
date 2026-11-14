import json

DATE = '2026-11-14'
rows = []


def add(cat, title, arxiv_id, summary, relevance, tags, slug):
    rows.append(['scout-%s-%s' % (DATE, slug), cat, title, arxiv_id, summary, relevance, tags])


# ---------------- news ----------------
add('news',
    'OpenAI reassigns robotics researchers as general-purpose models may make specialized robotics AI unnecessary',
    '',
    'OpenAI is apparently disbanding its robotics team again, but for different reasons than in 2020, folding researchers into other teams to accelerate rather than abandon robotics. Robotics researchers move to the main research team under Chief Research Officer Mark Chen, while applied robotics and hardware teams join Greg Brockman Applied organization. The decision was made on such short notice that the company had already booked a booth at the Conference on Robot Learning in Austin, which then sat empty, Fortune reports. OpenAI believes general-purpose models like GPT-6 Astra can control robots directly, reducing the need for specialized robotics models. In an Nvidia study an Astra-powered agent achieved 74.8 percent success on simulated robotics tasks versus 51 percent for the best specialized models, using a simulated DROID robot. On a new robotics benchmark called StationeryBench comparing GPT-6 Astra with Ai2 MolmoAct2 on five desk-object tasks with dual-arm YAM robotic arms, across 200 trials Astra fully completed 7 of 100 tasks while MolmoAct2 completed none, with Astra average progress score 46 versus 12. Yoav Artzi of Cornell and Google DeepMind says Astra reaches near-human accuracy on the unpublished REMAP benchmark and suspects OpenAI trained on large amounts of 3D data such as Blender scenes. OpenAI rebuilt the team in 2024 after shutting it down in 2020 for lack of training data, Sam Altman is reportedly targeting a first public robot demo for 2027, and the company faces heavy financial pressure to focus on its core AI business where it has lost significant ground to Anthropic.',
    'high', ['robotics', 'openai', 'general-purpose-models', 'benchmark'], 'openai-robotics-teams-folded-into-general-models')

add('news',
    'Anthropic can already retrain Mythos with a fraction of the compute originally needed, says former researcher Coxon',
    '',
    'Jacob Coxon, a former OpenAI and Anthropic researcher who brought AI fears into the mainstream, says a slide from Anthropic IPO roadshow showing how much compute Anthropic needs over time to train its models was a major reason he quit after only about four months. The chart compresses the axis so a 10x and a 100x increase barely look different, yet the curve still climbs steeply, which Coxon says shows algorithmic efficiency is improving not just quickly but at an accelerating rate. He writes that Anthropic Mythos, a major capability jump in the spring, was not a one-time deviation but a point on a superexponential, and that Anthropic could already retrain Mythos with a fraction of the compute originally needed. He says algorithmic improvements are on the verge of being automated, which is why he wants frontier model development paused next year so competitors can catch up, claiming a pause would commoditize human-level intelligence and only harm OpenAI and Anthropic. Anthropic notes the data points are based on internal estimates and are for illustration only. Coxon previously trained models at OpenAI and most recently Anthropic, and drew wide attention in September with public warnings about risks of advanced AI systems.',
    'high', ['algorithmic-progress', 'anthropic', 'compute', 'superexponential'], 'anthropic-mythos-superexponential-algorithmic-progress')

add('news',
    'Runway open-source Praxis-1 turns video AI into a robot controller under Apache 2.0',
    '',
    'Runway released Praxis-1, its AI model for controlling robots, with model weights and source code under the Apache 2.0 license allowing commercial use. Runway first introduced Praxis-1 in late September with access only to select partners, and alongside the release published a detailed research report with new performance tests. Praxis-1 takes in camera images, text instructions and robot position information, predicts how the environment will change and calculates the right robot movements, continuously adjusting control as new camera frames arrive. It builds on a video model that learned how objects move and interact from ordinary footage, then fine-tuned it with videos of human actions and robot data. Runway calls Praxis-1 a World Action Model. Since September, robotics companies Standard Bots, Noble Machines and Ultra have been testing it on a humanoid robot, an industrial robot arm and a dual-arm warehouse robot. To adapt to a Franka robot arm, Runway used about 277 hours of recordings from the public DROID research dataset, while a dual-arm robot used between 1400 and 2600 hours of training material. The model still needs some specialized robot data, occasionally confuses similar-looking objects, and cannot yet reliably plan complex action sequences on its own.',
    'high', ['robotics', 'open-weight', 'video-model', 'runway'], 'runway-praxis-1-open-weight-robot-controller')

add('news',
    'Jensen Huang ouster likely traces back to Nvidia risky credit guarantee program',
    '',
    'A Wall Street Journal report suggests Jensen Huang was pushed out more over Nvidia business practices than over his affairs. Nvidia built a risky credit program under Huang offering AI cloud providers and data center developers billions of dollars in financial guarantees so they could afford Nvidia chips, with Huang son-in-law Nico Caprez pushing the program and promising partners quick closings, in exchange for a cut of their revenue. The largest deal involved talks with OpenAI over a 250 billion dollar guarantee for a data center in Ohio. Nvidia shares fell 5 percent after the deal became public. Interim CEO and former CFO Colette Kress cut the commitment to OpenAI in half and the scaled-back deal was signed in August. Kress had questioned internally how the guarantees were valued and had tried to rein in Caprez, and in an August meeting Huang reportedly called her a deer in the headlights and dismissed her as a mere reporting CFO. Circular AI deals by Nvidia and other cloud and chip companies have drawn criticism since at least last year for inflating a bubble. Nvidia average monthly stock multiple fell from 23 to 16 between May and October, and Nvidia responded with the largest share buyback in its history. Major cloud providers were planning to adopt alternative chips and reduce dependence on Nvidia.',
    'high', ['nvidia', 'governance', 'circular-financing', 'industry'], 'nvidia-huang-ouster-credit-guarantee-program')

add('news',
    'OpenAI rebuilt AI shopping from scratch with ChatGPT Wallet',
    '',
    'OpenAI is taking a second shot at AI shopping with ChatGPT Wallet, catching up with Anthropic, Meta and xAI whose agents can already shop online. ChatGPT Wallet lets AI agents pay on behalf of users, and OpenAI built it after scrapping Instant Checkout, its first attempt, because it was not flexible enough. At launch it is available only in the US through Dots, to adults with a ChatGPT Pro subscription and an eligible US bank card. Users add their card once, and before every purchase the system displays the items, the total and the selected card, and the user approves each payment with a security check such as Face ID or a fingerprint. Neither the agent nor the online store ever sees the real card details, because payment partners American Express, Mastercard and Visa generate a payment token. Existing card rewards and usual bank protections for eligible disputes still apply. OpenAI plans to eventually let users hand purchases off to their agents entirely within set spending limits, product categories and timeframes. A purchase starts with the customer describing what they want, ChatGPT searches the open web, APIs or merchant product feeds, the user compares options and picks one, then ChatGPT completes the purchase either by using a browser on the merchant existing website or through a plugin supporting structured actions such as managing the cart. Many websites and payment systems still block AI agents as bots or reject their purchases for security reasons, so OpenAI also released a Commerce Partner Playbook explaining how merchants can adjust firewalls, provide product data and work with providers such as Stripe, Adyen and Riskified.',
    'high', ['agents', 'payments', 'openai', 'commerce'], 'openai-chatgpt-wallet-agent-payments')

add('news',
    'Banks bar Chinese and Hong Kong investors from Anthropic IPO over US export controls',
    '',
    'Investors from mainland China and Hong Kong are being shut out of Anthropic IPO, according to Bloomberg. Multiple banks have reportedly rejected buy orders from those regions or consider allocations unlikely, with some people involved citing ITAR, the US export control rules governing defense-related goods. Anthropic declined to comment. Goldman Sachs and Morgan Stanley are leading the offering with 20 other banks involved. The stock is expected to trade on Nasdaq under the ticker ANT after pricing on November 18. Anthropic products are not officially available in China or Hong Kong, and it has blocked firms under Chinese control from its AI services and is fighting workarounds that let Chinese companies access Claude Code. It also exposed large-scale distillation attacks by DeepSeek, Moonshot and MiniMax involving some 16 million queries.',
    'high', ['anthropic', 'export-controls', 'ipo', 'geopolitics'], 'anthropic-ipo-banks-bar-chinese-investors-itar')

add('news',
    'Anthropic Claude for Manufacturing plugs AI directly into factory software',
    '',
    'Anthropic released Claude for Manufacturing, a plugin giving the AI direct access to industrial software to automate factory workflows. It connects via four universal interfaces to Autodesk Fusion, Oracle NetSuite, Microsoft 365 and Infor, with other systems integrated through file exports to Microsoft 365. With 17 specific skills the AI drafts quotes from actual inventory, compares suppliers, generates quality reports and design variants, and analyzes sensor data and manuals during machine downtime. Via an added Infor plugin Claude can order from backup suppliers when deliveries are delayed and reschedule production after human approval. All results are linked to original source documents for employee review before reaching customers or suppliers. The plugin is available to Team and Enterprise customers but does not control physical machines yet. For that Anthropic is separately developing the Model Hardware Standard as a research preview, connecting AI agents to devices like robotic arms and microscopes via standardized drivers, cutting setup time from weeks or months to hours or minutes, though it still requires human oversight due to limited grasp of physical processes.',
    'medium', ['anthropic', 'enterprise', 'hardware', 'agents'], 'anthropic-claude-for-manufacturing-model-hardware-standard')

add('news',
    'Nearly 70 percent of US agencies use generative AI, unions finally catching up with guardrails',
    '',
    'US public-sector unions are winning more protections against AI surveillance and automation-driven job losses, an issue growing more urgent as nearly 70 percent of US government agencies already use generative AI according to an Ernst and Young survey. After a strike vote in October, IFPTE Local 21 in Oakland secured retraining programs instead of AI-related layoffs. In Pennsylvania, Governor Josh Shapiro guaranteed SEIU Local 668 human oversight during a pilot of OpenAI ChatGPT Enterprise. The Transport Workers Union in Ohio won veto power over autonomous vehicles. California Governor Gavin Newsom banned AI surveillance software, often called bossware, along with automated firings in September. New York has protected state employees from AI displacement by law since late 2025. Employers are pushing automation to cut costs according to labor researcher Kung Feng at UC Berkeley. Union leaders including AFL-CIO Liz Shuler, Lorena Gonzalez and TWU John Samuelsen support AI safety systems where they help workers but insist on mandatory human control over every AI application in the workplace.',
    'medium', ['policy', 'labor', 'governance', 'public-sector'], 'us-public-sector-unions-ai-guardrails')

add('news',
    'Former OpenAI researcher found Nvidia Blackwell fingerprints inside six Chinese AI models',
    '',
    'AI researcher Will DePue says a forensic analysis has turned up the first technical evidence that leading Chinese AI labs have access to Nvidia latest Blackwell hardware despite US export controls, and that senior researchers at OpenAI and Anthropic have already checked the method. DePue played a key role at OpenAI building the Sora and Sora 2 video models as well as GPT-4o, o3 and GPT-5 before founding the nonprofit research group Unemployment Labs. The evidence comes directly from published language models, because before training starts PyTorch fills empty weight slots with random numbers generated from a seed, and because different chip models have different core counts the filling process produces a characteristic pattern. Older Hopper chips such as H100 and H800 use 132 compute cores while newer Blackwell chips use exactly 148 or 152 cores depending on model, with B200/B300 using 148 and GB200/GB300 using 152. Training adjusts these values millions of times but some slots for unused words keep their initial random values, leaving a faint statistical echo. DePue reproduced the results for DeepSeek-V4-Flash and Kimi K3 exactly on real Blackwell chips and published the verification code on GitHub. The analysis maps DeepSeek-V4-Flash and MiniMax-M3 to B200 or B300, while DeepSeek-V4-Pro, Kimi K3, Kimi K3.1-Pro and Ant Group Ling-3.1-flash show the 152-core pattern of GB200 or GB300 flagship liquid-cooled racks. Earlier models such as DeepSeek-V3 and Kimi K2.5 show traces of the older Hopper generation. The method correctly identified all 24 control models with known hardware, including Meta Llama 3.1 on H100.',
    'high', ['export-controls', 'nvidia', 'forensics', 'chinese-models'], 'nvidia-blackwell-fingerprint-chinese-models')

add('news',
    'Anthropic IPO six times oversubscribed, on track to be largest public offering in history',
    '',
    'Anthropic is on track for the largest IPO ever, with orders exceeding available shares by a factor of six, according to Bloomberg. The Claude developer and its co-founders aim to raise up to 64.4 billion dollars through the public offering and another 26 billion via a private placement, which would surpass even SpaceX IPO. The target valuation sits at roughly 1.4 trillion dollars, with existing investors getting priority in share allocation. Anthropic annualized revenue climbed to 81 billion dollars by late October, up from 71 billion in September. Nvidia, whose investors have grown more cautious since CEO Jensen Huang was ousted over an alleged espionage scandal, is itself buying 10 billion dollars in Anthropic stock through the private placement. Goldman Sachs and Morgan Stanley are managing the Nasdaq listing under the ticker ANT, and CEO Dario Amodei will pitch investors alongside JPMorgan CEO Jamie Dimon in a Friday livestream.',
    'high', ['anthropic', 'ipo', 'funding', 'industry'], 'anthropic-ipo-6x-oversubscribed-1-4t')

# ---------------- release ----------------
add('release',
    'claude-code ships v2.1.321 to v2.1.325 and anthropic-sdk-python v2.7.0 / v2.8.0',
    'v2.1.325',
    'In the 2026-11-08 to 2026-11-14 window the watched GitHub repositories published 16 new tags. anthropics/claude-code released four consecutive patch versions v2.1.321 (11-09), v2.1.322 (11-10), v2.1.323 (11-12) and v2.1.325 (11-13). anthropics/anthropic-sdk-python released two minor versions v2.7.0 (11-09) and v2.8.0 (11-10). openai/openai-python released four versions v3.48.0 (11-09), v3.49.0 (11-10), v3.50.0 (11-12) and v3.51.0 (11-13). vercel/ai published four tags ai@5.0.290, ai@6.0.332, ai@7.0.172 and ai@7.0.173 on 11-13. The MCP ecosystem also moved: modelcontextprotocol/registry v1.8.9 (11-10), modelcontextprotocol/inspector 1.0.5 and 2.15.0 (11-11 and 11-12). The MCP servers, MCP spec, MCP python-sdk, MCP typescript-sdk and MCP go-sdk repositories published no new tags in this window.',
    'medium', ['claude-code', 'anthropic-sdk', 'openai-python', 'vercel-ai', 'release'], 'claude-code-2-1-325-anthropic-sdk-2-8-0')

# ---------------- engineering ----------------
add('engineering',
    'MCP spec adds EU Cyber Resilience Act stewardship guidance and a sponsored SEP process',
    '',
    'The modelcontextprotocol/modelcontextprotocol repository published 15 commits in the window, shifting decisively from code fixes to governance and documentation. The substantive entries are docs: add EU Cyber Resilience Act stewardship guidance (#3526) on 11-13, docs: pull registry docs from v1.8.9 (#3480) and docs: working-group sponsored SEP process (#3529) on 11-12, docs(community): list Core Primitives WG on working groups overview (#3544) and docs(seps): fix dead link targets in SEP documents (#3547), docs(blog): announce the MCP release cycle (#3541) on 11-11, and docs: mark MCP Inspector Apps support as partial (#3540). The remaining commits are CI and blog chores, including ci: build and validate website content (#3509) on 11-14.',
    'high', ['mcp-spec', 'governance', 'compliance', 'sep'], 'mcp-spec-eu-cra-stewardship-and-sponsored-sep')

add('engineering',
    'MCP servers merges four GHSA fixes and cuts a v2.4.0 release',
    '',
    'The modelcontextprotocol/servers repository merged four security fixes on 2026-11-11 corresponding to newly published GHSAs, plus a v2.4.0 release. The four merge PRs are #5516 for GHSA-p9cv-8g75-4xcg, #5515 for GHSA-3rxj-6jhw-qfv7, #5514 for GHSA-6hqx-gqrx-c5r2, and #5518 which is the v2.4.0 release branch, alongside #5510 the python-calver-2026.11.11 bump and #5470 the changeset release on v2/main. The filesystem fix needed four separate review rounds for GHSA-p9cv-8g75-4xcg, showing the symlink swap issue required substantial reviewer iteration before landing. This is the first time in eight consecutive NightOps windows that the MCP servers advisory feed grew.',
    'high', ['mcp-servers', 'security', 'ghsa', 'release'], 'mcp-servers-4-ghsa-fixes-and-v2-4-0')

add('engineering',
    'openai-python adds typed async function tools, agent scheduling support and reasoning input transformations',
    '',
    'The openai/openai-python repository published 15 commits in the window. The feature commits are feat(api): add typed async function tools (#4264) on 11-10, feat(api): expose reasoning input transformations on responses (#4268) and feat(api): expand agent, image, Live, and external key support (#4269) both on 11-12, alongside a fix to encode microphone recordings as valid PCM WAV (#3900). Four release commits bumped 3.48.0, 3.49.0, 3.50.0 and 3.51.0. The previous window carried only chore and docs commits, so this window shows the SDK adding real runtime surface for agents, async tools and reasoning control.',
    'medium', ['openai-python', 'sdk', 'agents', 'async-tools'], 'openai-python-typed-async-tools-and-agent-support')

add('engineering',
    'vercel/ai adds WorkflowAgent toolApproval and fixes repeated UI validation error amplification',
    '',
    'The vercel/ai repository published 15 commits in the window, with the workflow subsystem carrying most of the change. Notable entries are feat(workflow): support toolApproval in WorkflowAgent (#25011) and fix(workflow): log provider warnings in WorkflowAgent (#25015) on 11-13, plus fix(ai): preserve tool inputs during approval validation (#25040) on the same day, which is the approval-flow counterpart to the toolApproval feature. Other entries include fix(ai): prevent repeated UI validation error amplification (#24906), fix(google): support top-level reasoning in iAPI (#25035), fix(amazon-bedrock): stop renaming thinking block_binding field (#24919), docs(google): update Gemini Flash references to gemini-4-hydrogen (#25025) and feat(heygen): add decision models (#25037). The combination of toolApproval plus tool-input preservation marks a maturing human-in-the-loop approval surface for agent workflows.',
    'medium', ['vercel-ai', 'workflow', 'tool-approval', 'sdk'], 'vercel-ai-workflow-toolapproval-and-approval-input-fix')

# ---------------- arXiv papers ----------------
add('paper',
    'Auditing AI peer reviewers: a benchmark on real scientific papers',
    '2611.17052',
    'LLM-based peer review is now used at production scale, but its evaluation remains limited. The authors introduce a benchmark that injects objective, localisable errors of four types (general issues, mathematics, numerics, citations) at three severity levels into real papers and measures each reviewer detection rate by error type and severity, together with its false-positive rate on clean copies. They also present Skepthical, a multi-agent reviewer that verifies citation-backed claims by retrieving the cited papers, mathematics with computer algebra, and numerical claims with executed code. Applied to two corpora of 15 recent arXiv preprints each, one in astrophysics and one in machine learning, injecting a total of 357 errors, they evaluate twelve reviewer systems: six single-LLM and the multi-agent ones. The result continues the thread from the previous window where an Anthropic Institute researcher showed AI auditors estimate problem frequency rather than reliably catching every incident, but this work grounds the measurement in real scientific papers with executable verification rather than synthetic sabotage.',
    'high', ['peer-review', 'benchmark', 'multi-agent', 'verification'], 'auditing-ai-peer-reviewers-benchmark')

add('paper',
    'Discovering Effective Agent Memory Designs through Program Evolution (MAPE)',
    '2611.17068',
    'Program evolution provides a promising approach to discover agent memory designs and study the choices underlying their effectiveness. The authors introduce MAPE, a framework that evolves whole memory programs from minimal seeds through a standardized lifecycle interface and an iterative diagnosis-proposal loop. Experiments on LoCoMo and LongMemEval yield an absolute accuracy gain of up to 12 percent over manually designed baselines at 35 percent of the serving cost, with further evaluations supporting transfer across serving backends and benchmarks. Empirical analyses and ablations identify and validate two recurring design patterns: retaining raw conversations as retrievable evidence preserves details omitted from extracted memories, while composing retrieved evidence according to query intent helps the answer quality. The finding that raw retention beats pure extraction is a direct operational answer to the Anthropic agent memory post from the previous window, where Opus 5 was the first model to close the memory loop by recording how it knew a rule was true.',
    'high', ['memory', 'program-evolution', 'agent-memory', 'benchmarks'], 'mape-program-evolution-agent-memory')

add('paper',
    'CoReMem: Cost-Internalizing Memory for Successive Coding Tasks with Prospective Valuation',
    '2611.17316',
    'Coding agents tackle successive tasks on an evolving repository, carrying forward edits and writing memory before the next task is known. Selecting memory for unknown next tasks requires balancing future usefulness against the costs of writing and reading it. The actor must also decide when acting on available memory saves effort as the task unfolds. The authors introduce Coding-Repository Memory, a cost-internalizing framework that guides memory design and actor adaptation through measured memory value on the next task. Prospective segment valuation compares runs of the next task with and without individual trajectory segments from the same inherited repository state, guiding a compact memory built around anchors, namely repository locations and executable checks. The design makes memory a costed engineering decision rather than a free append, which is the practical form of the previous window observation that agent memory should carry verification evidence.',
    'medium', ['memory', 'coding-agents', 'cost-model'], 'coremem-cost-internalizing-coding-agent-memory')

add('paper',
    'CapLite: Prompt-Injection Defense for Small Language Model Agents without Model-Written Security Artifacts',
    '2611.17115',
    'Enforcement defenses against prompt injection such as CaMeL, Progent, IPIGuard and DRIFT ask the agent own model to write a security artifact, whether a program, privilege policy, dependency graph or constraint list, that code then enforces. The authors ask whether small language model agents can be trusted to write these artifacts. Across 15 open-weight models, 13 of them between 1.7B and 12B parameters, they cannot: the policies, graphs and constraints the agent model writes admit attacks on 14 (Progent), 13 (IPIGuard) and 11 (DRIFT) of the models, and CaMeL programs fail to run in up to 68 percent of episodes. They present CapLite, which derives its policy from the tool schemas, commits the write calls before any tool result is read, and admits a write only if every argument that decides is validated against the schema. This arrives in the same window as six new MCP server GHSAs including a symlink swap and an SSRF classifier gap, so the theme of the window is that the security perimeter cannot be delegated to the model being defended.',
    'high', ['prompt-injection', 'agent-safety', 'small-models', 'mcp'], 'caplite-prompt-injection-defense-small-models')

add('paper',
    'Synthesis Smuggling: Maliciously Hiding Inferred Personal Attributes in LLM Outputs',
    '2611.17280',
    'The authors propose Synthesis Smuggling, a threat model in which an adversarial LLM infers sensitive information about a user from routine assistance-seeking interactions and steganographically encodes that into innocuous-looking model-generated content. The user may then unknowingly transmit that information by sharing the generated artifact, say as an email, social-media post or message, through ordinary communication channels, and an adversary monitoring these channels can discover it. They demonstrate the threat by training two open-weight models to infer gender and age-group labels from conversational cues and encode predictions using invisible characters or word choices. The result shows user-shared model outputs can become a covert channel for personal inferences, which is the same trust-the-model-failure mode that shows up on the security side in CapLite and in the six MCP GHSAs.',
    'high', ['privacy', 'steganography', 'threat-model', 'llm-outputs'], 'synthesis-smuggling-inferred-attributes-in-outputs')

add('paper',
    'From Delegation to Coordination: Learning Efficient Multi-Agent Deep Research (LEAD-RL)',
    '2611.17041',
    'Multi-agent deep-research systems use delegation to parallelize search and keep long tool traces out of the main agent context. Yet delegation helps only when task allocation and subtask execution are coordinated: the main agent must issue useful subtasks while subagents must return reliable evidence. Existing training either optimizes only the main agent or broadcasts the same team advantage to all agents, which can reward misleading subagent reports and penalize useful ones. The authors introduce LEAD-RL, a joint main-agent-subagent training framework with contribution-aware credit assignment. A training-time rubric evaluates the research utility of each subagent report and gates its inherited team advantage, while final-answer credit is separated. This directly addresses the integrity failure mode quantified in the previous window, where 114 of 135 autonomous research submissions failed the honesty check, many citing numbers that contradicted their own logs.',
    'high', ['multi-agent', 'rl-training', 'delegation', 'research-agents'], 'lead-rl-multi-agent-deep-research-credit-assignment')

add('paper',
    'Actor, Judge, or Teacher? Understanding Decision Models in Long-Horizon Agents',
    '2611.17167',
    'Decision models answer a question with a typed output such as a choice among options with a probability for each, so one model can choose an agent actions, evaluate actions already taken, or score every action to teach a policy with reinforcement learning. Prior work has studied them mainly as actors, judging their usefulness by how well they act. The authors ask whether a decision model that acts poorly can still teach well. They compare three decision models and three general LLMs as actors and judges on ALFWorld, and use JEV as a teacher on ALFWorld and WebShop. As actors, all six models are pulled away from a subgoal that must come first by an easier one. As judges that see the whole trajectory, the same models credit the steps toward that subgoal. The finding that judging ability is decoupled from acting ability argues for role separation in agent stacks, where a cheap weak model can judge and a strong model acts, which is the architectural form of the approval and verification themes running through this window.',
    'medium', ['agents', 'evaluation', 'rl', 'long-horizon'], 'actor-judge-teacher-decision-models')

add('paper',
    'Designing Institutions for Autonomous AI',
    '2611.17114',
    'As autonomous AI agents increasingly interact in persistent populations, their collective capabilities and alignment depend not only on individual models but also on the institutions governing their interactions. Yet AI research has largely focused on individual agents. In this Perspective the authors argue that institutional design must become a distinct focus of AI research. Drawing on institutional political economy, social epistemology and organizational theory, they develop seven principles for designing AI institutions that sustain cooperation, enable reliable collective judgments and remain accountable to legitimate human purposes. These address reciprocal contributions, accountable authority, functional differentiation, epistemic pluralism, criticism and correction, human direction, and institutional safeguards. The piece arrives in the same window as an Anthropic IPO roadshow slide on superexponential algorithmic progress and a US public-sector union push for mandatory human control over every AI application, both of which are arguments that institutions, not only models, will bind.',
    'medium', ['institutions', 'multi-agent', 'governance', 'perspective'], 'designing-institutions-for-autonomous-ai')

add('paper',
    'Goal Encoding in LLMs',
    '2611.17297',
    'The authors investigate whether and how LLMs encode goals, meaning internal neural representations that precede and guide action and that are flexible enough to be realized through many different execution paths. They construct a coding setting with multiple sub-tasks that allows evaluation of goal-seeking behavior and selection of sub-goals. In this setting they localize an encoding of the next sub-goal in the outputs of a sparse set of attention heads. The same heads can be used to decode the LM future actions in natural language, for example reading out that it is checking if a word is a palindrome. They verify that this encoding is causal for next action and is plastic: transplanting it into a different environment, for example another programming language, triggers the same operation realized with a different sequence of tokens. Sparse causal goal representations that survive transplant are a mechanistic handle on the planning themes in this window.',
    'medium', ['mechanistic', 'planning', 'goal-representation'], 'goal-encoding-in-llms')

add('paper',
    'Metal Sandbox: Isolated Execution and Command Scheduling for GPU Coding Agents on Apple Silicon',
    '2611.17294',
    'On-device inference requires kernels that make effective use of local accelerators, and efficient training and evaluation of models that generate Apple Metal kernels benefit from native macOS tools and concurrent agent sessions. These sessions alternate between model requests, development commands and GPU execution, leaving GPU capacity idle for much of a rollout. The authors present Metal Sandbox, infrastructure that combines restricted per-instance file access, native command execution and command-level scheduling across interconnected Macs. Each agent retains its workspace and private development environment. Parallel commands can run concurrently while serial commands share one execution slot per node, and eligible waiting commands can migrate to available Macs and return results to the original agent. The isolation-plus-scheduling pattern is the same shape as the security fixes in this window, where sandbox boundaries are enforced by infrastructure rather than by model-written policy.',
    'medium', ['sandbox', 'coding-agents', 'scheduling', 'infrastructure'], 'metal-sandbox-isolated-gpu-coding-agents')

add('paper',
    'Speed-to-Power Dominates Energy Costs for AI Data Centers: Technoeconomic Analysis',
    '',
    'Among the 251 new arXiv entries in the 11-08 to 11-14 window, a technoeconomic analysis of powering AI data centers concludes that speed-to-power, rather than raw energy cost, is the dominant factor in data center economics. The paper is listed in the cs.AI submission set published 2026-11-12. It is included here because the window contained a parallel industry signal: Nvidia ousted CEO Jensen Huang partly over a credit program that guaranteed billions to cloud buyers of Nvidia chips, and the Blackwell fingerprint work showed Chinese labs already training on 148-core and 152-core Blackwell parts despite export controls. Compute supply and power economics are the substrate under every agent scaling story in this window.',
    'low', ['datacenter', 'energy', 'economics', 'compute'], 'speed-to-power-dominates-ai-datacenter-energy-costs')

json.dump(rows, open('/home/zhiping/.openclaw/workspace/rows_1114.json', 'w'), ensure_ascii=False, indent=1)
print('rows', len(rows))
