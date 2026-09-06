#!/usr/bin/env python3
"""Create a local HTML artifact review dashboard (not a Kibana saved object)."""
import argparse
from collections import Counter
from html import escape
from pathlib import Path
try:
    from .validate_output import artifacts, validate_file
except ImportError:
    from validate_output import artifacts, validate_file
import yaml

def generate(root, destination, suffixes=None):
    root = Path(root)
    files = [p for p in artifacts(root) if suffixes is None or p.suffix.lower() in suffixes]
    if not files:
        raise ValueError('No artifacts match the selected categories')
    cards = []
    for path in files:
        content = validate_file(path)
        cards.append(f'<details><summary>{escape(path.relative_to(root).as_posix())}</summary><pre>{escape(content)}</pre></details>')
    counts = Counter(p.suffix.lower() for p in files)
    metrics = ''.join(f'<div class="metric"><strong>{count}</strong>{escape(kind)} artifacts</div>' for kind, count in sorted(counts.items()))
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'"><title>CTI artifact review</title><style>
body{margin:0;background:#0a1220;color:#e8eef7;font:16px/1.6 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:48px 24px}small{color:#69e3b3;letter-spacing:.12em}h1{font-size:clamp(28px,5vw,48px);line-height:1.2}p{color:#bac9db}.metrics{display:flex;flex-wrap:wrap;gap:16px;margin:32px 0}.metric{background:#142235;border:1px solid #35506b;border-radius:12px;padding:18px;min-width:120px}strong{display:block;font-size:32px;color:#69e3b3}details{margin:12px 0;border:1px solid #35506b;border-radius:8px}summary{padding:18px;cursor:pointer;overflow-wrap:anywhere}summary:focus-visible{outline:3px solid #69e3b3}pre{padding:20px;background:#080e18;white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 monospace}
</style><main><small>THE SAFEHOUSE / CTI OPERATIONS</small><h1>Artifact review desk</h1><p>Local inventory of generated drafts. Counts describe files, not confirmed threats or validated detections. Expand an artifact to inspect its source text.</p><section class="metrics">'''+metrics+'</section>'+''.join(cards)+'</main></html>'
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding='utf-8')
    return destination

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--path', default='./output')
    p.add_argument('--output', default='dashboards/review.html')
    for flag in ('all', 'sigma', 'kql', 'playbooks'):
        p.add_argument('--'+flag, action='store_true')
    args = p.parse_args(argv)
    selected = set()
    if args.sigma: selected.update({'.yaml', '.yml'})
    if args.kql: selected.add('.kql')
    if args.playbooks: selected.add('.md')
    try:
        print(generate(args.path, args.output, None if args.all or not selected else selected))
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f'Dashboard failed: {type(exc).__name__}')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
