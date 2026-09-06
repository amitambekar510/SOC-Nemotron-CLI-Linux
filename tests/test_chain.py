import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_chain import CTIAutomationChain, ChainError
from scripts import validate_output, generate_dashboard, import_to_elk

class ChainTests(unittest.TestCase):
    def test_full_dry_run(self):
        with tempfile.TemporaryDirectory() as folder:
            runner = CTIAutomationChain(output_dir=folder, dry_run=True)
            with patch('scripts.run_chain.subprocess.run') as call:
                results = runner.run_chain('full', 'EVIDENCE_SENTINEL', {'sector':'TEST_SECTOR'})
            call.assert_not_called()
            self.assertEqual(sum(map(len, results.values())), 31)
            self.assertEqual(runner.manifest['status'], 'dry-run')
            self.assertEqual(len(runner.manifest['artifacts']), 31)
            first = runner.run_dir / runner.manifest['artifacts'][0]
            self.assertIn('EVIDENCE_SENTINEL', first.read_text(encoding='utf-8'))
            self.assertIn('TEST_SECTOR', first.read_text(encoding='utf-8'))
            self.assertEqual(validate_output.main(['--path', str(runner.run_dir)]), 0)

    def test_short_stage_failure_persists_partial_results(self):
        with tempfile.TemporaryDirectory() as folder:
            runner = CTIAutomationChain(output_dir=folder)
            with patch.object(runner, '_run_prompt_via_opencode', side_effect=['first draft', ChainError('failed')]):
                with self.assertRaises(ChainError): runner.run_chain('r1', 'evidence', {})
            manifest = json.loads((runner.run_dir/'manifest.json').read_text())
            self.assertEqual(manifest['status'], 'failed')
            self.assertEqual(len(manifest['artifacts']), 1)

    def test_missing_dependencies_fail_before_calls(self):
        with tempfile.TemporaryDirectory() as folder:
            runner = CTIAutomationChain(output_dir=Path(folder)/'unused')
            with patch.object(runner, '_run_prompt_via_opencode') as call:
                with self.assertRaisesRegex(ChainError, 'dependencies'): runner.run_chain('r2', 'evidence', {})
            call.assert_not_called()
            self.assertFalse(runner.output_dir.exists())

    def test_opencode_command_and_errors(self):
        runner = CTIAutomationChain()
        event = json.dumps({'type':'text','part':{'text':'reviewed draft'}})
        with patch('scripts.run_chain.subprocess.run', return_value=subprocess.CompletedProcess([],0,event,'')) as call:
            self.assertEqual(runner._run_prompt_via_opencode('input'), 'reviewed draft')
            self.assertEqual(call.call_args.args[0][:4], ['opencode','run','--format','json'])
            self.assertFalse(call.call_args.kwargs['shell'])
        for code, output in [(1,''),(0,''),(0,'[]'),(0,'{"type":"error"}'),(0,'not json')]:
            with patch('scripts.run_chain.subprocess.run', return_value=subprocess.CompletedProcess([],code,output,'')):
                with self.assertRaises(ChainError): runner._run_prompt_via_opencode('input')
        with patch('scripts.run_chain.subprocess.run', side_effect=subprocess.TimeoutExpired('opencode',1)):
            with self.assertRaisesRegex(ChainError,'timed out'): runner._run_prompt_via_opencode('input')

    def test_invalid_artifacts(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(validate_output.main(['--path',folder]),1)
            path=Path(folder)/'bad.json'; path.write_text('{')
            self.assertEqual(validate_output.main(['--path',folder]),1)
            path.unlink(); (Path(folder)/'bad.yml').write_text('- not a mapping')
            self.assertEqual(validate_output.main(['--path',folder]),1)

    def test_dashboard_escaping_and_stable_import_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'artifacts';root.mkdir()
            (root/'report.md').write_text('<script>alert(1)</script>',encoding='utf-8')
            (root/'rule.yml').write_text('title: Example\ndetection: {}\n',encoding='utf-8')
            target=generate_dashboard.generate(root,Path(folder)/'review.html')
            html=target.read_text(encoding='utf-8')
            self.assertNotIn('<script>',html)
            self.assertIn('&lt;script&gt;',html)
            indices=dict(sigma='sigma',playbook='reports',kql='kql',spl='spl')
            first=import_to_elk.prepare(root,indices)
            self.assertEqual(len(first),2)
            self.assertEqual(first,import_to_elk.prepare(root,indices))
            with patch('scripts.import_to_elk.build_opener') as call:
                self.assertEqual(import_to_elk.main(['--path',str(root),'--dry-run']),0)
            call.assert_not_called()

    def test_partial_import_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ('one','two'): (Path(folder)/(name+'.md')).write_text('draft')
            with patch('scripts.import_to_elk.build_opener') as factory:
                response=factory.return_value.open.return_value.__enter__.return_value
                response.status=201
                factory.return_value.open.side_effect=[factory.return_value.open.return_value, OSError('failed')]
                self.assertEqual(import_to_elk.main(['--path',folder,'--host','https://example.invalid','--api-key','test']),1)

if __name__ == '__main__': unittest.main()
