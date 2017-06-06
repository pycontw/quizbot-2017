import os
import logging
from pprint import pformat
from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, PostbackEvent

from .replier import Replier

from quizzler import db


logger = logging.getLogger('line_webhook') # linebot namespace is taken

# INIT LINE BOT
line_bot_api = LineBotApi(os.environ.get('LINE_ACCESS_TOKEN'))
line_webhook_handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))


@line_webhook_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    replier = Replier(event)
    reply = replier.handle_message()
    if reply is not None:
        line_bot_api.reply_message(event.reply_token, reply)


@line_webhook_handler.add(PostbackEvent)
def handle_postback(event):
    replier = Replier(event)
    reply = replier.handle_postback()
    if reply is not None:
        line_bot_api.reply_message(event.reply_token, reply)


# INIT FLASK APP
def configure_linebot_app(app):

    @app.after_request
    def commit_database(response):
        db.commit()
        return response

    @app.route("/api/line_webhook", methods=["POST"])
    def line_webhook():
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        logger.debug(f'Incoming message:\n{pformat(body)}')
        try:
            line_webhook_handler.handle(body, signature)
        except InvalidSignatureError:
            logger.warning('Message with an invalid signature received')
            abort(400)
        except LineBotApiError as e:
            logger.error(f'{e}\nDetails:\n{pformat(e.error.details)}')
            abort(500)
        except Exception as e:
            logger.error(f'Uncaught error: {e}')
            abort(500)
        return "OK"
