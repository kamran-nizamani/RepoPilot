from repopilot.ast_index import index_python_ast
from repopilot.scanner import scan_repository

def test_ast_index_finds_class_and_function(tmp_path):
    (tmp_path / "app.py").write_text("class App:\n    def run(self):\n        pass\n", encoding="utf-8")
    symbols = index_python_ast(tmp_path, scan_repository(tmp_path))
    assert {s.name for s in symbols} == {"App", "run"}
