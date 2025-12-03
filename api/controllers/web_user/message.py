# 修改日期2025-02-28
# 專屬給chat-web的controllers
# 修改日期2025-03-13
# MessageListApi修改搜索條件為ASC

import logging

from flask_restx import fields, marshal_with, reqparse  # type: ignore
from flask_restx.inputs import int_range  # type: ignore
from werkzeug.exceptions import InternalServerError, NotFound

import services
from controllers.web_user import web_chat_ns
from controllers.web_user.error import (
    AppMoreLikeThisDisabledError,
    AppSuggestedQuestionsAfterAnswerDisabledError,
    CompletionRequestError,
    NotChatAppError,
    NotCompletionAppError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from controllers.web_user.wraps import WebUserApiResource
from core.app.entities.app_invoke_entities import InvokeFrom
from core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, QuotaExceededError
from core.model_runtime.errors.invoke import InvokeError
from fields.conversation_fields import message_file_fields
from fields.message_fields import agent_thought_fields, feedback_fields, retriever_resource_fields
from fields.raws import FilesContainedField
from libs import helper
from libs.helper import TimestampField, uuid_value
from models.model import App, AppMode
from services.app_generate_service import AppGenerateService
from services.errors.app import MoreLikeThisDisabledError
from services.errors.conversation import ConversationNotExistsError
from services.errors.message import (
    MessageNotExistsError,
    SuggestedQuestionsAfterAnswerDisabledError,
)
from services.message_service import MessageService

logger = logging.getLogger(__name__)


@web_chat_ns.route("/messages/<uuid:app_id>")
class MessageListApi(WebUserApiResource):
    message_fields = {
        "id": fields.String,
        "conversation_id": fields.String,
        "parent_message_id": fields.String,
        "inputs": FilesContainedField,
        "query": fields.String,
        "answer": fields.String(attribute="re_sign_file_url_answer"),
        "message_files": fields.List(fields.Nested(message_file_fields)),
        "feedback": fields.Nested(feedback_fields, attribute="user_feedback", allow_null=True),
        "retriever_resources": fields.List(fields.Nested(retriever_resource_fields)),
        "created_at": TimestampField,
        "agent_thoughts": fields.List(fields.Nested(agent_thought_fields)),
        "metadata": fields.Raw(attribute="message_metadata_dict"),
        "status": fields.String,
        "error": fields.String,
    }

    message_infinite_scroll_pagination_fields = {
        "limit": fields.Integer,
        "has_more": fields.Boolean,
        "data": fields.List(fields.Nested(message_fields)),
    }

    @web_chat_ns.doc("Get Message List")
    @web_chat_ns.doc(description="Retrieve paginated list of messages from a conversation in a chat application.")
    @web_chat_ns.doc(
        params={
            "conversation_id": {"description": "Conversation UUID", "type": "string", "required": True},
            "first_id": {"description": "First message ID for pagination", "type": "string", "required": False},
            "limit": {
                "description": "Number of messages to return (1-100)",
                "type": "integer",
                "required": False,
                "default": 20,
            },
        }
    )
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Conversation Not Found or Not a Chat App",
            500: "Internal Server Error",
        }
    )
    @marshal_with(message_infinite_scroll_pagination_fields)
    def get(self, app_models: list[App], end_user, app_id):

        parser = (
            reqparse.RequestParser()
            .add_argument("conversation_id", required=True, type=uuid_value, location="args")
            .add_argument("first_id", type=uuid_value, location="args")
            .add_argument("limit", type=int_range(1, 100), required=False, default=20, location="args")
        )
        args = parser.parse_args()

        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotChatAppError()
        
        try:
            return MessageService.pagination_by_first_id(
                # app_model, end_user, args["conversation_id"], args["first_id"], args["limit"], "desc"
                app_model, end_user, args["conversation_id"], args["first_id"], args["limit"]
            )
        except services.errors.conversation.ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except services.errors.message.FirstMessageNotExistsError:
            raise NotFound("First Message Not Exists.")


@web_chat_ns.route("/messages/<uuid:app_id>/<uuid:message_id>/feedbacks")
class MessageFeedbackApi(WebUserApiResource):
    feedback_response_fields = {
        "result": fields.String,
    }

    @web_chat_ns.doc("Create Message Feedback")
    @web_chat_ns.doc(description="Submit feedback (like/dislike) for a specific message.")
    @web_chat_ns.doc(params={"message_id": {"description": "Message UUID", "type": "string", "required": True}})
    @web_chat_ns.doc(
        params={
            "rating": {
                "description": "Feedback rating",
                "type": "string",
                "enum": ["like", "dislike"],
                "required": False,
            },
            "content": {"description": "Feedback content/comment", "type": "string", "required": False},
        }
    )
    @web_chat_ns.doc(
        responses={
            200: "Feedback submitted successfully",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Message Not Found",
            500: "Internal Server Error",
        }
    )
    @marshal_with(feedback_response_fields)
    def post(self, app_models: list[App], end_user, app_id, message_id):
        message_id = str(message_id)

        parser = (
            reqparse.RequestParser()
            .add_argument("rating", type=str, choices=["like", "dislike", None], location="json")
            .add_argument("content", type=str, location="json", default=None)
        )
        args = parser.parse_args()

        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
            MessageService.create_feedback(
                app_model=app_model,
                message_id=message_id,
                user=end_user,
                rating=args.get("rating"),
                content=args.get("content"),
            )
        except services.errors.message.MessageNotExistsError:
            raise NotFound("Message Not Exists.")

        return {"result": "success"}


@web_chat_ns.route("/messages/<uuid:app_id>/<uuid:message_id>/more-like-this")
class MessageMoreLikeThisApi(WebUserApiResource):
    @web_chat_ns.doc("Generate More Like This")
    @web_chat_ns.doc(description="Generate a new completion similar to an existing message (completion apps only).")
    @web_chat_ns.doc(
        params={
            "message_id": {"description": "Message UUID", "type": "string", "required": True},
            "response_mode": {
                "description": "Response mode",
                "type": "string",
                "enum": ["blocking", "streaming"],
                "required": True,
            },
        }
    )
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request - Not a completion app or feature disabled",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Message Not Found",
            500: "Internal Server Error",
        }
    )
    def get(self, app_models: list[App], end_user, app_id, message_id):
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
                           
        if app_model.mode != "completion":
            raise NotCompletionAppError()

        message_id = str(message_id)

        parser = reqparse.RequestParser().add_argument(
            "response_mode", type=str, required=True, choices=["blocking", "streaming"], location="args"
        )
        args = parser.parse_args()

        streaming = args["response_mode"] == "streaming"

        try:
            response = AppGenerateService.generate_more_like_this(
                app_model=app_model,
                user=end_user,
                message_id=message_id,
                invoke_from=InvokeFrom.WEB_APP,
                streaming=streaming,
            )

            return helper.compact_generate_response(response)
        except MessageNotExistsError:
            raise NotFound("Message Not Exists.")
        except MoreLikeThisDisabledError:
            raise AppMoreLikeThisDisabledError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise e
        except Exception:
            logger.exception("internal server error.")
            raise InternalServerError()


@web_chat_ns.route("/messages/<uuid:app_id>/<uuid:message_id>/suggested-questions")
class MessageSuggestedQuestionApi(WebUserApiResource):
    suggested_questions_response_fields = {
        "data": fields.List(fields.String),
    }

    @web_chat_ns.doc("Get Suggested Questions")
    @web_chat_ns.doc(description="Get suggested follow-up questions after a message (chat apps only).")
    @web_chat_ns.doc(params={"message_id": {"description": "Message UUID", "type": "string", "required": True}})
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request - Not a chat app or feature disabled",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Message Not Found or Conversation Not Found",
            500: "Internal Server Error",
        }
    )
    @marshal_with(suggested_questions_response_fields)
    def get(self, app_models: list[App], end_user, app_id, message_id):
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotCompletionAppError()

        message_id = str(message_id)

        try:
            questions = MessageService.get_suggested_questions_after_answer(
                app_model=app_model, user=end_user, message_id=message_id, invoke_from=InvokeFrom.WEB_APP
            )
        except MessageNotExistsError:
            raise NotFound("Message not found")
        except ConversationNotExistsError:
            raise NotFound("Conversation not found")
        except SuggestedQuestionsAfterAnswerDisabledError:
            raise AppSuggestedQuestionsAfterAnswerDisabledError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except Exception:
            logger.exception("internal server error.")
            raise InternalServerError()

        return {"data": questions}
