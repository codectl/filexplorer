import pytest


@pytest.fixture()
def mocker_shell(mocker, request):
    code, output, errors = request.param
    mock = mocker.Mock(
        **{
            "code": code,
            "output.return_value": output,
            "errors.return_value": errors,
        }
    )
    mocker.patch("shell.Shell.run", return_value=mock)
