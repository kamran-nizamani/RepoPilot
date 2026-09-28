# RepoPilot

> Open-source AI coding agent for understanding, debugging, testing, and safely improving real codebases.

RepoPilot is designed around one principle: **AI proposes changes; humans approve them.**

## What it does

- Scans a repository and builds a lightweight codebase map
- Finds relevant files for a natural-language task
- Explains architecture and dependencies
- Detects common code/security issues
- Generates a proposed patch
- Shows a unified diff before changing files
- Runs tests and Git actions through explicit approval gates
- Supports local AI providers such as Ollama
- End-to-end issue workflow with optional apply, verify, commit, push, and PR creation

## Status

🚧 **v0.2 workspace foundation** — repository intelligence, local AI, planning, patch generation, an approval-gated local API/dashboard, and GitHub issue-to-PR workflow foundations are implemented on the development branch.

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"

repopilot scan .
repopilot ask "Explain the authentication flow"
repopilot plan "Fix the authentication error"
repopilot generate "Fix the authentication error"
repopilot verify
```

## Architecture

```
User
  │
  ▼
RepoPilot CLI
  │
  ├── Scanner ───────► File / language / symbol map
  ├── Context Engine ─► Relevant code retrieval
  ├── Agent ──────────► Plan + reasoning
  ├── Provider ───────► Local / OpenAI-compatible model
  ├── Patch Engine ───► Proposed unified diff
  └── Safety Gate ────► Human approval before writes
```

## Safety model

RepoPilot does **not** silently edit a repository. File writes and command execution are explicit actions behind an approval gate.

## Current capabilities

RepoPilot currently provides repository scanning, ranked source retrieval, Python AST symbol indexing, dependency inspection, heuristic security findings, local Ollama support, implementation planning, structured patch generation, unified diffs, path traversal protection, explicit patch application, test verification, and a non-destructive GitHub issue workflow.

## Roadmap

- [x] Repository scanner foundation
- [x] CLI foundation
- [x] Provider abstraction
- [x] Safe patch preview
- [x] Python symbol indexing
- [x] Safe implementation planning
- [x] Structured patch generation
- [x] Test verification command
- [ ] AST-aware indexing
- [ ] Semantic search
- [ ] Dependency graph
- [ ] Test generation
- [ ] Security/CWE analysis
- [ ] GitHub PR automation
- [x] Web dashboard
- [ ] MCP integration
- [ ] Project memory

## License

MIT

## Local AI with Ollama

Set the provider before using `ask`, `plan`, or `generate`:

```bash
REPOPILOT_PROVIDER=ollama
REPOPILOT_MODEL=your-local-model
REPOPILOT_BASE_URL=http://localhost:11434
```

On Windows PowerShell, use `$env:REPOPILOT_PROVIDER="ollama"` and the equivalent variables. RepoPilot uses Ollama's local HTTP API, so no cloud API key is required.

## GitHub issue workflow

Prepare an issue-driven fix without modifying files:

```bash
export GITHUB_TOKEN=your_token
repopilot fix-issue 12 --repo owner/project --path .\n\n# After reviewing the diff, explicitly approve the full workflow:\nrepopilot fix-issue 12 --repo owner/project --path . --branch fix/issue-12 --apply --verify --commit --push --create-pr
```

By default the command is preview-only. `--apply` approves file changes; `--verify` runs tests; `--commit`, `--push`, and `--create-pr` enable later stages. No merge is performed automatically.

## Development workflow

1. `repopilot scan .` — understand the repository.
2. `repopilot plan "..."` — review the proposed approach.
3. `repopilot generate "..."` — inspect the generated diff.
4. `repopilot generate "..." --apply` — explicitly apply approved changes.
5. `repopilot verify` — run the test suite.

Generated patches are constrained to the repository root and are never applied unless the explicit `--apply` action is used.


## Dashboard

The local dashboard is an AI workspace served by RepoPilot itself:

```bash
repopilot serve --port 8765
```

Open `http://127.0.0.1:8765/`. The workspace provides repository analysis, AI chat, implementation plans, generated diff previews, explicit apply approval, test execution, and Git status. It uses the local API and has no frontend dependency build step.

For local AI, configure Ollama before starting the server:

```text
REPOPILOT_PROVIDER=ollama
REPOPILOT_MODEL=llama3.2
REPOPILOT_BASE_URL=http://localhost:11434
```

Mutating and network operations remain approval-gated; RepoPilot does not auto-merge pull requests.

## Docker

Build and run RepoPilot against the current repository:

```bash
docker compose run --rm repopilot scan .
```

For local Ollama, configure `REPOPILOT_PROVIDER=ollama` and the model/base URL in your environment.

## Project memory

RepoPilot can store small project facts locally:

```bash
repopilot memory framework "FastAPI"
```

The memory file is local and should not contain secrets.
