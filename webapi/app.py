from flask import Flask, jsonify, redirect, render_template, url_for

from quizzler import users

from .utils import freeze_leader, request_wants_json


app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('leaderboard'), code=307)


@app.route('/leaderboard')
def leaderboard():
    if request_wants_json():
        leader_gen = users.generate_leaders(leader_factory=freeze_leader)
        return jsonify({'leaders': list(leader_gen)})
    leader_gen = users.generate_leaders()
    return render_template(
        'leaderboard.html', leader_gen=leader_gen,
    )
