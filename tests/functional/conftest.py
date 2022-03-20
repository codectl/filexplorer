import pytest

from src.app import create_app


@pytest.fixture(scope="class")
def app():
    app = create_app(
        config_name="testing",
        dotenv=False,
        configs={
            "FLASK_RUN_HOST": "localhost",
            "FLASK_RUN_PORT": 5000,
            "APPLICATION_ROOT": "/",
            "SUPPORTED_MEASURABLES": ["foo", "bar"],
            "OPENAPI": "3.0.3",  # default version
            "SUPPORTED_PATHS": ["/tmp"],
        },
    )
    with app.test_request_context():
        yield app


@pytest.fixture(scope="class")
def client(app):
    return app.test_client()


@pytest.fixture()
def mock_shell(mocker, request):
    code, output, errors = request.param
    mock = mocker.Mock(
        **{
            "code": code,
            "output.return_value": output,
            "errors.return_value": errors,
        }
    )
    mocker.patch("shell.Shell.run", return_value=mock)
