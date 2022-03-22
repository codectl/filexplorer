import contextlib
import io
import os
import tarfile

from flask_restful import abort
from werkzeug.http import HTTP_STATUS_CODES

from src.schemas.serlializers.http import HttpResponseSchema
from src.settings import oas


def normpath(path):
    return os.path.normpath(f"/{path.strip('/')}")


def validate_path(path, mode="r"):
    """Path validation.
    :raises:
        FileNotFoundError: if file is not found
        PermissionError: if missing permissions
        OSError: base exception
    """
    path = normpath(path)
    with contextlib.suppress(IsADirectoryError), open(path, mode=mode):
        pass
    return path


def attachment(path):
    """Get file attachment from given path.
    If path is a file, return file.
    If path is a directory, return compressed dir.
    """
    path = normpath(path)
    if os.path.isfile(path):
        return os.path.basename(path), path
    elif os.path.isdir(path):
        name = f"{os.path.basename(path)}.tar.gz"
        return name, tar_buffer_stream(path)


def tar_buffer_stream(path):
    """Get a compressed tar.gz byte stream of a given path."""
    path = normpath(path)
    basename = os.path.basename(path)
    file_io = io.BytesIO()
    with tarfile.open(fileobj=file_io, mode="w|gz") as tar:
        tar.add(path, arcname=basename)
    file_io.seek(0)
    return file_io


def http_response(code: int, message="", serialize=True, **kwargs):
    response = oas.HttpResponse(
        code=code, reason=HTTP_STATUS_CODES[code], message=message
    )
    if serialize:
        return HttpResponseSchema(**kwargs).dump(response)
    return response


def abort_with(code: int, message=""):
    abort(code, **http_response(code, message=message))
