# Platform support

The workbench uses Python's standard library and ordinary HTML/CSS/JavaScript. It is designed for local use on macOS, Linux, and Windows.

| Platform | Launch | Validation status |
| --- | --- | --- |
| macOS | `python3 scripts/workbench.py` | Manual desktop testing needed |
| Linux | `python3 scripts/workbench.py` | Launcher and automated checks tested in Linux |
| Windows | `py -3 scripts/workbench.py` | Manual desktop testing needed |
| WSL | `python3 scripts/workbench.py --no-browser` | Open the printed local URL manually; manual testing needed |

Python 3.10+ is recommended. The workbench itself needs no OpenCode, Node, or NVIDIA credentials. Node 18+ is needed for contributor tests.

For AI execution, follow [OpenCode installation](https://opencode.ai/docs/) and [Windows guidance](https://opencode.ai/docs/windows/). OpenCode recommends WSL for its web experience on Windows.

Primary edition: **Linux**. Automated CI runs on Ubuntu and Windows. Desktop browser interaction and live provider inference require separate manual validation.
