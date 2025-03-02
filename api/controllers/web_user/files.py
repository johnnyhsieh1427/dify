# 修改日期2025-02-28
# 專屬給chat-web的controllers

from flask import request
from flask_restful import marshal_with  # type: ignore

import services
from controllers.common.errors import FilenameNotExistsError
from controllers.web_user.error import FileTooLargeError, NoFileUploadedError, TooManyFilesError, UnsupportedFileTypeError
from controllers.web_user.wraps import WebUserApiResource
from fields.file_fields import file_fields
from services.file_service import FileService


class FileApi(WebUserApiResource):
    @marshal_with(file_fields)
    def post(self, app_models, end_user):
        file = request.files["file"]
        source = request.form.get("source")

        if "file" not in request.files:
            raise NoFileUploadedError()

        if len(request.files) > 1:
            raise TooManyFilesError()

        if not file.filename:
            raise FilenameNotExistsError

        if source not in ("datasets", None):
            source = None

        try:
            upload_file = FileService.upload_file(
                filename=file.filename,
                content=file.read(),
                mimetype=file.mimetype,
                user=end_user,
                source="datasets" if source == "datasets" else None,
            )
        except services.errors.file.FileTooLargeError as file_too_large_error:
            raise FileTooLargeError(file_too_large_error.description)
        except services.errors.file.UnsupportedFileTypeError:
            raise UnsupportedFileTypeError()

        return upload_file, 201
