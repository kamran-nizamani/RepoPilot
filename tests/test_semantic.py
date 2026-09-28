from repopilot.scanner import scan_repository
from repopilot.semantic import rank_context

def test_rank_context_prefers_matching_file(tmp_path):
    (tmp_path / "auth.py").write_text("authentication login token\n", encoding="utf-8")
    (tmp_path / "other.py").write_text("weather forecast\n", encoding="utf-8")
    ranked = rank_context(tmp_path, scan_repository(tmp_path), "authentication login")
    assert ranked[0][1] == "auth.py"
