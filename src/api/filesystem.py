import os
import typing

from flask import current_app
from shell import CommandError, shell

from src import utils

__all__ = ("FilesystemAPI",)


class FilesystemAPI:
    def __init__(self, username=None):
        self.username = username

    def ls(self, path):
        path = utils.validate_path(path, mode="r")
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
    def supported_paths():
        return current_app.config["SUPPORTED_PATHS"]
