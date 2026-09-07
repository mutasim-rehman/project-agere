"""
Batch PDF Downloader for Research Papers
Target Folder: d:\project-agere\sources
"""

import os
import sys
import time
import urllib.request
import urllib.error

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PAPERS = [
    # --- Pillar 1: Multi-Agent Systems vs. Single-Agent Systems ---
    {
        "id": "01",
        "filename": "01_Tran_2026_Single_Agent_LLMs_Outperform_Multi_Agent.pdf",
        "url": "https://arxiv.org/pdf/2604.02460.pdf",
        "title": "Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets",
        "authors": "Dat Tran, Douwe Kiela",
        "year": "2026",
        "venue": "arXiv:2604.02460 (Stanford University)",
        "role": "Primary Base Paper Candidate (Thinking Token Budget template)"
    },
    {
        "id": "02",
        "filename": "02_Zywot_2026_Can_Small_Agent_Collaboration_Beat_Single_Big_LLM.pdf",
        "url": "https://arxiv.org/pdf/2601.11327.pdf",
        "title": "Can Small Agent Collaboration Beat a Single Big LLM?",
        "authors": "Agata Zywot, Xinyi Chen, Maarten de Rijke",
        "year": "2026",
        "venue": "arXiv:2601.11327 (Univ. of Amsterdam)",
        "role": "Primary Base Paper Candidate (Tool-Use & Small vs Large Agent template)"
    },
    {
        "id": "03",
        "filename": "03_Kim_2025_Towards_a_Science_of_Scaling_Agent_Systems.pdf",
        "url": "https://arxiv.org/pdf/2512.08296.pdf",
        "title": "Towards a Science of Scaling Agent Systems",
        "authors": "Kim et al.",
        "year": "2025",
        "venue": "arXiv:2512.08296 (Google Research, Google DeepMind, MIT)",
        "role": "Foundational Scaling Laws & Multi-Agent Topologies"
    },
    {
        "id": "04",
        "filename": "04_Wang_2024_Mixture_of_Agents_Enhances_LLM.pdf",
        "url": "https://arxiv.org/pdf/2406.04692.pdf",
        "title": "Mixture-of-Agents Enhances Large Language Model Capabilities",
        "authors": "Junlin Wang et al.",
        "year": "2024",
        "venue": "arXiv:2406.04692 (Together AI, Duke, Stanford)",
        "role": "Layered Multi-Agent Architecture Baseline"
    },
    {
        "id": "05",
        "filename": "05_Wang_2024_Rethinking_Bounds_LLM_Reasoning_MultiAgent_Discussions.pdf",
        "url": "https://arxiv.org/pdf/2402.18272.pdf",
        "title": "Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key?",
        "authors": "Qineng Wang, Zihao Wang, Ying Su, Hanghang Tong, Yangqiu Song",
        "year": "2024",
        "venue": "ACL 2024 (Long Papers)",
        "role": "Single-Agent vs Multi-Agent Debate Baseline"
    },
    {
        "id": "06",
        "filename": "06_Li_2024_More_Agents_Is_All_You_Need.pdf",
        "url": "https://arxiv.org/pdf/2402.05120.pdf",
        "title": "More Agents Is All You Need",
        "authors": "Junyou Li, Qin Zhang, Yangbin Yu, Qiang Fu, Deheng Ye",
        "year": "2024",
        "venue": "TMLR 2024",
        "role": "Agent Ensemble Scaling Laws"
    },
    {
        "id": "07",
        "filename": "07_Cemri_2025_Why_Do_Multi_Agent_LLM_Systems_Fail.pdf",
        "url": "https://arxiv.org/pdf/2503.13657.pdf",
        "title": "Why Do Multi-Agent LLM Systems Fail?",
        "authors": "Cemri et al.",
        "year": "2025",
        "venue": "arXiv:2503.13657",
        "role": "MAST Multi-Agent Failure Mode Taxonomy"
    },
    {
        "id": "08",
        "filename": "08_Ke_2026_MAS_Orchestra_Holistic_Multi_Agent_Orchestration.pdf",
        "url": "https://arxiv.org/pdf/2601.14652.pdf",
        "title": "MAS-Orchestra: Benchmarking Holistic Multi-Agent Orchestration",
        "authors": "Ke et al.",
        "year": "2026",
        "venue": "arXiv:2601.14652",
        "role": "Multi-Agent Orchestration Benchmark"
    },
    {
        "id": "09",
        "filename": "09_Chen_2024_AgentVerse_Multi_Agent_Collaboration.pdf",
        "url": "https://arxiv.org/pdf/2308.10848.pdf",
        "title": "AgentVerse: Facilitating Multi-Agent Collaboration and Exploring Emergent Behaviors",
        "authors": "Weize Chen et al.",
        "year": "2024",
        "venue": "ICLR 2024",
        "role": "Multi-Agent Collaboration Framework"
    },
    {
        "id": "10",
        "filename": "10_Chan_2024_ChatEval_Multi_Agent_Debate.pdf",
        "url": "https://arxiv.org/pdf/2308.07201.pdf",
        "title": "ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate",
        "authors": "Chi-Min Chan et al.",
        "year": "2024",
        "venue": "ICLR 2024",
        "role": "Multi-Agent Debate Protocol"
    },
    {
        "id": "11",
        "filename": "11_Hong_2024_MetaGPT_Multi_Agent_Collaborative_Framework.pdf",
        "url": "https://arxiv.org/pdf/2308.00352.pdf",
        "title": "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework",
        "authors": "Sirui Hong et al.",
        "year": "2024",
        "venue": "ICLR 2024 (Oral)",
        "role": "SOP-based Hierarchical Agent Architecture"
    },
    {
        "id": "12",
        "filename": "12_Qian_2024_ChatDev_Communicative_Agents_Software_Development.pdf",
        "url": "https://arxiv.org/pdf/2307.07924.pdf",
        "title": "ChatDev: Communicative Agents for Software Development",
        "authors": "Chen Qian et al.",
        "year": "2024",
        "venue": "ACL 2024 (Long Papers)",
        "role": "Role-Specialized Communicative MAS"
    },
    {
        "id": "13",
        "filename": "13_Liu_2024_Dynamic_LLM_Agent_Network_DyLAN.pdf",
        "url": "https://arxiv.org/pdf/2310.02170.pdf",
        "title": "Dynamic LLM-Agent Network: An LLM-Agent Collaboration Framework with Dynamic Architecture",
        "authors": "Liu et al.",
        "year": "2024",
        "venue": "ICLR 2024",
        "role": "Dynamic Agent Pruning & Communication Efficiency"
    },
    {
        "id": "14",
        "filename": "14_Chen_2024_ReConcile_Round_Table_Discussion.pdf",
        "url": "https://arxiv.org/pdf/2309.13007.pdf",
        "title": "ReConcile: Round-Table Discussion Improves Reasoning via Consensus",
        "authors": "Chen et al.",
        "year": "2024",
        "venue": "ACL 2024",
        "role": "Consensus & Round-Table Debate Mechanism"
    },

    # --- Pillar 2: Budget-Constrained & Resource-Aware Inference ---
    {
        "id": "15",
        "filename": "15_Wang_2024_Reasoning_in_Token_Economies_Budget_Aware.pdf",
        "url": "https://aclanthology.org/2024.emnlp-main.1112.pdf",
        "title": "Reasoning in Token Economies: Budget-Aware Evaluation of LLM Reasoning Strategies",
        "authors": "Junlin Wang, Siddhartha Jain, Dejiao Zhang, Baishakhi Ray, Varun Kumar, Ben Athiwaratkun",
        "year": "2024",
        "venue": "EMNLP 2024",
        "role": "Budget-Normalized Evaluation Template"
    },
    {
        "id": "16",
        "filename": "16_Lin_2025_Bench360_Benchmarking_Local_LLM_Inference.pdf",
        "url": "https://arxiv.org/pdf/2511.16682.pdf",
        "title": "Bench360: Benchmarking Local LLM Inference from 360 Degrees",
        "authors": "Lin et al.",
        "year": "2025",
        "venue": "arXiv:2511.16682",
        "role": "Local Hardware & VRAM Memory Profiling Protocol"
    },
    {
        "id": "17",
        "filename": "17_Brown_2024_Large_Language_Monkeys_Scaling_Inference_Compute.pdf",
        "url": "https://arxiv.org/pdf/2407.21787.pdf",
        "title": "Large Language Monkeys: Scaling Inference Compute with Repeated Sampling",
        "authors": "Bradley Brown, Jordan Juravsky, Anthony Ryan, et al.",
        "year": "2024",
        "venue": "arXiv:2407.21787",
        "role": "Inference-Time Compute Scaling Baseline"
    },
    {
        "id": "18",
        "filename": "18_Su_2024_ToolOrchestra_Cost_Aware_Tool_Orchestration.pdf",
        "url": "https://arxiv.org/pdf/2411.08573.pdf",
        "title": "ToolOrchestra: Collaborative and Cost-Aware Tool Orchestration for Language Agents",
        "authors": "Su et al.",
        "year": "2024",
        "venue": "arXiv:2411.08573",
        "role": "Cost-Constrained Multi-Agent Tool Orchestration"
    },
    {
        "id": "19",
        "filename": "19_Chen_2026_The_qs_Inequality_MoE_Inference_Penalty.pdf",
        "url": "https://arxiv.org/pdf/2603.08960.pdf",
        "title": "The qs Inequality: Quantifying the Double Penalty of Mixture-of-Experts at Inference",
        "authors": "Chen et al.",
        "year": "2026",
        "venue": "arXiv:2603.08960",
        "role": "Theoretical Memory vs. Capacity Scaling"
    },
    {
        "id": "20",
        "filename": "20_Kwon_2023_vLLM_PagedAttention_Memory_Management.pdf",
        "url": "https://arxiv.org/pdf/2309.06180.pdf",
        "title": "Efficient Memory Management for Large Language Model Serving with PagedAttention (vLLM)",
        "authors": "Woosuk Kwon et al.",
        "year": "2023",
        "venue": "SOSP 2023 / MLSys",
        "role": "Serving Infrastructure & KV Cache Memory Management"
    },
    {
        "id": "21",
        "filename": "21_Yao_2024_Frugal_MoE_Cost_Effective_MoE_Routing.pdf",
        "url": "https://arxiv.org/pdf/2407.00951.pdf",
        "title": "Frugal-MoE: Cost-Effective Mixture of Experts via Activation-Guided Routing",
        "authors": "Yao et al.",
        "year": "2024",
        "venue": "ACL 2024 (Findings)",
        "role": "Capacity-Constrained Subnetwork Routing"
    },

    # --- Pillar 3: Quantization, Memory Scaling & On-Device LLMs ---
    {
        "id": "22",
        "filename": "22_Lin_2024_AWQ_Activation_Aware_Weight_Quantization.pdf",
        "url": "https://arxiv.org/pdf/2306.00978.pdf",
        "title": "AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration",
        "authors": "Ji Lin, Jiaming Tang, Haotian Tang, Shang Yang, Xingyu Chen, Wei-Chen Wang, Song Han",
        "year": "2024",
        "venue": "MLSys 2024 (Best Paper Award)",
        "role": "Single-Agent 4-bit Quantization Backbone"
    },
    {
        "id": "23",
        "filename": "23_Ashkboos_2024_QuaRot_Outlier_Free_4Bit_Inference.pdf",
        "url": "https://arxiv.org/pdf/2404.00456.pdf",
        "title": "QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs",
        "authors": "Saleh Ashkboos et al.",
        "year": "2024",
        "venue": "NeurIPS 2024",
        "role": "End-to-End 4-Bit Weight + KV-Cache Quantization"
    },
    {
        "id": "24",
        "filename": "24_Liu_2025_SpinQuant_LLM_Quantization_Learned_Rotations.pdf",
        "url": "https://arxiv.org/pdf/2405.16406.pdf",
        "title": "SpinQuant: LLM Quantization with Learned Rotations",
        "authors": "Zechun Liu et al.",
        "year": "2025",
        "venue": "ICLR 2025",
        "role": "State-of-the-Art Rotation-Based PTQ"
    },
    {
        "id": "25",
        "filename": "25_Egiazarian_2024_AQLM_Extreme_Compression_Additive_Quantization.pdf",
        "url": "https://arxiv.org/pdf/2401.06118.pdf",
        "title": "AQLM: Extreme Compression of Large Language Models via Additive Quantization",
        "authors": "Vage Egiazarian et al.",
        "year": "2024",
        "venue": "ICML 2024",
        "role": "Extreme Sub-3-bit Quantization Baseline"
    },
    {
        "id": "26",
        "filename": "26_Cheng_2024_AutoRound_Advanced_Weight_Only_Quantization.pdf",
        "url": "https://arxiv.org/pdf/2309.05516.pdf",
        "title": "Optimize Weight-Only Quantization of Large Language Models with an Advanced Rounding Technique (AutoRound)",
        "authors": "Weiwei Cheng et al.",
        "year": "2024",
        "venue": "EMNLP 2024",
        "role": "Advanced INT4 Rounding for Large Models"
    },
    {
        "id": "27",
        "filename": "27_Liu_2024_MobileLLM_Sub_Billion_Parameter_LLMs.pdf",
        "url": "https://arxiv.org/pdf/2402.14905.pdf",
        "title": "MobileLLM: Optimizing Sub-billion Parameter Language Models for On-Device Use Cases",
        "authors": "Zechun Liu et al. (Meta)",
        "year": "2024",
        "venue": "ICML 2024",
        "role": "Small On-Device Model Architecture Design"
    },
    {
        "id": "28",
        "filename": "28_Ma_2024_The_Era_of_1Bit_LLMs_BitNet_b158.pdf",
        "url": "https://arxiv.org/pdf/2402.17764.pdf",
        "title": "The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits (BitNet b1.58)",
        "authors": "Shuming Ma et al. (Microsoft Research)",
        "year": "2024",
        "venue": "arXiv:2402.17764",
        "role": "Extreme Quantization Theoretical Scaling"
    },
    {
        "id": "29",
        "filename": "29_Tseng_2024_QuIP_Hadamard_Incoherence_Lattice_Codebooks.pdf",
        "url": "https://arxiv.org/pdf/2402.04396.pdf",
        "title": "QuIP#: Even Better LLM Quantization with Hadamard Incoherence and Lattice Codebooks",
        "authors": "Albert Tseng, Jerry Chee, Qinghao Hu, et al.",
        "year": "2024",
        "venue": "ICML 2024",
        "role": "Theoretical Error Bounds in Post-Training Quantization"
    },
    {
        "id": "30",
        "filename": "30_Sheng_2024_SGLang_Efficient_Execution_Structured_LM.pdf",
        "url": "https://arxiv.org/pdf/2312.07104.pdf",
        "title": "SGLang: Efficient Execution of Structured Language Model Programs",
        "authors": "Lianmin Sheng et al.",
        "year": "2024",
        "venue": "NeurIPS 2024",
        "role": "Multi-Agent KV-Cache Sharing & High-Throughput Runtime"
    },

    # --- Pillar 4: Benchmarks & Empirical Evaluation Infrastructure ---
    {
        "id": "31",
        "filename": "31_Mialon_2024_GAIA_Benchmark_for_General_AI_Assistants.pdf",
        "url": "https://arxiv.org/pdf/2311.12983.pdf",
        "title": "GAIA: A Benchmark for General AI Assistants",
        "authors": "Gregoire Mialon et al. (Meta, Hugging Face, AutoGPT)",
        "year": "2024",
        "venue": "ICLR 2024",
        "role": "Primary Tool-Use & Multi-Step Agent Benchmark"
    },
    {
        "id": "32",
        "filename": "32_Jimenez_2024_SWE_bench_Real_World_GitHub_Issues.pdf",
        "url": "https://arxiv.org/pdf/2310.06770.pdf",
        "title": "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
        "authors": "Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan",
        "year": "2024",
        "venue": "ICLR 2024 (Oral)",
        "role": "Multi-Step Real-World Engineering Benchmark"
    },
    {
        "id": "33",
        "filename": "33_Krishna_2024_FRAMES_Factuality_Retrieval_Multihop.pdf",
        "url": "https://arxiv.org/pdf/2409.05591.pdf",
        "title": "FRAMES: Factuality, Retrieval, And Multi-hop Evaluation with Structured Knowledge",
        "authors": "Satyapriya Krishna et al. (Google)",
        "year": "2024",
        "venue": "arXiv:2409.05591 / EMNLP 2024",
        "role": "Multi-Hop Reasoning Benchmark"
    },
    {
        "id": "34",
        "filename": "34_Patil_2024_Berkeley_Function_Calling_Leaderboard_Gorilla.pdf",
        "url": "https://arxiv.org/pdf/2403.01374.pdf",
        "title": "The Berkeley Function-Calling Leaderboard (BFCL)",
        "authors": "Shishir G. Patil et al. (UC Berkeley)",
        "year": "2024",
        "venue": "arXiv:2403.01374 / ICML 2024",
        "role": "Standardized Tool/Function-Calling Evaluation"
    },
    {
        "id": "35",
        "filename": "35_Wang_2024_MMLU_Pro_Robust_Challenging_Benchmark.pdf",
        "url": "https://arxiv.org/pdf/2406.01574.pdf",
        "title": "MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark",
        "authors": "Yubo Wang et al.",
        "year": "2024",
        "venue": "NeurIPS 2024 (Datasets Track)",
        "role": "Parametric Knowledge Density Benchmark"
    }
]

def download_paper(paper, output_dir):
    filepath = os.path.join(output_dir, paper["filename"])
    if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
        print(f"[{paper['id']}/35] ALREADY DOWNLOADED: {paper['filename']} ({os.path.getsize(filepath) / 1024 / 1024:.2f} MB)")
        return True, os.path.getsize(filepath)

    print(f"[{paper['id']}/35] Downloading: {paper['title'][:50]}... from {paper['url']}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 ResearchPaperBot/1.0"
    }

    req = urllib.request.Request(paper["url"], headers=headers)
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                # Verify PDF signature
                if not data.startswith(b"%PDF"):
                    print(f"   [!] Error: Response is not a valid PDF (got {data[:20]!r})")
                    return False, 0
                with open(filepath, "wb") as f:
                    f.write(data)
                size_mb = len(data) / 1024 / 1024
                print(f"   [+] Saved {paper['filename']} ({size_mb:.2f} MB)")
                time.sleep(1.2)  # Respect server rate limits
                return True, len(data)
        except Exception as e:
            print(f"   [!] Attempt {attempt}/{max_retries} failed: {e}")
            time.sleep(2 * attempt)
            
    return False, 0

def main():
    print(f"=== Starting Download of {len(PAPERS)} Research Papers into {OUTPUT_DIR} ===\n")
    success_count = 0
    total_bytes = 0
    results = []

    for p in PAPERS:
        ok, size = download_paper(p, OUTPUT_DIR)
        if ok:
            success_count += 1
            total_bytes += size
        results.append({**p, "status": "Downloaded" if ok else "Failed", "size_mb": size / 1024 / 1024})

    print(f"\n=== Download Finished: {success_count}/{len(PAPERS)} papers downloaded successfully ({total_bytes / 1024 / 1024:.2f} MB total) ===")

    # Generate INDEX.md in sources/
    index_path = os.path.join(OUTPUT_DIR, "INDEX.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# Research Sources Catalog (2024–2026)\n\n")
        f.write(f"**Total Papers Downloaded:** {success_count} / {len(PAPERS)}\n")
        f.write(f"**Total Size:** {total_bytes / 1024 / 1024:.2f} MB\n\n")
        f.write("All papers are primary research publications (excluding surveys/SLRs) directly relevant to comparing Multi-Agent Systems of smaller LLMs vs. Single-Agent Systems of larger quantized LLMs under memory constraints.\n\n")
        f.write("| # | File | Title | Authors | Year | Venue | Role / Relevance | Size |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for p in results:
            status_mark = f"[{p['filename']}](./{p['filename']})" if p['status'] == 'Downloaded' else f"FAILED: {p['filename']}"
            f.write(f"| {p['id']} | {status_mark} | {p['title']} | {p['authors']} | {p['year']} | {p['venue']} | {p['role']} | {p['size_mb']:.2f} MB |\n")

    print(f"[+] Annotated bibliography index generated at {index_path}")

if __name__ == "__main__":
    main()
