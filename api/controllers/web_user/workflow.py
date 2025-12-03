# 修改日期2025-02-28
# 專屬給chat-web的controllers

import logging

from flask_restx import reqparse  # type: ignore
from werkzeug.exceptions import InternalServerError

from controllers.web.error import InvokeRateLimitError as InvokeRateLimitHttpError
from controllers.web_user import web_chat_ns
from controllers.web_user.error import (
    CompletionRequestError,
    InvokeRateLimitError,
    NotWorkflowAppError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from controllers.web_user.wraps import NotFound, WebUserApiResource
from core.app.apps.base_app_queue_manager import AppQueueManager
from core.app.entities.app_invoke_entities import InvokeFrom
from core.errors.error import (
    ModelCurrentlyNotSupportError,
    ProviderTokenNotInitError,
    QuotaExceededError,
)
from core.model_runtime.errors.invoke import InvokeError
from core.workflow.graph_engine.manager import GraphEngineManager
from libs import helper
from libs.helper import uuid_value
from models.model import App, AppMode, EndUser
from services.app_generate_service import AppGenerateService

logger = logging.getLogger(__name__)


@web_chat_ns.route("/workflows/run")
class WorkflowRunApi(WebUserApiResource):
    @web_chat_ns.doc("Run Workflow")
    @web_chat_ns.doc(description="Execute a workflow with provided inputs and files.")
    @web_chat_ns.doc(
        params={
            "app_id": {"description": "ID of the app", "type": "string", "required": True},
            "inputs": {"description": "Input variables for the workflow", "type": "object", "required": True},
            "files": {"description": "Files to be processed by the workflow", "type": "array", "required": False},
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
    def post(self, app_models: list[App], end_user: EndUser):
        """
        Run workflow
        """
        parser = (
            reqparse.RequestParser()
            .add_argument("app_id", required=True, type=uuid_value, location="args")
            .add_argument("inputs", type=dict, required=True, nullable=False, location="json")
            .add_argument("files", type=list, required=False, location="json")
        )
        args = parser.parse_args()
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == args["app_id"])
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode != AppMode.WORKFLOW:
            raise NotWorkflowAppError()
        
        try:
            response = AppGenerateService.generate(
                app_model=app_model, user=end_user, args=args, invoke_from=InvokeFrom.WEB_APP, streaming=True
            )

            return helper.compact_generate_response(response)
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except InvokeRateLimitError as ex:
            raise InvokeRateLimitHttpError(ex.description)
        except ValueError as e:
            raise e
        except Exception:
            logger.exception("internal server error.")
            raise InternalServerError()


@web_chat_ns.route("/workflows/tasks/<string:task_id>/stop")
class WorkflowTaskStopApi(WebUserApiResource):
    @web_chat_ns.doc("Stop Workflow Task")
    @web_chat_ns.doc(description="Stop a running workflow task.")
    @web_chat_ns.doc(
        params={
            "task_id": {"description": "Task ID to stop", "type": "string", "required": True},
        }
    )
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
    def post(self, app_models: list[App], end_user: EndUser, task_id: str):
        """
        Stop workflow task
        """
        parser = reqparse.RequestParser()
        parser.add_argument("app_id", required=True, type=uuid_value, location="args")
        args = parser.parse_args()
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == args["app_id"])
        except:
            raise NotFound("App Not Exists.")
        
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode != AppMode.WORKFLOW:
            raise NotWorkflowAppError()

        # Stop using both mechanisms for backward compatibility
        # Legacy stop flag mechanism (without user check)
        AppQueueManager.set_stop_flag_no_user_check(task_id)

        # New graph engine command channel mechanism
        GraphEngineManager.send_stop_command(task_id)

        return {"result": "success"}
