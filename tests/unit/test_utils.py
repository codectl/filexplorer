import subprocess
from dataclasses import asdict

import pytest

from src.utils import (
    normpath,
    shell,
    file_type,
    isfile,
    isdir,
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


def test_shell(mocker):
    mock = mocker.patch("subprocess.Popen").return_value
    mock.configure_mock(
        **{"communicate.return_value": ("file.txt", ""), "returncode": 0}
    )
    assert shell("ls") == "file.txt"

    mock.configure_mock(**{"communicate.return_value": ("", "error"), "returncode": 1})
    with pytest.raises(subprocess.CalledProcessError) as ex:
        shell("ls")
    assert ex.value.returncode == 1
    assert ex.value.stderr == "error"


def test_file_type():
    assert file_type(None) is None
    assert file_type("") is None
    assert file_type("-") == "-"
    assert file_type("-rwx") == "-"
    assert file_type("-rwxr--r--") == "-"
    assert file_type("drwxr--r--") == "d"
    assert file_type("prwxr--r-- etc") == "p"


def test_isfile():
    assert isfile(None) is False
    assert isfile("") is False
    assert isfile("d") is False
    assert isfile("p") is False
    assert isfile("etc") is False
    assert isfile("-") is True


def test_isdir():
    assert isdir(None) is False
    assert isdir("") is False
    assert isdir("p") is False
    assert isdir("etc") is False
    assert isdir("-") is False
    assert isdir("d") is True


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
