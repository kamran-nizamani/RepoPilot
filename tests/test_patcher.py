import pytest
from repopilot.patcher import PatchError, apply_change, build_change
from repopilot.diff import ProposedChange

def test_build_change_reads_existing_file(tmp_path):
    (tmp_path / "a.txt").write_text("old\n", encoding="utf-8")
    change = build_change(tmp_path, "a.txt", "new\n")
    assert change.before == "old\n"
    assert change.after == "new\n"

def test_apply_requires_approval(tmp_path):
    change = ProposedChange("a.txt", "", "new\n")
    with pytest.raises(PermissionError):
        apply_change(tmp_path, change)

def test_path_escape_rejected(tmp_path):
    with pytest.raises(PatchError):
        build_change(tmp_path, "../outside.txt", "x")
