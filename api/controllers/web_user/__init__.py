# 修改日期2025-02-28
# 新增新的controllers, 這樣在Class PassportUserAppResource的accessToken
# 只能在下列關係的使用

from flask import Blueprint
from flask_restx import Namespace

from libs.external_api import ExternalApi

bp = Blueprint("web_user", __name__, url_prefix="/web-chat/api")
api = ExternalApi(
    bp,
    version="1.0",
    title="Web Chat API",
    description="Web Chat APIs for web applications including file uploads, chat interactions, and app management",
)

# Create namespace
web_chat_ns = Namespace("web_chat", description="Web Chat application API operations", path="/")

api.add_namespace(web_chat_ns)

from . import (
    app,
    audio,
    completion,
    conversation,
    feature,
    files,
    login,
    message,
    remote_files,
    saved_message,
    site,
    workflow,
)

__all__ = [
    "api",
    "app",
    "audio",
    "bp",
    "completion",
    "conversation",
    "feature",
    "files",
    "login",
    "message",
    "remote_files",
    "saved_message",
    "site",
    "web_chat_ns",
    "workflow"
]