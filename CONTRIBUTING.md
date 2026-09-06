# Contributing

For workflow changes, edit `examples/workflows.json`, then run:

```bash
python3 scripts/build_workbench.py
python3 scripts/build_workbench.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/workbench.test.cjs
```

Do not edit generated `workbench/dist/workflows.js` or `examples/prompts/*.md` directly.

Use a unique lowercase workflow ID. Every `{{PLACEHOLDER}}` must have exactly one field definition. Supply synthetic sample filenames, a practical description, and verification steps. Keep each prompt focused on one analyst task.

For UI changes, test selection, sample inputs, required fields, copy fallback, download, workflow switching, and reset in a browser. Check keyboard navigation, narrow screens, and 200% zoom. State which platforms you tested in the pull request.

Do not add real evidence, API keys, or generated customer reports. Explain the problem, the resulting behavior, and your verification in each pull request.

