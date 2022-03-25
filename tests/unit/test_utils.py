import stat
import subprocess
from dataclasses import asdict

import pytest

from src.utils import (
    normpath,
    shell,
    file_mode,
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
    assert file_mode(None) is None
    assert file_mode("") is None
    assert file_mode("-") == stat.S_IFREG
    assert file_mode("-rwx") == stat.S_IFREG
    assert file_mode("-rwxr--r--") == stat.S_IFREG
    assert file_mode("drwxr--r--") == stat.S_IFDIR
    assert file_mode("drwxr--r-- ...") == stat.S_IFDIR
    assert file_mode("prwxr--r--") == 0


def test_isfile():
    assert isfile(None) is False
    assert isfile("") is False
    assert isfile(stat.S_IFREG) is True
    assert isfile(stat.S_IFDIR) is False
    assert isfile(stat.S_IFCHR) is False
    with pytest.raises(TypeError):
        isfile("x")
        isfile("abc")


def test_isdir():
    assert isdir(None) is False
    assert isdir("") is False
    assert isdir(stat.S_IFDIR) is True
    assert isdir(stat.S_IFREG) is False
    assert isdir(stat.S_IFCHR) is False
    with pytest.raises(TypeError):
        isdir("x")
        isdir("abc")


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
