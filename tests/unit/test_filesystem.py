import pytest
from flask import Flask
from shell import CommandError

from src.api.filesystem import FilesystemAPI


@pytest.fixture(scope="class")
def api():
    return FilesystemAPI(username="test")


class TestFilesystemAPI:
    def test_supported_paths_returns_values(self, api):
        app = Flask(__name__)
        app.config["SUPPORTED_PATHS"] = ["/test"]
        with app.test_request_context():
            assert api.supported_paths() == ["/test"]

    @pytest.mark.parametrize(
        "mocker_shell",
        [(0, ["file"], "")],
        indirect=True,
    )
    def test_valid_ls_returns_valid_data(self, api, mocker_shell, mocker):
        mocker.patch("src.utils.validate_path", return_value=True)
        assert api.ls(path="/valid-path") == ["file"]

    def test_ls_on_restricted_path_raises_exception(self, api, mocker):
        mocker.patch("src.utils.validate_path", side_effect=PermissionError)
        with pytest.raises(PermissionError):
            assert api.ls(path="/restricted-path")

    def test_ls_on_missing_file_raises_exception(self, api, mocker):
        mocker.patch("src.utils.validate_path", side_effect=FileNotFoundError)
        with pytest.raises(FileNotFoundError):
            assert api.ls(path="/missing-file")

    def test_ls_os_error_raises_exception(self, api, mocker):
        mocker.patch("src.utils.validate_path", side_effect=OSError)
        with pytest.raises(OSError):
            assert api.ls(path="/???")

    @pytest.mark.parametrize(
        "mocker_shell",
        [(1, "", "???")],
        indirect=True,
    )
    def test_command_error_raises_exception(self, api, mocker_shell, mocker):
        mocker.patch("src.utils.validate_path", return_value=True)
        with pytest.raises(CommandError):
            assert api.ls(path="/???")
