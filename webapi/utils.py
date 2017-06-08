from flask import request


def request_wants_json():
    """Based on `Armin's snippet <http://flask.pocoo.org/snippets/45/>`.
    """
    best = request.accept_mimetypes.best_match([
        'application/json', 'text/html',
    ])
    if best != 'application/json':
        return False
    json_score = request.accept_mimetypes['application/json']
    html_score = request.accept_mimetypes['text/html']
    return best == 'application/json' and json_score > html_score


def freeze_leader(ranking, score, user, registration):
    return {
        'ranking': ranking,
        'score': score,
        'user': {
            'serial': user.serial,
            'nickname': registration.nickname,
        },
    }
