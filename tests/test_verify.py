from repopilot.verify import run_tests

def test_verify_requires_explicit_approval(tmp_path):
    try:
        run_tests(tmp_path)
        assert False, "expected approval gate"
    except PermissionError:
        pass

def test_verify_returns_result(tmp_path):
    result = run_tests(tmp_path, approved=True)
    assert result.command == ["python", "-m", "pytest", "-q"]
    assert isinstance(result.returncode, int)
