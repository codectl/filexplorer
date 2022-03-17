import shell

__all__ = ("FilesystemAPI",)


class FilesystemAPI:

    def __init__(self, username=None):
        self.username = username
        self._shell = shell.Shell()

    def ls(self, path):
        command = f"ls -al {path}"
        return self._run(command)

    def sudo(self, command):
        return f"sudo -u {self.username} {command}"

    def _run(self, command):
        process = self._shell.run(self.sudo(command))
        if process.code > 0:
            raise shell.CommandError(process.errors(raw=True))
        return process.output(raw=True)
