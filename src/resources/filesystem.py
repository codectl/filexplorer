from flask import Blueprint, jsonify
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
                application/json:
                    schema:
                        type: array
                        items:
                            type: string
            400:
                $ref: '#/components/responses/BadRequest'
            401:
                $ref: '#/components/responses/Unauthorized'
            404:
                $ref: '#/components/responses/NotFound'
        """
        path = f"/{path}"
        username = current_username
        fs_api = FilesystemAPI(username=username)
        if not any(path.startswith(p) for p in fs_api.supported_paths()):
            abort(400, code=400, reason=HTTP_STATUS_CODES[400])
        try:
            result = fs_api.ls(path=path)
        except Exception:
            abort(404, code=404, reason=HTTP_STATUS_CODES[404])
        return jsonify(result)


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
