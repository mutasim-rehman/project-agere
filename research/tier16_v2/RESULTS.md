# 16 GB complete results

| Profile / arm | Reported C / W / H | Raw C / W / H | Time (h) | Peak RSS (GB) |
| --- | --- | --- | --- | --- |
| primary / SAS | 78 / 48 / 34 | 38 / 88 / 34 | 11.546 | 10.062 |
| primary / MAS | 5 / 3 / 152 | 5 / 3 / 152 | 2.432 | 10.929 |
| direct control / SAS | 50 / 66 / 44 | 14 / 102 / 44 | 5.266 | 10.040 |
| direct control / MAS | 0 / 5 / 155 | 0 / 5 / 155 | 0.821 | 10.901 |
| repair ablation / SAS | 79 / 50 / 31 | 38 / 91 / 31 | 13.494 | 10.074 |
| repair ablation / MAS | 5 / 3 / 152 | 5 / 3 / 152 | 3.682 | 10.913 |

The primary reported-answer contrast is MAS minus SAS: -73 correct deliveries (-45.625 percentage points), -45 wrong deliveries (-28.125 points), and +118 withholdings (+73.75 points). Raw execution gives -33 correct, -85 wrong, and the same +118 withholdings. Both metrics therefore show a correctness-versus-withholding trade-off, not MAS Pareto superiority.

Conditional precision among delivered primary answers is 61.90% for SAS (78/126) and 62.50% for MAS (5/8) under reported scoring. Similar conditional precision conceals radically different coverage: 78.75% versus 5.00%. Under raw execution precision is30.16% for SAS and 62.50% for MAS, again over different selected delivery sets. A small selected denominator is not evidence that MAS solves most questions more reliably.
