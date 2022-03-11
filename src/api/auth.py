import pam

__all__ = ("AuthAPI",)


class AuthAPI:

    def __init__(self):
        self._conn = pam.pam()

    def authenticate(self, username, password):
        return self._conn.authenticate(username, password)
