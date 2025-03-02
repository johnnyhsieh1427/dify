# 修改日期2025-02-28
# 新增新的controllers, 這樣在Class PassportUserAppResource的accessToken
# 只能在下列關係的使用

from flask import Blueprint
from libs.external_api import ExternalApi

# from .files import FileApi
# from .remote_files import RemoteFileInfoApi, RemoteFileUploadApi

bp = Blueprint("web_user", __name__, url_prefix="/web-chat/api")
api = ExternalApi(bp)

# # Files
# api.add_resource(FileApi, "/files/upload")

# # Remote files
# api.add_resource(RemoteFileInfoApi, "/remote-files/<path:url>")
# api.add_resource(RemoteFileUploadApi, "/remote-files/upload")

from . import app, audio, completion, conversation, feature, message, saved_message, site, workflow
