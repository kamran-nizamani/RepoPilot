from dataclasses import dataclass
from .github_flow import GitHubIssue, GitHubClient
from .models import RepoMap
from .planner import Planner
from .generator import PatchGenerator
from .patcher import build_change
from .diff import ProposedChange

@dataclass(frozen=True)
class WorkflowResult:
    issue: GitHubIssue
    plan: object
    changes: list[ProposedChange]

class IssueWorkflow:
    """Prepare an issue-driven fix without mutating the repository or merging a PR."""

    def __init__(self, github: GitHubClient, planner: Planner, generator: PatchGenerator):
        self.github = github
        self.planner = planner
        self.generator = generator

    def prepare(self, owner: str, repo: str, issue_number: int, root: str, repo_map: RepoMap) -> WorkflowResult:
        issue = self.github.get_issue(owner, repo, issue_number)
        goal = f"Issue #{issue.number}: {issue.title}\n\n{issue.body}".strip()
        plan = self.planner.create(goal, repo_map)
        generated = self.generator.generate(goal, root, repo_map)
        changes = [build_change(root, item.path, item.content) for item in generated]
        return WorkflowResult(issue=issue, plan=plan, changes=changes)
