"""
Full 35-Paper Literature Review Summary Builder
Outputs individual markdown summaries to d:\project-agere\literature_review\summaries\
and generates a master index at d:\project-agere\literature_review\summaries\README.md
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARIES_DIR = os.path.join(BASE_DIR, "summaries")
os.makedirs(SUMMARIES_DIR, exist_ok=True)

PAPERS = [
    # 01
    {
        "num": "01",
        "slug": "01_tran_2026_single_agent_llms_outperform_multi_agent",
        "title": "Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets",
        "authors": "Dat Tran, Douwe Kiela",
        "venue": "arXiv:2604.02460 (Stanford University)",
        "year": "2026",
        "pdf_rel": "../../sources/01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf",
        "role": "Primary Base Paper Candidate (Thinking Token Normalization Template)",
        "exec_summary": (
            "This paper provides a rigorous empirical and information-theoretic challenge to the prevailing belief that Multi-Agent Systems "
            "(MAS) naturally surpass Single-Agent Systems (SAS) on complex reasoning. By strictly controlling the computational thinking token "
            "budget—measuring combined internal reasoning and dialogue tokens—the authors demonstrate across Qwen3, DeepSeek-R1-Distill, and "
            "Gemini 2.5 that a single agent consistently matches or outperforms multi-agent debate, ensemble, and sequential setups on multi-hop QA."
        ),
        "motivation": (
            "Prior literature celebrated massive gains from multi-agent collaboration (e.g., Mixture-of-Agents, AgentVerse), but these studies "
            "conflated multi-agent architectural synergy with increased test-time compute. When an MAS generates thousands of intermediate communication "
            "tokens, it spends more inference compute than a zero-shot or short-chain single agent. The authors ask: Does multi-agent interaction provide "
            "inherent algorithmic synergy, or is it merely an expensive way to spend more test-time tokens?"
        ),
        "methodology": (
            "The study investigates three dominant MAS topologies alongside SAS:\n"
            "1. **Single-Agent System (SAS):** Standard autoregressive generation using extended Chain-of-Thought (CoT) reasoning budgets.\n"
            "2. **Sequential MAS:** Linear pipeline where Agent A generates intermediate rationales that are passed to Agent B.\n"
            "3. **Debate MAS:** Multi-round iterative peer review where multiple agent personas critique peer answers and revise conclusions.\n"
            "4. **Ensemble MAS:** Parallel independent generations aggregated via majority consensus.\n\n"
            "**The Equal Budget Control Mechanism:**\n"
            "Total test-time thinking budget $T$ is fixed. For SAS, $T$ tokens are allocated to the single model's reasoning trace. "
            "For MAS with $N$ agents over $R$ rounds, the per-agent generation is capped such that $\\sum_{i=1}^N \\sum_{r=1}^R t_{i,r} = T$. "
            "Experiments are run across model families (Qwen3, DeepSeek-R1-Distill-Llama, Gemini 2.5) on multi-hop reasoning benchmarks."
        ),
        "experiments": (
            "- **Benchmarks:** FRAMES (Factuality, Retrieval, and Multi-hop Evaluation), MuSiQue, and HotpotQA.\n"
            "- **Controlled Parameter:** Thinking token budget $T \\in [512, 1024, 2048, 4096, 8192]$.\n"
            "- **Ablations:** Context truncation thresholds, API budget enforcement quirks (revealing Gemini 2.5 token artifacts), and prompt formatting variance."
        ),
        "results": (
            "- Under equal thinking token budgets, SAS matches or outperforms MAS on over 82% of multi-hop evaluation splits.\n"
            "- Multi-agent debate exhibits severe diminishing returns: as debate rounds increase, error cascading and consensus drift cause accuracy degradation.\n"
            "- Information-theoretic proof: via the Data Processing Inequality ($I(X; Z) \\le I(X; Y)$), every inter-agent conversational handoff without external tool injection is lossy, progressively eroding context fidelity."
        ),
        "limitations": (
            "- Exclusively restricted to closed-book and retrieved-context multi-hop QA; does not examine tool execution (e.g., code sandboxes, web browsing).\n"
            "- Holds base model parameter size constant across agents; does not evaluate whether heterogeneous model teams or quantized scale shifts the outcome.\n"
            "- Treats compute (tokens) as the only resource axis, ignoring physical GPU resident VRAM constraints."
        ),
        "our_research_connection": (
            "Tran & Kiela is our **direct structural foundation**. We adopt their SAS vs. MAS comparative topology (sequential, debate, ensemble) "
            "and evaluation methodology, but swap their controlled resource from **thinking token budget** to **physical GPU VRAM memory ($M$)**. "
            "Where they tested equal tokens with identical model sizes, we test equal VRAM where the single agent spends freed memory on larger model "
            "scale via quantization (e.g., 1× 32B @ 4-bit vs. 2× 8B @ INT8 or 1× 8B + 2× 3B @ FP16)."
        ),
        "citation_utility": (
            "Cite in Section 1 (Introduction) and Section 2 (Related Work) as the definitive baseline establishing that compute-matched MAS does not "
            "beat SAS, framing our paper as extending this inquiry to the physical hardware memory boundary."
        )
    },

    # 02
    {
        "num": "02",
        "slug": "02_zywot_2026_can_small_agent_collaboration_beat_single_big_llm",
        "title": "Can Small Agent Collaboration Beat a Single Big LLM?",
        "authors": "Agata Zywot, Xinyi Chen, Maarten de Rijke",
        "venue": "arXiv:2601.11327 (University of Amsterdam, Preprint Under Review)",
        "year": "2026",
        "pdf_rel": "../../sources/02_Zywot_2026_Can_Small_Agent_Collaboration_Beat_Single_Big_LLM.pdf",
        "role": "Primary Base Paper Candidate (Tool-Use & Small vs. Large Agent Architecture)",
        "exec_summary": (
            "This paper evaluates whether collaborative multi-agent teams of smaller language models (4B–32B parameters) can surpass a single, "
            "substantially larger model on complex, real-world tasks requiring external tool use. Benchmarking on GAIA, the authors find that "
            "small agents equipped with external tools (web search, Python code interpreter, mind-mapping) and orchestrated hierarchically "
            "routinely outperform monolithic models that are up to 8× larger but lack tool augmentation."
        ),
        "motivation": (
            "Deploying frontier monolithic models (32B–70B+) incurs prohibitive hardware costs, high inference latency, and severe environmental footprints. "
            "The authors explore whether task decomposition across specialized small models can democratize agentic AI, challenging the 'bigger is always better' "
            "dogma in practical deployment settings."
        ),
        "methodology": (
            "The authors build an orchestrator-subagent architecture using the Qwen3 family (4B, 8B, 14B, 32B):\n"
            "1. **Central Orchestrator:** Decomposes complex user goals, assigns tasks, schedules tool invocations, and synthesizes intermediate outputs.\n"
            "2. **Specialized Worker Agents:** Equipped with dedicated toolkits—Searcher (web browsing), Coder (code sandbox), and Reasoner (logical planning).\n"
            "3. **Monolithic Baselines:** Standalone single models operating at larger parameter scales.\n\n"
            "The architecture tests asymmetrical scaling: varying the orchestrator size independently of worker sizes to measure where parameter capacity is most critical."
        ),
        "experiments": (
            "- **Benchmark:** GAIA (General AI Assistants benchmark, Levels 1, 2, and 3).\n"
            "- **Model Family:** Qwen3 models across 4B, 8B, 14B, and 32B scales.\n"
            "- **Ablation Studies:** Tool access on vs. off, orchestration topology (flat peer vs. hierarchical central), and sub-agent parameter variations."
        ),
        "results": (
            "- A 4B agent team with tools outperforms a standalone 32B monolithic model without tools on GAIA Levels 1 and 2.\n"
            "- Tool access is the dominant equalizing factor: small models with code execution and search bridge the reasoning gap against models 8× their size.\n"
            "- Orchestrator capacity matters significantly more than worker capacity: upgrading the orchestrator from 4B to 14B produces a dramatic jump in success rate, whereas scaling workers yields marginal gains."
        ),
        "limitations": (
            "- Does not control for concurrent resident VRAM: the multi-agent systems instantiate multiple distinct models without bounding total GPU memory.\n"
            "- Does not test post-training quantization on the single large model baseline (e.g., comparing 4B MAS against 32B 4-bit in identical memory).\n"
            "- GAIA evaluation relies heavily on external API reliability, introducing non-deterministic execution noise."
        ),
        "our_research_connection": (
            "Provides our **alternative base architecture** for the tool-augmented arm. It proves that MAS superiority depends heavily on tool integration. "
            "Our research directly fills their missing gap by holding total resident VRAM constant and comparing their small-agent team against a quantized large model."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 4 to justify our hierarchical orchestrator-worker topology and to support our hypothesis that task type (tool-use vs. pure reasoning) acts as a moderator."
        )
    },

    # 03
    {
        "num": "03",
        "slug": "03_kim_2025_towards_a_science_of_scaling_agent_systems",
        "title": "Towards a Science of Scaling Agent Systems",
        "authors": "Kim et al.",
        "venue": "arXiv:2512.08296 (Google Research, Google DeepMind, MIT)",
        "year": "2025",
        "pdf_rel": "../../sources/03_Kim_2025_Towards_a_Science_of_Scaling_Agent_Systems.pdf",
        "role": "Theoretical Scaling Laws & Agent Topology Selection Framework",
        "exec_summary": (
            "A collaborative study between Google Research, DeepMind, and MIT that formalizes quantitative scaling laws for multi-agent LLM systems. "
            "Moving beyond empirical trial-and-error, the authors systematically evaluate how agent system performance scales as a function of agent count, "
            "coordination topology, model capability, and intrinsic task dependency structures."
        ),
        "motivation": (
            "While neural network scaling laws (Kaplan et al., Chinchilla) govern pre-training compute, no principled scaling theory existed for agent systems. "
            "Practitioners blindly added agents assuming monotonic improvements. The authors set out to determine mathematically and empirically when multi-agent "
            "collaboration benefits vs. degrades performance."
        ),
        "methodology": (
            "Systematic evaluation across 4 topological paradigms:\n"
            "1. **Independent (Parallel):** Agents solve subtasks without mutual interaction; aggregated by voting or concatenation.\n"
            "2. **Centralized (Hierarchical):** One leader agent routes, delegates, and synthesizes.\n"
            "3. **Decentralized (Peer-to-Peer):** Fully connected graph of communicating agents.\n"
            "4. **Hybrid:** Multi-tiered clusters with regional coordinators.\n\n"
            "**Task Characterization Formalism:**\n"
            "Tasks are mathematically categorized by their dependency graph: degree of parallelizability ($P$) versus degree of sequential dependency ($S$)."
        ),
        "experiments": (
            "- Thousands of controlled evaluation runs spanning diverse model families and scales.\n"
            "- Agent team sizes varied from $N = 1$ to $N = 16$.\n"
            "- Predictive modeling: trained cross-validated regressors to predict system performance ($R^2 = 0.373 - 0.413$) based on task topology features."
        ),
        "results": (
            "- Adding agents to parallelizable tasks yields near-linear performance gains up to a saturation ceiling.\n"
            "- Adding agents to tasks with high sequential dependencies produces **negative scaling**: performance degrades as $N$ increases due to compounded communication noise and goal drift.\n"
            "- Architectures lacking centralized verification exhibit rapid error cascading."
        ),
        "limitations": (
            "- Assumes elastic cloud API infrastructure; does not incorporate GPU memory ceilings or concurrent weight residency.\n"
            "- Does not explore model quantization or hardware deployment constraints."
        ),
        "our_research_connection": (
            "Supplies the **theoretical backbone** explaining why dividing a fixed memory budget among multiple small agents succeeds on parallelizable subtasks "
            "but collapses on tightly coupled sequential multi-hop reasoning."
        ),
        "citation_utility": (
            "Cite in Section 2 (Theoretical Foundations) and Section 5 (Discussion) to ground our empirical observations in formal agent scaling principles."
        )
    },

    # 04
    {
        "num": "04",
        "slug": "04_wang_2024_mixture_of_agents_enhances_llm",
        "title": "Mixture-of-Agents Enhances Large Language Model Capabilities",
        "authors": "Junlin Wang et al.",
        "venue": "arXiv:2406.04692 (Together AI, Duke University, Stanford University)",
        "year": "2024",
        "pdf_rel": "../../sources/04_Wang_2024_Mixture_of_Agents_Enhances_LLM.pdf",
        "role": "Layered Multi-Agent Architecture Baseline",
        "exec_summary": (
            "Introduces the Mixture-of-Agents (MoA) methodology, which organizes multiple LLMs into sequential layers where each agent synthesizes "
            "the outputs of all agents in the previous layer. MoA achieved state-of-the-art results on AlpacaEval 2.0, MT-Bench, and FLASK, showing that "
            "collaborative open-source models could surpass proprietary frontier models like GPT-4 Omni."
        ),
        "motivation": (
            "Individual LLMs possess distinct inductive biases, domain knowledge, and generation styles. Prior ensemble approaches relied on simple "
            "voting or reranking. MoA hypothesizes that LLMs are inherently 'collaborative'—capable of generating significantly better responses when "
            "presented with candidate outputs from other models, even when those other models are individually weaker."
        ),
        "methodology": (
            "The MoA architecture consists of $L$ sequential layers:\n"
            "- Layer 1: $N$ diverse LLM agents independently generate responses to prompt $x$.\n"
            "- Layer $l \\in [2, L]$: Each agent receives the original prompt $x$ concatenated with the responses of all agents from layer $l-1$, producing a refined response.\n"
            "- Final Layer: A single aggregator model synthesizes the penultimate layer outputs into the definitive answer.\n"
            "Utilizes open-source models: Qwen-1.5, Llama-3, Mixtral, and WizardLM."
        ),
        "experiments": (
            "- Benchmarks: AlpacaEval 2.0 (length-controlled win rate), MT-Bench, and FLASK.\n"
            "- MoA-Lite (few agents, 2 layers) vs. Full MoA (multiple agents, 3 layers).\n"
            "- Cost and token latency profiling across heterogeneous model mixes."
        ),
        "results": (
            "- MoA using purely open-source models achieved a win rate of 65.1% on AlpacaEval 2.0, substantially outperforming GPT-4 Omni (57.5%).\n"
            "- Discovered the 'collaborativeness phenomenon': even weak models act as useful idea catalysts for stronger models in subsequent layers."
        ),
        "limitations": (
            "- Massive inference latency: sequential multi-layer generation multiplies end-to-end response time.\n"
            "- Enormous token consumption: passing all previous outputs creates quadratic prompt token growth ($O(N^2)$ context expansion).\n"
            "- High memory footprint: hosting diverse heterogeneous models concurrently requires multi-GPU clusters."
        ),
        "our_research_connection": (
            "MoA is the primary high-profile paper claiming that distributing compute across multiple models beats a single large model. "
            "Our research tests whether MoA's collaborative advantage survives when forced to fit within a single GPU's resident memory budget."
        ),
        "citation_utility": (
            "Cite in Section 1 and Section 2 as the leading representative of the 'MAS-wins' literature that Tran & Kiela (and our paper) critically re-evaluate."
        )
    },

    # 05
    {
        "num": "05",
        "slug": "05_wang_2024_rethinking_bounds_llm_reasoning_multiagent_discussions",
        "title": "Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key?",
        "authors": "Qineng Wang, Zihao Wang, Ying Su, Hanghang Tong, Yangqiu Song",
        "venue": "ACL 2024 (62nd Annual Meeting of the ACL, Long Papers)",
        "year": "2024",
        "pdf_rel": "../../sources/05_Wang_2024_Rethinking_Bounds_LLM_Reasoning_MultiAgent_Discussions.pdf",
        "role": "Single-Agent vs. Multi-Agent Debate Baseline & Prompting Rigor",
        "exec_summary": (
            "A peer-reviewed ACL 2024 paper that critically evaluates multi-agent discussion and debate frameworks across a battery of reasoning tasks. "
            "The authors find that when single-agent systems are provided with standard prompt engineering (such as Chain-of-Thought and few-shot demonstrations), "
            "they match the performance of multi-agent discussions, with multi-agent debate only helping in unprompted, zero-shot scenarios."
        ),
        "motivation": (
            "Multiple 2023 papers claimed multi-agent debate revolutionized reasoning. The authors questioned whether these improvements were genuine "
            "or merely an artifact of comparing rich multi-turn discussion prompts against severely under-prompted, zero-shot single-agent baselines."
        ),
        "methodology": (
            "Systematic empirical comparison between:\n"
            "- Single-Agent: Zero-shot CoT, Few-shot CoT, Self-Consistency.\n"
            "- Multi-Agent Discussion: Round-robin discussion, simultaneous debate, hierarchical debate.\n"
            "Investigates the internal communicative dynamics between agents: persuasion success rate, answer flipping rate, and confidence calibration."
        ),
        "experiments": (
            "- Models: ChatGPT (GPT-3.5-Turbo), GPT-4, Llama-2-70B.\n"
            "- Benchmarks: GSM8K, MATH, StrategyQA, ARC-Challenge.\n"
            "- Analysis of conformity: measuring how frequently agents abandon correct answers to conform with an incorrect majority."
        ),
        "results": (
            "- In few-shot settings, single agents match multi-agent debate on almost all mathematical and logical tasks.\n"
            "- Multi-agent debate provides a 5–10% boost *only* in zero-shot settings where the single agent lacks guidance.\n"
            "- Identified the 'Conformity Trap': agents frequently exhibit sycophancy, agreeing with hallucinated peer claims."
        ),
        "limitations": (
            "- Does not test tool-augmented agents.\n"
            "- Evaluates closed-source proprietary APIs (GPT-4) and unquantized open models; does not explore physical memory or quantization."
        ),
        "our_research_connection": (
            "Guarantees that our single-agent baseline is properly prompted with CoT and demonstrations, preventing our experiments from falling into "
            "the 'zero-shot baseline' trap that artificially inflated early MAS papers."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 3 to justify our Single-Agent baseline prompt design using fully peer-reviewed ACL 2024 evidence."
        )
    },

    # 06
    {
        "num": "06",
        "slug": "06_li_2024_more_agents_is_all_you_need",
        "title": "More Agents Is All You Need",
        "authors": "Junyou Li, Qin Zhang, Yangbin Yu, Qiang Fu, Deheng Ye",
        "venue": "TMLR 2024 (Transactions on Machine Learning Research)",
        "year": "2024",
        "pdf_rel": "../../sources/06_Li_2024_More_Agents_Is_All_You_Need.pdf",
        "role": "Agent Ensemble Scaling Laws via Sampling-and-Voting",
        "exec_summary": (
            "Published in TMLR 2024, this paper demonstrates that simply scaling the number of instantiated LLM agents via a sampling-and-voting "
            "methodology consistently improves reasoning accuracy across diverse tasks, with the magnitude of improvement strongly correlated with task difficulty."
        ),
        "motivation": (
            "Complex multi-agent collaboration frameworks require bespoke prompt engineering, complex communication graphs, and prone-to-failure "
            "parsing logic. The authors investigate whether an extremely simple, uncoordinated ensemble scaling method (instantiating $N$ independent agents "
            "and taking a majority vote) can deliver competitive scaling behavior."
        ),
        "methodology": (
            "- Instantiates $N$ identical or heterogeneous agents with query $q$.\n"
            "- Agents independently generate reasoning paths and terminal answers.\n"
            "- A consensus module aggregates votes to determine the winner.\n"
            "- Explores hierarchical voting: using smaller models to filter and generate candidate sets, followed by higher-capacity models for final verification."
        ),
        "experiments": (
            "- Models: Llama-2-13B, Llama-2-70B, GPT-3.5-Turbo.\n"
            "- Benchmarks: GSM8K, SVAMP, HumanEval, MMLU.\n"
            "- Evaluates scaling behavior as $N$ increases from 1 to 20+."
        ),
        "results": (
            "- Performance scales monotonically with the number of agents, exhibiting power-law improvements on complex problems.\n"
            "- The benefit of adding agents is orthogonal to prompt strategy: stacking voting on top of CoT or Reflexion yields additive gains.\n"
            "- Simple tasks saturate quickly (diminishing returns at $N=3$), while hard tasks continue improving up to $N=15+$."
        ),
        "limitations": (
            "- Multiplying agent count multiplies inference compute and memory linear in $N$.\n"
            "- Lacks collaborative specialization: all agents perform identical tasks rather than decomposing problems into specialized sub-roles."
        ),
        "our_research_connection": (
            "Represents our **peer-ensemble baseline**. Under an equal memory budget (e.g., 16 GB), can 3 identical 7B models with voting beat a 32B 4-bit model? "
            "Li et al. provides the reference scaling law for this comparison."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 3 as the definitive reference for sampling-and-voting multi-agent scaling."
        )
    },

    # 07
    {
        "num": "07",
        "slug": "07_cemri_2025_why_do_multi_agent_llm_systems_fail",
        "title": "Why Do Multi-Agent LLM Systems Fail?",
        "authors": "Mert Cemri et al.",
        "venue": "arXiv:2503.13657 (March 2025)",
        "year": "2025",
        "pdf_rel": "../../sources/07_Cemri_2025_Why_Do_Multi_Agent_LLM_Systems_Fail.pdf",
        "role": "Multi-Agent System Failure Taxonomy (MAST) & Error Analysis Framework",
        "exec_summary": (
            "A comprehensive forensic analysis of failure modes in multi-agent LLM systems. The authors examine over 1,600 annotated interaction traces "
            "across 7 prominent MAS frameworks, creating the MAST (Multi-Agent System Failure Taxonomy) of 14 failure modes grouped into specification, "
            "inter-agent misalignment, and verification breakdowns."
        ),
        "motivation": (
            "Despite immense hype, multi-agent frameworks often fail unpredictably in real-world deployment or yield negligible gains over single agents. "
            "Prior literature lacked a systematic diagnostic framework explaining the root causes of multi-agent failures."
        ),
        "methodology": (
            "- Analyzes 7 frameworks: AutoGen, MetaGPT, ChatDev, CrewAI, CAMEL, and custom architectures.\n"
            "- Curates MAST-Data: 1,600+ multi-turn execution traces annotated by human experts and automated evaluators.\n"
            "- Categorizes failures into 3 primary clusters:\n"
            "  1. System Specification & Design (~41.8%)\n"
            "  2. Inter-Agent Misalignment & Communication (~36.9%)\n"
            "  3. Task Verification & Termination (~21.3%)"
        ),
        "experiments": (
            "- Traces failure propagation across multi-step execution graphs.\n"
            "- Measures correlation between team size, dialogue length, and cascading error rates."
        ),
        "results": (
            "- **Error Amplification:** Hallucinations in early sub-agents compound exponentially in downstream agents because agents lack stable internal state verification.\n"
            "- **Context Collapse:** Passing long conversational histories causes instruction dilution, leading downstream agents to lose track of original user constraints.\n"
            "- Over 36% of failures originate from communication breakdowns (withholding info, misinterpreting intent, endless loops)."
        ),
        "limitations": (
            "- Purely diagnostic and observational; does not propose a new coordination architecture or runtime fix."
        ),
        "our_research_connection": (
            "Provides the **exact diagnostic vocabulary** for our Error Analysis and Discussion sections. When our small MAS arm underperforms "
            "the large quantized SAS model on multi-hop tasks, MAST allows us to classify whether failure stemmed from context collapse, cascading hallucination, "
            "or verification failure."
        ),
        "citation_utility": (
            "Cite extensively in Section 5 (Discussion and Error Analysis) to explain why small multi-agent models suffer from coordination overhead."
        )
    },

    # 08
    {
        "num": "08",
        "slug": "08_ke_2026_mas_orchestra_holistic_multi_agent_orchestration",
        "title": "MAS-Orchestra: Benchmarking Holistic Multi-Agent Orchestration",
        "authors": "Ke et al.",
        "venue": "arXiv:2601.14652 (January 2026)",
        "year": "2026",
        "pdf_rel": "../../sources/08_Ke_2026_MAS_Orchestra_Holistic_Multi_Agent_Orchestration.pdf",
        "role": "Multi-Agent Orchestration Benchmark & Efficiency Metrics",
        "exec_summary": (
            "A modern 2026 benchmarking platform dedicated to evaluating the holistic orchestration performance of multi-agent LLM systems, "
            "measuring dynamic task allocation, message routing compactness, and resilience under communication bottlenecks."
        ),
        "motivation": (
            "Most agent benchmarks evaluate either individual model capabilities or end-to-end task completion, without isolating whether failures "
            "are caused by poor orchestration (bad routing, redundant chatting) or weak sub-agent reasoning. MAS-Orchestra isolates the orchestration layer."
        ),
        "methodology": (
            "- Evaluates orchestration topologies: Hierarchical, Blackboard, Dynamic Router.\n"
            "- Introduces the Communication-to-Computation Ratio (CCR) to quantify conversational efficiency.\n"
            "- Tests resilience by injecting synthetic sub-agent failure and message corruption."
        ),
        "experiments": (
            "- Benchmarked across diverse task workflows requiring 3 to 10 interacting sub-agents.\n"
            "- Analyzes message redundancy and token overhead across orchestration styles."
        ),
        "results": (
            "- Ineffective orchestration accounts for over 45% of failed multi-agent workflows, independent of the underlying model's reasoning power.\n"
            "- Centralized hierarchical orchestrators with compact structured messaging achieve the highest task completion with minimal CCR."
        ),
        "limitations": (
            "- Focuses on orchestration message flow without evaluating GPU hardware resident memory limits."
        ),
        "our_research_connection": (
            "Informs how we measure communication overhead and message compactness in our MAS topologies, ensuring our small-agent orchestrators "
            "do not waste precious context tokens on redundant chatter."
        ),
        "citation_utility": (
            "Cite in Section 3 (Experimental Design) to justify our orchestration efficiency metrics."
        )
    },

    # 09
    {
        "num": "09",
        "slug": "09_chen_2024_agentverse_multi_agent_collaboration",
        "title": "AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors",
        "authors": "Weize Chen, Yusheng Su, Jingwei Zuo, et al.",
        "venue": "ICLR 2024",
        "year": "2024",
        "pdf_rel": "../../sources/09_Chen_2024_AgentVerse_Multi_Agent_Collaboration.pdf",
        "role": "Multi-Agent Collaboration Framework & Dynamic Group Scaffolding",
        "exec_summary": (
            "Published at ICLR 2024, AgentVerse introduces a flexible multi-agent framework that enables LLM agents to dynamically assemble, "
            "plan, execute, and evaluate collaborative task pipelines. It demonstrates that dynamic multi-agent teams solve complex problems "
            "more effectively than rigid, static agent pipelines."
        ),
        "motivation": (
            "Most multi-agent systems rely on static, pre-defined agent groups that cannot adapt to changing problem difficulties or unexpected subtask failures. "
            "AgentVerse was developed to provide autonomous group composition and collaborative evaluation."
        ),
        "methodology": (
            "Structured in four autonomous stages:\n"
            "1. **Expert Recruitment:** Analyzes task goals and dynamically instantiates agent personas.\n"
            "2. **Collaborative Decision-Making:** Facilitates structured group discussions to formulate action plans.\n"
            "3. **Action Execution:** Agents act within task environments or tool sandboxes.\n"
            "4. **Evaluation:** An evaluator agent inspects intermediate states, triggering replanning if errors occur."
        ),
        "experiments": (
            "- Benchmarks: Text evaluation, math reasoning, Minecraft embodied agent tasks, and software consulting.\n"
            "- Evaluates static vs. dynamic agent group recruitment across varying model scales."
        ),
        "results": (
            "- Dynamic agent teams achieve significantly higher task success rates than static single-agent or fixed multi-agent baselines.\n"
            "- Demonstrates emergent social behaviors, including spontaneous specialization and peer verification."
        ),
        "limitations": (
            "- High token consumption due to iterative multi-agent planning and evaluation phases.\n"
            "- Lacks memory management for local GPU VRAM residency."
        ),
        "our_research_connection": (
            "Provides the modular architectural scaffolding (recruitment, planning, execution, evaluation) used to structure our small-agent MAS configurations."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 3 as the ICLR 2024 foundational framework for multi-agent group formation."
        )
    },

    # 10
    {
        "num": "10",
        "slug": "10_chan_2024_chateval_multi_agent_debate",
        "title": "ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate",
        "authors": "Chi-Min Chan, Weize Chen, Yusheng Su, et al.",
        "venue": "ICLR 2024",
        "year": "2024",
        "pdf_rel": "../../sources/10_Chan_2024_ChatEval_Multi_Agent_Debate.pdf",
        "role": "Multi-Agent Peer Debate Protocol & Bias Mitigation",
        "exec_summary": (
            "ChatEval introduces a multi-agent debate framework where diverse referee agents critique each other's assessments to achieve objective, "
            "human-aligned evaluations, effectively eliminating the position and verbosity biases inherent in single LLM evaluators."
        ),
        "motivation": (
            "Using a single LLM as an evaluator ('LLM-as-a-judge') suffers from egocentric bias, verbosity bias, and prompt sensitivity. "
            "ChatEval hypothesizes that structured debate among specialized personas can triangulate objective ground truth."
        ),
        "methodology": (
            "- Defines distinct critic personas (e.g., factual precision, fluency, completeness).\n"
            "- Multi-turn debate rounds where agents present scores, justify critiques, and challenge peers.\n"
            "- Consensus aggregation mechanism calculating final calibrated ratings."
        ),
        "experiments": (
            "- Benchmarks: Text summarization (CNN/DailyMail), Dialogue generation, Translation.\n"
            "- Evaluates correlation against human expert rankings (Spearman $\\rho$, Pearson $r$)."
        ),
        "results": (
            "- Multi-agent debate achieves significantly higher correlation with human judgment than single-model evaluators.\n"
            "- Committees of smaller, cheaper models debating each other frequently match or exceed a single frontier model judge."
        ),
        "limitations": (
            "- Multiplies token costs linearly with agent count and debate rounds.\n"
            "- Risk of groupthink cascades when multiple models share common pre-training biases."
        ),
        "our_research_connection": (
            "Supplies the specific prompt structure and critique-revision loops used in our Peer Debate MAS arm."
        ),
        "citation_utility": (
            "Cite in Section 3 to justify our multi-agent peer debate protocol."
        )
    },

    # 11
    {
        "num": "11",
        "slug": "11_hong_2024_metagpt_multi_agent_collaborative_framework",
        "title": "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework",
        "authors": "Sirui Hong, Mingchen Zhuge, Jonathan Chen, et al.",
        "venue": "ICLR 2024 (Oral Presentation)",
        "year": "2024",
        "pdf_rel": "../../sources/11_Hong_2024_MetaGPT_Multi_Agent_Collaborative_Framework.pdf",
        "role": "SOP-Based Hierarchical Architecture Baseline",
        "exec_summary": (
            "Accepted as an Oral presentation at ICLR 2024, MetaGPT incorporates human Standardized Operating Procedures (SOPs) into multi-agent "
            "systems. By replacing unstructured natural language dialogue with structured engineering documents (PRDs, architecture designs, API specifications), "
            "MetaGPT prevents cascading hallucinations and coordinates specialized agents in complex multi-file software creation."
        ),
        "motivation": (
            "Natural language multi-agent conversations quickly degenerate into hallucination cascades, repetitive loops, and context drift. "
            "Human software organizations avoid this by enforcing rigorous SOPs and structured documentation schemas."
        ),
        "methodology": (
            "- Models human roles: Product Manager, Architect, Project Manager, Engineer, QA Engineer.\n"
            "- Replaces conversational chat with structured artifacts (Markdown tables, JSON schemas, UML diagrams).\n"
            "- Publish-subscribe message bus ensuring agents only receive documents relevant to their role."
        ),
        "experiments": (
            "- Benchmarks: HumanEval, MBPP, and end-to-end multi-file software synthesis.\n"
            "- Evaluates task completion rate, code executability, and documentation quality."
        ),
        "results": (
            "- Achieves state-of-the-art code generation pass rates, generating executable multi-file software projects.\n"
            "- SOP constraints reduce cascading logic errors by over 60% compared to unconstrained multi-agent dialogue."
        ),
        "limitations": (
            "- High token verbosity due to comprehensive documentation generation at each step.\n"
            "- Specifically optimized for software engineering rather than generalized reasoning."
        ),
        "our_research_connection": (
            "Serves as our primary **Hierarchical Orchestrator-Worker baseline**, demonstrating that small sub-agents need rigid role constraints to succeed."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 3 as the gold-standard peer-reviewed (ICLR Oral) hierarchical MAS framework."
        )
    },

    # 12
    {
        "num": "12",
        "slug": "12_qian_2024_chatdev_communicative_agents_software_development",
        "title": "ChatDev: Communicative Agents for Software Development",
        "authors": "Chen Qian, Wei Liu, Hongzhang Liu, et al.",
        "venue": "ACL 2024 (Long Papers)",
        "year": "2024",
        "pdf_rel": "../../sources/12_Qian_2024_ChatDev_Communicative_Agents_Software_Development.pdf",
        "role": "Sequential Pipeline MAS Architecture Baseline",
        "exec_summary": (
            "Published in ACL 2024, ChatDev models a virtual software company that operates through a sequential chat chain. "
            "By decomposing the development lifecycle into Designing, Coding, Testing, and Documenting, pairs of specialized agents interact "
            "via multi-turn dialogue to complete granular tasks for under $1 in API costs."
        ),
        "motivation": (
            "Monolithic LLMs struggle to maintain long-range coherence when asked to generate complex, multi-component programs from a single prompt. "
            "ChatDev tests whether sequential communicative decomposition across paired agents solves this limitation."
        ),
        "methodology": (
            "- Sequential multi-stage pipeline: Designing $\\to$ Coding $\\to$ Testing $\\to$ Documenting.\n"
            "- 'Chat Chain' mechanism: Each phase contains paired communicative agents (e.g., CEO $\\leftrightarrow$ CPO, Programmer $\\leftrightarrow$ Reviewer).\n"
            "- Incorporates self-reflection and peer-review loops at each stage."
        ),
        "experiments": (
            "- Evaluated across 70 custom software development scenarios.\n"
            "- Measures software completeness, code executability, vulnerability rates, and manufacturing costs."
        ),
        "results": (
            "- Successfully generates complete software applications in under 7 minutes for less than $1.00.\n"
            "- Peer testing and review loops catch and fix over 70% of potential syntax and runtime bugs before final output."
        ),
        "limitations": (
            "- High wall-clock latency caused by sequential round-trip dialogues.\n"
            "- Prone to context accumulation overhead across consecutive pipeline nodes."
        ),
        "our_research_connection": (
            "Represents our **Sequential Pipeline MAS baseline** (Decompose $\\to$ Execute $\\to$ Verify), showing how sequential stages reduce single-agent context load."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 3 to establish peer-reviewed ACL 2024 precedence for sequential agent pipelines."
        )
    },

    # 13
    {
        "num": "13",
        "slug": "13_liu_2024_dynamic_llm_agent_network_dylan",
        "title": "Dynamic LLM-Agent Network: An LLM-Agent Collaboration Framework with Dynamic Architecture (DyLAN)",
        "authors": "Liu et al.",
        "venue": "ICLR 2024",
        "year": "2024",
        "pdf_rel": "../../sources/13_Liu_2024_Dynamic_LLM_Agent_Network_DyLAN.pdf",
        "role": "Dynamic Agent Pruning & Communication Token Efficiency",
        "exec_summary": (
            "DyLAN introduces a dynamic multi-agent framework that measures agent contributions at each execution round and prunes inactive "
            "or redundant agents. It demonstrates that dynamic agent pruning reduces token consumption while improving overall task accuracy."
        ),
        "motivation": (
            "Static multi-agent systems suffer from token explosion and distracting chatter because all agents participate in all rounds regardless of utility. "
            "DyLAN addresses this by dynamically adjusting the collaboration network at runtime."
        ),
        "methodology": (
            "- Formulates an Agent Importance Score based on contribution to state advancement.\n"
            "- Dynamically prunes lowest-ranked agents after each discussion round.\n"
            "- Features an early stopping algorithm when agent consensus converges."
        ),
        "experiments": (
            "- Benchmarks: Arithmetic reasoning (GSM8K, SVAMP), Code generation (HumanEval), Multi-hop QA (HotpotQA).\n"
            "- Measures accuracy versus token consumption Pareto efficiency."
        ),
        "results": (
            "- Pruning ineffective agents cuts token overhead by 30–50% while improving reasoning accuracy by eliminating noisy distractions.\n"
            "- Outperforms static multi-agent debate frameworks across all tested benchmarks."
        ),
        "limitations": (
            "- Calculating agent importance requires additional evaluation passes.\n"
            "- Assumes cloud API execution rather than local GPU memory scheduling."
        ),
        "our_research_connection": (
            "Guides our strategies for trimming inter-agent communication overhead so our small-agent MAS configurations do not waste GPU memory on uninformative tokens."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 5 to discuss how communication pruning mitigates multi-agent coordination costs."
        )
    },

    # 14
    {
        "num": "14",
        "slug": "14_chen_2024_reconcile_round_table_discussion",
        "title": "ReConcile: Round-Table Discussion Improves Reasoning via Consensus",
        "authors": "Chen et al.",
        "venue": "ACL 2024 (Main Conference)",
        "year": "2024",
        "pdf_rel": "../../sources/14_Chen_2024_ReConcile_Round_Table_Discussion.pdf",
        "role": "Heterogeneous Model Consensus & Round-Table Discussion",
        "exec_summary": (
            "Accepted at ACL 2024, ReConcile introduces a round-table discussion protocol where heterogeneous LLM agents present reasoning paths, "
            "debate counterarguments, and adjust confidence levels to converge on an accurate consensus on complex reasoning problems."
        ),
        "motivation": (
            "Single models often suffer from stubborn blind spots. ReConcile explores whether convening a 'round-table' of diverse models with different "
            "pre-training lineages can eliminate individual errors through calibrated consensus."
        ),
        "methodology": (
            "- Multi-turn round-table protocol with confidence estimation.\n"
            "- Agents attempt to convince peers using deductive arguments.\n"
            "- Consensus mechanism: terminates when confidence-weighted unanimous agreement or stable majority is reached."
        ),
        "experiments": (
            "- Benchmarks: Mathematical reasoning (GSM8K, MATH), StrategyQA, CommonsenseQA.\n"
            "- Compares homogeneous agent teams (same model) vs. heterogeneous agent teams (different model families)."
        ),
        "results": (
            "- Heterogeneous agent teams significantly outperform homogeneous teams, proving that model diversity is the key driver of consensus gains.\n"
            "- Confidence-weighted voting prevents dominant but hallucinating models from misleading weaker peers."
        ),
        "limitations": (
            "- Simultaneous deployment of multiple diverse model weights multiplies GPU VRAM residency requirements.\n"
            "- Multi-round debates lead to quadratic context window expansion."
        ),
        "our_research_connection": (
            "Provides a strong consensus baseline for reasoning tasks, highlighting why heterogeneous model deployment is difficult under single-GPU VRAM constraints."
        ),
        "citation_utility": (
            "Cite in Section 2 as a peer-reviewed ACL 2024 benchmark for multi-model consensus."
        )
    },

    # 15
    {
        "num": "15",
        "slug": "15_wang_2024_reasoning_in_token_economies_budget_aware",
        "title": "Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies",
        "authors": "Junlin Wang, Siddhartha Jain, Dejiao Zhang, Baishakhi Ray, Varun Kumar, Ben Athiwaratkun",
        "venue": "EMNLP 2024 (Main Conference)",
        "year": "2024",
        "pdf_rel": "../../sources/15_Wang_2024_Reasoning_in_Token_Economies_Budget_Aware.pdf",
        "role": "Methodological Template for Budget-Normalized Evaluation",
        "exec_summary": (
            "A landmark EMNLP 2024 paper proving that many complex reasoning and agent strategies (multi-agent debate, Reflexion, Tree-of-Thoughts) "
            "do not outperform simpler baselines due to algorithmic superiority, but simply because they consume far more inference tokens. "
            "It establishes the paradigm of budget-aware evaluation."
        ),
        "motivation": (
            "Traditional NLP evaluations measure accuracy while ignoring inference compute. Complex agent architectures spend 5× to 20× more tokens "
            "per query and claim superiority over simple single-turn prompts. The authors argue that this comparison is methodologically broken."
        ),
        "methodology": (
            "- Normalizes all evaluation against fixed token budgets ($T \\in [512, 8192]$).\n"
            "- Evaluates Zero-shot, Few-shot CoT, Self-Consistency, Multi-Agent Debate, Reflexion, Tree-of-Thoughts.\n"
            "- Measures accuracy as a function of total tokens spent per query."
        ),
        "experiments": (
            "- Models: Llama-2-70B, GPT-3.5-Turbo, Claude-2.\n"
            "- Benchmarks: GSM8K, SVAMP, StrategyQA, ARC-Challenge."
        ),
        "results": (
            "- When a single agent with self-consistency (repeated sampling) is given the same token budget as multi-agent debate, the single agent wins decisively.\n"
            "- Complex strategies exhibit negative scaling beyond a certain token threshold, degrading performance."
        ),
        "limitations": (
            "- Normalizes tokens only; does not consider physical GPU memory, VRAM residency, or model parameter scale."
        ),
        "our_research_connection": (
            "Our **primary methodological inspiration**. We adopt Wang et al.'s exact principle—*'fair evaluation requires budget normalization'*—and "
            "apply it to physical GPU VRAM memory ($M$) instead of token count."
        ),
        "citation_utility": (
            "Cite in Section 1 and Section 3 as the definitive academic precedent for budget-normalized evaluation."
        )
    },

    # 16
    {
        "num": "16",
        "slug": "16_lin_2025_bench360_benchmarking_local_llm_inference",
        "title": "Bench360: Benchmarking Local LLM Inference from 360 Degrees",
        "authors": "Lin et al.",
        "venue": "arXiv:2511.16682 (Late 2025 / 2026)",
        "year": "2025",
        "pdf_rel": "../../sources/16_Lin_2025_Bench360_Benchmarking_Local_LLM_Inference.pdf",
        "role": "Hardware & VRAM Memory Profiling Protocol",
        "exec_summary": (
            "Bench360 provides a unified benchmarking platform that measures local LLM inference across hardware memory footprint (VRAM in GB), "
            "latency, throughput, energy consumption, and downstream task quality across multiple inference engines and quantization formats."
        ),
        "motivation": (
            "Local inference research is fragmented: quantization papers report perplexity, systems papers report throughput, and NLP papers report accuracy. "
            "Bench360 bridges this divide with a standardized 360-degree profiling suite."
        ),
        "methodology": (
            "- Profiles hardware metrics: Peak resident VRAM (GB), memory bandwidth, energy (Joules/query).\n"
            "- Evaluates runtimes: vLLM, SGLang, TGI, LMDeploy, llama.cpp.\n"
            "- Tests precision levels: FP16, INT8, INT4 (AWQ, GPTQ), 2-bit/3-bit across consumer and workstation GPUs."
        ),
        "experiments": (
            "- Workloads: Single-stream desktop, multi-turn chat, high-throughput batching.\n"
            "- Evaluates functional accuracy across summarization, QA, and code."
        ),
        "results": (
            "- Proves that no single model configuration is optimal across all hardware constraints.\n"
            "- Shows that 4-bit quantization drastically reduces VRAM but introduces dequantization compute latency on memory-bandwidth-unconstrained GPUs."
        ),
        "limitations": (
            "- Focuses on single-model serving rather than multi-agent collaborative workflows."
        ),
        "our_research_connection": (
            "Provides our **exact VRAM measurement and hardware profiling protocol**, establishing how we enforce and report our 8 GB, 16 GB, and 24 GB hardware tiers."
        ),
        "citation_utility": (
            "Cite in Section 3 (Experimental Setup) to validate our hardware memory accounting methodology."
        )
    },

    # 17
    {
        "num": "17",
        "slug": "17_brown_2024_large_language_monkeys_scaling_inference_compute",
        "title": "Large Language Monkeys: Scaling Inference Compute with Repeated Sampling",
        "authors": "Bradley Brown, Jordan Juravsky, Anthony Ryan, et al.",
        "venue": "arXiv:2407.21787 (July 2024)",
        "year": "2024",
        "pdf_rel": "../../sources/17_Brown_2024_Large_Language_Monkeys_Scaling_Inference_Compute.pdf",
        "role": "Inference-Time Compute Scaling Baseline",
        "exec_summary": (
            "Demonstrates that scaling coverage via repeated independent sampling ($k = 1$ to $10,000$) on small-to-medium models enables them "
            "to match or surpass models 10× to 100× larger on complex coding and reasoning benchmarks."
        ),
        "motivation": (
            "Investigates whether test-time inference compute can substitute for parameter scale: can a smaller model with extensive sampling "
            "outperform a monolithic frontier model?"
        ),
        "methodology": (
            "- Generates thousands of samples per query using varying temperatures.\n"
            "- Evaluates Pass@$k$ coverage and majority voting.\n"
            "- Analyzes compute-scaling curves across Llama-3-8B and Llama-3-70B."
        ),
        "experiments": (
            "- Benchmarks: SWE-bench Lite, HumanEval, GSM8K, MATH.\n"
            "- Compares Pass@$k$ scaling against pre-training compute scaling."
        ),
        "results": (
            "- Repeated sampling exhibits consistent power-law scaling on tasks with verifiable test cases.\n"
            "- An 8B model with sufficient sampling coverage solves problems that standard 70B models fail on."
        ),
        "limitations": (
            "- Requires automated verifiers or unit tests to select correct solutions at high $k$.\n"
            "- Extremely high cumulative token cost."
        ),
        "our_research_connection": (
            "Serves as a strong compute-matched baseline for our Single-Agent arm, testing whether repeated sampling on a quantized model beats multi-agent coordination."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 3 when defending our single-agent test-time compute baselines."
        )
    },

    # 18
    {
        "num": "18",
        "slug": "18_su_2024_toolorchestra_cost_aware_tool_orchestration",
        "title": "ToolOrchestra: Collaborative and Cost-Aware Tool Orchestration for Language Agents",
        "authors": "Su et al.",
        "venue": "arXiv:2411.08573 (November 2024)",
        "year": "2024",
        "pdf_rel": "../../sources/18_Su_2024_ToolOrchestra_Cost_Aware_Tool_Orchestration.pdf",
        "role": "Cost-Constrained Multi-Agent Tool Orchestration",
        "exec_summary": (
            "ToolOrchestra proposes an orchestration framework that dynamically schedules and routes tool calls under explicit constraints "
            "on monetary cost and latency budgets, proving that budget constraints eliminate redundant tool calls and improve accuracy."
        ),
        "motivation": (
            "Language agents invoking external tools often issue redundant, expensive API calls. ToolOrchestra models tool calling under strict resource economics."
        ),
        "methodology": (
            "- Cost-aware routing module estimating expected information gain against API invocation cost.\n"
            "- Dynamically selects between cheap internal heuristics and expensive external tool calls.\n"
            "- Benchmarked on ToolBench, API-Bank, and GAIA."
        ),
        "experiments": (
            "- Measures accuracy under varying per-query cost budgets.\n"
            "- Evaluates tool selection precision and latency reduction."
        ),
        "results": (
            "- Enforcing explicit budgets reduces API costs by up to 60% with zero loss in task success rate.\n"
            "- Prevents agents from entering infinite tool-calling loops."
        ),
        "limitations": (
            "- Focuses on monetary API costs rather than physical GPU VRAM."
        ),
        "our_research_connection": (
            "Highlights how multi-agent tool execution must be budgeted, reinforcing our resource-constrained research paradigm."
        ),
        "citation_utility": (
            "Cite in Section 2 as precedent for resource-constrained agent tool orchestration."
        )
    },

    # 19
    {
        "num": "19",
        "slug": "19_chen_2026_the_qs_inequality_moe_inference_penalty",
        "title": "The qs Inequality: Quantifying the Double Penalty of Mixture-of-Experts at Inference",
        "authors": "Chen et al.",
        "venue": "arXiv:2603.08960 (March 2026)",
        "year": "2026",
        "pdf_rel": "../../sources/19_Chen_2026_The_qs_Inequality_MoE_Inference_Penalty.pdf",
        "role": "Mathematical Theory: Capacity vs. Memory Parity Penalty",
        "exec_summary": (
            "A formal theoretical paper deriving the $q_s$ inequality, proving mathematically that sparse Mixture-of-Experts (MoE) architectures "
            "incur a double penalty at inference: when total resident memory is held equal, dense monolithic networks decisively outperform sparse networks."
        ),
        "motivation": (
            "While MoEs achieve superior performance when matching *active* parameters (compute FLOPs), practitioners noticed that dense models win "
            "when matching *total stored parameters* (VRAM). The authors set out to prove this mathematical quality-equivalence boundary."
        ),
        "methodology": (
            "- Derives the quality-equivalence multiplier $q_s$ bounding parameter efficiency.\n"
            "- Compares MoE vs. Dense under matched FLOPs vs. matched resident memory.\n"
            "- Validates theoretical bounds empirically across open transformer checkpoints."
        ),
        "experiments": (
            "- Comprehensive scaling experiments holding total parameter memory constant."
        ),
        "results": (
            "- Proves that distributing parameters across routed sub-networks incurs an inherent representation penalty under total memory parity.\n"
            "- The total parameter parity inversion: dense models consistently surpass MoEs when resident hardware memory is the binding constraint."
        ),
        "limitations": (
            "- Evaluates internal layer routing inside single models rather than multi-agent macro-orchestration."
        ),
        "our_research_connection": (
            "Provides our **core theoretical analogy**: just as the $q_s$ inequality proved that distributing capacity into sub-networks loses under total memory parity, "
            "we test whether distributing capacity into whole orchestrated agents loses to a monolithic model under equal VRAM."
        ),
        "citation_utility": (
            "Cite in Section 1 (Introduction) and Section 2 (Theory) as the formal mathematical foundation for our hypothesis."
        )
    },

    # 20
    {
        "num": "20",
        "slug": "20_kwon_2023_vllm_pagedattention_memory_management",
        "title": "Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM)",
        "authors": "Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, et al.",
        "venue": "SOSP 2023 / MLSys",
        "year": "2023",
        "pdf_rel": "../../sources/20_Kwon_2023_vLLM_PagedAttention_Memory_Management.pdf",
        "role": "Serving Infrastructure & KV-Cache Management",
        "exec_summary": (
            "The foundational systems paper that introduced PagedAttention and vLLM, eliminating KV-cache memory fragmentation and enabling near-zero "
            "memory waste during concurrent LLM inference through virtual memory paging."
        ),
        "motivation": (
            "Existing LLM serving systems wasted 60–80% of GPU memory due to internal and external KV-cache fragmentation. In memory-constrained settings, "
            "this caused premature Out-Of-Memory (OOM) crashes long before physical VRAM was actually filled."
        ),
        "methodology": (
            "- PagedAttention divides contiguous KV-caches into fixed-size physical memory blocks.\n"
            "- Dynamic non-contiguous allocation similar to OS virtual memory paging.\n"
            "- Supports copy-on-write page sharing for parallel sampling and beam search."
        ),
        "experiments": (
            "- Evaluates throughput and memory efficiency across diverse model scales and batch workloads."
        ),
        "results": (
            "- Reduces KV-cache memory waste to under 4%.\n"
            "- Increases serving throughput by 2× to 4× with zero accuracy degradation."
        ),
        "limitations": (
            "- Pure systems paper; does not explore multi-agent prompting or agent reasoning algorithms."
        ),
        "our_research_connection": (
            "The **core serving engine** of our experimental pipeline, ensuring multi-agent models and single-agent models run with near-zero KV memory waste."
        ),
        "citation_utility": (
            "Mandatory citation in Section 3 (Implementation Details) to validate our memory accounting."
        )
    },

    # 21
    {
        "num": "21",
        "slug": "21_yao_2024_frugal_moe_cost_effective_moe_routing",
        "title": "Frugal-MoE: Cost-Effective Mixture of Experts via Activation-Guided Routing",
        "authors": "Yao et al.",
        "venue": "ACL 2024 (Findings)",
        "year": "2024",
        "pdf_rel": "../../sources/21_Yao_2024_Frugal_MoE_Cost_Effective_MoE_Routing.pdf",
        "role": "Adaptive Subnetwork Activation Baseline",
        "exec_summary": (
            "Frugal-MoE introduces activation-guided dynamic routing to selectively skip expert loading and activation for simpler tokens, "
            "reducing runtime memory bandwidth and compute demands during inference."
        ),
        "motivation": (
            "Uniform expert activation wastes significant memory bandwidth on simple, predictable tokens."
        ),
        "methodology": (
            "- Predicts token difficulty and routes easy tokens to a minimal expert subset.\n"
            "- Dynamic capacity budgeting preserving accuracy on complex tokens."
        ),
        "experiments": (
            "- Benchmarks: MMLU, GSM8K, CommonsenseQA."
        ),
        "results": (
            "- Preserves 98%+ of accuracy while slashing inference compute by up to 40%."
        ),
        "limitations": (
            "- Restricted to MoE architectures; does not apply directly to dense multi-agent teams."
        ),
        "our_research_connection": (
            "Serves as an adaptive memory-saving contrast point against static multi-agent allocation."
        ),
        "citation_utility": (
            "Cite in Section 2 when discussing dynamic capacity allocation."
        )
    },

    # 22
    {
        "num": "22",
        "slug": "22_lin_2024_awq_activation_aware_weight_quantization",
        "title": "AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration",
        "authors": "Ji Lin, Jiaming Tang, Haotian Tang, Song Han, et al.",
        "venue": "MLSys 2024 (Best Paper Award)",
        "year": "2024",
        "pdf_rel": "../../sources/22_Lin_2024_AWQ_Activation_Aware_Weight_Quantization.pdf",
        "role": "Primary 4-Bit Quantization Backbone for SAS Arm",
        "exec_summary": (
            "Winner of the MLSys 2024 Best Paper Award, AWQ establishes that protecting the top ~1% of salient weights (identified via activation magnitude "
            "rather than weight magnitude) enables accurate, hardware-friendly 4-bit integer quantization without backpropagation or calibration overfitting."
        ),
        "motivation": (
            "Prior quantization methods (GPTQ) required complex reconstruction optimization and overfit to calibration data. Round-to-nearest (RTN) destroyed "
            "reasoning. AWQ provides an equivalent transformation that makes INT4 weight quantization virtually lossless."
        ),
        "methodology": (
            "- Discovers that salient weights protect model accuracy; salience is determined by observing average activation magnitude.\n"
            "- Applies an equivalent per-channel scaling factor transformation $W' = W \\cdot S, X' = S^{-1} \\cdot X$ to protect salient channels.\n"
            "- Hardware-accelerated INT4 GEMM kernel integrated into vLLM and TensorRT-LLM."
        ),
        "experiments": (
            "- Evaluated across LLaMA, Mistral, and Qwen families from 7B to 70B.\n"
            "- Benchmarks: WikiText perplexity, CommonSenseQA, MMLU, GSM8K."
        ),
        "results": (
            "- Retains near-FP16 perplexity across all model sizes.\n"
            "- Delivers >3× token throughput speedup on edge GPUs while slashing memory footprint by 75%."
        ),
        "limitations": (
            "- Weight-only quantization; activations and KV-cache remain in 16-bit."
        ),
        "our_research_connection": (
            "Our **primary quantization method** for the Single-Agent arm, used to compress 14B, 32B, and 70B models into target VRAM budgets."
        ),
        "citation_utility": (
            "Mandatory citation in Section 3 to validate our 4-bit single-agent baseline."
        )
    },

    # 23
    {
        "num": "23",
        "slug": "23_ashkboos_2024_quarot_outlier_free_4bit_inference",
        "title": "QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs",
        "authors": "Saleh Ashkboos et al.",
        "venue": "NeurIPS 2024",
        "year": "2024",
        "pdf_rel": "../../sources/23_Ashkboos_2024_QuaRot_Outlier_Free_4Bit_Inference.pdf",
        "role": "End-to-End 4-Bit Weights + Activations + KV-Cache Compression",
        "exec_summary": (
            "Published at NeurIPS 2024, QuaRot introduces randomized Hadamard rotations to eliminate activation outliers, enabling end-to-end 4-bit inference "
            "across weights, activations, and KV-cache simultaneously with 99% accuracy retention."
        ),
        "motivation": (
            "Weight-only quantization leaves the KV-cache and activations in 16-bit, which causes severe memory bottlenecks at long sequence lengths. "
            "Quantizing activations failed previously due to extreme outlier values. QuaRot eliminates outliers mathematically."
        ),
        "methodology": (
            "- Applies orthogonal randomized Hadamard matrices $H$ to weights and activations exploiting computational invariance: $(XH)(H^T W) = XW$.\n"
            "- Rotations spread outlier energy uniformly across all channels, eliminating extreme spikes.\n"
            "- Enables 4-bit integer GEMM matrix multiplication without dequantization."
        ),
        "experiments": (
            "- Models: LLaMA-2 (7B, 13B, 70B), LLaMA-3.\n"
            "- Full W4A4KV4 evaluation across perplexity and zero-shot reasoning."
        ),
        "results": (
            "- LLaMA-2-70B retains 99% of original zero-shot accuracy under full 4-bit inference.\n"
            "- Slashes total runtime memory footprint (including KV cache) by nearly 4×."
        ),
        "limitations": (
            "- Online rotation operations add slight arithmetic latency."
        ),
        "our_research_connection": (
            "Allows our single-agent arm to compress both weights and KV cache to 4-bit, testing whether end-to-end compression maximizes single-agent dominance."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 3 as the leading NeurIPS 2024 baseline for end-to-end 4-bit inference."
        )
    },

    # 24
    {
        "num": "24",
        "slug": "24_liu_2025_spinquant_llm_quantization_learned_rotations",
        "title": "SpinQuant: LLM Quantization with Learned Rotations",
        "authors": "Zechun Liu et al.",
        "venue": "ICLR 2025",
        "year": "2025",
        "pdf_rel": "../../sources/24_Liu_2025_SpinQuant_LLM_Quantization_Learned_Rotations.pdf",
        "role": "State-of-the-Art Learned Rotation Quantization Baseline",
        "exec_summary": (
            "Accepted at ICLR 2025, SpinQuant optimizes rotation matrices via Cayley optimization on the Stiefel manifold to suppress outliers, "
            "outperforming QuaRot and narrowing the accuracy gap between 4-bit quantized models and full-precision FP16 baselines."
        ),
        "motivation": (
            "Random Hadamard rotations (QuaRot) reduce outliers but do not exploit the specific weight geometry of a given model checkpoint. "
            "SpinQuant learns the optimal rotation angles directly."
        ),
        "methodology": (
            "- Optimizes rotation matrices constrained to the orthogonal group $O(n)$ using Cayley transforms.\n"
            "- End-to-end W4A4KV4 coverage.\n"
            "- Outperforms SmoothQuant and QuaRot on challenging reasoning tasks."
        ),
        "experiments": (
            "- Benchmarks: MMLU, GSM8K, HumanEval, WikiText perplexity."
        ),
        "results": (
            "- Recovers 1.5–3.0% higher accuracy than QuaRot on complex reasoning.\n"
            "- Closes over 95% of the perplexity gap with full-precision FP16."
        ),
        "limitations": (
            "- Requires an offline optimization phase (several GPU hours) before deployment."
        ),
        "our_research_connection": (
            "Provides an uncompromised, cutting-edge quantized single-agent baseline to guarantee that our SAS model is not handicapped by quantization artifacts."
        ),
        "citation_utility": (
            "Cite in Section 3 to establish that our study uses latest ICLR 2025 quantization standards."
        )
    },

    # 25
    {
        "num": "25",
        "slug": "25_egiazarian_2024_aqlm_extreme_compression_additive_quantization",
        "title": "AQLM: Extreme Compression of Large Language Models via Additive Quantization",
        "authors": "Vage Egiazarian et al.",
        "venue": "ICML 2024",
        "year": "2024",
        "pdf_rel": "../../sources/25_Egiazarian_2024_AQLM_Extreme_Compression_Additive_Quantization.pdf",
        "role": "Extreme 2-Bit / 3-Bit Quantization Baseline",
        "exec_summary": (
            "Published at ICML 2024, AQLM is the first Pareto-optimal quantization scheme for extreme compression regimes below 3 bits per parameter, "
            "generalizing Additive Quantization to LLMs via joint codebook optimization across transformer blocks."
        ),
        "motivation": (
            "Standard quantization schemes collapse into incoherent gibberish below 3 bits. AQLM breaks this barrier to fit massive models into consumer GPUs."
        ),
        "methodology": (
            "- Multi-codebook vector quantization representing weight vectors as the sum of learned codewords ($W \\approx \\sum C_m[i_m]$).\n"
            "- Block-wise joint fine-tuning via beam search codebook assignment.\n"
            "- Targets 2-bit, 2.5-bit, and 3-bit regimes."
        ),
        "experiments": (
            "- Models: LLaMA-2 (7B to 70B), Mistral-7B.\n"
            "- Perplexity and zero-shot accuracy evaluation."
        ),
        "results": (
            "- First scheme where 2-bit and 3-bit models retain non-trivial reasoning capability.\n"
            "- Compresses 70B models into under 16 GB of memory with viable perplexity."
        ),
        "limitations": (
            "- Slower decoding latency due to vector codebook lookups."
        ),
        "our_research_connection": (
            "Enables our **Extreme Scale experiment**: testing whether a massive 70B model compressed to 2-bit/3-bit beats an MAS of small models in a 16 GB budget."
        ),
        "citation_utility": (
            "Cite in Section 2 and Section 4 when exploring extreme parameter scaling boundaries."
        )
    },

    # 26
    {
        "num": "26",
        "slug": "26_cheng_2024_autoround_advanced_weight_only_quantization",
        "title": "Optimize Weight-Only Quantization of Large Language Models with an Advanced Rounding Technique (AutoRound)",
        "authors": "Weiwei Cheng et al.",
        "venue": "EMNLP 2024",
        "year": "2024",
        "pdf_rel": "../../sources/26_Cheng_2024_AutoRound_Advanced_Weight_Only_Quantization.pdf",
        "role": "Advanced INT4 Rounding for Large Models",
        "exec_summary": (
            "Published at EMNLP 2024, AutoRound optimizes weight rounding via sign gradient descent over a lightweight calibration set, "
            "consistently outperforming standard RTN and GPTQ on 4-bit and 2-bit models."
        ),
        "motivation": (
            "Standard round-to-nearest rounding causes substantial quantization error, while second-order methods like GPTQ can overfit. "
            "AutoRound provides fast, robust optimization."
        ),
        "methodology": (
            "- Optimizes rounding values by minimizing layer-wise output reconstruction error using sign gradient descent.\n"
            "- Completes calibration in minutes without hyperparameter tuning."
        ),
        "experiments": (
            "- Evaluated across W4A16 and W2A16 settings on broad model families."
        ),
        "results": (
            "- Outperforms GPTQ across 4-bit and 2-bit models with minimal compute overhead."
        ),
        "limitations": (
            "- Weight-only; does not quantize KV-cache."
        ),
        "our_research_connection": (
            "Provides an accessible, high-accuracy alternative quantization baseline for our single-agent models."
        ),
        "citation_utility": (
            "Cite in Section 3 as a high-performing alternative to AWQ."
        )
    },

    # 27
    {
        "num": "27",
        "slug": "27_liu_2024_mobilellm_sub_billion_parameter_llms",
        "title": "MobileLLM: Optimizing Sub-billion Parameter Language Models for On-Device Use Cases",
        "authors": "Zechun Liu et al. (Meta AI)",
        "venue": "ICML 2024",
        "year": "2024",
        "pdf_rel": "../../sources/27_Liu_2024_MobileLLM_Sub_Billion_Parameter_LLMs.pdf",
        "role": "Sub-Billion Model Architecture Principles for Edge Sub-Agents",
        "exec_summary": (
            "Published at ICML 2024 by Meta, MobileLLM proves that for sub-billion models (125M–1B), model architecture is far more critical than data scaling, "
            "introducing deep-thin topologies, embedding sharing, and block weight-sharing to maximize capability on edge devices."
        ),
        "motivation": (
            "Deploying LLMs on mobile and edge hardware requires models under 1B parameters. Prior small models simply shrunk width and depth uniformly, "
            "causing severe reasoning collapse."
        ),
        "methodology": (
            "- Deep-and-thin architecture optimizing memory bandwidth.\n"
            "- Input/output embedding sharing and Grouped-Query Attention (GQA).\n"
            "- Immediate block weight-sharing to increase effective depth with zero memory increase."
        ),
        "experiments": (
            "- Evaluated on commonsense reasoning, chat, and API-calling benchmarks."
        ),
        "results": (
            "- 125M and 350M models achieve 2.7% to 4.3% accuracy gains over prior state-of-the-art models of identical parameter scale."
        ),
        "limitations": (
            "- Requires pre-training from scratch."
        ),
        "our_research_connection": (
            "Informs how to select and configure small sub-agents (e.g., 1B models) in our tightest memory tier (8 GB VRAM)."
        ),
        "citation_utility": (
            "Cite in Section 3 to justify sub-agent architectural selection in edge regimes."
        )
    },

    # 28
    {
        "num": "28",
        "slug": "28_ma_2024_the_era_of_1bit_llms_bitnet_b158",
        "title": "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits (BitNet b1.58)",
        "authors": "Shuming Ma et al. (Microsoft Research)",
        "venue": "arXiv:2402.17764 (February 2024)",
        "year": "2024",
        "pdf_rel": "../../sources/28_Ma_2024_The_Era_of_1Bit_LLMs_BitNet_b158.pdf",
        "role": "Theoretical Boundary: Extreme 1.58-Bit Ternary Quantization",
        "exec_summary": (
            "Introduces BitNet b1.58, where every transformer weight is constrained to ternary values {-1, 0, 1}, matching full-precision 16-bit LLM "
            "performance while eliminating matrix multiplication in favor of integer addition."
        ),
        "motivation": (
            "Floating-point matrix multiplication is the dominant bottleneck in LLM memory and energy consumption. BitNet b1.58 redefines neural computing "
            "with ternary weights."
        ),
        "methodology": (
            "- Absmean quantization scaling weights to {-1, 0, 1} and activations to 8-bit integers.\n"
            "- Replaces FP16 matrix multiplications with pure integer addition kernels."
        ),
        "experiments": (
            "- Evaluated from 700M to 3B parameters across perplexity and commonsense QA."
        ),
        "results": (
            "- Matches FP16 performance starting at 3B parameters while saving up to 3.55× memory and 71× matrix multiplication energy."
        ),
        "limitations": (
            "- Requires full pre-training from scratch; cannot be applied as PTQ."
        ),
        "our_research_connection": (
            "Establishes the theoretical lower bound of single-model parameter storage cost."
        ),
        "citation_utility": (
            "Cite in Section 1 and Section 2 as the ultimate horizon of single-model compression."
        )
    },

    # 29
    {
        "num": "29",
        "slug": "29_tseng_2024_quip_hadamard_incoherence_lattice_codebooks",
        "title": "QuIP#: Even Better LLM Quantization with Hadamard Incoherence and Lattice Codebooks",
        "authors": "Albert Tseng, Jerry Chee, Qinghao Hu, et al.",
        "venue": "ICML 2024",
        "year": "2024",
        "pdf_rel": "../../sources/29_Tseng_2024_QuIP_Hadamard_Incoherence_Lattice_Codebooks.pdf",
        "role": "Theoretical Error Bounds in Post-Training Quantization",
        "exec_summary": (
            "Published at ICML 2024, QuIP# combines randomized Hadamard incoherence transformations with E8 lattice codebooks to achieve "
            "provably optimal post-training quantization at 2-bit, 3-bit, and 4-bit precision."
        ),
        "motivation": (
            "Establishes theoretical limits on quantization distortion and proves how incoherence suppresses outlier errors."
        ),
        "methodology": (
            "- Incoherence processing via orthogonal matrices.\n"
            "- Fast vector quantization using the Gosset lattice E8.\n"
            "- Derives mathematical bounds on reconstruction distortion."
        ),
        "experiments": (
            "- Comprehensive perplexity and zero-shot reasoning benchmarks across LLaMA models."
        ),
        "results": (
            "- Achieves state-of-the-art 2-bit and 3-bit accuracy among post-training quantization techniques."
        ),
        "limitations": (
            "- Complex decoding kernels requiring specialized hardware implementations."
        ),
        "our_research_connection": (
            "Provides theoretical bounds on quantization distortion versus model parameter scale."
        ),
        "citation_utility": (
            "Cite in Section 2 to ground our quantization error discussion in formal theory."
        )
    },

    # 30
    {
        "num": "30",
        "slug": "30_sheng_2024_sglang_efficient_execution_structured_lm",
        "title": "SGLang: Efficient Execution of Structured Language Model Programs",
        "authors": "Lianmin Sheng, Cody Hao Yu, Lianmin Zheng, et al.",
        "venue": "NeurIPS 2024",
        "year": "2024",
        "pdf_rel": "../../sources/30_Sheng_2024_SGLang_Efficient_Execution_Structured_LM.pdf",
        "role": "Multi-Agent KV-Cache Sharing & High-Throughput Runtime",
        "exec_summary": (
            "Accepted at NeurIPS 2024, SGLang introduces RadixAttention, which manages KV-caches as reusable radix trees, enabling automatic prefix "
            "caching and KV-cache sharing across multi-turn agent interactions and multi-agent workflows."
        ),
        "motivation": (
            "Multi-agent workflows pass identical prompt prefixes, system instructions, and history across multiple calls, causing massive redundant "
            "KV-cache memory consumption and recomputation."
        ),
        "methodology": (
            "- RadixAttention: treats KV-cache as dynamic search tree, matching and reusing cached prefix blocks automatically.\n"
            "- Structured decoding compiler optimizing branching agent execution."
        ),
        "experiments": (
            "- Evaluated across multi-turn chat, agent tool execution, and Tree-of-Thoughts reasoning."
        ),
        "results": (
            "- Delivers up to 5× throughput improvement over standard runtimes by eliminating redundant KV recomputations."
        ),
        "limitations": (
            "- Focused on runtime systems execution rather than reasoning algorithms."
        ),
        "our_research_connection": (
            "Directly reduces the memory footprint of our multi-agent system by sharing prompt KV-cache across cooperating sub-agents."
        ),
        "citation_utility": (
            "Cite in Section 3 (Systems Implementation) to validate how multi-agent KV memory was managed."
        )
    },

    # 31
    {
        "num": "31",
        "slug": "31_mialon_2024_gaia_benchmark_for_general_ai_assistants",
        "title": "GAIA: A Benchmark for General AI Assistants",
        "authors": "Gregoire Mialon et al. (Meta AI, Hugging Face, AutoGPT)",
        "venue": "ICLR 2024",
        "year": "2024",
        "pdf_rel": "../../sources/31_Mialon_2024_GAIA_Benchmark_for_General_AI_Assistants.pdf",
        "role": "Primary Tool-Use & Multi-Step Agent Benchmark",
        "exec_summary": (
            "Introduced at ICLR 2024, GAIA is the gold-standard benchmark for general AI assistants, comprising 466 real-world questions requiring "
            "multimodal handling, multi-step planning, web navigation, and tool execution—tasks simple for humans (92%) but difficult for AI (15%)."
        ),
        "motivation": (
            "Existing benchmarks saturated on esoteric trivia and standardized tests while failing to measure real-world operational assistant capabilities."
        ),
        "methodology": (
            "- 466 questions across Levels 1, 2, and 3 based on step complexity.\n"
            "- Objective string/numeric ground truth verification.\n"
            "- Requires multimodal parsing, web search, and Python code execution."
        ),
        "experiments": (
            "- Evaluated across GPT-4 with plugins, AutoGPT, and open-source models."
        ),
        "results": (
            "- Revealed massive gap between human baseline (92%) and GPT-4 with plugins (15%).\n"
            "- Resistant to statistical guessing and dataset memorization."
        ),
        "limitations": (
            "- Small test set (466 items); relies on external web environment stability."
        ),
        "our_research_connection": (
            "Our **primary tool-use benchmark** to test whether multi-agent tool specialization outperforms a single large quantized model."
        ),
        "citation_utility": (
            "Mandatory benchmark citation in Section 3 and Section 4."
        )
    },

    # 32
    {
        "num": "32",
        "slug": "32_jimenez_2024_swe_bench_real_world_github_issues",
        "title": "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
        "authors": "Carlos E. Jimenez, John Yang, Alexander Wettig, et al.",
        "venue": "ICLR 2024 (Oral Presentation)",
        "year": "2024",
        "pdf_rel": "../../sources/32_Jimenez_2024_SWE_bench_Real_World_GitHub_Issues.pdf",
        "role": "Complex Multi-Step Real-World Engineering Benchmark",
        "exec_summary": (
            "An ICLR 2024 Oral paper introducing SWE-bench, evaluating LLMs on resolving 2,294 real-world GitHub issues from 12 popular Python repositories "
            "requiring codebase navigation, bug localization, patch editing, and unit test execution."
        ),
        "motivation": (
            "Synthetic coding benchmarks (HumanEval) failed to capture the complexity of real-world software engineering across large codebases."
        ),
        "methodology": (
            "- Dockerized unit test evaluation harness.\n"
            "- Patch considered valid if and only if it passes both existing regression tests and newly added bug test cases."
        ),
        "experiments": (
            "- Evaluated across proprietary and open-source models."
        ),
        "results": (
            "- Initial models solved under 5% of real-world issues, establishing it as the definitive benchmark for agentic coding."
        ),
        "limitations": (
            "- Compute-heavy to evaluate; requires Docker container execution."
        ),
        "our_research_connection": (
            "Serves as our complex multi-step execution benchmark testing whether agent division of labor beats monolithic models on massive contexts."
        ),
        "citation_utility": (
            "Cite in Section 3 as the gold-standard benchmark for software engineering agents."
        )
    },

    # 33
    {
        "num": "33",
        "slug": "33_krishna_2024_frames_factuality_retrieval_multihop",
        "title": "FRAMES: Factuality, Retrieval, And Multi-hop Evaluation with Structured Knowledge",
        "authors": "Satyapriya Krishna et al. (Google)",
        "venue": "arXiv:2409.05591 / EMNLP 2024",
        "year": "2024",
        "pdf_rel": "../../sources/33_Krishna_2024_FRAMES_Factuality_Retrieval_Multihop.pdf",
        "role": "Primary Multi-Hop Reasoning Benchmark",
        "exec_summary": (
            "Introduces FRAMES, a benchmark designed to evaluate multi-hop retrieval and reasoning requiring models to synthesize information "
            "across 2 to 15 distinct sources and structured knowledge representations."
        ),
        "motivation": (
            "Prior multi-hop benchmarks rarely required more than 2 hops, allowing single models to succeed via statistical shortcuts. FRAMES tests high-hop reasoning."
        ),
        "methodology": (
            "- Questions requiring up to 15 reasoning hops across multiple articles.\n"
            "- Exact match and factual constraint verification."
        ),
        "experiments": (
            "- Evaluated across state-of-the-art models and retrieval-augmented systems."
        ),
        "results": (
            "- Exposes severe context degradation in multi-agent dialogue handoffs as hop count increases."
        ),
        "limitations": (
            "- Focused on retrieval and reasoning; does not evaluate tool execution."
        ),
        "our_research_connection": (
            "Our **primary multi-hop benchmark**, directly replicating and extending the evaluation suite used in Tran & Kiela (2026)."
        ),
        "citation_utility": (
            "Mandatory benchmark citation in Section 3 and Section 4."
        )
    },

    # 34
    {
        "num": "34",
        "slug": "34_patil_2024_berkeley_function_calling_leaderboard_gorilla",
        "title": "The Berkeley Function-Calling Leaderboard (BFCL)",
        "authors": "Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez",
        "venue": "arXiv:2403.01374 / ICML 2024 (Gorilla Team)",
        "year": "2024",
        "pdf_rel": "../../sources/34_Patil_2024_Berkeley_Function_Calling_Leaderboard_Gorilla.pdf",
        "role": "Standardized Tool/Function-Calling Evaluation",
        "exec_summary": (
            "A comprehensive benchmarking platform from UC Berkeley measuring function-calling accuracy across simple, multiple, parallel, "
            "and multi-turn function calls in diverse programming languages."
        ),
        "motivation": (
            "Evaluates whether models can accurately generate structured API calls with valid AST parameters."
        ),
        "methodology": (
            "- AST parsing and live API execution verification.\n"
            "- Separates function selection accuracy from argument generation accuracy."
        ),
        "experiments": (
            "- Evaluates models from 1B to 70B+ parameters."
        ),
        "results": (
            "- Small models often select the correct function but struggle with nested JSON parameter syntax."
        ),
        "limitations": (
            "- Evaluates single-turn function calling rather than long-horizon autonomous planning."
        ),
        "our_research_connection": (
            "Validates the tool-calling precision of small sub-agents compared to large quantized models."
        ),
        "citation_utility": (
            "Cite in Section 3 to validate tool-calling metrics."
        )
    },

    # 35
    {
        "num": "35",
        "slug": "35_wang_2024_mmlu_pro_robust_challenging_benchmark",
        "title": "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark",
        "authors": "Yubo Wang et al.",
        "venue": "NeurIPS 2024 (Datasets Track)",
        "year": "2024",
        "pdf_rel": "../../sources/35_Wang_2024_MMLU_Pro_Robust_Challenging_Benchmark.pdf",
        "role": "Parametric World Knowledge Benchmark",
        "exec_summary": (
            "Published at NeurIPS 2024, MMLU-Pro redesigns MMLU by expanding to 10 choices, integrating harder multi-step reasoning, "
            "and filtering out lucky guesses to accurately measure true parametric world knowledge."
        ),
        "motivation": (
            "Standard MMLU had become saturated due to prompt sensitivity and 4-choice random guessing."
        ),
        "methodology": (
            "- 12,000+ complex questions across 14 academic domains.\n"
            "- 10 answer choices per question.\n"
            "- Emphasizes multi-step reasoning over simple trivia recall."
        ),
        "experiments": (
            "- Evaluated across all leading frontier and open-source models."
        ),
        "results": (
            "- Lowers scores across all models by 15–30%, restoring clear separation between model capability tiers."
        ),
        "limitations": (
            "- Multiple-choice format; does not assess interactive agent workflows."
        ),
        "our_research_connection": (
            "Our **parametric world knowledge benchmark**, testing whether a single large model (even at 4-bit) retains superior world knowledge over small models."
        ),
        "citation_utility": (
            "Mandatory benchmark citation in Section 3 and Section 4."
        )
    }
]

def render_summary(p):
    md = f"""# {p['num']}. {p['title']}

> **Authors:** {p['authors']}  
> **Affiliation & Venue:** {p['venue']}  
> **Publication Year:** {p['year']}  
> **Local PDF Source:** [`{os.path.basename(p['pdf_rel'])}`]({p['pdf_rel']})  
> **Role in Our Study:** **{p['role']}**

---

## 1. Executive Summary & Core Premise
{p['exec_summary']}

---

## 2. Research Motivation & Problem Formulation
{p['motivation']}

---

## 3. Technical Architecture & Methodology
{p['methodology']}

---

## 4. Experimental Framework & Setup
{p['experiments']}

---

## 5. Key Quantitative Findings & Breakthroughs
{p['results']}

---

## 6. Critical Limitations, Caveats & Failure Modes
{p['limitations']}

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

{p['our_research_connection']}

---

## 8. Citation Utility & Key Takeaways
{p['citation_utility']}
"""
    return md

def main():
    print(f"Generating individual summaries for {len(PAPERS)} papers in {SUMMARIES_DIR}...")
    index_entries = []

    for p in PAPERS:
        filename = f"{p['slug']}.md"
        filepath = os.path.join(SUMMARIES_DIR, filename)
        content = render_summary(p)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        index_entries.append((p['num'], p['title'], filename, p['role'], p['venue']))
        print(f"  [+] Generated {filename}")

    # Generate README.md index in summaries/
    readme_path = os.path.join(SUMMARIES_DIR, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# Research Paper Detailed Summaries Index\n\n")
        f.write("This directory contains **self-contained, comprehensive study summaries for all 35 research papers** (2024–2026). Each summary covers problem formulation, technical methodology, experimental setup, key quantitative results, limitations, and direct strategic connection to our research question.\n\n")
        f.write("| # | Summary File | Title | Venue | Primary Role in Our Paper |\n")
        f.write("|---|---|---|---|---|\n")
        for num, title, fname, role, venue in index_entries:
            f.write(f"| {num} | [**`{fname}`**](./{fname}) | {title} | {venue} | {role} |\n")

    print(f"\n[+] Master summaries README generated at {readme_path}")
    print(f"=== Successfully built all {len(PAPERS)} paper summaries! ===")

if __name__ == "__main__":
    main()
