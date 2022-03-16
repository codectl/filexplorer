import pam

__all__ = ("AuthAPI",)


class AuthAPI:

    @staticmethod
    def authenticate(username, password):
        return pam.authenticate(username, password)
