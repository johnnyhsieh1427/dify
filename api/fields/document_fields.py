# 修改日期2025-07-23
# 新增upload_file_fields的欄位

from flask_restful import fields

from fields.dataset_fields import dataset_fields
from libs.helper import TimestampField

document_metadata_fields = {
    "id": fields.String,
    "name": fields.String,
    "type": fields.String,
    "value": fields.String,
}

document_fields = {
    "id": fields.String,
    "position": fields.Integer,
    "data_source_type": fields.String,
    "data_source_info": fields.Raw(attribute="data_source_info_dict"),
    "data_source_detail_dict": fields.Raw(attribute="data_source_detail_dict"),
    "dataset_process_rule_id": fields.String,
    "name": fields.String,
    "created_from": fields.String,
    "created_by": fields.String,
    "created_at": TimestampField,
    "tokens": fields.Integer,
    "indexing_status": fields.String,
    "error": fields.String,
    "enabled": fields.Boolean,
    "disabled_at": TimestampField,
    "disabled_by": fields.String,
    "archived": fields.Boolean,
    "display_status": fields.String,
    "word_count": fields.Integer,
    "hit_count": fields.Integer,
    "doc_form": fields.String,
    "doc_metadata": fields.List(fields.Nested(document_metadata_fields), attribute="doc_metadata_details"),
}

document_with_segments_fields = {
    "id": fields.String,
    "position": fields.Integer,
    "data_source_type": fields.String,
    "data_source_info": fields.Raw(attribute="data_source_info_dict"),
    "data_source_detail_dict": fields.Raw(attribute="data_source_detail_dict"),
    "dataset_process_rule_id": fields.String,
    "process_rule_dict": fields.Raw(attribute="process_rule_dict"),
    "name": fields.String,
    "created_from": fields.String,
    "created_by": fields.String,
    "created_at": TimestampField,
    "tokens": fields.Integer,
    "indexing_status": fields.String,
    "error": fields.String,
    "enabled": fields.Boolean,
    "disabled_at": TimestampField,
    "disabled_by": fields.String,
    "archived": fields.Boolean,
    "display_status": fields.String,
    "word_count": fields.Integer,
    "hit_count": fields.Integer,
    "completed_segments": fields.Integer,
    "total_segments": fields.Integer,
    "doc_metadata": fields.List(fields.Nested(document_metadata_fields), attribute="doc_metadata_details"),
}

dataset_and_document_fields = {
    "dataset": fields.Nested(dataset_fields),
    "documents": fields.List(fields.Nested(document_fields)),
    "batch": fields.String,
}

document_status_fields = {
    "id": fields.String,
    "indexing_status": fields.String,
    "processing_started_at": TimestampField,
    "parsing_completed_at": TimestampField,
    "cleaning_completed_at": TimestampField,
    "splitting_completed_at": TimestampField,
    "completed_at": TimestampField,
    "paused_at": TimestampField,
    "error": fields.String,
    "stopped_at": TimestampField,
    "completed_segments": fields.Integer,
    "total_segments": fields.Integer,
}

document_status_fields_list = {"data": fields.List(fields.Nested(document_status_fields))}

upload_file_fields = {
    "id": fields.String,
    "tenant_id": fields.String,
    "storage_type": fields.String,
    "key": fields.String,
    "name": fields.String,
    "size": fields.Integer,
    "extension": fields.String,
    "mime_type": fields.String,
    "created_by": fields.String,
    "created_at": TimestampField,
    "used": fields.Boolean,
    "used_by": fields.String,
    "used_at": TimestampField,
    "hash": fields.String,
    "created_by_role": fields.String,
    "source_url": fields.String,
}