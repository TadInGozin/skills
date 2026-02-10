#!/usr/bin/env python3
"""
Validate and normalize evaluation dimension weights.

Input (stdin JSON):
  {"weights": {"accuracy": 35, "verifiability": 10, ...}}

Output (stdout JSON):
  {"valid": true, "weights": {...}, "adjustments_made": [...], "truth_anchor_sum": N}

Config: protocols/standard.yaml -> rubric_selection.weight_constraints
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.io_helpers import read_input, write_output, fail, load_config

# Core6 dimensions that have bounds constraints
CORE6 = ["accuracy", "verifiability", "completeness", "clarity", "actionability", "relevance"]


def validate_and_normalize(weights, constraints):
    """Clip bounds, enforce truth anchor, normalize to 100."""
    adjustments = []
    result = dict(weights)

    # Step 1: Clip Core6 to bounds
    all_bounds = {}
    for tier_key in ("tier1", "tier2"):
        tier = constraints.get(tier_key, {})
        for dim, bounds in tier.items():
            if isinstance(bounds, dict):
                all_bounds[dim] = bounds

    for dim in CORE6:
        if dim not in result:
            continue
        bounds = all_bounds.get(dim)
        if not bounds:
            continue
        lo, hi = bounds.get("min", 0), bounds.get("max", 100)
        original = result[dim]
        if original < lo:
            result[dim] = lo
            adjustments.append(f"{dim}: {original} -> {lo} (below min)")
        elif original > hi:
            result[dim] = hi
            adjustments.append(f"{dim}: {original} -> {hi} (above max)")

    # Step 2: Truth anchor enforcement
    combined = constraints.get("combined", {})
    anchor_cfg = combined.get("truth_anchor_sum", {})
    min_anchor = anchor_cfg.get("min", 30) if isinstance(anchor_cfg, dict) else 30

    acc = result.get("accuracy", 0)
    ver = result.get("verifiability", 0)
    anchor_sum = acc + ver

    if anchor_sum < min_anchor and anchor_sum > 0:
        # Proportionally increase both to meet minimum
        factor = min_anchor / anchor_sum
        new_acc = round(acc * factor, 1)
        new_ver = round(ver * factor, 1)
        adjustments.append(
            f"truth_anchor: {acc}+{ver}={anchor_sum} < {min_anchor}, "
            f"scaled to {new_acc}+{new_ver}"
        )
        result["accuracy"] = new_acc
        result["verifiability"] = new_ver
        anchor_sum = new_acc + new_ver

    # Step 3: Normalize to 100
    total = sum(result.values())
    target = constraints.get("total", 100)

    if total > 0 and abs(total - target) > 0.5:
        factor = target / total
        old_total = total
        for dim in result:
            result[dim] = round(result[dim] * factor, 1)
        # Fix rounding to hit exactly target
        diff = target - sum(result.values())
        if abs(diff) > 0.01:
            # Add diff to the largest weight
            largest = max(result, key=result.get)
            result[largest] = round(result[largest] + diff, 1)
        adjustments.append(f"normalized: {old_total} -> {target}")

    return {
        "valid": len(adjustments) == 0,
        "weights": result,
        "adjustments_made": adjustments,
        "truth_anchor_sum": round(result.get("accuracy", 0) + result.get("verifiability", 0), 1),
    }


def main():
    data = read_input()
    weights = data.get("weights")
    if not weights or not isinstance(weights, dict):
        fail("Input must contain 'weights' object")

    constraints = load_config("rubric_selection.weight_constraints")
    result = validate_and_normalize(weights, constraints)
    write_output(result)


if __name__ == "__main__":
    main()
