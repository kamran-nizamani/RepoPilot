from repopilot.service import analyze_repository

def test_analyze_repository(tmp_path):
    (tmp_path / "app.py").write_text("def hello():\n    return 'hi'\n", encoding="utf-8")
    result = analyze_repository(tmp_path)
    assert result["files"] == 1
    assert result["symbols"] == 1
