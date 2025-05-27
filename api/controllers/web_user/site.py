# 修改日期2025-02-28
# 專屬給chat-web的controllers

from typing import List
from flask_restful import fields, marshal_with  # type: ignore

from controllers.web_user.error import AppUnavailableError
from configs import dify_config
from controllers.web_user import api
from controllers.web_user.wraps import WebUserApiResource
from extensions.ext_database import db
from libs.helper import AppIconUrlField
# from models.account import TenantStatus
from models.model import App, EndUser, Site

# from services.feature_service import FeatureService


class UserAppSiteApi(WebUserApiResource):
    """Resource for user app sites."""
    
    model_config_fields = {
        "opening_statement": fields.String,
        "suggested_questions": fields.Raw(attribute="suggested_questions_list"),
        "suggested_questions_after_answer": fields.Raw(attribute="suggested_questions_after_answer_dict"),
        "more_like_this": fields.Raw(attribute="more_like_this_dict"),
        "model": fields.Raw(attribute="model_dict"),
        "user_input_form": fields.Raw(attribute="user_input_form_list"),
        "pre_prompt": fields.String,
    }

    site_fields = {
        "title": fields.String,
        "chat_color_theme": fields.String,
        "chat_color_theme_inverted": fields.Boolean,
        "icon_type": fields.String,
        "icon": fields.String,
        "icon_background": fields.String,
        "icon_url": AppIconUrlField,
        "description": fields.String,
        "copyright": fields.String,
        "privacy_policy": fields.String,
        "custom_disclaimer": fields.String,
        "default_language": fields.String,
        "prompt_public": fields.Boolean,
        "show_workflow_steps": fields.Boolean,
        "use_icon_as_answer_icon": fields.Boolean,
    }

    app_fields = {
        "app_id": fields.String,
        "end_user_id": fields.String,
        "enable_site": fields.Boolean,
        "site": fields.Nested(site_fields),
        "model_config": fields.Nested(model_config_fields, allow_null=True),
        "plan": fields.String,
        "can_replace_logo": fields.Boolean,
        "custom_config": fields.Raw(attribute="custom_config"),
    }
    
    app_list = {
        "items": fields.List(fields.Nested(app_fields))
    }

    @marshal_with(app_list)
    # @marshal_with(app_fields)
    def get(self, app_models: List[App], end_user: EndUser):
        _list = []
        for app_model in app_models:
            site = db.session.query(Site).filter(Site.app_id == app_model.id).first()
            # if not site:
            #     _list.append(None)
            #     continue
            # if app_model.status != "normal":
            #     _list.append(None)
            #     continue
            # if not app_model.enable_site:
            #     _list.append(None)
            #     continue
            # if app_model.tenant.status == TenantStatus.ARCHIVE:
            #     _list.append(None)
            #     continue
            _list.append(AppSiteInfo(app_model.tenant, app_model, site, end_user.id, False))
        if not _list:
            raise AppUnavailableError("No site available for this app.")
        return {'items': _list}


api.add_resource(UserAppSiteApi, "/site")


class AppSiteInfo:
    """Class to store site information."""

    def __init__(self, tenant, app, site, end_user, can_replace_logo):
        """Initialize AppSiteInfo instance."""
        self.app_id = app.id
        self.end_user_id = end_user
        self.enable_site = app.enable_site
        self.site = site
        self.model_config = None
        self.plan = tenant.plan
        self.can_replace_logo = can_replace_logo

        if can_replace_logo:
            base_url = dify_config.FILES_URL
            remove_webapp_brand = tenant.custom_config_dict.get("remove_webapp_brand", False)
            replace_webapp_logo = (
                f"{base_url}/files/workspaces/{tenant.id}/webapp-logo"
                if tenant.custom_config_dict.get("replace_webapp_logo")
                else None
            )
            self.custom_config = {
                "remove_webapp_brand": remove_webapp_brand,
                "replace_webapp_logo": replace_webapp_logo,
            }
