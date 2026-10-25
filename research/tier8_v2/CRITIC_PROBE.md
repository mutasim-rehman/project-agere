# Train-only critic diagnostic

Source: scripts/tier8_v2_critic_probe.py.

The all-reject3B critic is not an established strong verifier. Test whether its
behavior changes on annotation-consistent versus deliberately wrong, executable
programs, and whether a simpler output protocol helps. This informs which baseline
must be strengthened before testing a novel repair contribution.

Use12 distinct annual-report groups from the existing training-only validation
corpus, one first qualifying example per group. Both original numerical answer
metrics must accept a reference and reject its first eligible single-operation
mutation. Operands/sources/units remain unchanged. These are24 controlled programs,
not natural errors or independently adjudicated semantic gold.

Each profile reviews all24 under the existing rich three-check/repair format and
a simpler verdict-only format (48 calls/profile;96 total). Inputs are identical
apart from protocol instructions. This tests protocol sensitivity, not a pure
schema effect. Load native0.5B F16 and3B Q4 separately, no adapter, CPU8 threads,
context4096, greedy seed42,192 output tokens/protocol,384/program. Reuse the actual
Models.call chat prompt and runtime-verified token accounting.

All new raw data, labels, traces, memory and model copies are on SSD. Only source,
protocol and aggregate metadata enter git. The worker never reads the label file.
Freeze source/public/label hashes and check complete unique case/protocol coverage.
Peak memory is controller+single worker, not the full MAS deployment footprint.
182 tests passed before launch, including rejection of numerically equivalent
mutations and exact matching of the deployed rich instruction.

No threshold or prompt will be selected from the reused development24 in this
probe. A gain here would justify further testing, not establish novelty, financial
safety or generalization to natural model errors. Report true/false accepts,
true/false rejects, UNKNOWN and parse failures separately.
