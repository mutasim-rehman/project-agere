# Literature Review: Pillar 1 (Continued) — Multi-Agent Topologies & Frameworks (Papers 09–14)

This document provides a comprehensive, rigorous literature review of Papers 09 through 14, covering the foundational **Multi-Agent System (MAS) topologies, collaborative frameworks, and communication protocols**.

---

## 09. AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors

* **File:** [`../sources/09_Chen_2024_AgentVerse_Multi_Agent_Collaboration.pdf`](../sources/09_Chen_2024_AgentVerse_Multi_Agent_Collaboration.pdf)
* **Authors:** Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, Chenfei Yuan, Chi-Min Chan, Heyang Yu, Yaxi Lu, Yi-Hsin Hung, Chen Qian, Yujia Qin, Xin Cong, Ruobing Xie, Zhiyuan Liu, Maosong Sun, Jie Zhou
* **Affiliation & Venue:** Tsinghua University, ModelBest, Tencent — **ICLR 2024**

### 1. What It Is
An open-source multi-agent platform designed to deploy autonomous LLM agents that dynamically assemble, plan, execute, and evaluate collaborative problem-solving pipelines across both task-solving workflows and social simulations.

### 2. How It Relates to Our Research
Provides the **software architecture and prompt templates** for implementing multi-agent collaboration in our experiments. Specifically, AgentVerse's modular stages (Expert Recruitment $\to$ Collaborative Decision-Making $\to$ Action Execution $\to$ Evaluation) supply the architectural scaffolding for our small-agent MAS configurations.

### 3. Detailed Methodology
* **Core Modules:**
  1. *Recruitment:* Dynamically selects which agents to instantiate based on task requirements.
  2. *Planning:* Facilitates consensus generation among agents before execution.
  3. *Execution:* Agents carry out subtasks.
  4. *Evaluation:* Verifies the final state against the original goal.
* **Benchmarks:** Text evaluation, math reasoning, Minecraft embodied agent tasks, and software consulting.
* **Metrics:** Task success rate, Collaboration efficiency, Communication rounds to consensus.

### 4. Key Novelty & Theoretical Contributions
* **Dynamic Group Formation:** Demonstrates that fixed agent teams often fail on diverse tasks, whereas dynamically adjusting team composition based on task complexity significantly boosts success rates.
* **Dual Framework Paradigm:** First unified system supporting both deterministic task-solving and open-ended social emergent simulation within a single agent abstraction.

### 5. Critical Limitations & Caveats
* High token overhead due to multi-turn group recruitment and planning phases.
* Assumes unconstrained memory access; does not provide runtime scheduling or KV-cache optimization for local GPU residency.

### 6. Why We SHOULD Include It as a Source
* **Top-tier ICLR 2024 publication.** Citing AgentVerse justifies our multi-agent architecture as adhering to established, peer-reviewed collaborative standards rather than an arbitrary home-grown prompt setup.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our paper chooses MetaGPT or ChatDev as its primary multi-agent codebase, AgentVerse serves as an adjacent related-work citation rather than a core experimental component.

---

## 10. ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate

* **File:** [`../sources/10_Chan_2024_ChatEval_Multi_Agent_Debate.pdf`](../sources/10_Chan_2024_ChatEval_Multi_Agent_Debate.pdf)
* **Authors:** Chi-Min Chan, Weize Chen, Yusheng Su, Jianxuan Yu, Wei Xue, Shanghang Zhang, Jie Fu, Zhiyuan Liu
* **Affiliation & Venue:** Tsinghua University, HKUST, Peking University — **ICLR 2024**

### 1. What It Is
A multi-agent debate framework that uses a committee of distinct LLM "referees" to evaluate generated text through structured, multi-turn debate, overcoming the individual biases and hallucinations of single LLM judges.

### 2. How It Relates to Our Research
Supplies the exact **peer-debate protocol** tested in our Multi-Agent Debate arm. When comparing a single large quantized model against small models debating each other, ChatEval provides the prompt structures, persona assignments, and consensus-reaching mechanisms for fair peer evaluation.

### 3. Detailed Methodology
* **Debate Protocol:** Multiple persona-assigned agents (e.g., Accuracy Critic, Fluency Critic, Domain Specialist) independently score outputs, review peer scores, exchange critique, and revise ratings.
* **Benchmarks:** Text summarization (CNN/DailyMail), Dialogue generation, Translation, Open-ended QA.
* **Metrics:** Correlation with human judgment (Spearman $\rho$, Pearson $r$), Evaluation variance reduction.

### 4. Key Novelty & Theoretical Contributions
* **Mitigating Single-Judge Bias:** Quantitatively demonstrates that single LLM judges suffer from position bias, verbosity bias, and egocentric bias, which multi-agent debate reliably mitigates.
* **Higher Human Alignment:** Shows that a committee of smaller/cheaper models debating each other aligns more closely with human ground-truth rankings than a single monolithic judge.

### 5. Critical Limitations & Caveats
* Linear increase in evaluation cost ($N$ agents $\times R$ debate rounds multiplies total token generation by $N \cdot R$).
* Vulnerable to peer cascade: if two agents share a common misunderstanding, they frequently convince the third agent to adopt the erroneous consensus.

### 6. Why We SHOULD Include It as a Source
* **Published at ICLR 2024.** Establishes the scientific legitimacy of using multi-agent debate as a reasoning and verification mechanism in our benchmark comparisons.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Specifically framed around "LLM-as-a-judge" evaluation rather than solving downstream math or tool-use problems. Can be trimmed if focusing solely on task execution.

---

## 11. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

* **File:** [`../sources/11_Hong_2024_MetaGPT_Multi_Agent_Collaborative_Framework.pdf`](../sources/11_Hong_2024_MetaGPT_Multi_Agent_Collaborative_Framework.pdf)
* **Authors:** Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Cheng Cheng, Ceyao Zhang, Jinlin Wang, Zili Wang, Steven Hoi Yau, Deyu Zhou, Chenglin Zou, Deng Jia, Jiayi Yuan, Jürgen Schmidhuber, et al.
* **Affiliation & Venue:** DeepWisdom, KAUST — **ICLR 2024 (Oral Presentation)**

### 1. What It Is
A pioneering multi-agent meta-programming framework that incorporates human software engineering **Standard Operating Procedures (SOPs)** to structure agent collaboration through structured output schemas (PRDs, architecture diagrams, API specs) rather than free-form natural language chat.

### 2. How It Relates to Our Research
Serves as the blueprint for our **Hierarchical Orchestrator-Worker MAS topology**. MetaGPT demonstrates that smaller models perform drastically better when restricted to rigid, structured intermediate formats (SOPs) rather than unconstrained chat, directly guiding how we prevent small sub-agents from hallucinating under tight memory budgets.

### 3. Detailed Methodology
* **Workflow:** Replicates waterfall and agile software engineering stages:
  1. *Product Manager:* Generates PRD.
  2. *Architect:* Designs system interfaces and data structures.
  3. *Project Manager:* Breaks design into distinct file tasks.
  4. *Engineer:* Writes code and unit tests.
  5. *QA Engineer:* Executes and debugs test suites.
* **Communication Channel:** Shared publish-subscribe message broker with typed schema documents.
* **Benchmarks:** HumanEval, MBPP, complex end-to-end multi-file software creation.
* **Metrics:** Pass@1 accuracy, Executability rate, Code complexity, Token efficiency.

### 4. Key Novelty & Theoretical Contributions
* **SOP-Constrained Communication:** Proves that replacing natural language chatter with standardized engineering artifacts (e.g., Markdown tables, JSON schemas, UML diagrams) drastically reduces inter-agent hallucination cascading.
* **ICLR 2024 Oral:** One of the highest-impact open-source agent frameworks (40k+ GitHub stars), validating real-world multi-agent division of labor.

### 5. Critical Limitations & Caveats
* Highly tailored to software engineering; less naturally applicable to closed-book factual QA or single-step mathematical deduction.
* Significant token consumption due to verbose documentation generation at each pipeline phase.

### 6. Why We SHOULD Include It as a Source
* **Top-tier ICLR 2024 Oral publication.** Gives our hierarchical MAS implementation an unimpeachable academic precedent. Reviewers widely recognize MetaGPT as the gold standard for structured agent collaboration.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our paper's experiments strictly avoid software engineering tasks (e.g., focusing only on QA and GAIA), MetaGPT's code-generation focus may be slightly tangential.

---

## 12. ChatDev: Communicative Agents for Software Development

* **File:** [`../sources/12_Qian_2024_ChatDev_Communicative_Agents_Software_Development.pdf`](../sources/12_Qian_2024_ChatDev_Communicative_Agents_Software_Development.pdf)
* **Authors:** Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen, Yufan Dang, Jiahao Li, Cheng Yang, Weize Chen, Yusheng Su, Xin Cong, Juyuan Xu, Dahai Li, Zhiyuan Liu, Maosong Sun
* **Affiliation & Venue:** Tsinghua University, ModelBest Inc. — **ACL 2024 (Long Papers)**

### 1. What It Is
A communicative multi-agent framework that structures the entire software development lifecycle into specialized, multi-phase chat chains where pairs of agents (e.g., CEO $\leftrightarrow$ CPO, CTO $\leftrightarrow$ Programmer, Programmer $\leftrightarrow$ Reviewer) converse to complete concrete subtasks.

### 2. How It Relates to Our Research
Represents our canonical **Sequential Pipeline MAS topology** (Decompose $\to$ Execute $\to$ Verify). ChatDev demonstrates how dividing a complex objective into paired conversational steps enables smaller models to solve multi-step problems that exceed a single model's context capacity.

### 3. Detailed Methodology
* **Architecture:** Sequential multi-stage pipeline: *Designing $\to$ Coding $\to$ Testing $\to$ Documenting*.
* **Interaction Mechanism:** "Chat Chain" — at each node, two complementary agents engage in multi-turn conversation with memory reflection and subtask consensus before advancing.
* **Benchmarks:** End-to-end software synthesis, task completion rate, bug injection testing.
* **Metrics:** Software completeness, Code executability, Software manufacturing cost ($<\$1$ per utility application), Average time per development run.

### 4. Key Novelty & Theoretical Contributions
* **Decomposed Conversational Chains:** Shows that breaking a complex goal into granular, two-agent peer dialogues prevents context overload and keeps agents focused on specific, verifiable deliverables.
* **Collaborative Self-Correction:** Demonstrates that peer code review and tester agents catch 70%+ of syntax and logic bugs introduced by coder agents before final output.

### 5. Critical Limitations & Caveats
* High cumulative execution latency: sequential chat chains require multiple round trips, compounding wall-clock time compared to single-agent generation.
* Context propagation overhead: maintaining history across consecutive chat nodes consumes substantial prompt tokens.

### 6. Why We SHOULD Include It as a Source
* **Published in ACL 2024.** Establishes the peer-reviewed empirical validity of sequential multi-agent pipelines, providing our experimental pipeline with a direct, citable baseline.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Highly overlapping in conceptual scope with MetaGPT. When filtering to 15 core papers, we can retain MetaGPT (ICLR Oral) and omit ChatDev to avoid redundancy.

---

## 13. Dynamic LLM-Agent Network: An LLM-Agent Collaboration Framework with Dynamic Architecture (DyLAN)

* **File:** [`../sources/13_Liu_2024_Dynamic_LLM_Agent_Network_DyLAN.pdf`](../sources/13_Liu_2024_Dynamic_LLM_Agent_Network_DyLAN.pdf)
* **Authors:** Liu et al.
* **Affiliation & Venue:** **ICLR 2024**

### 1. What It Is
A dynamic multi-agent framework that dynamically selects, ranks, and prunes agent team members across execution rounds based on their quantifiable contributions, preventing unnecessary communication overhead.

### 2. How It Relates to Our Research
Directly addresses the **memory and communication efficiency** of our MAS arm. In a memory-constrained hardware environment, DyLAN provides the algorithmic justification for dynamically deactivating or pruning non-essential agents to conserve VRAM and KV-cache space.

### 3. Detailed Methodology
* **Dynamic Architecture:**
  1. *Agent Importance Scoring:* Measures each agent's contribution to the task state via an Agent-Importance metric.
  2. *Dynamic Pruning:* Drops bottom-performing agents from subsequent discussion rounds.
  3. *Early Stopping:* Halts execution when agent consensus converges.
* **Benchmarks:** Arithmetic reasoning (GSM8K, SVAMP), Code generation (HumanEval), Multi-hop QA (HotpotQA).
* **Metrics:** Accuracy vs. Token Consumption Pareto curve, Pruning efficiency, Latency reduction.

### 4. Key Novelty & Theoretical Contributions
* **First Dynamic Topology Framework:** Moves beyond static multi-agent graphs, demonstrating that fixed agent teams waste 40%+ of their tokens on uninformative chatter.
* **Dual Efficiency Gain:** Improves reasoning accuracy while simultaneously cutting token consumption by pruning distracting or low-performing agent outputs.

### 5. Critical Limitations & Caveats
* Requires additional scoring passes to evaluate agent importance, which introduces computation overhead in lightweight settings.
* Does not evaluate physical GPU memory allocation or quantized model backbones.

### 6. Why We SHOULD Include It as a Source
* **ICLR 2024 paper.** Provides the ideal citation when discussing how multi-agent systems can be optimized for resource-constrained deployment by pruning communication redundancy.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Adds architectural complexity beyond standard static MAS baselines (hierarchical, debate, pipeline). Can be cited in the Discussion rather than implemented as a primary baseline.

---

## 14. ReConcile: Round-Table Discussion Improves Reasoning via Consensus

* **File:** [`../sources/14_Chen_2024_ReConcile_Round_Table_Discussion.pdf`](../sources/14_Chen_2024_ReConcile_Round_Table_Discussion.pdf)
* **Authors:** Chen et al.
* **Affiliation & Venue:** **ACL 2024** (Main Conference)

### 1. What It Is
A round-table discussion framework that enables heterogeneous LLM agents to engage in multi-round debate, present counterarguments, and adjust confidence levels to converge on a unified consensus answer for complex reasoning problems.

### 2. How It Relates to Our Research
Provides a strong, peer-reviewed **multi-model consensus baseline**. When exploring whether heterogeneous small models (e.g., 1× Qwen-3B + 1× Llama-3B + 1× Mistral-3B) can outperform a single large quantized model (e.g., Qwen-14B 4-bit) under equal memory, ReConcile supplies the exact consensus mechanism.

### 3. Detailed Methodology
* **Discussion Protocol:**
  1. *Initial Generation:* Each agent independently produces an answer with confidence scoring.
  2. *Discussion Rounds:* Agents review peer arguments and attempt to convince peers using deductive logic.
  3. *Consensus Verification:* Concludes when unanimous agreement or confidence-weighted majority is reached.
* **Benchmarks:** Mathematical reasoning (GSM8K, MATH), StrategyQA, CommonsenseQA.
* **Metrics:** Accuracy improvement over initial round, Convincingness score, Heterogeneous synergy gain.

### 4. Key Novelty & Theoretical Contributions
* **Heterogeneous Model Synergy:** Demonstrates that multi-agent consensus achieves significantly higher performance gains when agents use *different* base model architectures rather than identical model instances.
* **Confidence-Weighted Resolution:** Prevents strong models from being swayed by confident hallucinations of weaker models through explicit confidence calibration.

### 5. Critical Limitations & Caveats
* Inter-agent discussion rounds quickly escalate context window usage, increasing KV-cache VRAM consumption.
* Heterogeneous setups require loading multiple distinct model weights into VRAM simultaneously, exacerbating memory pressure on single GPUs.

### 6. Why We SHOULD Include It as a Source
* **ACL 2024 Main Conference.** Solidifies our review of consensus-based multi-agent reasoning, highlighting the role of model diversity in multi-agent gains.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our experimental design enforces a *single* model family (e.g., strictly Qwen 2.5/3 across all sizes) to eliminate architectural confounds, ReConcile's heterogeneous focus is less relevant.
