import pytest

from repopilot.patches import PatchProposal


def test_patch_requires_approval():
    patch = PatchProposal("demo.py", "x = 1\n", "x = 2\n")
    assert "-x = 1" in patch.diff()
    assert "+x = 2" in patch.diff()
    with pytest.raises(PermissionError):
        patch.apply(False)
