"""Report local prerequisites without reading secrets or calling a provider."""
import json
from pathlib import Path
import shutil
import sys

def main():
    root = Path(__file__).resolve().parents[1]
    config = root / 'examples/opencode.config.json'
    json.loads(config.read_text())
    print(f'Python: {sys.version.split()[0]}')
    print('Workbench: ' + ('available' if (root / 'workbench/dist/index.html').is_file() else 'missing'))
    print('Example config: valid JSON (not a provider connection test)')
    print('OpenCode: ' + ('found on PATH' if shutil.which('opencode') else 'not found; only needed to run AI prompts'))
    print('Provider authentication and model access: not tested')

if __name__ == '__main__':
    main()
