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

sys.path.insert(0, str(Path(__file__).parent))
from lib.yaml_parser import load_yaml

SCRIPT_DIR = Path(__file__).parent
RUBRICS_DIR = SCRIPT_DIR.parent / "rubrics"
OUTPUT_FILE = SCRIPT_DIR.parent / "rubrics_index.json"


def build_index() -> dict:
    """Build index from all rubric YAML files."""
    index = {}

    for filepath in sorted(RUBRICS_DIR.glob("*.yaml")):
        data = load_yaml(filepath)

        rubric_id = data.get('id', filepath.stem)
        description = data.get('description', '')
        if isinstance(description, str):
            description = description.split('\n')[0][:200]

        index[rubric_id] = {
            'keywords': data.get('detection_keywords', []),
            'description': description,
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
