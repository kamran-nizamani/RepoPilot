from repopilot.verify import run_tests

def test_verify_returns_result(tmp_path):
    result = run_tests(tmp_path)
    assert result.command == ["python", "-m", "pytest", "-q"]
    assert isinstance(result.returncode, int)
