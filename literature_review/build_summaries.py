"""
Comprehensive Literature Review Summaries Generator
Generates dedicated, in-depth Markdown summaries for all 35 research papers in literature_review/summaries/
"""

import os

SUMMARIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "literature_review", "summaries")
os.makedirs(SUMMARIES_DIR, exist_ok=True)

PAPERS_DATA = [
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
    }
]

# We will append the remaining papers (09-35) in subsequent blocks or build functions.
print(f"Loaded core definition for {len(PAPERS_DATA)} initial papers.")
