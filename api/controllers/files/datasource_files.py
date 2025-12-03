from urllib.parse import quote

from flask import Response
from flask_restx import Resource, reqparse
from werkzeug.exceptions import Forbidden, NotFound

from controllers.common.errors import UnsupportedFileTypeError
from controllers.files import files_ns
from core.datasource.datasource_file_manager import DatasourceFileManager


@files_ns.route("/datasources/<uuid:file_id>.<string:extension>")
class DatasourceFileApi(Resource):
    def get(self, file_id, extension):
        file_id = str(file_id)

        parser = (
            reqparse.RequestParser()
            .add_argument("timestamp", type=str, required=True, location="args")
            .add_argument("nonce", type=str, required=True, location="args")
            .add_argument("sign", type=str, required=True, location="args")
            .add_argument("as_attachment", type=bool, required=False, default=False, location="args")
        )

        args = parser.parse_args()
        if not DatasourceFileManager.verify_file(
            datasource_file_id=file_id,
            timestamp=args["timestamp"],
            nonce=args["nonce"],
            sign=args["sign"],
        ):
            raise Forbidden("Invalid request.")

        try:
            stream, datasource_file = DatasourceFileManager.get_file_generator_by_datasource_file_id(file_id)
        except Exception:  # pragma: no cover - storage errors bubble up as unsupported type
            raise UnsupportedFileTypeError()

        if not stream or not datasource_file:
            raise NotFound("file is not found")

        response = Response(
            stream,
            mimetype=datasource_file.mimetype,
            direct_passthrough=True,
            headers={},
        )

        if datasource_file.size and datasource_file.size > 0:
            response.headers["Content-Length"] = str(datasource_file.size)

        if args["as_attachment"]:
            download_name = datasource_file.name or f"{file_id}{extension.lower() or ''}"
            encoded_filename = quote(download_name)
            response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
            response.headers["Content-Type"] = "application/octet-stream"

        return response
