# Critic deployment gates

The critic epoch is separate from its deployment and quality evidence. Keep the
active trainer/corpus/base frozen. CPU inference must wait for training to finish.

1. Require a complete epoch, processed-example/update counts, finite validation
   loss and actual changed tensors; teacher-forced loss is not verification quality.
2. Convert to GGUF on SSD. Preserve purpose=critic and all training/conversion
   hashes. Fit adapters cannot qualify as trained systems.
3. Run reversible scale0→1→0 proof on one bound training-validation prompt, with
   the pinned3B deployment model and recorded memory. This proves application only.
4. Measure controlled discrimination and natural draft errors against matched
   unadapted binary-review and previous rich-review controls. Preserve initial
   draft identity, correct delivery, wrong delivery, withholding, token costs and
   full resident memory. Do not select a threshold from the reused development24.
5. Broaden to report-disjoint development and later a genuinely frozen confirmation
   protocol. Comparable SAS adaptation remains required for architecture claims.

Runtime options are explicit: --verifier-model3b --critic-protocol binary
--verifier-adapter <converted critic directory>. Actor --adapter is separate.
--weights-root may point to authorized SSD copies only when filenames, byte counts
and hashes match the pinned deployment checkpoints. Shared residency does not merge
instances with different adapter policies.

Binary UNKNOWN remains visible in records and fails the delivery gate. It supplies
no field/step localization. Binary mode therefore permits no repair or full
regeneration; patch/edge/endpoint modes are rejected. The old rich protocol stays
the default. No binary output is silently turned into per-field semantic labels.

Application proof now accepts --purpose critic --dataset <bound critic examples>
--model-path <identical pinned SSD3B GGUF>, with explicit MAS arm. Its source prompt
must come from the critic training-validation corpus, not a newly opened test set.
All new raw outputs stay SSD. Record exact CLI and hashes at launch; do not run
these gates before the preceding one actually passes.200 software tests pass;
real critic application and QA improvement remain unproven at this checkpoint.
