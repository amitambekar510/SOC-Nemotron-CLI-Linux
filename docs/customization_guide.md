# Customization

Edit `examples/workflows.json` to change browser workflows; run `python3 scripts/build_workbench.py` to regenerate browser data and Markdown templates together.

For the CTI chain, edit the appropriate `chains/*/chain.yaml`. Each prompt needs a repository-relative `file`, a unique lowercase `output_key`, and a `depends_on` list. Dependencies may reference earlier stage aggregates (`r1_intelligence`, `r2_detections`, `r3_automation`) or stage-prefixed keys such as `r2_validation_handoff`. Same-stage keys are also available. Cycles and missing prerequisites fail preflight.

Prompt documents must contain a fenced block under `## Prompt`. The runner substitutes `[sector name]`, `[country/region]`, `[stakeholder team names]`, `[job role]` and `[product/service]`, then appends evidence and dependency drafts. Evidence is inserted once, without recursively interpreting its placeholder-like text.

Optional configuration:

```bash
cp config.yaml.example config.yaml
.venv/bin/python scripts/run_chain.py --config config.yaml --chain r1 --input examples/intel-report.md --dry-run
```

Supported settings are `opencode.timeout_seconds` and optional `opencode.model` in provider/model format. Credentials belong in OpenCode, not this file. Old retry, output-format and ELK configuration keys are not implemented; use documented CLI flags instead.

Run the automated suite after changing dependencies or prompt keys. Use a full dry run to check the entire graph before any paid inference.
