# AI/Agent/MCP Research Corpus — September 1, 2026
# Source: arXiv cs.AI daily submissions + web intelligence
# Collected: 2026-09-01 16:24 UTC

## PAPER 1: Agentic Data Cracking
ID: arxiv:2608.31082
Title: Token-Efficient Data Reasoning Agents via Adaptive Structuring of Unstructured Data
Authors: Milad Rezaei Hajidehi et al.
Tags: agent, cost-efficiency, RAG, enterprise-AI
Abstract: Valuable data remains embedded in unstructured sources: web pages, reports, contracts, filings, earnings calls, and PDFs. The big bet in enterprise AI is deploying LLM agents that reason over this data to answer complex questions for every knowledge worker. Agents can do this today, but at prohibitive cost. Each question repeatedly opens large documents to recover scattered evidence, consuming up to a million tokens. However, if the data were already structured, the same question would reduce to a cheap database lookup. For example, on FanOutQA benchmark, reasoning over an ideal pre-structured store is 28X cheaper, and the gap grows to orders of magnitude as questions fan out over more documents. Yet structuring everything in advance is not viable: documents hold vastly more possible structure than any workload will use, and the useful structure and documents are unknown until queries arrive. We propose agentic data cracking, a method that structures unstructured data adaptively and speculatively as a byproduct of reasoning itself. Structuring is adaptive because observed queries decide when it happens and what matters, and speculative because it goes beyond the current question. Whenever the agent opens a document to answer, a cracking sub-agent forks from the already-loaded context at marginal cost and extracts grounded structure likely to serve related future queries. Over time, an increasing share of queries is fully covered by structured data and answered without opening a document, keeping agentic accuracy at close to RAG cost. On FanOutQA, extended with merely one related question per test question, cracking cuts cost by 53% while preserving accuracy. Agentic data cracking is a first step toward next-generation data infrastructure for agentic reasoning over unstructured data: a shared substrate beneath the model where knowledge that reasoning already paid to uncover accumulates.
Submission: Mon, 31 Aug 2026 16:53:45 UTC

## PAPER 2: Agent Working Memory
ID: arxiv:2608.31057
Title: Measure Before You Manage: Evaluating Agent Working Memory in Coding Agents
Authors: Le Chen et al.
Tags: agent, memory, coding-agent, evaluation
Abstract: Agent working memory is heterogeneous. Objects such as instructions, artifacts, tool outputs, and agent-generated state play different semantic roles and exhibit different size, retention, and representation profiles. Recent work has begun to explore memory-management mechanisms that account for such heterogeneity. This work focuses on semantic heterogeneity and studies how it should shape the management and evaluation of working memory in coding agents. Across 55 archived coding-agent trajectories, we find that semantically different working-memory objects exhibit distinct retention and compression behavior. This heterogeneity motivates semantically informed memory management. We study two semantically informed strategies: an object-aware compression policy and a retrieval-based policy. Their evaluation shows that calibration gains may not transfer to held-out tasks, and that equal token budgets do not imply equal delivered context or management cost. A real-system replay further exposes serving limits that nominal budgets alone do not capture. Together, these results show why semantic structure matters for agent working memory and why evaluating memory-management strategies requires more than a nominal token budget. We organize these lessons into four levels: stored state, delivered context, management work, and task or process outcome.
Submission: Mon, 31 Aug 2026 16:34:51 UTC

## PAPER 3: Turing-20B-A2B MoE for Physical AI
ID: arxiv:2608.30567
Title: Efficiently Scaling Foundation Models Toward Physical AI
Authors: Yuheng Zhang et al. (20+ authors)
Tags: MoE, physical-AI, long-context, foundation-model
Abstract: We present Turing-20B-A2B, a 20B-parameter Mixture-of-Experts language model that activates approximately 2B parameters per token, designed for long-context and latency-sensitive physical AI applications. The model adopts Quantile Routing in a dynamic top-k configuration, enabling token-adaptive expert allocation while maintaining balanced expert utilization and a controlled average compute budget. During deployment, we further apply capacity-constrained routing to prompt prefill for more regular and efficient expert execution, while retaining dropless routing during pretraining. Turing-20B-A2B also employs a hybrid attention architecture that combines Lightning Attention with a small number of full-attention layers for efficient long-context modeling. The model is pretrained with a progressive three-stage curriculum and extended to a native context length of 128K through continued pretraining, with further inference-time extension to 512K using YaRN. Despite its compact active-parameter budget, Turing-20B-A2B achieves, at the base-model stage, overall general capability exceeding Qwen3-8B Base and approaching Qwen3.5-9B Base, while maintaining strong long-context performance and favorable prefill-latency scaling. These results demonstrate an effective balance among model capability, long-context scalability, and practical inference efficiency.
Submission: Mon, 31 Aug 2026 10:30:xx UTC

## PAPER 4: OHCAM Action Model Learning
ID: arxiv:2608.30955
Title: Learning Action Models with Conditional and Quantified Effects via Uncertainty-Guided Exploration
Authors: William Solow et al.
Tags: planning, robotics, action-model, active-learning
Abstract: Accurate action models are critical for effective planning. Existing action-model learning methods largely assume simple action representations or become computationally intractable when learning conditional and quantified effects. We present Online Hypothesis-Driven Conditional Action Model Learning (OHCAM), an online approach for learning action models with conditional and quantified effects from limited interactions with the environment. OHCAM maintains a belief over hypothesized action models and actively selects informative actions to reduce uncertainty by maximizing disagreement among competing hypotheses, while being robust to noisy observations. To enable scalability, OHCAM begins with a small set of simple action model hypotheses and expands to more complex conditions only when the current hypotheses become inconsistent with the data. Experiments on six benchmark planning domains demonstrate that OHCAM is sample efficient in learning action models that solve substantially more tasks than baselines, even with observation noise. We validate OHCAM on two tasks using a Kinova Gen3 robot, demonstrating the real-world applicability of our approach.
Submission: Mon, 31 Aug 2026 15:23:43 UTC

## PAPER 5: SARGE Red-Teaming Self-Evolving Agents
ID: arxiv:2608.30429
Title: Red-Teaming Autonomous Skill Generation and Evolution in Self-Evolving Agents
Authors: Doyun Kim et al. — Accepted to EMNLP 2026
Tags: agent-security, red-teaming, self-evolving, EMNLP2026
Abstract: LLM-based agent systems increasingly adopt skill-based architectures to reduce repetitive reasoning costs and improve stable, efficient task execution. Recent studies propose self-evolving agents that autonomously generate, refine, and reuse skills from past experiences to enable continuous capability evolution. However, autonomous skill evolution introduces a new attack surface in which malicious capabilities are generated, stored, and reused as legitimate skills. In this paper, we define EvoSkill Injection as a threat model targeting the autonomous skill generation and evolution pipeline of self-evolving agents. We further propose SARGE (Red-teaming Autonomous Skill Generation and Evolution in self-evolving agents), a red-teaming framework for evaluating this threat model through iterative generation, escalation, and reinforcement interactions. To support our framework, we construct EvoSkillBench, a benchmark dataset of malicious interaction trajectories for inducing malicious skill formation in self-evolving agents, and introduce EvoSkillSafetyBench, a post-attack benchmark for evaluating whether injected malicious skills are subsequently retrieved and activated as harmful behaviors. Our evaluation shows that SARGE induces malicious skill formation and that injected skills are persistently stored and repeatedly activated, highlighting the risk of persistent capability corruption.
Submission: Mon, 31 Aug 2026 08:25:03 UTC

## PAPER 6: ATLAS Dual-Horizon Agent Evaluation
ID: arxiv:2608.30685
Title: Dual-Horizon Diagnostic Evaluation for Industrial Tool-Use Agents
Authors: Wei Chen, Peilun Zhou et al. (Meituan)
Tags: agent, evaluation, industrial, production
Abstract: Large language model (LLM) agents are increasingly deployed in user-facing services that require iterative tool use under dynamic business conditions. Reliable evaluation is essential for sustained improvement: it must reveal capability deficiencies, inform priorities, and assess interventions. Yet industrial agent service unfolds both through the iterative trajectory of a current request and through continued user interaction. Final-outcome assessment can therefore obscure where deficiencies arise and whether later service remains aligned with context from earlier exchanges. We propose ATLAS, a dual-horizon diagnostic evaluation framework for industrial tool-use agents. At the request horizon, trajectory-wise diagnostic signals relate deficiencies to execution locations and capability concerns. At the interaction horizon, user-wise signals assess whether service remains responsive across continued interaction. Together, these views provide structured diagnostic evidence for analyzing execution deficiencies and sustained service behavior. ATLAS instantiates them as executable signals with explicit evidence scopes and decision boundaries. LLM judge interfaces are calibrated against high-confidence references from real business logs; when needed, their decision behavior is distilled into efficient diagnostic models for lower-latency, lower-cost evaluation. The resulting feedback supports policy optimization. We evaluate ATLAS on Meituan Xiaotuan production traffic. Offline experiments assess diagnostic-signal fidelity and replay-based policy improvement, while online A/B experiments show concurrent gains in user engagement, downstream business outcomes, and sampled human-audit quality.
Submission: Mon, 31 Aug 2026 12:25:24 UTC

## PAPER 7: OLIVE XR Agent with BCI
ID: arxiv:2608.30369
Title: Augmenting Human Performance with an XR Agent Learning from Online Behavior and BCI Evidence
Authors: Ziheng Li et al. — ACM UIST 2026
Tags: XR, BCI, human-agent, adaptive, UIST2026
Abstract: We present OLIVE, a framework for adapting a foundation model to provide real-time assistance in temporally demanding, high-stakes, and dynamic tasks. We show that passive EEG, fused online with behavioral evidence, can meaningfully extend the number of targets users detect and engage beyond their unaided action bandwidth. OLIVE learns from both explicit behavioral signals (the targets the user shoots down in an XR first-person shooter game) and implicit physiological signals (fixation-locked EEG) to provide timely guidance, continuously adapting a frozen vision-language model's inference on which items are task-relevant by jointly estimating per-source reliability without manual labels or offline training. Through three user studies, including two live deployments of an assistive agent driven by OLIVE in XR, we show that OLIVE Pareto-dominates prior test-time adaptation frameworks, achieving the highest convergence rate at comparable convergence speed. Combining implicit physiological and explicit behavioral signals, the OLIVE agent produces the largest and most reliable within-session improvement to a user's ability to detect and engage targets, largely independent of the individual's skill. When the target switches silently, the agent that uses both behavioral and physiological signals reconverges significantly faster than the behavior-only agent (1.27 times faster on average, p = .008), restoring trustworthy guidance at the moment the task changes, precisely when reliable assistance matters most.
Submission: Mon, 31 Aug 2026 xx:xx UTC

## PAPER 8: APTS Answer Probing
ID: arxiv:2608.30345
Title: Answer Probing-Guided Search for Diverse Solution Exploration of LLMs
Authors: Yi Fang et al. — Accepted to EMNLP 2026 Main
Tags: LLM, reasoning, diversity, tree-search, EMNLP2026
Abstract: Generating multiple diverse and high-quality solutions is valuable for many applications, such as code-test generation and drug discovery. However, Large Language Models (LLMs) tend to converge on a single high-confidence solution during inference, limiting exploration of alternative valid solution paths. Existing test-time methods promote diversity through tree-like search and prune semantically similar branches using response-level semantic embeddings. However, we find that such embeddings are easily confounded by linguistic and stylistic similarities, making it difficult to distinguish genuinely distinct solution paths. To address this, we introduce Answer Probing, which probes the potential answer an LLM would reach from an intermediate reasoning path. We demonstrate that the hidden states of probed answers more effectively differentiate distinct solution paths than semantic embeddings, and the perplexity of probed answers serves as a practical proxy for reasoning correctness. Based on these findings, we propose Answer Probing-Guided Tree Search (APTS), which guides the tree search by the probed answers' hidden state similarity and perplexity. Experiments on three reasoning tasks across two LLMs show that APTS consistently enhances solution diversity, demonstrating its effectiveness and robustness.
Submission: Mon, 31 Aug 2026 07:01:36 UTC

## PAPER 9: Skill Compression for Self-Evolving Agents
ID: arxiv:2608.30785
Title: Execution-Aware Dynamic Compression of Progressively Loaded Skills for Self-Evolving Agents
Authors: Xiaofan Bai et al.
Tags: agent, skill, compression, token-efficiency
Abstract: Production agent skills are directory bundles, not isolated prompts. The root is loaded at activation; references, schemas, scripts, assets, and nested subskills are loaded only when an execution path needs them. Compressing only the root misses most deployment cost and may move branch-specific details into the always-loaded context. Flattening instead destroys progressive-loading boundaries. We introduce a method, an evaluation-free compressor for complete, progressively loaded skill bundles. It leaves the agent harness unchanged and emits an ordinary directory. The method combines two safeguards. First, it compresses across files, removing content from a reference or subskill when the root or a declared environment contract already provides it. Second, it preserves routing, so every required file and directly callable entry remains reachable after rewriting. Users can configure the method along two independent axes. One-Shot mode rebuilds the full bundle; Continual mode reuses state and applies Zip-on-Write after each evolution patch. Persistent compression rewrites the shipped bundle to reduce storage and runtime context. Transient compression keeps that bundle byte-identical and builds a task-specific view, reducing only per-run context after build cost. Entry contracts mark private, public, and conditional resources; a multi-entry audit preserves standalone public subskills. On a production content-moderation skill evaluated by our industrial multi-round harness, the method removes 38% of skill bundle tokens and 10.4% of end-to-end per-run tokens with no quality loss, while an unprotected 71% configuration loses up to 26 accuracy points to one-sided false positives. On a multi-entry bundle, the method efficiently reduces token cost while near-perfectly preserving every route and public entry.
Submission: Mon, 31 Aug 2026 13:41:16 UTC

## PAPER 10: OntoAligner-Ensemble
ID: arxiv:2608.31137
Title: Voting-Based Fusion across Heterogeneous Ontology Alignment Techniques
Authors: Hamed Babaei Giglou et al. — ISWC 2026 Workshop
Tags: knowledge-graph, ontology, LLM, ensemble, ISWC2026
Abstract: Ontology alignment (OA) has evolved through several methodological paradigms, ranging from lexical and structural aligners to knowledge graph embedding (KGE) models and, more recently, Large Language Model (LLM)-based approaches. Although modern OA frameworks provide unified ecosystems for deploying these heterogeneous aligners, mechanisms for systematically reconciling their complementary and sometimes conflicting predictions remain relatively underexplored. We present OntoAligner-Ensemble, a modular and aligner-agnostic framework that combines candidate correspondences through a configurable two-stage process comprising voting-based fusion strategies followed by post-fusion selection policies. The framework supports any aligner implemented within OntoAligner that produces candidate correspondences, enabling diverse alignment paradigms to be integrated through a unified decision process. To demonstrate its effectiveness, we instantiate the framework using representative lightweight string-aligner, KGE-based, and Retrieval-Augmented Generation aligners powered by both open-weight and API-based LLMs. We evaluate individual aligners and ensemble configurations across eight benchmark tasks from five OAEI tracks spanning biomedical to beyond-equivalence. The results show that ensemble fusion consistently improves the balance between precision and recall and frequently outperforms standalone aligners across diverse domains. Furthermore, our analysis reveals that ensemble composition directly affects the precision-recall trade-off: heterogeneous cross-paradigm ensembles generally improve precision, whereas homogeneous LLM ensembles more often achieve higher overall F1-scores.
Submission: Mon, 31 Aug 2026 17:44:25 UTC

## PAPER 11: LLM Scale for Ontology Learning
ID: arxiv:2608.31118
Title: When Does Bigger Help? A Controlled Study of LLM Scale for Ontology Learning
Authors: Hamed Babaei Giglou et al. — WOP 2026 workshop at ISWC 2026
Tags: LLM, ontology-learning, scaling, evaluation
Abstract: The effect of Large Language Model (LLM) scale on ontology learning (OL) performance remains insufficiently characterized. We present a controlled evaluation of 13 models spanning dense and Mixture-of-Experts variants from the Qwen3.5 and Qwen3.6 lineages, together with proprietary GPT release variants, using the OntoLearner retrieval-augmented generation pipeline. All models are evaluated with the same embedding model, retrieval configuration, prompt templates, decoding settings, datasets, and metrics on term typing, taxonomy discovery, and non-taxonomic relationship extraction across four biomedical and materials science and engineering ontologies. Within the dense Qwen3.5 lineage, increasing parameter count primarily improves precision rather than recall, with the largest gains occurring between 9B and 27B parameters. However, the effect of scale is neither monotonic nor uniform across tasks and domains. Dense 27B models outperform substantially larger sparse models on term typing, whereas larger Mixture-of-Experts models achieve the strongest open-weight results on taxonomy discovery. Non-taxonomic relationship extraction remains difficult across model scales, particularly for the Materials Data Science ontology. Performance differences across matched Qwen variants and proprietary GPT releases further indicate that architecture and model lineage can outweigh nominal parameter count. These findings show that model size alone is an insufficient selection criterion for OL and provide empirical guidance for reproducible LLM-assisted ontology engineering.
Submission: Mon, 31 Aug 2026 17:30:05 UTC

## PAPER 12: MNIST-PRO for AI Agent Perception
ID: arxiv:2608.31022
Title: MNIST is Back as a Partially Observable World for AI Agents
Authors: Vernon Toh et al.
Tags: agent, perception, partially-observable, benchmark
Abstract: AI agents in partially observable environments need to coordinate active sensing with working memory to maintain an evolving perceptual state. However, existing benchmarks struggle to isolate this perceptual-state construction and interpretation capability because they introduce physical and control complexities. We address this with MNIST-PRO, a benchmark that isolates agentic perception by converting MNIST digit recognition into a sequential, glimpse-based search task with lookback constraints. We evaluate ten multimodal models across four memory representations, including raw visual history, textual states, structured metric grid maps, and a consolidated visual canvas. While models excel under full observability, partial observability exposes a clear performance gap. We identify three distinct bottlenecks. First, perceptual-state construction and interpretation present a challenge, as agents struggle to integrate fragmented glimpses. Second, agents often stop exploring before they see the full sequence. Third, models often fail to revise early, incorrect beliefs even when faced with subsequent contradictory evidence. These results show that simply acquiring visual evidence is not enough. Agents must also be able to build and update a reliable perceptual state.
Submission: Mon, 31 Aug 2026 16:05:39 UTC

## PAPER 13: SimCRAFT Remote Sensing Agent Distillation
ID: arxiv:2608.30277
Title: Distilling Remote Sensing Agents via Synthetic Trajectories and Contextual Retrieval-Augmented Fine-Tuning
Authors: Jing Yao et al.
Tags: agent, distillation, remote-sensing, multi-agent
Abstract: The unprecedented surge in Earth observation data volume and diversity has exposed a critical bottleneck for traditional manual workflows, catalyzing the emergence of Remote Sensing (RS) Agents. However, the practical deployment of these advanced agents is severely hindered by their heavy reliance on large-scale general-purpose LLMs, which lack deep domain expertise and impose prohibitive infrastructure demands. To resolve this, we propose SimCRAFT, a model-agnostic framework that distills sophisticated RS orchestration capabilities into a compact 7B-scale model. Addressing data scarcity, we first pair a multiagent synthesis engine with a Mock Execution Engine that checks schema correctness, inter-tool dependencies, and sensor/tool compatibility, producing SimRS-14k, a large-scale, constraint-validated workflow planning corpus. Second, we propose Contextual Retrieval-Augmented Fine-Tuning (CRAFT) that finetunes the model to reason analogically by adapting retrieved Standard Operating Procedures to novel queries under a noise-robust objective, generalizing RAFT to multi-step RS workflow planning without mechanical copying. Extensive experiments demonstrate that SimCRAFT-7B significantly outperforms openweights LLMs and rivals advanced closed-source models and specialized RS agents, while reproducing across three 7B backbones. This work contributes a competitive open-weights baseline for lightweight RS intelligence, enabling efficient autonomous deployment under resource-constrained or resource-conserving conditions.
Submission: Mon, 31 Aug 2026 05:45:33 UTC

## PAPER 14: CoSC LLM-based Knowledge Graph Completion
ID: arxiv:2608.30235
Title: LLM-Based Knowledge Graph Completion Combining Discrete Structural Coding with Similar Entity Information
Authors: Dongying Lin et al. — ISWC 2026 Posters and Demos Track
Tags: knowledge-graph, LLM, completion, ISWC2026
Abstract: Knowledge graph completion requires models to use both textual descriptions and relational structure. Existing LLM-based methods either encode KG structure as discrete tokens or refine a restricted set of candidate entities, and these two directions have largely been studied separately. We propose CoSC for LLM-based KGC, which combines discrete structural coding with similar entity information. Specifically, an LLM generates an initial candidate entity ranking from discrete structural codes, after which information from entities with structures similar to that of the query entity refines the ranking. Experiments on FB15k-237 show that CoSC outperforms existing baselines on MRR and Hits@10 while remaining competitive on Hits@1.
Submission: Mon, 31 Aug 2026 04:39:44 UTC

## PAPER 15: Policy-Centroid Routing
ID: arxiv:2608.30757
Title: Which Rules Matter Now? Policy-Centroid Routing Before an Intelligent System Acts
Authors: Thomson D. Nguy (Radiant Institute for Manifold Studies)
Tags: policy, routing, AI-safety, governance
Abstract: Before an intelligent system can decide whether an action is allowed, it must first know which rules the action has approached. A single proposed action can implicate several policy regimes at once. Their requirements may stack, overlap, or qualify one another, yet many remain written in natural language while the action itself arrives as an incomplete description of intent. The first problem is not judgment. It is attention. Policy-centroid routing creates a layer before adjudication. It compresses expressions within each policy regime into one or more representative centroids, places the proposed action in the same semantic space, applies a declared measure, and routes every regime crossing a declared threshold to authoritative review. Several regimes may trigger at once. The output is a review agenda, not permission, prohibition, legality, breach, compliance, certification, or enforcement. The paper develops six falsifiable propositions and seven follow-on studies comparing the hypothesis with structured workflows, lexical and semantic retrieval, hierarchical and direct classification, and selective prediction under matched review burden. The studies are designed to identify where policy geometry recovers applicable regimes, where compression loses rare or overlapping obligations, and where the mechanism should abstain. The paper includes a synthetic worked example and reports no empirical efficacy result.
Submission: Mon, 31 Aug 2026 13:24:47 UTC

## PAPER 16: Automated Testing of LLM Explainers
ID: arxiv:2608.30581
Title: Automated Testing of LLM-Based Post Hoc Explainers Using Model Checking as an Oracle
Authors: Dennis Gross et al.
Tags: explainability, testing, model-checking, LLM
Abstract: Large language models (LLMs) are used as post hoc explainers of sequential decision-making policies, producing natural-language explanations of why an action was chosen. However, LLMs often generate plausible but incorrect statements, and no existing approach systematically tests whether such explanations are faithful to the underlying environment. Two classic software testing challenges stand in the way: there is no oracle for the correctness of an explanation, and the test inputs, natural language queries about a policy's behavior, lack the structure needed for systematic test case generation. We address both. Probabilistic model checking provides the test oracle, computing exact reference results against which LLM answers are graded automatically. A taxonomy of post hoc query categories structures the input space around the environment-level facts from which policy explanations are composed; test cases generated from it are prioritized by question-specific diagnostic difficulty scores. Across seven MDP environments, the testing separates three open-weight LLMs: a reasoning model passes 85% of test cases, a mid-size model 70%, and a 1B model falls below the random baseline, while prioritization surfaces significantly harder cases than random selection. Our results indicate how trustworthy LLM-generated explanations are in model-free settings, where the same LLMs are used but no oracle exists to verify them.
Submission: Mon, 31 Aug 2026 10:54:37 UTC

## Trends Summary — September 2026

1. Agent Working Memory — semantic heterogeneity requires specialized management
2. Self-Evolving Agent Security — EvoSkill Injection as new attack surface
3. Token Efficiency — data cracking, skill compression, MoE all targeting cost reduction
4. Industrial Agent Evaluation — dual-horizon diagnostic for production agents
5. MoE + Physical AI — efficient long-context for robotics/embodied AI
6. EEG + XR Agents — physiological signals for faster adaptation
7. Red-Teaming Self-Evolution — security risks in autonomous skill pipelines
8. Knowledge Graph + LLM — ontology alignment, KG completion, reasoning
9. LLM Scaling Studies — controlled studies showing scale isn't everything
10. Agent Benchmark Design — MNIST-PRO for partially observable perception

## Community Sources
- arXiv cs.AI: 424 new submissions on Sep 1, 2026
- Artificial Analysis: Model leaderboards, coding agent index
