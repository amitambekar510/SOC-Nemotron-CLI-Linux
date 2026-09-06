"""Generate browser data and Markdown prompts from one workflow catalog."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def outputs():
    workflows = json.loads((ROOT / 'examples/workflows.json').read_text())
    seen = set()
    result = {}
    for item in workflows:
        if not re.fullmatch(r'[a-z][a-z-]*', item['id']) or item['id'] in seen:
            raise ValueError('Invalid or duplicate workflow ID')
        seen.add(item['id'])
        keys = [f['key'] for f in item['fields']]
        if len(set(keys)) != len(keys) or set(keys) != set(re.findall(r'\{\{([A-Z_]+)\}\}', item['prompt'])):
            raise ValueError('Workflow fields must match prompt placeholders')
        content = '# ' + item['title'] + '\n\n' + item['description'] + '\n\n## Prompt\n\n```text\n' + item['prompt'] + '\n```\n\n## Review\n\n'
        content += '\n'.join('- ' + line for line in item['review']) + '\n\nFill in the placeholders and paste the prompt into an OpenCode session.\n'
        result['examples/prompts/' + item['id'] + '.md'] = content
    result['workbench/dist/workflows.js'] = 'window.SOC_WORKFLOWS = ' + json.dumps(workflows, ensure_ascii=True, indent=2) + ';\n'
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for name, content in outputs().items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    if stale:
        raise SystemExit('Regenerate with python3 scripts/build_workbench.py: ' + ', '.join(stale))
    print('Workflow catalog and generated files are consistent.')

if __name__ == '__main__':
    main()
