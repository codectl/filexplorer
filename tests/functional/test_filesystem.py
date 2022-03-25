import os
import re
import subprocess
from base64 import b64encode
from tempfile import NamedTemporaryFile

import pytest

from src.api.auth import AuthAPI


@pytest.fixture()
def auth(mocker):
    mocker.patch.object(AuthAPI, "authenticate", return_value=True)
    return {"Authorization": f"Basic {b64encode(b'user:pass').decode()}"}


class TestFilesystem:
    def test_supported_paths(self, client):
        response = client.get("/filesystem/supported-paths")
        assert response.status_code == 200

    def test_unauthorized_request_throws_401(self, client):
        response = client.get("/filesystem/tmp/", headers={})
        assert response.status_code == 401

    def test_unsupported_value_throws_400(self, client, auth):
        response = client.get("/filesystem/unsupported/", headers=auth)
        assert response.status_code == 400

    def test_valid_path_returns_200(self, client, auth, mocker):
        mocker.patch("src.utils.shell", return_value="file.txt")
        response = client.get("/filesystem/tmp/", headers=auth)
        assert response.status_code == 200
        assert response.json == ["file.txt"]

    def test_error_path_returns_400(self, client, auth, mocker):
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr="err")
        mocker.patch("src.utils.shell", side_effect=err)
        response = client.get("/filesystem/tmp/invalid/", headers=auth)
        assert response.status_code == 400
        assert response.json == {"code": 400, "message": "err", "reason": "Bad Request"}

    def test_permission_denied_returns_403(self, client, auth, mocker):
        stderr = "ls: /tmp/root/: Permission denied"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        response = client.get("/filesystem/tmp/root/", headers=auth)
        assert response.status_code == 403
        assert response.json == {
            "code": 403,
            "message": "permission denied",
            "reason": "Forbidden",
        }

    def test_missing_path_returns_404(self, client, auth, mocker):
        stderr = "ls: /tmp/invalid/: No such file or directory"
        err = subprocess.CalledProcessError(cmd="", returncode=1, stderr=stderr)
        mocker.patch("src.utils.shell", side_effect=err)
        response = client.get("/filesystem/tmp/invalid/", headers=auth)
        assert response.status_code == 404
        assert response.json == {
            "code": 404,
            "message": "no such file or directory",
            "reason": "Not Found",
        }

    def test_file_attachment_returns_200(self, client, auth, mocker):
        mocker.patch("src.utils.shell", side_effect=["file.txt", b""])
        mocker.patch("src.utils.isfile", return_value=True)
        headers = {**auth, "accept": "application/octet-stream"}
        response = client.get(f"/filesystem/tmp/file.txt", headers=headers)
        assert response.status_code == 200
        assert (
            response.headers["Content-Disposition"] == f"attachment; filename=file.txt"
        )
        assert response.headers["Content-Type"] == "text/plain; charset=utf-8"

    def test_directory_attachment_returns_200(self, client, auth, mocker):
        mocker.patch("src.utils.shell", side_effect=["dir/", b""])
        mocker.patch("src.utils.isdir", return_value=True)
        headers = {**auth, "accept": "application/octet-stream"}
        response = client.get(f"/filesystem/tmp/dir/", headers=headers)
        assert response.status_code == 200
        assert (
            response.headers["Content-Disposition"]
            == f"attachment; filename=dir.tar.gz"
        )
        assert response.headers["Content-Type"] == "application/x-tar"

    def test_unsupported_accept_header_path_returns_400(self, client, auth):
        headers = {**auth, "accept": "text/html"}
        response = client.get("/filesystem/tmp/", headers=headers)
        assert response.status_code == 400
        assert response.json == {
            "code": 400,
            "message": "unsupported 'accept' HTTP header",
            "reason": "Bad Request",
        }
