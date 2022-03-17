from flask import current_app
from shell import CommandError, Shell

__all__ = ("FilesystemAPI",)


class FilesystemAPI:
    def __init__(self, username=None):
        self.username = username
        self._shell = Shell()

    def ls(self, path):
        command = f"ls {path}"
        return self._run(command)

    def sudo(self, command):
        return f"sudo -u {self.username} {command}"

    def _run(self, command):
        process = self._shell.run(self.sudo(command))
        if process.code > 0:
            raise CommandError(process.errors(raw=True))
        return process.output()

    @staticmethod
    def supported_paths():
        return current_app.config["SUPPORTED_PATHS"]
