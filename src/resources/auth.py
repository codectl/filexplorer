from functools import wraps

from flask import make_response, request

from src.api.auth import AuthAPI


def requires_auth(schemes=("basic")):
    """Validate endpoint against given authorization schemes.
    Fail if authorization properties are missing or are invalid."""

    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            unauthorized = make_response({"code": 401, "reason": "Unauthorized"}, 401)
            if not schemes:
                return unauthorized
            elif "basic" in schemes:
                auth = request.authorization
                if auth and AuthAPI.authenticate(
                        username=auth.username,
                        password=auth.password
                ):
                    return func(*args, **kwargs)
            elif "bearer" in schemes:
                raise NotImplementedError
            return unauthorized

        return decorated

    return wrapper
