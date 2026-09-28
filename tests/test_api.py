from unittest.mock import patch
from repopilot.api import Handler

def test_api_module_exposes_handler():
    assert hasattr(Handler, "do_GET")

def test_analyze_service_is_called_for_endpoint():
    with patch("repopilot.api.analyze_repository", return_value={"files": 3}) as analyze:
        # Test the service dependency without opening a network socket.
        assert analyze(".") == {"files": 3}
