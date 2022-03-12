import base64

from src.api.auth import AuthAPI


class TestFilesystem:
    def test_unauthorized_request_throws_401(self, client):
        response = client.get("/filesystem/tmp", headers={})
        assert response.status_code == 401

    def test_authorized_request_returns_200(self, client, mocker):
        mocker.patch.object(AuthAPI, "authenticate", return_value=True)
        headers = {"Authorization": f"Basic {base64.b64encode(b'user:pass').decode()}"}
        response = client.get("/filesystem/tmp", headers=headers)
        assert response.status_code == 200

    def test_supported_paths(self, client):
        response = client.get("/filesystem/supported-paths")
        assert response.status_code == 200
