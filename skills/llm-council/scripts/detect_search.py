#!/usr/bin/env python3
"""
Detect search tools among available MCP tools using multi-signal scoring.

Input (stdin JSON):
  {"tools": [{"name": "...", "description": "...", "parameters": {...}}]}

Output (stdout JSON):
  {"search_tools": [...], "confirmation_needed": [...]}

Config: protocols/standard.yaml -> search_tool_detection
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.io_helpers import read_input, write_output, fail, load_config


def score_tool(tool, config):
    """Score a single tool for search capability."""
    total = 0
    evidence = []

    name = tool.get("name", "")
    desc = tool.get("description", "")
    params = tool.get("parameters", {})

    # Parameter signals
    total, evidence = _add(*_check_parameters(params, config.get("parameter_signals", {})),
                           total, evidence)

    # Description signals
    total, evidence = _add(*_check_description(desc, config.get("description_signals", {})),
                           total, evidence)

    # Name signals
    total, evidence = _add(*_check_name(name, config.get("name_signals", {})),
                           total, evidence)

    # Negative signals
    total, evidence = _add(*_check_negative(name, desc, config.get("negative_signals", {})),
                           total, evidence)

    thresholds = config.get("thresholds", {})
    classification = _classify(total, thresholds)

    return {
        "name": name,
        "score": total,
        "classification": classification,
        "evidence": evidence,
    }


def _add(s, e, total, evidence):
    return total + s, evidence + e


def _check_parameters(params, signals):
    """Check for search-indicative parameters (query, url)."""
    score = 0
    evidence = []

    param_keys = set()
    if isinstance(params, dict):
        for k, v in params.items():
            param_keys.add(k.lower())
            if isinstance(v, dict) and "properties" in v:
                param_keys.update(p.lower() for p in v["properties"])
    elif isinstance(params, list):
        param_keys = {str(p).lower() for p in params}

    sig = signals.get("query_parameter", {})
    pts = sig.get("score", 0) if isinstance(sig, dict) else sig
    if any(k in param_keys for k in ("query", "url")):
        score += pts
        evidence.append(f"query_parameter(+{pts})")

    return score, evidence


def _check_description(desc, signals):
    """Check description for search-related keywords."""
    score = 0
    evidence = []
    desc_lower = desc.lower()

    for signal_key, sig in signals.items():
        if not isinstance(sig, dict) or "keywords" not in sig:
            continue
        pts = sig.get("score", 0)
        for kw in sig["keywords"]:
            if kw.lower() in desc_lower:
                score += pts
                evidence.append(f"{signal_key}(+{pts})")
                break

    return score, evidence


def _check_name(name, signals):
    """Check tool name against search patterns."""
    name_lower = name.lower()

    patterns_sig = signals.get("patterns", {})
    if isinstance(patterns_sig, dict) and "patterns" in patterns_sig:
        pts = patterns_sig.get("score", 0)
        for pattern in patterns_sig["patterns"]:
            if re.search(pattern, name_lower, re.IGNORECASE):
                return pts, [f"name_pattern(+{pts})"]

    return 0, []


def _check_negative(name, desc, signals):
    """Negative signals: reduce score for non-search indicators."""
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
                break

    return score, evidence


def _classify(score, thresholds):
    """Classify by score thresholds."""
    definite = thresholds.get("definite_search", 60)
    not_search = thresholds.get("not_search", 30)

    if score >= definite:
        return "definite_search"
    elif score >= not_search:
        return "likely_search"
    return "not_search"


def main():
    data = read_input()
    tools = data.get("tools")
    if not tools or not isinstance(tools, list):
        fail("Input must contain 'tools' array")

    config = load_config("search_tool_detection")
    results = [score_tool(t, config) for t in tools]

    search_tools = [r for r in results if r["classification"] == "definite_search"]
    confirmation = [r for r in results if r["classification"] == "likely_search"]

    search_tools.sort(key=lambda r: r["score"], reverse=True)
    confirmation.sort(key=lambda r: r["score"], reverse=True)

    write_output({
        "search_tools": search_tools,
        "confirmation_needed": confirmation,
    })


if __name__ == "__main__":
    main()
