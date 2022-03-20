from base64 import b64encode

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
        "mock_shell",
        [(0, ["file"], "")],
        indirect=True,
    )
    def test_valid_path_returns_200(self, client, auth, mock_shell):
        response = client.get("/filesystem/tmp/", headers=auth)
        assert response.status_code == 200
        assert response.json == ["file"]

    @pytest.mark.parametrize(
        "mock_shell",
        [(1, [], "ls: root: Permission denied")],
        indirect=True,
    )
    def test_permission_denied_returns_403(self, client, auth, mock_shell):
        response = client.get("/filesystem/tmp/root/", headers=auth)
        assert response.status_code == 403
        assert response.json == {"code": 403, "message": "", "reason": "Forbidden"}

    @pytest.mark.parametrize(
        "mock_shell",
        [(1, [], "ls: /tmp/invalid/: No such file or directory")],
        indirect=True,
    )
    def test_missing_resource_returns_404(self, client, auth, mock_shell):
        response = client.get("/filesystem/tmp/invalid/", headers=auth)
        assert response.status_code == 404
        assert response.json == {"code": 404, "message": "", "reason": "Not Found"}

