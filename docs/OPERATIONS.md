# Analyst operating notes

## First successful run

1. Start the local workbench and choose IOC extraction.
2. Use sample inputs, then change filenames to match your approved workspace.
3. Configure OpenCode and verify the selected model.
4. Copy `examples/sample.log` into that workspace.
5. Paste the prepared prompt into OpenCode.
6. Compare the response with the original two log lines. An address appearing in a log is not a reputation verdict.
7. Save only reviewed output, separate from evidence.

## Review before sharing a result

- Are the source records and relevant timestamps identifiable?
- Does the response distinguish facts, assumptions, and missing information?
- Do proposed detections fit the actual telemetry and pass benign tests?
- Are original evidence and generated drafts kept separate?
- Has sensitive information been removed before external sharing?

## Capabilities and boundaries

The local workbench prepares text without uploads, AI requests, browser persistence, or shell execution. OpenCode is the separate execution layer. It may read files and call tools according to its own configuration.

Network triage expects a packet metadata export; memory triage expects existing forensic-tool output. Neither is a binary parser. The templates request drafts and evidence references, but prompt instructions are not a security boundary.

Use the included permission configuration as a starting point and review the effective settings for your environment. Provider availability and billing are independent of this project.

## Learning progression

- Start with synthetic logs and IOC extraction.
- Draft and locally validate a detection rule.
- Compare model summaries with known packet or forensic exports.
- Document an approved team workflow before using real cases.

## Documentation references

Reviewed 2026-09-05: [OpenCode CLI](https://opencode.ai/docs/cli/), [configuration](https://opencode.ai/docs/config/), [NVIDIA provider](https://opencode.ai/docs/providers/#nvidia), and [web interface](https://opencode.ai/docs/web/).

