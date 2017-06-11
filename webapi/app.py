from flask import Flask, jsonify, render_template, url_for

from quizzler import botdetection, users

from .utils import freeze_leader, request_wants_json


app = Flask(__name__)


@app.route('/')
def index():
    bot_links = [
        {
            'title': 'LINE',
            'url': 'https://line.me/R/ti/p/W1MINAEbHE',
            'external': True,
        },
        {
            'title': 'Facebook (web)',
            'url': 'https://www.facebook.com/pycontwchatbot/',
            'external': True,
        },
        {
            'title': 'Facebook (app)',
            'url': 'fb://page/299082580532144',
            'external': True,
        },
    ]
    misc_links = [
        {
            'title': '排行榜',
            'url': url_for('leaderboard'),
            'external': False,
        },
    ]
    return render_template(
        'index.html',
        bot_links=bot_links, misc_links=misc_links,
    )


@app.route('/leaderboard')
def leaderboard():
    if request_wants_json():
        leader_gen = users.generate_leaders(leader_factory=freeze_leader)
        return jsonify({'leaders': list(leader_gen)})
    leader_gen = users.generate_leaders()
    return render_template(
        'leaderboard.html', leader_gen=leader_gen,
    )


@app.route('/awards')
def awards():
    bot_serials = set(botdetection.generate_bot_serials())
    bot_leader_gen = filter(
        lambda d: d.user.serial in bot_serials,
        users.generate_leaders(),
    )
    human_leader_gen = filter(
        lambda d: d.user.serial not in bot_serials and d.score > 0,
        users.generate_leaders(),
    )
    return render_template(
        'awards.html',
        bot_leader_gen=bot_leader_gen, human_leader_gen=human_leader_gen,
    )
