import pytest
from repopilot.safety import SafetyPolicy, require_approval

def test_default_policy_denies_actions():
    policy = SafetyPolicy()
    assert not policy.check("write_file")
    assert not policy.check("shell")
    assert not policy.check("network")

def test_approval_is_required():
    with pytest.raises(PermissionError):
        require_approval("shell", False)
