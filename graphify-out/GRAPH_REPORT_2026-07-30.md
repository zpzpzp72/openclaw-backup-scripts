# Graph Report - graphify-raw  (2026-07-30)

## Corpus Check
- Corpus is ~2,306 words - fits in a single context window. You may not need a graph.

## Summary
- 67 nodes · 89 edges · 10 communities detected
- Extraction: 63% EXTRACTED · 37% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]

## God Nodes (most connected - your core abstractions)
1. `NightOps Scout 2026-07-30` - 9 edges
2. `Benchmarking` - 7 edges
3. `OPTScientist: Multi-Agent Optimizer Discovery` - 5 edges
4. `DFAH-Bench: Agent Instability` - 5 edges
5. `Multi-Agent Systems` - 5 edges
6. `DCGS: Multi-Turn Attack Defense` - 4 edges
7. `IPJ: Incomplete Prompt Jailbreaks` - 4 edges
8. `SonicSampler: LLM Sampling Kernels` - 4 edges
9. `PersonaTrail: Personalized Web Agents` - 4 edges
10. `ExpectBench: User Expectation Alignment` - 4 edges

## Surprising Connections (you probably didn't know these)
- `ATM: Autonomous Topology Mutation` --semantically_similar_to--> `DFAH-Bench: Agent Instability`  [INFERRED] [semantically similar]
  graphify-raw/2607.20488.txt → graphify-raw/2607.20491.txt
- `JAXBench: TPU Kernel Optimization` --semantically_similar_to--> `InferenceBench: LLM Inference Optimization`  [INFERRED] [semantically similar]
  graphify-raw/2607.20466.txt → graphify-raw/2607.20468.txt
- `SDR-Bench: LLM Personalization` --semantically_similar_to--> `ExpectBench: User Expectation Alignment`  [INFERRED] [semantically similar]
  graphify-raw/2607.20471.txt → graphify-raw/2607.20485.txt
- `DCGS: Multi-Turn Attack Defense` --semantically_similar_to--> `IPJ: Incomplete Prompt Jailbreaks`  [INFERRED] [semantically similar]
  graphify-raw/2607.20472.txt → graphify-raw/2607.20473.txt
- `SonicSampler: LLM Sampling Kernels` --related_to--> `Kernel Optimization`  [INFERRED]
  graphify-raw/2607.20475.txt → graphify-raw/2607.20466.txt

## Hyperedges (group relationships)
- **AI Safety & Dual-Use Knowledge Control** — claude_mythos_crypto, hawk_signature, gram_dual_use, j_space [INFERRED 0.75]
- **Physical World AI Control** — project_pilot_drone, drone_bench, claude_robotics [EXTRACTED 0.90]
- **Agent Framework Ecosystem** — deep_agents_v07, langchain_nvidia_nemoclaw, governed_agents, langgraph_3years, apollo_deep_agents, agent_sandbox [EXTRACTED 0.85]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.21
Nodes (12): Apollo Deep Agents Case Study, Claude Mythos Crypto Discovery, Claude Plays Robotics, Deep Agents v0.7, Drone-Bench Benchmark, GRAM: Gradient-Routed Auxiliary Modules, HAWK Post-Quantum Signature, J-Space: Global Workspace in LLMs (+4 more)

### Community 1 - "Community 1"
Cohesion: 0.33
Nodes (9): Benchmarking, LLM Inference Optimization, Kernel Optimization, Process Evaluation, Agent Stability, Tool Use, DFAH-Bench: Agent Instability, InferenceBench: LLM Inference Optimization (+1 more)

### Community 2 - "Community 2"
Cohesion: 0.32
Nodes (8): Critic-Generator Co-Evolution, Domain-Specific Languages, Evolutionary Search, Optimization Theory, Text-to-SQL, EvoSQL: Text-to-SQL Co-Evolution, OPTScientist: Multi-Agent Optimizer Discovery, VeriSimpl: Optimization Modeling

### Community 3 - "Community 3"
Cohesion: 0.25
Nodes (8): ARC-AGI-3 Benchmark, ChatGPT for Academic Researchers, Claude Code in Practice (400K sessions), Claude Fable 5, GPT-5.6 Model Family, GPT-5.6 Sol, Retained Reasoning + Compaction, Scientific Computing in Agentic AI

### Community 4 - "Community 4"
Cohesion: 0.43
Nodes (7): Attention Mechanisms, Formal Grammar Constraints, Representation Collapse, Sampling & Decoding, SonicSampler: LLM Sampling Kernels, Tractable Hierarchical Control, TRSP: Representation Collapse Mitigation

### Community 5 - "Community 5"
Cohesion: 0.43
Nodes (7): Memory-Augmented Systems, Personalization, User Expectations, Web Agents, ExpectBench: User Expectation Alignment, PersonaTrail: Personalized Web Agents, SDR-Bench: LLM Personalization

### Community 6 - "Community 6"
Cohesion: 0.43
Nodes (7): Jailbreak Attacks, LLM Safety, Markov Decision Processes, Multi-Turn Dialogue, Neuron-Level Interventions, DCGS: Multi-Turn Attack Defense, IPJ: Incomplete Prompt Jailbreaks

### Community 7 - "Community 7"
Cohesion: 0.47
Nodes (6): Agentic AI, Multi-Agent Systems, Runtime Safety Invariants, Agent Topology, AINTMA: Agentic Test Management, ATM: Autonomous Topology Mutation

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (2): Governed Agents Framework, 3 Years of LangGraph Engineering

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (1): Agents Need Their Own Computer

## Knowledge Gaps
- **13 isolated node(s):** `VeriSimpl: Optimization Modeling`, `Jailbreak Attacks`, `Text-to-SQL`, `Retained Reasoning + Compaction`, `HAWK Post-Quantum Signature` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 8`** (2 nodes): `Governed Agents Framework`, `3 Years of LangGraph Engineering`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `Agents Need Their Own Computer`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Benchmarking` connect `Community 1` to `Community 5`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `ATM: Autonomous Topology Mutation` connect `Community 7` to `Community 1`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does `OPTScientist: Multi-Agent Optimizer Discovery` connect `Community 2` to `Community 7`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Multi-Agent Systems` (e.g. with `Agentic AI` and `Agent Topology`) actually correct?**
  _`Multi-Agent Systems` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `VeriSimpl: Optimization Modeling`, `Jailbreak Attacks`, `Text-to-SQL` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._