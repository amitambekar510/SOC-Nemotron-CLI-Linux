import importlib.util
import json
from pathlib import Path
import re
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen
from functools import partial
from http.server import ThreadingHTTPServer
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workbench', ROOT / 'scripts/workbench.py')
workbench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workbench)

class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and 'src' in attrs:
            self.paths.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.paths.append(attrs['href'])

class ProjectTests(unittest.TestCase):
    def test_static_assets_exist(self):
        parser = References()
        parser.feed((workbench.ROOT / 'index.html').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(parser.paths), 4)
        for name in parser.paths:
            self.assertTrue((workbench.ROOT / name).is_file(), name)

    def test_readme_relative_references(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)|src="([^"]+)"', readme):
            path = next(part for part in target if part)
            if path.startswith(('http:', 'https:', '#')):
                continue
            self.assertTrue((ROOT / path.split('#')[0]).exists(), path)

    def test_config_uses_environment_reference(self):
        config = json.loads((ROOT / 'examples/opencode.config.json').read_text(encoding='utf-8'))
        self.assertEqual(config['provider']['nvidia']['options']['apiKey'], '{env:NVIDIA_API_KEY}')
        self.assertEqual(config['permission'], {'edit': 'ask', 'bash': 'ask'})

    def test_server_serves_only_workbench(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(workbench.Handler, directory=str(workbench.ROOT)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with urlopen(base + '/') as response:
                self.assertIn(b'SOC WORKBENCH', response.read())
                self.assertIn("connect-src 'none'", response.headers['Content-Security-Policy'])
            for path in ['/README.md', '/../../examples/workflows.json', '/%2e%2e/%2e%2e/examples/workflows.json']:
                with self.assertRaises(HTTPError) as error:
                    urlopen(base + path)
                self.assertEqual(error.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

if __name__ == '__main__':
    unittest.main()
