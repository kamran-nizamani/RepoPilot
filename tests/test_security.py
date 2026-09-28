from repopilot.scanner import scan_repository
from repopilot.security import scan_security

def test_security_finds_eval(tmp_path):
    (tmp_path / "app.py").write_text("result = eval(user_input)\n", encoding="utf-8")
    findings = scan_security(tmp_path, scan_repository(tmp_path))
    assert any(f.rule == "dangerous-eval" and f.line == 1 for f in findings)
