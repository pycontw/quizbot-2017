from flask import Flask, render_template

from quizzler import users
from .line.app import configure_linebot_app


app = Flask(__name__)

configure_linebot_app(app)

@app.route('/leaderboard')
def leaderboard():
    leader_gen = users.generate_leaders()
    return render_template(
        'leaderboard.html', leader_gen=leader_gen,
    )
