from flask import Blueprint, jsonify, request, Response
from flask_restful import abort, Api, Resource
from werkzeug.http import HTTP_STATUS_CODES

from src.api.filesystem import FilesystemAPI
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
        path = f"/{path}"
        try:
            result = FilesystemAPI(username=username).ls(path=path)
        except Exception:
            abort(404, code=404, reason=HTTP_STATUS_CODES[404])
        return Response(result, mimetype=request.headers["Accept"])


@api.resource("/supported-paths", endpoint="supported-paths")
class SupportedPaths(Resource):
    def get(self):
        """
        List content in given path.
        ---
        tags:
            - filesystem
        responses:
            200:
                description: Ok
                content:
                    application/json:
                        schema:
                            type: array
                            items:
                                type: string
        """
        return jsonify(FilesystemAPI.supported_paths())
