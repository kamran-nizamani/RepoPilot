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
- Runs tests/commands through an explicit approval gate
- Supports local AI providers such as Ollama
- Designed for GitHub workflows and future PR automation

## Status

🚧 **v0.1 foundation** — the core CLI, repository scanner, context engine, provider abstraction, and safe patch workflow are being built.

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

## Roadmap

- [x] Repository scanner foundation
- [x] CLI foundation
- [x] Provider abstraction
- [x] Safe patch preview
- [ ] AST-aware indexing
- [ ] Semantic search
- [ ] Dependency graph
- [ ] Test generation
- [ ] Security/CWE analysis
- [ ] GitHub PR automation
- [ ] Web dashboard
- [ ] MCP integration
- [ ] Project memory

## License

MIT


## Current architecture

RepoPilot now provides a public-repository scanner, ranked source-context retrieval, an AI debugging endpoint, unified-diff generation, and an approval-gated GitHub branch/PR workflow.

### Safety

AI analysis is read-only by default. GitHub writes require a server-side `GITHUB_TOKEN` and an explicit approval request. RepoPilot never auto-merges a generated pull request.

### Environment

For AI diagnosis configure `AI_GATEWAY_API_KEY`. For approved GitHub changes configure `GITHUB_TOKEN` as a Vercel server environment variable. Never expose either secret in client-side code.
