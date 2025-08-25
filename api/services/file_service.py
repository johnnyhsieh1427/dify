# 修改日期2025-08-25
# 後台FileService新增swap_file功能，用於文件替換
import datetime
import hashlib
import os
import uuid
from typing import Any, Literal, Union

from flask_login import current_user
from werkzeug.exceptions import NotFound

from configs import dify_config
from constants import (
    AUDIO_EXTENSIONS,
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
)
from core.file import helpers as file_helpers
from core.rag.extractor.extract_processor import ExtractProcessor
from extensions.ext_database import db
from extensions.ext_storage import storage
from libs.helper import extract_tenant_id
from models.account import Account
from models.dataset import Document
from models.enums import CreatorUserRole
from models.model import EndUser, UploadFile

from .errors.file import FileTooLargeError, UnsupportedFileTypeError

PREVIEW_WORDS_LIMIT = 3000


class FileService:
    @staticmethod
    def swap_file(
        *,
        filename: str,
        content: bytes,
        mimetype: str,
        user: Union[Account, EndUser, Any],
        source: Literal["datasets"] | None = None,
        source_url: str = "",
        original_document_id: str = "",
        original_dataset_id: str = "",
    ) -> UploadFile:
        # get file extension
        extension = os.path.splitext(filename)[1].lstrip(".").lower()

        # check if filename contains invalid characters
        if any(c in filename for c in ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]):
            raise ValueError("Filename contains invalid characters")

        if len(filename) > 200:
            filename = filename.split(".")[0][:200] + "." + extension

        if source == "datasets" and extension not in DOCUMENT_EXTENSIONS:
            raise UnsupportedFileTypeError()

        # get file size
        file_size = len(content)

        # check if the file size is exceeded
        if not FileService.is_file_size_within_limit(extension=extension, file_size=file_size):
            raise FileTooLargeError

        original_document = db.session.query(Document).where(
            Document.id == original_document_id,
            Document.dataset_id == original_dataset_id
        ).first()
        if not original_document:
            raise NotFound("Document not found")

        upload_file_id = original_document.data_source_info_dict.get("upload_file_id", "")
        original_upload_file = db.session.query(UploadFile).where(
            UploadFile.id == upload_file_id
        ).first()
        if not original_upload_file:
            raise NotFound("Original upload file not found")
        
        try:
            new_file_key = original_upload_file.key.rsplit(".", 1)[-1] + "." + extension
            storage.delete(original_upload_file.key)
            storage.save(new_file_key, content)

            original_document.name = filename
            original_upload_file.name = filename
            original_upload_file.extension = extension
            original_upload_file.size = file_size
            original_upload_file.mime_type = mimetype
            original_upload_file.key = new_file_key
            original_upload_file.hash = hashlib.sha3_256(content).hexdigest()

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"File swap failed: {str(e)}")

        return original_upload_file

    @staticmethod
    def upload_file(
        *,
        filename: str,
        content: bytes,
        mimetype: str,
        user: Union[Account, EndUser, Any],
        source: Literal["datasets"] | None = None,
        source_url: str = "",
    ) -> UploadFile:
        # get file extension
        extension = os.path.splitext(filename)[1].lstrip(".").lower()

        # check if filename contains invalid characters
        if any(c in filename for c in ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]):
            raise ValueError("Filename contains invalid characters")

        if len(filename) > 200:
            filename = filename.split(".")[0][:200] + "." + extension

        if source == "datasets" and extension not in DOCUMENT_EXTENSIONS:
            raise UnsupportedFileTypeError()

        # get file size
        file_size = len(content)

        # check if the file size is exceeded
        if not FileService.is_file_size_within_limit(extension=extension, file_size=file_size):
            raise FileTooLargeError

        # generate file key
        file_uuid = str(uuid.uuid4())

        current_tenant_id = extract_tenant_id(user)

        file_key = "upload_files/" + (current_tenant_id or "") + "/" + file_uuid + "." + extension

        # save file to storage
        storage.save(file_key, content)

        # save file to db
        upload_file = UploadFile(
            tenant_id=current_tenant_id or "",
            storage_type=dify_config.STORAGE_TYPE,
            key=file_key,
            name=filename,
            size=file_size,
            extension=extension,
            mime_type=mimetype,
            created_by_role=(CreatorUserRole.ACCOUNT if isinstance(user, Account) else CreatorUserRole.END_USER),
            created_by=user.id,
            created_at=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
            used=False,
            hash=hashlib.sha3_256(content).hexdigest(),
            source_url=source_url,
        )

        db.session.add(upload_file)
        db.session.commit()

        if not upload_file.source_url:
            upload_file.source_url = file_helpers.get_signed_file_url(upload_file_id=upload_file.id)
            db.session.add(upload_file)
            db.session.commit()

        return upload_file

    @staticmethod
    def is_file_size_within_limit(*, extension: str, file_size: int) -> bool:
        if extension in IMAGE_EXTENSIONS:
            file_size_limit = dify_config.UPLOAD_IMAGE_FILE_SIZE_LIMIT * 1024 * 1024
        elif extension in VIDEO_EXTENSIONS:
            file_size_limit = dify_config.UPLOAD_VIDEO_FILE_SIZE_LIMIT * 1024 * 1024
        elif extension in AUDIO_EXTENSIONS:
            file_size_limit = dify_config.UPLOAD_AUDIO_FILE_SIZE_LIMIT * 1024 * 1024
        else:
            file_size_limit = dify_config.UPLOAD_FILE_SIZE_LIMIT * 1024 * 1024

        return file_size <= file_size_limit

    @staticmethod
    def upload_text(text: str, text_name: str) -> UploadFile:
        if len(text_name) > 200:
            text_name = text_name[:200]
        # user uuid as file name
        file_uuid = str(uuid.uuid4())
        file_key = "upload_files/" + current_user.current_tenant_id + "/" + file_uuid + ".txt"

        # save file to storage
        storage.save(file_key, text.encode("utf-8"))

        # save file to db
        upload_file = UploadFile(
            tenant_id=current_user.current_tenant_id,
            storage_type=dify_config.STORAGE_TYPE,
            key=file_key,
            name=text_name,
            size=len(text),
            extension="txt",
            mime_type="text/plain",
            created_by=current_user.id,
            created_by_role=CreatorUserRole.ACCOUNT,
            created_at=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
            used=True,
            used_by=current_user.id,
            used_at=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
        )

        db.session.add(upload_file)
        db.session.commit()

        return upload_file

    @staticmethod
    def get_file_preview(file_id: str):
        upload_file = db.session.query(UploadFile).where(UploadFile.id == file_id).first()

        if not upload_file:
            raise NotFound("File not found")

        # extract text from file
        extension = upload_file.extension
        if extension.lower() not in DOCUMENT_EXTENSIONS:
            raise UnsupportedFileTypeError()

        text = ExtractProcessor.load_from_upload_file(upload_file, return_text=True)
        text = text[0:PREVIEW_WORDS_LIMIT] if text else ""

        return text

    @staticmethod
    def get_image_preview(file_id: str, timestamp: str, nonce: str, sign: str):
        result = file_helpers.verify_image_signature(
            upload_file_id=file_id, timestamp=timestamp, nonce=nonce, sign=sign
        )
        if not result:
            raise NotFound("File not found or signature is invalid")

        upload_file = db.session.query(UploadFile).where(UploadFile.id == file_id).first()

        if not upload_file:
            raise NotFound("File not found or signature is invalid")

        # extract text from file
        extension = upload_file.extension
        if extension.lower() not in IMAGE_EXTENSIONS:
            raise UnsupportedFileTypeError()

        generator = storage.load(upload_file.key, stream=True)

        return generator, upload_file.mime_type

    @staticmethod
    def get_file_generator_by_file_id(file_id: str, timestamp: str, nonce: str, sign: str):
        result = file_helpers.verify_file_signature(upload_file_id=file_id, timestamp=timestamp, nonce=nonce, sign=sign)
        if not result:
            raise NotFound("File not found or signature is invalid")

        upload_file = db.session.query(UploadFile).where(UploadFile.id == file_id).first()

        if not upload_file:
            raise NotFound("File not found or signature is invalid")

        generator = storage.load(upload_file.key, stream=True)

        return generator, upload_file

    @staticmethod
    def get_public_image_preview(file_id: str):
        upload_file = db.session.query(UploadFile).where(UploadFile.id == file_id).first()

        if not upload_file:
            raise NotFound("File not found or signature is invalid")

        # extract text from file
        extension = upload_file.extension
        if extension.lower() not in IMAGE_EXTENSIONS:
            raise UnsupportedFileTypeError()

        generator = storage.load(upload_file.key)

        return generator, upload_file.mime_type
