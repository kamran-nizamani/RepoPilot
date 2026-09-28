from repopilot.scanner import scan_repository


def test_scan_repository(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("ignore", encoding="utf-8")

    repo = scan_repository(tmp_path)

    assert len(repo.files) == 2
    assert repo.total_lines == 2
    assert {item.language for item in repo.files} == {"Python", "Markdown"}
