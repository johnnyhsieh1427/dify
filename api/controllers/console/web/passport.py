import uuid
from typing import cast

from flask import request
from flask_restful import Resource
from flask_login import current_user
from werkzeug.exceptions import NotFound, Unauthorized

from controllers.console import api
from controllers.web.error import WebSSOAuthRequiredError
from extensions.ext_database import db
from libs.passport import PassportService
from models.model import App, EndUser, Site, Account
from services.enterprise.enterprise_service import EnterpriseService
from services.feature_service import FeatureService

from controllers.console.wraps import account_initialization_required, setup_required
from libs.login import login_required


class PassportUserAuthResource(Resource):
    """Base resource for passport."""
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        app_code = request.args.get("appCode", default="", type=str)
        system_features = FeatureService.get_system_features()
        account = cast(Account, current_user)
        
        # if app_code is None:
        #     raise Unauthorized("X-App-Code header is missing.")

        if system_features.sso_enforced_for_web:
            app_web_sso_enabled = EnterpriseService.get_app_web_sso_enabled(app_code).get("enabled", False)
            if app_web_sso_enabled:
                raise WebSSOAuthRequiredError()
            
        if account is None or account.is_anonymous:
            raise Unauthorized("User login required.")
        
        # get site from db and check if it is normal
        site = db.session.query(Site).filter(Site.code == app_code, Site.status == "normal").first()
        if not site:
            raise NotFound()
        
        # get app from db and check if it is normal and enable_site
        app_model = db.session.query(App).filter(App.id == site.app_id).first()
        if not app_model or app_model.status != "normal" or not app_model.enable_site:
            raise NotFound()

        end_user = (
            db.session.query(EndUser)
            .filter(
                EndUser.tenant_id == app_model.tenant_id,
                EndUser.app_id == app_model.id,
                EndUser.session_id == account.id,
                EndUser.type == "browser",
            )
            .first()
        )
        
        if end_user is None:
            end_user = EndUser(
                tenant_id=app_model.tenant_id,
                app_id=app_model.id,
                type="browser",
                is_anonymous=False,
                session_id=account.id,
            )
            db.session.add(end_user)
            db.session.commit()

        payload = {
            "iss": site.app_id,
            "sub": "Web API Passport",
            "app_id": site.app_id,
            "app_code": app_code,
            "end_user_id": end_user.id,
        }

        tk = PassportService().issue(payload)

        return {
            "access_token": tk,
        }

api.add_resource(PassportUserAuthResource, "/passport_auth")

def generate_session_id():
    """
    Generate a unique session ID.
    """
    while True:
        session_id = str(uuid.uuid4())
        existing_count = db.session.query(EndUser).filter(EndUser.session_id == session_id).count()
        if existing_count == 0:
            return session_id
