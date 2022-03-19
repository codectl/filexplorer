import typing

from flask import current_app
from shell import CommandError, shell

from src import utils

__all__ = (
    "DefaultException",
    "FileNotFoundException",
    "PermissionDeniedException",
    "FilesystemAPI",
)


class DefaultException(CommandError):
    pass


class FileNotFoundException(CommandError):
    pass


class PermissionDeniedException(CommandError):
    pass


class FilesystemAPI:
    def __init__(self, username=None):
        self.username = username

    def ls(self, path):
        command = f"ls {path}"
        return self._run(command)

    def sudo(self, command):
        return f"sudo -u {self.username} {command}"

    def _run(self, command):
        process = shell(self.sudo(command))
        if process.code > 0:
            error = utils.clean_sh_error(process.errors(raw=True))
            raise self.raise_error(error)(error)
        return process.output()

    @staticmethod
    def raise_error(error) -> typing.Type[CommandError]:
        if error == "No such file or directory":
            return FileNotFoundException
        elif error == "Permission denied":
            return PermissionDeniedException
        else:
            return DefaultException

    @staticmethod
    def supported_paths():
        return current_app.config["SUPPORTED_PATHS"]
