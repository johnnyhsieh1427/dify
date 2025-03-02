# 修改日期2025-02-28
# 專屬給chat-web的controllers

from functools import wraps

from flask import request
from flask_restful import Resource  # type: ignore
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized

from extensions.ext_database import db
from libs.passport import PassportService
from models.model import App, EndUser


def validate_user_jwt_token(view=None):
    def decorator(view):
        @wraps(view)
        def decorated(*args, **kwargs):
            app_models, end_user = decode_user_jwt_token()

            return view(app_models, end_user, *args, **kwargs)

        return decorated

    if view:
        return decorator(view)
    return decorator


def decode_user_jwt_token():
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header is None:
            raise Unauthorized("Authorization header is missing.")

        if " " not in auth_header:
            raise Unauthorized("Invalid Authorization header format. Expected 'Bearer <api-key>' format.")

        auth_scheme, tk = auth_header.split(None, 1)
        auth_scheme = auth_scheme.lower()

        if auth_scheme != "bearer":
            raise Unauthorized("Invalid Authorization header format. Expected 'Bearer <api-key>' format.")
        decoded = PassportService().verify(tk)
        
        app_ids = decoded.get("app_ids")
        end_user_id = decoded.get("end_user_id")
        
        app_models = db.session.query(App).filter(App.id.in_(app_ids)).all()
        end_user = db.session.query(EndUser).filter(EndUser.id == end_user_id).first()
                
        if not end_user:
            raise BadRequest("User is not longer valid.")

        return app_models, end_user
    except Unauthorized as e:
        raise Unauthorized(e.description)
    except Exception as e:
        raise NotFound()


class WebUserApiResource(Resource):
    method_decorators = [validate_user_jwt_token]