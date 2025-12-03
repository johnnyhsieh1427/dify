# 修改日期2025-02-28
# 專屬給chat-web的controllers

import logging

from flask import request
from flask_restx import fields, marshal_with
from werkzeug.exceptions import InternalServerError, NotFound

import services
from controllers.web_user import web_chat_ns
from controllers.web_user.error import (
    AppUnavailableError,
    AudioTooLargeError,
    CompletionRequestError,
    NoAudioUploadedError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderNotSupportSpeechToTextError,
    ProviderQuotaExceededError,
    UnsupportedAudioTypeError,
)
from controllers.web_user.wraps import WebUserApiResource
from core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, QuotaExceededError
from core.model_runtime.errors.invoke import InvokeError
from models.model import App
from services.audio_service import AudioService
from services.errors.audio import (
    AudioTooLargeServiceError,
    NoAudioUploadedServiceError,
    ProviderNotSupportSpeechToTextServiceError,
    UnsupportedAudioTypeServiceError,
)

logger = logging.getLogger(__name__)


@web_chat_ns.route("/audio-to-text/<uuid:app_id>")
class AudioApi(WebUserApiResource):
    audio_to_text_response_fields = {
        "text": fields.String,
    }

    @marshal_with(audio_to_text_response_fields)
    @web_chat_ns.doc("Audio to Text")
    @web_chat_ns.doc(description="Convert audio file to text using speech-to-text service.")
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            413: "Audio file too large",
            415: "Unsupported audio type",
            500: "Internal Server Error",
        }
    )
    def post(self, app_models: list[App], end_user, app_id):
        """Convert audio to text"""
        file = request.files["file"]
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        try:
            response = AudioService.transcript_asr(app_model=app_model, file=file, end_user=end_user)

            return response
        except services.errors.app_model_config.AppModelConfigBrokenError:
            logger.exception("App model config broken.")
            raise AppUnavailableError()
        except NoAudioUploadedServiceError:
            raise NoAudioUploadedError()
        except AudioTooLargeServiceError as e:
            raise AudioTooLargeError(str(e))
        except UnsupportedAudioTypeServiceError:
            raise UnsupportedAudioTypeError()
        except ProviderNotSupportSpeechToTextServiceError:
            raise ProviderNotSupportSpeechToTextError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception("Failed to handle post request to AudioApi")
            raise InternalServerError()


@web_chat_ns.route("/text-to-audio/<uuid:app_id>")
class TextApi(WebUserApiResource):
    text_to_audio_response_fields = {
        "audio_url": fields.String,
        "duration": fields.Float,
    }
    
    @marshal_with(text_to_audio_response_fields)
    @web_chat_ns.doc("Text to Audio")
    @web_chat_ns.doc(description="Convert text to audio using text-to-speech service.")
    @web_chat_ns.doc(
        responses={
            200: "Success",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
        }
    )
    def post(self, app_models: list[App], end_user, app_id):
        from flask_restx import reqparse  # type: ignore

        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        try:
            parser = (
                reqparse.RequestParser()
                .add_argument("message_id", type=str, required=False, location="json")
                .add_argument("voice", type=str, location="json")
                .add_argument("text", type=str, location="json")
                .add_argument("streaming", type=bool, location="json")
            )
            args = parser.parse_args()

            message_id = args.get("message_id", None)
            text = args.get("text", None)
            voice = args.get("voice", None)
            response = AudioService.transcript_tts(
                app_model=app_model, text=text, voice=voice, end_user=end_user.external_user_id, message_id=message_id
            )

            return response
        except services.errors.app_model_config.AppModelConfigBrokenError:
            logger.exception("App model config broken.")
            raise AppUnavailableError()
        except NoAudioUploadedServiceError:
            raise NoAudioUploadedError()
        except AudioTooLargeServiceError as e:
            raise AudioTooLargeError(str(e))
        except UnsupportedAudioTypeServiceError:
            raise UnsupportedAudioTypeError()
        except ProviderNotSupportSpeechToTextServiceError:
            raise ProviderNotSupportSpeechToTextError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise e
        except Exception as e:
            logger.exception("Failed to handle post request to TextApi")
            raise InternalServerError()
