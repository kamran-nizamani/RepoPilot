# RepoPilot

> **Controlled AI engineering for real GitHub repositories.** Inspect evidence → diagnose a bug → propose an exact patch → require human approval → create a PR.

RepoPilot is a Next.js-based AI coding-agent dashboard built around a simple safety boundary:

**AI can analyze and propose. A human decides whether GitHub gets changed.**

## What RepoPilot does

- Reads a public GitHub repository and builds relevant code context
- Works across frameworks and languages instead of assuming Next.js
- Investigates bugs, errors, failing tests, security concerns, and code paths
- Uses Gemini for structured diagnosis and patch planning
- Produces exact oldText → newText patches grounded in retrieved evidence
- Shows evidence and proposed changes before any write
- Requires explicit human approval before GitHub writes
- Creates an isolated branch for approved changes
- Can open a GitHub pull request for review
- Verifies patch text against current repository content before writing

## How it works

~~~text
GitHub repository
       |
       v
Repository scan -> tree + project structure
       |
       v
Context engine -> relevant source + tests
       |
       v
Gemini diagnosis -> evidence-based analysis
       |
       v
Patch proposal -> exact oldText -> newText
       |
       v
Human review
       |
   +---+---+
   |       |
 Reject  Approve
           |
           v
     GitHub branch
           |
           v
      Pull Request
~~~

## Dashboard

The web application includes:

- Workspace
- Agent
- Issues
- Runs
- Analytics
- Observability
- Patch review

## Safety model

RepoPilot is intentionally approval-gated.

### Read phase
Repository source is retrieved for analysis. No GitHub write is performed.

### AI phase
The model receives only retrieved repository evidence and is instructed not to invent files or claim execution it did not perform.

### Approval phase
A user must explicitly approve a proposed patch before the GitHub write endpoint accepts it.

### Write phase
Approved changes are written to a separate branch. Before updating an existing file, RepoPilot verifies that the proposed oldText still exists in the current file. This helps prevent stale patches from silently overwriting newer work.

RepoPilot does not automatically merge pull requests.

## Run locally

Requirements:

- Node.js 24.x
- Google Gemini API key for AI diagnosis
- GitHub token only if approved PR creation is required

Install:

~~~bash
npm install
~~~

Create .env.local:

~~~env
GEMINI_API_KEY=your_gemini_key
GITHUB_TOKEN=your_github_token
~~~

Keep these values server-side. Never commit them.

Start:

~~~bash
npm run dev
~~~

Open http://localhost:3000.

Production build:

~~~bash
npm run build
npm start
~~~

## Deploy on Vercel

1. Import the repository into Vercel.
2. Use the Next.js framework preset.
3. Add GEMINI_API_KEY as a server environment variable.
4. Add GITHUB_TOKEN only if GitHub write/PR functionality is required.
5. Deploy.

No API key should be placed in client-side code.

## Example investigation

~~~text
Analyze this repository for a real, reproducible bug.
Do not assume a framework.
Inspect source and tests, identify one concrete issue,
and propose the smallest safe fix.
~~~

For a targeted investigation:

~~~text
Inspect packages/cortexward-agents/src/cortexward/agents/resilient_llm.py.
Determine whether retrying every Exception is correct.
Identify the bug and propose a minimal safe patch.
Do not modify files yet.
~~~

## Roadmap

- [x] Public GitHub repository scanning
- [x] Generic multi-language context retrieval
- [x] Evidence-based AI diagnosis
- [x] Structured patch proposals
- [x] Human approval gate
- [x] Approved GitHub branch writes
- [x] Pull request creation
- [x] Stale-patch verification
- [x] Web dashboard
- [ ] Automated test execution in an isolated sandbox
- [ ] AST-aware code indexing
- [ ] Semantic/vector retrieval
- [ ] Dependency graph analysis
- [ ] Security/CWE analysis
- [ ] Multi-provider AI support
- [ ] Persistent run history
- [ ] MCP integration
- [ ] Repository-specific project memory

## Contributing

Issues, bug reports, improvements, tests, and documentation contributions are welcome.

Before submitting a patch, explain:

1. What problem it solves
2. How the problem can be reproduced
3. Why the proposed change is safe
4. How it was verified

## License

MIT
