# System Gaps & Improvement List — SAS-Quant vs MAS-FP16

**Purpose:** Concrete list of **where each system fails for our finance use case**, what to improve, and **in what order** to test so the final comparison is fair.

**Use case:** Local KYC / CDD / credit-memo / mortgage-doc workflows on analyst RAM (see [`FINANCE_DOMAIN_CONTEXT.md`](./FINANCE_DOMAIN_CONTEXT.md)).

**Headline comparison (after hardening):** **MAS-FP16** vs **SAS-Quant** under equal peak RAM and thinking-token budget ([`EXPERIMENT_PROTOCOL.md`](./EXPERIMENT_PROTOCOL.md)).

---

## 0. Answer: Should we test as-is first, then fix, then compare?

**Yes — with one rule: freeze the “naive baseline” results before you start improving.**

### Recommended loop

| Phase | What you run | Why |
| :---: | :--- | :--- |
| **0 — Spec** | Same tasks, tools, RAM tier, token cap for both arms | Fairness invariants |
| **1 — Naive baseline** | **SAS-Quant as-is** (off-the-shelf Q4 instruct) **and** **MAS as-is** (simple pipeline, no special gates) | Shows industry-default pain *and* raw multi-agent pain |
| **2 — Error triage** | Tag every failure with the IDs below (S-*, M-*) | Turns anecdotes into an improvement backlog |
| **3 — Harden each arm** | Fix **only** use-case gaps (fine-tune / prompts / verifier / schemas) | Matches supervisor: quant alone ≠ useful; MAS alone ≠ useful |
| **4 — Final compare** | Hardened SAS-Quant vs hardened MAS-FP16 | Answers “which is better for *our* product after we do the work” |
| **5 — Ablations** | Turn fixes on/off | Proves which fix actually moved invention rate / mismatch recall |

### Do / don’t

- **Do** keep Phase-1 scores in the paper (“naive local default”).  
- **Do** improve **both** arms before crowning a winner (supervisor intent).  
- **Don’t** only polish MAS and compare to a crippled Q4 monolith (or vice versa).  
- **Don’t** skip Phase 1 — otherwise you cannot show that fixes were necessary.  
- **Don’t** change RAM/token/tool parity between phases.

### What “overcome” means before final compare

You are ready for Phase 4 when, on a held-out **dev** slice:

1. **Invention rate** and **mismatch recall** are measured for both arms.  
2. Top failure IDs from §1–2 each have at least one attempted mitigation.  
3. Metrics stabilize across 3 seeds (protocol).  
4. Negative-control track still runs (expect SAS-Quant stronger there).

---

## 1. Where **quantized SAS** lacks (use-case gaps)

Industry default: one larger Q4/Q5 generalist + tools on 16 GB.

| ID | Gap | What it looks like on KYC/credit | Why it happens | Improvement to try | Priority |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **S1** | **No domain adaptation** | Weak on KYC field names, memo structure, refusal phrasing | Quantization only compresses a *general* model | LoRA / QLoRA / instruction tune on synthetic KYC+memo packs | P0 |
| **S2** | **Invention under missing data** | Fills blank DOB, invents registry #, fabricates deposit | Generalist trained to be “helpful”; quant amplifies tool/agent errors ([Jang 2026](./literature_review/04_quantization_and_ondevice.md)) | Explicit refuse policy; “UNKNOWN” tokens; verifier pass; train on missing-field examples | P0 |
| **S3** | **Mixed roles in one brain** | Extraction errors invisible inside fluent narrative | One prompt does extract+judge+draft | Single-model **staged prompts** (pseudo-pipeline) + JSON schema checkpoints | P0 |
| **S4** | **Weak numeric discipline** | Prose changes EBITDA / DSCR vs spreadsheet | LLM treats numbers as language | Force calculator tool; ban free-form amounts; cite tool JSON only | P0 |
| **S5** | **Tool-call brittleness under quant** | Wrong tool names, bad args, entity drift mid-case | Quant amplifies existing agent failures ([Jang 2026](./literature_review/04_quantization_and_ondevice.md)) | Stricter schemas (BFCL-style); fewer tools; retry budget ≤2 | P1 |
| **S6** | **Citation theatre** | “According to passport…” with wrong/empty span | No quote-check loop | Mandatory span IDs; post-hoc string match gate | P0 |
| **S7** | **Missed mismatches** | ID ≠ registry not flagged | Attention diluted across long pack | Dedicated compare step in prompt; deterministic diff tool | P0 |
| **S8** | **Context window thrash** | Drops early docs when pack is large | One context for everything | Chunked extract-then-summarise; retrieval over case store | P1 |
| **S9** | **No audit-friendly structure** | Free text hard to sample in exams | Chatty completion style | Fixed output template (sections + discrepancy table) | P1 |
| **S10** | **Over-confident risk language** | Sounds like it approved / risk-rated | Instruction bleed | System prompt + train: “draft only; no approval” | P1 |
| **S11** | **Cross-client RAG risk** (if enabled) | Retrieves another client’s snippet | Shared index | Client-scoped collections; hard ACL | P0 |
| **S12** | **Quantization quality floor** | Sharp drop at aggressive Q3/Q2 | Precision loss on long structured outputs | Prefer Q4_K_M / Q5; measure vs FP16 same size (RQ1 control) | P2 |

### SAS improvement backlog (ordered)

1. Domain fine-tune / adapters on synthetic finance packs (**S1**)  
2. Refuse + cite + schema gates (**S2, S6, S3**)  
3. Deterministic numerics + mismatch tools (**S4, S7**)  
4. Tool schema hardening (**S5**)  
5. Chunking / case RAG (**S8, S11**)  
6. Output templates for audit (**S9, S10**)  
7. Quant level sweep only after above (**S12**)

---

## 2. Where **MAS** lacks (use-case gaps)

Typical naive MAS: chatty extract → draft → maybe “critic,” no hard contracts.

Literature anchor: [Cemri et al. MAST](./literature_review/summaries/07_cemri_2025_why_do_multi_agent_llm_systems_fail.md) (specification / misalignment / verification clusters).

| ID | Gap | What it looks like on KYC/credit | Why it happens | Improvement to try | Priority |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **M1** | **Specification drift** | Agents disagree on what “case complete” means | Vague role prompts | Written SOP per role; shared schema of done-ness | P0 |
| **M2** | **Lossy handoffs (DPI)** | Extractor softens “unknown”; drafter invents | Natural-language summaries drop uncertainty ([Tran](./literature_review/summaries/01_tran_2026_single_agent_llms_outperform_multi_agent.md)) | **JSON-only** contracts; pass UNKNOWN explicitly; no prose between stages | P0 |
| **M3** | **Hallucination snowball** | One bad amount appears in every later agent | No boundary gate ([Singh & Pawar](./sources/PAPERS_DICTIONARY.md)) | Verifier between stages; reject/regenerate on failed quote-check | P0 |
| **M4** | **Context collapse** | Downstream agent forgets original constraints (“cite or refuse”) | Long chat history | Stateless workers + orchestrator holds constraints; truncate chatter | P0 |
| **M5** | **Inter-agent misalignment** | Retriever returns policy for wrong product; drafter uses it | Weak routing | Explicit task packet (product, jurisdiction, doc IDs) | P1 |
| **M6** | **Endless loops / debate theatre** | Agents argue; burn token budget | Unbounded multi-round talk | Hard round caps; stop on schema-valid output | P1 |
| **M7** | **Weak / missing verifier** | Final narrative never quote-checked | Critic that only rephrases | Dedicated verifier with **deterministic** span match | P0 |
| **M8** | **Token budget fragmentation** | Team exhausts $T_{\text{think}}$ before verify | Equal total tokens vs SAS but split N ways | Budget scheduler; prefer extract+verify over debate | P0 |
| **M9** | **RAM residency vs sequential load** | Laptop OOMs or thrash | All agents resident vs load/unload | Report both modes; primary = resident parity with SAS | P1 |
| **M10** | **Orchestrator too weak** | Wrong stage order; skips mismatch check | Small orchestrator | Put more capacity in orchestrator than workers ([Żywot](./literature_review/summaries/02_zywot_2026_can_small_agent_collaboration_beat_single_big_llm.md)) | P1 |
| **M11** | **Duplicate work / tool races** | Two agents call extract differently | No shared case state | Single case store; tools owned by one role | P2 |
| **M12** | **No domain specialization** | “Extractor” is still a general chat model | Roles in name only | Per-role fine-tunes or specialized prompts + schemas | P0 |
| **M13** | **Verification theatre** | Verifier always says “looks good” | Same model family, sycophancy | Independent checklist; binary cite/fail; confidence gate | P0 |
| **M14** | **Latency / ops complexity** | Analyst waits; harder to debug | More moving parts | Structured logs per agent; SLA target secondary to grounding | P2 |

### MAS improvement backlog (ordered)

1. Strict JSON SOPs + UNKNOWN propagation (**M1, M2**)  
2. Hard verifier gates between stages (**M3, M7, M13**)  
3. Token budget scheduler (**M8**)  
4. Stateless workers + constraint packet (**M4, M5**)  
5. Cap debate / rounds (**M6**)  
6. Role-specific adapters if needed (**M12**)  
7. Orchestrator sizing + RAM mode reporting (**M9, M10**)  
8. Shared case store (**M11**)  

---

## 3. Shared gaps (both systems)

These are **not** solved by picking SAS or MAS alone:

| ID | Gap | Mitigation (both arms) |
| :--- | :--- | :--- |
| **X1** | Wrong eval (MMLU-style) | Use grounding, invention, mismatch recall |
| **X2** | LLM owns numeric truth | Calculators / spreads outside the model |
| **X3** | No human gate | UI/process: draft only |
| **X4** | Real PII in experiments | Synthetic packs only |
| **X5** | Unequal tools between arms | Identical tool schemas |
| **X6** | Unequal RAM/tokens | RUPP + Tran token parity |

---

## 4. Mapping gaps → Agere metrics

| If you see… | Count toward… | Typical owner |
| :--- | :--- | :--- |
| Invented amount/date/name | Invention rate | S2, M3 |
| Claim without correct span | Grounding accuracy ↓ | S6, M7 |
| Planted ID≠registry missed | Mismatch recall ↓ | S7, M1 |
| Missing field filled | Refusal correctness ↓ | S2, M2 |
| Tool arg errors | Process log (Jang-style) | S5 |
| Token exhaustion before answer | Token efficiency ↓ | M8, S8 |

Tag each failed case with **one primary ID** (S*/M*/X*) for the paper’s error analysis (MAST-aligned).

---

## 5. Fair final comparison checklist

Before declaring a winner for the use case:

- [ ] Phase-1 naive baselines recorded for **both** arms  
- [ ] S1–S7 and M1–M8 mitigations attempted or explicitly deferred with reason  
- [ ] Same **16 GB** primary tier, same $T_{\text{think}}$, same tools  
- [ ] Tracks A–C (origination / KYC / credit) + Track D negative control  
- [ ] Metrics: grounding, invention, mismatch recall (not only accuracy)  
- [ ] MAS resident vs sequential reported separately  
- [ ] Optional: show that domain fine-tune helped SAS **and** structured gates helped MAS  

---

## 6. One-slide summary for supervisor

1. **Test as-is** → measure mistakes.  
2. **Fix SAS** (fine-tune + refuse/cite/tools) **and fix MAS** (JSON handoffs + verifier + budget).  
3. **Compare** hardened systems under equal RAM/tokens on KYC/credit/mortgage tasks.  
4. **Quantization alone** and **multi-agent alone** are both incomplete for the product.

---

## 7. Living backlog

Update this table as experiments run:

| Date | Case ID | Arm | Gap ID | Symptom | Fix applied | Metric delta |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| _TBD_ | | SAS / MAS | | | | |
