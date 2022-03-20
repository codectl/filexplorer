import pytest
from flask import Flask

from src.api.filesystem import (
    DefaultException,
    FileNotFoundException,
    PermissionDeniedException,
    FilesystemAPI,
)


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
    def test_valid_ls_returns_valid_data(self, api, mocker_shell):
        assert api.ls(path="/valid-path") == ["file"]

    @pytest.mark.parametrize(
        "mocker_shell",
        [(1, [], "ls: root: Permission denied")],
        indirect=True,
    )
    def test_ls_on_restricted_file_raises_exception(self, api, mocker_shell):
        with pytest.raises(PermissionDeniedException):
            assert api.ls(path="/restricted-path")

    @pytest.mark.parametrize(
        "mocker_shell",
        [(1, [], "ls: /tmp/missing-file: No such file or directory")],
        indirect=True,
    )
    def test_ls_on_missing_file_raises_exception(self, api, mocker_shell):
        with pytest.raises(FileNotFoundException):
            assert api.ls(path="/missing-file")

    @pytest.mark.parametrize(
        "mocker_shell",
        [(1, [], "ls: ???")],
        indirect=True,
    )
    def test_ls_generic_error_raises_exception(self, api, mocker_shell):
        with pytest.raises(DefaultException):
            assert api.ls(path="/???")
