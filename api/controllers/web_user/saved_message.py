# 修改日期2025-02-28
# 專屬給chat-web的controllers

from flask_restful import fields, marshal_with, reqparse  # type: ignore
from flask_restful.inputs import int_range  # type: ignore
from werkzeug.exceptions import NotFound

from controllers.web_user import api
from controllers.web_user.error import NotCompletionAppError
from controllers.web_user.wraps import WebUserApiResource
from fields.conversation_fields import message_file_fields
from libs.helper import TimestampField, uuid_value
from models.model import App
from services.errors.message import MessageNotExistsError
from services.saved_message_service import SavedMessageService

feedback_fields = {"rating": fields.String}

message_fields = {
    "id": fields.String,
    "inputs": fields.Raw,
    "query": fields.String,
    "answer": fields.String,
    "message_files": fields.List(fields.Nested(message_file_fields)),
    "feedback": fields.Nested(feedback_fields, attribute="user_feedback", allow_null=True),
    "created_at": TimestampField,
}


class SavedMessageListApi(WebUserApiResource):
    saved_message_infinite_scroll_pagination_fields = {
        "limit": fields.Integer,
        "has_more": fields.Boolean,
        "data": fields.List(fields.Nested(message_fields)),
    }

    @marshal_with(saved_message_infinite_scroll_pagination_fields)
    def get(self, app_models: list[App], end_user, app_id):
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        if app_model.mode != "completion":
            raise NotCompletionAppError()
        
        parser = reqparse.RequestParser()
        parser.add_argument("last_id", type=uuid_value, location="args")
        parser.add_argument("limit", type=int_range(1, 100), required=False, default=20, location="args")
        args = parser.parse_args()
        
        return SavedMessageService.pagination_by_last_id(app_model, end_user, args["last_id"], args["limit"])

    def post(self, app_models: list[App], end_user, app_id):
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        if app_model.mode != "completion":
            raise NotCompletionAppError()

        parser = reqparse.RequestParser()
        parser.add_argument("message_id", type=uuid_value, required=True, location="json")
        args = parser.parse_args()

        try:
            SavedMessageService.save(app_model, end_user, args["message_id"])
        except MessageNotExistsError:
            raise NotFound("Message Not Exists.")

        return {"result": "success"}


class SavedMessageApi(WebUserApiResource):
    def delete(self, app_models: list[App], end_user, app_id, message_id):
        message_id = str(message_id)
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        if app_model.mode != "completion":
            raise NotCompletionAppError()

        SavedMessageService.delete(app_model, end_user, message_id)

        return {"result": "success"}


api.add_resource(SavedMessageListApi, "/saved-messages/<uuid:app_id>")
api.add_resource(SavedMessageApi, "/saved-messages/<uuid:app_id>/<uuid:message_id>")
