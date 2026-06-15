import string
from typing import Dict, List, Optional


def normalize_text(text: Optional[str]) -> str:
    """
    Lowercases, strips punctuation, and splits into tokens.
    Returns normalized text as a space-separated string of tokens.
    """
    if text is None:
        return ""

    text = text.lower()

    # Remove punctuation
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)

    tokens = text.split()
    return " ".join(tokens)


def token_overlap_f1(predicted: Optional[str], ground_truth: Optional[str]) -> float:
    """
    Computes precision, recall, and F1 from token overlap.
    """
    pred_tokens = normalize_text(predicted).split()
    gt_tokens = normalize_text(ground_truth).split()

    # Edge case: If both are empty (meaning entity is absent and predicted as absent)
    # the F1 score could be considered 1.0 (perfect match of absence), but usually
    # in information extraction, if GT is empty and pred is empty, we exclude it or
    # return 0.0. For this context, let's say matching empty strings yields 1.0.
    if not gt_tokens and not pred_tokens:
        return 1.0

    # If one is empty and the other isn't, no overlap
    if not gt_tokens or not pred_tokens:
        return 0.0

    # Count overlapping tokens
    common_tokens = set(pred_tokens).intersection(set(gt_tokens))

    if not common_tokens:
        return 0.0

    precision = len(common_tokens) / len(pred_tokens)
    recall = len(common_tokens) / len(gt_tokens)

    if precision + recall == 0:
        return 0.0

    f1 = 2 * (precision * recall) / (precision + recall)
    return float(f1)


def compute_per_label_f1(predictions: Dict[str, str], ground_truth: Dict[str, str], labels: List[str]) -> Dict[str, float]:
    """
    Returns F1 score per label.
    """
    results = {}
    for label in labels:
        pred_val = predictions.get(label, "")
        gt_val = ground_truth.get(label, "")
        results[label] = token_overlap_f1(pred_val, gt_val)
    return results


def compute_mean_f1(per_label_scores: Dict[str, float]) -> float:
    """
    Computes the overall mean score.
    """
    if not per_label_scores:
        return 0.0
    return sum(per_label_scores.values()) / len(per_label_scores)
