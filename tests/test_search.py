from repopilot.scanner import scan_repository
from repopilot.search import search_text

def test_search_text(tmp_path):
    (tmp_path / "app.py").write_text("def login():\n    return True\n", encoding="utf-8")
    results = search_text(tmp_path, scan_repository(tmp_path), "login")
    assert results[0][:2] == ("app.py", 1)
