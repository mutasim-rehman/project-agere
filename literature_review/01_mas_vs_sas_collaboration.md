# Literature Review: Pillar 1 — Multi-Agent Systems vs. Single-Agent Scaling (Papers 01–08)

This document provides a comprehensive, rigorous literature review of the first 8 papers covering **Single-Agent vs. Multi-Agent System (SAS vs. MAS) comparisons, agent scaling behavior, and orchestration failure modes**.

---

## 01. Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets

* **File:** [`../sources/01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf`](../sources/01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf)
* **Authors:** Dat Tran, Douwe Kiela
* **Affiliation & Venue:** Stanford University — *arXiv:2604.02460 (April 2026, Preprint Under Review)*

### 1. What It Is
An empirical and information-theoretic study demonstrating that reported performance advantages of Multi-Agent Systems (MAS) over Single-Agent Systems (SAS) on multi-hop reasoning tasks are primarily artifacts of increased test-time compute. When both architectures are strictly evaluated under **equal thinking token budgets**, a single agent consistently matches or outperforms multi-agent configurations.

### 2. How It Relates to Our Research
This is our **primary structural baseline template**. Tran & Kiela equalized test-time computation along the **thinking token budget** axis while holding model size constant. Our research adopts their comparative paradigm (SAS vs. sequential, debate, and ensemble MAS) but swaps the controlled resource constraint from *token budget* to *hardware resident VRAM budget ($M$)* and adds model scale + quantization on the single-agent arm.

### 3. Detailed Methodology
* **Models Evaluated:** Qwen3 family, DeepSeek-R1-Distill-Llama, and Gemini 2.5.
* **Architectures Compared:**
  1. *Single-Agent System (SAS):* Chain-of-Thought (CoT) reasoning with scaled token length.
  2. *Sequential MAS:* Pipeline where Agent $A$ passes context to Agent $B$.
  3. *Debate MAS:* Multi-round peer debate and cross-examination.
  4. *Ensemble MAS:* Parallel role generation with majority consensus.
* **Controlled Axis:** Total thinking token budget (enforced across all agent responses combined).
* **Benchmarks:** Multi-hop question answering benchmarks (FRAMES, MuSiQue, HotpotQA).
* **Metrics:** Accuracy (Exact Match / F1), Token Efficiency, Information Retention rate.

### 4. Key Novelty & Theoretical Contributions
* **Data Processing Inequality (DPI) Framing:** Provides an information-theoretic argument that each inter-agent communication handoff represents a lossy compression step ($I(X; Z) \le I(X; Y)$). Unless an agent injects novel external information (e.g., tools), handoffs inherently degrade context.
* **Benchmark Artifact Exposure:** Uncovers that Gemini 2.5 API budget controls and common evaluation harnesses artificially truncate single-agent reasoning while allowing multi-agent prompts to inflate generation tokens.

### 5. Critical Limitations & Caveats
* **Exclusively Reasoning-Focused:** Only evaluates multi-hop QA; ignores tool-use environments (e.g., web search, code interpreters) where division of labor is genuinely advantageous.
* **Zero Model Heterogeneity or Quantization:** Uses the exact same model weights across all agents and does not touch quantization or parameter scaling.
* **Compute vs. Hardware Reality:** Thinking tokens are a soft cost. In edge or single-GPU deployment, hardware memory (VRAM) is a rigid physical barrier, which this paper completely overlooks.

### 6. Why We SHOULD Include It as a Source
* It is the most direct conceptual predecessor to our work. Citing it establishes our paper's primary gap: *"Tran & Kiela equalized compute tokens; we equalize hardware resident memory and investigate the scale-vs-quantization trade-off."*
* Reviewers will immediately respect the structural alignment with a high-profile Stanford preprint.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* It is still an arXiv preprint (April 2026) and has not completed formal peer review. If an advisor or venue demands strictly peer-reviewed base papers, it must be supplemented with a published anchor.

---

## 02. Can Small Agent Collaboration Beat a Single Big LLM?

* **File:** [`../sources/02_Zywot_2026_Can_Small_Agent_Collaboration_Beat_Single_Big_LLM.pdf`](../sources/02_Zywot_2026_Can_Small_Agent_Collaboration_Beat_Single_Big_LLM.pdf)
* **Authors:** Agata Zywot, Xinyi Chen, Maarten de Rijke
* **Affiliation & Venue:** University of Amsterdam — *arXiv:2601.11327 (January 2026, Under Review)*

### 1. What It Is
An empirical investigation into whether collaborative teams of small language models (4B–32B) can outperform a much larger monolithic model (e.g., 32B+ or frontier models) on complex, multi-modal, tool-intensive real-world tasks.

### 2. How It Relates to Our Research
Serves as our **alternative base paper** and primary justification for the tool-augmented MAS arm. It provides empirical evidence that small models can beat large models when task complexity is decomposed across specialized tools, directly informing our hypothesis regarding task type as a moderator of the MAS vs. SAS trade-off.

### 3. Detailed Methodology
* **Models Evaluated:** Qwen3 series (spanning 4B, 8B, 14B, and 32B parameters).
* **Architectures Compared:** Single monolithic model vs. Hierarchical MAS (Orchestrator + Sub-Agents with specialized tools: code interpreter, web search, mind-mapping).
* **Benchmarks:** GAIA (General AI Assistants benchmark, Levels 1–3).
* **Metrics:** Task Completion Rate, Tool Selection Precision, End-to-End Latency, Cost per Solved Task.

### 4. Key Novelty & Theoretical Contributions
* **Isolating Tool Augmentation as the Decisive Equalizer:** Proves that an orchestrated 4B model with proper tool integration outperforms a 32B model lacking tool access on multi-step workflows.
* **Asymmetric Scaling Law in Agents:** Demonstrates that orchestrator capability scales non-linearly: upgrading the central orchestrator from 4B to 14B yields vastly larger system-level gains than upgrading the worker agents.

### 5. Critical Limitations & Caveats
* **Unconstrained Total Parameters:** The multi-agent systems run multiple models without constraining total concurrently loaded weights or resident VRAM.
* **No Quantization Comparison:** Compares a 4B model + tools against a larger unquantized model, rather than testing whether a 14B or 32B model quantized to 4-bit (fitting in the exact same memory) would win.

### 6. Why We SHOULD Include It as a Source
* Uses the exact model family (Qwen) that modern local deployments rely on.
* Provides the definitive citation to counter Tran & Kiela: while SAS wins on pure reasoning, MAS wins on tool-intensive benchmarks like GAIA.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Like Tran & Kiela, it is an early 2026 preprint under review. If our paper focuses solely on closed-book reasoning rather than tool use, GAIA becomes less central.

---

## 03. Towards a Science of Scaling Agent Systems

* **File:** [`../sources/03_Kim_2025_Towards_a_Science_of_Scaling_Agent_Systems.pdf`](../sources/03_Kim_2025_Towards_a_Science_of_Scaling_Agent_Systems.pdf)
* **Authors:** Kim et al.
* **Affiliation & Venue:** Google Research, Google DeepMind, MIT — *arXiv:2512.08296 (Late 2025 / 2026)*

### 1. What It Is
A large-scale foundational study that replaces ad-hoc agent heuristics with formal quantitative scaling laws, investigating how system performance scales across agent count, coordination structures, base model capabilities, and task properties.

### 2. How It Relates to Our Research
Provides the **theoretical scaling framework** for our paper. When we allocate a fixed 16 GB VRAM budget into either 1× 32B (quantized) or 4× 3B (dense) agents, Kim et al.'s framework allows us to predict whether the task's dependency structure will cause the multi-agent system to hit a coordination bottleneck.

### 3. Detailed Methodology
* **Coordination Topologies:** Independent (Parallel), Centralized (Orchestrator-Worker), Decentralized (Peer-to-Peer), and Hybrid topologies.
* **Experimental Scale:** Thousands of evaluation runs across varying model sizes (small to frontier) and agent team sizes ($N = 1$ to $N = 16$).
* **Task Characterization:** Classified tasks along two mathematical dimensions: degree of parallelism vs. degree of sequential dependency.
* **Metrics:** Cross-validated predictive accuracy ($R^2$), Performance ceilings, Scaling exponents.

### 4. Key Novelty & Theoretical Contributions
* **Predictive Topology Model ($R^2 \approx 0.41$):** First model capable of predicting the optimal multi-agent architecture given measurable task characteristics before running inference.
* **Negative Scaling Ceiling:** Proves mathematically and empirically that adding agents to tasks with high sequential dependencies produces negative scaling (performance degradation due to error propagation).

### 5. Critical Limitations & Caveats
* **Ignores Memory Footprint:** Analyzes agent count abstractly without accounting for GPU hardware residency, assuming API-based elasticity where spawning 10 agents has no physical memory penalty.

### 6. Why We SHOULD Include It as a Source
* Essential for Section 2 (Theoretical Framework). It elevates our paper from a purely descriptive benchmark to a principled exploration of agent scaling laws under physical constraints.
* Co-authored by DeepMind, Google Research, and MIT, lending top-tier academic credibility.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* High theoretical density. If our paper is positioned as an empirical systems/MLSys paper rather than an AI theory paper, it can be cited briefly rather than serving as a core baseline.

---

## 04. Mixture-of-Agents Enhances Large Language Model Capabilities

* **File:** [`../sources/04_Wang_2024_Mixture_of_Agents_Enhances_LLM.pdf`](../sources/04_Wang_2024_Mixture_of_Agents_Enhances_LLM.pdf)
* **Authors:** Junlin Wang et al.
* **Affiliation & Venue:** Together AI, Duke University, Stanford University — *arXiv:2406.04692 (June 2024)*

### 1. What It Is
Introduces the **Mixture-of-Agents (MoA)** architecture, which organizes multiple LLMs into sequential layers where each agent synthesizes the outputs of all agents in the previous layer, achieving state-of-the-art open-source LLM performance.

### 2. How It Relates to Our Research
MoA is the primary high-performing multi-agent baseline that argues *in favor* of distributing compute across many models. In our study, MoA represents a candidate MAS topology: can a layered MoA composed of 1B/3B models beat a single 14B/32B quantized model under the exact same VRAM envelope?

### 3. Detailed Methodology
* **Layered Structure:** $L$ layers, each containing $N$ LLM agents. Layer $l$ receives all generations from layer $l-1$ as context.
* **Models Used:** Open-source models (Qwen-1.5, Llama-3, Mixtral) and closed models.
* **Benchmarks:** AlpacaEval 2.0, MT-Bench, and FLASK.
* **Metrics:** Win-rate against GPT-4, Length-controlled win-rate, Per-token generation cost.

### 4. Key Novelty & Theoretical Contributions
* **Collaborativeness Phenomenon:** Shows that LLMs generate higher-quality outputs when presented with responses from other models—even if those other models are weaker than themselves.
* **Open-Source Surpassing Frontier:** First open-source multi-agent system to surpass GPT-4-Omni on AlpacaEval 2.0 (65.1% vs. 57.5%).

### 5. Critical Limitations & Caveats
* **Massive Token Inflation:** The $N \times L$ design creates an $O(N \cdot L)$ token explosion, severely increasing end-to-end latency.
* **Memory Inefficiency:** Running heterogeneous models across multiple layers requires enormous concurrent memory or frequent model weight swapping, making it impractical on single-GPU hardware without extreme quantization.

### 6. Why We SHOULD Include It as a Source
* It is the most influential MAS-wins paper in recent literature. Tran & Kiela (2026) was written specifically to challenge MoA's claims. To present an unbiased literature review, MoA must be cited alongside Tran & Kiela.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our experimental design only tests small agent topologies (2–3 agents) due to VRAM limits, MoA's multi-layer 12+ agent structure may be out of scope for low-memory tiers.

---

## 05. Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key?

* **File:** [`../sources/05_Wang_2024_Rethinking_Bounds_LLM_Reasoning_MultiAgent_Discussions.pdf`](../sources/05_Wang_2024_Rethinking_Bounds_LLM_Reasoning_MultiAgent_Discussions.pdf)
* **Authors:** Qineng Wang, Zihao Wang, Ying Su, Hanghang Tong, Yangqiu Song
* **Affiliation & Venue:** **ACL 2024** (62nd Annual Meeting of the ACL, Long Papers)

### 1. What It Is
A rigorous empirical critique of multi-agent debate frameworks, proving that when single-agent baselines are provided with standard prompt engineering (e.g., few-shot demonstrations, self-consistency), multi-agent debate offers no statistically significant advantage on complex reasoning tasks.

### 2. How It Relates to Our Research
Serves as the peer-reviewed empirical justification for our single-agent baseline design. It guarantees that our single quantized model is benchmarked with state-of-the-art prompt strategies (Chain-of-Thought with verification), ensuring our comparison against MAS is fair and not an artifact of an under-prompted single agent.

### 3. Detailed Methodology
* **Frameworks Tested:** Multi-agent debate (society of minds), round-table discussions, reflection loops vs. single-agent CoT.
* **Models:** ChatGPT (GPT-3.5-Turbo), GPT-4, Llama-2-70B.
* **Benchmarks:** GSM8K, MATH, StrategyQA, ARC-Challenge.
* **Metrics:** Accuracy, Token Consumption, Inter-agent agreement rate, Confidence drift.

### 4. Key Novelty & Theoretical Contributions
* **The "Zero-Shot Illusion":** Demonstrates that prior papers claiming huge gains from multi-agent debate compared against weak, zero-shot single-agent baselines. Adding 3-shot demonstrations to a single agent closes 95%+ of the performance gap.
* **Conformity Effect:** Identifies that weaker agents in a discussion frequently succumb to peer pressure and adopt incorrect answers from confident peers.

### 5. Critical Limitations & Caveats
* Does not evaluate tool-use, code compilation, or multi-modal tasks.
* Does not examine quantization or physical VRAM constraints.

### 6. Why We SHOULD Include It as a Source
* **Fully peer-reviewed ACL 2024 paper.** Reviewers often demand formal conference citations alongside preprints; this paper anchors the single-agent competitiveness argument with gold-standard peer review.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Pre-dates 2025/2026 reasoning models (e.g., DeepSeek-R1, Qwen3) that incorporate native test-time thinking tokens.

---

## 06. More Agents Is All You Need

* **File:** [`../sources/06_Li_2024_More_Agents_Is_All_You_Need.pdf`](../sources/06_Li_2024_More_Agents_Is_All_You_Need.pdf)
* **Authors:** Junyou Li, Qin Zhang, Yangbin Yu, Qiang Fu, Deheng Ye
* **Affiliation & Venue:** Tencent — **TMLR 2024** (Transactions on Machine Learning Research)

### 1. What It Is
An empirical scaling paper showing that simply increasing the number of instantiated LLM agents via sampling-and-voting methods reliably improves performance on complex reasoning tasks without requiring complex coordination protocols.

### 2. How It Relates to Our Research
Provides our baseline for **unstructured multi-agent ensembles**. Under a 16 GB budget, instead of complex orchestrator-worker pipelines, can we simply deploy 3 parallel instances of a 3B/7B model with majority voting to beat a 32B quantized model? Li et al. provides the formal scaling curve for this exact baseline.

### 3. Detailed Methodology
* **Mechanism:** Sampling-and-voting across $N$ independently instantiated agents ($N$ varying from 1 to 20+).
* **Models:** Llama-2-13B, Llama-2-70B, GPT-3.5-Turbo.
* **Benchmarks:** GSM8K, SVAMP, HumanEval, MMLU.
* **Metrics:** Task Accuracy as a function of agent count, Task Difficulty correlation.

### 4. Key Novelty & Theoretical Contributions
* **Orthogonality of Agent Scaling:** Shows that agent scaling via voting is orthogonal to prompting techniques (e.g., CoT or Reflexion) and can be stacked on top of them.
* **Task Difficulty Dependence:** Demonstrates that simple tasks hit accuracy plateaus quickly, whereas hard tasks exhibit power-law-like improvements as agent count increases.

### 5. Critical Limitations & Caveats
* **Inefficient for Latency/Memory:** Running $N$ parallel instances simultaneously multiplies memory consumption unless run sequentially with significant wall-clock latency penalties.
* **No Parametric Specialization:** All agents are clones of the same base model; there is no division of labor or specialized tooling.

### 6. Why We SHOULD Include It as a Source
* Published in TMLR 2024; provides the cleanest, mathematically simplest multi-agent baseline (majority voting) to test against our quantized single agent.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our paper focuses strictly on *collaborative* MAS (orchestrators, communication, tools) rather than parallel self-consistency voting ensembles, this paper plays a secondary role.

---

## 07. Why Do Multi-Agent LLM Systems Fail?

* **File:** [`../sources/07_Cemri_2025_Why_Do_Multi_Agent_LLM_Systems_Fail.pdf`](../sources/07_Cemri_2025_Why_Do_Multi_Agent_LLM_Systems_Fail.pdf)
* **Authors:** Mert Cemri et al.
* **Affiliation & Venue:** *arXiv:2503.13657 (March 2025)*

### 1. What It Is
A forensic empirical failure analysis introducing **MAST (Multi-Agent System Failure Taxonomy)** and a dataset of 1,600+ annotated interaction traces across 7 popular MAS frameworks, identifying why multi-agent systems frequently underperform on benchmarks.

### 2. How It Relates to Our Research
Provides the **diagnostic framework** for our Discussion and Error Analysis sections. When our small multi-agent setup loses to the large quantized single agent, MAST provides the exact taxonomy to classify whether the failure was due to specification design (41.8%), inter-agent misalignment (36.9%), or verification breakdown (21.3%).

### 3. Detailed Methodology
* **Taxonomy:** 14 distinct failure modes grouped into 3 operational clusters.
* **Frameworks Evaluated:** AutoGen, MetaGPT, ChatDev, CrewAI, Camel, and custom frameworks.
* **Dataset:** MAST-Data (1,600+ multi-turn interaction traces manually and automatically labeled).
* **Metrics:** Failure mode frequency distribution, Cascading error propagation probability.

### 4. Key Novelty & Theoretical Contributions
* **Error Amplification Discovery:** Demonstrates quantitatively that small initial errors or hallucinations by early sub-agents compound exponentially in downstream agent handoffs because agents lack internal self-correcting state estimators.
* **Context Collapse Quantification:** Shows that passing accumulated dialogue histories causes instruction drift and goal mutation, severely degrading small models with limited context-handling capacity.

### 5. Critical Limitations & Caveats
* Descriptive and diagnostic rather than algorithmic; does not propose a new coordination architecture to solve the identified failures.

### 6. Why We SHOULD Include It as a Source
* Essential for interpreting experimental failures. Reviewers love seeing a rigorous error taxonomy in the ablation/discussion section rather than hand-wavy explanations.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If page limits are extremely tight (e.g., 8 pages), detailed failure taxonomy discussions may be compressed into a single citation in Related Work.

---

## 08. MAS-Orchestra: Benchmarking Holistic Multi-Agent Orchestration

* **File:** [`../sources/08_Ke_2026_MAS_Orchestra_Holistic_Multi_Agent_Orchestration.pdf`](../sources/08_Ke_2026_MAS_Orchestra_Holistic_Multi_Agent_Orchestration.pdf)
* **Authors:** Ke et al.
* **Affiliation & Venue:** *arXiv:2601.14652 (January 2026)*

### 1. What It Is
A dedicated benchmarking framework designed to evaluate the orchestration capabilities of multi-agent LLM systems across complex, multi-agent workflows under communication and resource constraints.

### 2. How It Relates to Our Research
Informs the **orchestration protocol** of our MAS arm. It provides standardized metrics for message routing, task decomposition efficiency, and communication overhead when orchestrating smaller LLMs.

### 3. Detailed Methodology
* **Evaluation Dimensions:** Dynamic task planning, sub-agent dispatching, inter-agent communication compactness, and failure recovery.
* **Topologies Tested:** Hierarchical orchestrators, router-based networks, and blackboard architectures.
* **Metrics:** Orchestration Success Rate, Communication-to-Computation Ratio (CCR), Redundant Message Rate.

### 4. Key Novelty & Theoretical Contributions
* **Holistic Orchestration Scoring:** Separates base model reasoning power from orchestrator coordination skill, demonstrating that poor multi-agent performance is often caused by orchestration bottlenecks rather than sub-agent execution failures.

### 5. Critical Limitations & Caveats
* Does not evaluate physical GPU memory allocation or hardware-level resident weight budgeting.

### 6. Why We SHOULD Include It as a Source
* Establishes contemporary 2026 standards for measuring multi-agent orchestration efficiency, showing that our evaluation protocol aligns with the latest literature.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Highly specialized for orchestration benchmarks; if our experiments rely on established benchmarks like GAIA, FRAMES, and GSM8K, MAS-Orchestra can be filtered out to prioritize core quantization and budget papers.
