from repopilot.planner import Planner
from repopilot.providers import MockProvider
from repopilot.scanner import scan_repository

def test_planner_returns_safe_default():
    plan = Planner(MockProvider()).create('fix login', '.', scan_repository('.'))
    assert plan.steps
    assert plan.risks
