from repopilot.diff import ProposedChange

def test_diff_contains_file_headers():
    diff = ProposedChange('app.py', 'x = 1\n', 'x = 2\n').diff()
    assert '--- a/app.py' in diff
    assert '+++ b/app.py' in diff
