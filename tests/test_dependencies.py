from repopilot.dependencies import build_dependency_graph
from repopilot.scanner import scan_repository

def test_dependency_graph_finds_local_import(tmp_path):
    (tmp_path / "a.py").write_text("import b\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("VALUE = 1\n", encoding="utf-8")
    deps = build_dependency_graph(tmp_path, scan_repository(tmp_path))
    assert any(d.source == "a" and d.target == "b" for d in deps)
