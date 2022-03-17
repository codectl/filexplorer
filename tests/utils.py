from dataclasses import dataclass


@dataclass
class MockShell:
    code: int = 0
    output = lambda *args, **kwargs: ""
    errors = lambda *args, **kwargs: ""
