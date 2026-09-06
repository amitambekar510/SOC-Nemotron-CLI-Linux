# Chain operations

The repository retains 44 source prompts attributed in their original documents. The YAML chains schedule 31 of them: R1 intelligence (10), R2 detection (8), R3 automation (7), and R4 response (6). The browser workbench is a separate prompt preparation interface; it does not execute this chain.

## Prepare and run

Use Python 3.10+ and install `requirements.txt` in a virtual environment. Run from the repository root:

```bash
.venv/bin/python scripts/run_chain.py --chain full --input examples/intel-report.md --output output --dry-run
```

Inspect the prepared Markdown files before removing `--dry-run`. A live run invokes `opencode run --format json` once per scheduled prompt, using the provider configured in OpenCode. The subprocess runs from the repository root. Review its OpenCode configuration and permissions before execution. No tool permissions are automatically granted by this runner. Use a small, approved input first; 31 sequential model requests can incur costs.

Stage dependencies are checked before any model call. Prompts within a stage are ordered by dependencies; R4 executive briefing runs before the situation report that consumes it. R3 awareness now uses intelligence and current Sigma drafts instead of an unavailable future R4 briefing.

Each prompt receives the current stage evidence and its explicitly named dependency outputs. The original input feeds R1; later stages receive the previous stage's combined draft output. Generated content remains unverified and can propagate errors, so review the output before operational use.

## Outputs and failures

`--output` chooses the parent folder. Each invocation creates a unique timestamp/ID directory. Individual responses are persisted as `.md`, even when they contain embedded JSON, YAML, KQL or SPL blocks. Extract and review those blocks separately before format-specific validation or deployment.

`manifest.json` records completed artifacts and one of `running`, `dry-run`, `complete`, or `failed`. A failed model call stops execution, preserves completed files, and exits nonzero. There is no automatic resume or retry. A new invocation creates a new directory. Nonzero exit, missing executable, timeout, malformed events and empty responses are failures. Prompts over 60 KB are rejected before launching OpenCode.

## Individual stages

Both `--chain r1` and `--chain r1_intel` work. The wrapper also supports:

```bash
.venv/bin/python scripts/run_stage.py r1 --input examples/intel-report.md --output output --dry-run
```

Later standalone stages require `--context context.json`, a JSON object mapping dependency names listed in the selected chain YAML to reviewed text. Missing dependencies are reported before execution. `--stage-only r1` is a compatibility alias. Do not invent empty context to bypass a missing prerequisite.

## Review dashboard and Elasticsearch

```bash
.venv/bin/python scripts/validate_output.py --path output/RUN_DIRECTORY
.venv/bin/python scripts/generate_dashboard.py --path output/RUN_DIRECTORY --output dashboards/review.html
.venv/bin/python scripts/import_to_elk.py --path output/RUN_DIRECTORY --dry-run
```

The local HTML dashboard provides actual file counts and expandable escaped text. It replaces the broken prototype Kibana export; it is **not a Kibana saved object**. Syntax validation checks nonempty text, JSON parsing and YAML mappings. It does not validate Sigma schema, query correctness, ATT&CK mappings or factual accuracy.

For an approved Elasticsearch import, set `ELK_API_KEY` using your secret manager and provide `--host https://YOUR_HOST:9200`. The importer validates all files before sending, uses verified TLS by default, refuses redirects and uses deterministic document IDs. Reimporting the same relative path overwrites that document; distinct runs with identical relative paths also overwrite it in the same index. Select different index names when retaining separate runs.

The importer stores Markdown, YAML/YML, `.kql` and `.spl` as text documents. JSON manifests are not imported. It does not deploy detections. Here `.kql` means Microsoft Sentinel Kusto query text, not Elastic Kibana Query Language. Partial network failures exit nonzero and report the count already indexed. There is no rollback. The legacy `--all` flag is accepted; all supported types are already the default.
