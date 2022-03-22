from dataclasses import asdict

import pytest

from src.utils import (
    normpath,
    validate_path,
    attachment,
    http_response,
)


def test_normpath():
    assert normpath("/tmp") == "/tmp"
    assert normpath("//tmp") == "/tmp"
    assert normpath("///tmp") == "/tmp"
    assert normpath("tmp") == "/tmp"
    assert normpath("/tmp/") == "/tmp"
    assert normpath("tmp/") == "/tmp"
    assert normpath("//tmp//") == "/tmp"


def test_validate_path(mocker):
    with pytest.raises(ValueError):
        validate_path("/tmp", mode="xyz")
    mock_open = mocker.mock_open
    mocker.patch("builtins.open", new_callable=mock_open, read_data="data")
    assert validate_path("/tmp", mode="r") == "/tmp"
    assert validate_path("/tmp/", mode="r") == "/tmp"
    assert validate_path("tmp", mode="r") == "/tmp"
    assert validate_path("/tmp/foot.txt", mode="r") == "/tmp/foot.txt"
    mocker.patch("builtins.open", side_effect=FileNotFoundError)
    with pytest.raises(FileNotFoundError):
        validate_path("/tmp/foo.txt", mode="r")
    mocker.patch("builtins.open", side_effect=PermissionError)
    with pytest.raises(PermissionError):
        validate_path("/tmp/root/", mode="r")


def test_attachment(mocker):
    mocker.patch("os.path.isfile", return_value=True)
    assert attachment("/tmp/foo.txt") == ("foo.txt", "/tmp/foo.txt")

    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch("os.path.isdir", return_value=True)
    mocker.patch("src.utils.tar_buffer_stream", return_value=b"")
    assert attachment("/tmp/foo/") == ("foo.tar.gz", b"")


def test_response():
    assert http_response(code=200, message="test") == {
        "code": 200,
        "reason": "OK",
        "message": "test",
    }
    assert asdict(http_response(code=400, message="error", serialize=False)) == {
        "code": 400,
        "reason": "Bad Request",
        "message": "error",
    }
