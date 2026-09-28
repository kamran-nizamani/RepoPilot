from dataclasses import dataclass
from .context import build_context
from .models import RepoMap
from .providers import ModelProvider

@dataclass
class Plan:
    goal: str
    steps: list[str]
    risks: list[str]

class Planner:
    def __init__(self, provider: ModelProvider): self.provider = provider
    def create(self, goal: str, root: str, repo_map: RepoMap) -> Plan:
        context = build_context(root, repo_map, goal)
        prompt = f'''Create a safe implementation plan. Goal: {goal}\nRelevant code:\n{context}\nReturn STEPS: and RISKS: sections with bullet points. Do not modify files.'''
        text = self.provider.complete(prompt).text
        steps, risks, section = [], [], None
        for raw in text.splitlines():
            line = raw.strip()
            if line.upper().startswith('STEPS:'): section = 'steps'
            elif line.upper().startswith('RISKS:'): section = 'risks'
            elif line.startswith('- ') and section: (steps if section == 'steps' else risks).append(line[2:])
        return Plan(goal, steps or ['Review repository context and implement the requested change.'], risks or ['Review the generated plan before making changes.'])
