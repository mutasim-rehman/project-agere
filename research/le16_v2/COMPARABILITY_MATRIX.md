# Evidence regimes

| Dimension | Historical8 GB | Redeveloped8 GB FinQA | 16 GB FinQA |
| --- | --- | --- | --- |
| Task | Synthetic KYC/credit | Public train-source numerical QA | Public dev-source numerical QA |
| Unique questions | 175 test cases | 52 selection +49 reserved | 160 questions |
| Primary unit | Synthetic case/template | 15+15 company-year reports | 50 reports /36 companies |
| SAS | 7B Q4 | 7B Q4 + trained adapter | 14B Q4 pretrained |
| MAS | 1.5B+.5B+.5B F16 | Shared 3B Q4 role backbone + adapters | 1.5B+3B+.5B distinct F16 |
| Context | 2048 | 4096 | 4096 |
| Memory ceiling | 6.4GB | 6.4GB | 11.5 GB |
| Adaptation | Final naive baseline | Extensive development/adaptation | Pretrained both arms |
| Serving/backend | Earlier Windows study | Earlier native CPU backend | Portable AVX2 CPU backend |
| Causal RAM scaling comparison | No | No | No; recipes/question source differ |

The natural8 GB development inventory covers15 completed configurations,768 generated case outputs on 101 unique questions from 30 reports. The 16 GB study adds960 outputs on 160 unique questions from 50 different reports. The ID/report intersection is empty. These are1728 FinQA outputs but261 unique questions, with substantial repeated-condition dependence within each study. Adding historical synthetic paired outputs gives2078 core-ledger outputs on 436 distinct tasks/questions across unlike task regimes; that is NOT a valid pooled statistical N. Additional development, fitting, probe and external-control diagnostics are separate and are not counted as independent replications in that core ledger.

Within the 8 GB model-selection set, matched control SAS reports8/23/21 and control MAS 3/19/30; crossed SAS 10/16/26 and crossed MAS 3/15/34. On reserved49 questions, control SAS 8/20/21 versus MAS 4/17/28, and crossed SAS 9/20/20 versus MAS 4/9/36. The reported-correct ordering favors SAS in these observed pairs, but the magnitude cannot be read as a RAM effect or as independent replications across all variants.

The final reasoned8 GB secondary runs are also complete: original SAS 9/24/19, control9/20/23 and crossed9/10/33. Crossed preserves reported-correct deliveries while withholding more wrong answers; against control, raw correct falls11 to 10. The paired adoption gate across both metrics therefore still fails. The older8 GB statistical PDF predates these completed results and must not be treated as the final chronology.

The original8 GB empirical report used stronger language about legal necessity, universal capacity floors, Markov error cascades and causal mechanisms. Those claims are not carried forward as established facts. The raw synthetic summaries are rechecked here, while their unlike denominators/tasks and the absence of a factorial architecture experiment remain explicit. The 8 GB statistical PDF also relied on case-wise or unpaired tests in places; this dossier favors actual pairs and report/company dependence where data support it.
