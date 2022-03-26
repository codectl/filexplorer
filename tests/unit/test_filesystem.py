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
        assert api.ls(path="/tmp/") == ["file.txt"]

    def test_ls_on_restricted_path_raises_exception(self, api, mocker):
        stderr = "ls: /tmp/root/: Permission denied"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(PermissionError) as ex:
            assert api.ls(path="/tmp/root/")
        assert str(ex.value) == "permission denied"

    def test_ls_on_missing_file_raises_exception(self, api, mocker):
        stderr = "ls: /tmp/file.txt: No such file or directory"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(FileNotFoundError) as ex:
            assert api.ls(path="/tmp/file.txt")
        assert str(ex.value) == "no such file or directory"

    def test_ls_on_error_raises_exception(self, api, mocker):
        stderr = "there was an error"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(Exception) as ex:
            assert api.ls(path="/tmp/error")
        assert str(ex.value) == stderr

    def test_valid_file_attachment(self, api, mocker):
        mocker.patch("src.utils.shell", return_value=b"content")
        name, content = api.attachment(path="/tmp/file.txt", mode=stat.S_IFREG)
        assert name == "file.txt"
        assert content.read() == io.BytesIO(b"content").read()

    def test_valid_directory_attachment(self, api, mocker):
        mocker.patch("src.utils.shell", return_value=b"content")
        name, content = api.attachment(path="/tmp/dir/", mode=stat.S_IFDIR)
        assert name == "dir.tar.gz"
        assert content.read() == io.BytesIO(b"content").read()

    def test_restricted_file_attachment_raises_exceptions(self, api, mocker):
        stderr = "tar: Couldn't list extended attributes: Permission denied"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(PermissionError) as ex:
            assert api.attachment(path="/tmp/file.txt", mode=stat.S_IFREG)
        assert str(ex.value) == "permission denied"

    def test_restricted_directory_attachment_raises_exceptions(self, api, mocker):
        stderr = "tar: Couldn't list extended attributes: Permission denied"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(PermissionError) as ex:
            assert api.attachment(path="/tmp/dir/", mode=stat.S_IFDIR)
        assert str(ex.value) == "permission denied"

    def test_invalid_mode_attachment_raises_exceptions(self, api, mocker):
        with pytest.raises(ValueError) as ex:
            assert api.attachment(path="", mode=stat.S_IFCHR)
        assert str(ex.value) == "unsupported file mode"

    def test_missing_file_attachment_raises_exceptions(self, api, mocker):
        stderr = "tar: /tmp/file.txt: Cannot stat: No such file or directory"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(FileNotFoundError) as ex:
            assert api.ls(path="/tmp/file.txt")
        assert str(ex.value) == "no such file or directory"

    def test_missing_directory_attachment_raises_exceptions(self, api, mocker):
        stderr = "tar: /tmp/dir/: Cannot stat: No such file or directory"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(FileNotFoundError) as ex:
            assert api.ls(path="/tmp/dir/")
        assert str(ex.value) == "no such file or directory"

    def test_error_attachment_raises_exceptions(self, api, mocker):
        stderr = "tar: some error occurred"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        with pytest.raises(Exception) as ex:
            assert api.ls(path="/tmp/dir/")
        assert str(ex.value) == "some error occurred"

    def test_valid_file_upload(self, api, mocker):
        mocker.patch("src.utils.shell")
        file = mocker.MagicMock(filename="file.txt")
        api.upload_files(path="/tmp/dir/", files=[])
        api.upload_files(path="/tmp/dir/", files=[file])

    def test_existing_file_upload_raises_exception(self, api, mocker):
        mocker.patch("src.utils.shell", return_value="file.txt")
        file = mocker.MagicMock(filename="file.txt")
        with pytest.raises(FileExistsError):
            api.upload_files(path="/tmp/dir/", files=[file])

    def test_valid_file_update(self, api, mocker):
        mocker.patch("src.utils.shell", return_value="file.txt")
        file = mocker.MagicMock(filename="file.txt")
        api.upload_files(path="/tmp/dir/", files=[], update=True)
        api.upload_files(path="/tmp/dir/", files=[file], update=True)

    def test_missing_file_update_raises_exception(self, api, mocker):
        mocker.patch("src.utils.shell")
        file = mocker.MagicMock(filename="file.txt")
        with pytest.raises(FileNotFoundError):
            api.upload_files(path="/tmp/dir/", files=[file], update=True)
