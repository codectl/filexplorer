import os
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


class FilesystemAPI:
    def __init__(self, username=None):
        self.username = username

    def ls(self, path):
        path = utils.validate_path(path, mode="r")
        print(path)
        command = f"ls {path}"
        return self._run(command)

    def sudo(self, command):
        return f"sudo -u {self.username} {command}"

    def _run(self, command):
        process = shell(self.sudo(command))
        if process.code > 0:
            raise CommandError(process.errors(raw=True))
        return process.output()

    @staticmethod
    def file_from_path(path):
        if os.path.isfile(path):
            return os.path.basename(path), path
        elif os.path.isdir(path):
            path = os.path.normpath(path)
            name = f"{os.path.basename(path)}.tar.gz"
            return name, utils.tar_buffer_stream(path)

    @staticmethod
    def supported_paths():
        return current_app.config["SUPPORTED_PATHS"]
