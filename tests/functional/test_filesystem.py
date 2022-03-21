import os
import re
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

    @pytest.mark.parametrize(
        "mocker_shell",
        [(0, ["file"], "")],
        indirect=True,
    )
    def test_valid_path_returns_200(self, client, auth, mocker_shell, mocker):
        mocker.patch("src.utils.validate_path", return_value=True)
        response = client.get("/filesystem/tmp/", headers=auth)
        assert response.status_code == 200
        assert response.json == ["file"]

    def test_error_path_returns_400(self, client, auth, mocker):
        mocker.patch("src.utils.validate_path", side_effect=OSError)
        response = client.get("/filesystem/tmp/invalid/", headers=auth)
        assert response.status_code == 400
        assert response.json == {"code": 400, "message": "", "reason": "Bad Request"}

    def test_permission_denied_returns_403(self, client, auth, mocker):
        mocker.patch("src.utils.validate_path", side_effect=PermissionError)
        response = client.get("/filesystem/tmp/root/", headers=auth)
        assert response.status_code == 403
        assert response.json == {"code": 403, "message": "", "reason": "Forbidden"}

    def test_missing_path_returns_404(self, client, auth, mocker):
        mocker.patch("src.utils.validate_path", side_effect=FileNotFoundError)
        response = client.get("/filesystem/tmp/invalid/", headers=auth)
        assert response.status_code == 404
        assert response.json == {"code": 404, "message": "", "reason": "Not Found"}

    @pytest.mark.parametrize(
        "mocker_shell",
        [(0, ["foo.txt"], "")],
        indirect=True,
    )
    def test_file_attachment_returns_200(self, app, client, auth, mocker_shell, mocker):
        mocker.patch("src.utils.validate_path", return_value=True)
        headers = {**auth, "accept": "application/octet-stream"}
        with NamedTemporaryFile() as tmp:
            filename = os.path.basename(tmp.name)
            mocker.patch("src.utils.attachment", return_value=(filename, tmp.name))
            base_path = re.match(rf"{os.path.sep}\w*", tmp.name).group()
            app.config["SUPPORTED_PATHS"] = [base_path]
            response = client.get(f"/filesystem{tmp.name}", headers=headers)
            assert response.status_code == 200
            assert response.headers["Content-Disposition"] == f"attachment; filename={filename}"
            assert response.headers["Content-Type"] == "application/octet-stream"
