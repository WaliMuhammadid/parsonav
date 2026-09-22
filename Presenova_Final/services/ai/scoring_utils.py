"""
Scoring Utilities for AI Evaluators
Provides helpers to clamp, validate, and compute aggregate presentation scores.
"""

def clamp_score(value: float | int, min_val: int = 0, max_val: int = 100) -> int:
    """Clamp a numerical score within [min_val, max_val] range and return as integer."""
    try:
        return int(max(min_val, min(max_val, round(float(value)))))
    except (TypeError, ValueError):
        return min_val


def compute_weighted_overall(scores: dict[str, int | float], weights: dict[str, float] | None = None) -> int:
    """Compute weighted average score from a dictionary of category scores."""
    if not scores:
        return 70

    if not weights:
        # Default equal weighting
        valid_scores = [clamp_score(v) for v in scores.values() if isinstance(v, (int, float))]
        return int(round(sum(valid_scores) / max(1, len(valid_scores)))) if valid_scores else 70

    total_weight = 0.0
    weighted_sum = 0.0
    for key, weight in weights.items():
        if key in scores and isinstance(scores[key], (int, float)):
            weighted_sum += clamp_score(scores[key]) * weight
            total_weight += weight

    if total_weight <= 0:
        return 70

    return clamp_score(weighted_sum / total_weight)
