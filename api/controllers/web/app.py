# 修改日期2025-01-20
# 新增API AppTenantPermission，用於檢查使用者是否有權限訪問聊天機器人應用
from flask_restful import marshal_with
from werkzeug.exceptions import Forbidden

from controllers.common import fields
from controllers.common import helpers as controller_helpers
from controllers.web import api
from controllers.web.error import AppUnavailableError
from controllers.web.wraps import WebApiResource
from extensions.ext_database import db
from models.account import TenantAccountJoin
from models.model import App, AppMode, EndUser
from services.app_service import AppService


class AppParameterApi(WebApiResource):
    """Resource for app variables."""

    @marshal_with(fields.parameters_fields)
    def get(self, app_model: App, end_user):
        """Retrieve app parameters."""
        if app_model.mode in {AppMode.ADVANCED_CHAT.value, AppMode.WORKFLOW.value}:
            workflow = app_model.workflow
            if workflow is None:
                raise AppUnavailableError()

            features_dict = workflow.features_dict
            user_input_form = workflow.user_input_form(to_old_structure=True)
        else:
            app_model_config = app_model.app_model_config
            if app_model_config is None:
                raise AppUnavailableError()

            features_dict = app_model_config.to_dict()

            user_input_form = features_dict.get("user_input_form", [])

        return controller_helpers.get_parameters_from_feature_dict(
            features_dict=features_dict, user_input_form=user_input_form
        )


class AppMeta(WebApiResource):
    def get(self, app_model: App, end_user):
        """Get app meta"""
        return AppService().get_app_meta(app_model)


class AppTenantPermission(WebApiResource):
    def get(self, app_model: App, end_user: EndUser):
        if app_model and end_user:
            """Check if the user has permission to access the app"""
            result = db.session.query(TenantAccountJoin).filter(
                TenantAccountJoin.account_id == end_user.session_id, 
                TenantAccountJoin.tenant_id == app_model.tenant_id 
            ).first()
            if result:
                return {"result": "success"}
        raise Forbidden()


api.add_resource(AppParameterApi, "/parameters")
api.add_resource(AppMeta, "/meta")
api.add_resource(AppTenantPermission, "/permission")
