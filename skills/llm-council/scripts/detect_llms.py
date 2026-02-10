#!/usr/bin/env python3
"""
Detect LLM tools among available MCP tools using multi-signal scoring.

Input (stdin JSON):
  {"tools": [{"name": "...", "description": "...", "parameters": {...}}]}

Output (stdout JSON):
  {"participants": [...], "confirmation_needed": [...]}

Config: protocols/standard.yaml -> llm_tool_detection
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.io_helpers import read_input, write_output, fail, load_config


def score_tool(tool, config):
    """Score a single tool against all signal tiers."""
    total = 0
    evidence = []

    name = tool.get("name", "")
    desc = tool.get("description", "")
    params = tool.get("parameters", {})

    # Tier 1: Parameter signals
    s, e = _check_parameters(params, config.get("parameter_signals", {}))
    total += s
    evidence.extend(e)

    # Tier 2: Description signals
    s, e = _check_description(desc, config.get("description_signals", {}))
    total += s
    evidence.extend(e)

    # Tier 3: Name signals (only one applies)
    s, e = _check_name(name, config.get("name_signals", {}))
    total += s
    evidence.extend(e)

    # Negative signals
    s, e = _check_negative(name, desc, config.get("negative_signals", {}))
    total += s
    evidence.extend(e)

    # Classify
    thresholds = config.get("thresholds", {})
    classification = _classify(total, thresholds)

    return {
        "name": name,
        "score": total,
        "classification": classification,
        "evidence": evidence,
    }


def _check_parameters(params, signals):
    """Tier 1: Check for LLM-indicative parameters."""
    score = 0
    evidence = []

    # Normalize parameter keys (handle both dict-of-dicts and flat list)
    param_keys = set()
    if isinstance(params, dict):
        for k, v in params.items():
            param_keys.add(k.lower())
            # Handle nested properties (JSON Schema style)
            if isinstance(v, dict) and "properties" in v:
                param_keys.update(p.lower() for p in v["properties"])
    elif isinstance(params, list):
        param_keys = {str(p).lower() for p in params}

    checks = [
        ("required_prompt", "prompt", True),
        ("optional_prompt", "prompt", False),
        ("model_parameter", "model", None),
        ("temperature_parameter", "temperature", None),
        ("max_tokens_parameter", "max_tokens", None),
    ]

    prompt_matched = False
    for signal_key, param_name, required_flag in checks:
        if signal_key not in signals:
            continue
        sig = signals[signal_key]
        pts = sig.get("score", 0) if isinstance(sig, dict) else sig

        if param_name == "prompt":
            if "prompt" in param_keys:
                # Check required vs optional
                if required_flag is True:
                    # Check if prompt is actually required
                    is_required = _param_is_required(params, "prompt")
                    if is_required and not prompt_matched:
                        score += pts
                        evidence.append(f"required_prompt(+{pts})")
                        prompt_matched = True
                elif required_flag is False and not prompt_matched:
                    score += pts
                    evidence.append(f"optional_prompt(+{pts})")
                    prompt_matched = True
        else:
            # Also check camelCase variants
            variants = {param_name, param_name.replace("_", "")}
            if any(v in param_keys for v in variants):
                score += pts
                evidence.append(f"{signal_key}(+{pts})")

    return score, evidence


def _param_is_required(params, name):
    """Check if a parameter is required in the schema."""
    if isinstance(params, dict):
        # JSON Schema style: look for "required" array
        required = params.get("required", [])
        if isinstance(required, list) and name in required:
            return True
        # Check individual param definition
        param_def = params.get(name, {})
        if isinstance(param_def, dict):
            return param_def.get("required", False)
    return False


def _check_description(desc, signals):
    """Tier 2: Check description for LLM-related keywords."""
    score = 0
    evidence = []
    desc_lower = desc.lower()

    for signal_key, sig in signals.items():
        if not isinstance(sig, dict) or "keywords" not in sig:
            continue
        pts = sig.get("score", 0)
        keywords = sig["keywords"]
        for kw in keywords:
            if kw.lower() in desc_lower:
                score += pts
                evidence.append(f"{signal_key}(+{pts})")
                break  # One match per signal group

    return score, evidence


def _check_name(name, signals):
    """Tier 3: Check tool name against patterns. Only one signal applies."""
    name_lower = name.lower()

    # Try explicit patterns first
    explicit = signals.get("explicit_patterns", {})
    if isinstance(explicit, dict) and "patterns" in explicit:
        pts = explicit.get("score", 0)
        for pattern in explicit["patterns"]:
            if re.search(pattern, name_lower, re.IGNORECASE):
                return pts, [f"explicit_name(+{pts})"]

    # Fallback to suggestive patterns
    suggestive = signals.get("suggestive_patterns", {})
    if isinstance(suggestive, dict) and "patterns" in suggestive:
        pts = suggestive.get("score", 0)
        for pattern in suggestive["patterns"]:
            if re.search(pattern, name_lower, re.IGNORECASE):
                return pts, [f"suggestive_name(+{pts})"]

    return 0, []


def _check_negative(name, desc, signals):
    """Negative signals: reduce score for non-LLM indicators."""
    score = 0
    evidence = []
    combined = (name + " " + desc).lower()

    for signal_key, sig in signals.items():
        if not isinstance(sig, dict) or "keywords" not in sig:
            continue
        penalty = sig.get("penalty", 0)
        for kw in sig["keywords"]:
            if kw.lower() in combined:
                score += penalty
                evidence.append(f"{signal_key}({penalty})")
                break  # One match per signal group

    return score, evidence


def _classify(score, thresholds):
    """Classify by score thresholds."""
    definite = thresholds.get("definite_llm", 70)
    likely = thresholds.get("likely_llm", 40)

    if score >= definite:
        return "definite_llm"
    elif score >= likely:
        return "likely_llm"
    return "not_llm"


def main():
    data = read_input()
    tools = data.get("tools")
    if not tools or not isinstance(tools, list):
        fail("Input must contain 'tools' array")

    config = load_config("llm_tool_detection")
    results = [score_tool(t, config) for t in tools]

    participants = [r for r in results if r["classification"] == "definite_llm"]
    confirmation = [r for r in results if r["classification"] == "likely_llm"]

    # Sort by score descending
    participants.sort(key=lambda r: r["score"], reverse=True)
    confirmation.sort(key=lambda r: r["score"], reverse=True)

    write_output({
        "participants": participants,
        "confirmation_needed": confirmation,
    })


if __name__ == "__main__":
    main()
