#!/usr/bin/env python3
"""
Build rubric index for fast keyword matching in Stage 0.5.

Usage:
    python scripts/build_rubric_index.py

Run this script after modifying any rubrics/*.yaml file.
The output rubrics_index.json should be committed to version control.
"""

import json
import sys
from pathlib import Path

# PyYAML is optional - use simple parser if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

SCRIPT_DIR = Path(__file__).parent
RUBRICS_DIR = SCRIPT_DIR.parent / "rubrics"
OUTPUT_FILE = SCRIPT_DIR.parent / "rubrics_index.json"


def parse_yaml_simple(content: str) -> dict:
    """Simple YAML parser for our rubric format (no nested structures needed)."""
    result = {}
    current_list_key = None
    current_list = []

    for line in content.split('\n'):
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Handle list items
        if stripped.startswith('- '):
            if current_list_key:
                current_list.append(stripped[2:].strip().strip('"\''))
            continue

        # Save previous list if any
        if current_list_key and current_list:
            result[current_list_key] = current_list
            current_list = []
            current_list_key = None

        # Handle key-value pairs
        if ':' in stripped:
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip().strip('"\'')

            if not value:
                # This might be a list or nested structure
                current_list_key = key
                current_list = []
            else:
                result[key] = value

    # Save final list if any
    if current_list_key and current_list:
        result[current_list_key] = current_list

    return result


def parse_yaml(content: str) -> dict:
    """Parse YAML content."""
    if HAS_YAML:
        return yaml.safe_load(content)
    return parse_yaml_simple(content)


def build_index() -> dict:
    """Build index from all rubric YAML files."""
    index = {}

    for filepath in sorted(RUBRICS_DIR.glob("*.yaml")):
        content = filepath.read_text(encoding='utf-8')
        data = parse_yaml(content)

        rubric_id = data.get('id', filepath.stem)
        index[rubric_id] = {
            'keywords': data.get('detection_keywords', []),
            'description': data.get('description', '').split('\n')[0][:200],  # First line, max 200 chars
            'extends': data.get('extends'),
            'file': filepath.name
        }

    return index


def main():
    if not RUBRICS_DIR.exists():
        print(f"Error: Rubrics directory not found: {RUBRICS_DIR}", file=sys.stderr)
        sys.exit(1)

    index = build_index()

    if not index:
        print("Error: No rubric files found", file=sys.stderr)
        sys.exit(1)

    # Write index
    OUTPUT_FILE.write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )

    # Summary
    total_keywords = sum(len(r['keywords']) for r in index.values())
    print(f"✓ Built rubrics_index.json")
    print(f"  - {len(index)} rubrics indexed")
    print(f"  - {total_keywords} total keywords")
    print(f"  - Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
