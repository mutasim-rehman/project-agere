"""Build consistent human-readable reports from checked derived statistics."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
D=json.loads((ROOT/'research/tier16_v2/data/statistical_analysis.json').read_text())
X=json.loads((ROOT/'research/le16_v2/data/cross_tier_analysis.json').read_text())
H=json.loads((ROOT/'research/le16_v2/data/historical_diagnostics.json').read_text())
S=D['summaries']; P=D['comparisons']['primary']['endpoints']
METRICS={'case_success':'Reported answer','raw_execution_match':'Raw execution'}


def pct(x):return f'{100*x:.2f}%'
def pp(x):return f'{100*x:+.2f}'
def ci(x):return f'[{100*x[0]:+.2f}, {100*x[1]:+.2f}]'
def triplet(s,m='case_success'):
    d=s['metrics'][m];return f"{d['correct']} / {d['wrong']} / {d['withheld']}"
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',
        *['| '+' | '.join(str(v) for v in row)+' |' for row in rows]])+'\n'
def fig(name,caption):return f'![{caption}](figures/tier16_v2/{name}.png)\n'
def save(name,text):
    text=re.sub(r'^(#{1,6})(?=[^#\s])',r'\1 ',text,flags=re.M)
    for old,new in [('16GB','16 GB'),('8GB','8 GB'),('32GB','32 GB'),('11.5GB','11.5 GB'),('12.5GB','12.5 GB'),('12.6GB','12.6 GB'),('1GB','1 GB'),('100MB','100 MB'),('44MB','44 MB'),('34MB','34 MB'),('30October','30 October'),('28-30 October','28-30 October')]:
        text=text.replace(old,new)
    text=re.sub(r'\b(The|the|Both|both|All|all|only|from|to|on|for|with|versus|about|same|first|and|within|over|under|at|of|has|delivers|Among|among|Trained|Shared|SAS|MAS)(?=\d)',r'\1 ',text)
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')
def summary_table():
    return table(['Profile / arm','Reported C / W / H','Raw C / W / H','Time (h)','Peak RSS (GB)'],[
        [profile.replace('_',' ')+' / '+arm.upper(),triplet(S['tier16-'+arm+'-'+profile]),triplet(S['tier16-'+arm+'-'+profile],'raw_execution_match'),
        f"{S['tier16-'+arm+'-'+profile]['inference_seconds']/3600:.3f}",f"{S['tier16-'+arm+'-'+profile]['peak_rss_bytes']/1e9:.3f}"]
        for profile in ['primary','direct_control','repair_ablation'] for arm in ['sas','mas']])


META='''**Analysis date:** 30 October 2026. **Evaluation period:** 28-30 October 2026.
**Study status:** completed accuracy audit with retained resource failures.
**Nominal tier:** 16 GB; **physical host:** approximately 15.44 decimal GB available to Linux.
**Application ceiling:** 11,500,000,000 bytes of sampled controller-plus-worker RSS.
**Unique question set:** 160 FinQA questions, 50 company-year reports, 36 companies.
**Repeated outputs:** 960 = 160 questions x 2 arms x 3 profiles; these are not 960 independent questions.
**32 GB:** not evaluated. **New neural calls for these documents:** zero.
'''

DESIGN='''The experiment compares complete deployment recipes on the same questions, not isolated architecture, precision or parameter-count factors. SAS uses pretrained Qwen2.5-14B-Instruct Q4_K_M. Resident MAS uses pretrained Qwen2.5-1.5B-Instruct F16 for extraction/source suggestion, 3B F16 for drafting, and 0.5B F16 for verification. All declared MAS model instances stay loaded; there is no role-backbone sharing. Both arms are pretrained: the 8 GB trained adapters are not compatible with the larger SAS checkpoint and are not reused.

Both arms use CPU inference, eight threads, greedy decoding, seed 42, context 4,096 per call, `use_mmap=False`, no GPU layers, the same public evidence packets, and a 2,048 generated-token ceiling per case across stages. Equal ceilings do not mean equal expenditure or equal FLOPs. Prompt-token totals sum all calls and may exceed a single context window. The public packet uses lexical top-eight source-unit retrieval; MAS has the existing source-suggestion stage. Internal prompts/call counts therefore differ.

The primary profile uses the existing 128-token analysis allowance and two fixed training demonstrations, binary review, and no repair. Direct-control removes both analysis and demonstrations. Repair-ablation keeps primary prompting and adds the existing repair/review policy. These are bundled profile contrasts; they do not isolate demonstrations from analysis. No new source catalog, header materialization, adaptive repair method, training or routing was adopted for this evaluation.

All 50 reports were selected by fixed ID hash, excluding recorded earlier development/report exposure; all questions in a chosen report were retained. Scoring annotations were kept separate from sealed public packets. These are public FinQA development-source reports, not the official test split, bank client files, or a guarantee against model pretraining contamination. All output cases remain in denominators, including insufficient answers and withheld outputs.
'''

ENDPOINTS='''For each numerical metric, C means a correct delivered answer, W a wrong delivered answer, and H a withheld answer. Candidate correctness is not delivery: a correct candidate can be withheld. Coverage is (C+W)/N; conditional precision is C/(C+W). A system that withholds everything has zero wrong deliveries and zero useful answers.

The reported-answer metric uses the existing declared-unit normalization and rounding tolerance against `qa.answer`. The raw-execution metric uses the existing relative/absolute tolerance against `qa.exe_ans`, without reported-answer normalization. Neither is an official FinQA program-equivalence implementation. They assess related but different numerical conventions; neither is chosen after seeing which favors an arm. Source-supported execution means the deterministic operand/program checks passed, not that the final answer is financially correct.
'''

RESOURCE='''The application ceiling is 11.5 GB, including the controller. The separate 1 GB host reserve is not additional application usage; recovery adds a 100 MB launch cushion. The earlier 12.49 GB attempt stopped at a reserve check before model inference. Subsequent 8,192-context engineering probes encountered process swap, so the common context was reduced to 4,096 for both arms and tiers before the higher-tier accuracy run. Model weights and precision did not change.

The first SAS primary attempt stopped after 145 completed cases on 44,011,520 bytes of process-tree swap, while sampled peak RSS was 10,056,552,448 bytes. The first continuation later stopped after seven direct-control SAS cases on 34,430,976 swap bytes, with sampled peak RSS 10,039,861,248 bytes. Every reused checkpoint preceded the first invalid sample; the original 145 cases also passed full vocabulary-only prompt, program, score, delivery and token-ledger replay before reuse. No completed cases were selected by quality.

Both complete primary jobs and seven direct-control cases were retained in the final continuation (327 saved outputs at that point). Whole failed attempts remain in hashed provenance, while derived pre-breach prefixes are explicitly labelled as non-independent evidence. The final continuation ran in a user-systemd service with kernel `memory.swap.max=0`; global swap/swappiness settings were unchanged. This prevents research processes from swapping prospectively, but cannot retroactively erase the two earlier failures.

All six final jobs completed and the saved-response audit and export succeeded. The correct status is `complete_accuracy_audited_resource_invalid`, with `uninterrupted_no_swap_deployment_pass=false`. RSS enforcement samples every 0.2 seconds and is not a hard cgroup RSS bound. Passing engineering probes or later clean segments does not establish worst-case memory behavior, absence of between-sample peaks, or an uninterrupted product deployment pass.
'''

METHODS='''The prespecified primary comparison is the 16 GB primary-profile SAS/MAS pair. Endpoints were specified before evaluation; this extended statistical analysis, its extra tests and multiplicity grouping were written after inspecting results and are supplemental/post hoc. Secondary profiles and older experiments do not become additional chances to declare a favorable primary result.

Primary intervals resample all 50 company-year reports with replacement, retaining every question in each sampled report. The estimator remains question-weighted; sampled denominators vary with report sizes. We use 10,000 draws, NumPy `default_rng(42)`, and linear percentile quantiles. The original audit used Python `random.Random(42)` and different quantile indexing; its exact original JSON is retained. Small numerical interval differences are implementation differences, not different outcomes.

Company-level sensitivity resamples 36 companies, preserving their reports. We also report equal-report estimates and leave-one-report-out ranges. These checks address dependence/weighting sensitivity but cannot establish independence across firms or representative sampling. The ID-hash report selection is not a randomized architecture intervention.

Supplemental cluster sign-flip tests use independent cluster contributions and require sign-exchangeability/symmetry under the null. Nonzero cluster signs are enumerated exactly when at most 18 are present; otherwise 65,536 Monte Carlo sign assignments use seed 42 and p=(extreme+1)/(draws+1). These are not design-randomization causal p-values. At the Monte Carlo floor, p is not zero or infinitely precise. Case-IID exact McNemar results are included only as sensitivity diagnostics; they ignore report dependence.

Holm adjustment is applied to the four primary correct/wrong contrasts across the two metrics. Withholding is determined by the accounting identity and is not a fifth independent endpoint. Secondary tests are labelled exploratory/unadjusted. Bonferroni-style 98.75% bootstrap intervals are also provided for the four primary endpoints; their coverage remains approximate because bootstrap assumptions remain necessary.

Nonsignificance is not evidence of equality. No practical equivalence margin was prespecified, so no TOST/equivalence or noninferiority pass is declared. Zero-event bootstrap degeneracy is not population certainty. Precision comparisons condition on different selected delivery sets and are not interchangeable with matched unconditional accuracy comparisons. No post-hoc observed-power claim is used.
'''


def primary_table():
    result=[]
    for metric in METRICS:
        for event in ['correct','wrong','withheld']:
            e=P[metric+'/'+event]
            result.append([METRICS[metric]+' / '+event,pp(e['delta_rate']),ci(e['bootstrap95']),
                ci(e['company_sensitivity']['bootstrap95']),f"{e.get('holm_primary_family4_p',float('nan')):.6f}" if 'holm_primary_family4_p' in e else 'not independent test'])
    return table(['Endpoint','MAS-SAS (pp)','Report 95% CI (pp)','Company 95% CI (pp)','Holm p (4)'],result)


def cost_table():
    values=[]
    for arm in ['sas','mas']:
        s=S['tier16-'+arm+'-primary'];m=s['metrics']['case_success']
        values.append([arm.upper(),f"{s['inference_seconds']/160:.2f}",f"{s['inference_seconds']/m['correct']:.2f}",
            f"{s['generated_tokens']/160:.2f}",f"{s['prompt_tokens']/160:.2f}",f"{s['peak_rss_bytes']/1e9:.3f}",pct(m['precision_when_delivered'])])
    return table(['Arm','Seconds/case','Seconds/reported correct','Generated/case','Prompt/case','Peak GB','Reported precision'],values)


def funnel_table():
    values=[]
    for arm in ['sas','mas']:
        s=S['tier16-'+arm+'-primary'];m=s['metrics']['case_success']
        values.append([arm.upper(),m['valid_candidates'],m['correct_candidates'],m['correct'],m['wrong'],m['correct_candidates_withheld'],m['wrong_candidates_withheld'],m['invalid_or_insufficient_withheld']])
    return table(['Arm','Executable','Correct candidate','C delivered','W delivered','Correct withheld','Wrong withheld','Invalid withheld'],values)


def paired_secondary():
    result=[]
    for label in ['sas-reasoned_vs_direct','mas-reasoned_vs_direct','sas-repair_vs_primary','mas-repair_vs_primary']:
        d=D['comparisons'][label]
        for metric in METRICS:
            c,w=d['endpoints'][metric+'/correct'],d['endpoints'][metric+'/wrong']
            result.append([label.replace('_',' '),METRICS[metric],c['delta_count'],w['delta_count'],ci(c['bootstrap95']),ci(w['bootstrap95'])])
    return table(['Contrast (right-left)','Metric','Delta C','Delta W','C 95% CI (pp)','W 95% CI (pp)'],result)


def t8_table():
    result=[]
    for name,s in X['tier8_natural'].items():
        short=name.replace('model_selection-','Selection: ').replace('diagnostic_audit-','Reserved: ').replace('-full-01','').replace('_',' ')
        result.append([short,s['n'],triplet(s),triplet(s,'raw_execution_match'),f"{s['peak_rss_bytes']/1e9:.3f}"])
    return table(['8 GB condition','N','Reported C / W / H','Raw C / W / H','Peak GB'],result)


def historical_diagnostics():
    adaptation=H['finqa-mas-3b-adaptation-dev24-paired-01.json']['data']
    critic=H['critic3b-natural24-delivery-results-01.json']['data']['metrics']['case_success']['conditions']
    shared=H['shared3b-serving-parity-complete-01.json']['data']['phase_memory_maxima']
    external=H['external-baselines-completed-01.json']['data']['tasks']
    return table(['Supporting study','Cohort','Observed result','Interpretation limit'],[
        ['3B actor adaptation','24 development',f"+{adaptation['paired']['right_only_correct']} correct candidates; delivered0/0/24 to10/11/3",'Known QLoRA baseline improvement; not11 delivered correct'],
        ['Trained3B critic','24 natural /23 reports',f"C {critic['plain']['correct_delivered']} to{critic['adapted']['correct_delivered']}; W {critic['plain']['incorrect_delivered']} to{critic['adapted']['incorrect_delivered']}",'Same11 correct candidates; coverage/error trade-off'],
        ['Shared3B role serving','2 prompts /4 switches',f"RSS {shared['distinct']/1e9:.3f} to{shared['shared']/1e9:.3f}GB; observed logit delta0",'Small equivalence probe, not full-QA equivalence or novelty'],
        ['Header / catalog fitting','73 fitting cases','Mappable41 to45; same4 recovered cases','No neural QA-gain measurement; excluded16GB'],
        ['MortarBench','90 questions /9 groups',f"SAS{external['mortar']['conditions']['sas']['exact_matches']} vs MAS{external['mortar']['conditions']['mas']['exact_matches']} exact",'Different workflow/metric; no pooled FinQA score'],
        ['Later FRAMES control','100 questions',f"SAS{external['frames']['conditions']['sas']['exact_matches']} vs MAS{external['frames']['conditions']['mas']['exact_matches']} exact",'Near-floor control; not causal proof of failure mechanism']])


REFERENCES='''## References and source hierarchy

- [R1] Chen et al. (2021), [FinQA: A Dataset of Numerical Reasoning over Financial Data](https://aclanthology.org/2021.emnlp-main.300/). Benchmark source; the project uses disclosed custom subsets and scoring conventions.
- [R2] Cameron and Miller (2015), [A Practitioner's Guide to Cluster-Robust Inference](https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf). Dependence-aware inference background.
- [R3] American Statistical Association (2016), [Statement on statistical significance and p-values](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf). Interpret estimates and assumptions rather than a p-value threshold alone.
- [R4] Lakens (2017), [Equivalence Tests: A Practical Primer](https://doi.org/10.1177/1948550617697177). Equivalence requires an explicit margin and suitable design, not a nonsignificant difference.
- [R5] El-Yaniv and Wiener (2010), [On the Foundations of Noise-free Selective Classification](https://jmlr.org/papers/v11/el-yaniv10a.html). Risk/coverage and rejection are established ideas, not a new algorithm here.
- [R6] Holm (1979), [A Simple Sequentially Rejective Multiple Test Procedure](https://www.ime.usp.br/~abe/lista/pdf4R8xPVzCnX.pdf). Multiple-test control background.
- [R7] Hoeffding (1963), [Probability Inequalities for Sums of Bounded Random Variables](https://www.tandfonline.com/doi/abs/10.1080/01621459.1963.10500830). Independent bounded-cluster inequality background.
- [L1] Authoritative 16 GB audit: `AGERE/runs/lab_tiers_v1/lab-16-115gb-recovery-02/analysis/summary.json`; unchanged copy in `research/tier16_v2/evidence/original_audited_summary.json`.
- [L2] Final derived analysis: `research/tier16_v2/data/statistical_analysis.json`; file hashes and archive checksum in `research/tier16_v2/evidence/input_provenance.json`.
- [L3] Latest 8 GB natural runs: `AGERE/runs/tier8_method_qa/`; matched-study paired audits and secondary closure under `AGERE/runs/tier8_matched_continuation/` and `AGERE/runs/lab_handoff/closure-v1/`.
- [L4] Historical references: `TIER_8_RESEARCH_REPORT.md` and `TIER_8_V2_STATISTICAL_EVALUATION_REPORT.pdf`, retained unchanged. Their earlier snapshots and stronger interpretations do not supersede later raw evidence.
'''

LIMITS='''Only one model family, one fixed greedy recipe and one financial numerical benchmark are evaluated at 16 GB. The public development-source sample is report-held-out relative to recorded project exposure, not a clean pretraining holdout or the official FinQA test set. Equal memory/token ceilings do not match actual compute, prompt context, role allocation, training effort or latency.

MAS and SAS differ jointly in model size, precision, number of roles and internal prompts. The 8 GB redevelopment also differs in adaptation, serving mode, question source and CPU backend. Its deployment-budget label does not establish that adaptation training ran on a physically8GB host. Neither arm is established as the best possible system under its memory ceiling. Consequently neither the 16 GB recipe contrast nor the cross-tier inventory identifies a universal architecture law, a pure precision effect or a causal RAM-scaling slope.

The resource history contains two swap failures; recovered accuracy evidence cannot certify an uninterrupted no-swap product. No bank-client, KYC mismatch or regulatory-safety endpoint is measured in the 16 GB FinQA study. The older synthetic tests do not establish real-world regulatory readiness either. The analysis is not legal or deployment certification.

The added tests, strata, cost sensitivities and theoretical framing are post hoc. They cannot manufacture a new algorithmic contribution or prove population equivalence. Some analytical intervals require independent reports/companies, and deterministic report selection limits design-based generalization. Theoretical results below are conditional mathematical statements about the formalized quantities, not proofs of empirical MAS inferiority.
'''

THEORY='''## Formal framework and conditional propositions

The following identities and bounds are elementary/established tools applied to the audit. They are not claimed as novel theorems. Each proposition states its assumptions; none proves an architecture universally better.

### Proposition 1: endpoint accounting and rejection confounding

For one fixed metric, every case has exactly one delivery state C, W or H.

```text
C + W + H = N
Delta(C/N) + Delta(W/N) + Delta(H/N) = 0
```

Proof: sum the mutually exclusive per-case indicator identities. Therefore fewer wrong deliveries can be achieved simply by withholding more; it is not by itself an improvement in useful correctness. Always-withhold has C=W=0 and H=N. This also explains why withholding is not an independent additional primary test.

### Proposition 2: fixed-candidate gating upper bound

Assume the review gate can accept/reject a fixed candidate but cannot change its answer. Let A be the set of valid correct candidates and D the delivered set.

```text
C_gate = |A intersect D| <= |A|
```

Proof: A intersect D is a subset of A. On the primary 16 GB candidates, MAS has five reported-correct candidates, so any accept/reject-only gate on those SAME candidates can deliver at most 5/160 correct answers. SAS actually delivers 78/160. A better gate alone cannot bridge that fixed-candidate gap. This bound does not apply to a newly trained generator, expanded evidence representation or new candidate-generating method.

### Proposition 3: candidate-production and acceptance decomposition

Let q be the executable-candidate fraction, p correctness conditional on execution validity, a gate acceptance among correct executable candidates, and b acceptance among wrong executable candidates. All are defined on the same fixed metric/cohort.

```text
C/N = q * p * a
W/N = q * (1-p) * b
H/N = 1 - C/N - W/N
```

Proof: apply the conditional-probability chain rule to validity, correctness and acceptance. Independence between stages is NOT assumed. Empirical primary reported values are SAS q=.9375, p=.56, a=78/84, b=48/66; MAS q=.0625, p=.5, a=1, b=.6. Substitution exactly recovers 78/160, 48/160, 5/160 and 3/160. The MAS binding observed factor is executable-candidate production. Completeness of annotated retrieval does not guarantee that the compact operand catalog can express the reference solution, so this is not proof of generator incapacity alone.

### Proposition 4: utility switch points are preferences, not discovered safety thresholds

Normalize a correct delivery to benefit 1, a wrong delivery to cost lambda >= 0, and withholding to 0. This is an illustrative utility model, not a prespecified institutional loss.

```text
U(lambda) = (C - lambda*W) / N
U_SAS - U_MAS (reported primary) = (73 - 45*lambda)/160
Switch: lambda = 73/45 = 1.6222...
U_SAS - U_MAS (raw primary) = (33 - 85*lambda)/160
Switch: lambda = 33/85 = 0.3882...
```

Proof: subtract the two observed linear utilities and solve for zero. Always-withhold must remain a competitor. Under the reported metric, MAS has positive utility only for lambda < 5/3; its primary advantage over SAS occurs only above 73/45, a narrow interval before both can be beaten by withholding. Under raw execution the preference interval differs markedly. Choosing lambda after observing these outcomes would be post-hoc preference fitting, not scientific superiority.

If withholding requires human work, introduce a nonnegative cost kappa per withheld case. The utility becomes (C-lambda*W-kappa*H)/N. Subtracting observed primary counts gives a reported switch (73+118*kappa)/45 and raw switch (33+118*kappa)/85. Always-withhold then has utility -kappa, not zero. This extension shows why the free-withholding assumption matters; neither kappa nor lambda is estimated or optimized from these data.

### Proposition 5: repair break-even and observed dominance

```text
SAS repair - primary, reported utility = (1 - 2*lambda)/160
SAS repair - primary, raw utility = -3*lambda/160
MAS repair - primary, both delivery utilities = 0
```

Proof: substitute the exact paired delivery-count changes. With a nonnegative extra compute cost, SAS repair has an even stricter break-even condition; raw utility never improves for positive lambda. MAS repair adds compute while preserving all 160 delivery states exactly in this run. This is observed sample dominance under this utility/cost convention, not a population impossibility theorem for repair.

### Proposition 6: what memory arithmetic can and cannot prove

Assume genuinely distinct, fully resident weight tensors without aliasing or compressed/swap representations. If tensor j uses n_j scalar elements and b_j effective storage bits per element, then its storage contributes at least n_j*b_j/8 bytes, before KV caches, runtime buffers and controller memory.

```text
M_total >= sum_j(n_j*b_j/8) + M_KV + M_other
M_shared_roles counts a genuinely shared tensor allocation only once
```

Proof: add nonoverlapping resident allocations and nonnegative overhead. Quantized block scales and mixed tensor formats must be included in effective storage bits. GGUF file size is a disk proxy, not an exact RSS decomposition or exact tensor-only lower bound. In this run the model files total about8.99GB for SAS and10.27GB for MAS, while observed primary RSS is10.06GB and10.93GB. Fewer total nominal parameters do not guarantee less resident memory when precision differs.

### Proposition 7: bounded independent-cluster uncertainty

Let independent report contributions D_g lie in [-1,1], with fixed nonnegative weights w_g summing to1. For the weighted contrast, the bounded-difference/Hoeffding argument gives:

```text
Pr(|sum_g w_g*(D_g-E[D_g])| >= e)
  <= 2 * exp(-e^2 / (2*sum_g w_g^2))
e_(alpha,m) = sqrt(2*sum_g w_g^2 * log(2*m/alpha))
G_effective = 1 / sum_g w_g^2
```

Proof: each weighted centered independent variable has range length2*w_g. Hoeffding's lemma bounds the moment-generating function by exp(t*t*w_g*w_g/2). Independence allows multiplication across clusters; exponential Markov then gives:

```text
E exp(t*S) <= exp(t*t*sum(w_g*w_g)/2)
Pr(S >= e) <= inf_(t>0) exp(-t*e+t*t*sum(w_g*w_g)/2)
t_opt = e/sum(w_g*w_g)
```

Substitution, a two-tail bound and a union bound over m contrasts yield the displayed result. For question weighting, w_g=n_g/N. This distribution-free bound is often much wider than the fitted bootstrap. It requires independent clusters and fixed weights; deterministic report selection does not by itself justify a population-sampling guarantee. It is not an unconditional certificate for this deployment.

### Proposition 8: metric disagreement accounting

Let R-only be deliveries correct only under reported scoring and E-only deliveries correct only under raw execution.

```text
C_reported - C_raw = R_only - E_only
abs(C_reported-C_raw) <= R_only + E_only
```

Proof: concordant cases cancel when subtracting correctness indicators. For primary SAS, R-only=44 and E-only=4, giving 78-38=40 and 40<=48. The two metrics are not independent replications and cannot be interchanged without changing the estimand.

### Nonidentification and error-cascade cautions

A cross-tier regression cannot isolate a RAM effect when RAM, checkpoint size, adaptation, serving mode, profile and question source change together. With only those observed deployment configurations, multiple response functions with different RAM coefficients reproduce the same outcomes. More rows generated by reusing the same configuration/questions do not remove that confounding.

Likewise a pure Markov bottleneck or data-processing argument needs the downstream agent to receive information only through the proposed handoff. Our pipeline also exposes source evidence, so that assumption is not established. A product of unconditional stage success rates would additionally assume independence. We do not use either shortcut to claim a proven capacity floor or universal MAS error cascade.
'''

_bound=P['case_success/correct']
THEORY=THEORY.replace('### Proposition 8:',f'''Numerical check: the50-report question-weighted design has effective cluster count{_bound['effective_clusters_for_bounded_weights']:.2f}. The single-contrast95% bounded half-width is{100*_bound['bounded_difference_halfwidth95']:.2f} percentage points; the four-contrast bound is{100*_bound['bounded_difference_halfwidth95_family4']:.2f} points. Company grouping has effective count{_bound['company_sensitivity']['effective_clusters_for_bounded_weights']:.2f}, despite36 named companies. These conservative bounds show how much precision relies on stronger resampling assumptions.

### Proposition 8:''')


def build():
    main_results=summary_table()
    primary=primary_table()
    costs=cost_table()
    funnel=funnel_table()
    secondary=paired_secondary()
    concordance=table(['Delivered SAS primary','Raw correct','Raw incorrect','Total'],[
        ['Reported correct',34,44,78],['Reported incorrect',4,44,48],['Total',38,88,126]])
    details='''The primary reported-answer contrast is MAS minus SAS: -73 correct deliveries (-45.625 percentage points), -45 wrong deliveries (-28.125 points), and +118 withholdings (+73.75 points). Raw execution gives -33 correct, -85 wrong, and the same +118 withholdings. Both metrics therefore show a correctness-versus-withholding trade-off, not MAS Pareto superiority.

Conditional precision among delivered primary answers is 61.90% for SAS (78/126) and 62.50% for MAS (5/8) under reported scoring. Similar conditional precision conceals radically different coverage: 78.75% versus5.00%. Under raw execution precision is30.16% for SAS and62.50% for MAS, again over different selected delivery sets. A small selected denominator is not evidence that MAS solves most questions more reliably.
'''
    mechanism='''All160 initial program-stage responses parse as JSON objects in both primary recipes. SAS emits150 ANSWER and10 INSUFFICIENT decisions; MAS emits10 ANSWER and150 INSUFFICIENT decisions. This is program-stage syntax, not the same whole-workflow metric as the older synthetic report. The known grammar constraint addresses format; it does not ensure useful semantic/program coverage.

Primary SAS produces150 executable candidates, of which84 are reported-correct; review delivers78 correct and48 wrong, withholding6 correct candidates and18 executable wrong ones, in addition to10 invalid/insufficient outputs. MAS produces10 executable candidates,5 correct; it delivers all5 correct and3 wrong, withholding2 wrong and150 invalid/insufficient outputs. Its final low coverage is therefore not primarily a gate that rejects many correct drafts.

All annotated gold evidence is present in the public retrieval packet on138/160 questions. Within that stratum SAS delivers74 correct and has3 invalid/insufficient outputs; MAS delivers5 correct and has128 invalid/insufficient outputs. Among22 incomplete-retrieval questions, SAS delivers4 correct and MAS0. These are post-hoc reference-dependent diagnostics, not deployment routing features or causal evidence. Gold retrieval completeness does not certify reference-program expressibility in the compact catalog.

The analysis stage reaches its intentional128-token limit on159 SAS and157 MAS primary cases. These events must not be described as malformed final JSON or context failure: the audited structured generation continues afterward. The summaries record zero context/budget-skipped calls across these six jobs. A smaller context can still change reasoning quality, which this single-context study cannot estimate independently.
'''
    repair='''The reasoned profile changes both analysis allowance and demonstrations together. Relative to direct control, SAS gains28 reported correct deliveries and avoids18 wrong ones; raw execution gains24 correct and avoids14 wrong. MAS gains5 correct and avoids2 wrong under both metrics. These are actual matched profile contrasts, not proof that either component alone causes the change.

Primary and repair-ablation have identical initial answer, execution, score, verdict and plan on all160 matched cases in both arms. SAS repair adds one reported-correct and two wrong deliveries by releasing previously withheld cases. Under raw execution it adds zero correct and three wrong deliveries. MAS attempts152 repairs yet every final delivery state remains identical to primary; source-supported candidate programs fall from10 to8 without a delivered-answer gain.

SAS repair adds about1.95 inference hours; MAS adds about1.25 hours. Extra compute is a measured cost, not a benefit or a novel mechanism. The no-repair primary was specified before this complete comparison; it was not selected afterward as the best-looking profile.
'''
    metric='''The primary SAS delivered-answer concordance has34 correct under both metrics,44 reported-only correct,4 raw-only correct and44 wrong under both. Thus48/126 deliveries change correctness label across metrics. Primary MAS has5 correct under both and3 wrong under both. The reported-versus-raw difference is not simply a subset relation.

For example, `AAPL/2005/page_83.pdf-1` yields26.6667 with declared unit number, matching the rounded reference answer26.7 but not raw `exe_ans=0.26667`. This illustrates source numerical-convention differences; it does not license relabelling all disagreements as model errors or all as annotation defects. All48 disagreeing cases are exported in `metric_disagreements.csv`. Neither score is labelled official FinQA program equivalence.
'''
    economics='''SAS uses more inference time per case, but its larger number of useful answers changes the economics. Primary MAS is about4.75 times faster per case, yet requires roughly3.29 times as much inference time per reported-correct delivery. MAS also uses more primary peak RSS despite fewer nominal parameters:10.93GB versus10.06GB. The observed memory ordering is compatible with precision/storage trade-offs, not a general theorem that one architecture always uses more memory.

Stage-inference seconds cover committed-case calls and exclude loading, waiting and uncheckpointed/retried work. Across all six jobs they sum to roughly37.24 hours. The last service alone ran a shorter wall-clock interval because it reused327 completed outputs; do not present that service duration as the entire experiment cost. Prompt tokens include repeated evidence across calls, and actual generated-token expenditure differs below the shared ceiling.
'''
    decision='''The prespecified goal that resident MAS should reduce wrong delivery without losing correct delivery is not supported by the primary16GB result. Correct-delivery intervals favor SAS under both scoring conventions, while wrong-delivery counts favor a much more withholding MAS. This does not prove universal SAS superiority, accept a global null, establish equivalence, or validate regulatory safety.

The useful research contribution is a reproducible comparison of constrained deployment recipes, a coverage-aware interpretation, candidate/gate decomposition, metric-convention sensitivity and an honest repair/resource audit. No newly invented inference algorithm or globally novel feature is established. Engineering resumability, checksums and process-swap prevention support the measurement; they are not themselves evidence of algorithmic originality.
'''
    repro='''Raw source authority is the immutable SSD run and its checksum-protected result archive. Derived case/report/paired tables are committed separately for analysis; no model weights, private tokens or training environment are copied into the documentation package. The final audit replay reconstructs prompts, programs, delivery decisions, scores and token ledgers from saved model responses. These reports introduce no new generation, training, thresholds, case exclusions or metric changes.

Run the reproducible scripts with a Python environment containing NumPy and ReportLab; the existing bundled desktop runtime supplies both. The analysis script verifies the final audit's input hashes and export checksum before recomputing endpoints. Rendering is a separate presentation step. See `research/tier16_v2/REPRODUCIBILITY.md` for exact commands and artifact maps.
'''
    body16=f'''# Project Agere: 16 GB empirical research report

## Spend It Together or Spend It Big? A resource-qualified deployment comparison

{META}
## Executive summary

The primary14B Q4 monolith delivers78 correct reported answers out of160, versus5 for the resident F16 specialist team. MAS reduces wrong deliveries from48 to3 largely through withholding152 cases. Both recipes fit sampled11.5GB RSS, but two historical swap failures invalidate an uninterrupted no-swap deployment claim. The completed accuracy evidence and all recovery provenance are retained.

{details}
## 1. Research question and experimental design

{DESIGN}
## 2. Outcome definitions and denominator discipline

{ENDPOINTS}
## 3. Complete results across all profiles

{main_results}
{fig('01_outcome_profiles','All six16GB jobs: correct, wrong and withheld reported answers. Each bar represents the same160 questions.')}
## 4. Primary paired statistical assessment

{primary}
{fig('02_primary_effects','Primary MAS-minus-SAS effects with report-cluster95% and supplemental98.75% intervals. Negative correct differences favor SAS; negative wrong differences favor MAS.')}
The four supplemental sign-flip p-values hit the65,536-draw resolution floor; Holm-adjusted values are about0.000061. These depend on symmetry/cluster assumptions and are not exact causal probabilities. Correctness and wrong-delivery contrasts point in opposite operational directions; a small p-value cannot resolve that preference trade-off.

## 5. Where useful answers are lost

{funnel}
{mechanism}
{fig('03_candidate_funnel','Fixed-candidate production and delivery. This is a descriptive process decomposition, not an architecture-capacity theorem.')}
{fig('10_retrieval_strata','Correct delivery by annotated retrieval stratum. Reference-dependent and post hoc; no cases excluded.')}
## 6. Prompt-profile and repair ablations

{secondary}
{repair}
{fig('06_repair_cost','Extra repair work relative to primary, despite zero MAS outcome change and a SAS correctness/error trade-off.')}
## 7. Scoring-convention audit

{concordance}
{metric}
{fig('04_metric_concordance','Concordance of the two scoring conventions among delivered primary answers. Different denominators are explicit.')}
## 8. Memory, latency and useful-answer economics

{costs}
{economics}
{fig('05_cost_ratios','Primary MAS/SAS resource and utility-cost ratios. SAS equals1; actual values are in the accompanying table.')}
## 9. Resource validity and recovery chronology

{RESOURCE}
## 10. Hypothesis decisions and contribution

{decision}
## 11. Statistical methods and sensitivity

{METHODS}
## 12. Limitations and responsible scope

{LIMITS}
## 13. Reproducibility and retained evidence

{repro}
{REFERENCES}
'''
    save('TIER_16_RESEARCH_REPORT.md',body16)
    crossmatrix=table(['Dimension','Historical8GB','Redeveloped8GB FinQA','16GB FinQA'],[
        ['Task','Synthetic KYC/credit','Public train-source numerical QA','Public dev-source numerical QA'],
        ['Unique questions','175 test cases','52 selection +49 reserved','160 questions'],
        ['Primary unit','Synthetic case/template','15+15 company-year reports','50 reports /36 companies'],
        ['SAS','7B Q4','7B Q4 + trained adapter','14B Q4 pretrained'],
        ['MAS','1.5B+.5B+.5B F16','Shared3B Q4 role backbone + adapters','1.5B+3B+.5B distinct F16'],
        ['Context','2048','4096','4096'],['Memory ceiling','6.4GB','6.4GB','11.5GB'],
        ['Adaptation','Final naive baseline','Extensive development/adaptation','Pretrained both arms'],
        ['Serving/backend','Earlier Windows study','Earlier native CPU backend','Portable AVX2 CPU backend'],
        ['Causal RAM scaling comparison','No','No','No; recipes/question source differ']])
    legacy=table(['Historical synthetic test','SAS','MAS','Qualification'],[
        ['Valid JSON','175/175','111/175','Different from FinQA numerical correctness'],
        ['Complete claim-set invention','125/175','89/111','MAS denominator excludes64 malformed outputs'],
        ['Citation grounding',pct(X['legacy8_synthetic']['sas']['grounding_accuracy']),pct(X['legacy8_synthetic']['mas']['grounding_accuracy']),'Claim-level metric; not answer accuracy'],
        ['Mismatch recall','0/20','0/20','Planted synthetic positives; not population equivalence'],
        ['Peak RSS GB','5.030','5.540','Nominal8GB resource setting; not physical8GB validation here']])
    crossdiscussion='''The natural8GB development inventory covers15 completed configurations,768 generated case outputs on101 unique questions from30 reports. The16GB study adds960 outputs on160 unique questions from50 different reports. The ID/report intersection is empty. These are1728 FinQA outputs but261 unique questions, with substantial repeated-condition dependence within each study. Adding historical synthetic paired outputs gives2078 core-ledger outputs on436 distinct tasks/questions across unlike task regimes; that is NOT a valid pooled statistical N. Additional development, fitting, probe and external-control diagnostics are separate and are not counted as independent replications in that core ledger.

Within the8GB model-selection set, matched control SAS reports8/23/21 and control MAS3/19/30; crossed SAS10/16/26 and crossed MAS3/15/34. On reserved49 questions, control SAS8/20/21 versus MAS4/17/28, and crossed SAS9/20/20 versus MAS4/9/36. The reported-correct ordering favors SAS in these observed pairs, but the magnitude cannot be read as a RAM effect or as independent replications across all variants.

The final reasoned8GB secondary runs are also complete: original SAS9/24/19, control9/20/23 and crossed9/10/33. Crossed preserves reported-correct deliveries while withholding more wrong answers; against control, raw correct falls11 to10. The paired adoption gate across both metrics therefore still fails. The older8GB statistical PDF predates these completed results and must not be treated as the final chronology.

The original8GB empirical report used stronger language about legal necessity, universal capacity floors, Markov error cascades and causal mechanisms. Those claims are not carried forward as established facts. The raw synthetic summaries are rechecked here, while their unlike denominators/tasks and the absence of a factorial architecture experiment remain explicit. The8GB statistical PDF also relied on case-wise or unpaired tests in places; this dossier favors actual pairs and report/company dependence where data support it.
'''
    readiness='''A <=16GB manuscript can be drafted without32GB if its claim is narrowed to the completed constrained deployment recipes and the documented development history. A third nominal tier is not logically required to report a reproducible negative/trade-off result. However, this package is a pre-paper research dossier, not a guarantee of acceptance or proof of a new algorithm.

The strongest defensible claims are: the tested16GB SAS recipe delivers substantially more correct answers than the tested resident F16 MAS recipe; MAS's lower wrong count accompanies95% withholding; the observed MAS bottleneck is candidate production under this representation/profile; and this repair policy adds cost without a Pareto improvement. The candidate-only gate bound is exact for these fixed candidates. The wider architecture/precision/RAM conclusions remain unestablished.

Before claiming a clean product deployment, rerun the frozen primary pair from beginning to end under the same prospective no-swap service control, retaining the11.5GB ceiling, both metrics and all cases. No new method is required. For broader scientific claims, external report/benchmark or model-family replication and independent annotation/scoring review are more informative than retrospective significance hunting. Repeating a seed under deterministic greedy decoding is not an independent random replicate.

If32GB is unavailable, do not invent its results or extrapolate a scaling curve from these confounded tiers. Present the unmeasured32GB matrix as planned future work. Keep all failed resource attempts in the appendix, and keep theory conditional. A credible contribution may be empirical measurement and diagnosis; algorithmic novelty has not been demonstrated.
'''
    combined=f'''# Project Agere: research dossier for deployments at or below16GB

## Pre-paper draft: selective answering, memory allocation and failure-aware evidence

**Date:**30October2026. **Status:** empirical/pre-paper synthesis, not a submitted or accepted paper.
**Scope:** historical nominal8GB experiments and completed11.5GB-RSS16GB deployment recipes.32GB is unmeasured.

## Draft abstract

We study whether limited local inference memory is more usefully allocated to a larger quantized monolith or resident full-precision specialists. A completed16GB-tier evaluation uses160 financial numerical questions from50 reports and36 companies, under an11.5GB process-tree RSS ceiling and2048-token generation ceiling. The primary14B Q4 monolith delivers78 correct and48 wrong reported answers, while the resident1.5B/3B/0.5B F16 team delivers5 correct and3 wrong and withholds152. The raw execution metric yields38 versus5 correct deliveries, showing why unit/rounding conventions must remain explicit. Report- and company-cluster estimates support a large correctness/coverage trade-off for these recipes. Fixed-candidate decomposition locates the MAS bottleneck before final review: only10 executable candidates are produced. Repair adds no MAS delivery improvement and trades one extra SAS reported-correct answer for two extra wrong deliveries. Two swap failures require a qualified accuracy continuation; all checkpoints, failed attempts, replayed traces and provenance are retained. Historical8GB synthetic and adapted FinQA experiments are presented as separate evidence regimes rather than pooled RAM-scaling data. We supply coverage-aware utility identities and conditional bounds, but establish neither a novel inference algorithm nor universal architecture superiority. The dossier supports a bounded empirical manuscript without claiming unmeasured32GB performance.

## 1. Motivation and bounded research questions

Public financial-report numerical QA is a useful local reasoning workload, but it is not a substitute for KYC mismatch detection, real-client privacy evaluation or compliance certification. The deployment choice here concerns entire recipes under matched ceilings. We ask how much useful correctness, error exposure, withholding, latency and resident memory each recipe produces, and which bottlenecks the recorded stages reveal.

## 2. Evidence regimes and comparability

{crossmatrix}
{crossdiscussion}
## 3. Historical8GB synthetic results, retained as context

{legacy}
All historical numbers above are supported by existing175-case raw files and summaries. No hypothetical missed-field correction or post-hoc reinterpretation changes them. Conditional scorable denominators are visible. The historical narrative is a source artifact, not permission to generalize beyond measured tasks.

## 4. Complete8GB numerical-development inventory

{t8_table()}
### Supporting development and engineering diagnostics

{historical_diagnostics()}
The historical synthetic-phase FRAMES control had SAS1/100 and MAS2/100; the later baseline reverses that small near-floor ordering. Different protocols cannot be merged into a knowledge-scaling trend. The actor-adaptation artifact distinguishes11 correct candidates from10 delivered correct answers; that distinction corrects an easy reading error in the older statistical narrative. Header/catalog work improved reference-program mappability41 to45 of73, with the same4 cases recovered by catalog-only changes. All183 added quantity occurrences were already visible in their baseline source spans; no neural QA benefit or new information was demonstrated.

The paired8GB source audits and the197-artifact historical catalog remain traceable. Artifact count, commit count and repeated questions are not sample sizes or novelty measures. Selection versus reserved-report evidence is explicitly separated.

## 5. The16GB experiment and complete outcome table

{DESIGN}
{main_results}
{details}
{fig('09_cross_tier_descriptive','Separate FinQA recipe/cohort comparisons. This is a descriptive inventory, not a pooled or causal RAM-scaling curve.')}
## 6. Dependency-aware comparison and sensitivity

{primary}
{METHODS}
{fig('11_cluster_sensitivity','Report-cluster versus company-cluster95% intervals for the primary contrasts. Both remain assumption-dependent.')}
## 7. Candidate production, review and missing evidence

{funnel}
{mechanism}
{fig('03_candidate_funnel','A five-correct fixed-candidate gate ceiling does not imply all future MAS designs have that ceiling.')}
## 8. Profile changes and repair across the development journey

{secondary}
{repair}
The8GB crossed-critic and repair studies also tended to shift withholding/error exposure more readily than useful-correct coverage. That recurring descriptive pattern motivates the coverage-aware framework, but shared development cases and changed recipes prevent a pooled mechanistic claim.

## 9. Scoring conventions and numerical interpretation

{concordance}
{metric}
## 10. Resource, latency and decision economics

{costs}
{economics}
{fig('07_risk_coverage','Operating points only: no confidence-calibrated risk-coverage curve or safety guarantee is inferred.')}
{fig('08_utility_sensitivity','Illustrative primary-policy utility versus the assumed wrong-answer penalty. Always-withhold remains visible; no penalty is selected as a primary endpoint.')}
## 11. Formal resource-constrained selective-answering framework

{THEORY.replace('## Formal framework and conditional propositions','### Framework scope')}
## 12. Audit chronology and resource qualification

{RESOURCE}
## 13. Hypotheses, contribution and manuscript decision

{decision}
{readiness}
## 14. Limits, ethics and generalization

{LIMITS}
## 15. Reproducibility and retained artifacts

{repro}
{REFERENCES}
'''
    save('TIER_LE_16_RESEARCH_REPORT.md',combined)
    stat16=f'''#16GB v2 statistical evaluation report

## Paired financial-QA outcomes, conditional coverage and resource-qualified evidence

{META}
## 1. Statistical verdict and analysis hierarchy

{details}
The primary contrast has strongly negative MAS-minus-SAS correct-delivery intervals under both metrics, and strongly negative wrong-delivery intervals. This is a large trade-off, not a no-correct-loss win. The inference is conditional on the declared dependence/symmetry assumptions. The extended statistical plan is post hoc, while the primary profile and metrics were frozen before evaluation.

## 2. Protocol, cohort and statistical units

{DESIGN}
{ENDPOINTS}
## 3. All outcomes, including withholding

{main_results}
{fig('01_outcome_profiles','Complete cohort accounting over160 unique questions per job.960 outputs are repeated measurements, not independent questions.')}
## 4. Primary effects, intervals and multiplicity

{primary}
{fig('02_primary_effects','MAS-minus-SAS effects. Thin intervals95%; wider pale intervals98.75% supplemental family-of-four intervals.')}
The four supplemental report-sign-flip tests have Monte Carlo p=1/65,537 at this resolution and Holm p approximately0.000061. No p=0 is reported. The tests assume independent clusters and null sign symmetry; they are not exact randomization tests of a causal architecture effect. Case-IID McNemar p-values are exported only as dependence-ignoring sensitivity diagnostics.

## 5. Company dependence and cluster influence

{fig('11_cluster_sensitivity','Report50 and company36 resampling units. Disjoint report IDs do not guarantee independence across a shared company.')}
The analysis exports company-cluster intervals, report-equal estimates, leave-one-cluster-out ranges and effective weighted cluster counts. The sign of the large primary correct/wrong contrasts is stable under company clustering. This is robustness to one alternative dependence grouping, not a proof that all unmodelled dependence is absent.

## 6. Stage decomposition and selective-answering controls

{funnel}
{mechanism}
{fig('03_candidate_funnel','Executable and correct candidate funnel. No independence assumption is needed for the conditional decomposition.')}
## 7. Reasoning/demonstration bundle and repair

{secondary}
{repair}
{fig('06_repair_cost','Relative repair cost changes. MAS delivery-state transitions are exactly unchanged across all160 cases.')}
## 8. Numerical metric concordance

{concordance}
{metric}
{fig('04_metric_concordance','Delivered-case metric concordance, not two independent replications.')}
## 9. Runtime economics and coverage

{costs}
{economics}
{fig('07_risk_coverage','Coverage/conditional-risk operating points. Always-withhold has undefined conditional risk at zero coverage.')}
## 10. Resource exclusions and provenance

{RESOURCE}
## 11. Statistical implementation and assumptions

{METHODS}
## 12. What is and is not supported

{decision}
{LIMITS}
## 13. Mathematical checks and decision identities

{THEORY.split('### Proposition 6:')[0].replace('## Formal framework and conditional propositions','### Scope')}
Full memory, bounded-cluster and metric-disagreement propositions appear in the integrated advanced report. These identities clarify interpretation and do not establish a new algorithm.

## 14. Reproduction and files

{repro}
{REFERENCES}
'''
    save('TIER_16_V2_STATISTICAL_EVALUATION_REPORT.md',stat16)
    advanced=f'''# Advanced statistical evaluation: deployments at or below16GB

## Integrated empirical evidence, uncertainty and conditional theoretical framework

**Date:**30October2026. **Status:** pre-paper statistical dossier. No32GB outcomes are available.
**Primary16GB sample:**160 questions /50 reports /36 companies;960 repeated outputs.
**Historical matched numerical cohorts:**101 questions /30 reports;768 repeated outputs. Additional development/probe cohorts are listed separately.
**Legacy synthetic test:**175 cases, evaluated by two arms; metrics are not pooled with FinQA.

## 1. Executive inferential conclusion

{details}
This synthesis is sufficient to organize a bounded empirical manuscript, but not to claim a universally superior architecture or a novel inference method. Both numeric metrics, the withholding reference, source cohorts and historical resource failures remain mandatory parts of interpretation. Formal propositions are conditional definitions/bounds rather than proofs that observed model rankings generalize.

## 2. Study ledger, denominators and comparability

{crossmatrix}
{crossdiscussion}
## 3. Historical synthetic results and their measurement limits

{legacy}
The invention metric is conditional on complete claim sets and the grounding metric is claim-level. A union denominator175 cannot be substituted into89/111 without redefining the metric; malformed outputs must remain visible separately. The old report's claim that its negative-control results prove a specific grounding mechanism is not established by those marginal outcomes.

## 4. Complete8GB numerical study ledger

{t8_table()}
### Supporting diagnostics remain separate

{historical_diagnostics()}
The3B actor-adaptation comparison gained11 correct candidates but delivered10 correct answers; candidate correctness is not delivery. Header/catalog mapping41 to45 of73 and all183 newly exposed catalog occurrences being already visible are representation diagnostics, not measured QA improvements. The early synthetic FRAMES result(SAS1, MAS2 of100) and later result(SAS2, MAS1) are separate baseline/control settings, not a reliable monotonic trend. Controlled verifier/quartet probes and question-blind shortcut audits likewise do not establish natural QA ability.

{fig('09_cross_tier_descriptive','Different cohorts and recipes are plotted descriptively, without joining them into a RAM-response curve.')}
## 5.16GB design and complete performance table

{DESIGN}
{ENDPOINTS}
{main_results}
{fig('01_outcome_profiles','All repeated16GB measurements, with no dropped abstentions.')}
## 6. Primary estimates and dependent-data inference

{primary}
{fig('02_primary_effects','Report-level interval estimates plus a supplemental four-endpoint interval family.')}
{METHODS}
## 7. Cluster sensitivity and finite-sample limits

{fig('11_cluster_sensitivity','The company sensitivity changes the grouping, not the answer labels or case set.')}
The bounded-cluster proposition below gives a deliberately conservative alternative to bootstrap precision. For the reported-correct primary contrast, the exported half-width is computed from the observed report-size weights. Broad bounds are a limitation of weak assumptions, not a reason to select a narrower test after seeing its significance. Effective cluster count is1/sum(w_g squared), which differs from the number of repeated outputs.

## 8. Paired transitions and candidate/gate decomposition

{funnel}
{mechanism}
{fig('03_candidate_funnel','Observed candidates, not a universal capacity floor.')}
{fig('10_retrieval_strata','Post-hoc gold-retrieval strata retain all160 questions; strata are never fed to deployment.')}
## 9. Repair and prompting as separate scientific questions

{secondary}
{repair}
{fig('06_repair_cost','No MAS delivery-state changes despite152 repairs. SAS gains one reported correct and adds two wrong deliveries.')}
## 10. Metric sensitivity and annotation conventions

{concordance}
{metric}
{fig('04_metric_concordance','A44-versus4 scoring-convention asymmetry explains the40-answer primary SAS correctness difference.')}
## 11. Risk, coverage and utility sensitivity

{costs}
{economics}
{fig('07_risk_coverage','These are six operating recipes, not confidence thresholds fitted on a common score.')}
{fig('08_utility_sensitivity','Primary utility functions use an illustrative penalty, not an outcome-selected compliance loss.')}
## 12. Formal definitions, proofs and their assumptions

{THEORY.replace('## Formal framework and conditional propositions','### Scope of the mathematical statements')}
## 13. Deployment resource history and validity

{RESOURCE}
{fig('12_disk_vs_resident','GGUF file bytes versus sampled RSS. Disk size is not an exact decomposition of resident allocations.')}
## 14. Hypothesis ledger and scientific originality

{decision}
**Main head-to-head hypothesis:** the tested MAS recipe does not achieve fewer wrong deliveries without lost correct coverage. **Prompt bundle:** both systems show observed sample improvements over direct control, but this does not isolate the two prompt components. **Repair:** no no-loss/no-extra-error benefit is observed here. **RAM scaling law:** not identified by unlike cohorts/recipes. **Universal capacity floor:** not proven. **New algorithmic novelty:** not established.

## 15. A paper without32GB: scope and remaining work

{readiness}
## 16. Limits and reproducibility

{LIMITS}
{repro}
{REFERENCES}
'''
    save('TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT.md',advanced)
    supports={'RESULTS.md':'#16GB complete results\n\n'+main_results+'\n'+details,
        'PROTOCOL_SNAPSHOT.md':'#16GB protocol snapshot\n\n'+META+'\n'+DESIGN,
        'STATISTICAL_METHODS.md':'# Statistical methods and interpretation\n\n'+METHODS,
        'FAILURE_ANALYSIS.md':'# Candidate, metric and repair audit\n\n'+funnel+'\n'+mechanism+'\n'+metric+'\n'+repair,
        'RESOURCE_AUDIT.md':'# Resource validity and chronology\n\n'+RESOURCE+'\n'+costs,
        'SUPERVISOR_UPDATE_2026-10-30.md':'# Supervisor update:30October2026\n\n'+details+'\n'+decision+'\n'+readiness,
        'DATA_DICTIONARY.md':'''# Derived data dictionary

- `case_outcomes.csv`:960 rows, one model/profile output per row;160 unique question IDs. `reported_correct` and `raw_correct` describe the final candidate; use the outcome columns or delivered AND correct to count delivered correctness. `execution_valid` is deterministic support/format validity, not numerical correctness. `annotated_evidence_complete` is a post-hoc diagnostic from gold source IDs, not a generation input. Tokens and seconds sum stages; completed_time is Unix UTC. Some rows originate from explicitly qualified checkpoint prefixes.
- `report_outcomes.csv`: company-year report totals by job and metric. Reports recur across recipes/metrics and are not independent duplicates. Company is the first ID component; report is company/year.
- `paired_effects.csv`: right-minus-left event-rate contrasts, report-cluster95% intervals, company-cluster sensitivity, supplemental sign-flip tests, and case-IID McNemar sensitivity. Positive wrong/withheld changes are not correctness gains. Holm applies only to four primary correct/wrong tests. Other tests are exploratory/unadjusted.
- `resource_events.csv`: two retained source swap failures with first invalid sample times and sampled resource peaks. They remain failures.
- `stage_metrics.csv`: calls, tokens, seconds and finish reasons by job/role/stage for committed cases only; excludes aborted uncheckpointed work.
- `metric_disagreements.csv`:48 primary SAS deliveries whose correctness label differs across metrics, including predicted scalar, declared unit and both source references. No metric is silently replaced.
- `statistical_analysis.json`: complete numerical analysis, gates/funnels, retrieval strata, 3x3 transitions, MC resolution, effective cluster counts and all assumptions.
- All sizes labelled GB are decimal10^9 bytes; GiB conversion divides by2^30. RSS is sampled controller-plus-worker memory; a disk file is not an RSS component measurement. Seconds/correct is undefined if C=0; zero is not substituted.
'''}
    for name,content in supports.items():save('research/tier16_v2/'+name,content)
    save('research/le16_v2/COMPARABILITY_MATRIX.md','# Evidence regimes\n\n'+crossmatrix+'\n'+crossdiscussion)
    save('research/le16_v2/THEORETICAL_FRAMEWORK.md',THEORY)
    save('research/le16_v2/HYPOTHESES_AND_CLAIMS.md','# Hypothesis and claim ledger\n\n'+decision+'\n'+LIMITS)
    save('research/le16_v2/PUBLICATION_READINESS.md','# Bounded manuscript decision\n\n'+readiness)
    save('research/tier16_v2/README.md','''# Completed16GB analysis package

The final accuracy audit is complete; historical swap failures remain resource-invalid. No32GB run is included.

- [Empirical report](../../TIER_16_RESEARCH_REPORT.md)
- [Statistical report source](../../TIER_16_V2_STATISTICAL_EVALUATION_REPORT.md) and [PDF](../../output/pdf/TIER_16_V2_STATISTICAL_EVALUATION_REPORT.pdf)
- [Results](RESULTS.md), [protocol](PROTOCOL_SNAPSHOT.md), [methods](STATISTICAL_METHODS.md), [failure analysis](FAILURE_ANALYSIS.md), [resource audit](RESOURCE_AUDIT.md), [data dictionary](DATA_DICTIONARY.md), [reproduction](REPRODUCIBILITY.md)
- `data/`: six analysis CSVs plus full statistical JSON. `evidence/`: unchanged source-audit JSON and input SHA256 manifest. Raw responses and full memory traces remain on SSD.
- [Combined dossier](../../TIER_LE_16_RESEARCH_REPORT.md) and [advanced PDF](../../output/pdf/TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT.pdf)

Final source run: `AGERE/runs/lab_tiers_v1/lab-16-115gb-recovery-02`. Six complete160-case jobs;160 unique questions, not960 independent questions.
''')
    save('research/le16_v2/README.md','''# Integrated evidence for nominal tiers up to16GB

Read the [pre-paper research draft](../../TIER_LE_16_RESEARCH_REPORT.md), [advanced statistical source](../../TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT.md) and [advanced PDF](../../output/pdf/TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT.pdf).

Supporting documents: [comparability](COMPARABILITY_MATRIX.md), [formal framework](THEORETICAL_FRAMEWORK.md), [claims](HYPOTHESES_AND_CLAIMS.md), [publication readiness](PUBLICATION_READINESS.md).

`data/cross_tier_analysis.json` preserves the separate8GB synthetic,8GB adapted FinQA and16GB pretrained FinQA regimes. `tier8_condition_inventory.csv` contains15 completed numerical conditions; `tier8_case_outcomes.csv` has768 repeated outputs on101 unique questions with selection/reserved cohort labels for independent re-analysis. `tier8_evidence_catalog.json` indexes197 historical artifacts without treating them as independent experiments. No pooled causal RAM effect,32GB extrapolation or algorithmic-novelty proof is claimed.
''')
    save('research/tier16_v2/REPRODUCIBILITY.md',f'''# Reproduce analysis and documents

No neural inference/training is performed. Keep the original SSD connected; source hashes and the original result archive are verified. The code reads existing public/scoring artifacts and preserves original outputs.

```bash
cd /home/mutasim/Desktop/project-agere
export AGERE_SSD_ROOT="/run/media/mutasim/Data/AGERE"
export AGERE_REPORT_PYTHON="/home/mutasim/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
"$AGERE_REPORT_PYTHON" scripts/reporting/analyze_completed_tiers.py --ssd "$AGERE_SSD_ROOT"
"$AGERE_REPORT_PYTHON" scripts/reporting/build_research_documents.py
"$AGERE_REPORT_PYTHON" scripts/reporting/render_statistical_reports.py
```

The bundled runtime supplies NumPy and ReportLab; no new installation was required. Plotting uses ReportLab graphics, exporting SVG and publication-ready PNG. PDF pages are rendered with Poppler for visual verification. The two final PDFs are under `output/pdf/`; editable Markdown and machine-readable CSV/JSON stay separate.

Parameters: bootstrap{10000} draws; supplemental sign flips up to{65536}; seed42. Primary family has4 correct/wrong contrasts. The source audit uses a different random generator/quantile convention; it is retained unchanged. Supplemental plan is post hoc. CIs are not guaranteed under arbitrary dependent or nonrepresentative reports.

Source archive: `{D['archive']}`. Expected SHA256: `{D['archive_sha256']}`. Full input hashes: `evidence/input_provenance.json`. Raw weights are not copied into Git or the documentation bundle; model hashes remain pinned in the evaluation manifest. No tokens or credentials enter outputs.
''')
    write_index={'reports':['TIER_16_RESEARCH_REPORT.md','TIER_LE_16_RESEARCH_REPORT.md','TIER_16_V2_STATISTICAL_EVALUATION_REPORT.md','TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT.md'],
        'pdfs':['output/pdf/TIER_16_V2_STATISTICAL_EVALUATION_REPORT.pdf','output/pdf/TIER_LE_16_ADVANCED_STATISTICAL_EVALUATION_REPORT.pdf']}
    save('research/tier16_v2/data/document_index.json',json.dumps(write_index,indent=2))
    print('Created4 root reports,16GB support documentation and integrated pre-paper framework.')


if __name__=='__main__':build()
