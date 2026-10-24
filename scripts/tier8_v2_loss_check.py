"""Software equivalence check on a tiny random Qwen; not a task-performance run."""
from copy import deepcopy
import hashlib
import inspect
import json
import os
from pathlib import Path

from supervised_logits import supervised_window

ROOT = Path(__file__).resolve().parents[1]


def main():
    os.environ["TMPDIR"] = str(ROOT / ".local/tmp")
    os.environ["HF_HOME"] = str(ROOT / ".local/hf-training")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRITON_CACHE_DIR"] = str(ROOT / ".local/triton-cache")
    import torch
    import transformers
    from transformers import Qwen2Config, Qwen2ForCausalLM
    torch.set_num_threads(2)
    torch.manual_seed(42)
    config = Qwen2Config(vocab_size=64, hidden_size=32, intermediate_size=64,
        num_hidden_layers=1, num_attention_heads=4, num_key_value_heads=2,
        attention_dropout=0, use_cache=False)
    full = Qwen2ForCausalLM(config).eval()
    suffix = deepcopy(full)
    ids = torch.randint(0, 64, (1, 20))
    labels = ids.clone(); labels[:, :12] = -100
    window = supervised_window({"input_ids": ids[0].tolist(), "labels": labels[0].tolist()})
    loss_full = full(input_ids=ids, labels=labels).loss
    loss_suffix = suffix(input_ids=ids, labels=torch.tensor([window["labels"]]),
                         logits_to_keep=window["logits_to_keep"]).loss
    torch.testing.assert_close(loss_full, loss_suffix, rtol=1e-6, atol=1e-7)
    loss_full.backward(); loss_suffix.backward()
    errors = []
    for (name, a), (other, b) in zip(full.named_parameters(), suffix.named_parameters()):
        assert name == other and a.grad is not None and b.grad is not None
        torch.testing.assert_close(a.grad, b.grad, rtol=1e-5, atol=1e-6)
        errors.append((a.grad - b.grad).abs().max().item())
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    result = {"pass": True, "torch": torch.__version__, "transformers": transformers.__version__,
              "input_tokens": 20, "supervised_tokens": 8, "suffix_logit_positions": window["logits_to_keep"],
              "loss_full": loss_full.item(), "loss_suffix": loss_suffix.item(),
              "max_absolute_parameter_gradient_difference": max(errors), "parameter_tensors_checked": len(errors),
              "helper_sha256": sha(ROOT / "scripts/supervised_logits.py"), "script_sha256": sha(Path(__file__)),
              "qwen_implementation_sha256": sha(Path(inspect.getsourcefile(Qwen2ForCausalLM))),
              "scope": "Tiny random CPU Qwen software check; full input/target and causal-loss gradients preserved. Not real-model fit, task accuracy, or novelty."}
    output = ROOT / "research/tier8_v2/evidence/supervised-logits-equivalence-01.json"
    if output.exists():raise ValueError("Do not overwrite equivalence evidence")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
