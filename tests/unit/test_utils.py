from dataclasses import asdict

import pytest

from src.utils import (
    normpath,
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


def test_file_type():
    assert file_type(None) is None
    assert file_type("") is None
    assert file_type("-") is "-"
    assert file_type("-rwx") is "-"
    assert file_type("-rwxr--r--") is "-"
    assert file_type("drwxr--r--") is "d"
    assert file_type("prwxr--r-- etc") is "p"


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
