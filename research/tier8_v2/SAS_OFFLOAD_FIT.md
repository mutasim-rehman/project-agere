# Comparable SAS adaptation: measured fit gate

The MAS drafter has genuine adaptation; comparable SAS adaptation is still
missing. This gate attempts two updates on the longest example in the same
661-fitting/100-validation corpus with complete1024-token input/target bounds.
It does not shorten the task, train a full epoch, evaluate QA or establish novelty.

`scripts/tier8_v2_sas_offload_fit.py --prepare --out <new SSD directory>` freezes
code, corpus, tokenizer, runtime versions and the existing evaluation dependency.
`--plan <that directory>/plan.json` waits for the original PID/create-time/plan,
requires all frozen jobs to complete in order, revalidates completed external
arms and preserved originals, checks frozen inputs/runtime, then launches once.
Failure stops the controller. There is no automatic retry or implicit resume.

The worker verifies every original official Qwen7B source artifact against
`manifests/hf_snapshots.json`, then loads the decoder in NF4 with CPU head and
embedding placement. Training uses the same rank8/alpha16/all-linear LoRA and
AdamW2e-4/clip1 settings as the actor fit protocol. It requires changed tensors,
finite nonzero gradients and two actual optimizer updates; outputs are marked fit.

Accelerate's default CPU offload hooks reload complete matrices onto the GPU.
The new path detaches the embedding/head leaf hooks, verifies restored CPU
weights, performs CPU embedding lookup and explicitly transfers inputs_embeds
to the decoder. The head stays on CPU; the frozen-head loss transfers vocabulary
blocks. All target positions and vocabulary entries contribute. BF16 projection
uses FP32 logsumexp and backward product accumulation before the final cast.
This is known memory engineering, not a new learning objective or optimized CCE.

Training has a separate10.5GB complete-controller-tree RSS ceiling,1GB host
reserve and9GB available-RAM preflight. Sampling interval0.2s; a breach kills the
worker process group. GPU allocation/reservation and update RSS are also saved.
**These are training resources, not an8GB deployment-fit claim.** Deployment
must later satisfy the original6.4GB RSS cap in a separate inference experiment.

CPU checks cover offload hook restoration, original/explicit embedding agreement,
frozen heads under all-linear PEFT, checkpointed BF16 LoRA gradients, causal
label boundaries, numerical stability and full-vocabulary block gradients.
An end-to-end test exposed excessive error from BF16 rounding of each block's
partial backward product; the corrected FP32 accumulation passes its unchanged
tolerance. Failure logs and previous sources are preserved on SSD.

[CPU checks and source/log hashes](evidence/sas7b-offload-cpu-checks-01.json).
Actual7B CUDA loading/transfer/backward and measured fit remain unproven until a
terminal successful worker summary and complete controller memory trace exist.
A successful fit still requires full adaptation, conversion/application proof,
and paired QA before claiming SAS improvement. It cannot complete the research
goal or support an architecture comparison by itself.
