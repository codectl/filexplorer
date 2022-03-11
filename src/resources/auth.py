from functools import wraps

from flask import request

from src.api.auth import AuthAPI


def requires_auth(schemes=("basic")):
    """
    Validate endpoint against given authorization schemes. Fail if authorization
    properties are missing or are invalid.
    """
    def wrapper(func):

        @wraps(func)
        def decorated(*args, **kwargs):
            if "basic" in schemes:
                auth = request.authorization
                if not auth and not AuthAPI().authenticate(
                        username=auth.username,
                        password=auth.password
                ):
                    abort(401, code=401, reason="Unauthorized")
            elif "bearer" in schemes:
                raise NotImplemented()
            elif "digest" in schemes:
                raise NotImplemented()
            return func(*args, **kwargs)

        return decorated

    return wrapper
