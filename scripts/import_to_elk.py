#!/usr/bin/env python3
"""Index reviewed artifacts as documents; never installs or runs detection rules."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import ssl
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler
from urllib.error import URLError
import yaml
try:
    from .validate_output import artifacts, validate_file
except ImportError:
    from validate_output import artifacts, validate_file

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Elasticsearch redirects are not followed')

def prepare(root, indices):
    root = Path(root)
    result = []
    for path in artifacts(root):
        suffix = path.suffix.lower()
        if suffix == '.json':
            continue
        content = validate_file(path)
        kind = {'.yaml':'sigma', '.yml':'sigma', '.kql':'kql', '.spl':'spl', '.md':'playbook'}[suffix]
        relative = path.relative_to(root).as_posix()
        identifier = hashlib.sha256((kind+':'+relative).encode()).hexdigest()
        # Keep content as text to avoid mapping conflicts between unrelated rule schemas.
        result.append((indices[kind], identifier, {'source':'cti-automation-chain', 'type':kind, 'file_name':relative, 'content':content}))
    if not result:
        raise ValueError('No importable artifacts found')
    return result

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host')
    p.add_argument('--api-key', default=os.environ.get('ELK_API_KEY'), help='Prefer ELK_API_KEY environment variable')
    p.add_argument('--path', default='./output')
    p.add_argument('--rules-index', default='sigma-rules')
    p.add_argument('--kql-index', default='kql-queries')
    p.add_argument('--spl-index', default='spl-queries')
    p.add_argument('--playbook-index', default='cti-playbooks')
    p.add_argument('--all', action='store_true', help='All supported types (also the default)')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--no-verify-certs', action='store_true')
    args = p.parse_args(argv)
    completed = 0
    try:
        indices = dict(sigma=args.rules_index, kql=args.kql_index, spl=args.spl_index, playbook=args.playbook_index)
        if any(not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', value) for value in indices.values()):
            raise ValueError('Use lowercase index names containing letters, digits, hyphens or underscores')
        docs = prepare(args.path, indices)
        if args.dry_run:
            print(f'Dry run: {len(docs)} validated documents; no network requests')
            return 0
        host = urlsplit(args.host or '')
        if host.scheme != 'https' or not host.hostname or host.username or host.password or host.query or host.fragment:
            raise ValueError('Provide an HTTPS host URL without credentials, query or fragment')
        if not args.api_key:
            raise ValueError('Set ELK_API_KEY')
        context = ssl._create_unverified_context() if args.no_verify_certs else ssl.create_default_context()
        opener = build_opener(HTTPSHandler(context=context), NoRedirect())
        for index, identifier, doc in docs:
            req = Request(args.host.rstrip('/')+'/'+index+'/_doc/'+identifier, data=json.dumps(doc).encode(), method='PUT', headers={'Authorization':'ApiKey '+args.api_key, 'Content-Type':'application/json'})
            with opener.open(req, timeout=60) as response:
                if response.status not in (200, 201):
                    raise ValueError('Unexpected indexing response')
            completed += 1
        print(f'Indexed {completed} documents; no detection rules deployed')
        return 0
    except (OSError, ValueError, URLError, yaml.YAMLError) as exc:
        print(f'Import failed ({type(exc).__name__}); {completed} documents indexed. Check host, credentials and input syntax.')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
