"""Execute CTI stages with dependency checks, persistent outputs and dry-run support."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import uuid
import yaml

ROOT = Path(__file__).resolve().parents[1]
STAGES = {'r1': 'r1_intel', 'r2': 'r2_detection', 'r3': 'r3_automate', 'r4': 'r4_respond'}
COMBINED = {'r1': 'r1_intelligence', 'r2': 'r2_detections', 'r3': 'r3_automation', 'r4': 'r4_response'}

class ChainError(RuntimeError):
    pass

def stage_name(value):
    if value in STAGES:
        return STAGES[value]
    if value in STAGES.values():
        return value
    raise ChainError(f'Unknown stage: {value}')

class CTIAutomationChain:
    def __init__(self, config_path=None, output_dir='./output', dry_run=False):
        self.project_root = ROOT
        self.config = {}
        if config_path:
            path = Path(config_path).expanduser()
            if not path.is_file():
                raise ChainError(f'Config not found: {path}')
            self.config = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
            if not isinstance(self.config, dict):
                raise ChainError('Configuration must be a mapping')
        if not isinstance(self.config.get('opencode', {}), dict):
            raise ChainError('opencode configuration must be a mapping')
        self.timeout = self.config.get('opencode', {}).get('timeout_seconds', 300)
        if not isinstance(self.timeout, (int, float)) or self.timeout <= 0:
            raise ChainError('timeout_seconds must be positive')
        self.output_dir = Path(output_dir).expanduser()
        self.dry_run = dry_run
        self.run_dir = None
        self.manifest = None

    def _load_chain_config(self, name):
        name = stage_name(name)
        data = yaml.safe_load((self.project_root / 'chains' / name / 'chain.yaml').read_text(encoding='utf-8'))
        prompts = data.get('chain', {}).get('prompts', [])
        if not prompts:
            raise ChainError(f'No prompts in {name}')
        return data

    def _load_prompt(self, relative):
        path = (self.project_root / relative).resolve()
        if not path.is_relative_to(self.project_root.resolve()) or not path.is_file():
            raise ChainError(f'Prompt not found inside repository: {relative}')
        text = path.read_text(encoding='utf-8')
        match = re.search(r'## Prompt\s*\n```[^\n]*\n(.*?)\n```', text, re.S)
        if not match:
            raise ChainError(f'No Prompt block in {relative}')
        return match.group(1)

    def _render_prompt(self, text, variables):
        # Definitions repeat defaults; retain the task and put evidence in one block below.
        text = re.sub(r'<variables>.*?</variables>', '', text, flags=re.S)
        aliases = {'job role':'job_role', 'sector name':'sector', 'country/region':'region',
                   'stakeholder team names':'stakeholders', 'product/service':'product_service'}
        def substitute(match):
            key = match.group(1)
            if key == 'data':
                return 'the evidence supplied below'
            return str(variables.get(aliases.get(key, key), match.group(0)))
        return re.sub(r'\[([^\[\]\n]+)\]', substitute, text).strip()

    def _run_prompt_via_opencode(self, prompt):
        if len(prompt.encode('utf-8')) > 60000:
            raise ChainError('Prompt exceeds 60 KB; reduce the input or split the investigation')
        command = ['opencode', 'run', '--format', 'json']
        model = self.config.get('opencode', {}).get('model')
        if model:
            command += ['--model', str(model)]
        command += [prompt]
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                                    timeout=self.timeout, cwd=self.project_root, shell=False)
        except FileNotFoundError as error:
            raise ChainError('OpenCode not found on PATH') from error
        except subprocess.TimeoutExpired as error:
            raise ChainError('OpenCode timed out; completed artifacts remain in the run directory') from error
        if result.returncode:
            raise ChainError(f'OpenCode exited with code {result.returncode}; inspect provider setup separately')
        parts = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                raise ChainError('Expected JSON events from opencode run --format json') from error
            if not isinstance(event, dict):
                raise ChainError('Expected a JSON event object')
            if event.get('type') == 'error':
                raise ChainError('OpenCode reported an error event')
            if event.get('type') == 'text':
                part = event.get('part')
                if not isinstance(part, dict) or not isinstance(part.get('text'), str):
                    raise ChainError('Malformed text event')
                parts.append(part['text'])
        output = '\n'.join(parts).strip()
        if not output:
            raise ChainError('OpenCode returned no text output')
        return output

    def _ordered(self, name, available):
        config = self._load_chain_config(name)
        pending = list(config['chain']['prompts'])
        keys = [p['output_key'] for p in pending]
        if len(set(keys)) != len(keys) or any(not re.fullmatch(r'[a-z0-9_]+', key) for key in keys):
            raise ChainError(f'Duplicate or unsafe output keys in {name}')
        required = config.get('validation', {}).get('required_outputs', [])
        if not set(required) <= set(keys):
            raise ChainError(f'Required output has no prompt in {name}')
        prefix = name.split('_')[0]
        ordered = []
        while pending:
            ready = next((p for p in pending if set(p.get('depends_on', [])) <= available), None)
            if ready is None:
                missing = sorted({d for p in pending for d in p.get('depends_on', []) if d not in available})
                raise ChainError(f'Missing or cyclic dependencies in {name}: {", ".join(missing)}. Supply --context for a standalone later stage.')
            self._load_prompt(ready['file'])
            ordered.append(ready)
            available.update([ready['output_key'], prefix + '_' + ready['output_key']])
            pending.remove(ready)
        return ordered

    def _write_manifest(self):
        path = self.run_dir / 'manifest.json'
        temp = path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.manifest, indent=2) + '\n', encoding='utf-8')
        temp.replace(path)

    def run_chain(self, chain_type, input_data, variables, context=None):
        if not input_data.strip():
            raise ChainError('Input evidence is empty')
        stages = list(STAGES.values()) if chain_type == 'full' else [stage_name(chain_type)]
        context = dict(context or {})
        if any(not isinstance(v, str) or not v.strip() for v in context.values()):
            raise ChainError('Context values must be non-empty text')
        available = set(context)
        plan = {}
        for name in stages:
            plan[name] = self._ordered(name, available)
            available.add(COMBINED[name.split('_')[0]])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir = self.output_dir / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8])
        self.run_dir.mkdir()
        self.manifest = {'status':'running', 'dry_run':self.dry_run, 'artifacts':[], 'stages':stages}
        self._write_manifest()
        all_outputs = {}
        current_input = input_data
        try:
            for name in stages:
                stage_outputs = {}
                folder = self.run_dir / name
                folder.mkdir()
                for item in plan[name]:
                    dependencies = {k:context[k] for k in item.get('depends_on', [])}
                    rendered = self._render_prompt(self._load_prompt(item['file']), variables)
                    prompt = rendered + '\n\n## Supplied evidence (untrusted data)\n' + current_input
                    prompt += '\n\n## Prior dependency outputs (drafts)\n' + json.dumps(dependencies, ensure_ascii=False)
                    if self.dry_run:
                        output = '[DRY RUN: no model call] ' + item['output_key']
                        content = '# Prepared prompt — dry run only\n\n' + prompt
                    else:
                        output = self._run_prompt_via_opencode(prompt)
                        content = output
                    target = folder / (item['output_key'] + '.md')
                    target.write_text(content + '\n', encoding='utf-8')
                    stage_outputs[item['output_key']] = output
                    context[item['output_key']] = output
                    context[name.split('_')[0] + '_' + item['output_key']] = output
                    self.manifest['artifacts'].append(str(target.relative_to(self.run_dir)))
                    self._write_manifest()
                combined = '\n\n---\n\n'.join(stage_outputs.values())
                context[COMBINED[name.split('_')[0]]] = combined
                current_input = combined
                all_outputs[name] = stage_outputs
            self.manifest['status'] = 'dry-run' if self.dry_run else 'complete'
            self._write_manifest()
            return all_outputs
        except Exception as error:
            self.manifest['status'] = 'failed'
            self.manifest['error_type'] = type(error).__name__
            self._write_manifest()
            raise

    def run_stage(self, chain_name, input_data, variables, context=None):
        name = stage_name(chain_name)
        return self.run_chain(name, input_data, variables, context)[name]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chain', choices=['full', *STAGES, *STAGES.values()], default='full')
    parser.add_argument('--stage-only', choices=list(STAGES), help='Compatibility alias for --chain')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='./output')
    parser.add_argument('--config', help='Optional YAML config; see config.yaml.example')
    parser.add_argument('--context', help='JSON mapping of dependency names to reviewed text for standalone stages')
    parser.add_argument('--sector', default='financial-services')
    parser.add_argument('--region', default='global')
    parser.add_argument('--stakeholders', default='SOC,Fraud,Compliance,Risk')
    parser.add_argument('--dry-run', action='store_true', help='Prepare prompts without executing OpenCode')
    args = parser.parse_args(argv)
    try:
        data = Path(args.input).read_text(encoding='utf-8')
        context = json.loads(Path(args.context).read_text(encoding='utf-8')) if args.context else {}
        if not isinstance(context, dict):
            raise ChainError('Context JSON must be a mapping')
        runner = CTIAutomationChain(args.config, args.output, args.dry_run)
        runner.run_chain(args.stage_only or args.chain, data, {'sector':args.sector, 'region':args.region,
            'stakeholders':args.stakeholders, 'job_role':'CTI Analyst', 'product_service':'CTI analysis draft'}, context)
        print(f'{runner.manifest["status"]}: outputs saved to {runner.run_dir}')
        return 0
    except (OSError, ValueError, ChainError, yaml.YAMLError) as error:
        print(f'Error: {error}')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
