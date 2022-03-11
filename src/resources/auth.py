from functools import wraps

from flask import jsonify, make_response, request

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
                if not auth or not AuthAPI().authenticate(
                        username=auth.username,
                        password=auth.password
                ):
                    return make_response({"code": 401, "reason": "Unauthorized"}, 401)
            elif "bearer" in schemes:
                raise NotImplemented()
            elif "digest" in schemes:
                raise NotImplemented()
            return func(*args, **kwargs)

        return decorated

    return wrapper
