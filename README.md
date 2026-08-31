<div align="center">

# 🛡️ SOC-Nemotron-CLI-Linux

### Terminal-Based AI-Assisted Cybersecurity Operations
**Powered by NVIDIA Nemotron 3 Ultra (550B) + OpenCode CLI**

[![Platform](https://img.shields.io/badge/platform-Linux-FCC624?logo=linux&logoColor=black)](#-platform-support)
[![Status](https://img.shields.io/badge/status-partially--verified-brightgreen)](#)
[![Model](https://img.shields.io/badge/model-Nemotron%203%20Ultra%20550B-76B900?logo=nvidia&logoColor=white)](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)
[![CLI](https://img.shields.io/badge/agent-OpenCode%20CLI-blue)](https://opencode.ai/docs/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

</div>

---

## 📑 Table of Contents

- [About This Project](#-about-this-project)
- [Why This Stack](#-why-this-stack)
- [Platform Support](#-platform-support)
- [Repository Structure](#-repository-structure)
- [Skill-Level Operational Mapping](#-skill-level-operational-mapping)
- [Setup & Authentication](#-setup--authentication-linux)
- [Verify Your Installation](#-verify-your-installation)
- [Example Prompts by Use Case](#-example-prompts-by-use-case)
- [Sample Output (Illustrative)](#-sample-output-illustrative)
- [Rate Limits & Cost Notes](#-rate-limits--cost-notes)
- [Troubleshooting](#-troubleshooting-linux)
- [Uninstall / Disconnect](#-uninstall--disconnect)
- [Security & Operational Guidelines](#-security--operational-guidelines)
- [Official Reference Links](#-official-reference-links)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Source & Learning Notes](#-source--learning-notes)
- [Author](#-author)
- [License](#-license)

---

## 📖 About This Project

**SOC-Nemotron-CLI-Linux** is the Linux edition of my [SOC-Nemotron-CLI](https://github.com/amitambekar510) project — a hands-on operational guide and prompt library for **Security Operations Center (SOC) Analysts, Threat Hunters, Detection Engineers, and Incident Responders** to leverage **NVIDIA Nemotron 3 Ultra (550B)** — a free, hosted, agentic-reasoning LLM — directly from a Linux terminal via **OpenCode CLI**.

This repository is part of my ongoing self-study into **emerging AI tooling in the cybersecurity space**, adapted for Linux-based SOC analyst workstations and servers — no local GPU required.

> 📚 Compiled for study/reference purposes, adapting the original macOS-tested guide for Linux.

---

## 🚀 Why This Stack

- **Terminal-native** — stays inside the analyst's existing workflow instead of switching to a browser chat window mid-investigation.
- **Agentic, not just chat** — OpenCode can read files, run scripts, iterate on errors, and write output artifacts autonomously (`--loop` mode).
- **1M-token context** — large enough to ingest full log files, PCAP metadata dumps, or multi-file evidence sets in a single pass.
- **No local GPU required** — Nemotron 3 Ultra runs on NVIDIA's hosted endpoint, so a standard Linux analyst workstation is enough.
- **Scriptable & pipeline-friendly** — CLI-based, so it can be chained into shell scripts, cron jobs, or existing SOC automation on Linux servers — a natural fit given how much SOC tooling already runs on Linux.

---

## 💻 Platform Support

> ### ⚠️ Original project tested on macOS only — the Linux install path below has been independently verified
> The base workflow (OpenCode + NVIDIA Nemotron 3 Ultra) was originally documented and verified on **macOS**. For this Linux edition, I independently verified the **`npm install -g opencode-ai`** install path in a clean Linux (Ubuntu) environment — the CLI installed successfully and responded correctly to `opencode --version` and `opencode --help`. The full end-to-end NVIDIA connection flow (`/connect`, `/models`) follows OpenCode's official documented behavior but has not yet been run against a live NVIDIA key on this platform.
>
> Platform differences here are mostly cosmetic (PATH handling, shell config file, package manager for local tools) rather than functional — the underlying CLI and API behavior is identical across platforms. If you test the full flow on your own Linux box and find anything to correct, I'd genuinely appreciate you reaching out — see [Author](#-author) below.

| Platform | Status |
| :--- | :--- |
| 🍎 macOS | ✅ Tested & Documented ([original repo](https://github.com/amitambekar510)) |
| 🐧 **Linux** | 🧪 **This repo — install path verified, full flow community-testing** |
| 🪟 Windows | 🧪 Companion repo — see [Roadmap](#-roadmap) |

---

## 📁 Repository Structure

```
SOC-Nemotron-CLI-Linux/
├── README.md   → This guide: Linux setup, config, prompts, and operational notes
└── LICENSE     → MIT License
```

---

## 🎯 Skill-Level Operational Mapping

| Cybersecurity Role / Level | Primary Terminal Capabilities | Target Use Cases |
| :--- | :--- | :--- |
| **Tier 1 SOC Analyst** *(Beginner)* | Command-line parsing, log normalization, IOC extraction | Parse Syslog/Event IDs, defang IPs/URLs, create firewall blocklists. |
| **Tier 2 Detection Engineer** *(Intermediate)* | Scripting, query building, automated rule writing | Write & test Sigma/YARA rules, optimize Splunk SPL / Sentinel KQL queries. |
| **Tier 3 Incident Responder** *(Expert)* | Autonomous script execution, forensic analysis | Run iterative volatility loops, triage memory dumps, parse network PCAPs. |
| **SOC Lead / Security Manager** | Workflow automation, documentation generation | Generate threat intelligence briefs, automate client incident response reports. |

---

## ⚡ Setup & Authentication *(Linux)*

### 0. Get Your NVIDIA API Key

1. Open the [NVIDIA Nemotron 3 Ultra model page](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b) and sign in / create a free NVIDIA account.
2. Click **Generate API Key**.
3. Copy the key — it looks like `nvapi-xxxxxxxxxxxxxxxx`.

> ⚠️ Never share your API key publicly or commit it to source control.

### 1. Install OpenCode CLI

**Option A — Official installer script:**

```bash
curl -fsSL https://opencode.ai/install | bash
```

**Option B — via npm** *(✅ independently verified working — see note below)*:

```bash
npm install -g opencode-ai
```

> ✅ **Verified:** This install method was tested in a clean Linux (Ubuntu) environment and completed successfully — `opencode --version` returned a working install with the full command set (`opencode run`, `opencode providers`/`auth`, `opencode models`, `opencode uninstall`, etc.) available immediately after install.

See the [official OpenCode documentation](https://opencode.ai/docs/) for details.

### 2. Add OpenCode to Your PATH

Your default shell config file depends on your distro/shell — most Linux distros default to **bash**, not zsh:

```bash
# For bash (most common default on Linux):
echo 'export PATH=$HOME/.opencode/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# For zsh (if you use it instead):
echo 'export PATH=$HOME/.opencode/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

> If you installed via npm, OpenCode is typically already on PATH automatically (in `~/.npm-global/bin` or similar) — run `opencode --version` first before manually editing PATH.

### 3. Launch OpenCode and Connect to NVIDIA NIM

```bash
# Navigate to your investigation / log directory
cd ~/soc-investigations

# Launch OpenCode TUI
opencode

# Authenticate and select Nemotron 3 Ultra
/connect NVIDIA nvapi-YOUR_NVIDIA_API_KEY
/models  # Select: nvidia/nemotron-3-ultra-550b-a55b
```

### 4. Provider Configuration

Add the following to your OpenCode config (typically `~/.config/opencode/opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "nvidia": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NVIDIA NIM",
      "options": {
        "baseURL": "https://integrate.api.nvidia.com/v1",
        "apiKey": "nvapi-YOUR_NVIDIA_API_KEY"
      },
      "models": {
        "nvidia/nemotron-3-ultra-550b-a55b": {
          "name": "Nemotron 3 Ultra (550B)",
          "limit": {
            "context": 1000000,
            "output": 16384
          }
        }
      }
    }
  }
}
```

> Replace `nvapi-YOUR_NVIDIA_API_KEY` with your actual NVIDIA NIM API key. Never commit real keys to source control — use environment variables or a secrets manager instead.

### Model Specs at a Glance

| Attribute | Detail |
| :--- | :--- |
| Model ID | `nvidia/nemotron-3-ultra-550b-a55b` |
| API Endpoint | `https://integrate.api.nvidia.com/v1` |
| Context Window | Up to 1,000,000 tokens |
| Total Parameters | ~550B (NVIDIA lists 561B in endpoint specs) |
| Active Parameters | ~55B (MoE-style architecture) |
| Use Cases | Agentic reasoning, coding, planning, tool calling, long-context tasks |

---

## ✅ Verify Your Installation

```bash
# Confirm OpenCode is installed and on PATH
opencode --version

# Confirm the NVIDIA provider is connected and the model is selected
opencode
/models   # nvidia/nemotron-3-ultra-550b-a55b should show as active

# Run a quick smoke-test prompt
opencode "Reply with a one-line confirmation that Nemotron 3 Ultra is connected and ready."
```

If the model responds, your setup is complete and you're ready to move on to the SOC use cases below.

---

## 🧰 Example Prompts by Use Case

### IOC Extraction & Firewall Blocklist Generation

```bash
opencode "Read threat_feed.txt, extract all IPv4 addresses and SHA256 hashes, defang IPs (e.g., 192.168.1[.]1), and structure into firewall_blocklist.json."
```

### Sigma Detection Rule Authoring

```bash
opencode "Analyze malicious_ps_execution.log and build a valid Sigma detection rule targeting obfuscated PowerShell commands with MITRE ATT&CK mapping."
```

### Autonomous Memory Forensics Triage (Loop Mode)

```bash
opencode --loop "Write a Python script to parse memory dump metadata using Volatility3, run it against sample.raw, fix any syntax or execution errors, and generate a markdown triage report."
```

---

## 🖥️ Sample Output (Illustrative)

To show the *shape* of what Nemotron 3 Ultra returns, here's an illustrative (redacted/simplified) example for the **Sigma Detection Rule Authoring** prompt above:

```yaml
title: Obfuscated PowerShell Execution Detected
id: 3f1a2b4c-illustrative-example
status: experimental
description: Detects encoded/obfuscated PowerShell command-line patterns commonly used to evade logging.
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    Image|endswith: '\powershell.exe'
    CommandLine|contains:
      - '-enc'
      - '-EncodedCommand'
      - 'IEX('
      - 'FromBase64String'
  condition: selection
level: high
tags:
  - attack.execution
  - attack.t1059.001
```

> ⚠️ This is a simplified, illustrative example to show output format — not a production-validated rule. Always run generated Sigma/YARA rules and firewall entries through analyst review before deployment.

---

## 💰 Rate Limits & Cost Notes

- NVIDIA's hosted endpoint for Nemotron 3 Ultra is currently offered under a **free trial/API tier** — exact request-per-minute and token quotas are set by NVIDIA and **subject to change without notice**.
- Check current limits on your [NVIDIA build.nvidia.com](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b) account dashboard before relying on it for time-sensitive IR work.
- For high-volume or production SOC use, plan for the possibility of moving to a paid tier or self-hosted inference in the future.

---

## 🧩 Troubleshooting *(Linux)*

| Issue | Technical Cause | Operational Fix |
| :--- | :--- | :--- |
| `bash: opencode: command not found` | Terminal PATH missing OpenCode directory | Run `echo 'export PATH=$HOME/.opencode/bin:$PATH' >> ~/.bashrc && source ~/.bashrc`. |
| `"Not Found"` Error | OpenCode launched outside evidence directory | `cd` directly into the incident directory containing log files before starting `opencode`. |
| npm install fails with `EACCES` permission errors | npm's default global folder isn't user-writable | Reconfigure npm's global prefix to a user-owned directory (e.g. `npm config set prefix "$HOME/.npm-global"`) rather than using `sudo npm install -g`. |
| Execution Timeout on PCAPs | Sub-shell missing local security tool binaries | Install local tools via your distro's package manager, e.g. `sudo apt install tshark yara` (Debian/Ubuntu) or `sudo dnf install wireshark-cli yara` (Fedora), and install `volatility3` via `pip`. |

---

## 🗑️ Uninstall / Disconnect

**Remove OpenCode CLI:**

```bash
# If installed via the official script:
rm -rf ~/.opencode

# If installed via npm:
npm uninstall -g opencode-ai
```

Then remove the PATH line you added to `~/.bashrc` (or `~/.zshrc`) and run `source` on that file again.

**Revoke your NVIDIA API key:**

1. Go to your [NVIDIA build.nvidia.com](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b) account.
2. Navigate to API Keys and delete/revoke the key used for this project.

---

## ⚠️ Security & Operational Guidelines

1. **Redact Sensitive Data** — Always scrub production credentials, API secrets, and sensitive PII from logs before passing them to AI prompts.
2. **Isolate Environments** — Run autonomous loops (`--loop`) inside isolated staging VMs or containers when interacting with suspicious files.
3. **Analyst Verification** — Always manually inspect generated firewall rules and SIEM correlation queries prior to pushing to production environments.

---

## 🔗 Official Reference Links

- [NVIDIA Nemotron 3 Ultra — Model Page](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b)
- [NVIDIA Nemotron 3 Ultra — Model Card](https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b/modelcard)
- [OpenCode Documentation](https://opencode.ai/docs/)
- [OpenCode NVIDIA Provider Guide](https://opencode.ai/docs/providers)

---

## 🗺️ Roadmap

- [x] macOS setup guide, config, and prompt library ([original repo](https://github.com/amitambekar510))
- [x] Windows setup guide (companion repo, published separately)
- [x] Linux setup guide (this repo — npm install path verified)
- [ ] Full end-to-end NVIDIA connection flow verified live on Linux
- [ ] Additional SOC/IR prompt examples as the workflow expands

---

## 🤝 Contributing

This is a personal study/reference repo. The `npm install -g opencode-ai` path has been verified to work on Linux — if you run the full flow (connecting to NVIDIA, running the example prompts) on your own distro and find anything to correct, please open an issue/PR or reach out directly (see [Author](#-author)).

---

## 📝 Source & Learning Notes

This repo was compiled while researching and testing newly released terminal-based agentic AI tooling (OpenCode CLI) paired with NVIDIA's hosted Nemotron 3 Ultra endpoint, as part of ongoing self-study into emerging AI capabilities relevant to security operations. It adapts the original macOS-tested guide for Linux, with the install step independently re-verified.

> ⚠️ **Disclaimer:** NVIDIA's hosted endpoint is currently offered for free, but availability, quotas, and trial terms are subject to change and governed by NVIDIA's API Trial Terms and the model's license. This guide is for educational and informational purposes only — no outcome is guaranteed. NVIDIA, Nemotron, OpenCode, and other product names are trademarks of their respective owners.

---

## 👤 Author

**Amit Ambekar**
🔗 [GitHub — @amitambekar510](https://github.com/amitambekar510)
🔗 [LinkedIn — Amit Milind Ambekar](https://www.linkedin.com/in/amitmilindambekar/)

Exploring emerging AI tooling for cybersecurity operations. Spotted something that needs fixing on your Linux setup, or have a better approach? I'd genuinely like to hear it — connect with me on LinkedIn and let's discuss.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.
