from flask import Flask, redirect, render_template, url_for

from quizzler import users


app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('leaderboard'), code=307)


@app.route('/leaderboard')
def leaderboard():
    leader_gen = users.generate_leaders()
    return render_template(
        'leaderboard.html', leader_gen=leader_gen,
    )
