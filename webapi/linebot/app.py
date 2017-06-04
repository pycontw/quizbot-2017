from flask import Flask, request, abort
from linebot.exceptions import InvalidSignatureError

from .line import line_webhook_handler

from quizzler import db


app = Flask(__name__)


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
