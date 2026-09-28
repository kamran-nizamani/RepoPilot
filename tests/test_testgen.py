from repopilot.testgen import propose_python_test

def test_test_proposal():
    proposal = propose_python_test("app.py", "hello")
    assert proposal.path == "tests/test_app_hello.py"
    assert "def test_hello_behavior" in proposal.content
