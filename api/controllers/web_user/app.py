# 修改日期2025-02-28
# 專屬給chat-web的controllers
# 修改日期2025-08-25
# 新增AppLatestMessageIndex獲取當前APP中哪個是最後發表的
from flask_restx import marshal_with  # type: ignore

from controllers.common import fields
from controllers.web_user import api
from controllers.web_user.error import AppUnavailableError
from controllers.web_user.wraps import WebUserApiResource
from core.app.app_config.common.parameters_mapping import get_parameters_from_feature_dict
from extensions.ext_database import db
from models.model import App, AppMode, EndUser, Message
from services.app_service import AppService


class AppParameterApi(WebUserApiResource):
    """Resource for app variables."""

    @marshal_with(fields.parameters_fields)
    def get(self, app_models: list[App], end_user: EndUser):
        """Retrieve app parameters."""
        app_parameters = []
        for app_model in app_models:
            if app_model.mode in {AppMode.ADVANCED_CHAT.value, AppMode.WORKFLOW.value}:
                workflow = app_model.workflow
                if workflow is None:
                    continue

                features_dict = workflow.features_dict
                user_input_form = workflow.user_input_form(to_old_structure=True)
            else:
                app_model_config = app_model.app_model_config
                if app_model_config is None:
                    continue
                features_dict = app_model_config.to_dict()

                user_input_form = features_dict.get("user_input_form", [])

            app_parameters.append(get_parameters_from_feature_dict(
                features_dict=features_dict, user_input_form=user_input_form
            ))

        if app_parameters:
            return app_parameters
        raise AppUnavailableError()


class AppMeta(WebUserApiResource):
    def get(self, app_models: list[App], end_user: EndUser):
        """Get app meta"""
        app_metas = []
        for app_model in app_models:
            app_metas.append(AppService().get_app_meta(app_model))
        return app_metas


class AppLatestMessageIndex(WebUserApiResource):
    def get(self, app_models: list[App], end_user: EndUser):
        # 1. 如果没有 app_models，直接返回 0
        if not app_models:
            return {"latest_message_index": 0}

        # 2. 构造 id -> index 的映射，方便后续 O(1) 查找
        app_id_to_index = {
            app_model.id: idx
            for idx, app_model in enumerate(app_models)
        }
        app_ids = list(app_id_to_index.keys())

        # 3. 只查询最晚的那条消息的 app_id（不拉完整的 Message 对象）
        latest_app_id = (
            db.session
              .query(Message.app_id)
              .filter(
                  Message.from_end_user_id == end_user.id,
                  Message.app_id.in_(app_ids)
              )
              .order_by(Message.created_at.desc())
              .limit(1)
              .scalar()
        )

        # 4. 根据映射拿到 index，找不到就默认为 0
        latest_index = app_id_to_index.get(latest_app_id, 0)

        return {"latest_message_index": latest_index}

api.add_resource(AppParameterApi, "/parameters")
api.add_resource(AppMeta, "/meta")
api.add_resource(AppLatestMessageIndex, "/latest_message_index")
