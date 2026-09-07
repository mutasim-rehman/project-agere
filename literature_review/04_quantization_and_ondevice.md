# Literature Review: Pillar 3 — Quantization, Memory Scaling & On-Device LLMs (Papers 22–30)

This document provides a comprehensive, rigorous literature review of Papers 22 through 30, covering **weight-only and end-to-end quantization, extreme low-bit compression, sub-billion on-device model architectures, and multi-agent KV-cache serving runtimes**.

---

## 22. AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration

* **File:** [`../sources/22_Lin_2024_AWQ_Activation_Aware_Weight_Quantization.pdf`](../sources/22_Lin_2024_AWQ_Activation_Aware_Weight_Quantization.pdf)
* **Authors:** Ji Lin, Jiaming Tang, Haotian Tang, Shang Yang, Xingyu Chen, Wei-Chen Wang, Song Han
* **Affiliation & Venue:** MIT HAN Lab — **MLSys 2024 (Best Paper Award)**

### 1. What It Is
The industry-standard, hardware-friendly weight-only quantization method for LLMs, demonstrating that protecting the top ~1% of salient weights (identified by activation magnitude rather than weight magnitude) preserves generalization and enables lossless 4-bit integer inference on edge and workstation GPUs.

### 2. How It Relates to Our Research
Serves as our **primary quantization technique for the Single-Agent System (SAS) arm**. To fit larger models (e.g., 14B, 32B, 70B) into our target resident VRAM budgets (8 GB, 16 GB, 24 GB), we use AWQ to compress the model weights to 4-bit precision without breaking their core reasoning abilities.

### 3. Detailed Methodology
* **Core Technique:** Activation-aware per-channel scaling factor optimization; applies an equivalent transformation $W' = W \cdot S$ and $X' = S^{-1} \cdot X$ to reduce quantization error on salient weights.
* **Avoidance of Overfitting:** Avoids backpropagation or dataset reconstruction; uses only a tiny calibration set (e.g., 128 random text snippets).
* **Hardware Support:** Native INT4 GPU execution kernel integrated into vLLM, TensorRT-LLM, and Hugging Face.
* **Benchmarks:** Wikitext-2 perplexity, CommonSenseQA, MMLU, GSM8K.
* **Metrics:** Perplexity degradation, On-device token generation speedup ($>3\times$ over FP16), GPU memory footprint.

### 4. Key Novelty & Theoretical Contributions
* **Activation Salience Discovery:** Proves that weight magnitude is an unreliable indicator of importance; activation magnitude reliably flags the channels essential for preserving reasoning.
* **Generalization Preservation:** Unlike reconstruction-based methods (e.g., GPTQ), AWQ does not overfit to calibration domains, retaining superior zero-shot and out-of-domain reasoning.

### 5. Critical Limitations & Caveats
* Quantizes weights only; activations and the KV-cache remain in 16-bit precision, meaning KV-cache growth at long context lengths can still consume substantial VRAM.

### 6. Why We SHOULD Include It as a Source
* **MLSys 2024 Best Paper.** It is the most widely trusted and adopted 4-bit quantization framework in the open-source ecosystem. Using AWQ for our SAS arm eliminates any reviewer accusation that our single-agent baseline was degraded by poor quantization.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Cannot be excluded: it is the primary engine of our single-agent experimental setup.

---

## 23. QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs

* **File:** [`../sources/23_Ashkboos_2024_QuaRot_Outlier_Free_4Bit_Inference.pdf`](../sources/23_Ashkboos_2024_QuaRot_Outlier_Free_4Bit_Inference.pdf)
* **Authors:** Saleh Ashkboos, Amirkeivan Mohtashami, Maximilian L. Croci, Bo Li, Martin Jaggi, Dan Alistarh, Torsten Hoefler
* **Affiliation & Venue:** ETH Zurich, EPFL, IST Austria — **NeurIPS 2024**

### 1. What It Is
A breakthrough quantization scheme that uses randomized orthogonal Hadamard rotations to eliminate activation outliers, enabling **full end-to-end 4-bit inference** across model weights, activations, and the KV-cache simultaneously with virtually zero accuracy degradation.

### 2. How It Relates to Our Research
Provides our **end-to-end 4-bit baseline**. While AWQ leaves activations and KV caches in 16-bit, QuaRot quantizes the entire pipeline to 4-bit. This allows us to test an even larger model within our VRAM envelope because the KV-cache memory footprint is reduced by $4\times$.

### 3. Detailed Methodology
* **Core Mechanism:** Multiplies weight matrices and activation vectors by orthogonal randomized Hadamard matrices ($H$), exploiting computational invariance: $(X H)(H^T W) = X W$.
* **Full 4-Bit Coverage:** Weights (W4), Activations (A4), and KV-cache (KV4).
* **Models:** LLaMA-2 (7B, 13B, 70B), LLaMA-3.
* **Metrics:** WikiText-2 perplexity, Zero-shot accuracy (ARC, HellaSwag, PIQA), Memory consumption reduction.

### 4. Key Novelty & Theoretical Contributions
* **Elimination of Outliers via Rotation:** Solves the long-standing problem of activation outliers in transformers without requiring expensive clipping or channel-splitting.
* **Lossless 4-Bit KV-Cache:** Achieves 99% accuracy retention on LLaMA-2-70B while compressing the entire runtime memory footprint by nearly $4\times$.

### 5. Critical Limitations & Caveats
* Online rotation transformations add slight arithmetic overhead during GEMM matrix multiplication.

### 6. Why We SHOULD Include It as a Source
* **NeurIPS 2024 paper.** Represents the frontier of end-to-end 4-bit inference. Citing it proves our single-agent baseline includes the most aggressive, state-of-the-art memory compression techniques available.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our experiments use standard AWQ/vLLM kernels for implementation simplicity, QuaRot can be cited as the theoretical benchmark for full A4W4KV4 scaling.

---

## 24. SpinQuant: LLM Quantization with Learned Rotations

* **File:** [`../sources/24_Liu_2025_SpinQuant_LLM_Quantization_Learned_Rotations.pdf`](../sources/24_Liu_2025_SpinQuant_LLM_Quantization_Learned_Rotations.pdf)
* **Authors:** Zechun Liu, Barlas Oguz, Aasish Pappu, Lin Xiao, et al.
* **Affiliation & Venue:** Meta AI — **ICLR 2025**

### 1. What It Is
An advanced post-training quantization framework that learns optimized rotation matrices (using Cayley optimization on the Stiefel manifold) to suppress activation and weight outliers, outperforming random Hadamard rotations (QuaRot) and closing the accuracy gap with full-precision FP16 models.

### 2. How It Relates to Our Research
Serves as the **state-of-the-art 4-bit quantization baseline**. It guarantees that our single quantized model operates at the highest possible numeric fidelity available in the literature, eliminating quantization artifacts as a confounding variable.

### 3. Detailed Methodology
* **Optimization Technique:** Treats rotation matrices as learnable parameters constrained to the orthogonal group $O(n)$, optimized via gradient descent using Cayley transforms.
* **Coverage:** Weights (W4), Activations (A4), and KV-cache (KV4).
* **Benchmarks:** MMLU, GSM8K, HumanEval, WikiText perplexity.
* **Metrics:** Accuracy recovery relative to FP16, Perplexity gap.

### 4. Key Novelty & Theoretical Contributions
* **Learned vs. Random Rotations:** Demonstrates that random Hadamard transforms leave residual outlier energy; learning the rotation angles specifically tailored to a model's weight geometry recovers an additional 1.5–3.0% accuracy on complex reasoning tasks.

### 5. Critical Limitations & Caveats
* Requires an offline optimization phase (several GPU hours) to compute the learned rotation matrices before deployment.

### 6. Why We SHOULD Include It as a Source
* **Published at ICLR 2025.** Establishes that our study accounts for the absolute latest peer-reviewed breakthroughs in LLM quantization.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Can be grouped with QuaRot as rotation-based PTQ; if space is tight, keep AWQ and QuaRot and cite SpinQuant as an advanced extension.

---

## 25. AQLM: Extreme Compression of Large Language Models via Additive Quantization

* **File:** [`../sources/25_Egiazarian_2024_AQLM_Extreme_Compression_Additive_Quantization.pdf`](../sources/25_Egiazarian_2024_AQLM_Extreme_Compression_Additive_Quantization.pdf)
* **Authors:** Vage Egiazarian, Andrei Panferov, Denis Kuznitskiy, Artem Babenko, Dan Alistarh
* **Affiliation & Venue:** Yandex Research, IST Austria, HSE University — **ICML 2024**

### 1. What It Is
The first Pareto-optimal quantization scheme for extreme compression regimes below 3 bits per parameter, generalizing classical Additive Quantization (AQ) to LLMs through joint codebook optimization across entire transformer blocks.

### 2. How It Relates to Our Research
Enables our **Extreme Scale vs. MAS experiment**. In our 16 GB or 24 GB memory tier, AQLM allows us to compress a colossal **70B parameter model down to 2-bit or 3-bit precision** to reside in the exact same memory footprint as two or three 8B models. This directly tests: *does extreme parameter scale beat small multi-agent ensembles under identical VRAM?*

### 3. Detailed Methodology
* **Algorithm:** Additive vector quantization where each weight vector is represented as the sum of $M$ codewords from learned vector codebooks ($W \approx \sum_{m=1}^M C_m[i_m]$).
* **Optimization:** Beam search codebook assignment with block-wise gradient-based fine-tuning.
* **Target Bit-widths:** 2-bit, 2.5-bit, and 3-bit per weight.
* **Models:** LLaMA-2 (7B to 70B), Mistral-7B.
* **Metrics:** Perplexity on WikiText-2/C4, Zero-shot accuracy, Inference throughput.

### 4. Key Novelty & Theoretical Contributions
* **Breaking the 3-Bit Barrier:** Previous methods (GPTQ, AWQ) collapse into catastrophic perplexity explosion below 3 bits; AQLM is the first scheme where 2-bit/3-bit models remain coherent and retain non-trivial reasoning capability.

### 5. Critical Limitations & Caveats
* Very slow decoding speeds compared to hardware-native INT4 kernels, as codebook lookups do not map cleanly to standard Tensor Cores.

### 6. Why We SHOULD Include It as a Source
* **ICML 2024 publication.** Essential for exploring the absolute limits of the memory-vs-scale trade-off. It lets us test the most extreme expression of our research hypothesis.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our study restricts its single-agent arm strictly to standard 4-bit/8-bit precision (where hardware acceleration is robust), AQLM's sub-3-bit regime is an optional boundary case.

---

## 26. Optimize Weight-Only Quantization of Large Language Models with an Advanced Rounding Technique (AutoRound)

* **File:** [`../sources/26_Cheng_2024_AutoRound_Advanced_Weight_Only_Quantization.pdf`](../sources/26_Cheng_2024_AutoRound_Advanced_Weight_Only_Quantization.pdf)
* **Authors:** Weiwei Cheng et al.
* **Affiliation & Venue:** Intel Labs — **EMNLP 2024**

### 1. What It Is
An advanced weight-only post-training quantization method that optimizes rounding values via sign gradient descent over a lightweight calibration set, consistently outperforming standard round-to-nearest (RTN) and GPTQ on 4-bit and 2-bit settings.

### 2. How It Relates to Our Research
Provides an alternative, highly accurate **INT4 quantization pipeline** that integrates seamlessly with open-source runtimes (AutoGPTQ, Hugging Face), ensuring our quantized single models have competitive baseline options.

### 3. Detailed Methodology
* **Optimization:** Formulates rounding as an optimization problem minimizing layer-wise output reconstruction error using sign gradient descent with clipping.
* **Target Presets:** W4A16, W2A16 across broad model families.
* **Metrics:** Perplexity, Zero-shot reasoning accuracy, Quantization time (completes in minutes on 1 GPU).

### 4. Key Novelty & Theoretical Contributions
* **Fast and Superior Rounding:** Achieves accuracy superior to GPTQ and competitive with AWQ in a fraction of the calibration time, with zero architectural modifications.

### 5. Critical Limitations & Caveats
* Weight-only; does not quantize activations or KV-cache.

### 6. Why We SHOULD Include It as a Source
* **EMNLP 2024.** Demonstrates thorough awareness of the latest 2024 post-training quantization techniques.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Largely redundant with AWQ; in a 15-paper shortlist, AWQ (MLSys Best Paper) is the stronger representative for weight-only quantization.

---

## 27. MobileLLM: Optimizing Sub-billion Parameter Language Models for On-Device Use Cases

* **File:** [`../sources/27_Liu_2024_MobileLLM_Sub_Billion_Parameter_LLMs.pdf`](../sources/27_Liu_2024_MobileLLM_Sub_Billion_Parameter_LLMs.pdf)
* **Authors:** Zechun Liu et al.
* **Affiliation & Venue:** Meta AI — **ICML 2024**

### 1. What It Is
A landmark architecture study proving that for sub-billion parameter language models (125M–1B), **model architecture matters far more than data scaling**, proposing deep-and-thin designs, embedding sharing, and block weight-sharing to maximize capability on edge hardware.

### 2. How It Relates to Our Research
Informs how we select and structure the **small sub-agents in our low-memory (8 GB VRAM) tier**. In an 8 GB budget, a multi-agent system must deploy models under 2B parameters (e.g., 1B or sub-1B). MobileLLM provides the empirical blueprint for what architectural properties small agents must possess to avoid reasoning collapse.

### 3. Detailed Methodology
* **Architectural Innovations:**
  1. *Deep and Thin:* Maximizes layer depth while reducing hidden dimensions to optimize cache bandwidth.
  2. *Embedding Sharing:* Ties input and output embedding layers to save parameter footprint.
  3. *Grouped-Query Attention (GQA):* Reduces KV-cache memory overhead.
  4. *Immediate Block Weight-Sharing:* Reuses transformer blocks to increase effective depth with zero memory increase.
* **Benchmarks:** Commonsense reasoning, Chat benchmarks, Tool/API calling.
* **Metrics:** Zero-shot accuracy, On-device execution latency (iPhone / Android), Parameter efficiency.

### 4. Key Novelty & Theoretical Contributions
* **Sub-Billion Scaling Principles:** First paper to systematically map the scaling laws of models below 1B parameters, showing 2.7% to 4.3% accuracy gains over prior state-of-the-art models of identical size.

### 5. Critical Limitations & Caveats
* Focuses on pre-training and architecture design from scratch, whereas our study primarily evaluates existing off-the-shelf open-weight models (e.g., Qwen 2.5 0.5B/1.5B/3B).

### 6. Why We SHOULD Include It as a Source
* **ICML 2024.** Vital for justifying our sub-agent selection in resource-constrained regimes, proving that our small agent design choices are grounded in established edge architecture literature.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* If our smallest model evaluated is 3B parameters (e.g., in a 16 GB tier), sub-billion scaling principles are less central.

---

## 28. The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits (BitNet b1.58)

* **File:** [`../sources/28_Ma_2024_The_Era_of_1Bit_LLMs_BitNet_b158.pdf`](../sources/28_Ma_2024_The_Era_of_1Bit_LLMs_BitNet_b158.pdf)
* **Authors:** Shuming Ma, Hongyu Wang, Lingxiao Ma, Lei Wang, Wenhui Wang, Shaohan Huang, Li Dong, Ruiping Wang, Jilong Xue, Furu Wei
* **Affiliation & Venue:** Microsoft Research — *arXiv:2402.17764 (February 2024)*

### 1. What It Is
A revolutionary architecture paper introducing **BitNet b1.58**, where every transformer weight is constrained to ternary values $\{-1, 0, 1\}$, matching full-precision 16-bit LLM performance while fundamentally eliminating matrix multiplication in favor of integer addition.

### 2. How It Relates to Our Research
Establishes the **theoretical lower bound of parameter storage cost**. In the context of our research, BitNet represents the theoretical extreme of the single-agent arm: if a model can run at 1.58 bits, a monolithic 70B model could fit into less than 15 GB of memory, posing an existential challenge to multi-agent division of labor.

### 3. Detailed Methodology
* **Quantization Mechanism:** Absmean quantization scaling weights to ternary $\{-1, 0, 1\}$ and activations to 8-bit integers.
* **Compute Transformation:** Replaces FP16 matrix multiplications with pure integer addition kernels.
* **Benchmarks:** Perplexity, Winogrande, Hellaswag, ARC, OpenBookQA.
* **Metrics:** Memory consumption savings (up to $3.55\times$), Energy efficiency ($up to 71.4\times$ reduction in matrix multiplication energy), Latency speedup.

### 4. Key Novelty & Theoretical Contributions
* **Parity with FP16:** First architecture to prove that ternary 1.58-bit models can match full-precision Transformer models across perplexity and downstream tasks starting at 3B parameters.

### 5. Critical Limitations & Caveats
* Requires full pre-training from scratch; cannot be applied as post-training quantization (PTQ) to existing pre-trained checkpoints like Qwen or LLaMA.

### 6. Why We SHOULD Include It as a Source
* Extremely famous landmark paper (2024). Citing it in the Introduction or Related Work frames the ultimate theoretical horizon of memory-efficient single-model deployment.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Because it requires from-scratch training, we cannot use it empirically with standard open-weight checkpoints. Can be omitted from the top 15 core papers.

---

## 29. QuIP#: Even Better LLM Quantization with Hadamard Incoherence and Lattice Codebooks

* **File:** [`../sources/29_Tseng_2024_QuIP_Hadamard_Incoherence_Lattice_Codebooks.pdf`](../sources/29_Tseng_2024_QuIP_Hadamard_Incoherence_Lattice_Codebooks.pdf)
* **Authors:** Albert Tseng, Jerry Chee, Qinghao Hu, et al.
* **Affiliation & Venue:** Cornell University — **ICML 2024**

### 1. What It Is
A theoretical and empirical quantization paper combining randomized Hadamard transforms (incoherence processing) with $E_8$ lattice codebooks to achieve state-of-the-art post-training quantization at 2-bit, 3-bit, and 4-bit precision.

### 2. How It Relates to Our Research
Provides theoretical bounds on the **quantization distortion penalty**. It mathematically characterizes the exact point where aggressive quantization begins to destroy reasoning capability, helping us predict the crossover threshold where an intact smaller model in an MAS outperforms a degraded large quantized model.

### 3. Detailed Methodology
* **Mechanism:** Incoherence transformation via randomized orthogonal matrices + Fast lattice vector quantization using the Gosset lattice $E_8$.
* **Target Bit-widths:** 2-bit, 3-bit, and 4-bit.
* **Metrics:** Perplexity, Zero-shot accuracy, Theoretical quantization distortion bounds.

### 4. Key Novelty & Theoretical Contributions
* **Provable Distortion Bounds:** Establishes theoretical proofs that incoherence transformations bound maximum roundoff errors, enabling 2-bit models to retain grammatical and contextual structure.

### 5. Critical Limitations & Caveats
* Complex decoding algorithms that require specialized custom CUDA kernels not widely supported across standard inference runtimes like vLLM.

### 6. Why We SHOULD Include It as a Source
* **ICML 2024.** Elevates the mathematical rigor of our literature review regarding the theoretical error scaling of quantized models.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Highly specialized mathematical quantization theory; can be trimmed in favor of AWQ and QuaRot.

---

## 30. SGLang: Efficient Execution of Structured Language Model Programs

* **File:** [`../sources/30_Sheng_2024_SGLang_Efficient_Execution_Structured_LM.pdf`](../sources/30_Sheng_2024_SGLang_Efficient_Execution_Structured_LM.pdf)
* **Authors:** Lianmin Sheng, Cody Hao Yu, Lianmin Zheng, et al.
* **Affiliation & Venue:** LMSYS Org, UC Berkeley — **NeurIPS 2024**

### 1. What It Is
A high-performance execution engine and domain-specific programming language for complex, multi-call LLM programs and multi-agent workflows, introducing **RadixAttention** to automatically reuse and share KV-cache prefix trees across multi-agent dialogues.

### 2. How It Relates to Our Research
Directly solves the **multi-agent memory scaling bottleneck**. In multi-agent systems, agents share identical prompt prefixes, system instructions, and task descriptions. SGLang's RadixAttention enables multi-agent sub-models to share these KV-cache pages in GPU memory, drastically reducing the resident VRAM footprint of our MAS configurations.

### 3. Detailed Methodology
* **Core Innovation:** RadixAttention — manages KV caches as a radix tree, enabling automatic prefix caching, branch sharing, and multi-turn cache retention without manual user management.
* **Benchmarks:** Multi-turn chat, Tool-use agents, Chain-of-Thought reasoning, Branching search (Tree-of-Thoughts).
* **Metrics:** Throughput ($up to 5\times$ over vLLM), Latency reduction, GPU memory utilization.

### 4. Key Novelty & Theoretical Contributions
* **Automatic Multi-Agent KV Cache Reuse:** First system to eliminate the massive memory redundancy inherent in multi-agent prompt loops by treating the KV-cache as a dynamic, reusable search tree.

### 5. Critical Limitations & Caveats
* Focuses on runtime inference optimization rather than model reasoning accuracy.

### 6. Why We SHOULD Include It as a Source
* **NeurIPS 2024.** Essential for explaining how our MAS experimental setup was optimized for memory efficiency, proving that our MAS implementation was not artificially handicapped by naive KV-cache duplication.

### 7. Why We Might NOT Include It (Risks / Filtering Rationale)
* Can be cited together with vLLM in the Systems/Implementation subsection.
