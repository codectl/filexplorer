from base64 import b64encode

import pytest
from shell import Shell

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
        mocker.patch.object(Shell, "run", return_value=MockShell(code=0))
        response = client.get("/filesystem/tmp/", headers=auth)
        assert response.status_code == 200

    def test_invalid_path_returns_404(self, client, auth, mocker):
        mocker.patch.object(Shell, "run", return_value=MockShell(code=1))
        response = client.get("/filesystem/tmp/invalid/", headers=auth)
        assert response.status_code == 404
