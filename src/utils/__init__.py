import io
import os
import tarfile

from flask_restful import abort
from werkzeug.http import HTTP_STATUS_CODES

from src.schemas.serlializers.http import HttpResponseSchema
from src.settings import oas


def validate_path(path, mode="r"):
    """Path validation.
    :raises:
        FileNotFoundError: if file is not found
        PermissionError: if missing permissions
        OSError: base exception
    """
    path = os.path.normpath(path)
    try:
        open(path, mode=mode)
    except IsADirectoryError:
        pass
    return path


def http_response(code: int, message="", serialize=True, **kwargs):
    response = oas.HttpResponse(
        code=code, reason=HTTP_STATUS_CODES[code], message=message
    )
    if serialize:
        return HttpResponseSchema(**kwargs).dump(response)
    return response


def abort_with(code: int, message=""):
    abort(code, **http_response(code, message=message))


def tar_buffer_stream(path):
    """Get a compressed tar.gz byte stream of a given path."""
    path = os.path.normpath(path)
    basename = os.path.basename(path)
    file_io = io.BytesIO()
    with tarfile.open(fileobj=file_io, mode="w|gz") as tar:
        tar.add(path, arcname=basename)
    file_io.seek(0)
    return file_io
