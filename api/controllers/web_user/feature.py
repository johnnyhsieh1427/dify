# 修改日期2025-02-28
# 專屬給chat-web的controllers

from flask_restx import Resource

from controllers.web_user import web_chat_ns
from services.feature_service import FeatureService


@web_chat_ns.route("/system-features")
class SystemFeatureApi(Resource):
    @web_chat_ns.doc("get_system_features")
    @web_chat_ns.doc(description="Get system feature flags and configuration")
    @web_chat_ns.doc(responses={200: "System features retrieved successfully", 500: "Internal server error"})
    def get(self):
        return FeatureService.get_system_features().model_dump()
