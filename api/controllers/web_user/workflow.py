# 修改日期2025-02-28
# 專屬給chat-web的controllers

import logging
from typing import List

from flask_restful import reqparse  # type: ignore
from werkzeug.exceptions import InternalServerError

from controllers.web_user import api
from controllers.web_user.error import (
    CompletionRequestError,
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
from libs import helper
from libs.helper import uuid_value
from models.model import App, AppMode, EndUser
from services.app_generate_service import AppGenerateService

logger = logging.getLogger(__name__)


class WorkflowRunApi(WebUserApiResource):
    def post(self, app_models: List[App], end_user: EndUser):
        """
        Run workflow
        """
        parser = reqparse.RequestParser()
        parser.add_argument("app_id", required=True, type=uuid_value, location="args")
        parser.add_argument("inputs", type=dict, required=True, nullable=False, location="json")
        parser.add_argument("files", type=list, required=False, location="json")
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
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


class WorkflowTaskStopApi(WebUserApiResource):
    def post(self, app_models: List[App], end_user: EndUser, task_id: str):
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

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.WEB_APP, end_user.id)

        return {"result": "success"}


api.add_resource(WorkflowRunApi, "/workflows/run")
api.add_resource(WorkflowTaskStopApi, "/workflows/tasks/<string:task_id>/stop")
