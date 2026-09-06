# Chain troubleshooting

| Symptom | Action |
| --- | --- |
| Missing `yaml` module | Install `requirements.txt` with the same virtual-environment Python used to run the script |
| Missing or cyclic dependencies | Check `depends_on`; for standalone R2/R3/R4, supply reviewed dependency text through `--context` |
| Config not found | Omit optional `--config`, or copy `config.yaml.example` and pass its actual path |
| OpenCode not found | Verify `opencode --version` in the same shell |
| Model error or empty response | Check provider authentication and model selection interactively; inspect completed files and manifest |
| Timeout | Reduce evidence or set `opencode.timeout_seconds`; the runner does not automatically retry |
| Prompt exceeds 60 KB | Split the investigation into smaller reviewed inputs |
| No output directory | Preflight may have failed before any run was created; read the error and exit status |
| Dashboard cannot find files | Pass the actual run directory; supported inputs are Markdown, JSON, YAML/YML, KQL and SPL |
| Kibana rejects dashboard | The replacement dashboard is local HTML, not an importable Kibana saved object |
| Elasticsearch import fails | First run `--dry-run`; then check HTTPS host, API-key index permissions and certificates |

A successful process exit or syntax check is not proof of model accuracy. Validate generated artifacts against evidence and the target detection platform.
