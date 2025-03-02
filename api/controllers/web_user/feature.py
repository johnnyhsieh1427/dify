# 修改日期2025-02-28
# 專屬給chat-web的controllers

from flask_restful import Resource  # type: ignore

from controllers.web_user import api
from services.feature_service import FeatureService


class SystemFeatureApi(Resource):
    def get(self):
        return FeatureService.get_system_features().model_dump()

api.add_resource(SystemFeatureApi, "/system-features")
