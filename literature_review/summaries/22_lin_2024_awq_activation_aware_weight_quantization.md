# 22. AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration

> **Authors:** Ji Lin, Jiaming Tang, Haotian Tang, Song Han, et al.  
> **Affiliation & Venue:** MLSys 2024 (Best Paper Award)  
> **Publication Year:** 2024  
> **Local PDF Source:** [`22_Lin_2024_AWQ_Activation_Aware_Weight_Quantization.pdf`](../../sources/22_Lin_2024_AWQ_Activation_Aware_Weight_Quantization.pdf)  
> **Role in Our Study:** **Primary 4-Bit Quantization Backbone for SAS Arm**

---

## 1. Executive Summary & Core Premise
Winner of the MLSys 2024 Best Paper Award, AWQ establishes that protecting the top ~1% of salient weights (identified via activation magnitude rather than weight magnitude) enables accurate, hardware-friendly 4-bit integer quantization without backpropagation or calibration overfitting.

---

## 2. Research Motivation & Problem Formulation
Prior quantization methods (GPTQ) required complex reconstruction optimization and overfit to calibration data. Round-to-nearest (RTN) destroyed reasoning. AWQ provides an equivalent transformation that makes INT4 weight quantization virtually lossless.

---

## 3. Technical Architecture & Methodology
- Discovers that salient weights protect model accuracy; salience is determined by observing average activation magnitude.
- Applies an equivalent per-channel scaling factor transformation $W' = W \cdot S, X' = S^{-1} \cdot X$ to protect salient channels.
- Hardware-accelerated INT4 GEMM kernel integrated into vLLM and TensorRT-LLM.

---

## 4. Experimental Framework & Setup
- Evaluated across LLaMA, Mistral, and Qwen families from 7B to 70B.
- Benchmarks: WikiText perplexity, CommonSenseQA, MMLU, GSM8K.

---

## 5. Key Quantitative Findings & Breakthroughs
- Retains near-FP16 perplexity across all model sizes.
- Delivers >3× token throughput speedup on edge GPUs while slashing memory footprint by 75%.

---

## 6. Critical Limitations, Caveats & Failure Modes
- Weight-only quantization; activations and KV-cache remain in 16-bit.

---

## 7. Direct Strategic Connection to Our Research Project
**Central Research Dilemma:** *Can a Multi-Agent System of smaller LLMs outperform a single agent with a larger quantized LLM under equal resident VRAM?*

Our **primary quantization method** for the Single-Agent arm, used to compress 14B, 32B, and 70B models into target VRAM budgets.

---

## 8. Citation Utility & Key Takeaways
Mandatory citation in Section 3 to validate our 4-bit single-agent baseline.
