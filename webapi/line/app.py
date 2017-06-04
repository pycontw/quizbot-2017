import os
from flask import request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent

from .replier import Replier

from quizzler import db


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
        try:
            line_webhook_handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)
        return "OK"
