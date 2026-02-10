#!/usr/bin/env python3
"""
Sanitize LLM response content by stripping injection and self-ID patterns.

Input (stdin JSON):  {"content": "..."}
Output (stdout JSON): {"sanitized": "...", "stripped_patterns": [...]}

Config: protocols/standard.yaml -> security.sanitization + security.self_id_stripping
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.io_helpers import read_input, write_output, fail, load_config


def sanitize(content, injection_patterns, self_id_patterns):
    """Strip injection and self-ID patterns from content."""
    stripped = []
    result = content

    # Strip injection patterns
    for pattern in injection_patterns:
        for m in re.finditer(pattern, result):
            stripped.append(f"injection: {m.group()}")
        result = re.sub(pattern, "", result)

    # Strip self-identification
    for pattern in self_id_patterns:
        for m in re.finditer(pattern, result):
            stripped.append(f"self_id: {m.group()}")
        result = re.sub(pattern, "", result)

    # Clean up whitespace
    result = re.sub(r"  +", " ", result).strip()

    return {"sanitized": result, "stripped_patterns": stripped}


def main():
    data = read_input()
    content = data.get("content")
    if content is None:
        fail("Input must contain 'content' string")

    san_config = load_config("security.sanitization")
    sid_config = load_config("security.self_id_stripping")

    injection_patterns = san_config.get("patterns", [])
    self_id_patterns = sid_config.get("patterns", [])

    result = sanitize(content, injection_patterns, self_id_patterns)
    write_output(result)


if __name__ == "__main__":
    main()
