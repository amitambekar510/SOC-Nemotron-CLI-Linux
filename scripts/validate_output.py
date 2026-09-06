#!/usr/bin/env python3
"""Validate artifact syntax, not detection quality or factual accuracy."""
import argparse
import json
from pathlib import Path
import yaml

SUFFIXES = {'.md', '.json', '.yaml', '.yml', '.kql', '.spl'}

def artifacts(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError('Artifact directory does not exist')
    files = sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in SUFFIXES and p.name != 'manifest.json')
    if not files:
        raise ValueError('No supported artifacts found')
    return files

def validate_file(path):
    content = path.read_text(encoding='utf-8')
    if not content.strip():
        raise ValueError(f'Empty artifact: {path.name}')
    if path.suffix.lower() == '.json':
        json.loads(content)
    elif path.suffix.lower() in {'.yaml', '.yml'}:
        if not isinstance(yaml.safe_load(content), dict):
            raise ValueError(f'Expected YAML mapping: {path.name}')
    return content

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', default='./output')
    args = parser.parse_args(argv)
    try:
        files = artifacts(args.path)
        for path in files:
            validate_file(path)
        print(f'Syntax checks passed: {len(files)} artifacts. Analyst review is still required.')
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f'Validation failed: {type(exc).__name__}')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
