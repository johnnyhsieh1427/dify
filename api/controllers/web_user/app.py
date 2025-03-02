# 修改日期2025-02-28
# 專屬給chat-web的controllers

from typing import List
from flask_restful import marshal_with  # type: ignore

from controllers.common import fields
from controllers.common import helpers as controller_helpers
from controllers.web_user import api
from controllers.web_user.error import AppUnavailableError
from controllers.web_user.wraps import WebUserApiResource
from models.model import App, AppMode
from services.app_service import AppService


class AppParameterApi(WebUserApiResource):
    """Resource for app variables."""

    @marshal_with(fields.parameters_fields)
    def get(self, app_models: List[App], end_user):
        """Retrieve app parameters."""
        app_parameters = []
        for app_model in app_models:
            if app_model.mode in {AppMode.ADVANCED_CHAT.value, AppMode.WORKFLOW.value}:
                workflow = app_model.workflow
                if workflow is None:
                    continue
                    # raise AppUnavailableError()

                features_dict = workflow.features_dict
                user_input_form = workflow.user_input_form(to_old_structure=True)
            else:
                app_model_config = app_model.app_model_config
                if app_model_config is None:
                    continue
                    # raise AppUnavailableError()

                features_dict = app_model_config.to_dict()

                user_input_form = features_dict.get("user_input_form", [])

            app_parameters.append(
                controller_helpers.get_parameters_from_feature_dict(
                    features_dict=features_dict, user_input_form=user_input_form
                )
            )

        if app_parameters:
            return app_parameters
        raise AppUnavailableError()


class AppMeta(WebUserApiResource):
    def get(self, app_models: List[App], end_user):
        """Get app meta"""
        app_metas = []
        for app_model in app_models:
            app_metas.append(AppService().get_app_meta(app_model))
        return app_metas

    
api.add_resource(AppParameterApi, "/parameters")
api.add_resource(AppMeta, "/meta")
