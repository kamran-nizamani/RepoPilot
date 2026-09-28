from dataclasses import dataclass
from .github_flow import GitHubIssue, GitHubClient
from .models import RepoMap
from .planner import Planner
from .generator import PatchGenerator
from .patcher import build_change, apply_change
from .diff import ProposedChange
from .verify import run_tests
from .gitflow import create_branch, commit_changes, push_branch

@dataclass(frozen=True)
class WorkflowResult:
    issue: GitHubIssue
    plan: object
    changes: list[ProposedChange]

class IssueWorkflow:
    """Issue -> plan -> patch -> optional apply/verify/git/PR workflow.

    Every mutating, shell, or network step requires explicit approval flags.
    """
    def __init__(self, github: GitHubClient, planner: Planner, generator: PatchGenerator):
        self.github = github
        self.planner = planner
        self.generator = generator

    def prepare(self, owner: str, repo: str, issue_number: int, root: str, repo_map: RepoMap) -> WorkflowResult:
        issue = self.github.get_issue(owner, repo, issue_number)
        goal = f"Issue #{issue.number}: {issue.title}\\n\\n{issue.body}".strip()
        plan = self.planner.create(goal, root, repo_map)
        generated = self.generator.generate(goal, root, repo_map)
        changes = [build_change(root, item.path, item.content) for item in generated]
        return WorkflowResult(issue=issue, plan=plan, changes=changes)

    def apply_and_verify(self, result: WorkflowResult, root: str, approved: bool = False, verify: bool = False):
        for change in result.changes:
            apply_change(root, change, approved=approved)
        return run_tests(root, approved=approved) if verify else None

    def commit(self, root: str, message: str, approved: bool = False):
        return commit_changes(root, message, approved=approved)

    def push(self, root: str, remote: str = "origin", branch: str | None = None, approved: bool = False):
        return push_branch(root, remote, branch, approved=approved)
