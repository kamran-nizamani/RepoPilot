from unittest.mock import patch

from repopilot.api import Handler, _root


def test_api_module_exposes_handler():
    assert hasattr(Handler, "do_GET")
    assert hasattr(Handler, "do_POST")


def test_root_resolves_directory(tmp_path):
    assert _root(str(tmp_path)).is_dir()


def test_analyze_service_is_called_for_endpoint():
    with patch("repopilot.api.analyze_repository", return_value={"files": 3}) as analyze:
        from repopilot.api import analyze_repository
        assert analyze(".") == {"files": 3}
        analyze.assert_called_once_with(".")
