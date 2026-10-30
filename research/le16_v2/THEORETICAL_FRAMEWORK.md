## Formal framework and conditional propositions

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

Proof: add nonoverlapping resident allocations and nonnegative overhead. Quantized block scales and mixed tensor formats must be included in effective storage bits. GGUF file size is a disk proxy, not an exact RSS decomposition or exact tensor-only lower bound. In this run the model files total about 8.99GB for SAS and 10.27GB for MAS, while observed primary RSS is10.06GB and 10.93GB. Fewer total nominal parameters do not guarantee less resident memory when precision differs.

### Proposition 7: bounded independent-cluster uncertainty

Let independent report contributions D_g lie in [-1,1], with fixed nonnegative weights w_g summing to 1. For the weighted contrast, the bounded-difference/Hoeffding argument gives:

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

Numerical check: the 50-report question-weighted design has effective cluster count36.99. The single-contrast95% bounded half-width is44.66 percentage points; the four-contrast bound is52.38 points. Company grouping has effective count19.88, despite36 named companies. These conservative bounds show how much precision relies on stronger resampling assumptions.

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
