from flask import Flask, render_template

from quizzler import users


app = Flask(__name__)


@app.route('/leaderboard')
def leaderboard():
    leader_gen = users.generate_leaders()
    return render_template(
        'leaderboard.html', leader_gen=leader_gen,
    )
