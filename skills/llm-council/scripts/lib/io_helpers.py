"""
Shared I/O helpers for LLM Council scripts.

Contract: stdin JSON -> stdout JSON. Errors: {"error": msg} + exit(1).
"""

import json
import sys
from pathlib import Path

from .yaml_parser import load_yaml, extract_section

# Resolve standard.yaml relative to this file's location
_LIB_DIR = Path(__file__).parent
_PROTOCOLS_DIR = _LIB_DIR.parent.parent / "protocols"
_DEFAULT_CONFIG = _PROTOCOLS_DIR / "standard.yaml"


def read_input():
    """Read JSON from stdin."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON input: {e}")
    if not isinstance(data, dict):
        fail("Input must be a JSON object")
    return data


def write_output(data):
    """Write JSON to stdout."""
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def fail(message):
    """Write error JSON to stdout and exit."""
    json.dump({"error": message}, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.exit(1)


def load_config(section_dotpath, config_path=None):
    """Load standard.yaml and extract a section by dot-path.

    Args:
        section_dotpath: e.g. "llm_tool_detection.thresholds"
        config_path: override path to YAML file (default: protocols/standard.yaml)

    Returns:
        The extracted section value, or calls fail() if not found.
    """
    path = Path(config_path) if config_path else _DEFAULT_CONFIG
    if not path.exists():
        fail(f"Config file not found: {path}")
    config = load_yaml(path)
    section = extract_section(config, section_dotpath)
    if section is None:
        fail(f"Config section not found: {section_dotpath}")
    return section
