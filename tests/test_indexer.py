from repopilot.indexer import index_symbols
from repopilot.scanner import scan_repository

def test_index_python_symbols(tmp_path):
    (tmp_path / "app.py").write_text("class App:\n    def run(self):\n        pass\n", encoding="utf-8")
    symbols = index_symbols(tmp_path, scan_repository(tmp_path))
    assert [(s.kind, s.name, s.line) for s in symbols] == [("class", "App", 1), ("function", "run", 2)]
