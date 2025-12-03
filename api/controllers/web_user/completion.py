# 修改日期2025-02-28
# 專屬給chat-web的controllers

import logging

from flask_restx import reqparse  # type: ignore
from werkzeug.exceptions import InternalServerError, NotFound

import services
from controllers.web_user import web_chat_ns
from controllers.web_user.error import (
    AppUnavailableError,
    CompletionRequestError,
    ConversationCompletedError,
    NotChatAppError,
    NotCompletionAppError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from controllers.web_user.error import InvokeRateLimitError as InvokeRateLimitHttpError
from controllers.web_user.wraps import WebUserApiResource
from core.app.apps.base_app_queue_manager import AppQueueManager
from core.app.entities.app_invoke_entities import InvokeFrom
from core.errors.error import (
    ModelCurrentlyNotSupportError,
    ProviderTokenNotInitError,
    QuotaExceededError,
)
from core.model_runtime.errors.invoke import InvokeError
from libs import helper
from libs.helper import uuid_value
from models.model import App, AppMode
from services.app_generate_service import AppGenerateService
from services.errors.llm import InvokeRateLimitError

logger = logging.getLogger(__name__)


# define completion api for user
@web_chat_ns.route("/completion-messages/<uuid:app_id>")
class CompletionApi(WebUserApiResource):
    @web_chat_ns.doc("Completion Messages")
    @web_chat_ns.doc(description="Generate completion messages using the completion app.")
    @web_chat_ns.doc(
        params={
            "inputs": {"description": "Input variables for the completion", "type": "object", "required": True},
            "query": {"description": "Query text for completion", "type": "string", "required": False},
            "files": {"description": "Files to be processed", "type": "array", "required": False},
            "response_mode": {
                "description": "Response mode: blocking or streaming",
                "type": "string",
                "enum": ["blocking", "streaming"],
                "required": False,
            },
            "retriever_from": {"description": "Source of retriever", "type": "string", "required": False},
        }
    )
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "App Not Found",
            500: "Internal Server Error",
        }
    )
    def post(self, app_models: list[App], end_user, app_id):
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
            
        if app_model.mode != "completion":
            raise NotCompletionAppError()

        parser = (
            reqparse.RequestParser()
            .add_argument("inputs", type=dict, required=True, location="json")
            .add_argument("query", type=str, location="json", default="")
            .add_argument("files", type=list, required=False, location="json")
            .add_argument("response_mode", type=str, choices=["blocking", "streaming"], location="json")
            .add_argument("retriever_from", type=str, required=False, default="web_app", location="json")
        )

        args = parser.parse_args()

        streaming = args["response_mode"] == "streaming"
        args["auto_generate_name"] = False

        try:
            response = AppGenerateService.generate(
                app_model=app_model, user=end_user, args=args, invoke_from=InvokeFrom.WEB_APP, streaming=streaming
            )

            return helper.compact_generate_response(response)
        except services.errors.conversation.ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except services.errors.conversation.ConversationCompletedError:
            raise ConversationCompletedError()
        except services.errors.app_model_config.AppModelConfigBrokenError:
            logger.exception("App model config broken.")
            raise AppUnavailableError()
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
        except Exception as e:
            logger.exception("internal server error.")
            raise InternalServerError()


@web_chat_ns.route("/completion-messages/<uuid:app_id>/<string:task_id>/stop")
class CompletionStopApi(WebUserApiResource):
    @web_chat_ns.doc("Stop Completion Messages")
    @web_chat_ns.doc(description="Stop the generation of completion messages.")
    @web_chat_ns.doc(params={"task_id": {"description": "Task ID", "type": "string", "required": True}})
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Task Not Found",
            500: "Internal Server Error",
        }
    )
    def post(self, app_models: list[App], end_user, app_id, task_id):
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        if app_model.mode != "completion":
            raise NotCompletionAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.WEB_APP, end_user.id)

        return {"result": "success"}, 200


@web_chat_ns.route("/chat-messages/<uuid:app_id>")
class ChatApi(WebUserApiResource):
    @web_chat_ns.doc("Create Chat Message")
    @web_chat_ns.doc(description="Create a chat message for conversational applications.")
    @web_chat_ns.doc(
        params={
            "inputs": {"description": "Input variables for the chat", "type": "object", "required": True},
            "query": {"description": "User query/message", "type": "string", "required": True},
            "files": {"description": "Files to be processed", "type": "array", "required": False},
            "response_mode": {
                "description": "Response mode: blocking or streaming",
                "type": "string",
                "enum": ["blocking", "streaming"],
                "required": False,
            },
            "conversation_id": {"description": "Conversation UUID", "type": "string", "required": False},
            "parent_message_id": {"description": "Parent message UUID", "type": "string", "required": False},
            "retriever_from": {"description": "Source of retriever", "type": "string", "required": False},
        }
    )
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "App Not Found",
            500: "Internal Server Error",
        }
    )
    def post(self, app_models: list[App], end_user, app_id):
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotChatAppError()

        parser = (
            reqparse.RequestParser()
            .add_argument("inputs", type=dict, required=True, location="json")
            .add_argument("query", type=str, required=True, location="json")
            .add_argument("files", type=list, required=False, location="json")
            .add_argument("response_mode", type=str, choices=["blocking", "streaming"], location="json")
            .add_argument("conversation_id", type=uuid_value, location="json")
            .add_argument("parent_message_id", type=uuid_value, required=False, location="json")
            .add_argument("retriever_from", type=str, required=False, default="web_app", location="json")
        )

        args = parser.parse_args()

        streaming = args["response_mode"] == "streaming"
        args["auto_generate_name"] = False

        try:
            response = AppGenerateService.generate(
                app_model=app_model, user=end_user, args=args, invoke_from=InvokeFrom.WEB_APP, streaming=streaming
            )

            return helper.compact_generate_response(response)
        except services.errors.conversation.ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except services.errors.conversation.ConversationCompletedError:
            raise ConversationCompletedError()
        except services.errors.app_model_config.AppModelConfigBrokenError:
            logging.exception("App model config broken.")
            raise AppUnavailableError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeRateLimitError as ex:
            raise InvokeRateLimitHttpError(ex.description)
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception("internal server error.")
            raise InternalServerError()


@web_chat_ns.route("/chat-messages/<uuid:app_id>/<string:task_id>/stop")
class ChatStopApi(WebUserApiResource):
    @web_chat_ns.doc("Stop Chat Message")
    @web_chat_ns.doc(description="Stop a running chat message task.")
    @web_chat_ns.doc(params={"task_id": {"description": "Task ID to stop", "type": "string", "required": True}})
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Task Not Found",
            500: "Internal Server Error",
        }
    )
    def post(self, app_models: list[App], end_user, app_id, task_id):
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT}:
            raise NotChatAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.WEB_APP, end_user.id)

        return {"result": "success"}, 200
