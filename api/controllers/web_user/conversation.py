# 修改日期2025-02-28
# 專屬給chat-web的controllers


from flask_restx import fields, marshal_with, reqparse
from flask_restx.inputs import int_range  # type: ignore
from sqlalchemy.orm import Session
from werkzeug.exceptions import NotFound

from controllers.web_user import web_chat_ns
from controllers.web_user.error import NotChatAppError
from controllers.web_user.wraps import WebUserApiResource
from core.app.entities.app_invoke_entities import InvokeFrom
from extensions.ext_database import db
from fields.conversation_fields import conversation_infinite_scroll_pagination_fields, simple_conversation_fields
from libs.helper import uuid_value
from models.model import App, AppMode
from services.conversation_service import ConversationService
from services.errors.conversation import ConversationNotExistsError, LastConversationNotExistsError
from services.web_conversation_service import WebConversationService


@web_chat_ns.route("/conversations/<uuid:app_id>")
class ConversationListApi(WebUserApiResource):
    @web_chat_ns.doc("Get Conversation List")
    @web_chat_ns.doc(description="Retrieve paginated list of conversations for a chat application.")
    @web_chat_ns.doc(
        params={
            "last_id": {"description": "Last conversation ID for pagination", "type": "string", "required": False},
            "limit": {
                "description": "Number of conversations to return (1-100)",
                "type": "integer",
                "required": False,
                "default": 20,
            },
            "pinned": {
                "description": "Filter by pinned status",
                "type": "string",
                "enum": ["true", "false"],
                "required": False,
            },
            "sort_by": {
                "description": "Sort order",
                "type": "string",
                "enum": ["created_at", "-created_at", "updated_at", "-updated_at"],
                "required": False,
                "default": "-updated_at",
            },
        }
    )
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "App Not Found or Not a Chat App",
            500: "Internal Server Error",
        }
    )
    @marshal_with(conversation_infinite_scroll_pagination_fields)
    def get(self, app_models: list[App], end_user, app_id):

        parser = (
            reqparse.RequestParser()
            .add_argument("last_id", type=uuid_value, location="args")
            .add_argument("limit", type=int_range(1, 100), required=False, default=20, location="args")
            .add_argument("pinned", type=str, choices=["true", "false", None], location="args")
            .add_argument(
                "sort_by",
                type=str,
                choices=["created_at", "-created_at", "updated_at", "-updated_at"],
                required=False,
                default="-updated_at",
                location="args",
            )
        )
        args = parser.parse_args()

        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")

        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotChatAppError()
        
        pinned = None
        if "pinned" in args and args["pinned"] is not None:
            pinned = args["pinned"] == "true"

        try:
            with Session(db.engine) as session:
                return WebConversationService.pagination_by_last_id(
                    session=session,
                    app_model=app_model,
                    user=end_user,
                    last_id=args["last_id"],
                    limit=args["limit"],
                    invoke_from=InvokeFrom.WEB_APP,
                    pinned=pinned,
                    sort_by=args["sort_by"],
                )
        except LastConversationNotExistsError:
            raise NotFound("Last Conversation Not Exists.")


@web_chat_ns.route("/conversations/<uuid:app_id>/<uuid:c_id>")
class ConversationApi(WebUserApiResource):
    delete_response_fields = {
        "result": fields.String,
    }

    @web_chat_ns.doc("Delete Conversation")
    @web_chat_ns.doc(description="Delete a specific conversation.")
    @web_chat_ns.doc(params={"c_id": {"description": "Conversation UUID", "type": "string", "required": True}})
    @web_chat_ns.doc(
        responses={
            204: "Conversation deleted successfully",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Conversation Not Found or Not a Chat App",
            500: "Internal Server Error",
        }
    )
    @marshal_with(delete_response_fields)
    def delete(self, app_models: list[App], end_user, app_id, c_id):

        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotChatAppError()

        conversation_id = str(c_id)
        try:
            ConversationService.delete(app_model, conversation_id, end_user)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        WebConversationService.unpin(app_model, conversation_id, end_user)

        return {"result": "success"}, 204


@web_chat_ns.route("/conversations/<uuid:app_id>/<uuid:c_id>/name")
class ConversationRenameApi(WebUserApiResource):
    @web_chat_ns.doc("Rename Conversation")
    @web_chat_ns.doc(description="Rename a specific conversation with a custom name or auto-generate one.")
    @web_chat_ns.doc(params={"c_id": {"description": "Conversation UUID", "type": "string", "required": True}})
    @web_chat_ns.doc(
        params={
            "name": {"description": "New conversation name", "type": "string", "required": False},
            "auto_generate": {
                "description": "Auto-generate conversation name",
                "type": "boolean",
                "required": False,
                "default": False,
            },
        }
    )
    @web_chat_ns.doc(
        responses={
            200: "Conversation renamed successfully",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Conversation Not Found or Not a Chat App",
            500: "Internal Server Error",
        }
    )
    @marshal_with(simple_conversation_fields)
    def post(self, app_models: list[App], end_user, app_id, c_id):
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotChatAppError()

        conversation_id = str(c_id)

        parser = (
            reqparse.RequestParser()
            .add_argument("name", type=str, required=False, location="json")
            .add_argument("auto_generate", type=bool, required=False, default=False, location="json")
        )
        args = parser.parse_args()

        try:
            return ConversationService.rename(app_model, conversation_id, end_user, args["name"], args["auto_generate"])
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")


@web_chat_ns.route("/conversations/<uuid:app_id>/<uuid:c_id>/pin")
class ConversationPinApi(WebUserApiResource):
    pin_response_fields = {
        "result": fields.String,
    }

    @web_chat_ns.doc("Pin Conversation")
    @web_chat_ns.doc(description="Pin a specific conversation to keep it at the top of the list.")
    @web_chat_ns.doc(params={"c_id": {"description": "Conversation UUID", "type": "string", "required": True}})
    @web_chat_ns.doc(
        responses={
            200: "Conversation pinned successfully",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Conversation Not Found or Not a Chat App",
            500: "Internal Server Error",
        }
    )
    @marshal_with(pin_response_fields)
    def patch(self, app_models: list[App], end_user, app_id, c_id):
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotChatAppError()

        conversation_id = str(c_id)

        try:
            WebConversationService.pin(app_model, conversation_id, end_user)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")

        return {"result": "success"}


@web_chat_ns.route("/conversations/<uuid:app_id>/<uuid:c_id>/unpin")
class ConversationUnPinApi(WebUserApiResource):
    unpin_response_fields = {
        "result": fields.String,
    }

    @web_chat_ns.doc("Unpin Conversation")
    @web_chat_ns.doc(description="Unpin a specific conversation to remove it from the top of the list.")
    @web_chat_ns.doc(params={"c_id": {"description": "Conversation UUID", "type": "string", "required": True}})
    @web_chat_ns.doc(
        responses={
            200: "Conversation unpinned successfully",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Conversation Not Found or Not a Chat App",
            500: "Internal Server Error",
        }
    )
    @marshal_with(unpin_response_fields)
    def patch(self, app_models: list[App], end_user, app_id, c_id):
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotChatAppError()

        conversation_id = str(c_id)
        WebConversationService.unpin(app_model, conversation_id, end_user)

        return {"result": "success"}
