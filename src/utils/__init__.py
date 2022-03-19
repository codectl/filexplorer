from flask_restful import abort
from werkzeug.http import HTTP_STATUS_CODES

from src.schemas.serlializers.http import HttpResponseSchema
from src.settings import oas


def clean_sh_error(error):
    """Get a clean error returned by a shell command."""
    return error.split(":")[-1].strip()


def http_response(code: int, message="", serialize=True, **kwargs):
    response = oas.HttpResponse(
        code=code, reason=HTTP_STATUS_CODES[code], message=message
    )
    if serialize:
        return HttpResponseSchema(**kwargs).dump(response)
    return response


def abort_with(code: int, message=""):
    abort(code, **http_response(400, message=message))
