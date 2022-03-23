import subprocess

from flask import current_app
from werkzeug.utils import secure_filename

from src import utils

__all__ = ("FilesystemAPI",)


class FilesystemAPI:
    def __init__(self, username=None):
        self.username = str(username) if username else None

    def ls(self, path):
        return self._run(cmd=f"ls {path}", user=self.username)

    def create(self, path, files=()):
        path_files = self.ls(path)
        if any(secure_filename(file.filename) in path_files for file in files):
            raise FileExistsError(f"file already exists in given path")
        for file in files:
            filename = secure_filename(file.filename)
            dst = f"{path}/{filename}"
            self._run(
                cmd=f"tee {dst}",
                stdin=file,
                stdout=subprocess.DEVNULL,
                user=self.username
            )

    @classmethod
    def _run(cls, cmd, **kwargs):
        try:
            stdout = utils.shell(cmd, **kwargs)
        except subprocess.CalledProcessError as ex:
            cls.raise_error(ex.stderr)
        else:
            return stdout.splitlines() if stdout else []

    @staticmethod
    def raise_error(stderr):
        err = stderr.split(":")[-1].strip().lower()
        if err == "no such file or directory":
            raise FileNotFoundError(err)
        elif err == "permission denied":
            raise PermissionError(err)
        else:
            raise Exception(err)

    @staticmethod
    def supported_paths():
        return current_app.config["SUPPORTED_PATHS"]
