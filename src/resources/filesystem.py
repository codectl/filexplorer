from flask import Blueprint
from flask_restful import Api, Resource

from src.resources.auth import current_username, requires_auth


blueprint = Blueprint("filesystem", __name__, url_prefix="/filesystem")
api = Api(blueprint)


@api.resource("/<path:path>", endpoint="filesystem")
class Filesystem(Resource):
    @requires_auth(schemes=["basic"])
    def get(self, path):
        """
        List content in given path.
        ---
        parameters:
        - in: path
          name: path
          schema:
            type: string
          required: true
          description: the path to list content from
        tags:
            - filesystem
        security:
            - BasicAuth: []
        responses:
            200:
                description: Ok
                content:
                    text/plain:
                        schema:
                            type: string
            400:
                $ref: '#/components/responses/BadRequest'
            401:
                $ref: '#/components/responses/Unauthorized'
            404:
                $ref: '#/components/responses/NotFound'
        """
        username = current_username
        return f"/{path}"


@api.resource("/supported-paths", endpoint="supported-paths")
class SupportedPaths(Resource):
    def get(self):
        return []
