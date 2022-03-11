from flask import Blueprint, jsonify
from flask_restful import abort, Api, Resource

blueprint = Blueprint("filesystem", __name__, url_prefix="/filesystem")
api = Api(blueprint)


@api.resource("/<path:path>", endpoint="filesystem")
class Filesystem(Resource):
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
        responses:
            200:
                description: Ok
        """
        return path
