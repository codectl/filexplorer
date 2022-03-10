from flask import Blueprint, jsonify
from flask_restful import abort, Api, Resource

blueprint = Blueprint("filesystem", __name__, url_prefix="/filesystem")
api = Api(blueprint)


@api.resource("/<path:path>", endpoint="filesystem")
class Filesystem(Resource):
    def get(self):
        """
        List content.
        ---
        tags:
            - filesystem
        responses:
            200:
                description: Ok
        """
        return "ok"
