from flask import make_response, request
from flask_restx import Resource

from controllers.console.wraps import setup_required
from controllers.web_user import web_chat_ns
from controllers.web_user.wraps import decode_user_jwt_token
from libs.passport import PassportService
from libs.token import (
    clear_chat_app_token_from_cookie,
    extract_chat_app_passport,
)


# this api helps frontend to check whether user is authenticated
# TODO: remove in the future. frontend should redirect to login page by catching 401 status
@web_chat_ns.route("/login/status")
class LoginStatusApi(Resource):
    @setup_required
    @web_chat_ns.doc("web_app_login_status")
    @web_chat_ns.doc(description="Check login status")
    @web_chat_ns.doc(
        responses={
            200: "Login status",
            401: "Login status",
        }
    )
    def get(self):
        app_code = request.args.get("app_code")
        token = extract_chat_app_passport(request)
        if not app_code:
            return {
                "logged_in": bool(token),
                "app_logged_in": False,
            }
        try:
            PassportService().verify(token=token)
            user_logged_in = True
        except Exception:
            user_logged_in = False

        try:
            _ = decode_user_jwt_token()
            app_logged_in = True
        except Exception:
            app_logged_in = False

        return {
            "logged_in": user_logged_in,
            "app_logged_in": app_logged_in,
        }


@web_chat_ns.route("/logout")
class LogoutApi(Resource):
    @setup_required
    @web_chat_ns.doc("web_app_logout")
    @web_chat_ns.doc(description="Logout user from web application")
    @web_chat_ns.doc(
        responses={
            200: "Logout successful",
        }
    )
    def post(self):
        response = make_response({"result": "success"})
        # enterprise SSO sets same site to None in https deployment
        # so we need to logout by calling api
        clear_chat_app_token_from_cookie(response)
        return response
