from flask import Blueprint, jsonify, request, send_file
from flask_restful import Api, Resource

from src import utils
from src.api.filesystem import (
    DefaultException,
    FileNotFoundException,
    PermissionDeniedException,
    FilesystemAPI,
)
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
                    application/json:
                        schema:
                            type: array
                            items:
                                type: string
                    application/octet-stream:
                        schema:
                            type: string
                            format: binary
            400:
                $ref: "#/components/responses/BadRequest"
            401:
                $ref: "#/components/responses/Unauthorized"
            403:
                $ref: "#/components/responses/Forbidden"
            404:
                $ref: "#/components/responses/NotFound"
        """
        path = f"/{path}"
        username = current_username
        fs_api = FilesystemAPI(username=username)
        if not any(path.startswith(p) for p in fs_api.supported_paths()):
            utils.abort_with(code=400, message="unsupported path")
        result = []
        try:
            result = fs_api.ls(path=path)
        except PermissionDeniedException:
            utils.abort_with(code=403)
        except FileNotFoundException:
            utils.abort_with(code=404)
        except DefaultException as ex:
            utils.abort_with(code=400, message=str(ex))

        accept = request.headers["Accept"]
        if accept == "application/json":
            return jsonify(result)
        elif accept == "application/octet-stream":
            name, buffer = fs_api.file_from_path(path)
            return send_file(buffer, attachment_filename=name, as_attachment=True)
        else:
            utils.abort_with(code=400, message="Unsupported 'Accept' HTTP header")


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
