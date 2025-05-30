# 修改日期2025-02-28
# 專屬給chat-web的controllers

import logging

from flask import request
from werkzeug.exceptions import InternalServerError, NotFound

import services
from controllers.web_user import api
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
from models.model import App, AppMode
from services.audio_service import AudioService
from services.errors.audio import (
    AudioTooLargeServiceError,
    NoAudioUploadedServiceError,
    ProviderNotSupportSpeechToTextServiceError,
    UnsupportedAudioTypeServiceError,
)


class AudioApi(WebUserApiResource):
    def post(self, app_models: list[App], end_user, app_id):
        file = request.files["file"]
        
        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        try:
            response = AudioService.transcript_asr(app_model=app_model, file=file, end_user=end_user)

            return response
        except services.errors.app_model_config.AppModelConfigBrokenError:
            logging.exception("App model config broken.")
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
            logging.exception("Failed to handle post request to AudioApi")
            raise InternalServerError()


class TextApi(WebUserApiResource):
    def post(self, app_models: list[App], end_user, app_id):
        from flask_restful import reqparse  # type: ignore

        try:
            app_model = next(app_model for app_model in app_models if app_model.id == str(app_id))
        except:
            raise NotFound("App Not Exists.")
        
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("message_id", type=str, required=False, location="json")
            parser.add_argument("voice", type=str, location="json")
            parser.add_argument("text", type=str, location="json")
            parser.add_argument("streaming", type=bool, location="json")
            args = parser.parse_args()

            message_id = args.get("message_id", None)
            text = args.get("text", None)
            
            if (
                app_model.mode in {AppMode.ADVANCED_CHAT.value, AppMode.WORKFLOW.value}
                and app_model.workflow
                and app_model.workflow.features_dict
            ):
                text_to_speech = app_model.workflow.features_dict.get("text_to_speech", {})
                voice = args.get("voice") or text_to_speech.get("voice")
            else:
                try:
                    voice = args.get("voice") or app_model.app_model_config.text_to_speech_dict.get("voice")
                except Exception:
                    voice = None

            response = AudioService.transcript_tts(
                app_model=app_model, message_id=message_id, end_user=end_user.external_user_id, voice=voice, text=text
            )

            return response
        except services.errors.app_model_config.AppModelConfigBrokenError:
            logging.exception("App model config broken.")
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
            logging.exception("Failed to handle post request to TextApi")
            raise InternalServerError()


api.add_resource(AudioApi, "/audio-to-text/<uuid:app_id>")
api.add_resource(TextApi, "/text-to-audio/<uuid:app_id>")
