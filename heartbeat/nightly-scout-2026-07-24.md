# NightOps Scout Report — 2026-07-24

**Generated:** 2026-07-24 21:30 CST (Asia/Shanghai)  
**Window:** NightOps (Mon-Fri 21:30-23:30)  
**Model:** longcat/LongCat-2.0

---

## 📊 Daily Summary

- **arXiv cs.AI new listings:** 123 papers (354 total entries including cross-lists/replacements)
- **Key themes:** Agentic AI, LLM safety/robustness, inference optimization, multi-agent systems, benchmarking, watermarking, deception detection
- **Notable trend:** Heavy focus on agent safety, runtime restructuring, and evaluation methodologies

---

## 🔥 Top Papers of the Day

### 1. Autonomous Topology Mutation for Multi-Agent Systems
**arXiv:** [2607.20488](https://arxiv.org/abs/2607.20488)  
**Title:** Autonomous Topology Mutation: Safe Runtime Restructuring for Multi-Agent LLM Systems with Capability, State, and Shadow Invariants

Multi-agent LLM frameworks typically fix team topology at boot time. ATM introduces runtime team-mutation with three safety invariants: capability monotonicity, state-routing completeness, and shadow-before-live validation. Uses a six-signal Bottleneck Index (queue depth, context thrash, tool-error rate, role entropy, retry-loop rate, cross-agent wait time). On 720 DeepSeek-V3-driven task runs, ATM factoriser lifts code-task success from 3.3% to 61.7%. Privacy exposure reduced from 2.0 to 0.0 events per task. Runtime overhead: <500μs p99 latency.

**Key insight:** Runtime restructuring of agent teams is feasible and dramatically improves task success without compromising safety.

---

### 2. Robust Critics: Defending LLMs Against Multi-Turn Attacks
**arXiv:** [2607.20472](https://arxiv.org/abs/2607.20472)  
**Title:** Robust Critics: Defending LLMs Against Multi-Turn Attacks

Proposes Dialogue Critic Guided Sampling (DCGS), modeling adversarial dialogue as a Markov Decision Process. Learns value and regret-based critics at both token and utterance levels. Proves inference-time reweighting approximates exponential tilting of the base policy. Outperforms strong baselines on CARES-18k, WildJailbreak, Redbench, and Harmbench. Transfers to frontier models without fine-tuning.

**Key insight:** Multi-turn safety requires trajectory-level reasoning, not just per-turn classification.

---

### 3. Incomplete Prompt Jailbreaks in LLMs
**arXiv:** [2607.20473](https://arxiv.org/abs/2607.20473)  
**Title:** Incomplete Prompt Jailbreaks in Large Language Models

Formalizes "incomplete prompt jailbreaks" (IPJ) — sentence completion vulnerability to incomplete harmful prompts. Shows LLMs systematically delay refusal until sentence termination. Training models to refuse via parameter tuning is insufficient. Identifies two functional neurons: termination and continuation neurons, highlighting potential for neuron-level interventions.

**Key insight:** Current safety training fails on incomplete prompts; neuron-level interventions may be needed.

---

### 4. Benchmarking Autonomous TPU Kernel Optimization (JAXBench)
**arXiv:** [2607.20466](https://arxiv.org/abs/2607.20466)  
**Title:** Benchmarking Autonomous TPU Kernel Optimization

Introduces JAXBench, a TPU-native benchmark suite with 50 JAX workloads for AI-generated kernel optimization. Evaluates four feedback-driven methods with Gemini 3 Flash. Target-specific context matters more than model scale on Pallas DSL. Curated TPU documentation raises correctness from 5.8% to 37.3%. Autocomp's beam-search pipeline reaches 1.36x geomean speedup over XLA.

**Key insight:** AI agents can optimize TPU kernels but need domain-specific documentation to be effective.

---

### 5. InferenceBench: Open-Ended LLM Inference Optimization by AI Agents
**arXiv:** [2607.20468](https://arxiv.org/abs/2607.20468)  
**Title:** A Benchmark for Open-Ended LLM Inference Optimization by AI Agents

InferenceBench requires agents to deploy an OpenAI-compatible inference server and optimize LLM inference speed on a single H100 GPU with a 2-hour budget. Across 15 frontier agent configurations, agents improve up to 8.08× over naive PyTorch baseline, often match vLLM defaults (4.05×), but fall below hyperparameter search (11.53×). Agents converge on a single inference framework and test few configurations.

**Key insight:** Current agents lack the ability to propose diverse configurations systematically — the bottleneck is exploration, not domain knowledge.

---

### 6. Stochastic Sampling is Epistemically Shallow
**arXiv:** [2607.20464](https://arxiv.org/abs/2607.20464)  
**Title:** Stochastic Sampling is Epistemically Shallow: The Dimensionality Gap Between Temperature Variation and Model Diversity in LLMs

Compares one model run 100 times at τ=1 vs. an ensemble of 24 LLMs run once each at τ=0. Within any single model, at most one dimension rises above noise. Across the ensemble, four eigenvalues clear the noise edge. Self-consistency gives per-question uncertainty but no detectable cross-question structure; only diverse ensembles surface what a model does not know.

**Key insight:** Temperature-based diversity ≠ model diversity. Ensembles reveal knowledge gaps that self-consistency cannot.

---

### 7. Multi-Agent Discovery of Typed Optimizer Programs (OPTScientist)
**arXiv:** [2607.20486](https://arxiv.org/abs/2607.20486)  
**Title:** Multi-Agent Discovery of Typed Optimizer Programs for Transformer Pretraining

OPTScientist: a theory-guided multi-agent framework using four role agents (Theorist, Designer, Engineer, Reviewer) for optimizer discovery in a typed DSL. Combines evolutionary search with DSL extension mechanism. Discovers RS-MR, a reduced-state matrix optimizer improving transformer pretraining.

**Key insight:** Multi-agent collaboration with typed DSLs enables automated scientific discovery with theoretical grounding.

---

### 8. Benchmarking Observable Agent Instability in Financial Decision-Making (DFAH-Bench)
**arXiv:** [2607.20491](https://arxiv.org/abs/2607.20491)  
**Title:** Benchmarking Observable Agent Instability in Financial Decision-Making

DFAH-Bench measures behavioral instability across tool-call trajectories, evidence contacts, and decision concentration. Across 8,127 replay episodes (10 models, 3 financial tasks): frontier models agree on decisions 95% of the time but follow the same tool path only 77% — an 18pp gap. Three behavioral profiles: pattern matchers, stable executors, trajectory divergers.

**Key insight:** Outcome agreement masks significant process instability in agent systems.

---

### 9. Expectation Alignment of Language Models (ExpectBench)
**arXiv:** [2607.20485](https://arxiv.org/abs/2607.20485)  
**Title:** Expectation Alignment of Language Models for Real-World User Expectations

First systematic study of user expectations in real-world LLM interactions. Introduces ExpectBench grounded in real user expectations. Current LLMs struggle to satisfy and anticipate user hopes. Proposes LENS, a lightweight latent expectation-aware response generation framework that internalizes user expectations.

**Key insight:** There's a fundamental misalignment between benchmark performance and real user expectations.

---

### 10. Tractable Hierarchical Control of Autoregressive Language Models
**arXiv:** [2607.20483](https://arxiv.org/abs/2607.20483)  
**Title:** Tractable Hierarchical Control of Autoregressive Language Models

Demonstrates that satisfaction of any LR(k) grammar of finite duration can be calculated in polynomial time. Enables efficient constraint and steering of LLM generation towards output satisfying formal syntactic constraints. Applicable to SQL, JSON, and other context-free grammars.

**Key insight:** Polynomial-time constrained generation is achievable for practical formal grammars.

---

## 📈 Trend Analysis

### Rising Themes (July 2026)
1. **Agent Safety & Robustness** — Multi-turn attacks, incomplete prompt jailbreaks, runtime safety invariants
2. **Agent Evaluation** — Process stability (not just outcome), inference optimization benchmarks, financial agent instability
3. **Multi-Agent Systems** — Runtime topology mutation, collaborative discovery frameworks, typed DSLs
4. **LLM Inference Efficiency** — TPU kernel optimization, speculative decoding acceleration, unified sampling kernels
5. **Knowledge & Reasoning** — Stochastic sampling limits, decode-time decision subspaces, representation collapse mitigation

### Key Takeaways
- **Safety is shifting from static to dynamic:** Runtime restructuring (ATM) and multi-turn defense (DCGS) represent a move toward continuous safety
- **Evaluation is maturing:** From outcome-only to process-aware metrics (DFAH-Bench, InferenceBench)
- **Agents are being treated as engineering systems:** With telemetry, bottlenecks, and runtime optimization — not just prompt engineering

---

## 🔗 Cross-References

- ATM (2607.20488) ↔ DFAH-Bench (2607.20491): Both address agent runtime stability
- DCGS (2607.20472) ↔ IPJ (2607.20473): Complementary safety approaches (multi-turn vs. single-turn)
- OPTScientist (2607.20486) ↔ JAXBench (2607.20466): Multi-agent discovery meets automated benchmarking
- ExpectBench (2607.20485) ↔ SDR-Bench (2607.20471): Both study personalization and user expectations

---

*Next scout: 2026-07-25 21:30 CST*
