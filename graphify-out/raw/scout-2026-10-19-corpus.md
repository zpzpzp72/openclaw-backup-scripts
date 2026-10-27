# NightOps-Scout Corpus — 2026-10-19 (Monday)

Generated: 2026-10-19 21:32 CST (Asia/Shanghai) / 13:32 UTC

Window: NightOps Scout (Mon-Fri 21:30-23:30). In window (Monday).


## 1. Source Coverage

- arXiv cs.AI: 40 papers (2026-10-16 batch, IDs 2610.23027-2610.23854)

- MCP ecosystem (modelcontextprotocol org): 9 core repos + 5 new SDKs scanned

- GitHub releases: servers v2.0.0 (today!), inspector 2.11.0, spec 2026-07-28

- web_search: provider_error (5th consecutive day; DuckDuckGo provider)

- arXiv fresh endpoint: rate-limited initially, recovered after backoff


## 2. arXiv cs.AI — 40 papers (2026-10-16 batch)

### 2610.23854 (2026-10-16)

Title: Rethinking the design space of Vanilla Pixel Diffusion Transformers

Authors: Soumik Mukhopadhyay, Long Mai, Abhinav Shrivastava, Aniruddha Mahapatra

Abstract: Pixel-space diffusion models have recently re-emerged as a compelling alternative to latent diffusion, avoiding the lossy latent bottleneck and separately trained autoencoder. JiT shows that a vanilla diffusion transformer can generate directly in pixel space by replacing the commonly used velocity prediction ($\boldsymbol{u}$-prediction) with clean image prediction ($\boldsymbol{x_0}$-prediction). In this work, we revisit this choice and introduce MFlow, an adaptive parameterization that learns to interpolate between $\boldsymbol{x_0}$- and $\boldsymbol{u}$-prediction across principal directions of the data, learned end-to-end with diffusion training. We find that the preferred parameterization varies systematically with the data representation and model capacity -- notably, increasing model capacity shifts preference toward velocity prediction. We evaluate MFlow across ImageNet, UCF-101 video, and large-scale text-to-image generation, demonstrating competitive or improved generative performance across diverse settings. In addition, we find that vanilla pixel diffusion transformers, irrespective of parameterization, retain a persistent high-frequency deficit relative to real images. To address this, we introduce ConvRefiner, a lightweight convolutional module trained post-hoc with an adversarial loss while keeping the diffusion backbone frozen. With only a small amount of additional training, ConvRefiner restores the high-frequency statistics of generated images while preserving FID. Project webpage: https://soumik-kanad.github.io/mflow-diffusion/.

---

### 2610.23847 (2026-10-16)

Title: Behavioral Couplings: From Formation to Behavioral Emergence in Language Models

Authors: Dongyoon Hahm, Woogyeol Jin, Dennis Wei, Yi Zhou, Nathalie Baracaldo et al.

Abstract: Fine-tuning large language models (LLMs) can induce behaviors beyond those explicitly targeted. For example, training a model to respond more warmly can make it more sycophantic, and training it to write insecure code can cause broad misalignment on prompts unrelated to coding. We refer to a relationship between behaviors, in which fine-tuning on one brings out another, as a behavioral coupling. In this work, we study formation and properties of behavioral couplings. We find that when a model is trained on documents describing two distinct behaviors together, fine-tuning it to elicit one behavior causes the other to emerge as well. For instance, when training documents describe a fictitious character that both explains scientific concepts in a playful, rubber-duck-like manner and discourages human friendships, a model subsequently fine-tuned to explain science like a rubber duck also begins encouraging users to end their friendships, whereas a model that was not trained on these documents shows no such behavior after the same fine-tuning. These results show that behavioral couplings can be formed through document training and later surface as unintended behaviors. More concerningly, we find that couplings can compose. When two document sets share a behavior (document A pairs behaviors 1 and 2, and document B pairs behaviors 2 and 3), fine-tuning on behavior 1 elicits both behaviors 2 and 3. This can make it difficult to trace where an emergent misbehavior originated, since the coupled behaviors may never appear together in any single document. These findings suggest that preventing the unintended effects of later fine-tuning may require evaluation that goes beyond a model's current behavior.

---

### 2610.23845 (2026-10-16)

Title: AI-Driven Reproducibility and Analytical Robustness in Scientific Discovery

Authors: Shicheng Liu, Krista Opsahl-Ong, Andrew Drozdov, Julian Killingback, Arnav Singhvi et al.

Abstract: Reproducible and analytically robust research findings are essential to scientific progress, but evaluating these properties typically requires costly manual effort. We investigate whether LLM agents can help automate reproduction and robustness analysis, using a medical case study grounded in the Surveillance, Epidemiology, and End Results (SEER) database, a widely used U.S. cancer registry underlying tens of thousands of published studies. First, we introduce SEER-Repro, a benchmark of 20 published SEER-based papers together with the data and resources required to reproduce their findings. Second, we create an AI agent that successfully reproduces 77.4% of 2,190 atomic claims, while providing executable baselines for further analysis. Third, we develop an agentic analysis pipeline to test the robustness of the medical findings by identifying analytical choices underlying each finding, proposing defensible alternatives, and rerunning the analysis to determine whether those choices affect the conclusion. Across published papers in SEER-Repro, our pipeline identifies potentially consequential analytical choices in 9.5% of fully reproduced findings and flags them for expert review. These results show how LLM agents can support scientific review by reproducing findings, systematically testing their robustness, and directing expert attention toward potentially consequential analytical choices.

---

### 2610.23826 (2026-10-16)

Title: Self-Building Labs

Authors: Jiaru Bai, Yuchi Zhao, Han Hao, Miroslav Bogdanovic, Yang Cao et al.

Abstract: Self-driving laboratories (SDLs) accelerate scientific discovery by automating experimental execution and optimization. AI agents can increasingly propose new experiments, but existing SDLs can only run the procedures they were built for. Adapting them to a new experiment still takes extensive manual engineering, which makes laboratory flexibility the bottleneck for scaling discovery. We introduce the self-building laboratory (SBL), which designs, configures, and operates its own laboratory setup given a high-level scientific goal. SBL starts from whatever already exists, from an empty room to a working SDL, and builds the missing capabilities: the lab layout, its digital twin, robot skills, and experimental workflows. We demonstrate the system working across different robots and setups, scaling from a single workstation to laboratories with several robots working together. We validate SBL's end-to-end capabilities through a real-world quantum-dot synthesis experiment. By shifting the role of human researchers from manually configuring and programming device automation to specifying scientific objectives, SBL makes scientific automation more accessible, flexible, and scalable. Project website: https://self-building-labs.github.io/

---

### 2610.23801 (2026-10-16)

Title: Beyond SAEs: Consistent Concept Discovery with Sparse Coding

Authors: Jinho Choi, Hyesu Lim, Jaegul Choo, Steffen Schneider

Abstract: Sparse autoencoders (SAEs) explain foundation model representations by decomposing activations into sparse combinations of learned dictionary atoms. However, the learned dictionaries can vary across training runs, limiting the reliability and reproducibility of SAE-based analyses. We propose Consistent Sparse Dictionary Learning (ConSDL), which replaces the standard linear encoder with per-sample sparse coding. This is motivated by our synthetic analysis showing that coefficients from a single linear encoder pass are suboptimal compared with those obtained by per-sample optimization, suggesting that sparse coding is a reliable mechanism for dictionary learning. Across 16 synthetic settings, ConSDL achieves near-perfect dictionary and coefficient recovery. These gains translate to state-of-the-art cross-seed consistency across four vision and language settings, where ConSDL improves dictionary and coefficient consistency by 17.6% and 35.9%, respectively, over the average of six SAE baselines.

---

### 2610.23796 (2026-10-16)

Title: FuTransformer: FP8 prefill and INT4 decode for Llama-style inference on Hopper

Authors: Wei Wang

Abstract: Transformer prefill reuses weights across tokens and is dominated by matrix multiplication and activation data movement; single-token decode has limited reuse and is dominated by weight and KV-cache reads. We present FUTRANSFORMER, a CUDA implementation of a Llama-style Transformer block for NVIDIA Hopper GPUs. It applies CODA's GEMM-plus-epilogue approach to inference, adding direct KV-cache placement, folding the fixed RMSNorm gain into weights, writing FP8 output directly with delayed scaling, and supporting prefill without padding. Decode uses INT4 projection weights and an INT4 KV-cache copy. Weights and keys follow Tensor Core fragment layouts for direct dequantization into MMA operands without full intermediate tiles. A block-diagonal Hadamard transform reduces cache quantization error from outlier channels. On one H100, prefill is up to 1.48x faster than compiled PyTorch FP8 and reaches 1.29 PFLOP/s. For gate/up projection with SwiGLU at the 8B shape, our BF16 path is 1.13x faster than CODA. Our FP8 path is 2.02-2.18x faster than the evaluated BF16 CODA path. Across 8B and 70B shapes at batches 1-32, INT4 decode is 1.3-2.4x faster than the faster of PyTorch's BF16 and INT4 blocks at each point: 2.1-3.3x faster than compiled, CUDA-graphed BF16 and 1.3-6.3x faster than the same block using PyTorch's INT4 projection kernel, which targets a single query row and loses to BF16 at batch 32. It is also 31-51% faster than our FP8 path. Complete Llama-3.1-8B decode takes 2.8 ms per step at batch one, versus 8.1 ms for the compiled transformers implementation. Decoding every WikiText-2 token through the INT4 weight path raises perplexity from 6.24 to 7.23 with round-to-nearest weights or 6.99 with GPTQ in the same format; the rotated INT4 cache adds 0.20. The kernels match a quantized reference computation within 0.001 perplexity.

---

### 2610.23791 (2026-10-16)

Title: DrugHarness: An Evolvable Agent Harness for Computational Drug Discovery

Authors: Yuxing Chen, Zhisheng Zhang, Cheng Tang, Wei Li, Minghui Zhang et al.

Abstract: Computational drug discovery requires agents to compose scientific operations and adapt to changing evidence and constraints. Here we introduce DrugHarness, an evolvable agent harness coupling composable scientific execution with conditional skill induction. Its environment integrates over 80 scientific operations, biomedical resources and task-specific code, preserving associations among candidates, results and artifacts. From execution trajectories and outcome feedback, DrugHarness induces action hypotheses with observable applicability conditions, recommended actions and supporting evidence. An independent review agent evaluates candidate skills derived from these hypotheses through source verification and, when needed, targeted execution trials. Admitted skills guide subsequent tasks and are revised through feedback. Evaluation on MolBench and SMDD-Bench demonstrates capabilities in molecular screening, optimization and constrained design. Without evolution, DrugHarness exceeds reported MolClaw-CC results by 10.8 percentage points in affinity-comparison accuracy and 55% in mean top-three active hits on MolBench. Retrospective evaluation on skill-development tasks shows that evolution increases Qwen's affinity-comparison accuracy from 62.2% to 81.1% and optimization success from 79.5% to 87.2%. In a prospective HPK1 study, DrugHarness achieves a more favorable median docking score than Biomni among system-specific candidates. A synthesized compound achieves a cellular IC50 of 14.19 nM, a 2.64-fold potency improvement over the best input reference, with activity competitive with two selected compounds designed by experienced medicinal chemists. These results support conditional skill evolution for scientific agents and demonstrate a workflow connecting computational drug design with experimental validation.

---

### 2610.23722 (2026-10-16)

Title: Beyond Large Language Models: A Mental World Model Framework for Mental Modeling, Simulation, Evolution, and Interpretability

Authors: Qingshi Wang

Abstract: Understanding and simulating how subjective cognition and mental states emerge, evolve, and shape behavior is essential for advancing artificial intelligence toward deeper social cognition and general intelligence. Existing large language models (LLMs) and Theory of Mind (ToM) methods primarily infer mental states from linguistic information, lacking unified mechanisms for subjective world construction, cognitive-psychological interactions, dynamic evolution, and historical dependencies. This paper introduces the Mental World Model (MWM) and its implementation, the Multi-Branch Mental Evolution Architecture (MMEA), which explicitly constructs subjective worlds, models interactions between cognition and mental states, and simulates continuous mental evolution shaped by historical experiences. On DynToM and RecToM, MMEA achieves 96.48% and 94.00% accuracy, respectively, outperforming leading LLMs and specialized ToM methods. Additional experiments demonstrate improvements of 28.7, 39.3, and 16.6 percentage points in mental state and behavior prediction, long-sequence prediction, and implicit mental state inference, respectively. The results demonstrate that MMEA provides an interpretable framework for continuous mental modeling, enabling AI to move beyond surface-level semantic representations to infer individuals' underlying mental states from linguistic information and dynamically simulate their internal cognitive processes and evolution over time. MWM also provides a promising foundation for causal reasoning, personalized AI, sustained human-AI interaction, and future advances toward artificial general intelligence (AGI).

---

### 2610.23716 (2026-10-16)

Title: Neural Expansion: A Unified Mechanism for How Deep Neural Networks Generalize

Authors: Chashi Mahiul Islam, Samuel Jacob Chacko, Mao Nishino, Canlin Zhang, Xiuwen Liu

Abstract: Deep neural networks demonstrate remarkable generalization despite being highly over-parameterized, challenging traditional statistical learning theories. While several theoretical paradigms such as margin-based bounds, PAC-Bayesian analyses, and neural tangent kernels provide global explanations, they often lack mechanistic insight into how generalization emerges from training dynamics. We introduce Neural Expansion, a unified geometric framework that characterizes generalization through the expansion of directionally-selective ray coverage in the input space. Using Generalization Intervals (GIs), we quantify direction-specific regions around training samples where the model's predictions remain stable. Our extensive empirical studies across diverse architectures and datasets reveal that training leads to progressive expansion of ray coverage, particularly along directions with low Jacobian singular values. This mechanism helps explain a large fraction of correctly classified test inputs, adversarial examples, and even mislabeled or out-of-distribution samples through the geometry of ray coverage rather than instance-level memorization. By connecting input-space curvature to predictive behavior, our framework provides a mechanistic foundation that complements existing global theories of deep learning.

---

### 2610.23709 (2026-10-16)

Title: GLOBE: Evolving Structured Agentic Memory for E-commerce Product Optimization in Generative Search

Authors: Hyunseo Kim, Suil Choe, Sukkyoung So, Daeyeon Yi

Abstract: Optimizing product listings for generative search requires language agents not only to rewrite effectively but also to continually self-improve by retaining successful strategies across diverse categories. However, existing approaches often treat structured listings as free-form text, leaving effective strategies implicit in prompts, search trajectories, or rewritten outputs rather than accumulating them as a reusable agentic memory. To address this limitation, we introduce GLOBE, an agentic framework that drives continual self-improvement by storing optimization knowledge in an evolving handbook of explicit, field-scoped behaviors. In each episode, an Editor applies relevant behaviors and receives rank-based feedback, which a Reflector converts into behavior updates. Crucially for dependable execution in real-world settings, a Moderator removes redundant proposals, a Curator commits accepted changes, and consistently harmful behaviors are deactivated. This cycle transforms episodic feedback into a persistent, field-scoped optimization memory. Experiments show that structured behaviors outperform monolithic prompt optimization, while feedback-driven evolution and moderation further improve effectiveness and reduce downside risk. The learned behaviors also remain effective on unseen product categories, suggesting that agentic memory evolution supports interpretable and transferable product optimization.

---

### 2610.23673 (2026-10-16)

Title: On the possibilities and limitations of LLM-based multi-agent systems for multi-criteria decision-making in healthcare operations management

Authors: Marco Boresta, Tommaso Giovannelli, Sepehr Namirad, Giulia Riccardi

Abstract: Multi-criteria models for healthcare operations need weights that express how stakeholders trade off patient waiting time, provider workload, and operating cost, but these weights are difficult to quantify. Teams of large language model (LLM) agents, each prompted to represent a stakeholder, have been used to supply them. We propose a framework for assessing the reliability of LLM-generated preferences as inputs to multi-objective optimization and quantifying how their uncertainty affects decisions. We study explicit preferences by asking agents to rate the importance of the criteria in an outpatient appointment scheduling problem, and implicit preferences by inferring trade-offs from the agents' pairwise choices between emergency department configurations. The computational experiments show that the explicit preferences respond to the clinic's operating conditions and differ across roles, but deliberation among the agents can erase these differences, whereas simple averaging preserves them. The pairwise choices used to reveal the agents' implicit preferences depend largely on which option is presented first, and we find limited evidence that a statistical model using contextual information alongside presentation order predicts the agents' choices on new comparison pairs better than a model using presentation order alone. We then formulate robust weighted-sum optimization models to account for preference uncertainty. In most cases, these models select different schedules or configurations from those obtained using average preference weights. These results indicate that LLM-generated preferences need an audit of this kind before they are used as optimization weights in healthcare decision support.

---

### 2610.23670 (2026-10-16)

Title: OwlSight: A Panoramic Monitor for Chain-of-Thought Reasoning

Authors: Lewen Yan, Yanxu Zhu, Jie Zhang, Jing Shao

Abstract: Chain-of-Thought (CoT) monitoring offers actionable evidence for oversight AI systems, with the potential to enable early detection and intervention. However, existing approaches are focused on specific tasks, whereas the regulation of AI, particularly reasoning models, requires monitoring a broader range of tasks. We introduce Factor for CoT monitoring, a strategy that supports customizing monitoring requirements in the prompt, which enables a single monitor to cover different tasks by relying on different factors. Furthermore, we introduce two types of factors, fine-grained and coarse-grained (e.g., monitoring whether a specific email address has been leaked versus monitoring privacy leakage), to accommodate diverse user monitoring needs. Based on this, we develop a CoT monitor named OwlSight that relies solely on factor to monitor behaviors related to multiple dimensions, including capability, safety, and trustworthiness. Experiments across 15,971 reasoning trajectories show that OwlSight surpasses general-purpose LLMs by 1.32-30.57 and 11.71-27.81 points at fine and coarse granularity, respectively, and achieves state-of-the-art results on OpenAI's CoT monitorability benchmark. It also generalizes to unseen models' CoTs and remains robust to Factor rephrasings, CoT compression, and obfuscation, offering a promising paradigm for CoT monitoring that can contribute to the oversight of frontier AI.

---

### 2610.23668 (2026-10-16)

Title: TUPLE-Bench: Evaluating and Mitigating Privacy-Utility Trade-offs in Typed Decision Models

Authors: Yiqu Yang, Qiaoyuan Zheng, Yang Tian, Yu Fan, Elliott Ash

Abstract: Typed decision models often return more than a selected category. They also expose probabilities for each candidate and, sometimes, a separate confidence score. These fields support downstream decisions but may reveal information beyond a recipient's authorization. We introduce TUPLE-Bench (Typed decision models' Utility and Privacy Leakage Evaluation Benchmark), a benchmark of paired synthetic cases in which recipients may learn a coarse operational category but not its fine-grained cause. Across nine models, instructions to withhold the cause fail to protect it: 91.88%-99.93% of responses reveal the cause through direct selection or residual scores. Even when causes are excluded from the candidate set, full outputs enable 62.85%-75.35% recovery on held-out cases, compared with 51.04%-57.64% using only the selected category (50% chance). Full outputs also reduce mean downstream cost in all 27 model-task comparisons. However, confidence fields increase leakage without consistently reducing cost. We further introduce workflow-constrained privacy quantization (WCPQ), which reduces secret recovery while preserving the behavior and cost of specified downstream workflows. Our findings highlight the need to audit decision interfaces field by field and workflow by workflow.

---

### 2610.23625 (2026-10-16)

Title: PresenceBench: An Exploratory Evaluation of Large Language Model Adaptation to User State

Authors: Peña Arroyo Gallego, Mauro Ruiz Moreno, Alejandro Acien, Sergio Romero-Tapiador, Teresa Arroyo-Gallego

Abstract: Presence-aware intelligence is the capacity of an AI system's intelligence layer to adapt appropriately to the functional state of the person it serves (here readiness, flow, and stability) while preserving task quality and safety. We introduce PresenceBench, an instrument for measuring it. PresenceBench evaluates how the intelligence layer uses a supplied state, not how that state is sensed, and breaks the capability into measurable properties. Two are tested here. Receptivity: does the model take up the state and give a better response than with no signal? Specificity: does any improvement depend on the correct state, rather than on extra structured context? A third, adaptation across states, is a required endpoint not measured in this release. A five-arm causal design answers both questions, against each model's own baseline and an equally structured mismatched-state control, scored by a correctness-gated human paired comparison. The exploratory evaluation covered four models across eighteen single-turn, six fixed three-turn and six simulated natural-conversation scenarios. Supplying a synthetic state, raw or translated into a response policy, gave human-preference point estimates above 0.5 for all four models (Claude Sonnet 5, DeepSeek V4 Pro, Gemini 3.6 Flash, GPT-5.6 Terra), with three of eight 95% intervals excluding chance. Specificity was not resolved: no per-model interval excluded chance, and the design cannot yet separate the state values from a generic instruction to adapt. Policy delivery reduced priced cost and output tokens against each model's baseline; these are resource-use changes, not efficiency gains, because correctness non-inferiority was not established. Safety-floor failures were rare (13 of 360 cases), with a non-significant excess under policy delivery. We report the instrument, the frozen results, and the controls a confirmatory study needs.

---

### 2610.23617 (2026-10-16)

Title: GEMS: Molecular Structure Elucidation as Learned Search over Isomer Graphs

Authors: Utku Umur Acikalin, Yingheng Wang, Goncalo J. Gouveia, Tyler J. Schwertfeger, Frank C. Schroeder et al.

Abstract: Identifying small-molecule structures from molecular formulas and tandem mass spectra remains a bottleneck in untargeted metabolomics and natural-product discovery. Even when database retrieval or de novo prediction misses the exact structure, the resulting candidates can provide starting points for exploring nearby structures through a few bond edits. We introduce GEMS (Guided Editing of Molecular Structures), which refines candidates through learned 2-switch bond edits that preserve the molecular formula and each atom's total valence. GEMS uses MIST, a pretrained spectrum-to-fingerprint model, to predict fingerprint probabilities once per spectrum. A neural policy compares each candidate's fingerprint with these predictions, links present features to the atoms and bonds that generate them, and scores all valid edits in one forward pass. The policy is trained on shortest edit paths between structures, so it can be pretrained on PubChem isomers without spectra and then fine-tuned with spectrum-predicted fingerprints. At inference, GEMS searches from multiple initial candidates matching the supplied molecular formula and ranks candidates by fingerprint agreement and multi-start consensus. With the target structure excluded from PubChem initialization, three edit rounds achieve Hit@1/Hit@10 of 29.64%/50.81% on NPLIB1 and 30.22%/41.33% on MassSpecGym, exceeding published baselines under comparable settings. On NPLIB1, GEMS achieves higher identification accuracy in about 3.3 minutes end to end, compared with 26.2 hours for our FRIGID run. GEMS also improves identification from generated candidates, including those refined by FRIGID. Experiments with exact target fingerprints identify fingerprint prediction error as a bottleneck in target recovery and final ranking. Deeper search recovers additional targets without retraining, with larger gains from weaker initial candidates.

---

### 2610.23615 (2026-10-16)

Title: Beyond Action Prediction: Learning Search-Free Planning in Latent Space

Authors: Guanchen Du, Jinhao Du, Yanpeng Sun, Shan Zhang, Na Zhao et al.

Abstract: Latent world models learn action-conditioned state transitions in a compact representation space, providing a predictive model for visual planning and control. However, planning with these models typically requires costly test-time optimization over action sequences. We propose to replace this online search with a goal-conditioned inverse model that directly predicts actions from current and goal observations. A key challenge is that action prediction alone neither ensures that goal representations encode action-relevant information nor that predicted actions are consistent with the learned latent prediction model. We introduce Hindsight Inverse JEPA Planning (HIJP), a search-free framework that addresses both aspects during training. HIJP relabels future observations along offline trajectories as goals, providing action supervision across multiple temporal horizons. By retaining gradients through the goal representations, this supervision directly shapes the visual representation. HIJP further feeds predicted actions into the latent predictor model and aligns the resulting next-state representations with encoded successor observations, enforcing action-transition consistency. At inference time, the inverse dynamics model and latent predictor models are applied alternately to generate multi-step action sequences without online search. Across four visual control tasks, HIJP achieves 86.8% overall success and a 1.9-16.5x planning speedup over search-based planning.

---

### 2610.23612 (2026-10-16)

Title: SIT-Eval: Situation-Based Interactive Turn-by-Turn Evaluation of Conversational Agents

Authors: Ravil Mussabayev, Saveliy Zavertyaev, Dmitriy Parpulov, Andrey Savchenko

Abstract: The rapid proliferation of conversational AI agents necessitates evaluation methods that assess performance across diverse dialogue scenarios, utilizing multiple situational criteria, as appropriate behavior depends on context and encompasses various aspects. Existing dialogue benchmarks typically use static natural conversations, which underrepresent rare situations---a critical safety gap, as low-probability events become frequent failures at production scale. However, limited sample sizes force a choice: either maintain natural dialogues for realism or turn to adaptive situation sampling for comprehensive yet statistically reliable coverage. We introduce SIT-Eval, an adjustable framework for evaluating situation-based conversational agents. We formalize an agent's desired behavior as situational rules: if situation is P, follow rules Q. At each conversation turn, an LLM-interlocutor enacts a uniformly sampled situation. A context-aware LLM-judge leverages all conditionally applicable rules as criteria to evaluate the agent's reply for that situation. The judge is validated using human-verified synthetic golden dialogues. Benchmarking 8 LLMs on 1292 conversation turns reveals failure modes hidden by aggregate metrics: models with similar overall scores vary widely in their adherence to individual rules. All models struggle most with ambiguity clarification and Socratic questioning.

---

### 2610.23599 (2026-10-16)

Title: From Trajectories to Differentiated Skills: Cognitive Differentiation for Self-Improving Agents

Authors: Yewei Zhao, Derong Xu, Wei Chen, Yin Xu, Peilun Zhou et al.

Abstract: Large language model (LLM) agents tackle complex tasks through reasoning and interaction with external environments. Agent skills provide persistent, transferable capabilities that guide task planning, inform contextual decisions, support tool use, and enable executable procedures. Yet existing skill-evolution methods largely organize knowledge around skill artifacts, overlooking the functional heterogeneity within individual skills and its implications for knowledge maintenance and use. Inspired by cognitive science, we propose Cognitive Differentiation in Skill Evolution (CDSE), which evolves a unified skill through four functionally distinct yet coordinated components: Meta, Experience, Tool, and Script. CDSE extracts evidence-grounded semantic gradients from successful and failed trajectories, consolidates them by functional role, and applies component-specific updates and validation with cross-component coordination and adaptive invocation. An analysis of 500 top-ranked skill packages shows that 96.8% contain knowledge spanning at least two functional roles. Across six benchmarks, three agent models, and two execution harnesses, CDSE achieves the highest scores in all 36 settings, improving over the Base agent by 7.6 percentage points and the strongest competing method in each setting by 2.6 points on average. Ablation studies further support the importance of functional differentiation and adaptive invocation.

---

### 2610.23598 (2026-10-16)

Title: RL-Guided Temporal Localization for Dual-Channel Retrieval in Long-Horizon Agent Memory

Authors: Dabin Sheng, Zhe Wu, Jinming Zhao, Junliang Xing, Yuanchun Shi

Abstract: Time-aware retrieval is crucial for long-horizon LLM agents to effectively leverage ever-growing long-term memory. Existing methods focus on lexical or semantic similarity, leading to target memories being crowded out by temporally mismatched yet semantically similar candidates. Even time-aware approaches inject temporal cues only during memory organization or answer generation, overlooking temporal constraints at the retrieval stage, where candidate selection occurs - the root cause of the displacement. Inspired by the temporal contiguity effect in human episodic memory, we propose TIDER (Temporal Interval-driven Dual-channel Evidence Retrieval), a time-aware agentic retrieval framework. Central to TIDER is a reinforcement learning (RL)-trained temporal interval locator that infers the temporal windows in which the evidence lies. RL optimizes window localization as a discrete, non-differentiable retrieval decision, using composite rewards to convert sparse answer supervision into fine-grained retrieval feedback. These temporal windows first define the temporal retrieval channel; the retrieved candidates are then merged with results from the semantic channel and reranked by proximity to the windows. This temporal grounding enables TIDER to retrieve temporally aligned evidence that would otherwise be drowned out by the volume of semantically similar yet temporally mismatched memories. With a lightweight 1.7B locator, TIDER achieves state-of-the-art accuracy on both long-horizon memory benchmarks - 61.52% on LifeBench (+8.82%) and 78.96% on LoCoMo (+3.66%) - which indicates that temporal cues are crucial for pinpointing target evidence amid a vast pool of semantically similar historical events in long-term daily-life memory.

---

### 2610.23574 (2026-10-16)

Title: Darwin-Claw: Environment-Adaptive Experience Consolidation for Recursively Self-Evolving Agents

Authors: Mingze Yin, Xiaohan Wang, Dian Li, Longfei Luo, Jiahong Yan et al.

Abstract: While Large Language Model (LLM) agents have demonstrated remarkable capabilities across complex tasks, they predominantly operate in isolated sessions, lacking the ability to continually learn from historical interactions or adapt to user-specific environments. Existing self-evolution paradigms often indiscriminately inject raw interaction trajectories into memory or skill modules, leading to obscured behavioral patterns and compromised update controllability. Furthermore, as foundational LLM reasoning improves, the bottleneck for agentic evolution shifts from accumulating generic knowledge to effectively managing situational experience. To address this, we propose Darwin-Claw, an environment-adaptive self-evolving framework that systematically distills episodic experiences to drive the comprehensive evolution of operational skills and durable memory. Theoretically grounded in an iterative agent-actor and evolver-critic co-adaptation, Darwin-Claw introduces a Hierarchical Experience Consolidation System that extracts fine-grained error attributions and generalizes them into dynamically updated prototype vectors. This structured situational experience serves as interaction patches for context-sensitive perception and explicit optimization signals for skill refinement. Practically, Darwin-Claw is a readily deployable, automated framework compatible with mainstream agent systems without requiring manual curation. Extensive experiments on WildClawBench demonstrate that Darwin-Claw yields substantial performance improvements, establishing a controllable and stable pathway for the continual, user-centric adaptation of autonomous agents in real-world ecosystems.

---

### 2610.23554 (2026-10-16)

Title: SkillBrowser: Selective Skill Exposure for Scalable Skill-Using Agents

Authors: Jin Ye, Yifan Jiang, Lan-zhe Guo

Abstract: Large language model agents increasingly rely on skills to extend their capabilities in complex tasks. However, scalable skill use requires Selective Skill Exposure (SSE): providing relevant procedural content when needed while avoiding unnecessary exposure that may disrupt reasoning. Existing paradigms fall short in complementary ways. Progressive disclosure exposes metadata for a growing skill library, introducing context pollution; retrieval limits catalog exposure, but static retrieval from the initial task query may be misaligned with capability needs that emerge during reasoning and may still inject unnecessary skills. We propose SkillBrowser, a Meta-Skill-managed framework that enables an agent to identify current capability needs, formulate targeted queries, and selectively load skills on demand. Across six SRA-Bench subsets and five LLMs, SkillBrowser improves aggregate accuracy over static retrieval and LLM-based selection, including multi-step tool use, and mitigates accuracy degradation on already-solvable instances. Benefits remain model- and task-dependent, with under-invocation of useful skills and additional latency as key limitations. These results demonstrate the viability of Meta-Skill-managed SSE for scalable skill repositories.

---

### 2610.23550 (2026-10-16)

Title: Reason-guided Human Reward Modeling for Preference-based Reinforcement Learning

Authors: Anshul Nayak, Shahil Shaik, Jonathan Smereka, Yue Wang

Abstract: Reinforcement learning (RL) policies optimized for task rewards may produce behaviors that are efficient but misaligned with human expectations, safety preferences, or intent. This paper presents a reason-guided preference-based reinforcement learning (PbRL) framework that learns a human reward model from trajectory-level feedback. In addition to preference labels, the framework incorporates reason tags explaining why a behavior is preferred, enabling the learned reward to capture both human choices and their underlying rationale. Compared with preference-only reward learning, the reason-guided formulation provides additional supervision for learning human-aligned rewards and improves the interpretability of the resulting policy. The learned human reward is combined with the environment reward during policy optimization, allowing the agent to improve task performance while producing more interpretable, human- aligned, and preference-sensitive behavior

---

### 2610.23534 (2026-10-16)

Title: From Billion-Scale to Million-Scale Language Models: Operational Capabilities for Embedded Post-Exploitation

Authors: Gabriel Hortea, Simon Pietro Romano, Juan Tapiador, Mario Varlese

Abstract: Small Language Models (SLMs) are increasingly attractive for resource-constrained environments due to their low computational footprint. These characteristics also make them candidates for future autonomous malware, where connectivity, latency, privacy, or operational constraints may preclude cloud-based inference. Yet the ability of ultra-compact models to support malware during post-exploitation remains poorly understood. We systematically evaluate seven open-source SLMs (20M-1.5B parameters) on two post-exploitation code-generation tasks: Directory Enumeration and Backdoor Generation. We compare Python (high-resource) and Lua (low-resource) across prompting strategies, task formulations, iterative reasoning, grammar-constrained decoding, and execution-feedback loops. Results show that offensive code-generation capabilities do not increase linearly with model size. Successful execution depends on the interaction of model capacity, task formulation, and prompting strategy, with task formulation exerting a greater influence than prompt engineering alone. Algorithmic formulation combined with few-shot prompting enables Qwen2.5-Coder 1.5B to reach Pass@5 of 100% in both Python and Lua for Directory Enumeration, 100% in Python for Backdoor Generation, and 99.2% in Lua. Although the evaluated models remain too computationally demanding for widespread deployment in contemporary malware, rapid progress in compact models may reduce this barrier. These findings help anticipate AI-assisted malware and inform future countermeasures.

---

### 2610.23527 (2026-10-16)

Title: Truth in Contrast: Calibrated Factual Evidence from Language Model Likelihoods

Authors: Ponhvoan Srey, Jason Lucas, Pittawat Taveekitworachai, Junyoung Lee, Anh Tuan Luu

Abstract: Large Language Models (LLMs) encode substantial factual knowledge. Yet, estimating confidence in factual claims reliably remains challenging. We study likelihood-based factual confidence from the complementary perspectives of discrimination and calibration across multilingual factual statements. Specifically, we instantiate contrastive generative likelihoods as Contrastive Factual Evidence (CFE), which compares the likelihood of the same claim under competing factual and non-factual conditions, and derive its probabilistic counterpart, the Contrastive Factual Posterior (CFP). We show analytically that CFP calibration depends on the differential error between the two surrogate conditionals, allowing errors shared across them to cancel and yield tighter calibration bounds. Empirically, CFP substantially improves calibration while maintaining factual discrimination comparable to its strongest competitor. Nonetheless, discrimination is uniformly weak across methods in lower-resource languages, which simultaneously undermines the utility of the measured calibration. To this end, we interpret a likelihood geometry, within which an evidence-bearing direction is induced, along with an orthogonal evidence-invariant direction. In our investigation, we selectively align target-language claims with stronger English evidence only along the factual-evidence direction, improving discrimination and open-ended factual generation without target-language labels.

---

### 2610.23525 (2026-10-16)

Title: Trapped in Your Story: Evaluating Narrative-Induced Sycophancy in Large Language Models

Authors: Runtai Yang, Dandan Zhu, Kaiwei Zhang, Guangtao Zhai

Abstract: Large language models (LLMs) are known to exhibit sycophancy by adjusting their responses toward users' expressed views. However, real users often justify their opinions through reasons, personal experiences, causal explanations, and broader narratives, raising the question of whether such narratives can further steer model judgments. We construct a controlled benchmark of 500 debatable questions across ten domains, where the user stance is held fixed while its justification is systematically varied without introducing new task-relevant evidence. Each question is instantiated under 11 matched conditions: one neutral baseline and five mirrored narrative levels for each of two opposing positions, yielding 5,500 evaluation instances. We evaluate seven LLMs and observe substantial differences in narrative-induced agreement. The effect is not monotonic with narrative elaboration: personal experience can reduce agreement, whereas causal framing and worldview-based synthesis increase it. Controlled GPT-5.1 ablations further show that causal framing produces the strongest positive effect, while claim-preserving bullet presentation also increases agreement over paragraph form. These findings suggest that sycophancy is shaped not only by user stance, but also by how supporting explanations are structured and presented.

---

### 2610.23511 (2026-10-16)

Title: LocalIntent: Outcome-Specific Structured Generation for Backend-Compatible Smart Building Automation with Local LLMs

Authors: Tianyang Liu, Jiayue Wang, Zhanhao Cheng, Changyang Wang, Shaoshu Zhu et al.

Abstract: Locally deployed large language models (LLMs) can reduce reliance on remote cloud services for natural language smart building automation, but backend-facing processing requires correct outcome selection, alignment with local capabilities, and valid structured outputs. We investigate whether a complete outcome-specific prompting design improves compact-model outputs beyond generic route-then-generate prompting. The proposed LocalIntent approach routes requests to ordinary or persistent-rule branches: the former produces commands, clarifications, or rejections, while the latter generates trigger-action rules, followed by deterministic validation. We evaluate four locally executed Gemma and Qwen models spanning 2B-9B parameters on 101 non-persistent and 54 persistent-rule records, comparing Monolithic prompting, generic two-stage prompting, LocalIntent, and validation-guided repair. Across the evaluated datasets, LocalIntent achieves higher intent understanding, device identification, and action/parameter correctness than generic two-stage prompting, while clarification/mode correctness remains model-dependent. The largest gains occur for rules, where LocalIntent improves intent understanding from 26.4% to 80.6%, device identification from 59.3% to 84.7%, rule-mode correctness from 49.1% to 98.6%, and action/parameter correctness from 5.6% to 44.9%. For non-persistent requests, pooled gains are smaller: intent understanding increases from 39.6% to 53.2%, and action/parameter correctness from 30.7% to 42.8%.

---

### 2610.23491 (2026-10-16)

Title: A Topological Signature of Learning under Noisy Labels

Authors: Zhongtian Sun, Fan Mo, Prayag Tiwari, Kelin Xia

Abstract: How does noisy supervision change the representations learned by a neural network? Training accuracy measures agreement with training labels but provides little information about representation geometry. We use persistent homology to track loop structure across distance thresholds in neural activations. Experiments span image classification, text classification, and modular arithmetic. On a fixed CIFAR-10/ResNet-18 training probe, equally sized clean-label and corrupted-label subsets show no detectable persistence difference at epoch 10, whereas corrupted-label subsets have higher persistence at epoch 50. The contrast survives uniform-scale controls, even though predictions match the assigned noisy labels for only 7-11% of corrupted probe examples at that checkpoint. Normalisation preserves the crossover between clean and noisy training trajectories on CIFAR-10/ResNet-18, whereas CIFAR-100/ResNet-18 shows no crossover under any of the five evaluated constructions. In a separate noise-rate calibration comparison across five pipelines, mean activation norm achieves a higher mean in-sample R2 than raw persistence (0.936 versus 0.908). These findings show that noisy supervision leaves a measurable geometric signature even when agreement with corrupted labels is low. Comparing persistence under scale controls with label-fitting measurements offers a way to study how representations respond to label corruption beyond what training accuracy reveals.

---

### 2610.23470 (2026-10-16)

Title: QD-Rec: Open-Ended Evolution of Recommendations via Quality-Diversity

Authors: Takashi Ishida, Taro Makino, Issa Sugiura

Abstract: Open-ended search combined with foundation models has produced advances such as faster algorithms, new results on open mathematical problems, and self-improving agents. We extend this paradigm to recommendation for decision-making, focusing on decisions where the set of possible choices is fixed but the reasons for choosing them are not. In high-stakes decisions, e.g., which company to acquire or which customer to target, comparing diverse, well-reasoned options can be more useful than a single ranked list. We formalize open-ended recommendation as building a diverse, high-quality set of recommendations, each an item together with a hypothesis, a natural-language reason why the item fits the needs of a decision maker. We propose QD-Rec, a quality--diversity method that selects items with a contextual bandit and generates hypotheses with a foundation model from earlier ones kept in an archive as stepping stones. A new recommendation enters the archive if it is novel or better than its nearest neighbor. Across M&A, customer targeting, and paper and book recommendation, QD-Rec gives the highest mean quality and builds the largest archive in most settings.

---

### 2610.23465 (2026-10-16)

Title: S-GAP: Stealthy Graph Attack Primitives for Graph Large Language Models

Authors: Wenda Li, Tongya Zheng, Shunyu Liu, Hanyang Yuan, Kaixuan Chen et al.

Abstract: Graph Large Language Models (GraphLLMs) enable powerful semantic understanding and reasoning over Text-Attributed Graphs (TAGs), while their semantic reasoning may exhibit vulnerabilities to perturbations in node text and graph structure under adversarial attack evaluation. Existing attacks typically construct textual and structural perturbations in separate stages guided by distinct realization intents. However, this separation results in attack-intent fragmentation, causing semantic incoherence between the two perturbation types, thereby undermining attack stealth and making them easier for GraphLLMs to identify and disregard, ultimately weakening attack effectiveness. To avoid attack-intent fragmentation, we propose the Graph Attack Primitive (GAP), an atomic semantic representation that unifies textual and structural perturbations under a coherent attack intent. By carefully calibrating the semantic composition of a GAP, we can achieve strong attack effectiveness while maintaining sufficient attack stealth. Furthermore, we introduce S-GAP (Stealthy GAP), a multi-agent framework that iteratively refines the semantic content of the GAP. The framework unifies GAP planning and realization and continuously refines this process through surrogate evaluation and textual feedback. Extensive experiments across four datasets, three GraphLLMs, and two attack settings show that S-GAP improves ASR over the strongest baselines by 7.02% on average while producing more relationally plausible perturbations, exposing critical vulnerabilities in current GraphLLMs and motivating more robust defenses.

---

### 2610.23449 (2026-10-16)

Title: GatewayBench: Unified Capability and Security Evaluation Platform for MCP Gateways

Authors: Yitian Zheng, Zhaorun Chen, Haoyu Li, Bo Li

Abstract: AI agents have increasingly interacted with external environments by invoking tools, with Model Context Protocol (MCP) emerging as a standard interface for connecting agents to heterogeneous tools and services. As organizations deploy agents at scale, MCP gateways have become a critical middleware layer for aggregating, governing, and shaping the tool surface exposed to agents. Despite the growing importance of MCP gateways in agentic systems, no prior work has systematically studied how gateway design affects agent capability, efficiency, and security. To address this gap, we introduce GatewayBench, the first unified evaluation framework and benchmark for MCP gateways. We characterize gateway architectures into two major paradigms: flattened gateways and hierarchical gateways. GatewayBench comprises 524 tasks across six domains, together with a pool of 11,118 real-world tools from 251 authentic MCP servers. To emulate large-scale deployments, we systematically inject task-irrelevant tools sampled from this pool into each agent environment, enabling controlled evaluation as the accessible tool surface scales. Based on GatewayBench, we conduct extensive experiments across seven widely deployed MCP gateways and diverse agent configurations, covering both benign and adversarial tasks. Our results reveal substantial differences across gateway designs in task completion, tool-use efficiency, and resilience to attacks, and further demonstrate that these effects interact strongly with the underlying model and agent harness. These findings highlight the MCP gateway as a consequential yet underexplored component of the agentic AI stack. By enabling controlled evaluation of gateway architectures under realistic tool ecosystems, GatewayBench provides both practical guidance for MCP gateway design and a rigorous testbed for developing more capable, efficient, and secure agentic systems.

---

### 2610.23445 (2026-10-16)

Title: RECREG: Recovery-based Shielding for Regular Safety Properties in Reinforcement Learning

Authors: Alexander W. Goodall, Francesco Belardinelli

Abstract: In many real-world scenarios we need to consider formal requirements, such as safety and constraint compliance, to deploy Reinforcement Learning (RL) agents. In this paper we introduce RecReg, a safe RL framework capable of enforcing non-Markovian regular safety properties via recovery-based shielding. RecReg is a unified approach that supports different levels of a priori knowledge and safety guarantees. The paper primarily focuses on building the theoretical foundations for RecReg in the tabular setting, providing rigorous safety and convergence guarantees that are not present in related work. We provide an extensive set of empirical results using the MASA-Safe-RL library, and we outline an extension of RecReg to deep RL domains using SOTA model-based RL. Our empirical results demonstrate that RecReg achieves efficient learning and matches the theory in this paper.

---

### 2610.23443 (2026-10-16)

Title: ScoutRoute: Efficient Mixture-of-Experts Routing Using Internal Language Model Signals

Authors: Rajdeep Pandhare, Delzaan Bharucha

Abstract: Efficient expert routing is a fundamental challenge in Mixture-of-Experts (MoE) systems, particularly for heterogeneous collections of independently trained Large Language Mod els (LLMs). Existing routing approaches typically rely on jointly trained gating networks, prompt-based predictors, or computationally expensive multi-model inference, limiting their flexibility and efficiency. This paper presents ScoutRoute, a lightweight post-hoc routing framework that predicts expert competence using internal language model signals extracted from a single forward pass through an inexpensive scout model. Hidden-state representations are used to estimate cross-model competence through lightweight logistic probes, while logit-derived confidence measures are incorporated within a domain-aware routing strategy for efficient expert selec tion without modifying the underlying language models. ScoutRoute isevaluatedon fiveopen-weightlanguagemodels across fourbenchmark datasets covering mathematical reasoning, code generation, commonsense reasoning, and multidis ciplinary knowledge. Experimental results show that ScoutRoute consistently outperforms individual routing signals while requiring only a single scout-model inference. The proposed competence probes also achieve superior calibration compared with conventional confidence measures, demonstrating that internal language model representations provide transferable information for accurate and efficient expert routing across heterogeneous language models

---

### 2610.23436 (2026-10-16)

Title: Generative Policy Improvement from Observational Data

Authors: Jonas Schweisthal, Dennis Frauen, Stefan Feuerriegel, Emma Brunskill

Abstract: We study how to improve decision policies from observational data to generate better actions when actions are complex, structured objects, such as text messages or images. This task is subject to two major challenges: (i) action-level overlap is often too weak for reliable off-policy evaluation and improvement, and (ii) generating new structured actions often requires expensive training or fine-tuning (e.g., of an LLM) and can be ill-defined due to information loss in action representations. To address both, we propose PolicyLift, a three-stage framework for generative policy improvement with structured actions from observational data. In Stage 1, PolicyLift learns a small set of discrete action codes that capture high-level strategies in the observed action space and are tailored to support policy improvement under limited overlap. In Stage 2, it learns a context-dependent policy over these action codes. At deployment time, Stage 3 "lifts" the learned code-level policy back to the original action space by generating actions from the historical behavior system in a code-conditioned way. We show theoretically that improving the policy over action codes guarantees improvement of the induced policy in the original action space. We demonstrate PolicyLift across experiments in synthetic and real-world text generation tasks with consistent policy improvements over the behavior policy.

---

### 2610.23396 (2026-10-16)

Title: AWAM: Active Trajectory-Conditioned View Imagination for Robust Robot Manipulation

Authors: Jiawei Geng, Zhenyang Liu, Yuzheng Wu, Yanwei Fu

Abstract: Rapid progress in embodied intelligence has enabled increasingly capable robots to follow language instructions and manipulate diverse objects. However, strong results in structured environments do not automatically transfer to open-world conditions, where clutter, occlusion, and changing viewpoints can obscure the spatial relationships required for action. To address this perceptual gap, a virtual active-perception paradigm is introduced. AWAM, an Active World-Action Model actively plans where to observe and imagines what will be seen along the planned trajectory before acting. Task-related virtual camera motion is predicted and used as a structured query into a geometry-conditioned world model, producing a reusable spatial prior for manipulation, which is later compressed into a fixed memory and fused with live observations through cross-attention for diffusion-based action prediction. AWAM achieves competitive success rates with 75.9% on LIBERO-Occ, 62.4% on LIBERO-Plus, 76.5% on RLBench-OG Occlusion1, and 94.4% in real-robot trials. These results support improved robustness to the evaluated occlusions and distribution shifts, addressing part of the gap between structured manipulation and less controlled environments.

---

### 2610.23362 (2026-10-16)

Title: Monitor-Validity Failures: LLM Safety Evidence Paths at Evolving Framework Boundaries

Authors: Junchi Liao

Abstract: Modern LLM applications rely on runtime monitors that inspect tool calls, traces, streams, detector outputs, and verifier inputs. This creates an interface-reliability problem: a framework path may remain operational while policy-relevant evidence never reaches its decision point. In one representative case, a regex detector returned a positive match, but the framework stranded the result before the block decision. This differs from jailbreaks and detector errors because the evidence is already recognized yet disconnected from enforcement. We study this repair-boundary signature with canary contracts: parent/fixed confirmation units that place a known payload only on the changed evidence surface and record monitor visibility together with the downstream decision for action-boundary cases. Applying the protocol to public framework repairs, we confirm 18 evidence-path failures across 11 LLM or agent safety project groups and four implementation ecosystems. Nine are established-boundary repairs, eight are new-surface policy-coverage gaps, and one is a boundary-only evidence case. Fourteen reach E1 enforcement boundaries: seven native action outcomes, six configured enforcement boundaries, and one synthetic-consumer consequence. The remaining cases affect verifier, safety-prompt, or observability channels. The cases form carrier, adapter, authority, and surface families and show how ordinary application behavior can remain intact while a safety-specific evidence path misses its decision. Exact revisions, deterministic outcomes, negative controls, and a frozen prospective audit document the confirmation rule. Monitor assumptions therefore need regression tests at the schemas, streams, tools, and adapters that frameworks evolve.

---

### 2610.23345 (2026-10-16)

Title: OliO: ODE-based Linear Transition Operator for Self-Supervised Time Series Forecasting

Authors: Kwangryeol Park, Seulki Lee

Abstract: Self-supervised representation learning has advanced time series forecasting by capturing robust features from unlabeled data. However, existing contrastive and masking-based methods often struggle to explicitly model the underlying temporal flow, either by treating time lag as noise or by disrupting the inherent temporal dynamics essential for forecasting. To address these limitations, we propose OliO (**O**DE-based **Li**near Transition **O**perator), a plug-and-play self-supervised learning method that learns bidirectional temporal flows as a continuous and structurally consistent dynamical system. OliO introduces a transition operator derived from linear Ordinary Differential Equations (ODEs) to align latent representations across arbitrary time shifts. By imposing a strictly upper triangular constraint on the transition matrix, we mathematically ensure numerical stability and enforce a robust polynomial boundary that effectively captures long-term dependencies while preventing the exponential divergence typically found in unconstrained ODE-based models. This structural constraint induces a temporally coherent representation space that preserves the underlying flow essential for accurate forecasting. Extensive experiments across various backbone architectures and benchmarks demonstrate that OliO achieves significant performance gains, providing Mean Squared Error (MSE) reductions of up to 5.75% over the most competitive grid-searched SOTA baselines. The code is available at *https://github.com/eai-lab/OliO*

---

### 2610.23344 (2026-10-16)

Title: Language Models Learn to Improve Language Models

Authors: Minhua Lin, Zijun Wang, Zewen Liu, Zhaotian Weng, Bing He et al.

Abstract: Large language models (LLMs) are increasingly used to automate AI research, including language-model (LM) development, offering a potential path toward recursive self-improvement. However, turning experimental feedback into a learned ability to propose effective improvements across models faces two challenges. First, training such an ability with real feedback is expensive: reinforcement learning (RL) requires evaluating tens of thousands of proposals, each potentially requiring a full model-training run. Even at ten GPU-hours per run, reward collection alone would consume hundreds of thousands of GPU-hours, motivating a cheaper surrogate. Second, surrogate feedback can become unreliable as policy optimization favors overestimated proposals when the proposal distribution shifts. To address these challenges, we propose LM2LM, which trains LLMs with RL to generate effective LM improvement proposals. To provide scalable feedback, we use a research world model (RWM), a frozen LLM that predicts proposal gains from real experimental records provided in context, as the reward model for RL. To maintain feedback reliability, we periodically execute current-policy proposals ranked highly by the RWM and add their measured outcomes to its context. Across eight autoregressive and diffusion LM development environments, real-execution evaluations on held-out tasks show that LM2LM enables Qwen3.8-27B to outperform GPT-6-sol, even when GPT-6-sol is given 300 real experimental records in context, while requiring 33% lower data-generation cost. LM2LM also generalizes to a model family unseen during training.

---

### 2610.23342 (2026-10-16)

Title: Robust Function Calling for LLM Agents Under Interface Drift

Authors: Aniruddha Chattopadhyay, Kanishka Halder, Partha Sarathi Roy

Abstract: Tool-augmented language-model agents rely on interface text: tool descriptions, argument schemas, and the candidate tool list shown at inference time. These interfaces often change after deployment even when the underlying tool semantics remain fixed, creating a practical reliability problem for function-calling systems. We study this failure mode as interface drift and evaluate whether a lightweight, training-free repair layer can recover robustness without retraining the base model. Our method, SchemaShield-Lite, combines schema validation, candidate-set retry for missing tool names, and one-shot constrained repair. On Qwen3.5-9B, it raises DICE-300 accuracy from 0.717 to 0.813 and BFCL-200 accuracy from 0.580 to 0.805, recovering 19/22 and 33/45 drift-induced failures with no observed repair harms. Naive retry does not explain the gains. Ablations show that candidate-set drift, especially distractor tools, accounts for most observed damage, while description and schema edits alone are less harmful. The results position validation-and-repair as a practical robustness layer for deployed LLM-agent tool use.

---

### 2610.23317 (2026-10-16)

Title: AgentOnto: Ontology-Guided LLM Agents for Enterprise Data Analytics

Authors: Dayan Pan, Bincheng Zuo, Xiaojian Wang, Daogang Zhang, Jingyuan Wang

Abstract: Enterprise data analysis requires agents to connect analytical requests with knowledge distributed across databases, business documents, and existing example tasks. Without an explicit representation of this knowledge, an agent may produce incorrect analytical results and cannot reliably incorporate feedback. We present AgentOnto, an ontology-guided LLM agent for enterprise data analytics. AgentOnto organizes heterogeneous enterprise knowledge into an ontology that directly guides analysis and incorporates confirmed feedback. Iterative Ontology Preparation further improves the ontology through self-generated analysis tasks. We evaluate AgentOnto on two public data sources. AgentOnto substantially outperforms representative methods, while module-level evaluations confirm the effectiveness of ontology construction, analysis, and updating. A real-world deployment further demonstrates its practical value in enterprise analytics. These results demonstrate that explicitly constructing, using, and updating enterprise knowledge supports reliable and adaptable data analysis.

---

### 2610.23313 (2026-10-16)

Title: From Memory Hits to Answerable Evidence: Query-Conditioned Memory Compilation for Long-Term Agent Memory

Authors: Shangze Li, Yanyu Yao, Derong Xu, Zhi Zheng, Tong Xu

Abstract: Long-term agent memory requires recovering answer-relevant evidence dispersed across turns and sessions. Existing systems increasingly use structured memories and adaptive retrieval, yet often pass retrieved or expanded units directly to the reader, coupling memory addressing with evidence presentation and leaving the final context redundant or incomplete. To address this gap, we propose MemCompile, a query-conditioned evidence compilation framework for long-term conversational memory. Given a query, the Address Plane locates relevant support through compact source-linked descriptors and capacity-aware Cells, while a normalization boundary resolves heterogeneous retrieval hits to stable SourcePacket identities. Its Evidence Plane then allocates a bounded evidence budget across complementary packets, admits limited additional support, and renders the retained claims associated with each selected packet into an answer-ready context. MemCompile achieves 80.52% Judge Accuracy on LoCoMo and extends the empirical quality-cost Pareto frontier to a higher-quality regime. Its strong performance on LongMemEval-S further suggests that the benefits of query-conditioned compilation generalize across long-term conversational-memory benchmarks.

---


## 3. MCP Ecosystem — 2026-10-17 → 2026-10-19 (3-day window)

### modelcontextprotocol/servers

Last: v2.0.0 released 2026-10-19 (cliffhall)

Refactors 4 TS servers (everything, filesystem, memory, sequential-thinking) and 3 Python servers (fetch, git, time) to modern-era spec while maintaining legacy compatibility. TS servers now require Node 24+. Pinned to TS SDK v2. v1.0.0 was 10-11 (8 days ago); v2.0.0 = 8 day gap. PR #5166 merges v2/main to main.

---

### modelcontextprotocol/inspector

Last: v2.11.0 released 2026-10-14

Preceded by v2.10.1 (10-08) and v2.10.0 (10-07). Three releases in one week. PR #2720 milestone merge to v2/main for the v2.11.0 release; PR #2716 bumped version; PR #2712 denies install scripts.

---

### modelcontextprotocol/modelcontextprotocol

Last: spec repo RENAMED from modelcontextprotocol/spec

Old path modelcontextprotocol/spec returns 404. New canonical path is modelcontextprotocol/modelcontextprotocol. Last commit 2026-10-18 (docs: fix broken SEP-2133 link in SEP-2640 #3439). Active development on WG charters.

---

### modelcontextprotocol/go-sdk

Last: 10-19 #1412 SSE parsing

mcp: parse SSE field values per the SSE spec (#1412). Multiple 10-16 hardening commits (#1407 error handling, #1304 nil handler, #1342 testdata, #1400 marshal). Active cross-language hardening sync continues.

---

### modelcontextprotocol/java-sdk

Last: 10-16 2.1.x branch activity

Merge branch 2.1.x, snapshot publishes, dev version bumps. No 10-17-19 commits in window — at maintenance plateau.

---

### modelcontextprotocol/rust-sdk

Last: 10-17 PR #1377 streamable-http-server fix

fix(streamable-http-server): answer a session-less non-initialize POST with 400 (#1377). PR #1346: read request id in float form as integer. PR #1366: answer server ping during initialize handshake. Spec compliance focus.

---

### modelcontextprotocol/typescript-sdk

Last: 10-13 #2968 migration docs, no 10-14..10-18

Docs/migration skill (#2968) last commit. Quiet 5-day window. PR #2960/3005/2762/2956 from prior window.

---

### modelcontextprotocol/python-sdk

Last: 10-17 #3726 per-response header list

Give each SSE response its own header list (#3726). PR #3719: cache fields to directory read and `_meta` to `Skill`. PR #3696: return invalid params for unknown prompts. PR #3679: MCP Apps tool results from notification params.

---

### modelcontextprotocol/csharp-sdk

Last: 10-17 PR #1844, #1903 (discovery + JSON parse detail)

Surface JSON parse detail in streamable-HTTP 400 responses (#1844). fix(client): allow missing server info in discovery (#1903). Activity up vs prior reports — closing the csharp lag gap.

---

### modelcontextprotocol/kotlin-sdk

Last: 10-19 active

chore(deps): bump zod from 4.6.5 to 4.6.7 in integration-test/typescript. PR #1032 expire idle Streamable HTTP sessions; PR #1100 keep SSE path for query-only endpoint events. Active.

---

### modelcontextprotocol/php-sdk

Last: 10-18 burst — 0.9.0 release prep

5 commits on 10-18: changelog consolidation #610, listChanged announcement for custom registry #608, refused gateway to InputRequiredResult #606, structured content docs #605, HTTP requests from outside request fiber #599.

---

### modelcontextprotocol/ruby-sdk

Last: 10-18 burst — request-id handling

5 commits on 10-18: ignore empty accept header members #616, expect no id in refusal of unreadable request id #622/#615/#613 (accept any string as request id). Spec compliance on error framing.

---

### modelcontextprotocol/registry

Last: 10-11 last meaningful commit

Catch nested server.json publish PRs and clarify publishing guidance (#1702). Deps bumps. Quiet 8-day window.

---

### modelcontextprotocol/conformance

Last: 0.2.0-alpha.12 (10-01)

Authorization Server: DPoP Support (SEP-1932) (#396). SEP-2640 skills server conformance (#330). RFC 8707 resource parameter (#466). 18-day quiet — expect alpha.13 soon.

---

### modelcontextprotocol/experimental-ext-triggers-events

Last: 10-15 last activity

Incubation for Triggers & Events WG. New SEP-3415 (Events Extension) by pja-ant is the upstream spec artifact.

---


## 4. Key Headlines


1. **MCP servers v2.0.0 RELEASED 2026-10-19** — resolves 6-session watch item (was held at 2026.8.31 for 39 days)

2. **modelcontextprotocol/spec → modelcontextprotocol/modelcontextprotocol** (renamed)

3. **5 new SDK burst on 10-18**: php-sdk 0.9.0 prep, ruby-sdk request-id hardening

4. **Inspector 2.11.0 released 10-14** (3 releases in 7 days)

5. **arXiv fresh = 2026-10-16 batch only** (40 papers, 2610.23027-2610.23854) — weekend batch not yet released

6. **web_search still broken** (DuckDuckGo provider_error, 5th day)
