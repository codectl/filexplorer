import pytest
from flask import Flask

from src.api.filesystem import FilesystemAPI


@pytest.fixture(scope="class")
def api():
    return FilesystemAPI(username="test")


class TestFilesystemAPI:
    def test_supported_paths(self):
        app = Flask(__name__)
        app.config["SUPPORTED_PATHS"] = ["/test"]
        with app.test_request_context():
            assert FilesystemAPI.supported_paths() == ["/test"]
