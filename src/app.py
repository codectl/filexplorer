from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_plugins.webframeworks.flask import FlaskPlugin
from apispec_ui.flask import Swagger
from flask import Blueprint, Flask, redirect, url_for
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

from src import __meta__, __version__
from src.resources.filesystem import blueprint as filesystem
from src.schemas.serlializers.http import HttpResponseSchema
from src.settings import oas
from src.settings.env import config_class, load_dotenv


def create_app(config_name="development", dotenv=True, configs=None):
    """Create a new app."""

    # define the WSGI application object
    app = Flask(__name__, static_folder=None)

    # load object-based default configuration
    load_dotenv(dotenv)
    app.config.from_object(config_class(config_name))
    app.config.update(configs or {})

    setup_app(app)

    return app


def setup_app(app):
    """Initial setups."""
    url_prefix = app.config["APPLICATION_ROOT"]
    openapi_version = app.config["OPENAPI"]

    # initial blueprint wiring
    index = Blueprint("index", __name__)
    index.register_blueprint(filesystem)
    app.register_blueprint(index, url_prefix=url_prefix)

    # base template for OpenAPI specs
    oas.converter = oas.create_spec_converter(openapi_version)

    spec_template = oas.base_template(
        openapi_version=openapi_version,
        info={
            "title": __meta__["name"],
            "version": __version__,
            "description": __meta__["summary"],
        },
        servers=[oas.Server(url=url_prefix, description=app.config["ENV"])],
        auths=[oas.AuthSchemes.BasicAuth],
        tags=[
            oas.Tag(
                name="filesystem",
                description="CRUD operations over files in the current filesystem",
            )
        ],
        responses=[
            oas.HttpResponse(code=400, reason=HTTP_STATUS_CODES[400]),
            oas.HttpResponse(code=401, reason=HTTP_STATUS_CODES[401]),
            oas.HttpResponse(code=404, reason=HTTP_STATUS_CODES[404]),
        ],
    )

    spec = APISpec(
        title=__meta__["name"],
        version=__version__,
        openapi_version=openapi_version,
        plugins=(FlaskPlugin(), MarshmallowPlugin()),
        **spec_template
    )

    # create paths from app views
    for view in app.view_functions.values():
        spec.path(view=view, app=app, base_path=url_prefix)

    # create views for Swagger
    Swagger(app=app, apispec=spec, config=oas.swagger_configs(app_root=url_prefix))

    # redirect root path to context root
    app.add_url_rule("/", "index", view_func=lambda: redirect(url_for("swagger.ui")))

    # jsonify http errors
    schema = HttpResponseSchema(only=("code", "reason"))
    app.register_error_handler(
        HTTPException,
        lambda ex: (
            schema.dump(
                oas.HttpResponse(code=ex.code, reason=HTTP_STATUS_CODES[ex.code])
            ),
            ex.code,
        ),
    )
