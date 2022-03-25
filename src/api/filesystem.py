import io
import os
import subprocess
import typing

from flask import current_app
from werkzeug.utils import secure_filename

from src import utils

__all__ = ("FilesystemAPI",)


class FilesystemAPI:
    def __init__(self, username=None):
        self.username = str(username) if username else None

    def ls(self, path, flags=""):
        return self._run(cmd=f"ls {flags} {path}", user=self.username)

    def attachment(self, path) -> (str, typing.Union[str, bytes]):
        """Get attachable file data. If given path is a directory,
        return compressed format, otherwise file path is returned.
        """
        stat = self.ls(path=path, flags="-dlL")[0]
        if not utils.isfile(stat=stat) and not utils.isdir(stat=stat):
            raise ValueError("unsupported file type")
        elif utils.isfile(stat=stat):
            cmd = f"cat {path}"
            stream = self._run(cmd=cmd, user=self.username, universal_newlines=False)
            filename = os.path.basename(path)
            content = io.BytesIO(stream)
            return filename, content
        elif utils.isdir(stat=stat):
            archive_dir = os.path.dirname(path)
            archive_name = os.path.basename(path)
            cmd = f"tar -cvpf - -C {archive_dir} {archive_name}"
            stream = self._run(cmd=cmd, user=self.username, universal_newlines=False)
            filename = f"{os.path.basename(path)}.tar.gz"
            content = io.BytesIO(stream)
            return filename, content

    def upload_files(self, path, files=()):
        """Upload given files to the specified path ensuring
        files do not already exist.
        """
        path_files = self.ls(path)
        if any(secure_filename(file.filename) in path_files for file in files):
            raise FileExistsError("file already exists in given path")
        for file in files:
            filename = secure_filename(file.filename)
            dst = f"{path}/{filename}"
            self._run(
                cmd=f"tee {dst}",
                stdin=file,
                stdout=subprocess.DEVNULL,
                user=self.username,
            )

    @classmethod
    def _run(cls, cmd, **kwargs):
        try:
            stdout = utils.shell(cmd, **kwargs)
        except subprocess.CalledProcessError as ex:
            cls.raise_error(ex.stderr)
        else:
            return stdout.splitlines() if isinstance(stdout, str) else stdout

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
