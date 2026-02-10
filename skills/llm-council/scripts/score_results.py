#!/usr/bin/env python3
"""
Score aggregation and bias detection for LLM Council evaluations.

Input (stdin JSON):
  {
    "evaluations": [
      {"evaluator": "A", "scores": {"B": {"accuracy": 8, ...}, "C": {...}}},
      ...
    ],
    "weights": {"accuracy": 30, "verifiability": 15, ...}
  }

Output (stdout JSON):
  {"ranking": [{label, z_score, raw_score}], "bias_flags": [...]}
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.io_helpers import read_input, write_output, fail, load_config


def weighted_score(scores, weights):
    """Compute weighted sum: sum(score * weight/100)."""
    total = 0.0
    weight_sum = sum(weights.get(d, 0) for d in scores)
    if weight_sum == 0:
        return 0.0
    for dim, score in scores.items():
        w = weights.get(dim, 0) / 100.0
        total += score * w
    return round(total, 3)


def _mean(values):
    """Compute mean of a list."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _stdev(values, mean_val=None):
    """Compute population stdev."""
    if len(values) < 2:
        return 0.0
    if mean_val is None:
        mean_val = _mean(values)
    variance = sum((v - mean_val) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def z_normalize(evaluator_scores):
    """Z-score normalize one evaluator's weighted scores.

    Args:
        evaluator_scores: {response_label: weighted_score}

    Returns:
        {response_label: z_score}
    """
    values = list(evaluator_scores.values())
    if len(values) < 2:
        return {k: 0.0 for k in evaluator_scores}

    m = _mean(values)
    s = _stdev(values, m)

    if s == 0:
        return {k: 0.0 for k in evaluator_scores}

    return {k: round((v - m) / s, 4) for k, v in evaluator_scores.items()}


def aggregate_scores(evaluations, weights):
    """
    1. Compute weighted score per evaluator per response
    2. Z-normalize per evaluator
    3. Average z-scores per response
    4. Rank by averaged z-score
    """
    # Step 1+2: Per-evaluator weighted scores, then z-normalize
    response_z_scores = {}  # {response_label: [z_scores]}

    for ev in evaluations:
        evaluator_weighted = {}
        for resp_label, dim_scores in ev.get("scores", {}).items():
            evaluator_weighted[resp_label] = weighted_score(dim_scores, weights)

        z_scores = z_normalize(evaluator_weighted)

        for resp_label, z in z_scores.items():
            response_z_scores.setdefault(resp_label, []).append(z)

    # Step 3+4: Average and rank
    ranking = []
    for label, z_list in response_z_scores.items():
        avg_z = round(_mean(z_list), 4)
        # Also compute raw average for reference
        raw_scores = []
        for ev in evaluations:
            if label in ev.get("scores", {}):
                raw_scores.append(weighted_score(ev["scores"][label], weights))
        avg_raw = round(_mean(raw_scores), 3) if raw_scores else 0.0

        ranking.append({"label": label, "z_score": avg_z, "raw_score": avg_raw})

    ranking.sort(key=lambda r: r["z_score"], reverse=True)
    return ranking


def detect_bias(evaluations, weights, variance_threshold):
    """Flag evaluators whose scores deviate > threshold*sigma from cross-evaluator mean."""
    flags = []

    # Collect all weighted scores per response across evaluators
    response_scores = {}  # {response: [(evaluator, weighted_score)]}

    for ev in evaluations:
        evaluator = ev.get("evaluator", "?")
        for resp_label, dim_scores in ev.get("scores", {}).items():
            ws = weighted_score(dim_scores, weights)
            response_scores.setdefault(resp_label, []).append((evaluator, ws))

    # Check each response
    for resp_label, scores_list in response_scores.items():
        if len(scores_list) < 2:
            continue

        values = [s for _, s in scores_list]
        m = _mean(values)
        s = _stdev(values, m)

        if s == 0:
            continue

        for evaluator, ws in scores_list:
            deviation = abs(ws - m) / s
            if deviation > variance_threshold:
                flags.append({
                    "evaluator": evaluator,
                    "response": resp_label,
                    "score": ws,
                    "mean": round(m, 3),
                    "stdev": round(s, 3),
                    "deviation_sigma": round(deviation, 2),
                })

    return flags


def main():
    data = read_input()

    evaluations = data.get("evaluations")
    if not evaluations or not isinstance(evaluations, list):
        fail("Input must contain 'evaluations' array")

    weights = data.get("weights")
    if not weights or not isinstance(weights, dict):
        fail("Input must contain 'weights' object")

    bias_cfg = load_config("bias_mitigation.detection")
    variance_threshold = bias_cfg.get("variance_threshold", 2.0)

    ranking = aggregate_scores(evaluations, weights)
    bias_flags = detect_bias(evaluations, weights, variance_threshold)

    write_output({"ranking": ranking, "bias_flags": bias_flags})


if __name__ == "__main__":
    main()
