# Native Windows candidate generation pilot

This paired diagnostic reuses the 24 dev24 questions selected in the
historical 8 GB study. It compares the same unadapted 3B Q4 drafter with
refusal allowed versus a required program attempt. The intervention changes
both the drafting instruction and its allowed output branch. Both arms
receive the same evidence and use the same deterministic executor and
0.5B F16 verifier. The runner alternates arm order by question.

The CPU runner launches one native completion process at a time, so these
results apply to sequential roles. Sampled working-set RSS includes the
inference process and Python controller at 200 ms intervals. The runner
terminates an inference process when a sample exceeds 6.4 decimal GB.
Windows paging and peaks between samples remain unverified. Each call
reserves its full generation allowance against the per-question budget.

Runtime: official llama.cpp Windows x64 CPU build b12202, commit
`d6be06557`. Archive SHA-256
`75d108e6f91907638fef0cbdf4cc230e56bd9eac71bbffb209ae8da1f932590e`.
The drafter SHA-256 is
`626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d`
and verifier SHA-256 is
`f044b7e19bf2a007973e9c84119c34afcab419546e76595b0367f963275b66e9`.
Gold source SHA-256
`a847fb7e0d61a3125a1e2909852df6b89f1ee64d2c5ff1bf689e332214deee51`
matches the historical pilot manifest. Gold is passed to the scorer only.

```powershell
.venv\Scripts\python.exe scripts\tier8_windows_pilot.py --cli tmp\agere-win-runtime\llama-completion.exe --weights H:\AGERE\weights\tier8_v2 --gold H:\AGERE\datasets\tier8_v2_finqa\dev_report100_01\source-dev.json --output tmp\win-cli-dev24-v2
.venv\Scripts\python.exe scripts\tier8_windows_analyze.py tmp\win-cli-dev24-v2\cases.jsonl --gold H:\AGERE\datasets\tier8_v2_finqa\dev_report100_01\source-dev.json
```

The prefix diagnostic scores each earlier execution endpoint after the run.
It estimates where a correct numerical result appeared in an ultimately
incorrect program. Because it uses the answer key to select the endpoint,
this diagnostic does not measure deployable performance.

## Observed results

The planned 24-pair run was interrupted after the first five complete
pairs to test the endpoint failure directly. The follow-up used those
same five questions. The one-step arm used both a one-step grammar and
an explicit instruction to use one operation. This was a post-hoc
development intervention, and the sample was reused for diagnosis.

- Refusal allowed: five refusals and zero executable programs.
- Forced attempt: five executable programs, zero reported-answer matches
  and one raw-execution match. Two incorrect reported-answer endpoints
  had an earlier endpoint that matched the reported answer.
- Forced one-step: five executable programs, two reported-answer matches
  and one raw-execution match. The recovered reported-answer cases were
  the same two found by the prefix diagnostic.
- The verifier withheld every output in all three conditions. Accepting
  all one-step candidates would have delivered two correct and three wrong
  answers by the reported-answer metric.
- The largest sampled RSS was 2,478,895,104 bytes across completed calls.

The step cap changed candidate quality on this slice, but the result
depends on the scoring convention and did not improve delivery. The
one-step rule is unsuitable as a general solution for multi-step questions.
Further prompt-only tuning on the same cases would have low information
value. A future confirmation would need untouched reports, validated
scoring, and a verifier comparison on fixed candidate programs. Keep the
16 GB tier gated.

The completed case ledgers and machine-generated summary are archived
under `evidence/windows-candidate-pilot`. The follow-up command was the
same as above with `--output tmp\win-cli-one-step --limit 5 --one-step`.
