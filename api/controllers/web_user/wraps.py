# 修改日期2025-02-28
# 專屬給chat-web的controllers

from collections.abc import Callable
from functools import wraps
from typing import Concatenate, ParamSpec, TypeVar

from flask import request
from flask_restx import Resource  # type: ignore
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized

from extensions.ext_database import db
from libs.passport import PassportService
from libs.token import extract_chat_app_passport
from models.model import App, EndUser

P = ParamSpec("P")
R = TypeVar("R")


def validate_user_jwt_token(view: Callable[Concatenate[App, EndUser, P], R] | None = None):
    def decorator(view):
        @wraps(view)
        def decorated(*args: P.args, **kwargs: P.kwargs):
            app_models, end_user = decode_user_jwt_token()
            return view(app_models, end_user, *args, **kwargs)

        return decorated

    if view:
        return decorator(view)
    return decorator


def decode_user_jwt_token():
    try:
        tk = extract_chat_app_passport(request)
        decoded = PassportService().verify(tk)

        app_ids = decoded.get("app_ids")
        end_user_id = decoded.get("end_user_id")
        
        app_models = (
            db.session.query(App)
            .filter(App.id.in_(app_ids))
            .order_by(App.created_at.desc())
            .all()
        )
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