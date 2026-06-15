---
estimated_steps: 7
estimated_files: 1
skills_used: []
---

# T02: Implement F1 metric calculation module

Create `backend/eval/metrics.py` with token-overlap F1 score calculation.

The module must:
1. Implement `normalize_text(text: str) -> str` that lowercases, strips punctuation, and splits into tokens.
2. Implement `token_overlap_f1(predicted: str, ground_truth: str) -> float` that computes precision, recall, and F1 from token overlap.
3. Implement `compute_per_label_f1(predictions: dict, ground_truth: dict, labels: list[str]) -> dict[str, float]` that returns F1 per label.
4. Implement `compute_mean_f1(per_label_scores: dict[str, float]) -> float` for the overall score.
5. Handle edge cases: empty strings, None values, missing labels → F1 = 0.0.

## Inputs

- None specified.

## Expected Output

- `backend/eval/metrics.py`

## Verification

uv run python -c "from eval.metrics import token_overlap_f1; assert token_overlap_f1('hello world', 'hello world') == 1.0; print('ok')"
