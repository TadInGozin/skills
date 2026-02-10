#!/usr/bin/env python3
"""
Resource budget check for LLM Council.

Input (stdin JSON):
  {"elapsed": 45, "total_budget": 180, "current_mode": "deep",
   "strict": false, "trigger_ratio": 0.8}

Output (stdout JSON):
  {"action": "continue|degrade|stop", "ratio": 0.25, "degrade_to": "..."|null, "reason": "..."}

Defaults loaded from: protocols/standard.yaml -> resource_budget
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.io_helpers import read_input, write_output, fail, load_config

DEGRADATION_ORDER = ["deep", "standard", "quick"]


def check_budget(elapsed, total_budget, current_mode, strict, trigger_ratio):
    """Core budget check logic."""
    if total_budget <= 0:
        return {"action": "stop", "ratio": float("inf"), "degrade_to": None,
                "reason": "invalid budget (<=0)"}

    ratio = elapsed / total_budget

    if strict:
        if ratio >= 1.0:
            return {"action": "stop", "ratio": round(ratio, 3), "degrade_to": None,
                    "reason": "strict mode: budget exceeded"}
        return {"action": "continue", "ratio": round(ratio, 3), "degrade_to": None,
                "reason": "within budget (strict)"}

    if ratio >= trigger_ratio:
        try:
            idx = DEGRADATION_ORDER.index(current_mode)
        except ValueError:
            return {"action": "stop", "ratio": round(ratio, 3), "degrade_to": None,
                    "reason": f"unknown mode: {current_mode}"}

        if idx < len(DEGRADATION_ORDER) - 1:
            next_mode = DEGRADATION_ORDER[idx + 1]
            return {"action": "degrade", "ratio": round(ratio, 3),
                    "degrade_to": next_mode,
                    "reason": f"ratio {ratio:.2f} >= trigger {trigger_ratio}"}
        return {"action": "stop", "ratio": round(ratio, 3), "degrade_to": None,
                "reason": "no further degradation possible (already quick)"}

    return {"action": "continue", "ratio": round(ratio, 3), "degrade_to": None,
            "reason": "within budget"}


def main():
    data = read_input()

    # Load defaults from config
    defaults = load_config("resource_budget")
    time_cfg = defaults.get("time", {})
    deg_cfg = time_cfg.get("degradation", {})

    elapsed = data.get("elapsed")
    if elapsed is None:
        fail("Missing required field: elapsed")

    total_budget = data.get("total_budget")
    current_mode = data.get("current_mode", "standard")

    # Auto-resolve total_budget from config if not provided
    if total_budget is None:
        totals = time_cfg.get("total", {})
        total_budget = totals.get(current_mode)
        if total_budget is None:
            fail(f"No budget defined for mode: {current_mode}")

    strict = data.get("strict", time_cfg.get("strict", False))
    trigger_ratio = data.get("trigger_ratio", deg_cfg.get("trigger_ratio", 0.8))

    result = check_budget(elapsed, total_budget, current_mode, strict, trigger_ratio)
    result["elapsed_seconds"] = elapsed
    result["budget_seconds"] = total_budget
    write_output(result)


if __name__ == "__main__":
    main()
