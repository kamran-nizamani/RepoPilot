import argparse
from pathlib import Path

from .agent import RepoAgent
from .config import ModelConfig
from .indexer import index_symbols
from .providers_factory import create_provider
from .planner import Planner
from .patcher import build_change, apply_change
from .verify import run_tests
from .generator import PatchGenerator
from .dependencies import build_dependency_graph
from .ast_index import index_python_ast
from .semantic import rank_context
from .security import scan_security
from .scanner import scan_repository
from .github_flow import GitHubClient
from .workflow import IssueWorkflow
from .search import search_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repopilot",
        description="AI coding agent for understanding and safely improving repositories.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan a repository and print its codebase map.")
    scan.add_argument("path", nargs="?", default=".")

    ask = sub.add_parser("ask", help="Ask a repository-aware question.")
    ask.add_argument("question")
    ask.add_argument("--path", default=".")

    search = sub.add_parser("search", help="Search repository source text.")
    search.add_argument("query")
    search.add_argument("--path", default=".")

    plan = sub.add_parser("plan", help="Create a reviewable implementation plan.")
    plan.add_argument("goal")
    plan.add_argument("--path", default=".")

    generate = sub.add_parser("generate", help="Generate a patch proposal for a task.")
    generate.add_argument("goal")
    generate.add_argument("--path", default=".")
    generate.add_argument("--apply", action="store_true", help="Apply generated patches after preview.")

    fix_issue = sub.add_parser("fix-issue", help="Prepare a fix from a GitHub issue without applying it.")
    fix_issue.add_argument("issue", type=int)
    fix_issue.add_argument("--repo", required=True, help="GitHub owner/repository")
    fix_issue.add_argument("--path", default=".")

    ast_cmd = sub.add_parser("ast", help="Index Python symbols using the AST.")
    ast_cmd.add_argument("--path", default=".")

    semantic = sub.add_parser("semantic", help="Rank files by lexical semantic similarity.")
    semantic.add_argument("query")
    semantic.add_argument("--path", default=".")

    deps = sub.add_parser("deps", help="Show local Python dependency edges.")
    deps.add_argument("--path", default=".")

    security = sub.add_parser("security", help="Run lightweight security checks.")
    security.add_argument("--path", default=".")

    verify = sub.add_parser("verify", help="Run the repository test suite.")
    verify.add_argument("--path", default=".")

    symbols = sub.add_parser("symbols", help="List indexed Python symbols.")
    symbols.add_argument("--path", default=".")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "scan":
        repo = scan_repository(args.path)
        print(f"Repo: {repo.root}")
        print(f"Files: {len(repo.files)}")
        print(f"Lines: {repo.total_lines}")
        print(f"Size: {repo.total_size} bytes")
        for item in repo.files:
            print(f"  {item.path:<50} {item.language:<12} {item.lines:>6} lines")
        return 0

    if args.command == "search":
        repo = scan_repository(Path(args.path))
        for path, line, text in search_text(args.path, repo, args.query):
            print(f"{path}:{line}: {text}")
        return 0

    if args.command == "plan":
        repo = scan_repository(Path(args.path))
        result = Planner(create_provider(ModelConfig.from_env())).create(args.goal, args.path, repo)
        print(f"Goal: {result.goal}\n\nSteps:")
        for i, step in enumerate(result.steps, 1): print(f"  {i}. {step}")
        print("\nRisks:")
        for risk in result.risks: print(f"  - {risk}")
        return 0

    if args.command == "generate":
        repo = scan_repository(Path(args.path))
        patches = PatchGenerator(create_provider(ModelConfig.from_env())).generate(args.goal, args.path, repo)
        if not patches:
            print("No structured patches were generated.")
            return 2
        for patch in patches:
            change = build_change(args.path, patch.path, patch.content)
            print(change.diff())
            if args.apply:
                apply_change(args.path, change, approved=True)
                print(f"Applied: {patch.path}")
        return 0

    if args.command == "fix-issue":
        import os
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN is required for fix-issue.")
        owner, repo_name = args.repo.split("/", 1)
        repo_map = scan_repository(Path(args.path))
        provider = create_provider(ModelConfig.from_env())
        workflow = IssueWorkflow(GitHubClient(token), Planner(provider), PatchGenerator(provider))
        result = workflow.prepare(owner, repo_name, args.issue, args.path, repo_map)
        print(f"Issue #{result.issue.number}: {result.issue.title}")
        print("\nPlan:\n" + "\n".join(f"- {step}" for step in result.plan.steps))
        print("\nProposed changes:")
        for change in result.changes:
            print(change.diff() or f"No diff for {change.path}")
        print("\nNo files were changed. Review the diff and apply explicitly with the patch workflow.")
        return 0

    if args.command == "ast":
        repo = scan_repository(Path(args.path))
        for symbol in index_python_ast(args.path, repo): print(f"{symbol.path}:{symbol.line}: {symbol.kind} {symbol.name}")
        return 0

    if args.command == "semantic":
        repo = scan_repository(Path(args.path))
        for score, path in rank_context(args.path, repo, args.query): print(f"{score:.3f} {path}")
        return 0

    if args.command == "deps":
        repo = scan_repository(Path(args.path))
        for dep in build_dependency_graph(args.path, repo): print(f"{dep.source} -> {dep.target} [{dep.kind}]")
        return 0

    if args.command == "security":
        repo = scan_repository(Path(args.path))
        findings = scan_security(args.path, repo)
        for f in findings: print(f"{f.severity.upper()}: {f.path}:{f.line}: {f.message} [{f.rule}]")
        return 1 if findings else 0

    if args.command == "verify":
        result = run_tests(args.path)
        print(result.output)
        return result.returncode

    if args.command == "symbols":
        repo = scan_repository(Path(args.path))
        for symbol in index_symbols(args.path, repo):
            print(f"{symbol.path}:{symbol.line}: {symbol.kind} {symbol.name}")
        return 0

    if args.command == "ask":
        repo = scan_repository(Path(args.path))
        response = RepoAgent(create_provider(ModelConfig.from_env())).ask(args.question, repo)
        print(response)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
