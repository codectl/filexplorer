import io
import stat
import subprocess

import pytest
from flask import Flask

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

    def test_valid_ls_returns_valid_data(self, api, mocker):
        mocker.patch("src.utils.shell", return_value="file.txt")
        assert api.ls(path="/valid-path") == ["file.txt"]

    def test_ls_on_restricted_path_raises_exception(self, api, mocker):
        stderr = "ls: /tmp/root/: Permission denied"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(PermissionError) as ex:
            assert api.ls(path="/restricted-path")
        assert str(ex.value) == "permission denied"

    def test_ls_on_missing_file_raises_exception(self, api, mocker):
        stderr = "ls: /tmp/missing/: No such file or directory"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(FileNotFoundError) as ex:
            assert api.ls(path="/missing")
        assert str(ex.value) == "no such file or directory"

    def test_ls_on_error_raises_exception(self, api, mocker):
        stderr = "there was an error"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(Exception) as ex:
            assert api.ls(path="/???")
        assert str(ex.value) == stderr

    def test_valid_file_attachment(self, api, mocker):
        mocker.patch("src.utils.shell", return_value=b"content")
        name, content = api.attachment(path="/file.txt", mode=stat.S_IFREG)
        assert name == "file.txt"
        assert content.read() == io.BytesIO(b"content").read()

    def test_valid_directory_attachment(self, api, mocker):
        mocker.patch("src.utils.shell", return_value=b"content")
        name, content = api.attachment(path="/dir/", mode=stat.S_IFDIR)
        assert name == "dir.tar.gz"
        assert content.read() == io.BytesIO(b"content").read()
