import argparse
from pathlib import Path

from .agent import RepoAgent
from .indexer import index_symbols
from .providers import MockProvider
from .scanner import scan_repository
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

    if args.command == "symbols":
        repo = scan_repository(Path(args.path))
        for symbol in index_symbols(args.path, repo):
            print(f"{symbol.path}:{symbol.line}: {symbol.kind} {symbol.name}")
        return 0

    if args.command == "ask":
        repo = scan_repository(Path(args.path))
        response = RepoAgent(MockProvider()).ask(args.question, repo)
        print(response)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
