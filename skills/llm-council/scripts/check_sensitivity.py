#!/usr/bin/env python3
"""
Classify question sensitivity level.

Input (stdin JSON):  {"question": "..."}
Output (stdout JSON): {"level": "public|sensitive", "matched_keywords": [...]}

Config: protocols/standard.yaml -> security.sensitivity
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.io_helpers import read_input, write_output, fail, load_config


def check_sensitivity(question, sensitive_keywords):
    """Keyword match against question text."""
    q_lower = question.lower()
    matched = [kw for kw in sensitive_keywords if kw.lower() in q_lower]
    level = "sensitive" if matched else "public"
    return {"level": level, "matched_keywords": matched}


def main():
    data = read_input()
    question = data.get("question")
    if not question:
        fail("Input must contain 'question' string")

    config = load_config("security.sensitivity")
    keywords = config.get("sensitive_keywords", [])
    result = check_sensitivity(question, keywords)
    write_output(result)


if __name__ == "__main__":
    main()
