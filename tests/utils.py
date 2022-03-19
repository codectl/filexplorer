from dataclasses import dataclass


@dataclass
class MockShell:
    code: int = 0

    @staticmethod
    def output(*args, **kwargs):
        return ""

    @staticmethod
    def errors(*args, **kwargs):
        return ""
