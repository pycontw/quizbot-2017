from flask import Flask

from quizzler import db


app = Flask(__name__)


@app.after_request
def commit_database(response):
    db.commit()
    return response
