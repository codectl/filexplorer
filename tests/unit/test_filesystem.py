import pytest
from flask import Flask
from shell import CommandError, Shell

from src.api.filesystem import FilesystemAPI
from tests.utils import MockShell


@pytest.fixture(scope="class")
def api():
    return FilesystemAPI(username="test")


class TestFilesystemAPI:
    def test_supported_paths(self, api):
        app = Flask(__name__)
        app.config["SUPPORTED_PATHS"] = ["/test"]
        with app.test_request_context():
            assert api.supported_paths() == ["/test"]

    def test_ls(self, api, mocker):
        mock_shell = MockShell(code=0)
        mock_shell.output = lambda: "valid"
        mocker.patch.object(Shell, "run", return_value=mock_shell)
        assert api.ls(path="/valid-path") == "valid"

        mock_shell = MockShell(code=1)
        mock_shell.errors = lambda **_: "error"
        mocker.patch.object(Shell, "run", return_value=mock_shell)
        with pytest.raises(CommandError) as ex:
            assert api.ls(path="/invalid-path")
            assert str(ex) == "error"
