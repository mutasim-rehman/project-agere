# Matched SAS continuation: training completed, QA pending

Both policies reload the SAME fully trained original joint7B adapter; fit updates
are discarded. Both complete64 updates on512 examples under the same optimizer,
base/runtime/task weighting and positive/rehearsal exposure.448 validation rows
are byte-identical. Counterfactual negative prompts are the intervention. Training
steps are matched; token counts differ slightly as previously disclosed.

| Recorded teacher-validation loss | Control | Crossed |
|---|---:|---:|
| Crossed critic192 rows |0.093800|0.030767|
| Mutation critic192 rows |0.009672|0.018942|
| Replay critic32 rows |0.004545|0.006232|
| Replay drafter32 rows |0.025758|0.022407|
| Weighted aggregate448 rows |0.033459|0.017700|

Family means are unweighted per-example means; aggregate applies existing task
weights (drafter2, critic2/3), not uniform averaging of the four displayed means.
The metadata audit recombines recorded means; it does not rerun model forwards.
Repeated positives across validation families and one training seed limit inference.
Lower token loss does not establish better verdict accuracy or natural QA.

Crossed critic examples also change the shared SAS drafter policy probabilities:
drafter data were held fixed, yet recorded drafter loss differs. This is consistent
with cross-task transfer, not proof of better generation, an intrinsic architecture
advantage or a novel principle. Unlike the fixed-actor MAS pair, SAS initial
answers may change; natural prefix/full-trajectory audits must separate those
changes from verification and repair effects.

Crossed worker summary/validation and final controller source checks are complete.
Independent audit replays64 ordered finite-gradient updates/512 examples and13013
memory samples: peak8,262,852,608 bytes under10.5GB TRAINING allowance; reserve kept.
All392 LoRA tensors change,20,185,088 trainable parameters. Saved adapter SHA
1cb77c6e8e5dc49d8c3156597a90c9f4f93010fd4f0e5822c8fe2f202be26c5c.
Full converted GGUF SHA b152ef4060570a8150cfb2f1f5af7bb8ffd915ff70c691ff22aef7a089d23c04
verified from bytes. Native deployment application proof is complete and independently
replayed: exit0, sampled tree RSS5,140,795,392 bytes below6.4GB, source and rendered
prompt checks preserved. The fixed52-case natural control SAS evaluation is running;
no completed natural SAS comparison is available yet.

No candidate method adopted, natural SAS improvement or first-use novelty claimed.
The fixed natural selection, original baseline, reserved audit and secondary prompt
checks remain required. Header-materialization prototype is not used in this study.

[Control evidence](evidence/matched-control-sas-complete-01.json) ·
[Crossed evidence](evidence/matched-crossed-sas-complete-01.json).


Natural control SAS is now complete and independently replayed; crossed SAS is
running. Control repair adds two wrong deliveries without a correct-delivery gain
versus its recorded no-repair prefix. This single condition does not establish a
paired training improvement. [Natural results](MATCHED_SAS_SELECTION.md).
