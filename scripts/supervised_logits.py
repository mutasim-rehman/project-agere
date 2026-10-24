"""Use HF logits_to_keep for the loss-bearing suffix, retaining full inputs.

Keep the last prefix position because it predicts the first supervised token.
The final position is ignored by causal-LM shifting. This is a known optimization,
not a different training objective or a context/target truncation.
"""


def supervised_window(row):
    ids, labels = row["input_ids"], row["labels"]
    if len(ids) != len(labels) or not ids:
        raise ValueError("Input and label lengths must match")
    first = next((i for i, value in enumerate(labels) if value != -100), len(labels))
    if not 0 < first < len(labels) or any(value == -100 for value in labels[first:]):
        raise ValueError("Require masked prefix followed by complete supervised target")
    if labels[first:] != ids[first:]:
        raise ValueError("Supervised target differs from complete input suffix")
    suffix = labels[first - 1:]
    return {"labels": suffix, "logits_to_keep": len(suffix),
            "input_ids": ids, "prefix_tokens": first, "supervised_tokens": len(labels) - first}
